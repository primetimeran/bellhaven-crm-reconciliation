import requests
import pandas as pd
import streamlit as st

base = st.secrets["CRM_BASE_URL"].rstrip("/")
headers = {"Authorization": f'Bearer {st.secrets["CRM_TOKEN"]}'}

accounts = []
page = 1

while True:
    r = requests.get(
        f"{base}/accounts",
        headers=headers,
        params={"page": page, "page_size": 100},
        timeout=30
    )
    r.raise_for_status()
    result = r.json()
    batch = result.get("data", [])
    accounts.extend(batch)

    if not batch or len(accounts) >= result.get("total", 0):
        break

    page += 1

df = pd.DataFrame(accounts)

fields = [
    "account_id", "name", "status",
    "lifetime_revenue", "outstanding_ar",
    "chow_current_account", "duplicate_of_account",
    "parent_id", "note"
]

audit = df[fields].copy()

audit["requires_financial_review"] = (
    (pd.to_numeric(audit["outstanding_ar"], errors="coerce").fillna(0) != 0)
    | audit["chow_current_account"].fillna("").astype(str).str.strip().ne("")
    | audit["duplicate_of_account"].fillna("").astype(str).str.strip().ne("")
)

audit.to_csv("crm_financial_audit.csv", index=False)

print("CRM accounts audited:", len(audit))
print("Accounts requiring financial review:", audit["requires_financial_review"].sum())
print("Accounts with outstanding AR:",
      (pd.to_numeric(audit["outstanding_ar"], errors="coerce").fillna(0) != 0).sum())
print("Saved crm_financial_audit.csv")
