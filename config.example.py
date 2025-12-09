# Configuration for 10-Minute Reading App (V1)
# Copy this file to config.py and customize the values for your setup

# Student Information
STUDENT_NAME = "Student 1"  # Name of the student

# Folder Paths (relative to project root)
INBOX_FOLDER = "./inbox"        # Where student submits homework files
GENERATED_FOLDER = "./generated"  # Where generated homework files are saved

# Database
DB_PATH = "./data/homework.db"  # SQLite database location

# Scoring Configuration
MIN_SCORE = 0  # Minimum possible score
MAX_SCORE = 5  # Maximum possible score

# File Watching
POLL_INTERVAL = 5  # Seconds between folder checks
SUPPORTED_EXTENSIONS = [".docx", ".txt"]  # Supported file formats