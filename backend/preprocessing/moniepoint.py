import pandas as pd
import re
import numpy as np
from pathlib import Path


def moniepoint_preprocessing(file_path: str, user_name: str, bank_name: str) -> pd.DataFrame:
    """
    Preprocess Moniepoint bank statement into standardized 8-column format.
    
    Args:
        file_path: Path to the Moniepoint statement file
        user_name: Name of the user for file naming
        bank_name: Name of the bank (Moniepoint)
    
    Returns:
        DataFrame with standardized columns: Date, Description, Debit, Credit, Balance, Category, User, Bank
    """

    KEYWORDS = {
        "Airtime": ['AIRTIME', 'TOP UP'],

        "Data Purchase": [
            'DATA BUNDLE', 'DATA PLAN', 'DATAMTN', 'DATAGLO', 'DATAAIRTEL', 'DATA9MOBILE',
            'INTERNET SUBSCRIPTION', 'MOBILE DATA', 'DATA PURCHASE',
        ],

        "Betting": [
            'SPORTYBET', 'SPORTY', 'BET9JA', '1XBET',
            'BETKING', 'BETWAY', 'BETBONANZA', 'NAIRABET', 'MSPORT',
            'BETANO', 'BETWINNER', 'PARIPESA', 'MELBET', 'MEGAPARI',
            '22BET', 'BETPAWA', 'LIVESCOREBET', 'MOZZARTBET', 'WAZOBET',
            'ACCESSBET', 'BETFAIR', 'BETLAND', 'GREENLOTTO', 'AFRIBET',
            'ZEBET', 'FOOTBALLBET', 'BETTING', 'FOOTBALL BET',
        ],

        "Church": [
            'CHURCH', 'MINISTRY', 'MINISTRIES', 'CHAPEL', 'PARISH', 'CATHEDRAL',
            'MOSQUE', 'ASSEMBLY', 'FELLOWSHIP', 'MISSION', 'GOSPEL', 'APOSTOLIC',
            'EVANGELICAL', 'PENTECOSTAL', 'BAPTIST', 'CATHOLIC', 'ANGLICAN', 'RCCG',
            'WINNERS', 'DEEPER LIFE', 'SALVATION', 'MOUNTAIN OF FIRE', 'CHRIST EMBASSY',
            'DAYSTAR', 'LIVING FAITH', 'SANCTUARY', 'WORSHIP CENTRE', 'TITHE',
            'OFFERING', 'HEADQUARTERS',
        ],

        "SMS Charges": ['SMS SUBSCRIPTION', 'SMS CHARGE', 'SMS'],

        "Charges": [
            'ELECTRONIC MONEY TRANSFER LEVY', 'EMTL',
            'VAT', 'VALUE ADDED TAX', 'STAMP DUTY', 'COMMISSION', 'BANK CHARGE',
            'TRANSFER FEE', 'SERVICE FEE', 'MAINTENANCE FEE', 'LEVY', 'WTAX', 'USSD',
        ],

        "Electricity": [
            'ELECTRICITY', 'PREPAID', 'KWH', 'ELECTRIC',
            'ELECTRICITY DISTRIBUTION', 'ELECTRICITY BILL',
            'AEDC', 'ABUJA ELECTRICITY', 'EKEDC', 'EKO ELECTRICITY',
            'IKEDC', 'IKEJA ELECTRICITY', 'PHED', 'PORT HARCOURT ELECTRICITY',
            'EEDC', 'ENUGU ELECTRICITY', 'BEDC', 'BENIN ELECTRICITY',
            'KAEDCO', 'KADUNA ELECTRICITY', 'KEDCO', 'KANO ELECTRICITY',
            'JEDC', 'JOS ELECTRICITY', 'YEDC', 'YOLA ELECTRICITY',
            'IBEDC', 'IBADAN ELECTRICITY', 'BILL PAYMENT FOR MURTALA',
            'NEPA', 'PHCN',
        ],

        "Savings": [
            'SAFEBOX', 'SAVINGS', 'DEPOSIT',
            'SPEND AND SAVE', 'SPEND & SAVE', 'INTEREST EARNED', 'INTEREST',
            'PB_SAV_ACCT_INTEREST', 'INTR',
        ],
    }

    POS_PURCHASE_PATTERNS = ['POS PURCHASE AT', 'POS PURCHASE']

    # ==================== HELPERS ============================================

    def clean_text(text):
        text = re.sub(r'[-–—/\\|().,;:\'\"!?&@#%^*+=<>]+', ' ', text)
        text = re.sub(r'\s{2,}', ' ', text)
        return text.strip()

    def is_credit(credit):
        try:
            return float(credit or 0) > 0
        except (ValueError, TypeError):
            return False

    def parse_compact_nip(text):
        m = re.match(r'^NIP([A-Z][A-Z\s]+?)(\d{5,})([A-Z][A-Z\s]+)$', text.strip())
        if m:
            return m.group(1).strip(), m.group(3).strip()
        return None, None

    def parse_name_plus_number(text):
        m = re.match(r'^([A-Z][A-Z\s]{3,}?)[\s:]*(\d{7,11})\s*$', text.strip())
        if m:
            return m.group(1).strip()
        return None

    def parse_word_to_name_ref(text):
        normalised = re.sub(r'[.:]', ' ', text)
        m = re.match(r'^([A-Z][A-Z\s]{1,20}?)\s+TO\s+[A-Z][A-Z\s]+\d{10,}',
                     normalised.strip(), re.IGNORECASE)
        if m:
            return m.group(1).strip()
        return None

    # ==================== CATEGORY ===========================================

    def get_category(narration, tref, debit, credit):
        tref_str = str(tref).upper()

        if 'INTR' in tref_str or 'PB_SAV_ACCT_INTEREST' in tref_str: return "Savings"
        if 'EMTL' in tref_str: return "Charges"
        if 'VAT_OUTPUT' in tref_str: return "Charges"

        text = str(narration).upper().strip()
        if not text or text == 'NAN': return "Others"

        text_nospace = text.replace(' ', '')

        if any(p in text for p in POS_PURCHASE_PATTERNS):
            return "POS Transaction"

        for cat, keys in KEYWORDS.items():
            if cat == "Betting":
                if any(k.replace(' ', '') in text_nospace for k in keys):
                    return cat
            else:
                if any(k in text for k in keys):
                    return cat

        if 'VAT_OUTPUT' in text: return "Charges"
        if 'REMITA' in text: return "Online Transfer"
        if 'TRANSFER TO' in text or 'TRANSFER FROM' in text: return "P2P Transfer"
        if 'MOBILE TRF' in text or 'MMF' in text: return "P2P Transfer"
        if re.search(r'^TRF.{0,20}FRM\s+', text): return "P2P Transfer"
        if re.match(r'^NIP', text): return "P2P Transfer"
        if 'POS TRANSFER AT' in text: return "P2P Transfer"

        if re.search(r'\bFROM\b', text): return "P2P Transfer"

        if re.match(r'^MFDS', text): return "P2P Transfer"
        if re.search(r' TO .+ MONIEPOINT \*', text): return "P2P Transfer"
        if re.search(r'\|TRF\|', text): return "P2P Transfer"
        if re.match(r'^(ATP|BPT|DTP)\|', text): return "P2P Transfer"
        if 'PERSONAL TRANSFER' in text: return "P2P Transfer"
        if 'NIP TRANSFER' in text: return "P2P Transfer"

        if re.match(r'^MOB', text): return "P2P Transfer"

        if parse_name_plus_number(text): return "P2P Transfer"
        if parse_word_to_name_ref(text): return "P2P Transfer"

        stripped = text.strip()
        if stripped and len(stripped.split()) <= 10:
            if not re.search(r'\d{6,}', stripped) and '|' not in stripped:
                return "P2P Transfer"

        return "Others"

    # ==================== DESCRIPTION ========================================

    def clean_description(narration, tref, category, debit, credit):
        raw = re.sub(r'\s+', ' ', str(narration).upper()).strip()
        tref_str = re.sub(r'\s+', ' ', str(tref).upper()).strip()
        incoming = is_credit(credit)
        direction = "Transfer from" if incoming else "Transfer to"

        if category == "Savings":
            if 'PB_SAV_ACCT_INTEREST' in tref_str or 'INTR' in tref_str:
                m = re.search(r'(\d{4}-\d{2})', tref_str)
                return clean_text(f"Moniepoint Savings Interest Earned {m.group(1) if m else ''}".strip())
            return "Savings Deposit"

        if category == "Online Transfer":
            return "Payment via Remita Checkout"

        if category == "Charges":
            if 'ELECTRONIC MONEY TRANSFER LEVY' in raw or 'EMTL' in tref_str:
                return "Electronic Money Transfer Levy"
            if 'VAT_OUTPUT' in tref_str or 'VAT_OUTPUT' in raw: return "Bank VAT Charge"
            if 'USSD' in raw: return "USSD Charges"
            if 'STAMP DUTY' in raw: return "Stamp Duty Charge"
            if 'VAT' in raw or 'VALUE ADDED TAX' in raw: return "Bank VAT Charge"
            return "Bank Charges"

        if not raw or raw == 'NAN': return "Others"

        if '_RVSL' in tref_str or '_RVSL' in raw:
            if 'VAT_OUTPUT' in tref_str or 'VAT_OUTPUT' in raw: return "Bank VAT Charge Reversal"
            if 'MSPORT' in raw or 'SPORTY' in raw: return "Betting Reversal"
            pipe_r = re.match(r'^(.+?)\|TRF\|', raw)
            if pipe_r: return clean_text(f"Reversal Transfer to {pipe_r.group(1).strip().title()}")
            return "Transaction Reversal"

        raw_clean = re.split(r'/(TRF|ATP|BPT|DTP)\|', raw)[0].strip()

        if re.match(r'^ATP\|', raw_clean): return "Automated Transfer Payment"
        if re.match(r'^BPT\|', raw_clean): return "Bill Payment"
        if re.match(r'^DTP\|', raw_clean): return "Direct Transfer Payment"

        if category == "Airtime":
            providers = ['MTN', 'GLO', 'AIRTEL', '9MOBILE']
            id_m = re.search(r'(0\d{10}|\d{11})', raw_clean)
            identifier = id_m.group(0) if id_m else ""
            found_p = next((p for p in providers if p in raw_clean), "")
            return clean_text(f"Airtime Purchase to {identifier} {found_p}".strip())

        if category == "Data Purchase":
            providers = ['MTN', 'GLO', 'AIRTEL', '9MOBILE']
            id_m = re.search(r'(0\d{10}|\d{11})', raw_clean)
            identifier = id_m.group(0) if id_m else ""
            found_p = next((p for p in providers if p in raw_clean), "")
            return clean_text(f"Data Purchase to {identifier} {found_p}".strip())

        if category == "Betting":
            raw_clean_nospace = raw_clean.replace(' ', '')
            betting_platforms = [
                'SPORTYBET', 'BET9JA', '1XBET', 'BETKING', 'BETWAY',
                'BETBONANZA', 'NAIRABET', 'MSPORT', 'BETANO', 'BETWINNER',
                'PARIPESA', 'MELBET', 'MEGAPARI', '22BET', 'BETPAWA',
                'LIVESCOREBET', 'MOZZARTBET', 'WAZOBET', 'ACCESSBET',
                'BETFAIR', 'BETLAND', 'GREENLOTTO', 'AFRIBET', 'ZEBET',
                'FOOTBALLING', 'FOOTBALLBET',
            ]
            found_p = next((p for p in betting_platforms if p in raw_clean_nospace), "Betting Platform")
            if incoming:
                return clean_text(f"Betting Credit from {found_p.title()}")
            return clean_text(f"Betting Payment to {found_p.title()}")

        if category == "Electricity":
            DISCO_NAMES = {
                'AEDC': 'AEDC', 'ABUJA ELECTRICITY': 'AEDC',
                'EKEDC': 'EKEDC', 'EKO ELECTRICITY': 'EKEDC',
                'IKEDC': 'IKEDC', 'IKEJA ELECTRICITY': 'IKEDC',
                'PHED': 'PHED', 'PORT HARCOURT ELECTRICITY': 'PHED',
                'EEDC': 'EEDC', 'ENUGU ELECTRICITY': 'EEDC',
                'BEDC': 'BEDC', 'BENIN ELECTRICITY': 'BEDC',
                'KAEDCO': 'KAEDCO', 'KADUNA ELECTRICITY': 'KAEDCO',
                'KEDCO': 'KEDCO', 'KANO ELECTRICITY': 'KEDCO',
                'JEDC': 'JEDC', 'JOS ELECTRICITY': 'JEDC',
                'YEDC': 'YEDC', 'YOLA ELECTRICITY': 'YEDC',
                'IBEDC': 'IBEDC', 'IBADAN ELECTRICITY': 'IBEDC',
                'NEPA': 'NEPA', 'PHCN': 'PHCN',
            }
            found_disco = next((DISCO_NAMES[k] for k in DISCO_NAMES if k in raw_clean), "")
            tok = re.search(r'(\d{11,})', raw_clean)
            meter = tok.group(1) if tok else ""
            return clean_text(f"Electricity Purchase {found_disco} {meter}".strip())

        if category == "SMS Charges":
            return "SMS Subscription Charge"

        if category == "Church":
            church_text = re.sub(r'^TRANSFER (TO|FROM)\s+', '', raw_clean, flags=re.IGNORECASE).strip()
            return clean_text(f"{direction} {church_text.title()}")

        if category == "POS Transaction":
            pos_name_match = re.search(
                r'POS (?:PURCHASE|TRANSFER) AT\s+(?:T\s+)?(.+?)(?:\s+\d{3,})?$',
                raw_clean, re.IGNORECASE
            )
            if pos_name_match:
                name = pos_name_match.group(1).strip()
                name = re.sub(r'\s+(MFB|BANK|LTD|PLC|NIG).*$', '', name, flags=re.IGNORECASE).strip()
                name = re.sub(r'\*+\d*.*$', '', name).strip()
                return clean_text(f"POS Purchase at {name.title()}")
            return "POS Purchase"

        if category == "P2P Transfer":

            pos_trf_match = re.search(
                r'TRANSFER TO POS\s*(?:TRANSFER)?[\s\-]+(.+?)(?:\s+(?:MONIEPOINT|OPAY|FIRST BANK|GTB|UBA|ZENITH|WEMA|PROVIDUS|ACCESS|FIDELITY|POLARIS|STERLING|KEYSTONE|HERITAGE|TITAN|UNION|STANDARD|CASHCONNECT|MICROFINANCE|MFB).*)?$',
                raw_clean, re.IGNORECASE
            )
            if pos_trf_match:
                name = re.sub(r'\*+\d+.*$', '', pos_trf_match.group(1)).strip()
                name = re.sub(r'\s+(MFB|BANK|LTD).*$', '', name, flags=re.IGNORECASE).strip()
                return clean_text(f"Transfer to POS {name.title()}")

            pos_agent_match = re.search(r'TRANSFER TO (.+?)\s+POS AGENT', raw_clean, re.IGNORECASE)
            if pos_agent_match:
                return clean_text(f"Transfer to POS {pos_agent_match.group(1).strip().title()}")

            if 'POS TRANSFER AT' in raw_clean:
                return clean_text(raw_clean.title())

            mobile_trf_match = re.search(
                r'MOBILE TRF TO MMF\s+(.+?)(?:\s+\d+.*)?$',
                raw_clean, re.IGNORECASE
            )
            if mobile_trf_match:
                name = mobile_trf_match.group(1).strip()
                name_parts = name.split()
                real_name_parts = []
                for part in reversed(name_parts):
                    if re.match(r'^[A-Z]+$', part):
                        real_name_parts.insert(0, part)
                        if len(real_name_parts) >= 3:
                            break
                    else:
                        break
                if real_name_parts:
                    name = ' '.join(real_name_parts)
                return clean_text(f"{direction} {name.title()}")

            trf_frm_match = re.search(
                r'TRF.{0,30}FRM\s+(.+?)\s+TO\s+',
                raw_clean, re.IGNORECASE
            )
            if trf_frm_match:
                return clean_text(f"Transfer from {trf_frm_match.group(1).strip().title()}")

            party_a, party_b = parse_compact_nip(raw_clean)
            if party_a and party_b:
                if incoming:
                    return clean_text(f"Transfer from {party_b.title()}")
                else:
                    return clean_text(f"Transfer to {party_b.title()}")

            nip_from_match = re.search(
                r'NIP.*?FROM\s+([A-Z][A-Z\s\-]+?)(?:\s*$)',
                raw_clean, re.IGNORECASE
            )
            if nip_from_match:
                name = nip_from_match.group(1).strip()
                return clean_text(f"{direction} {name.title()}")

            nip_match = re.search(r'NIP TRANSFER TO\s+(.+?)(?:\s*\.\s*\d+.*)?$', raw_clean)
            if nip_match:
                name = re.sub(r'\s*\.\s*\d+.*$', '', nip_match.group(1)).strip()
                return clean_text(f"Transfer to {name.title()}")

            mob_from_match = re.search(r'\bFROM\s+([A-Z][A-Z\s\-]+?)(?:\s*$)', raw_clean, re.IGNORECASE)
            if mob_from_match:
                name = mob_from_match.group(1).strip()
                return clean_text(f"{direction} {name.title()}")

            trf_out_match = re.search(
                r'^TRANSFER TO\s+(.+?)(?:\s+(?:OPAY|FIRST BANK|GTB|GUARANTY|UBA|UNITED BANK|ZENITH|WEMA|PROVIDUS|ACCESS|FIDELITY|POLARIS|STERLING|KEYSTONE|HERITAGE|TITAN|UNION|STANDARD|CASHCONNECT|MICROFINANCE|MFB|MONIEPOINT).*)?$',
                raw_clean, re.IGNORECASE
            )
            if trf_out_match:
                name = re.sub(r'\*+\d+.*$', '', trf_out_match.group(1)).strip()
                return clean_text(f"Transfer to {name.title()}")

            trf_in_match = re.search(r'^TRANSFER FROM\s+(.+)$', raw_clean, re.IGNORECASE)
            if trf_in_match:
                full_name = trf_in_match.group(1).strip()
                repeat_match = re.search(r'-\s*FROM\s+(.+)$', full_name, re.IGNORECASE)
                if repeat_match:
                    full_name = repeat_match.group(1).strip()
                return clean_text(f"Transfer from {full_name.title()}")

            mfds_match = re.search(r'/#/([^#/]+?):\d+/#/', raw_clean)
            if mfds_match:
                return clean_text(f"Transfer from {mfds_match.group(1).strip().title()}")
            if re.match(r'^MFDS', raw_clean):
                desc_match = re.search(r'/#/[^#]+/#/([^#/]+?)/#/', raw_clean)
                if desc_match:
                    desc = desc_match.group(1).strip()
                    if desc and desc.upper() not in ('', 'MONIEPOINT MICR'):
                        return clean_text(f"Transfer from Moniepoint User {desc.title()}")
                return "Transfer from Moniepoint User"

            dash_from_match = re.search(r'-\s*FROM\s+([A-Z][A-Z\s]+?)(?:\s*$)', raw_clean, re.IGNORECASE)
            if dash_from_match:
                return clean_text(f"Transfer from {dash_from_match.group(1).strip().title()}")

            old_nip_match = re.search(r'FROM\s+([A-Z][A-Z\s]+?)(?:\s+-\s+FROM\s+.+)?$', raw_clean)
            if old_nip_match:
                return clean_text(f"Transfer from {old_nip_match.group(1).strip().title()}")

            fbn_match = re.search(r'FROM\s+([A-Z][A-Z\s]+)$', raw_clean)
            if fbn_match:
                return clean_text(f"Transfer from {fbn_match.group(1).strip().title()}")

            cba_match = re.search(r'TO\s+(.+?)\s+MONIEPOINT\s+\*', raw_clean)
            if cba_match:
                return clean_text(f"Transfer to {cba_match.group(1).strip().title()}")

            if 'PERSONAL TRANSFER' in raw_clean:
                return "Personal Transfer Received"

            name_only = parse_name_plus_number(raw_clean)
            if name_only:
                return clean_text(f"{direction} {name_only.title()}")

            purpose = parse_word_to_name_ref(raw_clean)
            if purpose:
                return clean_text(f"Transfer for {purpose.title()}")

            narration_title = clean_text(raw_clean.split('/')[0].split('|')[0].strip().title())
            return clean_text(f"Transfer for {narration_title}")

        return clean_text(raw_clean.split('/')[0].split('|')[0].strip().title())

    # ==================== FILE LOADER ========================================

    def load_file(file_path):
        ext = Path(file_path).suffix.lower()
        account_name = "Moniepoint_Preprocessed"
        user_name_extracted = "Unknown User"

        invalid_account_names = {
            "ACCOUNT NAME",
            "ACCOUNT NAME:",
            "TRANSACTION TYPE",
            "TRANSACTION REF",
            "NARRATION",
            "DATE",
            "BALANCE AFTER (NGN)",
            "SETTLEMENT DEBIT (NGN)",
            "SETTLEMENT CREDIT (NGN)",
        }

        def extract_account_name(header_df):
            for _, row in header_df.iterrows():
                for i, val in enumerate(row):
                    if str(val).strip().upper() in {"ACCOUNT NAME", "ACCOUNT NAME:"}:
                        for offset in (1, 2):
                            if i + offset >= len(row):
                                continue
                            name = str(row.iloc[i + offset]).strip()
                            if name and name.upper() != "NAN" and name.upper() not in invalid_account_names:
                                return name
            return None

        if ext == '.csv':
            header_df = pd.read_csv(file_path, header=None, nrows=20)
            name = extract_account_name(header_df)
            if name:
                account_name = name.replace(" ", "_")
                user_name_extracted = name.strip()
            df = pd.read_csv(file_path, skiprows=7, header=0)
            df.columns = [c.strip() for c in df.columns]

        else:
            raw = pd.read_excel(file_path, header=None, engine='calamine')

            name = extract_account_name(raw.iloc[:20])
            if name:
                account_name = name.replace(" ", "_")
                user_name_extracted = name.strip()

            raw.columns = raw.iloc[7]
            df = raw.iloc[8:].reset_index(drop=True)
            df.columns = [
                str(c).strip() if str(c).strip() not in ('nan', 'None', '') else f'_col{i}'
                for i, c in enumerate(df.columns)
            ]

            unnamed_cols = [c for c in df.columns if c.startswith('_col')]
            best_col = None
            best_score = 0
            markers = ['TRANSFER', 'POS', 'DATA', 'AIRTIME', 'NIP', 'PURCHASE']
            for col in unnamed_cols:
                sample = df[col].astype(str).str.upper()
                score = sum(sample.str.contains(m, na=False).sum() for m in markers)
                if score > best_score:
                    best_score = score
                    best_col = col
            if best_col and best_score > 0:
                df['Narration'] = df[best_col].where(
                    df[best_col].str.strip() != '', df['Narration']
                )

        return account_name, user_name_extracted, df

    # ==================== MAIN ===============================================

    try:
        account_name, user_name_extracted, df = load_file(file_path)

        for col in ['Settlement Debit (NGN)', 'Settlement Credit (NGN)', 'Balance After (NGN)']:
            df[col] = (df[col].astype(str)
                              .str.replace(',', '', regex=False)
                              .str.replace('--', '0', regex=False)
                              .str.strip())
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')

        df['Category'] = df.apply(
            lambda r: get_category(
                r['Narration'], r['Transaction Ref'],
                r['Settlement Debit (NGN)'], r['Settlement Credit (NGN)']
            ), axis=1
        )
        df['Description'] = df.apply(
            lambda r: clean_description(
                r['Narration'], r['Transaction Ref'],
                r['Category'],
                r['Settlement Debit (NGN)'], r['Settlement Credit (NGN)']
            ), axis=1
        )

        final_df = df.rename(columns={
            'Settlement Debit (NGN)':  'Debit',
            'Settlement Credit (NGN)': 'Credit',
            'Balance After (NGN)':     'Balance'
        })[['Date', 'Category', 'Description', 'Debit', 'Credit', 'Balance']]

        final_df = final_df.dropna(subset=['Date'])

        final_df['User'] = user_name_extracted if user_name_extracted != "Unknown User" else user_name
        final_df['Bank'] = bank_name

        return final_df

    except Exception as e:
        raise ValueError(f"Could not process Moniepoint file: {e}")
