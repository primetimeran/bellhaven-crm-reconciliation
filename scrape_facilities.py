import csv
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://analyst-assessment-production.up.railway.app"
session = requests.Session()
links = {}

for page in range(1, 11):
    url = f"{BASE}/communities?page={page}"
    response = session.get(url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    found = {}
    for a in soup.select('a[href]'):
        full_url = urljoin(url, a["href"]).split("#")[0]
        if "/communities/" in full_url:
            found[full_url] = a.get_text(" ", strip=True)

    before = len(links)
    links.update(found)
    print(f"Page {page}: {len(found)} links, {len(links)} unique")

    if len(links) == before:
        break

records = []

for url, listing_name in sorted(links.items()):
    response = session.get(url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    h1 = soup.find("h1")
    name = h1.get_text(" ", strip=True) if h1 else listing_name

    text = soup.get_text(" ", strip=True)

    address_match = re.search(
        r"Address\s+(.+?)\s+Care Offerings",
        text, flags=re.IGNORECASE
    )
    care_match = re.search(
        r"Care Offerings\s+(.+?)\s+Administrator",
        text, flags=re.IGNORECASE
    )

    address = address_match.group(1).strip() if address_match else ""
    care = care_match.group(1).strip() if care_match else ""

    records.append({
        "name": name,
        "address": address,
        "care_offerings": care,
        "source_url": url
    })

    print(f"Extracted: {name}")

with open("facilities.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["name", "address", "care_offerings", "source_url"]
    )
    writer.writeheader()
    writer.writerows(records)

print("\nCOMPLETE")
print("Facilities saved:", len(records))
print("File: facilities.csv")
print("Missing addresses:", sum(not r["address"] for r in records))
print("Missing care offerings:", sum(not r["care_offerings"] for r in records))
