"""CRM approval gate. Safe by default: no API writes."""
from pathlib import Path
import pandas as pd

review = pd.read_csv("crm_review_report.csv").fillna("")
path = Path("approval_decisions.csv")

if path.exists():
    decisions = pd.read_csv(path).fillna("")
else:
    decisions = pd.DataFrame(columns=["facility", "decision"])

approved = decisions[
    decisions["decision"] == "Approve for further processing"
]

merged = review.merge(
    approved[["facility", "decision"]],
    on="facility",
    how="inner"
)

blocked = merged[
    merged["proposed_action"].str.startswith(
        ("BLOCK", "HOLD", "INVESTIGATE"), na=False
    )
]

eligible = merged.drop(blocked.index)

print("CRM APPROVAL SAFETY GATE")
print("Approved for further processing:", len(merged))
print("Blocked for additional verification:", len(blocked))
print("Candidates for further review:", len(eligible))
print("CRM API writes executed: 0")
print("DRY RUN ONLY — no account creation or updates.")

if not eligible.empty:
    print("\nCandidates requiring verified change details:")
    print(eligible[[
        "facility", "crm_account_id", "proposed_action"
    ]].to_string(index=False))
