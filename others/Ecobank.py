import pandas as pd
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path


def ecobank_preprocessing():

    # ==================== CHURCH KEYWORDS ====================
    CHURCH_KEYWORDS = [
        'CHURCH', 'MINISTRY', 'MINISTRIES', 'CHAPEL',
        'PARISH', 'CATHEDRAL', 'MOSQUE', 'ASSEMBLY',
        'FELLOWSHIP', 'MISSION', 'GOSPEL', 'APOSTOLIC',
        'EVANGELICAL', 'PENTECOSTAL', 'BAPTIST', 'CATHOLIC',
        'ANGLICAN', 'RCCG', 'WINNERS', 'DEEPER LIFE',
        'SALVATION', 'MOUNTAIN OF FIRE', 'CHRIST EMBASSY',
        'DAYSTAR', 'LIVING FAITH', 'SANCTUARY', 'WORSHIP CENTRE',
        'TITHE', 'OFFERING', 'HEADQUARTERS', 'PACEM IN TERRIS',
        'RCCG CAMP', 'RCCG NATIONAL',
    ]

    BETTING_KEYWORDS = [
        'SPORTYBET', 'SPORTY', 'BET9JA', '1XBET', 'BETKING',
        'BETWAY', 'BETBONANZA', 'NAIRABET', 'MSPORT', 'BETANO',
        'BETWINNER', 'PARIPESA', 'MELBET', 'MEGAPARI', '22BET',
        'BETPAWA', 'LIVESCOREBET', 'MOZZARTBET', 'WAZOBET',
        'ACCESSBET', 'BETFAIR', 'BETLAND', 'GREENLOTTO',
        'AFRIBET', 'ZEBET', 'FOOTBALLING',
    ]

    # ==================== CATEGORISATION LOGIC ====================
    def get_category(desc: str, debit, credit) -> str:
        u = str(desc).upper()

        # --- Charges (must come first) ---
        if 'VAT' in u and 'NIP' in u:
            return 'Charges'
        if 'CHARGE NIP' in u or ('CHARGE' in u and 'NIP' in u):
            return 'Charges'
        if 'SMS CHARGE' in u:
            return 'SMS Charges'
        if 'USSD' in u:
            return 'Charges'
        if re.search(r'\bC13ZSTM\w*', u):
            return 'Charges'

        # --- Airtime ---
        if 'AIRTIME TOPUP' in u or 'AIRTIME TOP UP' in u:
            return 'Airtime'

        # --- POS ---
        if 'POS PURCHASE' in u:
            return 'POS Transaction'
        if 'POS TRANSFER' in u or 'POS Transfer' in str(desc):
            return 'POS Transaction'

        # --- Interest ---
        if 'INTEREST' in u and ('PAID' in u or 'EARNED' in u):
            return 'Savings'

        # --- Betting ---
        if any(k in u for k in BETTING_KEYWORDS):
            return 'Betting'

        # --- Church (MUST come before P2P/IFO check) ---
        if any(k in u for k in CHURCH_KEYWORDS):
            return 'Church'

        # --- P2P (MUST come before savings keywords) ---
        if 'NIP TRANSFER IFO' in u or re.search(r'\bIFO\b', u):
            return 'P2P Transfer'
        if 'NIP FROM' in u:
            return 'P2P Transfer'
        if re.search(r'\bB/O\b', u):
            return 'P2P Transfer'

        # --- Savings ---
        if 'SAVINGS' in u or 'REPAYMENT' in u:
            return 'Savings'

        # --- Online / E-payment ---
        if 'E-PAYMENT' in u or 'TRANSFER' in u:
            return 'Online Transfer'

        return 'Others'

    # ==================== DESCRIPTION CLEANING ====================
    def extract_ifo_name(raw: str) -> str:
        m = re.search(
            r'IFO\s+(.+?)(?:\s+Interbank|\s+REF:|\s+Ref\.).*$',
            raw, re.IGNORECASE
        )
        if m:
            name = m.group(1).strip()
            name = re.sub(r'^POS\s+Transfer\s*[-–]\s*', '', name, flags=re.IGNORECASE).strip()
            return name
        return ''

    def extract_nip_from_name(raw: str) -> str:
        m = re.search(r'NIP FROM\s+(.+?)(?:/|$)', raw, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        return ''

    def extract_bo_name(raw: str) -> str:
        m = re.search(r'B/O\s+(.+?)(?:\s+from\b|\s+Ref\.|\s+REF:)', raw, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        return ''

    def clean_description(desc: str, category: str, debit, credit) -> str:
        raw = str(desc).strip()
        u = raw.upper()

        is_debit  = pd.notna(debit)  and float(debit)  != 0
        is_credit = pd.notna(credit) and float(credit) != 0

        if category == 'Airtime':
            m = re.search(r'AIRTIME TOPUP:\s*([\d]+)', raw, re.IGNORECASE)
            number = m.group(1).strip() if m else ''
            return f"Airtime Transfer to {number}" if number else "Airtime Top Up"

        if category == 'POS Transaction':
            if 'POS PURCHASE' in u:
                return "POS Purchase"
            name = extract_ifo_name(raw)
            if name:
                direction = "Transfer from" if is_credit else "Transfer to"
                return f"{direction} POS {name}"
            return "POS Transaction"

        if category == 'SMS Charges':
            return "SMS Charge"

        if category == 'Charges':
            if 'VAT' in u and 'NIP' in u:
                name = extract_ifo_name(raw)
                return f"VAT Charge for Transfer to {name}" if name else "VAT Charge"
            if 'CHARGE NIP' in u or ('CHARGE' in u and 'NIP' in u):
                name = extract_ifo_name(raw)
                return f"Charge for Transfer to {name}" if name else "Bank Charge"
            if 'USSD' in u:
                return "USSD Charge"
            if re.search(r'\bC13ZSTM\w*', u):
                return "Bank Levy Charge"
            return "Bank Charge"

        if category == 'Betting':
            if is_credit:
                return "Betting Winnings Received"
            provider = next((k for k in BETTING_KEYWORDS if k in u), 'Betting Platform')
            return f"Betting Payment to {provider}"

        # --- Church description cleaning ---
        if category == 'Church':
            name = extract_ifo_name(raw)
            if not name:
                m = re.search(r'B/O\s+(.+?)(?:\s+from\b|\s+Ref\.|\s+REF:)', raw, re.IGNORECASE)
                if m:
                    name = m.group(1).strip()
            direction = "Transfer from" if is_credit else "Transfer to"
            return f"{direction} {name}" if name else "Church Transfer"

        if category == 'Savings':
            if 'INTEREST' in u:
                return "Interest Earned"
            name = extract_ifo_name(raw)
            if not name:
                name = 'Account Holder'
            name = re.sub(r'\s+(savings|repayment|i)\s*$', '', name, flags=re.IGNORECASE).strip()
            direction = "Transfer from" if is_credit else "Transfer to"
            return f"{direction} {name}"

        if category == 'P2P Transfer':
            direction = "Transfer from" if is_credit else "Transfer to"

            if 'NIP TRANSFER IFO' in u or re.search(r'\bIFO\b', u):
                name = extract_ifo_name(raw)
                return f"{direction} {name}" if name else "P2P Transfer"

            if 'NIP FROM' in u:
                name = extract_nip_from_name(raw)
                return f"{direction} {name}" if name else "P2P Transfer"

            if re.search(r'\bB/O\b', u):
                name = extract_bo_name(raw)
                return f"{direction} {name}" if name else "P2P Transfer Received"

            return "P2P Transfer"

        if category == 'Online Transfer':
            if is_credit:
                return "Online Transfer Received"
            return "Online Transfer Sent"

        return raw

    # ==================== MAIN EXECUTION ====================
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    file_path = filedialog.askopenfilename(
        title="Select Ecobank CSV Statement",
        filetypes=[("CSV files", "*.csv")]
    )
    if not file_path:
        return

    try:
        df_raw = pd.read_csv(file_path, skiprows=6, header=0)

        df_raw.columns = [c.strip() for c in df_raw.columns]
        df_raw = df_raw.rename(columns={
            'Transaction Date': 'Date',
            'Description':      'Description_raw',
            'Reference Number': 'Reference',
            'DEBIT':            'Debit',
            'CREDIT':           'Credit',
            'Balance':          'Balance'
        })

        df_raw = df_raw.dropna(subset=['Date']).reset_index(drop=True)

        # ---- Copy Debit / Credit / Balance exactly as-is from raw ----
        df_raw['Debit']   = pd.to_numeric(df_raw['Debit'],   errors='coerce').fillna(0.0)
        df_raw['Credit']  = pd.to_numeric(df_raw['Credit'],  errors='coerce').fillna(0.0)
        df_raw['Balance'] = pd.to_numeric(df_raw['Balance'], errors='coerce').fillna(0.0)

        df_raw['Date'] = pd.to_datetime(df_raw['Date'], format='%d %b %Y', errors='coerce')
        df_raw = df_raw.dropna(subset=['Date'])
        df_raw['Date'] = df_raw['Date'].dt.strftime('%Y-%m-%d')

        df_raw['Category'] = df_raw.apply(
            lambda r: get_category(r['Description_raw'], r['Debit'], r['Credit']), axis=1
        )

        df_raw['Description'] = df_raw.apply(
            lambda r: clean_description(r['Description_raw'], r['Category'],
                                        r['Debit'], r['Credit']), axis=1
        )

        # ==================== EXTRACT USER & BANK FROM HEADER ====================
        df_header = pd.read_csv(file_path, nrows=5, header=None)
        account_name = "Unknown"
        bank_name = "Unknown"
        for _, row in df_header.iterrows():
            row_vals = [str(v).strip() for v in row if pd.notna(v) and str(v).strip()]
            if len(row_vals) >= 2 and 'Account Name' in row_vals[0]:
                account_name = row_vals[1]
                break
        for _, row in df_header.iterrows():
            row_vals = [str(v).strip() for v in row if pd.notna(v) and str(v).strip()]
            if len(row_vals) >= 2 and 'Bank' in row_vals[0]:
                bank_name = row_vals[1]
                break
        if bank_name == "Unknown":
            bank_name = "Ecobank"

        final_df = df_raw[['Date', 'Category', 'Description', 'Debit', 'Credit', 'Balance']].copy()
        final_df['User'] = account_name
        final_df['Bank'] = bank_name

        save_path = Path(__file__).parent.parent / "backend" / "data" / "uploads" / f"{account_name.replace(' ', '_')}_Ecobank_Preprocessed.xlsx"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        final_df.to_excel(save_path, index=False)
        messagebox.showinfo("Success", f"Ecobank Preprocessing Complete!\nSaved to: {save_path}")

    except Exception as e:
        messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    ecobank_preprocessing()