import os
import json
import csv
import datetime

# Define directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_SOURCES_DIR = os.path.join(PROJECT_ROOT, "Data Sources")
LEDGER_PATH = os.path.join(PROJECT_ROOT, "external reports/ledger_data.json")
EMAILS_PATH = os.path.join(DATA_SOURCES_DIR, "apartment_leak_emails.json")
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "index_template.html")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "index.html")

def get_file_size_str(filepath):
    try:
        size_bytes = os.path.getsize(filepath)
        if size_bytes >= 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        elif size_bytes >= 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes} Bytes"
    except Exception:
        return "Unknown"

def scan_data_sources():
    print("Scanning Data Sources...")
    document_index = []
    
    # We walk the Data Sources directory
    for root, dirs, files in os.walk(DATA_SOURCES_DIR):
        for file in files:
            if file.startswith('.') or file.endswith('.json') or file.endswith('.csv'):
                continue  # skip hidden files and raw json/csv database files
            
            filepath = os.path.join(root, file)
            relative_path = os.path.relpath(filepath, PROJECT_ROOT)
            folder_rel = os.path.relpath(root, DATA_SOURCES_DIR)
            if folder_rel == ".":
                folder_rel = "Root"
            
            # Format folder name for display
            folder_display = folder_rel.replace("_", " ").title()
            
            size_str = get_file_size_str(filepath)
            
            # Extract basic date or mock it
            mtime = os.path.getmtime(filepath)
            date_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            
            document_index.append({
                "name": file,
                "folder": folder_display,
                "size": size_str,
                "date": date_str,
                "path": relative_path
            })
            
    # Sort files alphabetically by folder, then name
    document_index.sort(key=lambda x: (x["folder"], x["name"]))
    print(f"Indexed {len(document_index)} documents.")
    return document_index

def load_ledger_data():
    print("Loading Ledger Data...")
    
    # Try reconciled master ledger first, fallback to raw ledger
    reconciled_path = os.path.join(PROJECT_ROOT, "scratch/reconciled_master_ledger.json")
    if os.path.exists(reconciled_path):
        print(f"Found reconciled ledger at {reconciled_path}")
        path_to_use = reconciled_path
    elif os.path.exists(LEDGER_PATH):
        print(f"Found raw ledger at {LEDGER_PATH}")
        path_to_use = LEDGER_PATH
    else:
        print("Warning: Ledger data file not found. Mocking empty ledger.")
        return []
    
    with open(path_to_use, 'r', encoding='utf-8') as f:
        raw_txs = json.load(f)
        
    mapped_txs = []
    for tx in raw_txs:
        mapped_txs.append({
            "date": tx.get("tx_date", ""),
            "vendor": tx.get("vendor_name", "Unknown"),
            "category": tx.get("category", "Uncategorized"),
            "amount": float(tx.get("amount", 0.0)),
            "desc": tx.get("description", tx.get("remarks", "")),
            "check": tx.get("check_no", "")
        })
        
    print(f"Loaded {len(mapped_txs)} transactions.")
    return mapped_txs

def load_email_data():
    print("Loading Email Summaries...")
    if not os.path.exists(EMAILS_PATH):
        print(f"Warning: Emails file not found at {EMAILS_PATH}. Mocking empty email set.")
        return []
        
    with open(EMAILS_PATH, 'r', encoding='utf-8') as f:
        emails = json.load(f)
        
    keywords = [
        "reserve", "transfer", "assessment", "bylaw", "rule", "bylaws", 
        "nova", "credit", "heater", "roof", "leak", "board", "meeting", 
        "minutes", "agenda", "gumley", "pisco", "perez", "marchetti"
    ]
    
    filtered_emails = []
    
    for email in emails:
        subject = str(email.get("subject", "")).lower()
        snippet = str(email.get("snippet", "")).lower()
        from_val = email.get("from", "")
        
        # Check if email is relevant based on keywords
        is_relevant = any(k in subject or k in snippet for k in keywords)
        if is_relevant:
            filtered_emails.append({
                "date": email.get("date", ""),
                "from": from_val,
                "subject": email.get("subject", ""),
                "snippet": email.get("snippet", "")
            })
            
    print(f"Extracted {len(filtered_emails)} relevant emails.")
    return filtered_emails[:60]

