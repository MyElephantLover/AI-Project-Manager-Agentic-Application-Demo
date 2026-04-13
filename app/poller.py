import os
import time
import sqlite3
from typing import Any
import json
from app.ai_service import generate_intake_summary
from app.clickup_client import update_task_status
from app.super_agent import process_task_with_super_agent

import requests
from dotenv import load_dotenv

load_dotenv()

CLICKUP_TOKEN = os.getenv("CLICKUP_TOKEN")
CLICKUP_LIST_ID = os.getenv("CLICKUP_LIST_ID")
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "30"))

if not CLICKUP_TOKEN:
    raise ValueError("Missing CLICKUP_TOKEN in .env")

if not CLICKUP_LIST_ID:
    raise ValueError("Missing CLICKUP_LIST_ID in .env")

BASE_URL = "https://api.clickup.com/api/v2"

HEADERS = {
    "Authorization": CLICKUP_TOKEN,
    "Content-Type": "application/json",
}

DB_PATH = "processed_tasks.db"


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS processed_tasks (
            task_id TEXT PRIMARY KEY,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def has_been_processed(task_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM processed_tasks WHERE task_id = ?",
        (task_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return row is not None


def mark_as_processed(task_id: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO processed_tasks (task_id) VALUES (?)",
        (task_id,),
    )
    conn.commit()
    conn.close()


def get_tasks_from_list(list_id: str) -> list[dict[str, Any]]:
    url = f"{BASE_URL}/list/{list_id}/task"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data.get("tasks", [])


# def is_new_intake(task: dict[str, Any]) -> bool:
#     status_obj = task.get("status", {})
#     status_name = status_obj.get("status", "")
#     return status_name.strip().lower() == "new intake"

def is_new_intake(task: dict[str, Any]) -> bool:
    status_obj = task.get("status", {})
    status_name = status_obj.get("status", "")
    return status_name.strip().lower() == "new submission"

def should_check_task(task: dict[str, Any]) -> bool:
    return is_new_intake(task)


def add_comment_to_task(task_id: str, comment_text: str) -> None:
    url = f"{BASE_URL}/task/{task_id}/comment"
    payload = {
        "comment_text": comment_text,
        "notify_all": False,
    }
    response = requests.post(url, headers=HEADERS, json=payload, timeout=30)
    response.raise_for_status()

# def update_task_status(task_id: str, status: str) -> None:
#     url = f"{BASE_URL}/task/{task_id}"
#     payload = {"status": status}
#     response = requests.put(url, headers=HEADERS, json=payload, timeout=30)
#     response.raise_for_status()

# def process_task(task):
#     task_id = task["id"]
#     task_name = task.get("name", "")
#     description = task.get("description", "")

#     print(f"Processing task: {task_name}")

#     # Call AI
#     ai_summary = generate_intake_summary(task_name, description)

#     # Add AI comment to ClickUp
#     add_comment_to_task(task_id, ai_summary)

#     # Move task forward
#     update_task_status(task_id, "Processing")  # use your real status

#     # Save as processed
#     mark_as_processed(task_id)

def process_task(task):
    result = process_task_with_super_agent(task)

    if result.get("status") == "success":
        mark_as_processed(task["id"])

def poll_once() -> None:
    print("Polling ClickUp for tasks...")
    tasks = get_tasks_from_list(CLICKUP_LIST_ID)
    print(f"Found {len(tasks)} total tasks")

    for task in tasks:
        #print(json.dumps(task, indent=2))
        print(
            f'- Task: {task.get("name")} | '
            f'Status: {task.get("status", {}).get("status")} | '
            f'ID: {task.get("id")}'
        )

        task_id = task["id"]
        task_name = task.get("name", "(no name)")

        if should_check_task(task):
            process_task_with_super_agent(task)

        if not is_new_intake(task):
            continue

        if has_been_processed(task_id):
            print(f"Skipping already processed task: {task_name} ({task_id})")
            continue

        try:
            process_task(task)
        except Exception as exc:
            print(f"Error processing task {task_name} ({task_id}): {exc}")


def main() -> None:
    init_db()
    print(f"Starting poller. Interval: {POLL_INTERVAL_SECONDS} seconds")

    while True:
        try:
            poll_once()
        except Exception as exc:
            print(f"Polling error: {exc}")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()





