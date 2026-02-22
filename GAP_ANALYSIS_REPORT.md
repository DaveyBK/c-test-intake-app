# C-TEST APP — Gap Analysis and Student Profile Integration Report

**Date:** 2026-02-18  
**Analyst:** Systems Analyst  
**Purpose:** Map current state of C-Test app against requirements for NestMind integration

---

## EXECUTIVE SUMMARY

This report documents the current state of the C-Test Intake App, identifies code that does not belong, and outlines gaps that must be addressed before integrating with the NestMind ecosystem's shared student database (inventory.db).

**Key Findings:**
- The C-Test app is currently mixed with "10-Minute Reading App" code
- Student identity is hardcoded via config (single student only)
- Local database (homework.db) has no student/class schema
- No mechanism exists to read from or write to inventory.db
- Folder watching (watcher.py) is reading app functionality, not C-Test
- README contains significant reading app content that doesn't belong

---

## TASK 1 — README AUDIT

Analysis of `/README.md` to identify C-Test vs. Reading App content:

### BELONGS IN C-TEST README:

- **C-test Format section** (lines 17-59): Correctly describes C-test format, examples, and grading rubric. This is core C-Test functionality.
- **C-test grading auto-grade feature** (line 9): "Auto-grade C-test submissions with exact match checking" - legitimate C-Test feature.
- **Support for British/American spelling variants** (line 10): Relevant to C-Test grading.
- **Item-by-item feedback** (line 11): C-Test specific grading detail.
- **C-test Configuration section** (lines 22-34 in config): `C_TEST_ACCEPT_VARIANTS`, `C_TEST_DEFAULT_VERSION`, `C_TEST_PASSING_SCORE` are C-Test specific.
- **Answer Key Format** (lines 118-133): Describes how to create C-Test answer keys.
- **API Usage section** (lines 281-321): Shows how to use C-Test grading and parsing programmatically.
- **Adding a New C-test Template** (lines 258-279): Describes C-Test template management.

### DOES NOT BELONG (Reading App or Other):

- **App title and description** (lines 1-3): "A homework tracking app for English C-test assessment and tutoring" - The C-Test is an intake/placement tool, not a homework tracking system. This description fits the reading app.
- **"Watch a local folder for new C-test submissions"** (line 7): Folder watching is for continuous homework submission monitoring (reading app), not one-time intake testing.
- **"Backward compatible with reading/writing grading"** (line 15): The C-Test should not need backward compatibility with reading/writing grading. This indicates mixed codebases.
- **Filename pattern matching** (lines 152-160, 96-103): Pattern matching like `YYYYMMDD_Student1_hwNN.docx` suggests ongoing homework tracking, not one-time C-Test administration.
- **Folder Structure** (lines 187-209): Lists files like `watcher.py` (folder watching), `grader.py` (reading/writing grading), `generator.py` (homework generation) - none of these are C-Test functions.
- **Google Drive Sync section** (lines 211-221): This describes setting up Google Drive for automatic homework syncing. The C-Test is administered as a one-time placement test, not via continuous file syncing.
- **"Student submits C-test" workflow** (lines 99-103): Describes student saving files to inbox folder with specific filename patterns. A proper C-Test intake should have a UI where student logs in, takes test, and submits - not file-based submission.
- **Backward Compatibility section** (lines 171-186): Describes reading/writing/listening score grading. This is not C-Test functionality.
- **Generator in folder structure** (line 201): `generator.py` for homework generation - C-Test doesn't generate homework, it's a standardized placement test.
- **Watcher description** (line 196): "Folder watching" - belongs to continuous homework monitoring, not C-Test.
- **Grader.py description** (line 198): "Traditional reading/writing grading" - explicitly not C-Test.

### UNCLEAR:

- **"Multiple students" in Future Ideas** (line 325): This could be relevant for C-Test (testing multiple students), but the current implementation is single-student only via config. Whether this belongs depends on whether the C-Test UI will select students or remain config-based.
- **SQLite database for tracking** (line 13): Database tracking is needed for C-Test results, but the current `homework.db` schema is designed for homework submissions, not placement test results.
- **Simple Tkinter GUI** (line 14): A GUI is needed for C-Test administration, but the current GUI (`gui.py`) is designed for homework review, not test-taking.

---

## TASK 2 — C-TEST CODEBASE AUDIT

