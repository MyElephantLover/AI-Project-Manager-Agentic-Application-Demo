import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLICKUP_TOKEN = os.getenv("CLICKUP_TOKEN")

headers = {
   "Authorization": CLICKUP_TOKEN,
   "Content-Type": "application/json",
}

resp = requests.get("https://api.clickup.com/api/v2/team", headers=headers)
print(resp.status_code)
print(resp.text)
