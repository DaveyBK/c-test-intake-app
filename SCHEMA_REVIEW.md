# Schema Review - inventory.db C-Test Tables

## ⚠️ IMPORTANT - Read Before Running

This document contains the **exact SQL schemas** that will be added to your shared `inventory.db` database. Review carefully before initializing.

---

## Questions Answered

### 1. Are the 50 tests existing or new?

**EXISTING TESTS** - They were already in the repository before my changes.

- `test_c_test_grader.py` - 17 tests (existing)
- `test_c_test_parser.py` - 33 tests (existing)

**What this means:** The tests confirm that my schema changes (switching from INTEGER to TEXT student_id) **did not break the core C-Test grading and parsing logic**. These are the original tests, so passing them validates backward compatibility.

### 2. Does it use CREATE TABLE IF NOT EXISTS?

**YES** ✅ - All table creation is safe:

```sql
CREATE TABLE IF NOT EXISTS c_test_results (...)
CREATE TABLE IF NOT EXISTS c_test_result_items (...)
CREATE INDEX IF NOT EXISTS idx_c_test_student (...)
CREATE INDEX IF NOT EXISTS idx_c_test_date (...)
```

**What this means:** 
- Safe to run `initialize_c_test_tables()` multiple times
- Won't fail if tables already exist
- Won't overwrite existing data
- Idempotent operation

### 3. What exactly gets added to inventory.db?

Two tables and two indexes (detailed below).

---

## Table Schemas to be Added to inventory.db

### Table 1: `c_test_results`

**Purpose:** Main C-Test results (one row per test taken)

```sql
CREATE TABLE IF NOT EXISTS c_test_results (
    result_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id      TEXT NOT NULL,
    test_version    TEXT NOT NULL,
    test_date       TEXT NOT NULL,
    num_items       INTEGER NOT NULL,
    num_correct     INTEGER NOT NULL,
    percentage      REAL NOT NULL,
    score           INTEGER NOT NULL,
    placement_level TEXT,
    completed       INTEGER DEFAULT 1,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);
```

**Column Details:**

| Column | Type | Constraints | Description | Example |
|--------|------|-------------|-------------|---------|
| `result_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique test result ID | 1, 2, 3... |
| `student_id` | TEXT | NOT NULL, FOREIGN KEY | Links to students.student_id | '20231107' |
| `test_version` | TEXT | NOT NULL | Test version/form | 'A', 'B', 'Form1' |
| `test_date` | TEXT | NOT NULL | When test was taken | '2024-01-15 14:30:00' |
| `num_items` | INTEGER | NOT NULL | Total questions in test | 20, 40, 50 |
| `num_correct` | INTEGER | NOT NULL | Number answered correctly | 15, 35, 48 |
| `percentage` | REAL | NOT NULL | Percentage score | 75.0, 87.5, 96.0 |
| `score` | INTEGER | NOT NULL | Placement score (0-5 scale) | 0, 1, 2, 3, 4, 5 |
| `placement_level` | TEXT | nullable | Recommended level | 'Advanced', 'Intermediate' |
| `completed` | INTEGER | DEFAULT 1 | Test completion flag (1=yes, 0=no) | 1 |
| `created_at` | TEXT | DEFAULT CURRENT_TIMESTAMP | Record creation time | '2024-01-15 14:35:12' |

**Foreign Key:**
- `student_id` → `students(student_id)` with `ON DELETE CASCADE`
- If student is deleted, their C-Test results are also deleted

**Compatibility with existing schema:**
- Uses TEXT for student_id (matches your students table)
- Uses TEXT for dates (matches your existing convention)
- Uses INTEGER for boolean flags (matches SQLite best practice)

---

### Table 2: `c_test_result_items`

**Purpose:** Item-level details (one row per question answered)

```sql
CREATE TABLE IF NOT EXISTS c_test_result_items (
    item_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id       INTEGER NOT NULL,
    item_number     INTEGER NOT NULL,
    correct_word    TEXT NOT NULL,
    student_answer  TEXT,
    is_correct      INTEGER NOT NULL,
    FOREIGN KEY (result_id) REFERENCES c_test_results(result_id) ON DELETE CASCADE
);
```

**Column Details:**

| Column | Type | Constraints | Description | Example |
|--------|------|-------------|-------------|---------|
| `item_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique item record ID | 1, 2, 3... |
| `result_id` | INTEGER | NOT NULL, FOREIGN KEY | Links to c_test_results | 1, 2, 3... |
| `item_number` | INTEGER | NOT NULL | Question number in test | 1, 2, 3...20 |
| `correct_word` | TEXT | NOT NULL | The correct answer | 'weather', 'yesterday' |
| `student_answer` | TEXT | nullable | What student wrote | 'weather', 'yesterady' (typo) |
| `is_correct` | INTEGER | NOT NULL | Correct flag (1=yes, 0=no) | 1 or 0 |

**Foreign Key:**
- `result_id` → `c_test_results(result_id)` with `ON DELETE CASCADE`
- If a test result is deleted, all its item details are also deleted

**Example data:**
```
result_id=1, item_number=1, correct_word='weather', student_answer='weather', is_correct=1
result_id=1, item_number=2, correct_word='cold', student_answer='cold', is_correct=1
result_id=1, item_number=3, correct_word='yesterday', student_answer='yesterady', is_correct=0
```

---

### Indexes Created

**Index 1: Student lookup**
```sql
CREATE INDEX IF NOT EXISTS idx_c_test_student 
ON c_test_results(student_id);
```
- Speeds up queries like: "Get all tests for student '20231107'"
- Essential for student history views

