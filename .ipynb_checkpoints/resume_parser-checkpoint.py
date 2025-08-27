import os
import docx2txt
import PyPDF2
from io import BytesIO
import pytesseract
from PIL import Image
import re
from word2number import w2n
from rapidfuzz import fuzz
from pdf2image import convert_from_bytes

# Set your Poppler path (for OCR PDF)
POPPLER_PATH = r"C:\\Users\\Mayuri\\Downloads\\Release-24.08.0-0\\Library\\bin"

def extract_text_from_pdf(file):
    text = ''
    try:
        file.seek(0)
        pdf_reader = PyPDF2.PdfReader(BytesIO(file.read()))
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        print(f"PDF direct text extraction failed: {e}")
        text = ''

    if not text.strip():
        try:
            file.seek(0)
            images = convert_from_bytes(file.read(), poppler_path=POPPLER_PATH)
            text = ''
            for img in images:
                text += pytesseract.image_to_string(img)
        except Exception as e:
            print("OCR failed:", e)
            return None

    return text.lower()

def extract_text_from_docx(file):
    try:
        file.seek(0)
        return docx2txt.process(BytesIO(file.read())).lower()
    except Exception as e:
        print("DOCX extraction failed:", e)
        return None

def extract_text_from_image(file):
    try:
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
        return text.lower()
    except Exception as e:
        print("Image OCR failed:", e)
        return None

def extract_text_from_file(file):
    filename = file.name
    extension = filename.split('.')[-1].lower()

    if extension == "pdf":
        return extract_text_from_pdf(file)
    elif extension == "docx":
        return extract_text_from_docx(file)
    elif extension in ['jpg', 'jpeg', 'png']:
        return extract_text_from_image(file)
    else:
        print(f"Unsupported file format: {extension}")
        return None

def extract_experience(text):
    text = text.lower()
    years = []

    matches = re.findall(r'(\d+)\s*\+?\s*(?:years?|yrs?)', text)
    years.extend([int(m) for m in matches])

    matches_spelled = re.findall(r'([a-z]+)\s*(?:years?|yrs?)', text)
    for word in matches_spelled:
        try:
            years.append(w2n.word_to_num(word))
        except:
            continue

    return max(years, default=0)

def extract_education(text):
    text = text.lower()
    if "phd" in text or "doctor of philosophy" in text:
        return "PhD"
    elif any(x in text for x in ["master", "msc", "m.tech", "mtech"]):
        return "Master's"
    elif any(x in text for x in ["bachelor", "bsc", "b.tech", "btech"]):
        return "Bachelor's"
    else:
        return "Unknown"

def extract_skills(text, relevant_skills):
    text = text.lower()
    found_skills = []
    for skill in relevant_skills:
        if fuzz.partial_ratio(skill.lower(), text) >= 85:
            found_skills.append(skill.lower())
    return list(set(found_skills))

def extract_certifications(text, certifications_list):
    text = text.lower()
    found = 0
    for cert in certifications_list:
        if fuzz.partial_ratio(cert.lower(), text) >= 85:
            found += 1
    return found

def extract_features_from_resume(file, relevant_skills, certifications_list):
    text = extract_text_from_file(file)
    if text is None:
        return None

    experience = extract_experience(text)
    education = extract_education(text)
    skills_matched = extract_skills(text, relevant_skills)
    cert_count = extract_certifications(text, certifications_list)

    return experience, education, skills_matched, cert_count
