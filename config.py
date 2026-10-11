"""
CampusInsight Configuration Module
Defines system-wide constants, grading criteria, passing rules, and environment settings.
"""
from pathlib import Path
from typing import Dict, List, Tuple

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "campus_insight.db"
SAMPLE_DATA_DIR = BASE_DIR / "sample_data"
POWERBI_DIR = BASE_DIR / "powerbi"

# Ensure directories exist
SAMPLE_DATA_DIR.mkdir(exist_ok=True)
POWERBI_DIR.mkdir(exist_ok=True)

# Application Metadata
APP_NAME = "CampusInsight"
APP_TAGLINE = "Academic Performance & Student Improvement Intelligence System"
VERSION = "1.0.0"

# Theme Colors (Professional Education SaaS: Navy & Teal)
THEME_COLORS = {
    "primary": "#1E3A8A",      # Deep Navy
    "primary_light": "#3B82F6",# Royal Blue
    "secondary": "#0D9488",    # Teal
    "secondary_light": "#14B8A6",
    "background": "#F8FAFC",   # Very Light Slate
    "card_bg": "#FFFFFF",
    "text_dark": "#0F172A",    # Dark Slate
    "text_muted": "#64748B",   # Slate Muted
    "success": "#10B981",      # Emerald
    "warning": "#F59E0B",      # Amber
    "danger": "#EF4444",       # Crimson
    "border": "#E2E8F0"
}

# Standard 10-Point Academic Grading Scheme (Configurable)
# (Grade, Min Total %, Grade Point, Description)
DEFAULT_GRADE_SCALE: List[Tuple[str, float, int, str]] = [
    ("O",  90.0, 10, "Outstanding"),
    ("A+", 80.0, 9,  "Excellent"),
    ("A",  70.0, 8,  "Very Good"),
    ("B+", 60.0, 7,  "Good"),
    ("B",  55.0, 6,  "Above Average"),
    ("C",  50.0, 5,  "Average"),
    ("P",  40.0, 4,  "Pass"),
    ("F",  0.0,  0,  "Fail"),
]

# Configurable Passing Rules
DEFAULT_PASSING_RULES: Dict[str, float] = {
    "min_internal_percentage": 40.0,   # Minimum 40% in internal assessments
    "min_external_percentage": 35.0,   # Minimum 35% in semester end examination
    "min_total_percentage": 40.0,      # Minimum 40% overall in the subject
}

# Supported Departments / Branches
DEPARTMENTS: List[str] = [
    "Computer Science and Engineering",
    "Information Science and Engineering",
    "Electronics and Communication Engineering",
    "Mechanical Engineering",
]

# Demo Credentials for Local Evaluation
DEMO_CREDENTIALS = {
    "faculty_1": {
        "username": "dr.sharma",
        "password": "Password123!",
        "role": "faculty",
        "name": "Dr. Ramesh Sharma",
        "email": "r.sharma@campusinsight.edu",
        "dept": "Computer Science and Engineering",
        "subjects": ["CS501", "CS503"]
    },
    "faculty_2": {
        "username": "prof.anita",
        "password": "Password123!",
        "role": "faculty",
        "name": "Prof. Anita Deshmukh",
        "email": "a.deshmukh@campusinsight.edu",
        "dept": "Computer Science and Engineering",
        "subjects": ["CS502", "CS504"]
    },
    "student_1": {
        "username": "usn101",
        "password": "Student123!",
        "role": "student",
        "usn": "1CI22CS101",
        "name": "Aarav Patel",
        "email": "aarav.patel@student.edu",
        "branch": "Computer Science and Engineering",
        "semester": 5,
        "section": "A"
    },
    "student_2": {
        "username": "usn102",
        "password": "Student123!",
        "role": "student",
        "usn": "1CI22CS102",
        "name": "Bhavya Rao",
        "email": "bhavya.rao@student.edu",
        "branch": "Computer Science and Engineering",
        "semester": 5,
        "section": "A"
    },
    "student_3": {
        "username": "usn103",
        "password": "Student123!",
        "role": "student",
        "usn": "1CI22CS103",
        "name": "Chirag Nair",
        "email": "chirag.nair@student.edu",
        "branch": "Computer Science and Engineering",
        "semester": 5,
        "section": "B"
    }
}