**Index 2: Date-based queries**
```sql
CREATE INDEX IF NOT EXISTS idx_c_test_date 
ON c_test_results(test_date);
```
- Speeds up queries like: "Get all tests from January 2024"
- Useful for reporting and analytics

---

## Schema Compatibility Check

### ✅ Matches existing inventory.db conventions:

1. **TEXT student_id** - Matches `students` table
2. **TEXT dates** - Matches existing date storage (not DATETIME)
3. **INTEGER booleans** - Matches SQLite convention (0/1 not TRUE/FALSE)
4. **AUTOINCREMENT PKs** - Matches existing tables like `attendance`
5. **Foreign key constraints** - Follows your existing pattern with `ON DELETE CASCADE`
6. **created_at timestamps** - Matches existing `admin_logs`, `items` tables

### ✅ Naming conventions:

- Uses underscores (not camelCase): `result_id`, `student_id`, `created_at`
- Uses descriptive names: `c_test_results` (not just `results`)
- Prefixes C-Test tables: `c_test_*` to avoid naming conflicts

### ✅ No conflicts:

- Table names don't exist in your schema (verified against 12 existing tables)
- Column names follow your existing patterns
- No overlap with reserved SQLite keywords

---

## Relationship Diagram

```
students (existing)
    |
    | student_id (TEXT)
    |
    ▼
c_test_results (NEW)
    |
    | result_id (INTEGER)
    |
    ▼
c_test_result_items (NEW)
```

**Cascade behavior:**
- Delete student → Deletes all their C-Test results → Deletes all item details
- Delete test result → Deletes all its item details
- No orphaned records possible

---

## Safety Checklist

Before running `initialize_c_test_tables()`:

- [ ] **Backup inventory.db** 
  ```bash
  cp inventory.db inventory.db.backup.$(date +%Y%m%d_%H%M%S)
  ```

- [ ] **Verify path** - Check config.py points to correct inventory.db

- [ ] **Test on copy** - Run on a copy first if you want to be extra safe:
  ```python
  from inventory_db import InventoryDatabase
  test_db = InventoryDatabase("/tmp/inventory_test.db")
  test_db.initialize_c_test_tables()
  ```

- [ ] **Review schema** - Make sure table structure fits your needs

- [ ] **Check permissions** - Ensure write access to inventory.db

---

## What initialize_c_test_tables() Does

```python
def initialize_c_test_tables(self) -> bool:
    """
    Create C-Test tables in inventory.db if they don't exist.
    
    Returns:
        True if successful, False otherwise
    """
    if not self.is_available():
        return False
    
    try:
        with self._connect() as conn:
            conn.executescript(CREATE_C_TEST_TABLES)
        print("✓ C-Test tables initialized in inventory.db")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize C-Test tables: {e}")
        return False
```

**What it does:**
1. Checks if inventory.db is available
2. Creates tables **only if they don't exist**
3. Creates indexes **only if they don't exist**
4. Returns True/False for success/failure
5. Prints status message

**What it does NOT do:**
- Does NOT drop existing tables
- Does NOT modify existing data
- Does NOT change schema if tables exist
- Does NOT fail if tables already exist

---

## Sample Data After Running

After adding a test for student '20231107' (Bella), your database would contain:

**c_test_results:**
```
result_id | student_id | test_version | test_date           | num_items | num_correct | percentage | score | placement_level
----------|------------|--------------|---------------------|-----------|-------------|------------|-------|----------------
1         | 20231107   | A            | 2024-01-15 14:30:00 | 20        | 18          | 90.0       | 5     | Advanced
```

**c_test_result_items:**
```
item_id | result_id | item_number | correct_word | student_answer | is_correct
--------|-----------|-------------|--------------|----------------|------------
1       | 1         | 1           | weather      | weather        | 1
2       | 1         | 2           | cold         | cold           | 1
3       | 1         | 3           | yesterday    | yesterday      | 1
...     | ...       | ...         | ...          | ...            | ...
20      | 1         | 20          | late         | late           | 1
```

---

## Migration Path (if needed later)

If you need to change the schema later:

1. **Add columns:** Use `ALTER TABLE ADD COLUMN` (SQLite supports this)
2. **Rename columns:** Create new table, copy data, drop old (standard SQLite migration)
3. **Change types:** Would require migration (create new, copy, drop old)

**Recommendation:** Get the schema right now, as you mentioned!

---

## Verification Queries

After initializing, verify with these queries:

```sql
-- Check table exists
SELECT name FROM sqlite_master WHERE type='table' AND name='c_test_results';

-- Check columns
PRAGMA table_info(c_test_results);

-- Check foreign keys
PRAGMA foreign_key_list(c_test_results);

-- Check indexes
SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='c_test_results';

-- Test query
SELECT COUNT(*) FROM c_test_results;
```

---

## Summary

**Tables to add:** 2
- `c_test_results` (main results)
- `c_test_result_items` (detailed answers)

**Indexes to add:** 2
- `idx_c_test_student` (for student lookups)
- `idx_c_test_date` (for date filtering)

**Safety:** ✅ All use `IF NOT EXISTS`
**Compatibility:** ✅ Matches your existing schema conventions
**Testing:** ✅ 50 existing C-Test tests pass (grading logic intact)

**Ready to proceed?** Review this document, backup inventory.db, then run:
```python
from inventory_db import get_inventory_db
inventory = get_inventory_db()
inventory.initialize_c_test_tables()
```