def get_roof_transactions(transactions):
    print("Filtering Roof & Terrace Transactions...")
    roof_checks = set()
    roof_keywords = ["ROOF", "FACADE", "FISP", "LEAK", "WATER INFILTRATION", "CON-RO", "PROBES", "TERRACE", "DECK", "LANDSC"]
    direct_vendors = ["NOVA", "GARDINER", "THEOBALD", "G&T", "BR DESIGN", "BRD", "TERRAIN"]
    
    for tx in transactions:
        v = tx.get("vendor", "").upper()
        desc = tx.get("desc", "").upper()
        check = tx.get("check", "")
        cat = tx.get("category", "")
        
        is_direct = any(dv in v for dv in direct_vendors)
        has_kw = any(kw in desc for kw in roof_keywords)
        is_roof_cat = (cat == "Roof Repair Project")
        
        if (is_direct or ("RAND" in v and has_kw) or is_roof_cat) and check:
            roof_checks.add(check)
            
    roof_txs = []
    for tx in transactions:
        v = tx.get("vendor", "").upper()
        desc = tx.get("desc", "").upper()
        check = tx.get("check", "")
        cat = tx.get("category", "")
        
        is_selected = False
        if check in roof_checks:
            if any(x in v for x in ["NOVA", "GARDINER", "THEOBALD", "G&T", "BR DESIGN", "BRD", "TERRAIN", "RAND"]):
                is_selected = True
            elif cat == "Roof Repair Project":
                is_selected = True
        elif any(dv in v for dv in direct_vendors):
            is_selected = True
        elif "RAND" in v and any(kw in desc for kw in roof_keywords):
            is_selected = True
        elif cat == "Roof Repair Project":
            is_selected = True
            
        if is_selected:
            # Filter out non-roof items
            if any(x in desc for x in ["LOCAL LAW 88", "HEATING PLANT UPGRADE", "WATER PUMP SYSTEM", "COOLING TOWER", "PLUMBING SYSTEM EVAL", "CHIMNEY"]):
                continue
            roof_txs.append(tx)
            
    def parse_date(tx_obj):
        try:
            parts = tx_obj["date"].split('/')
            m = int(parts[0])
            d = int(parts[1])
            y = int(parts[2].split(' ')[0])
            if y < 100:
                y += 2000
            return (y, m, d)
        except Exception:
            return (0, 0, 0)
            
    roof_txs.sort(key=parse_date)
    print(f"Filtered {len(roof_txs)} roof transactions.")
    return roof_txs

def build_forecast_data():
    return [
        {
            "vendor": "NOVA Construction Services",
            "category": "Contract Commitment",
            "amount": 430000.00,
            "desc": "Remaining committed balance on active roof waterproofing and rehabilitation contract.",
            "status": "Committed Balance"
        },
        {
            "vendor": "NOVA Construction Services",
            "category": "Change Orders",
            "amount": 40000.00,
            "desc": "Remaining committed balance on approved change orders for envelope/structural repairs.",
            "status": "Committed Balance"
        },
        {
            "vendor": "RAND Engineering, P.C.",
            "category": "Engineering Oversight",
            "amount": 25000.00,
            "desc": "Remaining committed balance for construction administration, monitoring, and final FISP sign-off.",
            "status": "Committed Balance"
        },
        {
            "vendor": "Terrain Landscape Arch",
            "category": "Landscape Design SOW",
            "amount": 20000.00,
            "desc": "Remaining contract balance for site landscape planning, bidding prep, and architectural layout.",
            "status": "Committed Balance"
        },
        {
            "vendor": "RODA America Ltd",
            "category": "Terrace Furniture",
            "amount": 100875.00,
            "desc": "Contract value for outdoor terrace furniture package (50% list price discount). Terms: 50% deposit ($50,437.50) approved to order, 50% balance due at delivery.",
            "status": "Approved / Ordered"
        },
        {
            "vendor": "Terrain Landscape Arch",
            "category": "Terrace Construction",
            "amount": 1800000.00,
            "desc": "High-level construction estimate for landscaping, decking, soil, and installation (excludes furniture). Sub-contractor bids due mid-June 2026.",
            "status": "Estimate / Bidding"
        },
        {
            "vendor": "BR Design Associates",
            "category": "Terrace Design SOW",
            "amount": 41500.00,
            "desc": "Architectural and design fee for pre-construction, value engineering, and trade oversight (approved; revised down from $60,000, saving $18,500).",
            "status": "Approved SOW"
        },
        {
            "vendor": "BR Design Associates",
            "category": "Sidewalk Repair SOW",
            "amount": 31680.00,
            "desc": "Option 3: Full concrete sidewalk replacement (approx 1,200 sq ft) with 5-year warranty. Recommended by BR Design to resolve tripping hazards.",
            "status": "Proposed SOW"
        }
    ]

