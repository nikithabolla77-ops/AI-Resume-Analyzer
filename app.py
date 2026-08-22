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
    text = text.replace("\x00", " ")

    # Replace multiple spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize line breaks
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


# ============================================================
# VALIDATE NAME
# ============================================================

def is_valid_name(name):

    if not name:
        return False

    name = name.strip()

    # Remove unwanted characters
    name = re.sub(r"\s+", " ", name)

    # Length check
    if len(name) < 3 or len(name) > 60:
        return False

    # Must contain letters
    if not re.search(r"[A-Za-z]", name):
        return False

    # Don't allow email
    if "@" in name:
        return False

    # Don't allow numbers
    if re.search(r"\d", name):
        return False

    # Don't allow URLs
    lower_name = name.lower()

    if "linkedin" in lower_name:
        return False

    if "github" in lower_name:
        return False

    if "http" in lower_name:
        return False

    # Common resume words that are NOT names
    invalid_names = {
        "resume",
        "curriculum vitae",
        "career objective",
        "career",
        "objective",
        "profile",
        "summary",
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
        "contact",
        "email",
        "phone",
        "mobile",
        "address",
        "skills",
        "qualification",
        "linkedin profile",
        "github profile",
        "declaration",
        "achievements"
    }

    if lower_name in invalid_names:
        return False

    # Maximum 5 words
    words = name.split()

    if len(words) > 5:
        return False

    return True


# ============================================================
# EXTRACT NAME
# ============================================================

def extract_name(text, filename=""):

    if not text:
        return "Not
