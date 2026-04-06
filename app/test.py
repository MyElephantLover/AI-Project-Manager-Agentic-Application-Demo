import os
import requests
from dotenv import load_dotenv

load_dotenv()

# CLICKUP_TOKEN = os.getenv("CLICKUP_TOKEN")

# headers = {
#    "Authorization": CLICKUP_TOKEN,
#    "Content-Type": "application/json",
# }

# resp = requests.get("https://api.clickup.com/api/v2/team", headers=headers)
# print(resp.status_code)
# print(resp.text)


from app.clickup_client import get_new_intake_tasks

tasks = get_new_intake_tasks()
print(f"Found {len(tasks)} New Intake tasks")
for t in tasks:
    print(t["id"], t["name"])

from app.rag import build_vector_store, query_kb

build_vector_store()
results = query_kb("bug in checkout button")
for r in results:
    print(r.metadata, r.page_content[:200])

from app.rag import query_kb, generate_triage_response

task_text = """
Title: Checkout button does nothing
Description: Users click the checkout button and the page does not respond. This affects multiple customers in production.
"""

results = query_kb(task_text, k=3)

print("=== Retrieved Context ===")
for r in results:
    print(r.metadata, r.page_content[:300])
    print("-" * 40)

response = generate_triage_response(task_text, results)

print("\n=== Triage Recommendation ===")
print(response)


# from app.clickup_client import post_comment

# task_id = "86b99bjyw"
# comment = """Category: Bug
# Priority: P1
# Owner: Frontend Team
# Next Action: Move to In Progress
# Reasoning: This impacts a core user flow and affects multiple users in production."""
# post_comment(task_id, comment)
# print("Comment posted.")