def main():
    if not os.path.exists(TEMPLATE_PATH):
        print(f"Error: Template HTML not found at {TEMPLATE_PATH}.")
        return
        
    # Check if raw files exist. If not, try to parse from the existing index.html to recover data model
    reconciled_path = os.path.join(PROJECT_ROOT, "scratch/reconciled_master_ledger.json")
    raw_files_exist = os.path.exists(reconciled_path) or os.path.exists(LEDGER_PATH)
    
    doc_index = None
    transactions = None
    emails = None
    roof_txs = None
    roof_forecast = None
    last_updated_str = None
    
    if not raw_files_exist and os.path.exists(OUTPUT_PATH):
        print("Raw data files not found. Attempting to parse existing index.html to recover data model...")
        try:
            with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
                existing_html = f.read()
            
            import re
            m_doc = re.search(r'const documentIndex\s*=\s*(\[.*?\]);', existing_html, re.DOTALL)
            m_raw = re.search(r'const rawTransactions\s*=\s*(\[.*?\]);', existing_html, re.DOTALL)
            m_email = re.search(r'const relevantEmails\s*=\s*(\[.*?\]);', existing_html, re.DOTALL)
            m_roof = re.search(r'const roofTransactions\s*=\s*(\[.*?\]);', existing_html, re.DOTALL)
            m_forecast = re.search(r'const roofForecast\s*=\s*(\[.*?\]);', existing_html, re.DOTALL)
            m_time = re.search(r'const lastUpdatedTime\s*=\s*"(.*?)";', existing_html)
            
            if m_doc and m_raw and m_email and m_roof and m_forecast and m_time:
                doc_index = json.loads(m_doc.group(1))
                transactions = json.loads(m_raw.group(1))
                emails = json.loads(m_email.group(1))
                roof_txs = json.loads(m_roof.group(1))
                roof_forecast = json.loads(m_forecast.group(1))
                last_updated_str = m_time.group(1)
                print("Successfully recovered data model from index.html.")
        except Exception as e:
            print(f"Failed to recover data from index.html: {e}")
            
    # Fallback to normal loading if we couldn't parse it or if raw files exist
    if doc_index is None:
        doc_index = scan_data_sources()
        transactions = load_ledger_data()
        emails = load_email_data()
        roof_txs = get_roof_transactions(transactions)
        roof_forecast = build_forecast_data()
        last_updated_str = datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p')
    
    # Read Template
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    # Build JavaScript injection block
    data_injection = f"""
        const documentIndex = {json.dumps(doc_index, indent=4)};
        const rawTransactions = {json.dumps(transactions, indent=4)};
        const relevantEmails = {json.dumps(emails, indent=4)};
        const lastUpdatedTime = "{last_updated_str}";
        const roofTransactions = {json.dumps(roof_txs, indent=4)};
        const roofForecast = {json.dumps(roof_forecast, indent=4)};
    """
    
    # Inject Data
    compiled_html = html_content.replace("/* {{DATA_INJECTION}} */", data_injection)
    
    # Save output index.html
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(compiled_html)
        
    print(f"Successfully compiled dashboard at {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
