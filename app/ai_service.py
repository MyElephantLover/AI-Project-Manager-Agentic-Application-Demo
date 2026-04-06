import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env")

client = OpenAI(api_key=api_key)

def generate_intake_summary(task_name: str, description: str) -> str:
    prompt = f"""
You are an AI project manager assistant.

Analyze this task and return:
1. Summary
2. Category
3. Priority
4. Recommended next step
5. Clarifying questions

Task name: {task_name}
Description: {description if description else "No description provided."}
"""

    response = client.responses.create(
        model="gpt-5.4",
        input=prompt,
    )
    return response.output_text