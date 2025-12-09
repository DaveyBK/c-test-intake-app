"""
Local folder watcher for 10-Minute Reading App (V1).

Polls a local folder for new homework files.
Uses simple polling (no watchdog library needed).
"""

import re
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, List

from config import INBOX_FOLDER, POLL_INTERVAL, SUPPORTED_EXTENSIONS, STUDENT_NAME


class FolderWatcher:
    """
    Watches a local folder for new files.
    
    Uses polling to detect new files matching the expected pattern.
    """
    
    def __init__(
        self,
        folder: Path = INBOX_FOLDER,
        poll_interval: int = POLL_INTERVAL,
        on_new_file: Optional[Callable[[Path, int], None]] = None,
        is_processed: Optional[Callable[[str], bool]] = None,
    ):
        """
        Initialize the watcher.
        
        Args:
            folder: Folder to watch
            poll_interval: Seconds between checks
            on_new_file: Callback(file_path, hw_number) when new file found
            is_processed: Callback(file_path) to check if already processed
        """
        self.folder = Path(folder)
        self.poll_interval = poll_interval
        self.on_new_file = on_new_file
        self.is_processed = is_processed or (lambda x: False)
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_check: Optional[datetime] = None
    
    def start(self) -> None:
        """Start watching in a background thread."""
        if self._running:
            print("Watcher already running")
            return
        
        if not self.folder.exists():
            print(f"Creating inbox folder: {self.folder}")
            self.folder.mkdir(parents=True, exist_ok=True)
        
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        print(f"Started watching: {self.folder}")
    
    def stop(self) -> None:
        """Stop watching."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None
        print("Watcher stopped")
    
    def check_once(self) -> List[tuple]:
        """
        Check for new files once.
        
        Returns:
            List of (file_path, hw_number) tuples for new files
        """
        new_files = []
        
        if not self.folder.exists():
            return new_files
        
        for file_path in self.folder.iterdir():
            if not file_path.is_file():
                continue
            
            # Check extension
            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            
            # Check if already processed
            if self.is_processed(str(file_path)):
                continue
            
            # Try to parse the filename
            parsed = parse_filename(file_path.name)
            if parsed is None:
                print(f"Skipping file (bad format): {file_path.name}")
                continue
            
            hw_number = parsed["hw_number"]
            new_files.append((file_path, hw_number))
            
            # Call callback
            if self.on_new_file:
                try:
                    self.on_new_file(file_path, hw_number)
                except Exception as e:
                    print(f"Error processing {file_path.name}: {e}")
        
        self._last_check = datetime.now()
        return new_files
    
    def _poll_loop(self) -> None:
        """Background polling loop."""
        while self._running:
            try:
                self.check_once()
            except Exception as e:
                print(f"Watcher error: {e}")
            
            # Wait for next check
            for _ in range(self.poll_interval):
                if not self._running:
                    break
                time.sleep(1)
    
    @property
    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self._running
    
    @property
    def last_check_time(self) -> Optional[datetime]:
        """Get time of last check."""
        return self._last_check


def parse_filename(filename: str) -> Optional[dict]:
    """
    Parse a homework filename to extract metadata.

    Expected formats:
        YYYYMMDD_Student1_hwNN.ext  (e.g., 20250115_Student1_hw03.docx)
        Student1_hwNN.ext           (e.g., Student1_hw03.txt)
        hwNN_Student1.ext           (e.g., hw03_Student1.docx)

    Returns:
        Dict with 'date', 'student', 'hw_number' or None if unparseable
    """
    # Remove extension
    name = Path(filename).stem
    student = STUDENT_NAME.lower()
    
    # Pattern 1: YYYYMMDD_Student1_hwNN
    pattern1 = rf"^(\d{{8}})_{student}_hw(\d+)$"
    match = re.match(pattern1, name, re.IGNORECASE)
    if match:
        try:
            date = datetime.strptime(match.group(1), "%Y%m%d")
            return {
                "date": date,
                "student": STUDENT_NAME,
                "hw_number": int(match.group(2)),
            }
        except ValueError:
            pass
    
    # Pattern 2: Student1_hwNN
    pattern2 = rf"^{student}_hw(\d+)$"
    match = re.match(pattern2, name, re.IGNORECASE)
    if match:
        return {
            "date": datetime.now(),
            "student": STUDENT_NAME,
            "hw_number": int(match.group(1)),
        }
    
    # Pattern 3: hwNN_Student1
    pattern3 = rf"^hw(\d+)_{student}$"
    match = re.match(pattern3, name, re.IGNORECASE)
    if match:
        return {
            "date": datetime.now(),
            "student": STUDENT_NAME,
            "hw_number": int(match.group(1)),
        }
    
    # Pattern 4: Just hwNN (assume it's the configured student's)
    pattern4 = r"^hw(\d+)$"
    match = re.match(pattern4, name, re.IGNORECASE)
    if match:
        return {
            "date": datetime.now(),
            "student": STUDENT_NAME,
            "hw_number": int(match.group(1)),
        }
    
    return None
