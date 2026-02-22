#!/usr/bin/env python3
"""
Test script to demonstrate C-Test integration with inventory.db schema.

This script shows:
1. Creating students matching inventory.db schema
2. Grading a C-Test
3. Saving results to local database
4. How to integrate with inventory.db once available
"""

import json
from datetime import datetime
from pathlib import Path

# Import C-Test modules
from models import Student, CTestResult, CTestItem
from c_test_grader import grade_c_test
from c_test_parser import extract_c_test_answers
from db import get_db
from config import PLACEMENT_LEVELS


def demo_student_schema():
    """Demonstrate the student schema matching inventory.db."""
    print("=" * 70)
    print("DEMO: Student Schema (matches inventory.db)")
    print("=" * 70)
    
    # Create a student matching the actual schema
    student = Student(
        student_id="20231107",  # TEXT primary key
        first_name="Bella",
        last_name="Smith",
        level="SM4",
        status="active",
        qr_code="QR123456"
    )
    
    print(f"\nStudent ID: {student.student_id} (TEXT)")
    print(f"Name: {student.full_name}")
    print(f"Level: {student.level}")
    print(f"Status: {student.status}")
    print(f"QR Code: {student.qr_code}")
    print()


def demo_c_test_grading():
    """Demonstrate C-Test grading."""
    print("=" * 70)
    print("DEMO: C-Test Grading")
    print("=" * 70)
    
    # Answer key for a sample C-Test
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
    
    # Simulate student submission
    student_text = """
    1. weather
    2. cold
    3. yesterday
    4. morning
    5. walked
    6. school
    7. because
    8. late
    """
    
    print("\nAnswer Key:", json.dumps(answer_key, indent=2))
    print("\nStudent Submission:")
    print(student_text)
    
    # Parse student answers
    student_answers = extract_c_test_answers(student_text, num_items=8)
    print("\nParsed Answers:", json.dumps(student_answers, indent=2))
    
    # Grade the test
    score, items, feedback = grade_c_test(answer_key, student_answers, accept_variants=True)
    
    print("\n" + "=" * 70)
    print("GRADING RESULTS")
    print("=" * 70)
    print(f"\nScore: {score}/5")
    print(f"Placement Level: {PLACEMENT_LEVELS.get(score, 'Unknown')}")
    print(f"\nDetailed Feedback:\n{feedback}")
    
    return score, items


def demo_save_to_local_db():
    """Demonstrate saving results to local database."""
    print("\n" + "=" * 70)
    print("DEMO: Save to Local Database")
    print("=" * 70)
    
    # Create a student
    student = Student(
        student_id="20231107",
        first_name="Bella",
        last_name="Smith",
        level="SM4",
        status="active"
    )
    
    # Grade a test (reusing from previous demo)
    answer_key = {1: "test", 2: "example", 3: "answer"}
    student_answers = {1: "test", 2: "example", 3: "answer"}
    score, items, feedback = grade_c_test(answer_key, student_answers)
    
    # Create result object
    result = CTestResult(
        student_id=student.student_id,  # TEXT
        test_version="A",
        test_date=datetime.now(),
        num_items=len(answer_key),
        num_correct=score,
        percentage=100.0,
        score=5,
        placement_level=PLACEMENT_LEVELS.get(5),
        items=items,
        completed=True,
        synced_to_inventory=False
    )
    
    # Save to local database
    db = get_db()
    result_id = db.add_c_test_result(result)
    
    print(f"\n✓ Saved to local database with ID: {result_id}")
    print(f"  Student ID: {result.student_id} (TEXT)")
    print(f"  Score: {result.score}/5")
    print(f"  Placement: {result.placement_level}")
    
    # Retrieve and verify
    retrieved = db.get_c_test_result(result_id)
    print(f"\n✓ Retrieved from database:")
    print(f"  Student ID: {retrieved.student_id}")
    print(f"  Items graded: {len(retrieved.items)}")
    print(f"  Synced to inventory: {retrieved.synced_to_inventory}")
    
    # Cache the student
    db.cache_student(student)
    print(f"\n✓ Student cached locally")
    
    # Get student results
    student_results = db.get_student_results(student.student_id)
    print(f"\n✓ Found {len(student_results)} result(s) for student {student.student_id}")
    
    return result_id


def demo_inventory_integration():
    """Demonstrate inventory.db integration (when available)."""
    print("\n" + "=" * 70)
    print("DEMO: Inventory.db Integration")
    print("=" * 70)
    
    from inventory_db import get_inventory_db
    
    inventory = get_inventory_db()
    
    print(f"\nInventory DB Available: {inventory.is_available()}")
    print(f"DB Path: {inventory.db_path}")
    
    if inventory.is_available():
        print("\n✓ Connected to inventory.db")
        
        # Initialize C-Test tables
        if inventory.initialize_c_test_tables():
            print("✓ C-Test tables created/verified in inventory.db")
        
        # Get students
        students = inventory.get_students(status='active')
        print(f"\n✓ Found {len(students)} active students")
        
        if students:
            student = students[0]
            print(f"\nSample Student:")
            print(f"  ID: {student.student_id} (TEXT)")
            print(f"  Name: {student.full_name}")
            print(f"  Level: {student.level}")
            print(f"  Status: {student.status}")
            
            # Get test history
            history = inventory.get_student_c_test_history(student.student_id)
            print(f"\n✓ C-Test history: {len(history)} test(s)")
            
            for test in history:
                print(f"  - {test['date']}: Score {test['score']}/5, Level: {test['level']}")
    else:
        print("\n⚠ Inventory database not configured/available")
        print("\nTo enable:")
        print("  1. Set INVENTORY_DB_PATH in config.py")
        print("  2. Point it to your actual inventory.db")
        print("  3. Run: inventory.initialize_c_test_tables()")
        print("\nExample config.py:")
        print("  INVENTORY_DB_PATH = '/path/to/inventory.db'")
        print("  OFFLINE_MODE = False")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("C-TEST INTEGRATION DEMONSTRATION")
    print("=" * 70)
    print("\nThis script demonstrates:")
    print("  1. Student schema matching inventory.db")
    print("  2. C-Test grading engine")
    print("  3. Local database storage")
    print("  4. Inventory.db integration (when available)")
    print()
    
    try:
        demo_student_schema()
        demo_c_test_grading()
        demo_save_to_local_db()
        demo_inventory_integration()
        
        print("\n" + "=" * 70)
        print("✓ ALL DEMONSTRATIONS COMPLETE")
        print("=" * 70)
        print("\nNext Steps:")
        print("  1. Set INVENTORY_DB_PATH in config.py")
        print("  2. Run this script again to test full integration")
        print("  3. Build the C-Test administration UI")
        print()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
