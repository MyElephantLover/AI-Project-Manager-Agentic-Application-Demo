from clickup_client import (
    extract_custom_fields,
    update_task_status,
    add_task_comment,
)
from agent_router import route_task
from certified_agents import onboarding_agent, support_agent, documentation_agent


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

        agent_name = route_task(task, custom_fields)
        result = run_certified_agent(agent_name, task)

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