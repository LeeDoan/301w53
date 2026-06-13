# 301 West 53rd Street Condominium - Board Dashboard

A secure, high-fidelity one-stop shop dashboard for the Residential Board of Managers at 301 West 53rd Street.

## Features

- **Executive Summary**: Core highlights, progress tracking, and resident notices.
- **Financial Hub**: Operating budget comparisons, repairs/maintenance breakdowns, forensic statement reconciliation variance reports, and interactive transaction ledger search.
- **Roof & Terrace Project**: Nova Construction waterproofing progress tracker, BR Design landscaping updates, and 25E leak mitigation log.
- **Board Admin & Meetings**: Nic Pisco operational reports, sidewalk option proposals, and monthly meeting agendas.
- **Authoritative Document Index**: Searchable index of all building documents.
- **Security Gate**: Basic password protection to secure view-only data.

## Sync Automation

To update this dashboard with your latest emails and local file changes:

1. Place your latest bank statement PDFs, agendas, and reports in the local Google Drive folder structure.
2. Run the update script:
   ```bash
   python scripts/update_dashboard.py
   ```
3. Run the deployment script to push updates live:
   ```bash
   ./scripts/deploy.sh
   ```

*Note: For privacy, raw PDFs and statement ledgers are kept local to your machine and are excluded via `.gitignore`.*
