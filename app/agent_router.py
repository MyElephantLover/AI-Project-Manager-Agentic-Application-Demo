from app.clickup_client import extract_custom_fields

TASK_TO_AGENT = {
    "onboarding": "onboarding_agent",
    "incident": "support_agent",
    "kb_update": "documentation_agent",
}


def route_task(task: dict, custom_fields: dict) -> str:
    explicit_agent = custom_fields.get("Agent Type")
    if explicit_agent:
        return explicit_agent

    task_type = custom_fields.get("Task Type")
    return TASK_TO_AGENT.get(task_type, "general_agent")