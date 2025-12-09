# core/utils.py
import re
from PyPDF2 import PdfReader
from docx import Document

def extract_text_from_pdf(path):
    text = ""
    try:
        reader = PdfReader(path)
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
    except Exception:
        # fallback empty string
        pass
    return text

def extract_text_from_docx(path):
    text_parts = []
    try:
        doc = Document(path)
        for p in doc.paragraphs:
            text_parts.append(p.text)
    except Exception:
        pass
    return "\n".join(text_parts)

def extract_text_from_file(file_path, filename):
    name = filename.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    if name.endswith(".docx"):
        return extract_text_from_docx(file_path)
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""

def compute_alignment_score(resume_text, jd_text):
    r_words = set(re.findall(r"\w+", (resume_text or "").lower()))
    jd_words = set(re.findall(r"\w+", (jd_text or "").lower()))
    if not jd_words:
        return 0.0
    matched = len(jd_words & r_words)
    score = (matched / len(jd_words)) * 100
    return round(score, 2)

def suggest_improvements(resume_text, jd_text):
    r_words = set(re.findall(r"\w+", (resume_text or "").lower()))
    jd_words = set(re.findall(r"\w+", (jd_text or "").lower()))
    missing = sorted(list(jd_words - r_words))[:30]
    suggestions = []
    if missing:
        suggestions.append("Keywords missing from resume (top 30): " + ", ".join(missing))
    if len((resume_text or "").strip()) < 200:
        suggestions.append("Resume is short — consider adding details about projects, responsibilities, and measurable results.")
    suggestions.append('Consider adding a clear "Skills" section with bullet points matching JD keywords.')
    return "\n\n".join(suggestions)
