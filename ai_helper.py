import os
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
project_id = os.getenv("OPENAI_PROJECT_ID")

if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in environment.")
if not project_id:
    raise ValueError("❌ OPENAI_PROJECT_ID not found in environment.")

client = OpenAI(api_key=api_key, project=project_id)

def tailor_resume(resume_text: str, job_desc: str) -> str:
    prompt = f"""
    You are an AI career assistant.
    Resume: {resume_text}
    Job Description: {job_desc}
    ---
    Create:
    1. A tailored resume (optimized for the job).
    2. A tailored cover letter.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
