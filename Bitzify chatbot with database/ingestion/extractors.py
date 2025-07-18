import fitz
import pandas as pd
from docx import Document

def extract_from_pdf(path):
    return "\n".join(page.get_text() for page in fitz.open(path))

def extract_from_excel(path):
    df = pd.read_excel(path)
    return "\n".join(df.astype(str).apply(" | ".join, axis=1))

def extract_from_docx(path):
    doc = Document(path)
    return "\n".join(para.text for para in doc.paragraphs)

def extract_from_txt(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
