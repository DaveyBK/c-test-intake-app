# C-Test Intake App

A placement and intake tool for English language assessment using the C-Test format.

## What is a C-Test?

A C-Test is a language proficiency test where students complete partially deleted words in context. This tests reading comprehension, vocabulary, and grammar knowledge simultaneously.

**Example C-Test:**

```
The wea____ was col__ yest____day morn____. 
I walk____ to scho____ beca____ I was lat____.
```

**Student answers:**
```
1. weather
2. cold
3. yesterday
4. morning
5. walked
6. school
7. because
8. late
```

**Grading:** Each correct completion = 1 point. Percentage is converted to 0-5 scale for placement.

## Features

- ✅ Exact-match C-Test grading with spelling variants
- ✅ Support for British/American spelling (colour/color, centre/center, etc.)
- ✅ Item-by-item feedback and detailed scoring
- ✅ Multiple answer formats (numbered list or bracket format)
- ✅ Student profile integration (ready for inventory.db)
- ✅ Local SQLite database for offline operation
- ✅ Placement level assignment (0-5 scale)
- ✅ Full test history tracking

## Scoring Rubric

Percentage correct is converted to 0-5 placement scale:

| Score | Percentage | Placement Level |
|-------|------------|-----------------|
| 5 | 90%+ | Advanced |
| 4 | 75-89% | Upper-Intermediate |
| 3 | 60-74% | Intermediate |
| 2 | 45-59% | Pre-Intermediate |
| 1 | 30-44% | Elementary |
| 0 | <30% | Beginner |

## Setup

### 1. Install Python 3.8+

Make sure Python 3.8 or higher is installed.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure settings

Copy `config.example.py` to `config.py` and edit:

```python
# Database paths
DB_PATH = "./data/c_test.db"              # Local database
INVENTORY_DB_PATH = "/path/to/inventory.db"  # Shared database (optional)

# Integration settings
OFFLINE_MODE = True   # Set to False to enable inventory.db sync
AUTO_SYNC = False     # Auto-sync to inventory.db after each test
```

### 4. Run the app

```bash
python main.py
```

## Usage

### Programmatic API

```python
from c_test_grader import grade_c_test
from c_test_parser import extract_c_test_answers

# Define answer key
answer_key = {
    1: "weather",
    2: "cold",
    3: "yesterday",
    4: "morning"
}

# Student's submission text
student_text = """
1. weather
2. cold
3. yesterday
4. morning
"""

# Parse answers
student_answers = extract_c_test_answers(student_text, num_items=4)

# Grade the test
score, items, feedback = grade_c_test(answer_key, student_answers)

print(f"Score: {score}/5")
print(feedback)
```

### Answer Formats Supported

**Numbered List Format:**
```
1. weather
2. cold
3. yesterday
```

**Bracket Format:**
```
The wea[weather] was col[cold] yest[yesterday]day.
```

### Database Integration

The app uses a dual-database architecture:

1. **Local database (`c_test.db`)**: Stores all test results locally for offline operation
2. **Inventory database (`inventory.db`)**: Shared database with student profiles and complete learning history

When `OFFLINE_MODE = False` and inventory.db is available:
- Student list is loaded from inventory.db
- Test results are saved to both databases
- Sync status is tracked for reliability

## File Structure

```
c-test-intake-app/
├── main.py                 # Application entry point
├── config.example.py       # Configuration template
├── config.py               # Your configuration (create from example)
├── models.py               # Data models (Student, CTestResult, CTestItem)
├── db.py                   # Local database operations
├── inventory_db.py         # Shared database integration
├── c_test_grader.py        # Grading engine
├── c_test_parser.py        # Answer parsing
├── tests/                  # Unit tests
│   ├── test_c_test_grader.py
│   └── test_c_test_parser.py
├── data/
│   └── c_test.db           # Local database (created automatically)
└── GAP_ANALYSIS_REPORT.md  # Integration planning document
```

## Adding C-Test Templates

```python
from db import get_db
import json

# Create answer key
answer_key = {
    1: "weather",
    2: "cold",
    3: "yesterday",
    4: "morning",
    5: "walked",
    6: "school",
    7: "because",
    8: "late"
}

# Add template to database
db = get_db()
db.add_c_test_template(
    version="A",
    text="The wea____ was col____ yest____day morn____...",
    answer_key=json.dumps(answer_key),
    num_items=len(answer_key)
)
```

## Inventory Database Integration

### Required Schema

To integrate with your school's inventory.db, ensure it has these tables:

```sql
-- Students table
CREATE TABLE students (
    student_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    current_level TEXT
);

-- C-Test results table
CREATE TABLE c_test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    test_version TEXT NOT NULL,
    test_date DATETIME NOT NULL,
    num_items INTEGER NOT NULL,
    num_correct INTEGER NOT NULL,
    percentage REAL NOT NULL,
    score INTEGER NOT NULL,
    placement_level TEXT,
    completed BOOLEAN DEFAULT 1,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- Optional: Item-level details
CREATE TABLE c_test_result_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id INTEGER NOT NULL,
    item_number INTEGER NOT NULL,
    correct_word TEXT NOT NULL,
    student_answer TEXT,
    is_correct BOOLEAN NOT NULL,
    FOREIGN KEY (result_id) REFERENCES c_test_results(id)
);
```

### Providing Schema Access

If your inventory.db has a different schema, please update `inventory_db.py` with the correct table and column names.

## Development

### Running Tests

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test file
python -m unittest tests.test_c_test_grader
```

All 50 unit tests should pass:
- 17 tests for grading engine
- 33 tests for answer parsing

### Code Quality

The app follows these principles:
- Pure C-Test functionality (no reading/writing homework code)
- Student-aware (supports multiple students via inventory.db)
- Offline-first (works without inventory.db connection)
- Tested (50+ unit tests with 100% pass rate)

## Architecture

The C-Test app is designed to integrate with the NestMind school ecosystem:

```
┌─────────────────┐
│  C-Test Intake  │
│   Application   │
└────────┬────────┘
         │
    ┌────▼─────────────┐
    │  Local Database  │ ← Always available (offline mode)
    │  (c_test.db)     │
    └────┬─────────────┘
         │
    ┌────▼──────────────┐
    │ Inventory Database│ ← Shared with teacher portal
    │ (inventory.db)    │
    └───────────────────┘
```

**Benefits:**
- Works offline (local database)
- Syncs to shared database when online
- Integrates with teacher portal and lesson planning
- Feeds student learning history across all apps

## Troubleshooting

### Database not found

Create the data directory:
```bash
mkdir -p data
```

### Inventory database connection fails

Check `config.py`:
1. Verify `INVENTORY_DB_PATH` points to correct file
2. Ensure the file exists and is readable
3. Set `OFFLINE_MODE = True` to use local database only

### Import errors

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## License

See LICENSE file for details.

## Related Documents

- `GAP_ANALYSIS_REPORT.md`: Detailed analysis of the C-Test codebase and integration planning
- `config.example.py`: Configuration options with comments

---

**Note:** This is a pure C-Test placement tool. It does NOT include:
- Homework tracking or generation
- Reading comprehension grading
- Writing quality assessment
- Folder watching or file monitoring

For ongoing homework management, see the separate reading/writing app.
