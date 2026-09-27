"""
Central configuration for the UGBS Student Welfare Assistant.

All secrets are read from environment variables (or a local .env file via
python-dotenv). Nothing is hard-coded, so this is safe to commit.
"""

import os
from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------------------------
# Database / Storage
# ---------------------------------------------------------------------------

DB_DIR = "./ugbs_welfare_db"

ANALYTICS_DB_PATH = "./welfare_analytics.sqlite3"


# ---------------------------------------------------------------------------
# Machine Learning / Embedding Configuration
# ---------------------------------------------------------------------------

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

TRAINING_DATA_PATH = "./data/welfare_training_examples.csv"

CLASSIFIER_MODEL_PATH = "./models/welfare_classifier.pt"

CLASSIFIER_LABELS_PATH = "./models/welfare_classifier_labels.json"


# ---------------------------------------------------------------------------
# LLM Configuration
# ---------------------------------------------------------------------------

# Available providers:
#   - ollama
#   - gemini
#   - anthropic
#
# Ollama is the default because it can run locally without an API key.

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()


# Ollama

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2"
)

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434"
)


# Google Gemini

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)


# Anthropic

ANTHROPIC_API_KEY = os.getenv(
    "ANTHROPIC_API_KEY",
    ""
)

ANTHROPIC_MODEL = os.getenv(
    "ANTHROPIC_MODEL",
    "claude-haiku-4-5-20251001"
)


# ---------------------------------------------------------------------------
# Student Language Understanding
# ---------------------------------------------------------------------------
#
# Students often do not use the formal names found in university documents.
#
# Examples:
#
#   "SFAO"
#   "fin aid"
#   "acct office"
#   "cashier"
#   "cash office"
#   "fee office"
#   "UG"
#   "SRC"
#
# These dictionaries provide a single source of truth that can be used by
# risk_classifier.py before classification and RAG retrieval.
#
# IMPORTANT:
# These expansions do NOT assert that two differently named offices are
# physically the same office. They simply provide related terminology for
# search/classification so the knowledge base can determine the correct answer.
# ---------------------------------------------------------------------------


ABBREVIATIONS = {

    # University
    "UG": "University of Ghana",

    "UGBS": "University of Ghana Business School",

    # Financial aid
    "SFAO": "Student Financial Aid Office",

    # Student governance
    "SRC": "Students Representative Council",

    "JCR": "Junior Common Room",

    "BHJCR": "Business House Junior Common Room",

    # Counselling / support
    "UGCCD": (
        "University of Ghana Counselling and Placement Centre"
    ),

    # Student portal / services
    "STS": (
        "student academic records registration and payment system"
    ),

    # Gender / advocacy
    "CEGENSA": (
        "Centre for Gender Studies and Advocacy"
    ),
}


# ---------------------------------------------------------------------------
# Common Student Terms
# ---------------------------------------------------------------------------
#
# These are informal terms students may use when referring to university
# services. The classifier can append the formal terminology to the original
# question so both the student's wording and the institutional wording remain
# available to the retriever.
# ---------------------------------------------------------------------------

STUDENT_TERMS = {

    # -----------------------------------------------------------------------
    # Fees / payments
    # -----------------------------------------------------------------------

    "school fees": (
        "academic fees fee payment"
    ),

    "fees": (
        "academic fees"
    ),

    "fee": (
        "academic fee"
    ),

    "fee payment": (
        "academic fees payment"
    ),

    "fees payment": (
        "academic fees payment"
    ),

    "payment office": (
        "fee payment accounts office"
    ),

    "fee office": (
        "fee payment accounts office"
    ),


    # -----------------------------------------------------------------------
    # Accounts / Cashier
    # -----------------------------------------------------------------------

    "acct": (
        "accounts"
    ),

    "acct office": (
        "accounts office Students Accounts Office"
    ),

    "account office": (
        "accounts office Students Accounts Office"
    ),

    "accounts office": (
        "Students Accounts Office"
    ),

    "student accounts": (
        "Students Accounts Office"
    ),

    "students accounts": (
        "Students Accounts Office"
    ),

    "cash office": (
        "cash office Students Accounts Office fee payment"
    ),

    "cashier": (
        "cash office Students Accounts Office fee payment"
    ),


    # -----------------------------------------------------------------------
    # Financial aid
    # -----------------------------------------------------------------------

    "fin aid": (
        "financial aid Student Financial Aid Office"
    ),

    "financial aid": (
        "financial aid Student Financial Aid Office"
    ),

    "scholarship": (
        "scholarship financial aid"
    ),

    "scholarships": (
        "scholarships financial aid"
    ),


    # -----------------------------------------------------------------------
    # Counselling
    # -----------------------------------------------------------------------

    "counsellor": (
        "counselling service counsellor"
    ),

    "counselor": (
        "counselling service counsellor"
    ),

    "counselling": (
        "counselling support"
    ),

    "counseling": (
        "counselling support"
    ),


    # -----------------------------------------------------------------------
    # Academic language
    # -----------------------------------------------------------------------

    "results": (
        "academic results academic records"
    ),

    "academic results": (
        "academic records results"
    ),

    "resit": (
        "resit examination academic assessment"
    ),

    "resits": (
        "resit examinations academic assessment"
    ),

    "course registration": (
        "academic course registration STS"
    ),

    "register courses": (
        "academic course registration STS"
    ),


    # -----------------------------------------------------------------------
    # Governance
    # -----------------------------------------------------------------------

    "student election": (
        "student elections student governance SRC JCR"
    ),

    "student elections": (
        "student elections student governance SRC JCR"
    ),

    "president": (
        "student leadership election president"
    ),

    "jcr president": (
        "JCR president student leadership election"
    ),

    "src president": (
        "SRC president student leadership election"
    ),


    # -----------------------------------------------------------------------
    # Business School terminology
    # -----------------------------------------------------------------------

    "business school": (
        "University of Ghana Business School UGBS"
    ),

    "business house": (
        "Business House UGBS BHJCR"
    ),
}


