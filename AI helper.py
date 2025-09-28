import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def tailor_resume(resume_text, job_desc):
    prompt = f"""
    You are an AI career coach.
    Task: Rewrite the resume content so it matches this job description:
    JOB DESCRIPTION:
    {job_desc}

    RESUME:
    {resume_text}

    Output:
    1. Improved Resume Bullet Points (optimized for the job).
    2. Tailored Cover Letter.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content
