import os
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found. Please set it in your environment or .env file.")

# ✅ Initialize OpenAI client
client = OpenAI(api_key=api_key)

def tailor_resume(resume_text, job_desc):
    prompt = f"""
    You are an AI resume assistant.
    Tailor the following resume to the job description.

    Resume:
    {resume_text}

    Job Description:
    {job_desc}

    Provide two sections:
    1. Tailored Resume
    2. Tailored Cover Letter
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # or gpt-4o if available
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content
