# Bellhaven CRM Intelligence

A Python and Streamlit workflow for discovering senior-living
facilities, comparing public facility data against CRM accounts,
and identifying records requiring human review.

## Features

- Scrapes Bellhaven's public community directory and detail pages
- Extracts facility names, addresses, care offerings, and source URLs
- Retrieves paginated CRM accounts through an authenticated API
- Uses fuzzy matching and address comparisons
- Flags possible missing accounts and ambiguous matches
- Identifies accounts with outstanding receivables
- Provides a Streamlit approval-review interface
- Generates CSV reports for auditing
- Supports repeatable, read-only reconciliation

## Running locally

Create and activate a Python virtual environment.

Install dependencies:

    pip install -r requirements.txt

Create `.streamlit/secrets.toml` with:

    CRM_BASE_URL = "https://analyst-assessment-production.up.railway.app/api/v1"
    CRM_TOKEN = "YOUR_PRIVATE_TOKEN"

Run the daily reconciliation:

    python daily_run.py

Start the dashboard:

    streamlit run app.py

## Safety

The reconciliation process does not automatically create,
merge, delete, or modify CRM accounts.

Financially sensitive accounts and potential ownership
changes require manual verification before any write operation.

Approval decisions are stored locally for review.
Applying approved changes through the CRM API is not yet implemented.

## Data completeness

The public community directory currently exposes 34 unique
facility URLs. Pages 4 through 8 repeat the final directory
results. The 34 discovered facilities have unique names and URLs.

If 35 facilities are expected, this discrepancy requires
confirmation from the source owner.

## Limitations

- Fuzzy matches require human validation.
- Financial and ownership safeguards prevent automatic changes.
- Daily reconciliation must currently be triggered manually or
  scheduled externally.
- CRM write operations are not implemented.
- No claim is made that proposed CRM changes have been applied.

## Outputs

- facilities.csv
- crm_matches.csv
- crm_financial_audit.csv
- crm_review_report.csv
- crm_verified_review.csv
- crm_final_review.csv

## Technologies

Python, Streamlit, pandas, requests, Beautiful Soup, RapidFuzz.
