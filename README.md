# 301 West 53rd Street Condominium Board Portal — Workspace Guide

Welcome to the 301 West 53rd Street Condominium Board Portal repository. This workspace compiles a secure, password-gated, interactive dashboard for board members to track finances, capital projects, operational items, and documentation.

## 🔗 Key Documentation
- **Operational & Building Context**: Read [BOARD_CONTEXT.md](file:///Users/ldoan6/Library/CloudStorage/GoogleDrive-lee.n.doan@gmail.com/My%20Drive/07.%20Shared%20AI/301w53/BOARD_CONTEXT.md) for details on major projects (roof/terrace, RODA outdoor furniture), active apartment leaks (Unit 25E), operational proposals (security system, sidewalk concrete repair), meeting minutes drafts, and financial audit findings.
- **Compiled Dashboard**: [index.html](file:///Users/ldoan6/Library/CloudStorage/GoogleDrive-lee.n.doan@gmail.com/My%20Drive/07.%20Shared%20AI/301w53/index.html) is the generated static web app.
- **Live Site**: Hosted at [https://leedoan.github.io/301w53/](https://leedoan.github.io/301w53/) (Password: `bearacles`).

---

## 📂 Directory Structure Map

This workspace contains both local raw documents and developer-maintained automation assets:

```
301w53/
├── .gitignore               # Strict whitelist ensuring only scripts, templates, and READMEs are tracked
├── README.md                # Developer & agent workspace guide (this file)
├── BOARD_CONTEXT.md         # Building domain knowledge, project briefs, and audit context
├── index.html               # Compiled, password-gated web dashboard (injected with data)
├── Data Sources/            # [LOCAL-ONLY] Raw condo data folders (gitignored)
│   ├── 01_Monthly_.../      # 20+ months of monthly bank & board financial statements
│   ├── 02_General_.../      # General ledgers & disbursements trackers
│   ├── 03_Board_Mi.../      # Meeting agendas & draft board minutes
│   ├── 04_Resident.../      # Monthly resident manager status reports
│   ├── 05_Capital_.../      # Active project bids, proposals, and design specs
│   ├── 06_Insuranc.../      # Insurance policies & compliance certificates
│   ├── 07_Other_Op.../      # Utility logs, oil tank tests, elevator service agreements
│   ├── apartment_leak_emails.json  # Raw Gmail exports relating to condo management
│   └── apartment_leak_emails_index.csv # Indexed summaries of the Gmail data
├── external reports/        # [LOCAL-ONLY] Processed ledger data sources (gitignored)
│   └── ledger_data.json     # Master transaction database containing 1,899 ledger entries
├── financials/              # [LOCAL-ONLY] Forensic audit logs & backups (gitignored)
├── approvals/               # [LOCAL-ONLY] Signed documents and specifications (gitignored)
├── updates and comms/       # [LOCAL-ONLY] Agendas, minutes, and newsletters (gitignored)
└── scripts/                 # Automation scripts & dashboard templates (tracked in git)
    ├── update_dashboard.py  # Crawls local documents, aggregates ledger & email JSONs, compiles index.html
    ├── index_template.html  # High-fidelity dashboard HTML/CSS/JS shell with dynamic Chart.js rendering
    └── publish_browser.py   # Playwright backup script for automated repository/Pages setup
```

---

## 🗃️ Data Formats & Schemas

### 1. General Ledger Transactions (`external reports/ledger_data.json`)
The transaction ledger contains 1,899 entries covering December 2023 through April 2026. The format is a JSON array of objects:
```json
{
  "date": "MM/DD/YY H:MM [AM/PM]", // Transaction timestamp
  "vendor": "String",              // Payee name (e.g., "NOVA CONSTRUCTION SERV")
  "category": "String",            // Accounting category (e.g., "Repairs & Maint")
  "amount": Float,                 // Negative for expenses, positive for revenues
  "desc": "String",                // Invoice/Remarks summary
  "check": "String"                // Check number if applicable
}
```

### 2. Document Index (`documentIndex` object in JavaScript)
When `scripts/update_dashboard.py` runs, it scans all raw files in `Data Sources/` recursively and generates an index list:
```json
{
  "name": "File_Name.pdf",
  "folder": "Display Category Folder",
  "size": "File Size (e.g., 250.45 KB)",
  "date": "YYYY-MM-DD",            // Last modified date
  "path": "Data Sources/Relative/Path/To/File.pdf"
}
```

### 3. Relevant Email Summaries (`relevantEmails` object in JavaScript)
Emails matching relevant condo board keywords are filtered and injected:
```json
{
  "date": "RFC 2822 Timestamp",
  "from": "Sender Name <email>",
  "subject": "Email Subject",
  "snippet": "Short preview snippet of the email body"
}
```

---

## 🔄 Compilation & Sync Pipeline

To update the live dashboard with new local files, transactions, or emails:

1. **Add Data**: Copy new invoices, statements, or updated JSON databases into their respective local directories (`Data Sources/`, `external reports/`).
2. **Recompile**: Run the update script to inject the new dataset into the HTML layout:
   ```bash
   python3 scripts/update_dashboard.py
   ```
3. **Commit & Push**: Commit the updated `index.html` and push it to GitHub:
   ```bash
   git add index.html scripts/index_template.html
   git commit -m "Update: Synchronized latest transactions and document index"
   git push origin main
   ```
4. **Deploy**: GitHub Actions will automatically rebuild and deploy the site to GitHub Pages.

---

## 🔒 Security Policy & .gitignore

Since the repository is public to support GitHub Pages, privacy is maintained client-side:
- **Strict .gitignore**: Excludes all directories hosting raw PDFs, spreadsheets, or source JSON databases.
- **Client-Side Password Gate**: Requires entering `"bearacles"` to unlock dashboard view access. Access authorization is stored in `sessionStorage` for the active browsing session.
