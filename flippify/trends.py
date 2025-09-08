import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import sqlite3
from database import DatabaseManager

class TrendsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.configure(padding=0)
        self.build_modern_ui()

    def build_modern_ui(self):
        # Header section
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 30))

        title_label = ttk.Label(
            header_frame,
            text="📦 Trends",
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(anchor="w")

        subtitle_label = ttk.Label(
            header_frame,
            text="Track your flipping inventory and sales",
            font=("Segoe UI", 12),
            foreground="#888888"
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # Main content container
        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True)


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Flippify - Trends")
    root.geometry("1200x700")

    # Configure the style
    style = ttk.Style()
    style.theme_use('clam')

    app = TrendsTab(root)
    app.pack(fill="both", expand=True, padx=20, pady=20)

    root.mainloop()