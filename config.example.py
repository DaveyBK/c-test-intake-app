# Configuration for C-Test Intake App
# Copy this file to config.py and customize the values for your setup

# Database Paths
DB_PATH = "./data/c_test.db"  # Local C-Test database
INVENTORY_DB_PATH = None  # Path to shared inventory.db (set to actual path when available)

# Scoring Configuration
MIN_SCORE = 0  # Minimum possible score
MAX_SCORE = 5  # Maximum possible score

# C-Test Configuration
C_TEST_ACCEPT_VARIANTS = True  # Accept British/American spelling variants
C_TEST_DEFAULT_VERSION = "A"   # Default test version
C_TEST_PASSING_SCORE = 3       # Minimum passing score (0-5)

# C-Test Scoring Thresholds (percentage to score conversion)
C_TEST_SCORE_THRESHOLDS = {
    5: 90,  # 90%+ = score 5
    4: 75,  # 75-89% = score 4
    3: 60,  # 60-74% = score 3
    2: 45,  # 45-59% = score 2
    1: 30,  # 30-44% = score 1
}

# Placement Level Mapping (score to level)
PLACEMENT_LEVELS = {
    0: "Beginner",
    1: "Elementary",
    2: "Pre-Intermediate",
    3: "Intermediate",
    4: "Upper-Intermediate",
    5: "Advanced"
}

# Integration Settings
OFFLINE_MODE = True  # If True, only uses local database
AUTO_SYNC = False    # If True, automatically syncs to inventory.db when available