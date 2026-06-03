import pandas as pd
import re
import numpy as np
from pathlib import Path

def opay_preprocessing(file_path: str, user_name: str, bank_name: str) -> pd.DataFrame:
    """
    Preprocess OPay bank statement into standardized 8-column format.
    
    Args:
        file_path: Path to the OPay statement file
        user_name: Name of the user for file naming
        bank_name: Name of the bank (OPay)
    
    Returns:
        DataFrame with standardized columns: Date, Description, Debit, Credit, Balance, Category, User, Bank
    """

    KEYWORDS = {
        "Airtime": ['AIRTIME', 'TOP UP'],
        "Mobile Data": [
            'DATA BUNDLE', 'DATA PLAN', 'DATAMTN', 'DATAGLO', 'DATAAIRTEL', 'DATA9MOBILE',
            'INTERNET SUBSCRIPTION', 'MOBILE DATA'
        ],
        "Betting": [
            'SPORTYBET', 'SPORTY', 'BET9JA', 'BET 9JA', '1XBET', '1X BET',
            'BETKING', 'BET KING', 'BETWAY', 'BET WAY', 'BETBONANZA', 'BET BONANZA',
            'NAIRABET', 'NAIRA BET', 'MSPORT', 'M SPORT', 'BETANO',
            'BETWINNER', 'BET WINNER', 'PARIPESA', 'PARI PESA', 'MELBET', 'MEL BET',
            'MEGAPARI', 'MEGA PARI', '22BET', '22 BET', 'BETPAWA', 'BET PAWA',
            'LIVESCOREBET', 'LIVESCORE BET', 'MOZZARTBET', 'MOZZART BET',
            'WAZOBET', 'WAZO BET', 'ACCESSBET', 'ACCESS BET', 'BETFAIR', 'BET FAIR',
            'BETLAND', 'BET LAND', 'GREENLOTTO', 'GREEN LOTTO', 'AFRIBET', 'AFRI BET',
            'ZEBET', 'ZE BET', 'FOOTBALLING', 'FOOTBALL BET'
        ],
        "Church": [
            'CHURCH', 'MINISTRY', 'MINISTRIES', 'CHAPEL', 'PARISH', 'CATHEDRAL',
            'MOSQUE', 'ASSEMBLY', 'FELLOWSHIP', 'MISSION', 'GOSPEL', 'APOSTOLIC',
            'EVANGELICAL', 'PENTECOSTAL', 'BAPTIST', 'CATHOLIC', 'ANGLICAN', 'RCCG',
            'WINNERS', 'DEEPER LIFE', 'SALVATION', 'MOUNTAIN OF FIRE', 'CHRIST EMBASSY',
            'DAYSTAR', 'LIVING FAITH', 'SANCTUARY', 'WORSHIP CENTRE', 'TITHE',
            'OFFERING', 'HEADQUARTERS'
        ],
        "SMS Charges": ['SMS SUBSCRIPTION', 'SMS CHARGE'],
        "Charges": [
            'ELECTRONIC MONEY TRANSFER LEVY', 'EMTL', 'VAT', 'VALUE ADDED TAX',
            'STAMP DUTY', 'COMMISSION', 'WTAX', 'USSD'
        ],
        "Utilities": ['ABUJA ELECTRICITY', 'ELECTRICITY', 'AEDC', 'PREPAID', 'EKEDC', 'IKEDC', 'KWH'],
        "Savings": [
            'SAFEBOX', 'SAVINGS', 'DEPOSIT', 'OWEALTH', 'O-WEALTH', 'O WEALTH',
            'SPEND AND SAVE', 'SPEND & SAVE', 'INTEREST EARNED', 'INTEREST'
        ],
        "POS Transaction": ['OPAY CARD PAYMENT', 'CARD PAYMENT']
    }

    WHOLE_WORD_CHARGES = [r'\bFEE\b', r'\bLEVY\b', r'\bCHARGE\b']

    def clean_text(text):
        text = re.sub(r'[-–—/\\|().,;:\'\"!?&@#%^*+=<>]+', ' ', text)
        text = re.sub(r'\s{2,}', ' ', text)
        return text.strip()

    def match_keyword(text, cat, keys):
        if any(k in text for k in keys):
            return True
        if cat == "Charges":
            if any(re.search(pattern, text) for pattern in WHOLE_WORD_CHARGES):
                return True
        return False

    def get_category(desc, credit):
        text = str(desc).upper()
        is_transfer = "TRANSFER TO" in text or "TRANSFER FROM" in text
        if is_transfer:
            TRANSFER_SAFE_CATS = ["Betting", "Church", "Savings", "Utilities", "Airtime", "Mobile Data"]
            for cat in TRANSFER_SAFE_CATS:
                if match_keyword(text, cat, KEYWORDS[cat]):
                    return cat
            return "P2P Transfer"
        for cat, keys in KEYWORDS.items():
            if match_keyword(text, cat, keys):
                return cat
        return "Others"

    def extract_narration(parts):
        if len(parts) <= 3:
            return ""
        raw_narration = parts[-1].strip()
        narration_match = re.search(
            r'(REFUND|PAYMENT|CONTRIBUTION|ALLOWANCE|LOAN|RENT|FOOD|SCHOOL|FEES|TITHE|SALARY|'
            r'RECHARGE|GIFT|TRANSFER|SUPPORT|BILL|LEVY|CHARGE|PURCHASE|DEPOSIT|WITHDRAWAL|'
            r'SAVINGS|FEEDING|MEDICAL|TRANSPORT|BUSINESS|PROJECT|BALANCE|SETTLEMENT)',
            raw_narration
        )
        if narration_match:
            narration = raw_narration[narration_match.start():].strip()
            narration = re.sub(r'\s+', ' ', narration).strip()
            narration = re.sub(r'\s+[A-Z]\s*$', '', narration).strip()
            narration = re.sub(r'\d{5,}.*$', '', narration).strip()
            return narration
        return ""

    def clean_description(desc, category, credit):
        raw = str(desc).upper().strip()
        if not raw or raw == 'NAN' or raw == '':
            return "NaN"

        id_match = re.search(r'\b(070|080|081|090|091|020)\d{8}\b|\b\d{10,11}\b', raw)
        identifier = id_match.group(0) if id_match else ""

        kwh_match = re.search(r'(\d+\.?\d*)\s*KWH', raw, re.IGNORECASE)
        kwh_val = kwh_match.group(0) if kwh_match else ""

        if category == "Utilities":
            parts = raw.split('|')
            provider = parts[2].strip() if len(parts) > 2 else "Utility Provider"
            return clean_text(f"Electricity purchase {kwh_val} through {provider}")

        if category == "Mobile Data":
            providers = ['MTN', 'DATAGLO', 'GLO', 'DATAMTN', 'AIRTEL', '9MOBILE']
            found_p = next((p for p in providers if p in raw), "").replace("DATA", "")
            return clean_text(f"Mobile Data payment to {identifier} {found_p}")

        if category == "Airtime":
            providers = ['MTN', 'GLO', 'AIRTEL', '9MOBILE']
            found_p = next((p for p in providers if p in raw), "")
            return clean_text(f"Airtime payment to {identifier} {found_p}")

        if category == "Betting":
            betting_platforms = [
                'SPORTYBET', 'BET9JA', '1XBET', 'BETKING', 'BETWAY',
                'BETBONANZA', 'NAIRABET', 'MSPORT', 'BETANO', 'BETWINNER',
                'PARIPESA', 'MELBET', 'MEGAPARI', '22BET', 'BETPAWA',
                'LIVESCOREBET', 'MOZZARTBET', 'WAZOBET', 'ACCESSBET',
                'BETFAIR', 'BETLAND', 'GREENLOTTO', 'AFRIBET', 'ZEBET',
                'FOOTBALLING', 'FOOTBALL BET'
            ]
            found_p = next((p for p in betting_platforms if p in raw), "Betting Platform")
            if credit > 0:
                return clean_text(f"Betting winnings from {found_p}")
            return clean_text(f"Betting payment to {found_p}")

        if category == "Church":
            church_text = re.sub(r'^TRANSFER (TO|FROM)\s+', '', raw.split('|')[0].strip(), flags=re.IGNORECASE)
            prefix = "Transfer from" if credit > 0 else "Transfer to"
            return clean_text(f"{prefix} {church_text.strip()}")

        if category == "Charges":
            if "USSD" in raw: return "USSD Charges"
            if "STAMP DUTY" in raw: return "Stamp Duty Charge"
            if "ELECTRONIC MONEY TRANSFER LEVY" in raw or "EMTL" in raw:
                return "Electronic Money Transfer Levy"
            if "VAT" in raw or "VALUE ADDED TAX" in raw: return "VAT Charge"
            if "COMMISSION" in raw: return "Commission Charge"
            return "Bank Charges"

        if category == "SMS Charges":
            return "SMS Subscription Charge"

        if category == "Savings":
            if "OWEALTH" in raw or "O-WEALTH" in raw or "O WEALTH" in raw:
                if "INTEREST" in raw: return "OWealth Interest Earned"
                if "WITHDRAWAL" in raw: return "OWealth Withdrawal"
                return "OWealth Deposit"
            if "SPEND AND SAVE" in raw or "SPEND & SAVE" in raw:
                return "Spend and Save Deposit"
            return "Savings Deposit"

        if category == "POS Transaction":
            parts = raw.split('|')
            merchant = parts[4].strip() if len(parts) > 4 else (parts[0].strip() if parts else "Unknown Merchant")
            merchant = re.sub(r'\s+', ' ', merchant).strip()
            prefix = "Card Payment from" if credit > 0 else "Card Payment to"
            return clean_text(f"{prefix} {merchant}")

        if category == "Others":
            main_part = raw.split('|')[0].strip()
            others_text = re.sub(r'\s+', ' ', main_part).strip()
            return clean_text(others_text)

        # ---- P2P Transfer ----
        parts = raw.split('|')
        main_part = parts[0].strip()

        pos_match = re.search(r'POS\s*TRANSFER[\s\-]+(.+)', main_part, re.IGNORECASE)
        if pos_match:
            person_name = pos_match.group(1).strip()
            for junk in ['NIP CR', 'NIP DR', 'OPAY', 'MONIEPOINT', 'MONIE POINT']:
                person_name = person_name.replace(junk, '').strip()
            return clean_text(f"Transfer to POS {person_name.strip()}")

        p2p_text = re.sub(r'^TRANSFER (TO|FROM)\s+', '', main_part, flags=re.IGNORECASE)
        for junk in ['NIP CR', 'NIP DR', 'OPAY', 'MONIEPOINT', 'MONIE POINT']:
            p2p_text = p2p_text.replace(junk, '')

        narration = extract_narration(parts)
        prefix = "Transfer from" if credit > 0 else "Transfer to"
        base = f"{prefix} {p2p_text.strip()}"
        if narration:
            return clean_text(f"{base} {narration.title()}")
        return clean_text(base)

    # Read and process the file
    try:
        header_df = (pd.read_csv(file_path, header=None, nrows=6)
                     if file_path.endswith(".csv")
                     else pd.read_excel(file_path, header=None, nrows=6))
        
        account_name = "OPay_Preprocessed"
        user_name = "Unknown User"   # Default

        for _, row in header_df.iterrows():
            for i, val in enumerate(row):
                if str(val).strip().upper() == "ACCOUNT NAME" and i + 1 < len(row):
                    name = str(row[i + 1]).strip()
                    if name and name.upper() != "NAN":
                        account_name = name.replace(" ", "_")
                        user_name = name.strip()          # <-- This is the User name
                        break

        df = (pd.read_csv(file_path, skiprows=6, header=0)
                  if file_path.endswith(".csv")
                  else pd.read_excel(file_path, skiprows=6, header=0))
        df.columns = [c.strip() for c in df.columns]

        for col in ['Debit(₦)', 'Credit(₦)', 'Balance After(₦)']:
            df[col] = (df[col].astype(str)
                              .str.replace('₦', '', regex=False)
                              .str.replace(',', '', regex=False)
                              .str.replace('--', '0', regex=False))
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        df['Date'] = pd.to_datetime(df['Value Date'], errors='coerce').dt.strftime('%Y-%m-%d')

        df['Category'] = df.apply(
            lambda r: get_category(r['Description'], r['Credit(₦)']), axis=1
        )
        df['Description'] = df.apply(
            lambda r: clean_description(r['Description'], r['Category'], r['Credit(₦)']), axis=1
        )

        final_df = df.rename(columns={
            'Debit(₦)':        'Debit',
            'Credit(₦)':       'Credit',
            'Balance After(₦)': 'Balance'
        })[['Date', 'Category', 'Description', 'Debit', 'Credit', 'Balance']]

        final_df = final_df.dropna(subset=['Date'])

        # Add the two new columns
        final_df['User'] = user_name
        final_df['Bank'] = "OPay"

        return final_df

    except Exception as e:
        raise ValueError(f"Could not process OPay file: {e}")
