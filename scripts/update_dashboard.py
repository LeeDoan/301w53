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
    if not os.path.exists(LEDGER_PATH):
        print(f"Warning: Ledger data not found at {LEDGER_PATH}. Mocking empty ledger.")
        return []
    
    with open(LEDGER_PATH, 'r', encoding='utf-8') as f:
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
    seen_subjects = set()
    
    for email in emails:
        subject = str(email.get("subject", "")).lower()
        snippet = str(email.get("snippet", "")).lower()
        from_val = email.get("from", "")
        
        # Check if email is relevant based on keywords
        is_relevant = any(k in subject or k in snippet for k in keywords)
        if is_relevant:
            # Clean subject (remove Re:, Fwd:, etc. for duplicate checking if wanted)
            clean_subj = subject.replace("re:", "").replace("fwd:", "").strip()
            
            # For the dashboard, we want a curated list, let's keep it clean
            filtered_emails.append({
                "date": email.get("date", ""),
                "from": from_val,
                "subject": email.get("subject", ""),
                "snippet": email.get("snippet", "")
            })
            
    # Sort emails - note dates are like "Fri, 29 May 2026 17:50:22 +0000"
    # For a simple prototype, we'll keep the order from the json (newest is generally first or last)
    # Let's limit to top 60 relevant emails to keep file size optimized
    print(f"Extracted {len(filtered_emails)} relevant emails.")
    return filtered_emails[:60]

def main():
    if not os.path.exists(TEMPLATE_PATH):
        print(f"Error: Template HTML not found at {TEMPLATE_PATH}.")
        return
        
    doc_index = scan_data_sources()
    transactions = load_ledger_data()
    emails = load_email_data()
    
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
    """
    
    # Inject Data
    compiled_html = html_content.replace("/* {{DATA_INJECTION}} */", data_injection)
    
    # Save output index.html
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(compiled_html)
        
    print(f"Successfully compiled dashboard at {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