Analysis of all Python files in the repository:

### FILE: `watcher.py`
**Purpose:** Polls a local folder for new homework files, detects them, parses filenames, and triggers processing.  
**Belongs to C-Test:** **NO** - This is 10-Minute Reading App functionality  
**Key functions:**
  - `FolderWatcher.__init__()`: Initialize folder watcher with polling interval
  - `FolderWatcher.start()`: Start watching in background thread
  - `FolderWatcher.check_once()`: Check for new files once
  - `FolderWatcher._poll_loop()`: Background polling loop
  - `parse_filename()`: Parse homework filename to extract date, student, hw_number
**External dependencies:** `config` (INBOX_FOLDER, POLL_INTERVAL, STUDENT_NAME)  
**Database interactions:** None directly, but checks if file is processed via callback  
**Student identity:** Parses student name from filename using `STUDENT_NAME` from config  
**Comments:** File header explicitly says "Local folder watcher for 10-Minute Reading App (V1)". This is for continuous homework monitoring, not one-time C-Test intake.

---

### FILE: `main.py`
**Purpose:** Application entry point. Starts the GUI.  
**Belongs to C-Test:** **PARTIALLY** - Entry point is needed, but branding is wrong  
**Key functions:**
  - `main()`: Initialize database, start GUI
**External dependencies:** `config`, `db`, `gui`  
**Database interactions:** Calls `get_db()` to initialize homework.db  
**Student identity:** Prints `STUDENT_NAME` from config  
**Comments:** File header says "10-Minute Reading App (V1)" - wrong branding. The entry point logic is generic and could work for C-Test, but initialization should be for C-Test, not reading app.

---

### FILE: `models.py`
**Purpose:** Data models for submissions, scores, and C-test items.  
**Belongs to C-Test:** **PARTIALLY** - CTestItem and CTestSubmission belong, Homework and GeneratedHomework don't  
**Key functions:**
  - `Homework`: Dataclass for homework submissions with reading/writing/listening scores
  - `GeneratedHomework`: Dataclass for generated homework assignments
  - `CTestItem`: Dataclass for single C-test completion item
  - `CTestSubmission`: Dataclass for complete C-test submission
