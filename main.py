#!/usr/bin/env python3
"""
C-Test Intake App

Entry point for the C-Test placement and intake application.
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
    print("C-Test Intake App")
    print("=" * 50)
    
    # Import here to catch any import errors clearly
    try:
        from config import DB_PATH, INVENTORY_DB_PATH, OFFLINE_MODE
        print(f"Local database: {DB_PATH}")
        if INVENTORY_DB_PATH and not OFFLINE_MODE:
            print(f"Inventory database: {INVENTORY_DB_PATH}")
        else:
            print("Mode: Offline (local database only)")
        print()
    except ImportError as e:
        print(f"Configuration error: {e}")
        print("Please create config.py from config.example.py")
        sys.exit(1)
    
    # Initialize database
    try:
        from db import get_db
        db = get_db()
        print("✓ Local database initialized")
    except Exception as e:
        print(f"Database error: {e}")
        sys.exit(1)
    
    # Check inventory database connection
    try:
        from inventory_db import get_inventory_db
        inventory = get_inventory_db()
        if inventory.is_available():
            print("✓ Inventory database connected")
        else:
            print("⚠ Inventory database not available (offline mode)")
    except Exception as e:
        print(f"⚠ Inventory database connection failed: {e}")
    
    # Start GUI
    print()
    print("Starting C-Test administration interface...")
    print("-" * 50)
    
    try:
        # TODO: Replace with C-Test GUI when ready
        print("GUI not yet implemented - C-Test core is ready")
        print("\nAvailable modules:")
        print("  - c_test_grader: Grading engine")
        print("  - c_test_parser: Answer parsing")
        print("  - db: Local database")
        print("  - inventory_db: Shared database integration")
        print("\nTo use programmatically, see GAP_ANALYSIS_REPORT.md")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
