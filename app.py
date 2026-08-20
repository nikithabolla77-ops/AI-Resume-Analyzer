import streamlit as st
import re
from PyPDF2 import PdfReader


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)


# =========================================================
# EXTRACT TEXT FROM PDF
# =========================================================

def extract_text(pdf_file):
    try:
        reader = PdfReader(pdf_file)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""


# =========================================================
# CLEAN TEXT
# =========================================================

def clean_text(text):
    # Replace multiple spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Replace multiple blank lines
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


# =========================================================
# EXTRACT NAME
# =========================================================

def extract_name(text):

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    # -----------------------------------------------------
    # Method 1:
    # Look for name after common name headings
    # -----------------------------------------------------

    name_headers = [
        "name",
        "full name",
        "candidate name"
    ]

    for i, line in enumerate(lines):

        clean_line = line.lower().replace(":", "").strip()

        if clean_line in name_headers:

            if i + 1 < len(lines):

                possible_name = lines[i + 1].strip()

                if is_valid_name(possible_name):
                    return possible_name

    # -----------------------------------------------------
    # Method 2:
    # Check first 20 lines
    # -----------------------------------------------------

    ignored_words = [
        "resume",
        "curriculum vitae",
        "career objective",
        "objective",
        "education",
        "educational qualification",
        "qualification",
        "skills",
        "technical skills",
        "experience",
        "work experience",
        "projects",
        "project",
        "certifications",
        "certificates",
        "linkedin",
        "github",
        "email",
        "phone",
        "contact",
        "profile",
        "summary"
    ]

    for line in lines[:20]:

        line_lower = line.lower().strip()

        # Ignore headings
        if line_lower in ignored_words:
            continue

        # Ignore email
        if "@" in line:
            continue

        # Ignore URLs
        if "http" in line_lower:
            continue

        # Ignore LinkedIn/GitHub
        if "linkedin" in line_lower or "github" in line_lower:
            continue

        # Ignore phone numbers
        if re.search(r"\d{7,}", line):
            continue

        # Ignore lines containing too many symbols
        if len(re.findall(r"[^a-zA-Z .'-]", line)) > 2:
            continue

        # Check whether it looks like a person's name
        if is_valid_name(line):
            return line

    # -----------------------------------------------------
    # Method 3:
    # Search for common name patterns
    # -----------------------------------------------------

    name_patterns = [
        r"(?:Name|Full Name|Candidate Name)\s*[:\-]\s*([A-Za-z .'-]{3,50})",
        r"(?:I am|I'm)\s+([A-Za-z .'-]{3,50})"
    ]

    for pattern in name_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            name = match.group(1).strip()

            if is_valid_name(name):
                return name

    return "Not Found"


# =========================================================
# VALIDATE NAME
# =========================================================

def is_valid_name(name):

    name = name.strip()

    if not name:
        return False

    # Name should not be too long
    if len(name) > 50:
        return False

    # Split words
    words = name.split()

    # Normally a name has 2-5 words
    if len(words) < 2 or len(words) > 5:
        return False

    # Reject common resume headings
    blocked_words = [
        "resume",
        "curriculum",
        "objective",
        "career",
        "education",
        "qualification",
        "skills",
        "technical",
        "experience",
        "projects",
        "certifications",
        "linkedin",
        "github",
        "email",
        "phone",
        "contact"
    ]

    name_lower = name.lower()

    for word in blocked_words:
        if word in name_lower:
            return False

    # Every word should contain letters
    for word in words:

        cleaned_word = word.replace(".", "").replace("-", "")

        if not cleaned_word.isalpha():
            return False

    return True


# =========================================================
# EXTRACT EMAIL
# =========================================================

def extract_email(text):

    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    emails = re.findall(pattern, text)

    if emails:
        return emails[0]

    return "Not Found"


# =========================================================
# EXTRACT PHONE NUMBER
# =========================================================

def extract_phone(text):

    patterns = [

        # Indian mobile number
        r"(?:\+91[\s-]?)?[6-9]\d{9}",

        # Phone with spaces
        r"(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}",

        # Phone with brackets
        r"\(?\d{3,5}\)?[\s-]?\d{3,5}[\s-]?\d{4}"
    ]

    for pattern in patterns:

        phones = re.findall(pattern, text)

        if phones:

            phone = phones[0]

            # Remove unnecessary spaces
            phone = re.sub(r"\s+", " ", phone).strip()

            return phone

    return "Not Found"


