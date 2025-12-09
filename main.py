#!/usr/bin/env python3
"""
10-Minute Reading App (V1)

Entry point for the application.
Run this file to start the GUI.

Usage:
    python main.py
"""

import sys
from pathlib import Path

# Ensure the app directory is in the path
app_dir = Path(__file__).parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))


def main():
    """Main entry point."""
    print("=" * 50)
    print("10-Minute Reading App - V1")
    print("=" * 50)
    
    # Import here to catch any import errors clearly
    try:
        from config import INBOX_FOLDER, GENERATED_FOLDER, STUDENT_NAME
        print(f"Student: {STUDENT_NAME}")
        print(f"Inbox folder: {INBOX_FOLDER}")
        print(f"Generated folder: {GENERATED_FOLDER}")
        print()
    except ImportError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    
    # Check for python-docx
    try:
        import docx
        print("✓ python-docx available")
    except ImportError:
        print("⚠ python-docx not installed - .docx files won't work")
        print("  Install with: pip install python-docx")
        print()
    
    # Initialize database
    try:
        from db import get_db
        db = get_db()
        print("✓ Database initialized")
    except Exception as e:
        print(f"Database error: {e}")
        sys.exit(1)
    
    # Start GUI
    print()
    print("Starting GUI...")
    print("-" * 50)
    
    try:
        from gui import App
        app = App()
        app.run()
    except Exception as e:
        print(f"GUI error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
