import streamlit as st
import re
from pypdf import PdfReader


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)


# ============================================================
# EXTRACT TEXT FROM PDF
# ============================================================

def extract_text_from_pdf(uploaded_file):

    try:
        reader = PdfReader(uploaded_file)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    except Exception as e:
        st.error("Error reading PDF: " + str(e))
        return ""


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    text = text.replace("\x00", " ")

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n+", "\n", text)

    return text.strip()


# ============================================================
# VALIDATE NAME
# ============================================================

def is_valid_name(name):

    if not name:
        return False

    name = name.strip()

    if len(name) < 3 or len(name) > 60:
        return False

    if "@" in name:
        return False

    if re.search(r"\d", name):
        return False

    if not re.search(r"[A-Za-z]", name):
        return False

    words = name.split()

    if len(words) > 5:
        return False

    invalid_words = [
        "resume",
        "curriculum vitae",
        "career objective",
        "objective",
        "profile",
        "summary",
        "career",
        "education",
        "educational qualification",
        "technical skills",
        "professional skills",
        "skills",
        "projects",
        "experience",
        "work experience",
        "certifications",
        "contact",
        "email",
        "phone",
        "mobile",
        "address",
        "linkedin",
        "github",
        "artificial intelligence",
        "machine learning",
        "bachelor of technology",
        "bachelor technology"
    ]

    if name.lower() in invalid_words:
        return False

    return True


# ============================================================
# EXTRACT NAME
# ============================================================

def extract_name(text, filename):

    if not text:
        return "Not Found"

    text = text.replace("\r", "\n")

    lines = text.splitlines()

    cleaned_lines = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        line = re.sub(r"\s+", " ", line)

        cleaned_lines.append(line)


    # --------------------------------------------------------
    # METHOD 1: Name: XXXXX
    # --------------------------------------------------------

    for line in cleaned_lines[:40]:

        match = re.search(
            r"^(?:name|full name)\s*[:\-]?\s*(.+)$",
            line,
            re.IGNORECASE
        )

        if match:

            candidate = match.group(1).strip()

            candidate = re.split(
                r"\b(?:email|phone|mobile|linkedin|github|education|career|objective)\b",
                candidate,
                flags=re.IGNORECASE
            )[0].strip()

            if is_valid_name(candidate):
                return candidate


    # --------------------------------------------------------
    # METHOD 2: First lines of resume
    # --------------------------------------------------------

    ignored = [
        "resume",
        "curriculum vitae",
        "career",
        "career objective",
        "objective",
        "profile",
        "summary",
        "education",
        "educational qualification",
        "skills",
        "technical skills",
        "professional skills",
        "projects",
        "experience",
        "work experience",
        "certifications",
        "contact"
    ]

    for line in cleaned_lines[:20]:

        lower_line = line.lower()

        if lower_line in ignored:
            continue

        if "@" in line:
            continue

        if "linkedin" in lower_line:
            continue

        if "github" in lower_line:
            continue

        if "http" in lower_line:
            continue

        if re.search(r"\d", line):
            continue

        # Name should contain only letters, spaces, dots,
        # apostrophes or hyphens.
        if not re.fullmatch(
            r"[A-Za-z][A-Za-z .'-]{2,59}",
            line
        ):
            continue

        words = line.split()

        if 1 <= len(words) <= 4:

            if is_valid_name(line):
                return line


    # --------------------------------------------------------
    # METHOD 3: Find capitalized names
    # Example: Bolla Sai Nikhitha
    # --------------------------------------------------------

    pattern = (
        r"\b[A-Z][a-zA-Z'-]{1,20}"
        r"(?:\s+[A-Z][a-zA-Z'-]{1,20}){1,3}\b"
    )

    matches = re.findall(pattern, text)

    for match in matches:

        candidate = match.strip()

        if not is_valid_name(candidate):
            continue

        lower_candidate = candidate.lower()

        if "artificial intelligence" in lower_candidate:
            continue

        if "machine learning" in lower_candidate:
            continue

        if "bachelor technology" in lower_candidate:
            continue

        if "technical skills" in lower_candidate:
            continue

        return candidate


    # --------------------------------------------------------
    # METHOD 4: Use PDF filename
    # --------------------------------------------------------

    if filename:

        name_from_file = filename

        name_from_file = re.sub(
            r"\.pdf$",
            "",
            name_from_file,
            flags=re.IGNORECASE
        )

        name_from_file = re.sub(
            r"[_\-]+",
            " ",
            name_from_file
        )

        name_from_file = re.sub(
            r"\b(resume|cv)\b",
            "",
            name_from_file,
            flags=re.IGNORECASE
        )

        name_from_file = re.sub(
            r"\s+",
            " ",
            name_from_file
        ).strip()

        if is_valid_name(name_from_file):
            return name_from_file


    return "Not Found"


