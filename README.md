# 10-Minute Reading App (V1)

A simple homework tracking app for English tutoring.

## V1 Features

- ✅ Watch a local folder for new homework files
- ✅ Extract text from `.docx` and `.txt` files
- ✅ Auto-grade reading and writing (simple rule-based)
- ✅ Manual score adjustment and comments
- ✅ Generate next homework (reading + writing template)
- ✅ SQLite database for tracking
- ✅ Simple Tkinter GUI

## V1 Limitations (by design)

- ❌ No Google Drive API (use Drive for Desktop sync)
- ❌ Single student only (designed for individual tutoring)
- ❌ No PDF support
- ❌ No charts or progress graphs
- ❌ No difficulty scaling

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
- Other settings as needed

### 4. Run the app

```bash
python main.py
```

## Usage

### Workflow

1. **Student submits homework**
    - Saves file to inbox folder (or synced Drive folder)
    - Filename format: `YYYYMMDD_Student1_hwNN.docx` or `Student1_hwNN.txt`
    - Example: `20250115_Student1_hw03.docx`

2. **App detects the file**
   - Automatically extracts text
   - Auto-generates reading and writing scores (0-5)
   - Shows in the homework list

3. **You review and adjust**
   - Select homework in the list
   - View student's response
   - Adjust scores if needed
   - Add a comment
   - Click "Save Scores"

4. **Generate next homework**
   - Click "Generate Next Homework"
   - App creates reading + writing files
   - Files saved to `generated/` folder
   - You share them with student (manually or via Drive sync)

### Filename Patterns

The app recognizes these filename formats:

| Format | Example |
|--------|---------|
| `YYYYMMDD_Student1_hwNN.ext` | `20250115_Student1_hw03.docx` |
| `Student1_hwNN.ext` | `Student1_hw03.txt` |
| `hwNN_Student1.ext` | `hw03_Student1.docx` |
| `hwNN.ext` | `hw03.txt` (assumes Student 1) |

### Scoring Rubric

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
ten_min_app/
├── main.py           # Run this to start
├── config.example.py # Configuration template (copy to config.py)
├── config.py         # Configuration (create from example)
├── db.py             # Database operations
├── models.py         # Data classes
├── watcher.py        # Folder watching
├── extractor.py      # Text extraction
├── grader.py         # Auto-scoring
├── generator.py      # Homework generation
├── gui.py            # Tkinter interface
├── requirements.txt  # Dependencies
├── inbox/            # Student drops files here
├── generated/        # Generated homework goes here
└── data/
    └── homework.db   # SQLite database
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
- Only `.docx` and `.txt` are supported in V1
- Check the inbox folder path in `config.py`

### Database errors

Delete `data/homework.db` to reset (you'll lose history).

## Future V2 Ideas

- Multiple students
- Progress charts
- PDF support
- Google Drive API integration
- LLM-based grading
- Difficulty adaptation
