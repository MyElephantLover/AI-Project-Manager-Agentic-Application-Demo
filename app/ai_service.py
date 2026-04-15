import os
from dotenv import load_dotenv
from openai import OpenAI
from app.rag import query_kb

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env")

client = OpenAI(api_key=api_key)

# def generate_intake_summary(task_name: str, description: str) -> str:
#     prompt = f"""
# You are an AI project manager assistant.

# Analyze this task and return:
# 1. Summary
# 2. Category
# 3. Priority
# 4. Recommended next step
# 5. Clarifying questions

# Task name: {task_name}
# Description: {description if description else "No description provided."}
# """

#     response = client.responses.create(
#         model="gpt-5.4",
#         input=prompt,
#     )
#     return response.output_text


# def generate_intake_summary(task_name, description):
#     kb_context = query_kb(task_name + " " + description)

#     prompt = f"""
#     You are an onboarding agent.

#     Use the knowledge base context below to improve your answer.

#     Knowledge Base:
#     {kb_context}

#     Task: {task_name}
#     Description: {description}

#     Generate:
#     1. Onboarding Summary
#     2. Risks
#     3. Next Steps
#     """

def generate_intake_summary(task_name: str, description: str) -> str:
    safe_description = description if description else "No description provided."
    kb_context = query_kb(f"{task_name}\n{safe_description}")

    prompt = f"""
You are a Certified Onboarding Agent for Meridian E-Co.

Use the following sources of context in order:
1. ClickUp task data (primary)
2. Internal knowledge base context
3. CRM context if available

Knowledge Base Context:
{kb_context}

Task Name:
{task_name}

Task Description:
{safe_description}

Your task is to:
1. Review the intake task and description
2. Identify onboarding needs
3. Generate a structured onboarding summary
4. Highlight risks and dependencies
5. Recommend next steps and ownership

If required context is missing, clearly state assumptions.
Do not execute actions or modify task state.
Prepare output for human review.

Return your answer in exactly this format:

Onboarding Summary:
- ...

Next Steps:
- ...

Risk Flags:
- ...

Recommended Owner:
- ...
"""

    response = client.responses.create(
        model="gpt-5.4",
        input=prompt,
    )
    return response.output_text