# ============================================================
# EXTRACT EMAIL
# ============================================================

def extract_email(text):

    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    emails = re.findall(pattern, text)

    if emails:
        return emails[0]

    return "Not Found"


# ============================================================
# EXTRACT PHONE
# ============================================================

def extract_phone(text):

    patterns = [
        r"\+91[\s\-]?[6-9]\d{4}[\s\-]?\d{5}",
        r"\b[6-9]\d{9}\b",
        r"\b[6-9]\d{3}[\s\-]\d{3}[\s\-]\d{3}\b"
    ]

    for pattern in patterns:

        phones = re.findall(pattern, text)

        if phones:
            return phones[0]

    return "Not Found"


# ============================================================
# EXTRACT SKILLS
# ============================================================

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
        "Deep Learning",
        "Artificial Intelligence",
        "NLP",
        "OpenCV",
        "Pandas",
        "NumPy",
        "TensorFlow",
        "PyTorch",
        "React",
        "Node.js",
        "Django",
        "Flask",
        "AWS",
        "Git",
        "GitHub",
        "Excel",
        "Power BI",
        "Communication",
        "Teamwork",
        "Problem Solving"
    ]

    found_skills = []

    text_lower = text.lower()

    for skill in skills_list:

        if skill.lower() in text_lower:
            found_skills.append(skill)

    if found_skills:
        return found_skills

    return ["Not Found"]


# ============================================================
# RESUME SCORE
# ============================================================

def calculate_score(text, skills):

    score = 0

    text_lower = text.lower()

    if "skills" in text_lower:
        score += 10

    if any(word in text_lower for word in [
        "education",
        "qualification",
        "bachelor",
        "degree"
    ]):
        score += 10

    if "project" in text_lower:
        score += 10

    if any(word in text_lower for word in [
        "experience",
        "internship"
    ]):
        score += 10

    if "certification" in text_lower:
        score += 10

    if any(word in text_lower for word in [
        "objective",
        "summary",
        "profile"
    ]):
        score += 10

    if skills != ["Not Found"] and len(skills) >= 3:
        score += 10

    if extract_email(text) != "Not Found":
        score += 5

    if extract_phone(text) != "Not Found":
        score += 5

    if extract_name(text, "") != "Not Found":
        score += 10

    return min(score, 100)


# ============================================================
# STREAMLIT UI
# ============================================================

st.title("📄 AI Resume Analyzer")

st.write(
    "Upload your resume and automatically extract "
    "important information using Python, NLP and Regex."
)


# ============================================================
# UPLOAD RESUME
# ============================================================

uploaded_file = st.file_uploader(
    "Upload your Resume",
    type=["pdf"]
)


# ============================================================
# PROCESS RESUME
# ============================================================

if uploaded_file:

    st.success("Resume uploaded successfully! ✅")

    resume_text = extract_text_from_pdf(uploaded_file)

    resume_text = clean_text(resume_text)

    if not resume_text:

        st.error(
            "Unable to extract text from this PDF. "
            "Please upload a text-based PDF."
        )

        st.stop()


    # Extract information

    name = extract_name(
        resume_text,
        uploaded_file.name
    )

    email = extract_email(resume_text)

    phone = extract_phone(resume_text)

    skills = extract_skills(resume_text)

    score = calculate_score(
        resume_text,
        skills
    )


    # ========================================================
    # CANDIDATE INFORMATION
    # ========================================================

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


    # ========================================================
    # SKILLS
    # ========================================================

    st.header("💻 Technical Skills")

    if skills != ["Not Found"]:

        for skill in skills:

            st.write("✅ " + skill)

    else:

        st.write("No skills detected.")


    # ========================================================
    # SCORE
    # ========================================================

    st.header("📊 Resume Score")

    st.progress(score / 100)

    st.write(
        f"**Score: {score}/100**"
    )


    # ========================================================
    # EXTRACTED TEXT
    # ========================================================

    st.header("📄 Extracted Resume")

    with st.expander("View extracted text"):

        st.text(resume_text)


    # ========================================================
    # DOWNLOAD
    # ========================================================

    st.download_button(
        "Download Extracted Text",
        resume_text,
        file_name="extracted_resume.txt",
        mime="text/plain"
    )
