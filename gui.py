"""
Tkinter GUI for 10-Minute Reading App (V1).

Simple interface for viewing, scoring, and generating homework.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from pathlib import Path
from typing import Optional
import os

from config import STUDENT_NAME, MIN_SCORE, MAX_SCORE, INBOX_FOLDER, GENERATED_FOLDER
from db import get_db, Database
from models import Homework
from watcher import FolderWatcher
from extractor import extract_text, ExtractionError
from grader import grade_homework, get_score_explanation
from generator import HomeworkGenerator


class App:
    """Main application window."""
    
    def __init__(self):
        self.db = get_db()
        self.watcher: Optional[FolderWatcher] = None
        self.current_homework: Optional[Homework] = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title(f"10-Minute Reading App - {STUDENT_NAME}")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Setup UI
        self._setup_menu()
        self._setup_layout()
        self._setup_status_bar()
        
        # Load data
        self._refresh_homework_list()
        
        # Start watcher
        self._start_watcher()
        
        # Periodic refresh
        self._schedule_refresh()
    
    def _setup_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Refresh", command=self._refresh_homework_list, accelerator="F5")
        file_menu.add_command(label="Open Inbox Folder", command=self._open_inbox_folder)
        file_menu.add_command(label="Open Generated Folder", command=self._open_generated_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        
        # Keyboard shortcuts
        self.root.bind("<F5>", lambda e: self._refresh_homework_list())
    
    def _setup_layout(self):
        """Create the main layout."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create paned window for resizable split
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - homework list
        left_frame = self._create_left_panel(paned)
        paned.add(left_frame, weight=1)
        
        # Right panel - details
        right_frame = self._create_right_panel(paned)
        paned.add(right_frame, weight=2)
    
    def _create_left_panel(self, parent) -> ttk.Frame:
        """Create the left panel with homework list."""
        frame = ttk.Frame(parent, padding="5")
        
        # Header
        header = ttk.Label(frame, text=f"Homework Submissions - {STUDENT_NAME}", font=("TkDefaultFont", 11, "bold"))
        header.pack(fill=tk.X, pady=(0, 10))
        
        # Homework list
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for homework list
        columns = ("hw", "date", "status")
        self.hw_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        self.hw_tree.heading("hw", text="HW#")
        self.hw_tree.heading("date", text="Date")
        self.hw_tree.heading("status", text="Status")
        
        self.hw_tree.column("hw", width=60, anchor="center")
        self.hw_tree.column("date", width=100, anchor="center")
        self.hw_tree.column("status", width=80, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.hw_tree.yview)
        self.hw_tree.configure(yscrollcommand=scrollbar.set)
        
        self.hw_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection
        self.hw_tree.bind("<<TreeviewSelect>>", self._on_homework_selected)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="↻ Refresh", command=self._refresh_homework_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Check Now", command=self._check_for_new_files).pack(side=tk.LEFT, padx=2)
        
        return frame
    
    def _create_right_panel(self, parent) -> ttk.Frame:
        """Create the right panel with details and scoring."""
        frame = ttk.Frame(parent, padding="5")
        
        # Header
        self.detail_header = ttk.Label(frame, text="Select a homework to view details", font=("TkDefaultFont", 11, "bold"))
        self.detail_header.pack(fill=tk.X, pady=(0, 10))
        
        # Text preview
        preview_frame = ttk.LabelFrame(frame, text="Student Response", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.text_preview = scrolledtext.ScrolledText(preview_frame, wrap=tk.WORD, height=10, state=tk.DISABLED)
        self.text_preview.pack(fill=tk.BOTH, expand=True)
        
        # Scoring section
        scoring_frame = ttk.LabelFrame(frame, text="Scores (0-5)", padding="10")
        scoring_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create grid for scores
        score_grid = ttk.Frame(scoring_frame)
        score_grid.pack(fill=tk.X)
        
        # Reading score
        ttk.Label(score_grid, text="Reading:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.reading_var = tk.IntVar(value=0)
        self.reading_spin = ttk.Spinbox(score_grid, from_=MIN_SCORE, to=MAX_SCORE, textvariable=self.reading_var, width=5, state="disabled")
        self.reading_spin.grid(row=0, column=1, padx=5, pady=5)
        
        # Writing score
        ttk.Label(score_grid, text="Writing:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.writing_var = tk.IntVar(value=0)
        self.writing_spin = ttk.Spinbox(score_grid, from_=MIN_SCORE, to=MAX_SCORE, textvariable=self.writing_var, width=5, state="disabled")
        self.writing_spin.grid(row=0, column=3, padx=5, pady=5)
        
        # Listening score (manual entry)
        ttk.Label(score_grid, text="Listening:").grid(row=0, column=4, sticky="e", padx=5, pady=5)
        self.listening_var = tk.IntVar(value=0)
        self.listening_spin = ttk.Spinbox(score_grid, from_=MIN_SCORE, to=MAX_SCORE, textvariable=self.listening_var, width=5, state="disabled")
        self.listening_spin.grid(row=0, column=5, padx=5, pady=5)
        
        # Score explanation
        self.score_info = ttk.Label(scoring_frame, text="", foreground="gray")
        self.score_info.pack(fill=tk.X, pady=(10, 0))
        
        # Comment
        comment_frame = ttk.LabelFrame(frame, text="Teacher Comment", padding="5")
        comment_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.comment_entry = ttk.Entry(comment_frame, state="disabled")
        self.comment_entry.pack(fill=tk.X)
        
        # Action buttons
        action_frame = ttk.Frame(frame)
        action_frame.pack(fill=tk.X)
        
        self.save_btn = ttk.Button(action_frame, text="💾 Save Scores", command=self._save_scores, state="disabled")
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.generate_btn = ttk.Button(action_frame, text="📝 Generate Next Homework", command=self._generate_next_homework)
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        
        return frame
    
    def _setup_status_bar(self):
        """Create the status bar."""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding="2 5")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _start_watcher(self):
        """Start the folder watcher."""
        self.watcher = FolderWatcher(
            folder=INBOX_FOLDER,
            on_new_file=self._on_new_file_detected,
            is_processed=self.db.is_file_processed,
        )
        self.watcher.start()
        self._set_status(f"Watching: {INBOX_FOLDER}")
    
    def _schedule_refresh(self):
        """Schedule periodic list refresh."""
        self._refresh_homework_list()
        self.root.after(10000, self._schedule_refresh)  # Every 10 seconds
    
    def _on_new_file_detected(self, file_path: Path, hw_number: int):
        """Handle new file detection (called from background thread)."""
        # Schedule processing on main thread
        self.root.after(0, lambda: self._process_new_file(file_path, hw_number))
    
    def _process_new_file(self, file_path: Path, hw_number: int):
        """Process a new homework file."""
        self._set_status(f"Processing: {file_path.name}")

        try:
            # Check if already exists
            existing = self.db.get_homework_by_number(hw_number)
            if existing:
                # Ask user what to do
                result = messagebox.askyesnocancel(
                    "Duplicate Homework",
                    f"HW#{hw_number} already exists.\n\n"
                    f"Yes = Replace existing\n"
                    f"No = Skip this file\n"
                    f"Cancel = Do nothing",
                    icon="warning"
                )

                if result is None:  # Cancel
                    self._set_status(f"HW#{hw_number} processing cancelled")
                    return
                elif result is False:  # No (Skip)
                    self._set_status(f"HW#{hw_number} already exists, skipped")
                    return
                else:  # Yes (Replace)
                    self.db.delete_homework(existing.id)
                    self._set_status(f"Replacing existing HW#{hw_number}")

            # Extract text
            try:
                text = extract_text(file_path)
            except ExtractionError as e:
                self._set_status(f"Error: {e}")
                messagebox.showerror("Extraction Error", f"Failed to process {file_path.name}:\n\n{e}")
                return

            # Auto-grade
            reading_score, writing_score = grade_homework(text)

            # Create homework record
            hw = Homework(
                hw_number=hw_number,
                file_name=file_path.name,
                file_path=str(file_path),
                extracted_text=text,
                status="scored",
                reading_score=reading_score,
                writing_score=writing_score,
            )

            # Save to database
            hw.id = self.db.add_homework(hw)

            self._set_status(f"Added HW#{hw_number} (Reading: {reading_score}, Writing: {writing_score})")
            self._refresh_homework_list()

        finally:
            # Always mark as processed, even if errors occurred
            # This prevents repeated processing of problematic files
            self.db.mark_file_processed(str(file_path))
    
    def _refresh_homework_list(self):
        """Refresh the homework list from database."""
        # Clear current items
        for item in self.hw_tree.get_children():
            self.hw_tree.delete(item)
        
        # Load from database
        homeworks = self.db.get_all_homeworks()
        
        for hw in homeworks:
            # submitted_at is always a datetime object or None (guaranteed by db.py)
            if hw.submitted_at:
                date_str = hw.submitted_at.strftime("%Y-%m-%d")
            else:
                date_str = "?"

            self.hw_tree.insert(
                "", tk.END, iid=str(hw.id), values=(
                    f"HW{hw.hw_number:02d}",
                    date_str,
                    hw.status.title(),
                )
            )
    
    def _on_homework_selected(self, event):
        """Handle homework selection."""
        selection = self.hw_tree.selection()
        if not selection:
            self._clear_details()
            return
        
        hw_id = int(selection[0])
        self.current_homework = self.db.get_homework(hw_id)
        
        if self.current_homework:
            self._display_homework()
    
    def _display_homework(self):
        """Display the selected homework details."""
        hw = self.current_homework
        if not hw:
            return
        
        # Update header
        self.detail_header.config(text=f"HW#{hw.hw_number} - {hw.status.title()}")
        
        # Update text preview
        self.text_preview.config(state=tk.NORMAL)
        self.text_preview.delete("1.0", tk.END)
        self.text_preview.insert(tk.END, hw.extracted_text or "(No text extracted)")
        self.text_preview.config(state=tk.DISABLED)
        
        # Update scores
        self.reading_var.set(hw.reading_score or 0)
        self.writing_var.set(hw.writing_score or 0)
        self.listening_var.set(hw.listening_score or 0)
        
        # Enable score inputs
        self.reading_spin.config(state="normal")
        self.writing_spin.config(state="normal")
        self.listening_spin.config(state="normal")
        
        # Update score explanation
        if hw.extracted_text:
            explanation = get_score_explanation(
                hw.reading_score or 0,
                hw.writing_score or 0,
                hw.extracted_text
            )
            self.score_info.config(text=explanation)
        else:
            self.score_info.config(text="")
        
        # Update comment
        self.comment_entry.config(state="normal")
        self.comment_entry.delete(0, tk.END)
        self.comment_entry.insert(0, hw.comment or "")
        
        # Enable save button
        self.save_btn.config(state="normal")
    
    def _clear_details(self):
        """Clear the details panel."""
        self.current_homework = None
        self.detail_header.config(text="Select a homework to view details")
        
        self.text_preview.config(state=tk.NORMAL)
        self.text_preview.delete("1.0", tk.END)
        self.text_preview.config(state=tk.DISABLED)
        
        self.reading_var.set(0)
        self.writing_var.set(0)
        self.listening_var.set(0)
        
        self.reading_spin.config(state="disabled")
        self.writing_spin.config(state="disabled")
        self.listening_spin.config(state="disabled")
        
        self.score_info.config(text="")
        
        self.comment_entry.config(state="normal")
        self.comment_entry.delete(0, tk.END)
        self.comment_entry.config(state="disabled")
        
        self.save_btn.config(state="disabled")
    
    def _save_scores(self):
        """Save the current scores."""
        if not self.current_homework:
            return
        
        hw = self.current_homework
        hw.reading_score = self.reading_var.get()
        hw.writing_score = self.writing_var.get()
        hw.listening_score = self.listening_var.get()
        hw.comment = self.comment_entry.get()
        hw.status = "confirmed"
        
        self.db.update_homework(hw)
        
        self._set_status(f"Saved scores for HW#{hw.hw_number}")
        self._refresh_homework_list()
        
        # Re-select the same homework
        self.hw_tree.selection_set(str(hw.id))
    
    def _generate_next_homework(self):
        """Generate the next homework assignment."""
        next_num = self.db.get_next_hw_number()
        
        # Confirm
        result = messagebox.askyesno(
            "Generate Homework",
            f"Generate homework #{next_num} for {STUDENT_NAME}?"
        )
        
        if not result:
            return
        
        try:
            generator = HomeworkGenerator()
            gen_hw = generator.generate(next_num)
            
            # Save to database
            self.db.add_generated_homework(gen_hw)
            
            self._set_status(f"Generated HW#{next_num}")
            
            messagebox.showinfo(
                "Homework Generated",
                f"Created HW#{next_num}:\n\n"
                f"Reading: {Path(gen_hw.reading_file).name}\n"
                f"Writing: {Path(gen_hw.writing_file).name}\n\n"
                f"Files saved to:\n{GENERATED_FOLDER}"
            )
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate homework:\n{e}")
    
    def _check_for_new_files(self):
        """Manually check for new files."""
        if self.watcher:
            self._set_status("Checking for new files...")
            new_files = self.watcher.check_once()
            if new_files:
                self._set_status(f"Found {len(new_files)} new file(s)")
            else:
                self._set_status("No new files found")
    
    def _open_inbox_folder(self):
        """Open the inbox folder in file explorer."""
        self._open_folder(INBOX_FOLDER)
    
    def _open_generated_folder(self):
        """Open the generated folder in file explorer."""
        self._open_folder(GENERATED_FOLDER)
    
    def _open_folder(self, folder: Path):
        """Open a folder in the system file explorer."""
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        
        if os.name == "nt":  # Windows
            os.startfile(folder)
        elif os.name == "posix":  # macOS/Linux
            import subprocess
            subprocess.run(["xdg-open" if os.uname().sysname == "Linux" else "open", str(folder)])
    
    def _show_about(self):
        """Show the about dialog."""
        messagebox.showinfo(
            "About",
            "10-Minute Reading App\n"
            "Version 1.0\n\n"
            "A simple homework tracking app for English tutoring.\n\n"
            f"Student: {STUDENT_NAME}\n"
            f"Inbox: {INBOX_FOLDER}\n"
            f"Generated: {GENERATED_FOLDER}"
        )
    
    def _set_status(self, message: str):
        """Update the status bar."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_var.set(f"{timestamp} - {message}")
        print(f"[{timestamp}] {message}")
    
    def run(self):
        """Run the application."""
        self.root.mainloop()
        
        # Cleanup
        if self.watcher:
            self.watcher.stop()


def main():
    """Entry point for the GUI."""
    app = App()
    app.run()


if __name__ == "__main__":
    main()
