import os
import openai

# ✅ Load API key once
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found. Please set it in your .env file.")

openai.api_key = api_key

def tailor_resume(resume_text: str, job_desc: str) -> str:
    """
    Uses OpenAI to tailor resume & cover letter to job description.
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

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",   # ✅ classic stable model
        messages=[{"role": "user", "content": prompt}],
    )

    return response["choices"][0]["message"]["content"]
