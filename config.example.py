# Configuration for C-test Intake App
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

# C-test Configuration
C_TEST_ACCEPT_VARIANTS = True  # Accept British/American spelling
C_TEST_DEFAULT_VERSION = "A"   # Default test version
C_TEST_PASSING_SCORE = 3       # Minimum passing score (0-5)

# C-test Scoring Thresholds (percentage to score conversion)
C_TEST_SCORE_THRESHOLDS = {
    5: 90,  # 90%+ = score 5
    4: 75,  # 75-89% = score 4
    3: 60,  # 60-74% = score 3
    2: 45,  # 45-59% = score 2
    1: 30,  # 30-44% = score 1
}