import os
from openai import OpenAI

# ✅ Load API key + Project ID
api_key = os.getenv("OPENAI_API_KEY")
project_id = os.getenv("OPENAI_PROJECT_ID")

if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found. Please set it in your .env or Streamlit secrets.")

if not project_id:
    raise ValueError("❌ OPENAI_PROJECT_ID not found. Please set it in your .env or Streamlit secrets.")

# ✅ Initialize OpenAI client with project auth
client = OpenAI(api_key=api_key, project=project_id)

def tailor_resume(resume_text: str, job_desc: str) -> str:
    """
    Uses OpenAI (with project-scoped keys) to tailor resume & cover letter.
    """
    prompt = f"""
    You are an AI career assistant.
    Given this resume and job description:
    ---
    Resume: {resume_text}
    ---
    Job Description: {job_desc}
    ---
    Create:
    1. A tailored resume (optimized for the job).
    2. A tailored cover letter.
    Format clearly with headings.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # ✅ safe lightweight model
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content
