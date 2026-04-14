from app.clickup_client import (
    extract_custom_fields,
    update_task_status,
    add_task_comment,
)

from app.clickup_client import (
    add_task_comment,
    update_processing_status,
    update_review_status,
)

from app.agent_router import route_task
from app.certified_agents import onboarding_agent, support_agent, documentation_agent


def run_certified_agent(agent_name: str, task: dict) -> dict:
    if agent_name == "onboarding_agent":
        return onboarding_agent.run(task)
    if agent_name == "support_agent":
        return support_agent.run(task)
    if agent_name == "documentation_agent":
        return documentation_agent.run(task)

    return {
        "status": "completed",
        "comment": f"General agent processed task: {task.get('name', 'Untitled Task')}",
    }


def should_process_task(task: dict, custom_fields: dict) -> bool:
    processing_status = custom_fields.get("Processing Status")
    auto_process = custom_fields.get("Auto Process")

    if processing_status not in [None, "pending"]:
        return False

    if auto_process in [False, "false", "False", 0]:
        return False

    return True


def process_task(task: dict) -> dict:
    task_id = task["id"]
    custom_fields = extract_custom_fields(task)

    if not should_process_task(task, custom_fields):
        return {"status": "skipped", "reason": "Task not eligible for processing"}

    try:
        update_task_status(task_id, "in progress")

        # agent_name = route_task(task, custom_fields)
        # result = run_certified_agent(agent_name, task)

        agent_name = route_task(task)
        result = run_certified_agent(agent_name, task)

        print("DEBUG agent result:", result)

        add_task_comment(task_id, result["comment"])
        update_task_status(task_id, "complete")

        return {
            "status": "success",
            "agent": agent_name,
            "result": result,
        }

    except Exception as exc:
        add_task_comment(task_id, f"Agent processing failed: {str(exc)}")
        return {
            "status": "failed",
            "error": str(exc),
        }
    
def process_task_with_super_agent(task: dict) -> dict:
    task_id = task["id"]
    fields = extract_custom_fields(task)

    processing_status = fields.get("Processing Status")
    review_status = fields.get("Review Status")

    print("DEBUG normalized fields:", fields)

    # 1. First pass: generate draft
    if processing_status == "pending" and review_status in [None, "", 0]:
        agent_name = route_task(task, fields)
        result = run_certified_agent(agent_name, task)

        comment = str(result.get("comment", "")).strip()
        if not comment:
            raise ValueError("Agent returned empty comment")

        add_task_comment(task_id, comment)
        update_processing_status(task, "running")
        update_review_status(task, "pending_review")

        return {"status": "awaiting_review"}

    # 2. Pause for human review
    if processing_status == "running" and review_status == "pending_review":
        print(f"Task {task_id} is waiting for human review")
        return {"status": "waiting_for_review"}

    # 3. Human approved
    if processing_status == "running" and review_status == "approved":
        add_task_comment(task_id, "✅ Review approved. Continuing workflow.")
        update_processing_status(task, "completed")
        return {"status": "completed"}

    # 4. Human rejected
    if review_status == "rejected":
        add_task_comment(task_id, "❌ Review rejected. Needs rework.")
        update_processing_status(task, "failed")
        return {"status": "failed"}

    return {"status": "ignored"}