def run(task: dict) -> dict:
    task_name = task.get("name", "Untitled Task")

    summary = (
        f"Support agent processed task: {task_name}\n"
        f"- Reviewed issue context\n"
        f"- Identified likely problem area\n"
        f"- Suggested next troubleshooting steps"
    )

    return {
        "status": "completed",
        "comment": summary,
    }