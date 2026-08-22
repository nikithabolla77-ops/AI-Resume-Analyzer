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
        st.error(f"Error reading PDF: {e}")
        return ""


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    if not text:
        return ""

    # Remove null characters
    text = text.replace("\x00", "")

    # Normalize different dash characters
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n", text)

    return text.strip()


# ============================================================
# VALID NAME WORDS
# ============================================================

INVALID_NAME_WORDS = {
    "resume",
    "cv",
    "curriculum vitae",
    "career",
    "career objective",
    "objective",
    "profile",
    "summary",
    "professional summary",
    "description",
    "about",
    "education",
    "educational",
    "qualification",
    "educational qualification",
    "technical skills",
    "skills",
    "skill",
    "projects",
    "project",
    "experience",
    "work experience",
    "internship",
    "internships",
    "certifications",
    "certification",
    "contact",
    "contact information",
    "personal information",
    "linkedin",
    "linkedin profile",
    "github",
    "github profile",
    "email",
    "phone",
    "mobile",
    "address",
    "bachelor",
    "bachelor of technology",
    "technology",
    "artificial intelligence",
    "machine learning",
    "computer science",
    "engineering",
    "python",
    "java",
    "html",
    "css",
    "sql",
    "c",
    "javascript",
    "data science",
    "data analysis"
}


# ============================================================
# CHECK WHETHER TEXT LOOKS LIKE A REAL NAME
# ============================================================

def is_valid_name(name):

    if not name:
        return False

    name = name.strip()

    # Remove extra spaces
    name = re.sub(r"\s+", " ", name)

    # Length check
    if len(name) < 3 or len(name) > 60:
        return False

    lower_name = name.lower()

    # Exact invalid words
    if lower_name in INVALID_NAME_WORDS:
        return False

    # Reject if contains invalid heading words
    for word in INVALID_NAME_WORDS:
        if lower_name == word:
            return False

    # Reject email
    if "@" in name:
        return False

    # Reject URLs
    if "http" in lower_name or "www." in lower_name:
        return False

    if "linkedin" in lower_name or "github" in lower_name:
        return False

    # Reject numbers
    if re.search(r"\d", name):
        return False

    # Name should contain mostly alphabetic characters
    if not re.fullmatch(r"[A-Za-z][A-Za-z .'-]*", name):
        return False

    words = name.split()

    # Usually 1-5 words
    if len(words) > 5:
        return False

    # Reject if any word is a common heading
    for word in words:
        if word.lower() in {
            "resume",
            "career",
            "objective",
            "description",
            "education",
            "qualification",
            "skills",
            "projects",
            "experience",
            "certifications",
            "contact",
            "linkedin",
            "github",
            "profile",
            "summary"
        }:
            return False

    return True


# ============================================================
# EXTRACT NAME
# ============================================================

def extract_name(text, filename=""):

    if not text:
        return "Not Found"

    lines = text.splitlines()

    # --------------------------------------------------------
    # METHOD 1: Look for explicit "Name:"
    # --------------------------------------------------------

    name_patterns = [
        r"(?i)^\s*name\s*[:\-]\s*([A-Za-z][A-Za-z .'-]{2,60})\s*$",
        r"(?i)^\s*full\s*name\s*[:\-]\s*([A-Za-z][A-Za-z .'-]{2,60})\s*$"
    ]

    for line in lines:

        line = line.strip()

        for pattern in name_patterns:

            match = re.search(pattern, line)

            if match:

                name = match.group(1).strip()

                if is_valid_name(name):
                    return name


    # --------------------------------------------------------
    # METHOD 2: Find name near email
    # --------------------------------------------------------

    email_index = None

    for i, line in enumerate(lines):

        if re.search(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            line
        ):
            email_index = i
            break

    if email_index is not None:

        # Check lines before email
        start = max(0, email_index - 5)

        for i in range(email_index - 1, start - 1, -1):

            candidate = lines[i].strip()

            if not candidate:
                continue

            # Remove bullets
            candidate = re.sub(r"^[•●▪►\-\*\|]+\s*", "", candidate)

            candidate = re.sub(r"\s+", " ", candidate)

            if is_valid_name(candidate):
                return candidate


    # --------------------------------------------------------
    # METHOD 3: Check first 30 meaningful lines
    # --------------------------------------------------------

    cleaned_lines = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Remove bullets
        line = re.sub(r"^[•●▪►\-\*\|]+\s*", "", line)

        # Remove repeated spaces
        line = re.sub(r"\s+", " ", line)

        cleaned_lines.append(line)


    # Words that should never be treated as names
    ignored = {
        "resume",
        "cv",
        "curriculum vitae",
        "linkedin",
        "github",
        "career",
        "career objective",
        "objective",
        "profile",
        "summary",
        "description",
        "education",
        "educational",
        "qualification",
        "skills",
        "technical skills",
        "projects",
        "experience",
        "work experience",
        "certifications",
        "contact",
        "email",
        "phone",
        "mobile",
        "address",
        "bachelor",
        "technology",
        "artificial intelligence",
        "machine learning",
        "engineering"
    }


    for line in cleaned_lines[:30]:

        lower_line = line.lower()

        # Skip headings
        if lower_line in ignored:
            continue

        # Skip lines containing email
        if re.search(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            line
        ):
            continue

        # Skip phone numbers
        if re.search(r"\b\d{10}\b", line):
            continue

        # Skip URLs
        if re.search(r"(linkedin|github|http|www\.)", lower_line):
            continue

        # Skip lines with too many special characters
        if re.search(r"[@:/\\]", line):
            continue

        # Candidate must contain letters
        if not re.search(r"[A-Za-z]", line):
            continue

        # Candidate should not be too long
        if len(line) > 60:
            continue

        # Candidate should not look like a sentence
        words = line.split()

        if len(words) > 5:
            continue

        if is_valid_name(line):
            return line


    # --------------------------------------------------------
    # METHOD 4: Combine first few words
    # Useful when PDF extracts each name word separately
    # --------------------------------------------------------

    candidate_words = []

    for line in cleaned_lines[:20]:

        lower_line = line.lower()

        if lower_line in ignored:
            continue

        if "@" in line:
            continue

        if re.search(r"\d", line):
            continue

       
