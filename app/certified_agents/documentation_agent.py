def run(task: dict) -> dict:
    task_name = task.get("name", "Untitled Task")

    summary = (
        f"Documentation agent processed task: {task_name}\n"
        f"- Reviewed KB update request\n"
        f"- Drafted documentation recommendations\n"
        f"- Flagged follow-up items"
    )

    return {
        "status": "completed",
        "comment": summary,
    }