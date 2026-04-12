from fastapi import APIRouter, Request
from clickup_client import get_task
from agent_router import route_task

router = APIRouter()

@router.post("/clickup/webhook")
async def clickup_webhook(request: Request):
    payload = await request.json()

    print("🔔 Webhook received:", payload)

    task_id = payload.get("task_id")

    if not task_id:
        return {"status": "ignored", "reason": "no task_id"}

    # Step 1: fetch full task
    task = get_task(task_id)

    # Step 2: route to agent
    agent_type = route_task(task)

    print(f"🤖 Routing to agent: {agent_type}")

    # Step 3: run your pipeline
    run_agent(agent_type, task)   # ← your existing function

    return {"status": "processed"}