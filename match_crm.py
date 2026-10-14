import re
from difflib import SequenceMatcher

import pandas as pd
import requests
import streamlit as st

BASE = st.secrets["CRM_BASE_URL"].rstrip("/")
HEADERS = {"Authorization": f'Bearer {st.secrets["CRM_TOKEN"]}'}

facilities = pd.read_csv("facilities.csv").fillna("")
accounts = []
page = 1

while True:
    response = requests.get(
        f"{BASE}/accounts",
        headers=HEADERS,
        params={"page": page, "page_size": 100},
        timeout=30,
    )
    response.raise_for_status()
    result = response.json()
    batch = result.get("data", [])
    accounts.extend(batch)

    if not batch or len(accounts) >= result.get("total", 0):
        break
    page += 1

ABBREVIATIONS = {
    "rd": "road", "st": "street", "ave": "avenue",
    "blvd": "boulevard", "dr": "drive", "ln": "lane",
    "ct": "court", "pkwy": "parkway", "hwy": "highway",
}

def clean(value):
    words = re.sub(r"[^a-z0-9 ]", " ", str(value).lower()).split()
    return " ".join(ABBREVIATIONS.get(w, w) for w in words)

def similarity(a, b):
    return SequenceMatcher(None, clean(a), clean(b)).ratio()

def parse_address(address):
    address = str(address).strip()
    match = re.search(r"^(.*?),\s*([A-Z]{2})\s+(\d{5})$", address)

    if not match:
        return address, "", "", ""

    street_city, state, zipcode = match.groups()

    cities = sorted(
        {str(a.get("billing_city", "")).strip()
         for a in accounts if a.get("billing_city")},
        key=len,
        reverse=True,
    )

    for city in cities:
        if street_city.lower().endswith(" " + city.lower()):
            return street_city[:-(len(city) + 1)], city, state, zipcode

    return street_city, "", state, zipcode

rows = []

for _, facility in facilities.iterrows():
    street, city, state, zipcode = parse_address(facility["address"])
    candidates = []

    for account in accounts:
        name_match = similarity(facility["name"], account.get("name", ""))
        street_match = similarity(street, account.get("billing_street", ""))
        city_match = clean(city) == clean(account.get("billing_city", ""))
        state_match = clean(state) == clean(account.get("billing_state", ""))
        zip_match = str(zipcode) == str(account.get("billing_zip", ""))

        score = (
            name_match * 45
            + street_match * 30
            + (10 if city_match and city else 0)
            + (10 if state_match and state else 0)
            + (5 if zip_match and zipcode else 0)
        )

        candidates.append((score, account))

    candidates.sort(key=lambda x: x[0], reverse=True)
    score, best = candidates[0]

    address_conflict = (
        clean(state) != clean(best.get("billing_state", ""))
        or (city and clean(city) != clean(best.get("billing_city", "")))
    )

    ownership_flag = bool(
        best.get("chow_current_account")
        or best.get("duplicate_of_account")
    )

    if address_conflict or ownership_flag:
        recommendation = "Ownership/address review"
    elif score >= 90:
        recommendation = "Likely match - verify"
    elif score >= 70:
        recommendation = "Manual review"
    else:
        recommendation = "Potential missing account"

    rows.append({
        "facility": facility["name"],
        "facility_address": facility["address"],
        "crm_account": best.get("name", ""),
        "crm_account_id": best.get("account_id", ""),
        "crm_address": " ".join(str(best.get(k, "") or "") for k in [
            "billing_street", "billing_city", "billing_state", "billing_zip"
        ]).strip(),
        "confidence": round(score, 1),
        "recommendation": recommendation,
        "crm_status": best.get("status", ""),
        "chow_current_account": best.get("chow_current_account", ""),
        "duplicate_of_account": best.get("duplicate_of_account", ""),
    })

df = pd.DataFrame(rows)
df.to_csv("crm_matches.csv", index=False)

print("Facilities compared:", len(facilities))
print("CRM accounts compared:", len(accounts))
print("\nMatching results:")
print(df["recommendation"].value_counts().to_string())
print("\nSaved crm_matches.csv")
