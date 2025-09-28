import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

def tailor_resume(resume_text, job_desc):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("❌ OPENAI_API_KEY not found. Please set it in your .env file.")

    client = OpenAI(api_key=api_key)

    # Structured prompt
    prompt = f"""
    You are an AI career coach.
    Rewrite the resume to fit this job description.

    JOB DESCRIPTION:
    {job_desc}

    RESUME:
    {resume_text}

    Output strictly in this format:

    ### Tailored Resume
    (Write improved bullet points here)

    ### Tailored Cover Letter
    (Write a professional cover letter here)
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content
