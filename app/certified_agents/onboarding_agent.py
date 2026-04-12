def run(task: dict) -> dict:
    task_name = task.get("name", "Untitled Task")

    summary = (
        f"Onboarding agent processed task: {task_name}\n"
        f"- Reviewed onboarding context\n"
        f"- Generated initial onboarding plan\n"
        f"- Recommended next actions"
    )

    return {
        "status": "completed",
        "comment": summary,
    }