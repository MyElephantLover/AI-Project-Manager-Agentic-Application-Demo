import os
import requests
from dotenv import load_dotenv

# Load .env
load_dotenv()

CLICKUP_TOKEN = os.getenv("CLICKUP_TOKEN")
CLICKUP_LIST_ID = os.getenv("CLICKUP_LIST_ID")

if not CLICKUP_TOKEN:
    raise ValueError("Missing CLICKUP_TOKEN")

if not CLICKUP_LIST_ID:
    raise ValueError("Missing CLICKUP_LIST_ID")

BASE_URL = "https://api.clickup.com/api/v2"

HEADERS = {
    "Authorization": CLICKUP_TOKEN,
    "Content-Type": "application/json",
}

# 🔍 Get list details (including statuses)
url = f"{BASE_URL}/list/{CLICKUP_LIST_ID}"

resp = requests.get(url, headers=HEADERS, timeout=30)
resp.raise_for_status()

data = resp.json()

print("Statuses for this list:\n")
for status in data.get("statuses", []):
    print(f"- Name: {status['status']} | ID: {status['id']}")