**External dependencies:** `dataclasses`, `datetime`  
**Database interactions:** None (just data models)  
**Student identity:** No student identifier in any model  
**Comments:** 
  - **BELONGS:** `CTestItem`, `CTestSubmission` - these are C-Test specific
  - **DOES NOT BELONG:** `Homework` (reading/writing/listening scores are not C-Test), `GeneratedHomework` (C-Test doesn't generate homework)

---

### FILE: `db.py`
**Purpose:** SQLite database layer with schema and CRUD operations.  
**Belongs to C-Test:** **PARTIALLY** - C-test tables belong, homework/generated tables don't  
**Key functions:**
  - `Database.__init__()`: Initialize database and create tables
  - `Database.add_homework()`: Add homework submission
  - `Database.get_homework()`: Get homework by ID
  - `Database.update_homework()`: Update homework scores/comment
  - `Database.add_c_test_template()`: Add C-test template
  - `Database.get_c_test_template()`: Get C-test template
  - `Database.save_c_test_items()`: Save C-test item-level results
  - `Database.get_c_test_items()`: Get C-test item results
  - `Database.add_generated_homework()`: Add generated homework record
  - `Database.is_file_processed()`: Check if file was processed
  - `Database.mark_file_processed()`: Mark file as processed
**External dependencies:** `sqlite3`, `config` (DB_PATH)  
**Database interactions:** Creates and manages `homework.db` with tables:
  - `homeworks`: Homework submissions (hw_number, file info, reading/writing/listening scores)
  - `generated_homeworks`: Generated homework records
  - `processed_files`: Tracks which files were processed
  - `c_test_items`: C-test item-level grading details
  - `c_test_templates`: C-test versions/answer keys
**Student identity:** **NONE** - No student_id column in any table  
**Comments:** File header says "10-Minute Reading App (V1)". 
  - **BELONGS:** `c_test_items`, `c_test_templates` tables and their operations
  - **DOES NOT BELONG:** `homeworks`, `generated_homeworks`, `processed_files` tables
  - **CRITICAL GAP:** No student table, no class table, no student_id foreign key

---

### FILE: `grader.py`
**Purpose:** Rule-based grading for reading comprehension and writing quality.  
**Belongs to C-Test:** **NO** - This is reading/writing homework grading  
**Key functions:**
  - `grade_homework()`: Grade reading and writing (returns 0-5 scores)
  - `_calculate_reading_score()`: Score based on comprehension phrases
  - `_calculate_writing_score()`: Score based on word count, sentence variety
  - `_count_basic_errors()`: Count writing errors
  - `get_score_explanation()`: Generate explanation of scores
**External dependencies:** `config` (MIN_SCORE, MAX_SCORE), `extractor` (word/sentence count)  
**Database interactions:** None  
**Student identity:** None  
**Comments:** File header says "Simple rule-based grading for 10-Minute Reading App (V1)". This grades reading comprehension and writing quality using heuristics - not C-Test exact-match grading.

---

### FILE: `c_test_grader.py`
**Purpose:** C-test grading engine with exact match and spelling variants.  
**Belongs to C-Test:** **YES** - Core C-Test grading  
**Key functions:**
  - `CTestGrader.__init__()`: Initialize with answer key and variant settings
  - `CTestGrader.grade_submission()`: Grade C-test submission against answer key
  - `CTestGrader._check_answer()`: Check if answer matches (with variants)
  - `CTestGrader._percentage_to_score()`: Convert percentage to 0-5 score
  - `CTestGrader._generate_feedback()`: Generate detailed feedback
  - `grade_c_test()`: Convenience function for grading
**External dependencies:** `models` (CTestItem)  
**Database interactions:** None (pure grading logic)  
**Student identity:** None  
**Comments:** This is correct C-Test grading logic. Accepts answer key as dict, grades student answers, returns score (0-5), items, and feedback.

---

### FILE: `c_test_parser.py`
**Purpose:** Parse C-test student answers from various formats.  
**Belongs to C-Test:** **YES** - Core C-Test parsing  
**Key functions:**
  - `extract_c_test_answers()`: Main extraction function, tries multiple formats
  - `_parse_numbered_list()`: Parse "1. weather" format
  - `_parse_bracket_format()`: Parse "wea[weather]" format
  - `parse_c_test_with_template()`: Parse using template comparison
  - `normalize_answer()`: Normalize answer for comparison
  - `validate_answers()`: Validate completeness of answers
**External dependencies:** `re`  
**Database interactions:** None  
**Student identity:** None  
**Comments:** Correct C-Test functionality. Extracts student answers from text submissions.

---

### FILE: `extractor.py`
**Purpose:** Extract text from .docx and .txt files.  
**Belongs to C-Test:** **PARTIALLY** - Text extraction is needed, but focus is on homework files  
**Key functions:**
  - `extract_text()`: Main extraction function (supports .txt, .docx)
  - `_extract_txt()`: Extract from plain text
  - `_extract_docx()`: Extract from Word doc
  - `_clean_text()`: Clean up extracted text
  - `get_word_count()`: Count words
  - `get_sentence_count()`: Count sentences
**External dependencies:** `pathlib`, `docx` (python-docx)  
**Database interactions:** None  
**Student identity:** None  
**Comments:** File header says "10-Minute Reading App (V1)". Text extraction is a utility function that could be used by C-Test if submissions are file-based. However, a proper C-Test intake would have a form UI, not file extraction. Word/sentence counting is for reading/writing grading, not C-Test.

---

### FILE: `generator.py`
**Purpose:** Generate reading texts and writing prompts for homework.  
**Belongs to C-Test:** **NO** - C-Test doesn't generate homework  
**Key functions:**
  - `HomeworkGenerator.__init__()`: Initialize generator
  - `HomeworkGenerator.generate()`: Generate new homework assignment
  - `HomeworkGenerator._select_reading_text()`: Select from text bank
  - `HomeworkGenerator._select_writing_template()`: Select writing prompts
  - `HomeworkGenerator._write_reading_file()`: Write reading file
  - `HomeworkGenerator._write_writing_file()`: Write writing template
  - `generate_next_homework()`: Convenience function
**External dependencies:** `config` (GENERATED_FOLDER, STUDENT_NAME), `models` (GeneratedHomework)  
**Database interactions:** None (files written to disk)  
**Student identity:** Uses `STUDENT_NAME` from config  
**Comments:** File header says "Homework generator for 10-Minute Reading App (V1)". This generates reading comprehension homework with prompts. Not C-Test functionality - C-Test is a standardized placement test.

---

### FILE: `gui.py`
**Purpose:** Tkinter GUI for viewing, scoring, and generating homework.  
**Belongs to C-Test:** **NO** - This is homework review UI, not C-Test administration  
**Key functions:**
  - `App.__init__()`: Initialize GUI window and database
  - `App._setup_menu()`: Create menu bar
  - `App._setup_layout()`: Create main layout (homework list + details)
  - `App._create_left_panel()`: Homework list panel
  - `App._create_right_panel()`: Details and scoring panel
  - `App._start_watcher()`: Start folder watcher
  - `App._on_new_file_detected()`: Handle new file from watcher
  - `App._process_new_file()`: Process and grade new homework
  - `App._refresh_homework_list()`: Refresh homework list
  - `App._on_homework_selected()`: Display selected homework
  - `App._save_scores()`: Save teacher-adjusted scores
  - `App._generate_next_homework()`: Generate new homework assignment
**External dependencies:** `tkinter`, `db`, `watcher`, `extractor`, `grader`, `generator`, `config`  
**Database interactions:** Uses `Database` for all homework CRUD operations  
**Student identity:** Uses `STUDENT_NAME` from config, displays in title bar  
**Comments:** File header says "Tkinter GUI for 10-Minute Reading App (V1)". This is a teacher review interface for:
  - Watching inbox folder for submissions
  - Auto-grading reading/writing homework
  - Manually adjusting scores
  - Generating new homework
  
This is NOT a C-Test administration UI. A proper C-Test UI would:
  - Show student selection or login
  - Display C-Test questions with fragments
  - Allow student to enter answers
  - Submit and grade in real-time
  - Display results and placement level

---

### FILE: `config.example.py`
**Purpose:** Configuration template for the app.  
**Belongs to C-Test:** **PARTIALLY** - C-Test config belongs, reading app config doesn't  
**Key settings:**
  - `STUDENT_NAME`: Hardcoded student name (single student)
  - `INBOX_FOLDER`, `GENERATED_FOLDER`: File-based workflow folders
  - `DB_PATH`: Database path (homework.db)
  - `MIN_SCORE`, `MAX_SCORE`: Score range (0-5)
  - `POLL_INTERVAL`, `SUPPORTED_EXTENSIONS`: File watching settings
  - `C_TEST_ACCEPT_VARIANTS`, `C_TEST_DEFAULT_VERSION`, `C_TEST_PASSING_SCORE`: C-Test settings
**External dependencies:** None  
**Database interactions:** Defines DB_PATH  
**Student identity:** **HARDCODED** - single student via `STUDENT_NAME`  
**Comments:** 
  - **BELONGS:** C-Test specific settings
  - **DOES NOT BELONG:** INBOX_FOLDER, GENERATED_FOLDER, POLL_INTERVAL (reading app)
  - **CRITICAL GAP:** No inventory.db path, no multi-student support

---

### SUMMARY: Core C-Test Files (Keep)

These files contain legitimate C-Test functionality:

- **`c_test_grader.py`**: C-test grading engine (exact match, spelling variants, 0-5 scoring)
- **`c_test_parser.py`**: C-test answer parsing (numbered list, bracket format)
- **`models.py` (partial)**: `CTestItem`, `CTestSubmission` dataclasses
- **`db.py` (partial)**: `c_test_items`, `c_test_templates` tables and operations

---

### SUMMARY: Reading App Files (Do Not Belong)

These files are for the 10-Minute Reading App and should be removed or separated:

- **`watcher.py`**: Folder watching for continuous homework monitoring
- **`grader.py`**: Reading/writing homework grading (heuristics, not exact match)
- **`generator.py`**: Homework generation (reading texts + writing prompts)
- **`models.py` (partial)**: `Homework`, `GeneratedHomework` dataclasses
- **`db.py` (partial)**: `homeworks`, `generated_homeworks`, `processed_files` tables

---

### SUMMARY: Shared/Ambiguous Files

These files serve both apps or have mixed functionality:

- **`main.py`**: Generic entry point, but branded as "10-Minute Reading App"
  - KEEP: Entry point structure
  - CHANGE: Branding, initialization logic
  
- **`gui.py`**: Homework review UI, not C-Test administration UI
  - REMOVE: Current homework review interface
  - REPLACE: C-Test administration UI (show test, collect answers, grade, display results)
  
- **`extractor.py`**: Text extraction utility
  - KEEP IF: C-Test submissions are file-based
  - REMOVE IF: C-Test uses form-based UI (preferred)
  
- **`db.py`**: Database layer
  - KEEP: C-Test tables (`c_test_items`, `c_test_templates`)
  - REMOVE: Reading app tables (`homeworks`, `generated_homeworks`, `processed_files`)
  - ADD: Student/class schema integration, inventory.db connection
  
- **`config.example.py`**: Configuration
  - KEEP: C-Test settings
  - REMOVE: Reading app settings (INBOX_FOLDER, POLL_INTERVAL)
  - ADD: inventory.db path, multi-student support

---

## TASK 3 — ZONE B STUDENT SCHEMA

**Status:** The zoneb-teacher-assistant repository is private and requires authentication. I was unable to clone it to examine the schema directly.

### FINDINGS:

**STUDENT TABLE:**  
Cannot access - repository is private.

**CLASS TABLE:**  
Cannot access - repository is private.

**CLASS-STUDENT LINK:**  
Cannot access - repository is private.

**ANY EXISTING TEST/ASSESSMENT TABLES:**  
Cannot access - repository is private.

### RECOMMENDATIONS:

To complete this task, the analyst needs:
1. Access credentials to the zoneb-teacher-assistant repository, OR
2. Schema documentation for inventory.db (SQL CREATE statements or entity relationship diagram), OR
3. A copy of inventory.db to examine with SQLite browser

### ASSUMED SCHEMA (for gap analysis purposes):

Based on typical school management systems, inventory.db likely contains:

```sql
-- Students table
CREATE TABLE students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    date_of_birth DATE,
    enrollment_date DATE,
    current_level TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Classes table
CREATE TABLE classes (
    class_id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_name TEXT NOT NULL,
    teacher_id INTEGER,
    school_year TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Class enrollment (many-to-many)
CREATE TABLE class_students (
    class_id INTEGER,
    student_id INTEGER,
    enrollment_date DATE,
    PRIMARY KEY (class_id, student_id),
    FOREIGN KEY (class_id) REFERENCES classes(class_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);
```

**NOTE:** This is speculation. Actual schema must be verified.

---

## TASK 4 — GAP ANALYSIS

### 4a. Student Identity Gap

**Current State:**
- Student identity is **hardcoded** in `config.py` via `STUDENT_NAME = "Student 1"`
- No student selection UI exists
- No student database table exists
- All submissions are assumed to be from the single configured student
- Student name is parsed from filenames (e.g., `20250115_Student1_hw03.docx`)

**How it works now:**
1. `config.py` defines `STUDENT_NAME`
2. `watcher.py` uses `STUDENT_NAME` to parse filenames
3. Submissions are stored in `homeworks` table with `hw_number` but no `student_id`
4. GUI displays `STUDENT_NAME` in title bar

**What's Missing:**
- No concept of multiple students
- No student selection before taking C-Test
- No student login or authentication
- No reading from inventory.db to get student list
- No student profile loading (name, current level, test history)

**What Would Need to Change:**

1. **Database schema:**
   - Add `student_id` column to C-Test results table
   - Add foreign key to inventory.db students table
   
2. **UI changes:**
   - Add student selection screen (dropdown or search)
   - Load student list from inventory.db
   - Display selected student's name during test
   
3. **Code changes:**
   - Remove `STUDENT_NAME` from config
   - Add `get_students()` function to read from inventory.db
   - Pass `student_id` to all C-Test operations
   - Store `student_id` with test results

---

### 4b. Database Gap

**Current homework.db Schema:**

The C-Test app currently uses a local SQLite database at `./data/homework.db` with these tables:

```sql
-- Existing tables (homework.db)
CREATE TABLE homeworks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hw_number INTEGER NOT NULL UNIQUE,  -- No student_id!
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    extracted_text TEXT,
    status TEXT DEFAULT 'pending',
    submitted_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reading_score INTEGER,   -- Not C-Test
    writing_score INTEGER,   -- Not C-Test
    listening_score INTEGER, -- Not C-Test
    comment TEXT
);

CREATE TABLE c_test_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    homework_id INTEGER NOT NULL,  -- Links to homework, not student!
    item_number INTEGER NOT NULL,
    correct_word TEXT NOT NULL,
    student_answer TEXT,
    is_correct BOOLEAN,
    FOREIGN KEY (homework_id) REFERENCES homeworks(id)
);

CREATE TABLE c_test_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL UNIQUE,
    text_with_fragments TEXT NOT NULL,
    answer_key TEXT NOT NULL,
    num_items INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Reading app tables (not C-Test)
CREATE TABLE generated_homeworks (...);
CREATE TABLE processed_files (...);
```

**Critical Gaps:**

1. **No student_id anywhere** - Cannot track which student took which test
2. **`homeworks` table is wrong model** - C-Test results ≠ homework submissions
3. **Reading/writing/listening scores** - Not C-Test data
4. **`homework_id` foreign key** - Items link to homework, not to test sessions
5. **No test date/time tracking** - When was test taken?
6. **No placement level storage** - Where do we record the placement result?
7. **No connection to inventory.db** - Completely isolated database

**What a C-Test Results Table Should Look Like (in inventory.db):**

```sql
CREATE TABLE c_test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    test_version TEXT NOT NULL,  -- e.g., "A", "B"
    test_date DATETIME NOT NULL,
    num_items INTEGER NOT NULL,
    num_correct INTEGER NOT NULL,
    percentage REAL NOT NULL,
    score INTEGER NOT NULL,  -- 0-5 scale
    placement_level TEXT,  -- e.g., "Intermediate", "Advanced"
    completed BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE c_test_result_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id INTEGER NOT NULL,
    item_number INTEGER NOT NULL,
    correct_answer TEXT NOT NULL,
    student_answer TEXT,
    is_correct BOOLEAN NOT NULL,
    FOREIGN KEY (result_id) REFERENCES c_test_results(id)
);
```

**Integration Requirements:**

1. **Keep homework.db for offline/local operation** - C-Test can work offline
2. **Add inventory.db connection** - For reading student list and writing results
3. **Sync strategy:**
   - Take test → save to local homework.db immediately
   - Write to inventory.db when online
   - Track sync status (pending, synced, failed)

---

### 4c. Integration Gap

**What Does Not Exist Yet:**

1. **Reading inventory.db to load student list**
   - No code to connect to inventory.db
   - No function to query students table
   - No UI to display/select students
   
2. **Writing test results to inventory.db**
   - No `c_test_results` table in inventory.db (assumed - cannot verify)
   - No code to insert into inventory.db
   - No error handling for write failures
   
3. **Keeping local copy in homework.db**
   - Current schema doesn't support proper C-Test results
   - Need to redesign local schema to mirror inventory.db structure
   - Need student_id column
   
4. **Syncing between local and shared database**
   - No sync mechanism exists
   - No sync status tracking
   - No conflict resolution (what if student takes test offline and online?)
   - No queue for pending writes

**Proposed Architecture:**

```
┌─────────────────┐
│   C-Test UI     │
│  (new Tkinter)  │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  Select  │
    │  Student │ ← Read from inventory.db
    └────┬─────┘
         │
    ┌────▼────────┐
    │  Administer │
    │   C-Test    │
    └────┬────────┘
         │
    ┌────▼─────┐
    │   Grade  │
    └────┬─────┘
         │
    ┌────▼────────────────┐
    │  Save to:           │
    │  1. homework.db     │ ← Always (local)
    │  2. inventory.db    │ ← When online
    └─────────────────────┘
```

**Required Code Changes:**

1. **New module: `inventory_db.py`**
   ```python
   def get_students() -> List[Student]:
       """Load student list from inventory.db"""
   
   def save_c_test_result(result: CTestResult) -> int:
       """Write C-Test result to inventory.db"""
   
   def is_inventory_db_available() -> bool:
       """Check if inventory.db is accessible"""
   ```

2. **Update `db.py`:**
   - Rename `homeworks` table to `c_test_results_local`
   - Add `student_id` column
   - Remove reading/writing/listening scores
   - Add placement_level, sync_status columns
   
3. **New UI flow:**
   - Step 1: Select student (from inventory.db)
   - Step 2: Administer test (display questions, collect answers)
   - Step 3: Grade and display results
   - Step 4: Save to both databases

---

### 4d. Code That Doesn't Belong

**Files to Remove (Reading App Code):**

1. **`watcher.py`** (183 lines)
   - **Why:** Folder watching for continuous homework monitoring
   - **Impact:** GUI (`gui.py`) depends on it - needs refactoring
   - **Depends on:** config (INBOX_FOLDER, POLL_INTERVAL, STUDENT_NAME)
   
2. **`grader.py`** (165 lines)
   - **Why:** Reading/writing homework grading using heuristics
   - **Impact:** GUI uses it for auto-grading - remove calls
   - **Depends on:** extractor (word_count, sentence_count)
   
3. **`generator.py`** (274 lines)
   - **Why:** Generates reading texts and writing prompts
   - **Impact:** GUI has "Generate Next Homework" button - remove
   - **Depends on:** config (GENERATED_FOLDER, STUDENT_NAME), models (GeneratedHomework)

**Files to Partially Remove/Refactor:**

4. **`models.py`** - Remove 2 of 4 classes
   - **Remove:** `Homework`, `GeneratedHomework`
   - **Keep:** `CTestItem`, `CTestSubmission`
   - **Add:** `Student`, `CTestResult` (for inventory.db)
   
5. **`db.py`** - Remove 3 of 6 tables
   - **Remove:** `homeworks`, `generated_homeworks`, `processed_files`
   - **Keep:** `c_test_items`, `c_test_templates`
   - **Redesign:** Replace with `c_test_results_local` (with student_id)
   
6. **`gui.py`** - Complete rewrite needed
   - **Remove:** Entire homework review UI (518 lines)
   - **Replace:** C-Test administration UI
   - **Remove dependencies:** watcher, grader, generator
   
7. **`extractor.py`** - Decision needed
   - **If file-based submission:** Keep for extracting student answers from .docx/.txt
   - **If form-based UI:** Remove entirely (preferred approach)
   
8. **`main.py`** - Update branding
   - **Change:** Title from "10-Minute Reading App" to "C-Test Intake App"
   - **Change:** Initialize C-Test UI, not homework review UI
   
9. **`config.example.py`** - Remove reading app settings
   - **Remove:** INBOX_FOLDER, GENERATED_FOLDER, POLL_INTERVAL, SUPPORTED_EXTENSIONS, STUDENT_NAME
   - **Add:** INVENTORY_DB_PATH, OFFLINE_MODE

**Functions to Remove from `gui.py`:**

- `_start_watcher()`: Starts folder watcher
- `_on_new_file_detected()`: Handles new file from watcher
- `_process_new_file()`: Processes homework files
- `_generate_next_homework()`: Generates homework
- `_open_inbox_folder()`: Opens inbox folder
- `_open_generated_folder()`: Opens generated folder
- All reading/writing score handling

**Total Lines to Remove:** ~1,200 lines of reading app code

---

### 4e. Watcher.py Specifically

**File Analysis:**
- **Location:** `/watcher.py`
- **Size:** 202 lines
- **Purpose:** "Local folder watcher for 10-Minute Reading App (V1)" (line 2)
- **Functionality:** Polls INBOX_FOLDER every POLL_INTERVAL seconds, detects new files, parses filenames, calls callback

**Does Any C-Test Functionality Depend on watcher.py?**

**NO.** The C-Test grading logic is completely independent:
- `c_test_grader.py`: Takes answer key and student answers → returns score (no file watching)
- `c_test_parser.py`: Takes text → extracts answers (no file watching)
- `db.py`: C-Test tables don't use processed_files tracking

**Current Dependencies:**

Only `gui.py` depends on `watcher.py`:
- `from watcher import FolderWatcher` (line 17)
- `self.watcher: Optional[FolderWatcher] = None` (line 28)
- `self._start_watcher()` (line 46)
- `self._on_new_file_detected()` callback (line 219)

**Can watcher.py Be Removed Without Breaking C-Test Grading?**

**YES.** The removal process:

1. **Remove `watcher.py`** completely
2. **Update `gui.py`:**
   - Remove `from watcher import FolderWatcher`
   - Remove `self.watcher` attribute
   - Remove `_start_watcher()` method
   - Remove `_on_new_file_detected()` method
   - Remove "Check Now" button
3. **No impact on:**
   - C-Test grading (`c_test_grader.py`)
   - C-Test parsing (`c_test_parser.py`)
   - C-Test database (`c_test_items`, `c_test_templates`)

**What Is the Actual C-Test Entry Point?**

**Current entry point (WRONG for C-Test):**
```
User drops file → watcher detects → processes → auto-grades → teacher reviews
```

**Proper C-Test entry point should be:**
```
Teacher selects student → UI shows test → student enters answers → submit → grade → save results
```

**Recommended Flow:**

1. **Start app** → `main.py` → `gui.py` (new C-Test UI)
2. **Teacher clicks "New Test"** → Student selection dialog
3. **Select student** → Loads from inventory.db
4. **Click "Start Test"** → Displays C-Test template (text with fragments)
5. **Student enters answers** → Form inputs or text area
6. **Click "Submit"** → Calls `c_test_parser.extract_c_test_answers()`
7. **Grade test** → Calls `c_test_grader.grade_c_test()`
8. **Display results** → Shows score, placement level
9. **Save** → Writes to homework.db AND inventory.db

**No file watching required.**

---

## RECOMMENDATIONS

### Phase 1: Cleanup (Remove Reading App Code)

1. Delete files: `watcher.py`, `grader.py`, `generator.py`
2. Update `models.py`: Remove `Homework`, `GeneratedHomework`
3. Update `db.py`: Remove reading app tables
4. Update `config.example.py`: Remove reading app settings
5. Update `README.md`: Remove all reading app documentation

### Phase 2: Add Student/Class Integration

1. Access zoneb-teacher-assistant repo to get actual inventory.db schema
2. Create `inventory_db.py` module for reading students and writing results
3. Add `Student` model to `models.py`
4. Add student_id to C-Test results schema
5. Implement sync mechanism (local + shared database)

### Phase 3: Rebuild UI

1. Design new C-Test administration UI (wireframe)
2. Implement student selection screen
3. Implement test administration screen (display questions, collect answers)
4. Implement results display screen (score, placement level)
5. Remove old homework review UI from `gui.py`

### Phase 4: Testing

1. Test offline mode (local database only)
2. Test online mode (write to inventory.db)
3. Test sync behavior (offline → online)
4. Test multi-student workflow
5. Integration testing with Zone B portal

---

## APPENDIX: Schema Comparison

### Current (homework.db - WRONG)
```
homeworks
├─ id (PK)
├─ hw_number (unique, but NO student_id!)
├─ file_name, file_path (file-based, not form-based)
├─ reading_score, writing_score, listening_score (not C-Test)
└─ comment

c_test_items
├─ homework_id (FK) ← Links to homework, not student
└─ item grading details
```

### Needed (inventory.db + homework.db)
```
inventory.db:
  students
  ├─ student_id (PK)
  ├─ first_name, last_name
  └─ current_level

  classes
  ├─ class_id (PK)
  └─ class_name

  class_students
  ├─ class_id (FK)
  └─ student_id (FK)

  c_test_results
  ├─ id (PK)
  ├─ student_id (FK) ← Links to student!
  ├─ test_version, test_date
  ├─ num_correct, percentage, score
  └─ placement_level

  c_test_result_items
  ├─ result_id (FK)
  └─ item grading details

homework.db (local copy):
  c_test_results_local (same structure)
  ├─ sync_status: pending/synced/failed
  └─ synced_at timestamp
```

---

## CONCLUSION

The C-Test Intake App repository currently contains a **mixture of two applications**:

1. **C-Test intake/placement tool** (~20% of code)
   - C-Test grading engine ✓
   - C-Test answer parsing ✓
   - C-Test item storage ✓
   
2. **10-Minute Reading App homework tracker** (~80% of code)
   - Folder watching ✗
   - Reading/writing grading ✗
   - Homework generation ✗

**Before integration can begin:**
- Remove all reading app code (~1,200 lines)
- Access Zone B schema to understand student/class structure
- Add student_id to C-Test results
- Build proper C-Test administration UI
- Implement dual-database architecture (local + shared)

**Current state:** The app cannot integrate with NestMind because it has no concept of students, no connection to inventory.db, and is designed for single-student file-based workflow.

**Required effort:** Significant refactoring. Estimate 60-70% of current code needs to be removed or rewritten.

---

**Report End**
