import os
import requests

from dotenv import load_dotenv

load_dotenv()

CLICKUP_API_KEY = os.getenv("CLICKUP_API_KEY")
CLICKUP_LIST_ID = os.getenv("CLICKUP_LIST_ID")

BASE_URL = "https://api.clickup.com/api/v2"
HEADERS = {
    "Authorization": CLICKUP_API_KEY,
    "Content-Type": "application/json",
}


def get_tasks_from_list():
    url = f"{BASE_URL}/list/{CLICKUP_LIST_ID}/task"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json().get("tasks", [])


def get_task(task_id: str):
    url = f"{BASE_URL}/task/{task_id}"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def add_task_comment(task_id: str, comment_text: str):
    url = f"{BASE_URL}/task/{task_id}/comment"
    payload = {"comment_text": comment_text}
    response = requests.post(url, headers=HEADERS, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def update_task_status(task_id: str, status: str):
    url = f"{BASE_URL}/task/{task_id}"
    payload = {"status": status}
    response = requests.put(url, headers=HEADERS, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def extract_custom_fields(task: dict) -> dict:
    field_map = {}
    for field in task.get("custom_fields", []):
        name = field.get("name")
        value = field.get("value")
        field_map[name] = value
    return field_map


def get_custom_field_id(task: dict, field_name: str) -> str | None:
    for field in task.get("custom_fields", []):
        if field.get("name") == field_name:
            return field.get("id")
    return None


def update_custom_field(task_id: str, field_id: str, value):
    url = f"{BASE_URL}/task/{task_id}/field/{field_id}"
    payload = {"value": value}
    response = requests.post(url, headers=HEADERS, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def update_processing_status(task: dict, value):
    task_id = task["id"]
    field_id = get_custom_field_id(task, "Processing Status")

    if not field_id:
        raise ValueError("Processing Status field not found on task")

    return update_custom_field(task_id, field_id, value)


def update_review_status(task: dict, value):
    task_id = task["id"]
    field_id = get_custom_field_id(task, "Review Status")

    if not field_id:
        raise ValueError("Review Status field not found on task")

    return update_custom_field(task_id, field_id, value)