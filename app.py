
import streamlit as st
import re
import PyPDF2
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")


# -----------------------------
# Extract PDF Text
# -----------------------------
def extract_text(pdf_file):

    text = ""

    reader = PyPDF2.PdfReader(pdf_file)

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# -----------------------------
# Extract Name
def extract_name(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # First, look for a line containing Name:
    for line in lines:
        if re.match(r"^(name|full name)\s*[:\-]", line, re.I):
            name = re.sub(r"^(name|full name)\s*[:\-]\s*", "", line, flags=re.I).strip()
            if name:
                return name

    # Words that should not be considered as a person's name
    ignore_words = {
        "resume", "curriculum vitae", "cv", "coursera",
        "objective", "summary", "education", "skills",
        "technical skills", "experience", "projects",
        "certifications", "contact", "profile"
    }

    # Check the first few lines of the resume
    for line in lines[:10]:
        clean_line = re.sub(r"[^A-Za-z .'-]", "", line).strip()

        if not clean_line:
            continue

        if clean_line.lower() in ignore_words:
            continue

        # Don't use email, phone numbers or headings
        if "@" in line or re.search(r"\d{5,}", line):
            continue

        words = clean_line.split()

        # A person's name usually has 2–5 words
        if 2 <= len(words) <= 5:
            return clean_line

    return "Not Found"

# -----------------------------
# Extract Email
# -------------------

# -----------------------------
# Extract Email
# -----------------------------
def extract_email(text):

    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'

    emails = re.findall(pattern, text)

    if emails:
        return emails[0]

    return "Not Found"


# -----------------------------
# Extract Phone
# -----------------------------
def extract_phone(text):

    pattern = r'(?:\+91[\s-]?)?[6-9]\d{9}'

    phones = re.findall(pattern, text)

    if phones:
        return phones[0]

    return "Not Found"


# -----------------------------
# Extract Skills
# -----------------------------
def extract_skills(text):

    skills_list = [
        "Python",
        "C",
        "Java",
        "HTML",
        "CSS",
        "JavaScript",
        "SQL",
        "MySQL",
        "Machine Learning",
        "Artificial Intelligence",
        "NLP",
        "OpenCV",
        "Pandas",
        "NumPy",
        "TensorFlow",
        "Git",
        "GitHub"
    ]

    found_skills = []

    text_lower = text.lower()

    for skill in skills_list:

        if skill.lower() in text_lower:
            found_skills.append(skill)

    return sorted(set(found_skills))


# -----------------------------
# Resume Score
# -----------------------------
def calculate_score(text, skills):

    score = 0

    text_lower = text.lower()

    sections = [
        ["skills", "technical skills"],
        ["education", "qualification"],
        ["projects", "project"],
        ["experience", "internship"],
        ["certifications", "certificates"],
        ["objective", "summary"]
    ]

    for section in sections:

        if any(word in text_lower for word in section):
            score += 10

    if len(skills) >= 3:
        score += 10

    if extract_email(text) != "Not Found":
        score += 5

    if extract_phone(text) != "Not Found":
        score += 5

    return min(score, 100)


# -----------------------------
# Streamlit Interface
# -----------------------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume Analyzer")

st.write(
    "Upload your resume and automatically extract "
    "important information using Python, NLP and Regex."
)


# Upload PDF
uploaded_file = st.file_uploader(
    "Upload your Resume",
    type=["pdf"]
)


if uploaded_file:

    st.success("Resume uploaded successfully! ✅")

    # Extract text
    resume_text = extract_text(uploaded_file)

    if not resume_text.strip():

        st.error("Unable to extract text from this PDF.")

    else:

        # Extract details
        name = extract_name(resume_text)
        email = extract_email(resume_text)
        phone = extract_phone(resume_text)
        skills = extract_skills(resume_text)

        score = calculate_score(
            resume_text,
            skills
        )


        # Candidate Information
        st.header("👤 Candidate Information")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Name")
            st.write(name)

        with col2:
            st.subheader("Email")
            st.write(email)

        with col3:
            st.subheader("Phone")
            st.write(phone)


        # Skills
        st.header("💻 Technical Skills")

        if skills:

            for skill in skills:
                st.write("✅", skill)

        else:

            st.write("No skills detected.")


        # Resume Score
        st.header("📊 Resume Score")

        st.progress(score / 100)

        st.write(
            f"**Score: {score}/100**"
        )


        # Resume Text
        st.header("📄 Extracted Resume")

        with st.expander("View extracted text"):

            st.text(resume_text)


        # Download
        st.download_button(
            "Download Extracted Text",
            resume_text,
            file_name="extracted_resume.txt",
            mime="text/plain"
        )
