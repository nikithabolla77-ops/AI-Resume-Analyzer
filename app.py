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

    # Normalize spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize excessive new lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ============================================================
# VALIDATE NAME
# ============================================================

def is_valid_name(name):

    if not name:
        return False

    name = name.strip()

    # Length check
    if len(name) < 3 or len(name) > 60:
        return False

    # Email should not be a name
    if "@" in name:
        return False

    # Numbers should not be present
    if re.search(r"\d", name):
        return False

    # Must contain letters
    if not re.search(r"[A-Za-z]", name):
        return False

    # Remove unwanted punctuation
    cleaned = re.sub(r"[^A-Za-z .'-]", "", name)

    if cleaned != name:
        return False

    # Maximum 5 words
    words = name.split()

    if len(words) > 5:
        return False

    # Common resume words
    invalid_words = {
        "resume",
        "curriculum vitae",
        "cv",
        "career",
        "career objective",
        "objective",
        "profile",
        "summary",
        "career summary",
        "education",
        "educational qualification",
        "qualification",
        "technical skills",
        "professional skills",
        "skills",
        "work experience",
        "experience",
        "projects",
        "certifications",
        "artificial intelligence",
        "machine learning",
        "bachelor technology",
        "bachelor of technology",
        "linkedin profile",
        "github profile",
        "description",
        "email",
        "phone",
        "mobile",
        "address"
    }

    if name.lower() in invalid_words:
        return False

    # Individual words should look like names
    for word in words:
        if len(word) < 1:
            return False

    return True


# ============================================================
# EXTRACT NAME
# ============================================================

def extract_name(text):

    if not text:
        return "Not Found"

    # --------------------------------------------------------
    # Create cleaned lines
    # --------------------------------------------------------

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Remove excessive spaces
        line = re.sub(r"\s+", " ", line)

        lines.append(line)

    # --------------------------------------------------------
    # METHOD 1: Explicit Name field
    # Examples:
    # Name: Bolla Sai Nikhitha
    # Name - Bolla Sai Nikhitha
    # Name Bolla Sai Nikhitha
    # --------------------------------------------------------

    name_patterns = [
        r"(?i)^\s*name\s*[:\-]\s*([A-Za-z][

       
