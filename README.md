# Automated Resume Screening System (ML-based)

## Overview
The Automated Resume Screening System is a machine learning–based web application that helps recruiters automatically parse, analyze, and rank resumes.  
It extracts candidate details such as experience, skills, education, and certifications, applies recruiter-defined weightages, and generates a ranked list of candidates with visual analytics.

The project also supports image-based resumes (OCR) and allows recruiters to download ranked candidates with clickable resume links in HTML format.

---

## Features
- Upload resumes in PDF, DOCX, JPG, PNG formats  
- OCR support for scanned/image resumes using Tesseract  
- Customizable recruiter preferences (weightages for experience, education, skills, certifications)  
- ML model (Scikit-learn) trained on mock resume data  
- Analytics dashboard:
  - Candidate ranking (bar chart)  
  - Score distribution (histogram)  
  - Feature contribution (pie chart)  
- Download Top N candidates with clickable resume links in HTML format  

---

## Tech Stack
- **Frontend**: Streamlit  
- **Backend**: Python  
- **ML Library**: Scikit-learn  
- **Data Processing**: Pandas, NumPy  
- **Visualization**: Matplotlib, Seaborn  
- **Resume Parsing**: docx2txt, PyPDF2 / pdfminer.six, Tesseract OCR, pdf2image, Pillow  
- **Fuzzy Matching**: rapidfuzz  

---

## Project Structure
```

Automated\_Resume\_Screening\_System/
│── app.py                     # Streamlit web app
│── resume\_parser.py            # Resume parsing functions (skills, education, experience, OCR)
│── model.pkl                   # Trained ML model
│── mock\_resume\_data.csv        # Mock training dataset
│── top\_ranked\_candidates.html  # Downloadable ranked candidates (generated)
│── requirements.txt            # Project dependencies
│── README.md                   # Project documentation
│── resumes/                    # Uploaded resumes folder

````

---

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/mayuri-jagtap/Automated_Resume_Screening_System.git
cd Automated_Resume_Screening_System
````

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
streamlit run app.py
```

---

## Usage

1. Open the Streamlit app in your browser
2. Upload resumes (PDF/DOCX/JPG/PNG)
3. Set recruiter preferences (weightages for skills, education, etc.)
4. View ranked candidates with analytics
5. Download Top N candidates with clickable resume links

---

## Example Recruiter Preferences

* Experience weight: 40%
* Skills weight: 30%
* Education weight: 20%
* Certifications weight: 10%

---

## Future Enhancements

* Support for real-time job description matching
* Advanced NLP-based skill extraction
* Cloud deployment (AWS/GCP)
* Integration with ATS (Applicant Tracking Systems)

---

## Contributors

* **Mayuri Jagtap** – MIT ADT University

---

## Requirements

```
streamlit
pandas
numpy
scikit-learn
matplotlib
seaborn
pillow
pdf2image
pytesseract
python-docx
PyPDF2
pdfminer.six
rapidfuzz
```




