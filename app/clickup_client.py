import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLICKUP_TOKEN = os.getenv("CLICKUP_TOKEN")
CLICKUP_LIST_ID = os.getenv("CLICKUP_LIST_ID")

BASE_URL = "https://api.clickup.com/api/v2"
HEADERS = {
    "Authorization": CLICKUP_TOKEN,
    "Content-Type": "application/json",
}


def get_tasks():
    url = f"{BASE_URL}/list/{CLICKUP_LIST_ID}/task"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json().get("tasks", [])


def get_new_intake_tasks():
    tasks = get_tasks()
    return [t for t in tasks if t["status"]["status"] == "New Intake"]


def post_comment(task_id: str, comment_text: str):
    url = f"{BASE_URL}/task/{task_id}/comment"
    payload = {"comment_text": comment_text}
    response = requests.post(url, headers=HEADERS, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()

def update_task_status(task_id: str, new_status: str):
    url = f"{BASE_URL}/task/{task_id}"
    payload = {
        "status": new_status
    }
    response = requests.put(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()

