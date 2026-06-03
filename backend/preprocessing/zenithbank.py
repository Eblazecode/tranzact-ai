import pdfplumber
import pandas as pd
import re
from pathlib import Path

def zenithbank_preprocessing(file_path: str, user_name: str, bank_name: str) -> pd.DataFrame:
    """
    Preprocess Zenith Bank statement into standardized 8-column format.
    
    Args:
        file_path: Path to Zenith Bank statement file
        user_name: Name of the user for file naming
        bank_name: Name of the bank (Zenith Bank)
    
    Returns:
        DataFrame with standardized columns: Date, Description, Debit, Credit, Balance, Category, User, Bank
    """

    KEYWORDS = {
        "Airtime": ['AIRTIME'],
        "Data Purchase": ['BUNDLE'],
        "Mobile Charges": [
            'ELECTRONIC MONEY TRANSFER LEVY', 'FGN - ELECTRONIC MONEY TRANSFER LEVY', 'EMTL'
        ],
        "SMS Charges": ['SMS FEE', 'SMS CHARGE', 'SMS SUBSCRIPTION'],
        "Charges": [
            'NIP CHARGE + VAT', 'CHARGE + VAT', 'CREDIT INTEREST ACQUIRED',
            'STAMP DUTY CHARGE', 'STAMP DUTY',
        ],
        "USSD Charges": ['USSD SESSION CHARGE', 'USSD CHARGE', 'USSD'],
        "School": ['TUITION', 'REMITA CHECKOUT'],
        "Hospital": ['PHARMACY', 'HOSPITAL', 'CLINIC', 'MEDICAL'],
        "Savings": ['CAPITALIZED INTEREST CREDIT'],
        "Tax": ['STATE WITHOLDING TAX', 'WITHOLDING TAX'],
        "Betting": [
            'SPORTYBET', 'SPORTY', 'BET9JA', 'BET 9JA', '1XBET',
            'BETKING', 'BETWAY', 'BETBONANZA', 'NAIRABET', 'MSPORT',
            'BETANO', 'BETWINNER', 'PARIPESA', 'MELBET', 'MEGAPARI',
            '22BET', 'BETPAWA', 'LIVESCOREBET', 'MOZZARTBET', 'WAZOBET',
            'ACCESSBET', 'BETFAIR', 'BETLAND', 'GREENLOTTO', 'AFRIBET',
            'ZEBET', 'FOOTBALL BET', 'BETTING'
        ],
        "Card Maintenance": [
            'MASTER CARD MAINTENANCE FEE', 'CARD MAINTENANCE FEE'
        ],
        "Refund": ['RVSL', 'REFUND'],
        "Church": [
            'CHURCH', 'MINISTRY', 'MINISTRIES', 'CHAPEL', 'PARISH', 'CATHEDRAL',
            'MOSQUE', 'ASSEMBLY', 'FELLOWSHIP', 'MISSION', 'GOSPEL', 'APOSTOLIC',
            'EVANGELICAL', 'PENTECOSTAL', 'BAPTIST', 'CATHOLIC', 'ANGLICAN', 'RCCG',
            'WINNERS', 'DEEPER LIFE', 'SALVATION', 'MOUNTAIN OF FIRE', 'CHRIST EMBASSY',
            'DAYSTAR', 'LIVING FAITH', 'SANCTUARY', 'WORSHIP CENTRE', 'TITHE',
            'OFFERING'
        ],
        "Utilities": [
            'ABUJA ELECTRICITY', 'ELECTRICITY', 'AEDC', 'PREPAID',
            'EKEDC', 'IKEDC', 'KWH', 'ELECTRICITY DISTRIBUTION'
        ],
        "Loan": [
            'ZEDVANCE', 'FAIRMONEY', 'CARBON', 'BRANCH', 'PALMCREDIT',
            'QUICKCHECK', 'AELLA', 'RENMONEY', 'MIGO', 'OKASH',
        ],
    }

    # Subscription platforms — only used when MC POS INTL is in text
    SUBSCRIPTION_KEYWORDS = [
        'NETFLIX', 'SPOTIFY', 'YOUTUBE', 'APPLE MUSIC', 'APPLE',
        'DSTV', 'SHOWMAX', 'AMAZON', 'DISNEY', 'HULU', 'CANVA',
        'CHATGPT', 'OPENAI', 'MICROSOFT', 'GOOGLE', 'DROPBOX',
        'ZOOM', 'ADOBE', 'LINKEDIN', 'TWITCH', 'PARAMOUNT',
        'HBO', 'PEACOCK', 'AUDIBLE', 'SUBSCRIPTION',
    ]

    # Betting platforms list (used for both category and description)
    BETTING_PLATFORMS = [
        'SPORTYBET', 'BET9JA', '1XBET', 'BETKING', 'BETWAY', 'BETBONANZA',
        'NAIRABET', 'MSPORT', 'BETANO', 'BETWINNER', 'PARIPESA', 'MELBET',
        'MEGAPARI', '22BET', 'BETPAWA', 'LIVESCOREBET', 'MOZZARTBET',
        'WAZOBET', 'ACCESSBET', 'BETFAIR', 'BETLAND', 'GREENLOTTO',
        'AFRIBET', 'ZEBET', 'SPORTY'
    ]

    # ── CATEGORY ─────────────────────────────────────────────────────────────
    def get_category(desc, credit=0):
        text = str(desc).upper().strip()
        if not text or text == 'NAN':
            return "Others"

        # ATM fee must come before ATM withdrawal check
        if re.search(r'ISO.*ATM.*WDL.*FEE|MC\s+LOC\s+ATM\s+WDL\s+FEE', text):
            return "Charges"

        # ATM WDL anywhere in text → ATM Withdrawal
        if 'ATM WDL' in text or re.search(r'MC\s+LOC\s+ATM\s+WDL', text):
            return "ATM Withdrawal"

        # Loan: NIP with PP:: pattern (loan disbursement)
        if re.search(r'NIP/\w+/.+/PP::', text):
            return "Loan"

        # MC POS Intl (no PRCH/PYT) — subscription or online purchase
        if 'MC POS INTL' in text:
            if any(k in text for k in SUBSCRIPTION_KEYWORDS):
                return "Subscription"
            return "Online Purchase"

        # MC Loc Web Prch → Online Purchase
        if re.search(r'MC\s+LOC\s+WEB\s+PRCH', text):
            return "Online Purchase"

        # POS Prch or POS Pyt → always POS Transaction
        if re.search(r'POS\s+PRCH|POS\s+PYT', text):
            return "POS Transaction"

        # TRF FRM ... TO ...
        if re.match(r'TRF\s+FRM\s+', text):
            return "P2P Transfer"

        # NIP CR/MOB with WITHDRAW → Card Withdrawal
        if ('NIP CR/MOB' in text or 'NIP CR MOB' in text) and 'WITHDRAW' in text:
            return "Card Withdrawal"

        # NIP CR/MOB/Remita Checkout/TUITION → School
        if ('NIP CR/MOB' in text or 'NIP CR MOB' in text):
            if 'TUITION' in text or 'REMITA CHECKOUT' in text:
                return "School"
            return "P2P Transfer"

        # NIP CR (space before CR, incoming)
        if re.match(r'NIP\s+CR/', text):
            return "P2P Transfer"

        for cat, keys in KEYWORDS.items():
            if keys and any(k in text for k in keys):
                return cat

        if re.search(r'QTR\s+\d\s+MASTER', text):
            return "Card Maintenance"

        nip_m = re.search(r'^NIP/\w+/(.+?)/(.+)', text)
        if nip_m:
            narration = nip_m.group(2).strip()
            if 'TUITION' in narration:
                return "School"
            return "P2P Transfer"

        if re.match(r'NIP/', text):
            return "P2P Transfer"
        if ':ETZ INFLOW' in text:
            return "P2P Transfer"
        if text.startswith('CIP'):
            return "P2P Transfer"
        if text.startswith('TRANSFER FROM'):
            return "P2P Transfer"

        if re.match(r'\d{8,}/', text):
            return "Mobile Purchase"

        return "Others"

    # ── DESCRIPTION ──────────────────────────────────────────────────────────
    def clean_description(desc, category, credit=0):
        raw = str(desc).strip()
        upper = raw.upper()
        is_credit = float(credit) > 0

        if category == "Airtime":
            m = re.search(r'Airtime//([\d\s]+)//', raw, re.IGNORECASE)
            phone = m.group(1).replace(' ', '').strip() if m else ''
            return f"Airtime Payment to {phone}" if phone else "Airtime Top Up"

        if category == "Data Purchase":
            m = re.search(r'Bundle//([\d\s]+)//', raw, re.IGNORECASE)
            phone = m.group(1).strip() if m else ''
            return f"Data Bundle Purchase to {phone}" if phone else "Data Bundle"

        if category == "Mobile Charges":
            return "Electronic Money Transfer Levy"

        if category == "SMS Charges":
            return raw

        if category == "Charges":
            if 'NIP CHARGE' in upper or 'CHARGE + VAT' in upper:
                return "NIP Transfer Charge + VAT"
            if 'CREDIT INTEREST' in upper:
                return "Credit Interest Charge"
            if 'STAMP DUTY' in upper:
                return "Stamp Duty Charge"
            if re.search(r'ISO.*ATM.*WDL.*FEE|MC\s+LOC\s+ATM\s+WDL\s+FEE', upper):
                return "ATM Withdrawal Fee"
            return "Bank Charges"

        if category == "USSD Charges":
            return "USSD Session Charge"

        if category == "ATM Withdrawal":
            loc = _extract_atm_location(raw)
            if loc:
                return f"ATM Cash Withdrawal at {loc}"
            m = re.search(r'(?:ATM\d*|ZIB)[,\s\-]+([A-Z][A-Z\s]+?)(?:\s+LANG|\s+NG-|$)', raw, re.IGNORECASE)
            if m:
                return f"ATM Cash Withdrawal at {m.group(1).strip().title()}"
            return "ATM Cash Withdrawal"

        if category == "School":
            return "School Tuition Payment via Remita"

        if category == "Hospital":
            name = _extract_pos_name(raw)
            if name:
                return f"POS Payment - {name}"
            nip_m = re.search(r'NIP/\w+/(.+?)/(.+)', raw, re.IGNORECASE)
            if nip_m:
                return f"Transfer to {nip_m.group(1).strip().title()} for Medical"
            return "Medical Payment"

        if category == "Savings":
            return "Capitalized Interest Credit"

        if category == "Tax":
            return "State Withholding Tax"

        if category == "Betting":
            if re.search(r"SP[\s]?ORTYBET|SPORTYBET", upper):
                platform = "SPORTYBET"
            else:
                platform = next((p for p in BETTING_PLATFORMS if p in upper and not (p == "MSPORT" and "COMSPORTY" in upper)), None)
            if is_credit:
                if platform:
                    return f"Betting Winnings Received from {platform.title()}"
                if 'PAYSTACK' in upper:
                    return "Betting Winnings Received via Paystack"
                return "Betting Winnings Received"
            else:
                if platform:
                    return f"Betting Deposit to {platform.title()}"
                if 'PAYSTACK' in upper:
                    return "Betting Deposit via Paystack"
                return "Betting Deposit"

        if category == "Card Maintenance":
            m1 = re.search(r'(\d{4})\s+Qtr\s+(\d)', raw, re.IGNORECASE)
            if m1:
                return f"Master Card Maintenance Fee Qtr {m1.group(2)} {m1.group(1)}"
            m2 = re.search(r'Qtr\s+(\d)\s+MASTER', raw, re.IGNORECASE)
            if m2:
                return f"Master Card Maintenance Fee Qtr {m2.group(1)}"
            return "Master Card Maintenance Fee"

        if category == "POS Transaction":
            name = _extract_pos_name(raw)
            return f"POS Payment - {name}" if name else "POS Transaction"

        if category == "Online Purchase":
            dlo = re.search(r'DLO\*([A-Z0-9]+)', raw, re.IGNORECASE)
            if dlo:
                return f"Online Purchase - {dlo.group(1).strip().title()}"
            web = re.search(r'MC\s+Loc\s+Web\s+Prch-\d+-+\s*(.+?)(?:\s{2,}|\s+Lagos|\s+NG|$)', raw, re.IGNORECASE)
            if web:
                return f"Online Purchase - {web.group(1).strip().title()}"
            name = _extract_pos_intl_name(raw)
            return f"Online Purchase - {name}" if name else "Online Purchase"

        if category == "Subscription":
            for platform in SUBSCRIPTION_KEYWORDS:
                if platform in upper and platform != 'SUBSCRIPTION':
                    return f"Online Subscription - {platform.title()}"
            name = _extract_pos_intl_name(raw)
            return f"Online Subscription - {name}" if name else "Online Subscription"

        if category == "Loan":
            m = re.search(r'NIP/\w+/(.+?)/', raw, re.IGNORECASE)
            lender = m.group(1).strip().title() if m else ''
            return f"Loan Credit from {lender}" if lender else "Loan Credit"

        if category == "Mobile Purchase":
            return "Mobile Purchase"

        if category == "Card Withdrawal":
            m = re.search(r'NIP CR/?MOB/(.+?)/\w+\s*/?\s*Withdraw', raw, re.IGNORECASE)
            if m:
                return f"Cash Withdrawal by {m.group(1).strip().title()}"
            m = re.search(r'NIP CR MOB\s+(.+?)\s+\w+\s*/?\s*Withdraw', raw, re.IGNORECASE)
            if m:
                return f"Cash Withdrawal by {m.group(1).strip().title()}"
            return "Cash Withdrawal"

        if category == "Refund":
            if 'RVSL' in upper:
                detail = re.sub(r'RVSL\s*', '', raw, flags=re.IGNORECASE).strip()
                return f"Reversal - {detail}"
            m = re.search(r'NIP/\w+/(.+?)/REFUND', raw, re.IGNORECASE)
            if m:
                return f"Refund from {m.group(1).strip().title()}"
            return f"Refund - {raw}"

        if category == "Church":
            m = re.search(r'(?:Send to|NIP CR/?MOB)\s*(.+)', raw, re.IGNORECASE)
            return f"Transfer to {m.group(1).strip().title()}" if m else raw

        if category == "Utilities":
            return "Electricity Bill Payment"

        if category == "P2P Transfer":
            return _p2p_description(raw)

        if category == "Others":
            dlo_m = re.search(r'DLO\*(\S+)', raw, re.IGNORECASE)
            if dlo_m:
                return f"Online Purchase - {dlo_m.group(1).strip().title()}"
            return raw

        return raw

    # ── HELPERS ───────────────────────────────────────────────────────────────
    def _extract_atm_location(raw):
        m = re.search(
            r'MC\s+Loc\s+ATM\s+Wdl-\d+--(.+?)(?:\s{2,}|\s+NG-|\s+LANG-|$)',
            raw, re.IGNORECASE
        )
        if m:
            return m.group(1).strip().title()
        m = re.search(
            r'MC\s+ATM\s+Wdl-\d+--(.+?)(?:\s{2,}|\s+NG-|\s+LANG-|$)',
            raw, re.IGNORECASE
        )
        if m:
            return m.group(1).strip().title()
        m = re.search(
            r'ATM\s+Wdl\s+Fee-\d+--(.+?)(?:\s{2,}|\s+NG-|\s+LANG-|$)',
            raw, re.IGNORECASE
        )
        if m:
            return m.group(1).strip().title()
        return ''

    def _extract_pos_name(raw):
        m = re.search(
            r'MC\s+Loc\s+POS\s+Prch-\d+--(.+?)(?:\s{2,}|\s+LANG-|\s+NG-|$)',
            raw, re.IGNORECASE
        )
        if m:
            return m.group(1).strip().title()
        m = re.search(r'MC\s+Loc\s+POS\s+Prch-\d+--(.+)', raw, re.IGNORECASE)
        if m:
            name = re.sub(r'\s+(LANG-|NG-)\s*$', '', m.group(1), flags=re.IGNORECASE).strip()
            return name.title()
        m = re.search(r'MC\s+POS\s+Pyt-\d+-+\w+-T\s+(.+?)\s+\d{6}', raw, re.IGNORECASE)
        if m:
            return m.group(1).strip().title()
        m = re.search(r'--T\s+(.+?)\s+\d{6}', raw, re.IGNORECASE)
        if m:
            return m.group(1).strip().title()
        return ''

    def _extract_pos_intl_name(raw):
        m = re.search(r'MC\s+POS\s+Intl-(.+?)\s*-', raw, re.IGNORECASE)
        return m.group(1).strip().title() if m else ''

    def _p2p_description(raw):
        SKIP = {'TR', 'TRF', 'TRANSFER', ''}

        m = re.search(r'TRF\s+FRM\s+(.+?)\s+TO\s+(.+?)(?:\|(.+))?$', raw, re.IGNORECASE)
        if m:
            sender    = m.group(1).strip().title()
            recipient = m.group(2).strip().title()
            narration = m.group(3).strip().title() if m.group(3) else ''
            if narration:
                return f"Transfer from {sender} to {recipient} for {narration}"
            return f"Transfer from {sender} to {recipient}"

        m = re.search(r'NIP\s+CR/(.+?)/(\w+)$', raw, re.IGNORECASE)
        if m:
            return f"Transfer from {m.group(1).strip().title()}"

        m = re.search(r'NIP/FDP/(.+?)/ONB TRF FROM', raw, re.IGNORECASE)
        if m:
            return f"Transfer from {m.group(1).strip().title()}"

        if re.match(r'^NIP/\w+/.+/$', raw.strip()):
            m = re.search(r'^NIP/\w+/(.+?)/$', raw.strip(), re.IGNORECASE)
            if m:
                return f"Transfer from {m.group(1).strip().title()}"

        m = re.search(r'^NIP/\w+/(.+?)/(.+)', raw, re.IGNORECASE)
        if m:
            name      = m.group(1).strip().title()
            narration = m.group(2).strip()
            n_up      = narration.upper()
            if (n_up in SKIP or n_up.startswith('TRANSFER FROM') or
                    n_up.startswith('ONB TRF') or n_up.startswith('TRF FROM')):
                return f"Transfer from {name}"
            return f"Transfer from {name} for {narration.title()}"

        m = re.search(r'NIP CR/MOB/(.+?)/\w+\s*/\s*(.+)', raw, re.IGNORECASE)
        if m:
            name      = m.group(1).strip().title()
            narration = m.group(2).strip()
            n_up      = narration.upper()
            if n_up in SKIP or n_up in {'TRANSFER', 'PAYMENT'}:
                return f"Payment to {name}"
            return f"Payment to {name} for {narration.title()}"

        m = re.search(
            r'NIP CR MOB\s+(.+?)\s+'
            r'(?:OPAY|GTB|FDP|ROLEZ|FBN|UBA|ACCESS|ZENITH|FCMB|POLARIS|WEMA|FIRST|KEYSTONE|HERITAGE)\s*/?\s*(.*)',
            raw, re.IGNORECASE
        )
        if m:
            name      = m.group(1).strip().title()
            narration = m.group(2).strip()
            if narration and narration.upper() not in SKIP:
                return f"Payment to {name} for {narration.title()}"
            return f"Payment to {name}"

        m = re.search(r'TRANSFER FROM (.+?)(?:;|\d{8,}|$)', raw, re.IGNORECASE)
        if m:
            return f"Transfer from {m.group(1).strip().title()}"

        m = re.search(r'CIP/CR//Transfer from (.+?)(?:\s+\d{10,}|$)', raw, re.IGNORECASE)
        if m:
            return f"Transfer from {m.group(1).strip().title()}"

        m = re.search(r'CIP\|[^|]+\|(.+?)\|', raw, re.IGNORECASE)
        if m:
            return f"Transfer from {m.group(1).strip().title()}"

        m = re.search(r'^Transfer from (.+)$', raw, re.IGNORECASE)
        if m:
            return f"Transfer from {m.group(1).strip().title()}"

        return raw

    # ── EXTRACT ACCOUNT NAME FROM PDF ────────────────────────────────────────
    def extract_account_name_from_pdf(pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            first_page_text = pdf.pages[0].extract_text() or ''
        patterns = [
            r'ACCOUNT NAME[:\s]+([A-Z][A-Z\s]+?)(?:\n|Account Statement)',
            r'ACCOUNT NAME[:\s]+(.+?)(?:\n)',
        ]
        for pattern in patterns:
            m = re.search(pattern, first_page_text, re.IGNORECASE)
            if m:
                name = m.group(1).strip()
                return re.sub(r'\s+', '_', name).upper()
        return "Unknown_Account_Holder"

    # ── EXTRACT TRANSACTIONS FROM PDF ────────────────────────────────────────
    def extract_transactions_from_pdf(pdf_path):
        rows = []
        opening_balance = 0.0
        header_found = False

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        cleaned = [str(c).replace('\n', ' ').strip() if c else '' for c in row]
                        full = ' '.join(cleaned)

                        if ('DESCRIPTION' in full.upper() and
                                'DEBIT' in full.upper() and
                                'CREDIT' in full.upper()):
                            header_found = True
                            continue

                        if not header_found:
                            continue

                        if 'OPENING BALANCE' in full.upper():
                            for c in reversed(cleaned):
                                try:
                                    opening_balance = float(c.replace(',', '').strip())
                                    break
                                except Exception:
                                    continue
                            continue

                        if 'TOTALS' in full.upper():
                            continue

                        date_str = cleaned[0].strip() if cleaned else ''
                        if not re.match(r'\d{2}/\d{2}/\d{4}', date_str):
                            continue

                        if len(cleaned) < 5:
                            continue

                        description = cleaned[1] if len(cleaned) > 1 else ''
                        debit_raw   = cleaned[2] if len(cleaned) > 2 else '0'
                        credit_raw  = cleaned[3] if len(cleaned) > 3 else '0'
                        balance_raw = cleaned[5] if len(cleaned) > 5 else cleaned[-1]

                        rows.append({
                            'raw_date':    date_str,
                            'description': description,
                            'debit_raw':   debit_raw,
                            'credit_raw':  credit_raw,
                            'balance_raw': balance_raw,
                        })

        return rows, opening_balance

    # ── MAIN PROCESSING ─────────────────────────────────────────────────────
    try:
        account_name = extract_account_name_from_pdf(file_path)
        rows, opening_balance = extract_transactions_from_pdf(file_path)

        if not rows:
            raise ValueError('No transaction data found in PDF.')

        df = pd.DataFrame(rows)

        df['Date'] = pd.to_datetime(
            df['raw_date'], format='%d/%m/%Y', errors='coerce'
        ).dt.strftime('%Y-%m-%d')

        df['Debit'] = pd.to_numeric(
            df['debit_raw'].str.replace(',', '', regex=False), errors='coerce'
        ).fillna(0)

        df['Credit'] = pd.to_numeric(
            df['credit_raw'].str.replace(',', '', regex=False), errors='coerce'
        ).fillna(0)

        df['Balance'] = pd.to_numeric(
            df['balance_raw'].str.replace(',', '', regex=False), errors='coerce'
        )

        df['Category']    = df.apply(lambda r: get_category(r['description'], r['Credit']), axis=1)
        df['Description'] = df.apply(
            lambda r: clean_description(r['description'], r['Category'], r['Credit']), axis=1
        )

        final_df = df[
            ['Date', 'Category', 'Description', 'Debit', 'Credit', 'Balance']
        ].dropna(subset=['Date'])

        # ====================== ADD USER AND BANK COLUMNS ======================
        # Added exactly as requested - after the Balance column
        final_df['User'] = account_name.replace("_", " ")
        final_df['Bank'] = "Zenith Bank"

        return final_df

    except Exception as e:
        raise ValueError(f"Could not process Zenith Bank file: {e}")
