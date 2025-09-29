import streamlit as st
import sys, os
from fpdf import FPDF   # using fpdf2 (Unicode-ready)

# ✅ Ensure backend folder is always in path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from parser import parse_pdf, parse_docx
from ai_helper import tailor_resume

# Page config
st.set_page_config(page_title="AI Resume Tailor", page_icon="📄", layout="wide")

# Custom CSS for modern look
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        text-align: center;
        background: -webkit-linear-gradient(45deg, #FF512F, #DD2476);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(45deg, #FF512F, #DD2476);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
    }
    .stDownloadButton>button {
        background: #222;
        color: white;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-size: 0.95rem;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar info
st.sidebar.title("ℹ️ About AI Resume Tailor")
st.sidebar.write(
    "This app helps you tailor your resume and cover letter to a job description using AI. "
    "Upload your resume, paste a job description, and get a customized PDF instantly."
)
st.sidebar.markdown("---")
st.sidebar.write("👨‍💻 Built by [YASHK3345](https://github.com/YASHK3345)")

# Main Title
st.markdown("<h1 class='main-title'>📄 AI Resume Tailor</h1>", unsafe_allow_html=True)

# 📂 Two-column input layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Upload Your Resume")
    uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])

with col2:
    st.subheader("📝 Paste Job Description")
    job_desc = st.text_area("Job Description", height=280)

resume_text = ""
if uploaded_file:
    if uploaded_file.name.endswith(".pdf"):
        resume_text = parse_pdf(uploaded_file)
    else:
        uploaded_file.seek(0)
        resume_text = parse_docx(uploaded_file)

    st.success("✅ Resume uploaded successfully!")

# 🚀 Tailor with AI
if st.button("🚀 Tailor Resume Now"):
    if resume_text and job_desc:
        with st.spinner("⏳ AI is tailoring your resume..."):
            result = tailor_resume(resume_text, job_desc)

        st.subheader("✨ Tailored Resume + Cover Letter")
        st.markdown(result)

        # 📥 PDF Export with Unicode + Bold headers
        pdf = FPDF()
        pdf.add_page()

        # ✅ Load fonts (regular, bold, italic)
        font_path = os.path.join(os.path.dirname(__file__), "fonts")
        try:
            pdf.add_font("DejaVu", "", os.path.join(font_path, "DejaVuSans.ttf"), uni=True)
            pdf.add_font("DejaVu", "B", os.path.join(font_path, "DejaVuSans-Bold.ttf"), uni=True)
            pdf.add_font("DejaVu", "I", os.path.join(font_path, "DejaVuSans-Oblique.ttf"), uni=True)
            pdf.set_font("DejaVu", size=12)
        except FileNotFoundError:
            pdf.set_font("Helvetica", size=12)

        # Split AI result into sections
        sections = result.split("###")
        for section in sections:
            if not section.strip():
                continue

            if "Tailored Resume" in section:
                pdf.set_font("DejaVu", "B", 14)
                pdf.cell(0, 12, "Tailored Resume", ln=True)
                pdf.ln(4)
                pdf.set_font("DejaVu", "", 12)
                pdf.multi_cell(0, 10, section.replace("Tailored Resume", "").strip())

            elif "Tailored Cover Letter" in section:
                pdf.add_page()
                pdf.set_font("DejaVu", "B", 14)
                pdf.cell(0, 12, "Tailored Cover Letter", ln=True)
                pdf.ln(4)
                pdf.set_font("DejaVu", "", 12)
                pdf.multi_cell(0, 10, section.replace("Tailored Cover Letter", "").strip())

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
        st.error("⚠️ Please upload a resume and paste a job description.")
