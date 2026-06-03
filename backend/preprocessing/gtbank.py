import pdfplumber
import pandas as pd
import re
from pathlib import Path

def gtbank_preprocessing(file_path: str, user_name: str, bank_name: str) -> pd.DataFrame:
    """
    Preprocess GTBank statement into standardized 8-column format.
    
    Args:
        file_path: Path to GTBank statement file
        user_name: Name of the user for file naming
        bank_name: Name of the bank (GTBank)
    
    Returns:
        DataFrame with standardized columns: Date, Description, Debit, Credit, Balance, Category, User, Bank
    """

    # ==================== KEYWORD LISTS ====================

    CHURCH_KEYWORDS = [
        'CHURCH', 'MINISTRY', 'MINISTRIES', 'CHAPEL', 'PARISH', 'CATHEDRAL',
        'MOSQUE', 'ASSEMBLY', 'FELLOWSHIP', 'MISSION', 'GOSPEL', 'APOSTOLIC',
        'EVANGELICAL', 'PENTECOSTAL', 'BAPTIST', 'CATHOLIC', 'ANGLICAN', 'RCCG',
        'WINNERS', 'DEEPER LIFE', 'SALVATION', 'MOUNTAIN OF FIRE', 'CHRIST EMBASSY',
        'DAYSTAR', 'LIVING FAITH', 'SANCTUARY', 'WORSHIP CENTRE', 'TITHE',
        'OFFERING', 'HEADQUARTERS',
    ]

    BETTING_KEYWORDS = [
        'SPORTYBET', 'SPORTY', 'BET9JA', '1XBET', 'BETKING', 'BETWAY',
        'BETBONANZA', 'NAIRABET', 'MSPORT', 'BETANO', 'BETWINNER', 'PARIPESA',
        'MELBET', 'MEGAPARI', '22BET', 'BETPAWA', 'LIVESCOREBET', 'MOZZARTBET',
        'WAZOBET', 'ACCESSBET', 'BETFAIR', 'BETLAND', 'GREENLOTTO', 'AFRIBET',
        'ZEBET', 'FOOTBALLING', 'FOOTBALL BET', 'BETTING',
    ]

    # Bank routing codes that appear in GTBank transfer remarks
    BANK_CODES = (
        r'FCMB|GTB|UBA|ZENITH|ACCESS|FIRST\s+BANK|FBN|WEMA|KEYSTONE|'
        r'POLARIS|STANBIC|UNION|HERITAGE|TITAN|OPAY|MONIEPOINT|MONIEMFB|PALMPAY|'
        r'RAVEN|BEMFB|FDP|ROLEZ|CBN|ECOBANK|FIDELITY|STERLING|JAIZ|MFB'
    )

    # Nigerian location tokens GTBank embeds in POS remarks
    LOCATION_TOKENS = (
        r'Lagos|Kaduna|Abuja|Kano|Ibadan|Bwari|Owerri|Enugu|Benin|Jos|Ilorin|Port Harcourt'
    )

    # ==================== HELPERS ====================

    def clean_text(text):
        text = re.sub(r'[-\u2013\u2014/\\|().,;:\'"!?&@#%^*+=<>]+', ' ', str(text))
        text = re.sub(r'\s{2,}', ' ', text)
        return text.strip()

    def clean_name(name):
        return re.sub(r'\s+', ' ', str(name)).strip().title()

    def is_credit(credit):
        try:
            return float(credit or 0) > 0
        except (ValueError, TypeError):
            return False

    # ==================== CATEGORY ====================

    def get_category(remarks, ref, debit, credit):
        u = str(remarks).upper().strip()
        ref_u = str(ref).upper().strip().lstrip("'")

        if not u or u in ('NAN', 'NONE', ''):
            return 'Others'

        # ── Step 1: Reference suffix decides category ────────────────────
        if ref_u.endswith('FOS') or ref_u.endswith('DCI'):
            return 'POS Transaction'
        if ref_u.endswith('FEB'):
            return 'Online Payment'
        if ref_u.endswith('USS'):
            return 'Airtime'
        if ref_u.endswith('API'):
            # NEFT credits sometimes arrive with API ref — check remarks first
            if 'NEFT TRANSFER' not in u:
                return 'Reversal'
        if ref_u.endswith('NIP'):
            return 'P2P Transfer'

        if ref_u.endswith('GTW'):
            if 'REVERSED' in u or 'DISPENSE ERROR' in u:
                return 'Reversal'
            if 'COMMISSION ON NIP' in u:
                return 'Charges'
            if 'VATCHARGES' in u or ('VAT' in u and 'CHARGES' in u):
                return 'Charges'
            if any(k in u for k in CHURCH_KEYWORDS):
                return 'Church'
            if any(k in u for k in BETTING_KEYWORDS):
                return 'Betting'
            return 'P2P Transfer'

        # ── Step 2: Remarks-based for BR, blank ref, etc. ───────────────
        if 'DISPENSE ERROR' in u:
            return 'Dispense Error Reversal'
        if 'REVERSED' in u:
            return 'Reversal'
        if 'SMS ALERT CHARGE' in u or 'SMS CHARGES' in u or 'SMS CHARGE' in u:
            return 'SMS Charges'
        if 'STAMP DUTI' in u or 'STAMP DUTY' in u:
            return 'Charges'
        if 'COMMISSION ON NIP' in u:
            return 'Charges'
        if 'VATCHARGES' in u or ('VAT' in u and 'CHARGES' in u):
            return 'Charges'
        if any(k in u for k in CHURCH_KEYWORDS):
            return 'Church'
        if any(k in u for k in BETTING_KEYWORDS):
            return 'Betting'
        if 'TRANSFER BETWEEN CUSTOMERS' in u:
            return 'P2P Transfer'
        if 'NIBSS INSTANT PAYMENT OUTWARD' in u:
            return 'P2P Transfer'
        if 'NIP TRANSFER' in u:
            return 'P2P Transfer'
        if 'NEFT TRANSFER' in u:
            return 'NEFT Payment'

        # ── Anything else goes to Others ─────────────────────────────────
        return 'Others'

    # ==================== NAME EXTRACTION HELPERS ====================

    def extract_nip_transfer_name(remarks):
        u = remarks.upper()
        m = re.search(r'NIP\s+TRANSFER\s+TO\s+\S+\s*[-\u2013]\s*(.+)$', u)
        if m:
            after_bank = m.group(1).strip()
            parts = [p.strip() for p in re.split(r'\s*[-\u2013]\s*', after_bank) if p.strip()]
            if parts:
                real_parts = [p for p in parts if not re.match(
                    r'^(?:POS\s+TRANSFER|POS\s+AGENT|WEB\s+TRANSFER|NIP\s+TRANSFER)\s*$',
                    p, re.IGNORECASE
                )]
                if real_parts:
                    # Join all parts (handles names like 'P - S DYNAMIC CONCEPT LIMITED')
                    return clean_name(' '.join(real_parts))
        m = re.search(r'NIP\s+TRANSFER\s+TO\s+(.+)$', u)
        if m:
            name = re.sub(r'\d+.*$', '', m.group(1)).strip()
            return clean_name(name)
        return ''

    def extract_transfer_between_customers_names(remarks):
        """
        Returns (recipient, sender).

        Format 1 — TO [GTBANK PLC] <RECIPIENT>-<BANKCODE>-<SENDER>
        Format 2 — FROM <SENDER> TO <RECIPIENT>  (VIA GTWORLD)
        Format 3 — TRANSFER FROM <SENDER>-<BANKCODE>-...
        Format 4 — SENT FROM <APP>-<BANKCODE>-<SENDER>
        Format 5 — FIP:USSD:/<SENDER> or FIP:MB:/<SENDER>
        Format 6 — ends with -<BANKCODE>-<SENDER NAME>
        """
        u = remarks.upper()

        # Format 5: FIP:USSD or FIP:MB
        m = re.search(
            r'FIP\s*:\s*(?:USSD|MB)\s*:/\s*([A-Z][A-Z\s]{2,40}?)(?:\s*/|\s+USSD_|\s+EM/|$)', u
        )
        if m:
            raw = re.sub(r'\s+[A-Z]{1,2}$', '', m.group(1).strip()).strip()
            return '', clean_name(raw)

        # Format 3
        m = re.search(r'TRANSFER\s+FROM\s+([A-Z][A-Z\s]+?)[-\u2013](' + BANK_CODES + r')', u)
        if m:
            return '', clean_name(m.group(1))

        # Format 4
        m = re.search(r'SENT\s+FROM\s+(.+?)$', u)
        if m:
            parts = re.split(r'[-\u2013]', m.group(1).strip())
            for part in reversed(parts):
                part = part.strip().rstrip('.')
                if part and re.match(r'^[A-Z\s]+$', part) and not re.fullmatch(BANK_CODES, part):
                    return '', clean_name(part)

        # Format 1
        m = re.search(
            r'TO\s+(?:GTBANK\s+PLC\s+)?([A-Z][A-Z\s]+?)'
            r'[-\u2013](' + BANK_CODES + r')\s*[-\u2013]?\s*([A-Z][A-Z\s]+?)(?:\s*\.|$)',
            u
        )
        if m:
            return clean_name(m.group(1)), clean_name(m.group(3))

        # Format 2
        m = re.search(r'\bFROM\s+([A-Z][A-Z\s,]+?)\s+TO\s+([A-Z][A-Z\s]+?)$', u)
        if m:
            sender    = clean_name(re.sub(r',', ' ', m.group(1)))
            recipient = clean_name(m.group(2))
            return recipient, sender

        # Format 6: ends with -<BANKCODE>-<SENDER NAME>
        # e.g. '...MONIEMFB-OLANREWAJU OLUWAFEMI'
        m = re.search(
            r'[-\u2013](?:' + BANK_CODES + r')[-\u2013]([A-Z][A-Z\s]+?)(?:\s*\.|$)', u
        )
        if m:
            return '', clean_name(m.group(1))

        return '', ''

    def extract_pos_merchant(remarks):
        # Step 1: strip boilerplate
        cleaned = re.sub(
            r'(?:POSWEB PURCHASE TRANSACTION POS (?:PUR|WD)|'
            r'POS\s+WEB TRANSFER TRANSACTION POS (?:PUR|WD))\s*',
            '', remarks, flags=re.IGNORECASE
        ).strip()

        # Step 2: strip leading lone 'T '
        cleaned = re.sub(r'^T\s+', '', cleaned, flags=re.IGNORECASE).strip()

        # Step 3: strip leading Nigerian bank / fintech agent prefix
        # Guard: only strip if the next word is NOT a business suffix
        # e.g. 'PALMPAY LIMITED' stays intact, 'PALMPAY JOHN DOE' -> 'JOHN DOE'
        _APFX = (
            r'OPAY|PALMPAY|PALM\s*PAY|MONIEPOINT|MONIE\s*POINT|MONIEMFB|'
            r'KUDA|CARBON|FAIRMONEY|RENMONEY|PAGA|CHIPPER|'
            r'FLUTTERWAVE|PAYSTACK|PIGGYVEST|COWRYWISE|ALAT|'
            r'GTBANK|GTB|GTWORLD|ZENITH|ACCESS|UBA|FCMB|FIDELITY|'
            r'FIRSTBANK|FIRST\s*BANK|FBN|WEMA|KEYSTONE|POLARIS|'
            r'STANBIC|STERLING|UNION|HERITAGE|JAIZ|ECOBANK|ROLEZ'
        )
        _BSFX = r'LIMITED|LTD|PLC|ENTERPRISES?|VENTURES?|SERVICES?|COMPANY|GROUP|NIGERIA|GLOBAL'
        _pm = re.match(r'^(?:' + _APFX + r')\s+(\S+)', cleaned, flags=re.IGNORECASE)
        if _pm and not re.match(r'^(?:' + _BSFX + r')$', _pm.group(1), re.IGNORECASE):
            cleaned = re.sub(r'^(?:' + _APFX + r')\s+', '', cleaned, flags=re.IGNORECASE).strip()

        # Step 4: cut at location token, smart fused-cut detection
        def cut_location(text):
            m = re.search(r'(?i)(' + LOCATION_TOKENS + r'|KDNG|LANG\b)', text)
            if m:
                before = text[:m.start()]
                if m.start() > 0 and text[m.start() - 1] != ' ':
                    before = re.sub(r'\s+[A-Z]{1,3}\s*$', '', before, flags=re.IGNORECASE)
                return before.strip()
            return text
        cleaned = cut_location(cleaned)

        # Step 5: stop at POS AGENT, NG, LA, or long number
        cleaned = re.sub(r'\s+POS\s+AGENT.*$', '', cleaned, flags=re.IGNORECASE).strip()

        m = re.match(
            r'^([A-Za-z][A-Za-z\s\-&]+?)(?:\s+(?:NG\b|LA\b)|\s+\d{4,})',
            cleaned, re.IGNORECASE
        )
        if m:
            return clean_name(m.group(1))

        words = cleaned.split()
        name_words = []
        for w in words:
            if re.match(r'^\d+', w):
                break
            if w.upper() in ('NG', 'LA'):
                break
            name_words.append(w)
            if len(name_words) >= 6:
                break
        if name_words:
            return clean_name(' '.join(name_words))

        return 'POS Merchant'

    def extract_feb_merchant(remarks):
        m = re.search(
            r'WEB\s+PUR\s+(?:\d+\s+)?([A-Za-z][A-Za-z0-9\s]+?)'
            r'(?:(?:' + LOCATION_TOKENS + r')\b|LANG\b|\s+NG\b|\s+\d{4,})',
            remarks, re.IGNORECASE
        )
        if m:
            name = m.group(1).strip()
            name = re.sub(r'\s+[A-Za-z]+\d+.*$', '', name).strip()
            name = re.sub(r'\s+', ' ', name).strip()
            if name:
                return name.title()
        return 'Online Payment'

    def extract_reversed_phone(remarks):
        m = re.search(r'[-\u2013]((?:234|0)\d{9,12})[-\u2013]', remarks)
        if m:
            return m.group(1)
        m = re.search(r'\b((?:234|0)\d{9,12})\b', remarks)
        if m:
            return m.group(1)
        return ''

    def extract_dispense_error_ref(remarks):
        cleaned = re.sub(
            r'^DISPENSE\s+ERROR\s+(?:REVERSAL\s*)?', '', remarks, flags=re.IGNORECASE
        ).strip()
        cleaned = clean_text(cleaned)
        return f"Dispense Error Reversal {cleaned}" if cleaned else 'Dispense Error Reversal'

    def extract_neft_description(remarks):
        """
        Strip compact ref code (e.g. TRCLGZIB/NFT/11/335272865) then clean what remains.
        'NEFT TRANSFER TRCLGZIB/NFT/11/335272865/CORONATION REGISTRARS/MTNN - PAYMENT 34 OF 30/09/2025'
        -> 'NEFT Payment Coronation Registrars Mtnn Payment 34 Of 30 09 2025'
        """
        s = re.sub(r'^NEFT\s+TRANSFER\s+', '', remarks, flags=re.IGNORECASE).strip()
        s = re.sub(r'^[A-Z0-9]+(?:/[A-Z0-9]+)*/\d+\s*', '', s, flags=re.IGNORECASE).strip()
        cleaned = clean_text(s)
        return f"NEFT Payment {cleaned.title()}" if cleaned else 'NEFT Payment'

    # ==================== DESCRIPTION ====================

    def clean_description(remarks, ref, category, debit, credit):
        raw = str(remarks).strip()
        u   = raw.upper()

        if not raw or u in ('NAN', 'NONE', ''):
            return 'Others'

        credit_flag = is_credit(credit)
        direction   = 'Transfer from' if credit_flag else 'Transfer to'

        # --- NEFT Payment ---
        if category == 'NEFT Payment':
            return extract_neft_description(raw)

        # --- Dispense Error Reversal ---
        if category == 'Dispense Error Reversal':
            return extract_dispense_error_ref(raw)

        # --- Reversal ---
        if category == 'Reversal':
            if 'REVERSED' in u and ('GTWORLD' in u or 'VIA' in u):
                phone = extract_reversed_phone(raw)
                if phone:
                    return clean_text(f"Reversal made for transaction to {phone}")
            return clean_text(raw)

        # --- Airtime ---
        if category == 'Airtime':
            m = re.search(r'[-\u2013]((?:234|0)\d{9,12})[-\u2013]', raw)
            if not m:
                m = re.search(r'((?:234|0)\d{9,12})', raw)
            phone = m.group(1) if m else ''
            return clean_text(f"Airtime Purchase for {phone}") if phone else 'Airtime Purchase'

        # --- SMS Charges ---
        if category == 'SMS Charges':
            m = re.search(
                r'SMS ALERT CHARGE FOR\s+(.+?)(?:SMS CHARGES|Recover|$)', raw, re.IGNORECASE
            )
            if m:
                return clean_text(f"SMS Alert Charge For {m.group(1).strip()}")
            return 'SMS Alert Charge'

        # --- Charges ---
        if category == 'Charges':
            if 'COMMISSION ON NIP' in u:
                return 'Commission on NIP Transfer'
            if 'VATCHARGES' in u or ('VAT' in u and 'CHARGES' in u and 'SMS' not in u):
                return 'VAT Charges'
            if 'STAMP DUTI' in u or 'STAMP DUTY' in u:
                m = re.search(
                    r'(?:Stamp Duties?\s+(?:STAMP DUTIES?\s+)?[-\u2013]?\s*)(.+)',
                    raw, re.IGNORECASE
                )
                if m:
                    return clean_text(f"Stamp Duties {m.group(1).strip()}")
                return 'Stamp Duties'
            return 'Bank Charges'

        # --- Church ---
        if category == 'Church':
            name = extract_nip_transfer_name(raw)
            if not name:
                recipient, sender = extract_transfer_between_customers_names(raw)
                name = recipient or sender
            return clean_text(f"{direction} {name}") if name else f"{direction} Church"

        # --- Betting ---
        if category == 'Betting':
            platform = next((k for k in BETTING_KEYWORDS if k in u), 'Betting Platform')
            if credit_flag:
                return clean_text(f"Betting Winnings Received from {platform.title()}")
            return clean_text(f"Betting Payment to {platform.title()}")

        # --- Online Payment ---
        if category == 'Online Payment':
            merchant = extract_feb_merchant(raw)
            if credit_flag:
                return clean_text(f"Online Payment from {merchant}")
            return clean_text(f"Online Payment to {merchant}")

        # --- POS Transaction ---
        if category == 'POS Transaction':
            merchant = extract_pos_merchant(raw)
            return clean_text(f"{direction} {merchant}")

        # --- P2P Transfer ---
        if category == 'P2P Transfer':
            if 'TRANSFER BETWEEN CUSTOMERS' in u:
                recipient, sender = extract_transfer_between_customers_names(raw)
                # Credit = money in  → show who sent it
                # Debit  = money out → show who received it
                if credit_flag and sender:
                    return clean_text(f"Transfer from {sender}")
                elif not credit_flag and recipient:
                    return clean_text(f"Transfer to {recipient}")
                elif sender:
                    return clean_text(f"Transfer from {sender}")
                elif recipient:
                    return clean_text(f"Transfer to {recipient}")

            if 'NIBSS INSTANT PAYMENT OUTWARD' in u or 'NIP TRANSFER' in u:
                name = extract_nip_transfer_name(raw)
                if name:
                    return clean_text(f"{direction} {name}")

            return clean_text(f"P2P Transfer {'Received' if credit_flag else 'Sent'}")

        # --- Others ---
        return 'Others'

    # ==================== ACCOUNT NAME FROM PDF ====================

    def extract_account_name_from_pdf(pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            text = pdf.pages[0].extract_text() or ''
        patterns = [
            r'CUSTOMER STATEMENT\s*\n+\s*([A-Z][A-Z\s,]+?)(?:\n)',
            r'Account Name[:\s]+([A-Z][A-Z\s]+?)(?:\n)',
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                name = m.group(1).strip()
                return re.sub(r'[\s,]+', '_', name).upper()
        return 'GTBANK_ACCOUNT_HOLDER'

    # ==================== EXTRACT BANK NAME FROM PDF ====================

    def extract_bank_name_from_pdf(pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            text = pdf.pages[0].extract_text() or ''
        patterns = [
            r'(Guaranty Trust Bank|GTBank|GT Bank)',
            r'(GUARANTY TRUST BANK|GTBANK|GT BANK)',
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                return m.group(1).strip().title()
        return 'GTBank'

    # ==================== EXTRACT TRANSACTIONS FROM PDF ====================

    def extract_transactions_from_pdf(pdf_path):
        rows = []
        header_found = False
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if not row:
                            continue
                        cleaned = [str(c).replace('\n', ' ').strip() if c else '' for c in row]
                        full = ' '.join(cleaned).upper()

                        if ('TRANS' in full or 'DATE' in full) and 'DEBIT' in full and 'CREDIT' in full:
                            header_found = True
                            continue
                        if not header_found:
                            continue
                        if not cleaned or not cleaned[0]:
                            continue

                        date_str = cleaned[0].strip()
                        if not re.match(r'\d{2}-[A-Za-z]{3}-\d{4}', date_str):
                            continue
                        if len(cleaned) < 5:
                            continue

                        ref         = cleaned[2] if len(cleaned) > 2 else ''
                        debit_raw   = cleaned[3] if len(cleaned) > 3 else '0'
                        credit_raw  = cleaned[4] if len(cleaned) > 4 else '0'
                        balance_raw = cleaned[5] if len(cleaned) > 5 else ''
                        remarks     = cleaned[7] if len(cleaned) > 7 else (cleaned[-1] if cleaned else '')

                        rows.append({
                            'raw_date':    date_str,
                            'reference':   ref,
                            'debit_raw':   debit_raw,
                            'credit_raw':  credit_raw,
                            'balance_raw': balance_raw,
                            'remarks':     remarks,
                        })
        return rows

    # ==================== MAIN PROCESSING ====================

    try:
        account_name = extract_account_name_from_pdf(file_path)
        bank_name    = extract_bank_name_from_pdf(file_path)
        rows         = extract_transactions_from_pdf(file_path)

        if not rows:
            raise ValueError('No transaction data found in PDF.')

        df = pd.DataFrame(rows)

        df['Date'] = pd.to_datetime(
            df['raw_date'], format='%d-%b-%Y', errors='coerce'
        ).dt.strftime('%Y-%m-%d')

        df['Debit'] = pd.to_numeric(
            df['debit_raw'].astype(str).str.replace(',', '', regex=False), errors='coerce'
        ).fillna(0)

        df['Credit'] = pd.to_numeric(
            df['credit_raw'].astype(str).str.replace(',', '', regex=False), errors='coerce'
        ).fillna(0)

        df['Balance'] = pd.to_numeric(
            df['balance_raw'].astype(str).str.replace(',', '', regex=False), errors='coerce'
        )

        df['Category'] = df.apply(
            lambda r: get_category(r['remarks'], r['reference'], r['Debit'], r['Credit']), axis=1
        )
        df['Description'] = df.apply(
            lambda r: clean_description(
                r['remarks'], r['reference'], r['Category'], r['Debit'], r['Credit']
            ), axis=1
        )

        final_df = df[
            ['Date', 'Category', 'Description', 'Debit', 'Credit', 'Balance']
        ].dropna(subset=['Date']).copy()

        # ==================== ADD USER & BANK COLUMNS ====================
        final_df['User'] = account_name.replace('_', ' ').title()
        final_df['Bank'] = bank_name

        return final_df

    except Exception as e:
        raise ValueError(f"Could not process GTBank file: {e}")
