import os
import json
import pickle
import base64
import pytesseract
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from pdf2image import convert_from_path
from resume_parser import (
    extract_text_from_file,
    extract_experience,
    extract_skills,
    extract_education,
    extract_certifications
)

# Constants
RESUME_DIR = "resumes"
os.makedirs(RESUME_DIR, exist_ok=True)

# Clear previous resumes
for f in os.listdir(RESUME_DIR):
    file_path = os.path.join(RESUME_DIR, f)
    if os.path.isfile(file_path):
        os.remove(file_path)

# Load ML model
try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
except Exception as e:
    st.error(f"❌ Error loading the model: {e}")
    st.stop()

# Default certifications
DEFAULT_CERTIFICATIONS = ['aws certified developer', 'google cloud certified', 'pmp', 'azure']

# Education encoding
education_map = {"PhD": 3, "Master's": 2, "Bachelor's": 1, "Unknown": 0}

# Load recruiter preferences
preferences_file = "recruiter_preferences.json"
if os.path.exists(preferences_file):
    with open(preferences_file, "r") as f:
        recruiter_preferences = json.load(f)
else:
    recruiter_preferences = {
        "experience_weight": 25,
        "education_weight": 25,
        "skills_weight": 25,
        "certifications_weight": 25
    }

# OCR utility
def extract_text_with_ocr(file_path):
    ext = file_path.split('.')[-1].lower()

    if ext == 'pdf':  # For scanned PDFs
        images = convert_from_path(file_path)
        return " ".join([pytesseract.image_to_string(img) for img in images])

    elif ext in ['jpg', 'jpeg', 'png']:  # For image resumes
        image = Image.open(file_path)
        return pytesseract.image_to_string(image)

    # Skip OCR for DOCX or unsupported formats
    return ""


# Streamlit UI
st.title('📄 Automated Resume Screening System (ML-based)')
st.write("### Upload Resumes")
uploaded_files = st.file_uploader("Choose resumes", type=["pdf", "docx", "jpg", "jpeg", "png"], accept_multiple_files=True)

# Sidebar inputs
st.sidebar.title("Recruiter Inputs")
experience_weight = st.sidebar.slider("Experience Weight", 0, 100, recruiter_preferences["experience_weight"])
education_weight = st.sidebar.slider("Education Weight", 0, 100, recruiter_preferences["education_weight"])
skills_weight = st.sidebar.slider("Skills Weight", 0, 100, recruiter_preferences["skills_weight"])
certifications_weight = st.sidebar.slider("Certifications Weight", 0, 100, recruiter_preferences["certifications_weight"])

custom_skills = st.sidebar.text_area("Custom Skills (comma-separated)", placeholder="e.g. react, flask, tensorflow")
custom_certifications = st.sidebar.text_area("Custom Certifications (comma-separated)", placeholder="e.g. OCI, CEH")

# Save preferences
if st.sidebar.button("Save Preferences"):
    recruiter_preferences = {
        "experience_weight": experience_weight,
        "education_weight": education_weight,
        "skills_weight": skills_weight,
        "certifications_weight": certifications_weight
    }
    with open(preferences_file, "w") as f:
        json.dump(recruiter_preferences, f)
    st.sidebar.success("Preferences saved!")

# Combine custom skills and default + custom certifications
custom_skill_list = [s.strip().lower() for s in custom_skills.split(",") if s.strip()]
custom_cert_list = [c.strip().lower() for c in custom_certifications.split(",") if c.strip()]
relevant_skills = custom_skill_list
certifications_list = list(set(DEFAULT_CERTIFICATIONS + custom_cert_list))

# Main logic
if uploaded_files:
    candidates = []

    for file in uploaded_files:
        file_path = os.path.join(RESUME_DIR, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())

        text = extract_text_from_file(file)
        if not text or len(text.strip()) < 50:
            text = extract_text_with_ocr(file_path)

        if not text or len(text.strip()) == 0:
            st.warning(f"⚠️ Could not extract text from: {file.name}")
            continue

        experience = extract_experience(text)
        education = extract_education(text)
        education_numeric = education_map.get(education, 0)
        skills = extract_skills(text, relevant_skills)
        cert_count = extract_certifications(text, certifications_list)

        features = [experience, education_numeric, len(skills), cert_count]
        model_score = model.predict([features])[0]

        weighted_score = (
            experience * experience_weight +
            education_numeric * education_weight +
            len(skills) * skills_weight +
            cert_count * certifications_weight
        ) / 100

        candidates.append({
            'filename': file.name,
            'score': weighted_score,
            'experience': experience,
            'skills': skills,
            'education': education,
            'certifications': cert_count
        })

    candidates.sort(key=lambda x: x['score'], reverse=True)
    st.write("### 🏆 Top Ranked Candidates")

    for candidate in candidates:
        st.write(f"**Resume**: {candidate['filename']}")
        st.write(f"**Predicted Score**: {candidate['score']:.2f}")
        st.write(f"**Experience**: {candidate['experience']} years")
        st.write(f"**Skills**: {', '.join(candidate['skills']) if candidate['skills'] else 'None found'}")
        st.write(f"**Education**: {candidate['education']}")
        st.write(f"**Certifications Count**: {candidate['certifications']}")

        with open(os.path.join(RESUME_DIR, candidate['filename']), "rb") as file:
            st.download_button(
                label="📥 Download Resume",
                data=file,
                file_name=candidate['filename'],
                mime="application/octet-stream"
            )
        st.write("---")

    # DataFrame and Visualizations
    df = pd.DataFrame(candidates)

    st.write("### 📊 Candidate Ranking")
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    sns.barplot(x='filename', y='score', data=df, palette="Blues_d", ax=ax1)
    ax1.set_ylabel("Score")
    ax1.set_title("Ranking of Candidates")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig1)

    st.write("### 📈 Score Distribution")
    fig2, ax2 = plt.subplots()
    sns.histplot(df['score'], bins=10, kde=True, color='skyblue', ax=ax2)
    ax2.set_xlabel("Score")
    ax2.set_title("Distribution of Candidate Scores")
    st.pyplot(fig2)

    st.write("### 🧮 Feature Contribution for Top Candidate")
    top = df.iloc[0]
    labels = ['Experience', 'Education', 'Skills', 'Certifications']
    contributions = [
        top['experience'] * experience_weight,
        education_map.get(top['education'], 0) * education_weight,
        len(top['skills']) * skills_weight,
        top['certifications'] * certifications_weight
    ]
    fig3, ax3 = plt.subplots()
    ax3.pie(contributions, labels=labels, autopct='%1.1f%%', startangle=140)
    ax3.axis('equal')
    st.pyplot(fig3)

    # Download limit input
    max_to_download = st.number_input(
        "🔢 Number of Top Candidates to Include in Download",
        min_value=1,
        max_value=len(candidates),
        value=min(5, len(candidates)),
        step=1
    )

    # Create HTML download links
    def create_download_link(file_path, filename):
        with open(file_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">Download</a>'

    # Use only top N candidates for download
    top_n_candidates = candidates[:max_to_download]
    for candidate in top_n_candidates:
        resume_path = os.path.join(RESUME_DIR, candidate['filename'])
        candidate['download_link'] = create_download_link(resume_path, candidate['filename'])

    df_download = pd.DataFrame(top_n_candidates)
    html_table = df_download.to_html(escape=False, index=False)

    with open("top_ranked_candidates.html", "w", encoding='utf-8') as f:
        f.write(html_table)

    st.download_button(
        label="📥 Download Top Ranked Candidates (HTML with Download Links)",
        data=html_table,
        file_name="top_ranked_candidates.html",
        mime="text/html"
    )
