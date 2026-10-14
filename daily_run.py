import subprocess
import sys
from datetime import datetime, timezone

STEPS = [
    "scrape_facilities.py",
    "match_crm.py",
    "audit_crm.py",
    "build_review_report.py",
]

print("Bellhaven daily reconciliation")
print("Started:", datetime.now(timezone.utc).isoformat())

for script in STEPS:
    print(f"\nRunning {script}...", flush=True)
    subprocess.run([sys.executable, script], check=True)

print("\nReports refreshed successfully.")
print("CRM records were not modified.")
print("All proposed changes require separate review and approval.")
