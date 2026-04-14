import os
import requests

from dotenv import load_dotenv

load_dotenv()

# CLICKUP_API_KEY = os.getenv("CLICKUP_API_KEY")

CLICKUP_API_KEY = os.getenv("CLICKUP_API_KEY") or os.getenv("CLICKUP_TOKEN")
CLICKUP_LIST_ID = os.getenv("CLICKUP_LIST_ID")

if not CLICKUP_API_KEY:
    raise ValueError("Missing CLICKUP_API_KEY or CLICKUP_TOKEN in .env")

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


# def add_task_comment(task_id: str, comment_text: str):
#     url = f"{BASE_URL}/task/{task_id}/comment"
#     payload = {"comment_text": comment_text}
#     response = requests.post(url, headers=HEADERS, json=payload, timeout=30)
#     response.raise_for_status()
#     return response.json()

def add_task_comment(task_id: str, comment_text: str):
    url = f"{BASE_URL}/task/{task_id}/comment"
    payload = {
        "comment_text": str(comment_text).strip(),
        "notify_all": False,
    }

    print("DEBUG add_task_comment()")
    print("DEBUG task_id:", task_id)
    print("DEBUG payload:", payload)

    response = requests.post(url, headers=HEADERS, json=payload, timeout=30)

    print("DEBUG response status:", response.status_code)
    print("DEBUG response body:", response.text)

    response.raise_for_status()
    return response.json()


def update_task_status(task_id: str, status: str):
    url = f"{BASE_URL}/task/{task_id}"
    payload = {"status": status}
    response = requests.put(url, headers=HEADERS, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()

# def extract_custom_fields(task: dict) -> dict:
#     field_map = {}
#     for field in task.get("custom_fields", []):
#         name = field.get("name")
#         value = field.get("value")
#         field_map[name] = value
#     return field_map

def extract_custom_fields(task: dict) -> dict:
    field_map = {}

    for field in task.get("custom_fields", []):
        name = field.get("name")
        raw_value = field.get("value")
        field_type = field.get("type")

        # Convert dropdown raw values/indexes into readable option names
        if field_type == "drop_down":
            options = field.get("type_config", {}).get("options", [])
            resolved_value = raw_value

            if isinstance(raw_value, int):
                # raw_value can be the option orderindex
                match = next(
                    (opt for opt in options if opt.get("orderindex") == raw_value),
                    None,
                )
                if match:
                    resolved_value = match.get("name")

            elif isinstance(raw_value, str):
                # sometimes raw_value can be the option UUID
                match = next(
                    (opt for opt in options if opt.get("id") == raw_value),
                    None,
                )
                if match:
                    resolved_value = match.get("name")

            field_map[name] = resolved_value
        else:
            field_map[name] = raw_value

    return field_map


def get_custom_field_id(task: dict, field_name: str) -> str | None:
    for field in task.get("custom_fields", []):
        if field.get("name") == field_name:
            return field.get("id")
    return None


# def update_custom_field(task_id: str, field_id: str, value):
#     url = f"{BASE_URL}/task/{task_id}/field/{field_id}"
#     payload = {"value": value}
#     response = requests.post(url, headers=HEADERS, json=payload, timeout=30)
#     response.raise_for_status()
#     return response.json()

def update_custom_field(task_id: str, field_id: str, value):
    url = f"{BASE_URL}/task/{task_id}/field/{field_id}"
    payload = {"value": value}

    print("DEBUG update_custom_field()")
    print("DEBUG task_id:", task_id)
    print("DEBUG field_id:", field_id)
    print("DEBUG payload:", payload)

    response = requests.post(url, headers=HEADERS, json=payload, timeout=30)

    print("DEBUG response status:", response.status_code)
    print("DEBUG response body:", response.text)

    response.raise_for_status()
    return response.json()


def update_processing_status(task: dict, value: str):
    task_id = task["id"]
    field_id = get_custom_field_id(task, "Processing Status")
    option_id = get_dropdown_option_id(task, "Processing Status", value)

    if not field_id:
        raise ValueError("Processing Status field not found on task")
    if not option_id:
        raise ValueError(f"Option '{value}' not found for Processing Status")

    return update_custom_field(task_id, field_id, option_id)


def update_review_status(task: dict, value: str):
    task_id = task["id"]
    field_id = get_custom_field_id(task, "Review Status")
    option_id = get_dropdown_option_id(task, "Review Status", value)

    if not field_id:
        raise ValueError("Review Status field not found on task")
    if not option_id:
        raise ValueError(f"Option '{value}' not found for Review Status")

    return update_custom_field(task_id, field_id, option_id)

def get_dropdown_option_id(task: dict, field_name: str, option_name: str) -> str | None:
    for field in task.get("custom_fields", []):
        if field.get("name") in ["Processing Status", "Review Status"]:
            print("DEBUG field metadata:", field)
        if field.get("name") != field_name:
            continue

        options = field.get("type_config", {}).get("options", [])
        for option in options:
            if option.get("name", "").strip().lower() == option_name.strip().lower():
                return option.get("id")

    return None