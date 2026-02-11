# C-test Intake App

A homework tracking app for English C-test assessment and tutoring.

## Features

- ✅ Watch a local folder for new C-test submissions
- ✅ Extract text from `.docx` and `.txt` files
- ✅ Auto-grade C-test submissions with exact match checking
- ✅ Support for British/American spelling variants
- ✅ Item-by-item feedback and detailed scoring
- ✅ Manual score adjustment and comments
- ✅ SQLite database for tracking
- ✅ Simple Tkinter GUI
- ✅ Backward compatible with reading/writing grading

## C-test Format

A C-test requires students to complete word fragments in context. This tests reading comprehension, vocabulary, and grammar knowledge.

**Example C-test:**

```
The wea____ was col__ yest____day morn____. 
I walk____ to scho____ beca____ I was lat____.
```

**Student submits answers as:**

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

**Or in bracket format:**

```
The wea[weather] was col[cold] yest[yesterday]day morn[morning].
I walk[walked] to scho[school] beca[because] I was lat[late].
```

**Grading:**

- Each correct completion = 1 point
- Percentage correct converted to 0-5 scale:
  - 90%+ = 5 (Excellent)
  - 75-89% = 4 (Good)
  - 60-74% = 3 (Pass)
  - 45-59% = 2 (Below Average)
  - 30-44% = 1 (Poor)
  - <30% = 0 (Fail)
- British/American spelling variants accepted (e.g., "colour"/"color")

## Setup

### 1. Install Python 3.8+

Make sure Python 3.8 or higher is installed on your Windows PC.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or just:

```bash
pip install python-docx
```

### 3. Configure settings

Copy `config.example.py` to `config.py` and edit the values:

- `STUDENT_NAME`: Student name for filename matching (default: `"Student 1"`)
- `INBOX_FOLDER`: Where student puts homework files (default: `./inbox`)
- `GENERATED_FOLDER`: Where generated homework goes (default: `./generated`)
- `C_TEST_ACCEPT_VARIANTS`: Accept British/American spelling (default: `True`)
- `C_TEST_PASSING_SCORE`: Minimum passing score (default: `3`)
- Other settings as needed

### 4. Run the app

```bash
python main.py
```

## Usage

### C-test Workflow

1. **Student submits C-test**
   - Saves file to inbox folder (or synced Drive folder)
   - Filename format: `YYYYMMDD_Student1_hwNN.docx` or `Student1_hwNN.txt`
   - Example: `20250115_Student1_hw03.docx`
   - Answers in numbered list or bracket format

2. **App detects and grades the file**
   - Automatically extracts answers
   - Grades against answer key
   - Shows item-by-item results
   - Calculates percentage and 0-5 score

3. **You review and adjust**
   - Select homework in the list
   - View student's responses and grading details
   - Adjust scores if needed
   - Add a comment
   - Click "Save Scores"

### Answer Key Format

Create answer keys as Python dictionaries:

```python
answer_key = {
    1: "weather",
    2: "cold",
    3: "yesterday",
    4: "morning",
    5: "walked",
    6: "school",
    7: "because",
    8: "late",
}
```

### Submission Formats

**Numbered List Format (Recommended):**
```
1. weather
2. cold
3. yesterday
4. morning
```

**Bracket Format:**
```
The wea[weather] was col[cold] yest[yesterday]day morn[morning].
```

### Filename Patterns

The app recognizes these filename formats:

| Format | Example |
|--------|---------|
| `YYYYMMDD_Student1_hwNN.ext` | `20250115_Student1_hw03.docx` |
| `Student1_hwNN.ext` | `Student1_hw03.txt` |
| `hwNN_Student1.ext` | `hw03_Student1.docx` |
| `hwNN.ext` | `hw03.txt` (assumes Student 1) |

### Scoring Rubric

**C-test Score (0-5):**
- 90%+ correct = 5 (Excellent)
- 75-89% correct = 4 (Good)
- 60-74% correct = 3 (Pass)
- 45-59% correct = 2 (Below Average)
- 30-44% correct = 1 (Poor)
- <30% correct = 0 (Fail)

**Backward Compatibility:**

The app still supports traditional reading/writing grading:

**Reading Score (0-5):**
- Based on comprehension phrases found
- Examples: "the main idea", "according to the text", "because"
- Penalized for very short responses

**Writing Score (0-5):**
- Based on word count and sentence variety
- Penalized for missing punctuation, lowercase errors

**Listening Score (0-5):**
- Entered manually by teacher

## Folder Structure

```
c-test-intake-app/
├── main.py              # Run this to start
├── config.example.py    # Configuration template (copy to config.py)
├── config.py            # Configuration (create from example)
├── db.py                # Database operations
├── models.py            # Data classes
├── watcher.py           # Folder watching
├── extractor.py         # Text extraction
├── grader.py            # Traditional reading/writing grading
├── c_test_grader.py     # C-test grading engine
├── c_test_parser.py     # C-test answer parser
├── generator.py         # Homework generation
├── gui.py               # Tkinter interface
├── requirements.txt     # Dependencies
├── tests/               # Unit tests
├── inbox/               # Student drops files here
├── generated/           # Generated homework goes here
└── data/
    └── homework.db      # SQLite database
```

## Google Drive Sync (Optional)

For automatic syncing with Google Drive:

1. Install [Google Drive for Desktop](https://www.google.com/drive/download/)
2. Set up a shared folder with your student
3. Change `INBOX_FOLDER` in `config.py` to point to:
   - Windows: `C:\Users\YourName\Google Drive\Homework\inbox`
   - Or wherever your synced folder is
4. The app watches this folder; Drive syncs it automatically

## Troubleshooting

### "python-docx not installed"

```bash
pip install python-docx
```

### Files not detected

- Check filename matches expected pattern
- Only `.docx` and `.txt` are supported
- Check the inbox folder path in `config.py`

### C-test grading issues

- Ensure answer key is properly formatted
- Check that student submission uses numbered list or bracket format
- Verify British/American spelling variants are enabled in config if needed

### Database errors

Delete `data/homework.db` to reset (you'll lose history).

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_c_test_grader.py
```

### Adding a New C-test Template

```python
from db import get_db
import json

# Create answer key
answer_key = {
    1: "weather",
    2: "cold",
    # ... more items
}

# Add to database
db = get_db()
db.add_c_test_template(
    version="A",
    text="The wea____ was col____...",
    answer_key=json.dumps(answer_key),
    num_items=len(answer_key)
)
```

## API Usage

### Grading a C-test Programmatically

```python
from c_test_grader import grade_c_test

# Define answer key
answer_key = {
    1: "weather",
    2: "cold",
    3: "yesterday"
}

# Student answers
student_answers = {
    1: "weather",
    2: "cold",
    3: "yesterday"
}

# Grade the test
score, items, feedback = grade_c_test(answer_key, student_answers)

print(f"Score: {score}/5")
print(feedback)
```

### Parsing Student Submissions

```python
from c_test_parser import extract_c_test_answers

# From numbered list
text = "1. weather\n2. cold\n3. yesterday"
answers = extract_c_test_answers(text, num_items=3)

# From bracket format
text = "The wea[weather] was col[cold]"
answers = extract_c_test_answers(text, num_items=2)
```

## Future Ideas

- Multiple students
- Progress charts
- PDF support
- Google Drive API integration
- Multiple C-test versions
- Adaptive difficulty
- Detailed analytics
