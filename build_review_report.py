import pandas as pd

matches = pd.read_csv("crm_matches.csv").fillna("")
audit = pd.read_csv("crm_financial_audit.csv").fillna("")

risk_ids = set(
    audit.loc[
        audit["requires_financial_review"].astype(str).str.lower() == "true",
        "account_id"
    ].astype(str)
)

matches["financial_risk"] = (
    matches["crm_account_id"].astype(str).isin(risk_ids)
)

matches["proposed_action"] = "HOLD - manual verification required"

confirmed = matches["recommendation"].eq("Likely match - verify")
safe = confirmed & ~matches["financial_risk"]

matches.loc[safe, "proposed_action"] = (
    "REVIEW - existing account, no automatic update"
)

matches.loc[
    matches["financial_risk"],
    "proposed_action"
] = "BLOCK - financial review required"

matches.loc[
    matches["recommendation"].eq("Potential missing account")
    & ~matches["financial_risk"],
    "proposed_action"
] = "INVESTIGATE - possible new account"

matches.to_csv("crm_review_report.csv", index=False)

print("\nCRM REVIEW REPORT")
print(matches["proposed_action"].value_counts().to_string())
print("\nSaved: crm_review_report.csv")
print("No CRM records were modified.")