# =========================================================
# EXTRACT TECHNICAL SKILLS
# =========================================================

def extract_skills(text):

    skills_list = [

        "Python",
        "C",
        "C++",
        "Java",
        "HTML",
        "CSS",
        "JavaScript",
        "SQL",
        "MySQL",
        "Oracle",
        "Machine Learning",
        "Artificial Intelligence",
        "AI",
        "NLP",
        "OpenCV",
        "Pandas",
        "NumPy",
        "TensorFlow",
        "Keras",
        "Git",
        "GitHub",
        "React",
        "Django",
        "Flask",
        "Streamlit",
        "Power BI",
        "Tableau",
        "Excel",
        "AWS",
        "Azure"
    ]

    found_skills = []

    text_lower = text.lower()

    for skill in skills_list:

        skill_lower = skill.lower()

        # Use word boundary for short skills
        if skill_lower in text_lower:

            if skill not in found_skills:
                found_skills.append(skill)

    return sorted(found_skills)


# =========================================================
# CALCULATE RESUME SCORE
# =========================================================

def calculate_score(text, skills):

    score = 0

    text_lower = text.lower()

    # -----------------------------------------------------
    # Resume sections
    # -----------------------------------------------------

    sections = [

        ["skills", "technical skills"],

        ["education", "qualification"],

        ["projects", "project"],

        ["experience", "internship", "work experience"],

        ["certifications", "certificates"],

        ["objective", "summary", "career objective"],

        ["contact", "email", "phone"]
    ]

    for section in sections:

        if any(word in text_lower for word in section):

            score += 10

    # -----------------------------------------------------
    # Skills
    # -----------------------------------------------------

    if len(skills) >= 3:
        score += 10

    elif len(skills) >= 1:
        score += 5

    # -----------------------------------------------------
    # Email
    # -----------------------------------------------------

    if extract_email(text) != "Not Found":
        score += 5

    # -----------------------------------------------------
    # Phone
    # -----------------------------------------------------

    if extract_phone(text) != "Not Found":
        score += 5

    # Maximum score
    return min(score, 100)


# =========================================================
# STREAMLIT INTERFACE
# =========================================================

st.title("📄 AI Resume Analyzer")

st.write(
    "Upload your resume and automatically extract important "
    "information using Python, NLP and Regex."
)


# =========================================================
# UPLOAD PDF
# =========================================================

uploaded_file = st.file_uploader(
    "Upload your Resume",
    type=["pdf"]
)


# =========================================================
# PROCESS RESUME
# =========================================================

if uploaded_file:

    st.success("Resume uploaded successfully! ✅")

    # -----------------------------------------------------
    # Extract text
    # -----------------------------------------------------

    resume_text = extract_text(uploaded_file)

    resume_text = clean_text(resume_text)

    # -----------------------------------------------------
    # Check extracted text
    # -----------------------------------------------------

    if not resume_text:

        st.error(
            "Unable to extract text from this PDF. "
            "Please upload a text-based PDF."
        )

    else:

        # -------------------------------------------------
        # Extract candidate details
        # -------------------------------------------------

        name = extract_name(resume_text)

        email = extract_email(resume_text)

        phone = extract_phone(resume_text)

        skills = extract_skills(resume_text)

        score = calculate_score(
            resume_text,
            skills
        )


        # =================================================
        # CANDIDATE INFORMATION
        # =================================================

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


        # =================================================
        # TECHNICAL SKILLS
        # =================================================

        st.header("💻 Technical Skills")

        if skills:

            for skill in skills:

                st.write(
                    f"✅ {skill}"
                )

        else:

            st.write(
                "No technical skills detected."
            )


        # =================================================
        # RESUME SCORE
        # =================================================

        st.header("📊 Resume Score")

        st.progress(
            score / 100
        )

        st.write(
            f"Score: {score}/100"
        )


        # =================================================
        # EXTRACTED RESUME
        # =================================================

        st.header("📄 Extracted Resume")

        with st.expander(
            "View extracted text"
        ):

            st.text(
                resume_text
            )


        # =================================================
        # DOWNLOAD EXTRACTED TEXT
        # =================================================

        st.download_button(

            label="Download Extracted Text",

            data=resume_text,

            file_name="extracted_resume.txt",

            mime="text/plain"
        )
