import streamlit as st
import re
from pypdf import PdfReader


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
        st.error(f"Error reading PDF: {e}")
        return ""


# =========================================================
# CLEAN TEXT
# =========================================================

def clean_text(text):

    text = text.replace("\x00", " ")

    # Replace multiple spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Replace excessive new lines
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


# =========================================================
# EXTRACT NAME
# =========================================================

def extract_name(text):

    if not text:
        return "Not Found"

    # -----------------------------------------------------
    # METHOD 1: Look for "Name: ..."
    # -----------------------------------------------------

    name_patterns = [
        r"(?im)^\s*name\s*[:\-]\s*([A-Za-z][A-Za-z .'-]{2,60})\s*$",
        r"(?im)name\s*[:\-]\s*([A-Za-z][A-Za-z .'-]{2,60})"
    ]

    for pattern in name_patterns:

        match = re.search(pattern, text)

        if match:
            name = match.group(1).strip()

            # Remove unwanted trailing words
            name = re.split(
                r"\b(?:email|phone|mobile|linkedin|github|career|objective|education)\b",
                name,
                flags=re.IGNORECASE
            )[0].strip()

            if is_valid_name(name):
                return name

    # -----------------------------------------------------
    # METHOD 2: Check first few lines
    # -----------------------------------------------------

    lines = text.splitlines()

    cleaned_lines = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        line = re.sub(r"\s+", " ", line)

        cleaned_lines.append(line)

    # -----------------------------------------------------
    # Remove common resume headings
    # -----------------------------------------------------

    ignored_words = {
        "resume",
        "curriculum vitae",
        "cv",
        "career objective",
        "objective",
        "profile",
        "summary",
        "career",
        "education",
        "educational qualification",
        "skills",
        "technical skills",
        "projects",
        "experience",
        "certifications",
        "contact",
        "linkedin",
        "github",
        "email",
        "phone",
        "mobile",
        "address"
    }

    # -----------------------------------------------------
    # METHOD 3: First 15 lines
    # -----------------------------------------------------

    for line in cleaned_lines[:15]:

        lower_line = line.lower()

        if lower_line in ignored_words:
            continue

        # Skip lines containing email
        if re.search(r"\S+@\S+\.\S+", line):
            continue

        # Skip lines containing phone number
        if re.search(r"\+?\d[\d\s\-()]{8,}", line):
            continue

        # Skip URLs
        if re.search(r"(linkedin|github|http|www\.)", lower_line):
            continue

        # Name should mostly contain letters
        if not re.fullmatch(r"[A-Za-z .'-]+", line):
            continue

        # Remove excessive spaces
        name = re.sub(r"\s+", " ", line).strip()

        if is_valid_name(name):
            return name

    # -----------------------------------------------------
    # METHOD 4: Handle PDF extraction where each word
    # appears on a separate line
    # -----------------------------------------------------

    top_lines = cleaned_lines[:40]

    candidate_words = []

    for line in top_lines:

        # Skip email
        if "@" in line:
            continue

        # Skip URLs
        if "linkedin" in line.lower():
            continue

        if "github" in line.lower():
            continue

        # Skip headings
        if line.lower() in ignored_words:
            continue

        # Only consider single words
        if re.fullmatch(r"[A-Za-z]{2,20}", line):

            # Ignore common resume words
            if line.lower() not in {
                "bachelor",
                "technology",
                "artificial",
                "intelligence",
                "machine",
                "learning",
                "education",
                "qualification",
                "objective",
                "career",
                "skills",
                "projects",
                "experience",
                "certifications",
                "python",
                "java",
                "html",
                "css",
                "sql"
            }:

                candidate_words.append(line)

    # Try combinations of first 2-4 words
    for number in range(2, 5):

        if len(candidate_words) >= number:

            candidate = " ".join(candidate_words[:number])

            if is_valid_name(candidate):
                return candidate

    # -----------------------------------------------------
    # METHOD 5: Search anywhere for 2-4 capitalized words
    # -----------------------------------------------------

    pattern = r"\b[A-Z][a-z]{1,20}(?:\s+[A-Z][a-z]{1,20}){1,3}\b"

    matches = re.findall(pattern, text)

    for match in matches:

        if is_valid_name(match):
            return match.strip()

    return "Not Found"


# =========================================================
# VALIDATE NAME
# =========================================================

def is_valid_name(name):

    if not name:
        return False

    name = name.strip()

    # Length check
    if len(name) < 3 or len(name) > 60:
        return False

    # Must contain letters
    if not re.search(r"[A-Za-z]", name):
        return False

    # Do not allow email
    if "@" in name:
        return False

    # Do not allow numbers
    if re.search(r"\d", name):
        return False

    # Common words that are NOT names
    invalid_names = {
        "resume",
        "curriculum vitae",
        "career objective",
        "career",
        "objective",
        "education",
        "educational qualification",
        "technical skills",
        "professional skills",
        "work experience",
        "experience",
        "projects",
        "certifications",
        "artificial intelligence",
        "machine learning",
        "bachelor technology",
        "bachelor of technology",
        "linkedin profile",
        "github profile"
    }

    if name.lower() in invalid_names:
        return False

    # Too many words usually means it's a sentence
    words = name.split()

    if len(words) > 5:
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
# EXTRACT PHONE
# =========================================================

def extract_phone(text):

    patterns = [
        r"\+91[\s-]?[6-9]\d{9}",
        r"\b[6-9]\d{9}\b",
        r"\+?\d{1,3}[\s-]?\d{10}\b"
    ]

    for pattern in patterns:

        phones = re.findall(pattern, text)

        if phones:
            return phones[0]

    return "Not Found"


# =========================================================
# EXTRACT SKILLS
# =========================================================

# ==================================================
# EXTRACT SKILLS
# ==================================================

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
        "Deep Learning",
        "Data Analysis",
        "Data Science",
        "React",
        "Node.js",
        "Django",
        "Flask",
        "AWS",
        "Git",
        "Github",
        "Excel",
        "Power BI",
        "Communication",
        "Teamwork",
        "Problem Solving",
    ]

    found_skills = []

    for skill in skills_list:
        if skill.lower() in text.lower():
            found_skills.append(skill)

    return found_skills if found_skills else ["Not Found"]
