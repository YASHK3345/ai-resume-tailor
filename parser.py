import PyPDF2
import docx
import io

def parse_pdf(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def parse_docx(file):
    # Streamlit uploads files as BytesIO → convert it
    file_bytes = io.BytesIO(file.read())
    doc = docx.Document(file_bytes)
    text = "\n".join([p.text for p in doc.paragraphs])
    return text
