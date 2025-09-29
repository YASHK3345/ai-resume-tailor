import streamlit as st
import sys, os

# ✅ Ensure backend folder is always in path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from parser import parse_pdf, parse_docx
from ai_helper import tailor_resume
from fpdf import FPDF   # using fpdf2 (supports Unicode)

st.set_page_config(page_title="AI Resume Tailor", page_icon="📄")

st.title("📄 AI Resume Tailor")
st.write("Upload your resume and paste a job description to get a tailored version with AI.")

# 📂 Resume Upload
uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

resume_text = ""
if uploaded_file:
    if uploaded_file.name.endswith(".pdf"):
        resume_text = parse_pdf(uploaded_file)
    else:
        uploaded_file.seek(0)  # reset pointer before reading
        resume_text = parse_docx(uploaded_file)

    st.subheader("📑 Extracted Resume Text")
    st.text_area("Resume Content", resume_text, height=200)

# 📝 Job Description Input
job_desc = st.text_area("Paste Job Description Here:", height=150)

# 🚀 Tailor with AI
if st.button("🚀 Tailor Resume with AI"):
    if resume_text and job_desc:
        with st.spinner("⏳ AI is tailoring your resume..."):
            result = tailor_resume(resume_text, job_desc)

        # Show result in the app
        st.subheader("✨ Tailored Resume + Cover Letter")
        st.markdown(result)

        # 📥 PDF Export (fpdf2 handles Unicode safely)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)

        for line in result.split("\n"):
            if line.strip():
                pdf.multi_cell(0, 10, line)

        pdf_file = "tailored_resume.pdf"
        pdf.output(pdf_file)

        with open(pdf_file, "rb") as f:
            st.download_button(
                label="📥 Download Tailored Resume & Cover Letter (PDF)",
                data=f,
                file_name="tailored_resume.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("⚠️ Please upload a resume and paste a job description.")