# ---------------------------------------------------------------------------
# Knowledge Base Files
# ---------------------------------------------------------------------------

MARKDOWN_FILES = [

    # Careers / counselling
    "careers_and_counselling_faq.md",

    # Financial aid
    "sfao_financial_aid.md",

    # Academic
    "ugbs_academic_policies.md",

    # Counselling
    "ugccd counselling policy.md",

    # Student governance
    "bhjcr_constitution.md",

    "ug_statutes_governance.md",

    "ug_src_electoral_ci24.md",

    # Academic affairs
    "ug_academic_affairs_qna.md",

    # Discipline / governance
    "ug_discipline_governance.md",

    # Accommodation
    "accommodation.md",

    # Sexual harassment / GBV
    "sexual_harassment_support.md",

    # Programmes / options
    "ugbs_programmes_and_options.md",

    # -----------------------------------------------------------------------
    # Offices / contacts / locations
    # -----------------------------------------------------------------------

    "ugbs_offices_and_contacts.md",

    # -----------------------------------------------------------------------
    # STS
    # -----------------------------------------------------------------------

    "sts_portal_and_payments_faqs.md",

    "sts_academic_records_and_regulations_faqs.md",

    "sts_graduation_and_certificates_faqs.md",
]


# ---------------------------------------------------------------------------
# Classification Categories
# ---------------------------------------------------------------------------

CATEGORIES = [

    "Financial Distress",

    "Academic Distress",

    "Accommodation",

    "Mental Health / Counselling",

    "Career Guidance",

    "Student Governance / JCR",

    "Sexual Harassment / GBV",

    "Out of Scope",
]


# ---------------------------------------------------------------------------
# Nationality-Sensitive Categories
# ---------------------------------------------------------------------------
#
# Some information can differ depending on the student's nationality.
# The assistant should ask for clarification instead of assuming.
# ---------------------------------------------------------------------------

NATIONALITY_SENSITIVE_CATEGORIES = [

    "Financial Distress",

    "Accommodation",
]


# ---------------------------------------------------------------------------
# Official Websites
# ---------------------------------------------------------------------------

UGBS_WEBSITE = "https://ugbs.ug.edu.gh"

UG_WEBSITE = "https://www.ug.edu.gh"


# ---------------------------------------------------------------------------
# Severity Levels
# ---------------------------------------------------------------------------

SEVERITY_LEVELS = [

    "Low",

    "Medium",

    "High",

    "Critical",
]


# ---------------------------------------------------------------------------
# Admin Configuration
# ---------------------------------------------------------------------------

# Optional admin password.
#
# Set this in your .env file:
#
# ADMIN_PASSWORD=your_password
#
# Do NOT put the real password directly in this file.

ADMIN_PASSWORD = os.getenv(
    "ADMIN_PASSWORD",
    ""
)


# ---------------------------------------------------------------------------
# LLM Availability Check
# ---------------------------------------------------------------------------

def llm_is_configured() -> bool:
    """
    Determine whether the configured LLM provider is usable.

    Ollama does not require an API key. The application will attempt to
    connect to the configured Ollama server and handle connection failures
    elsewhere.

    Gemini and Anthropic require their respective API keys.
    """

    if LLM_PROVIDER == "ollama":
        return True

    if LLM_PROVIDER == "gemini":
        return bool(GEMINI_API_KEY)

    if LLM_PROVIDER == "anthropic":
        return bool(ANTHROPIC_API_KEY)

    return False