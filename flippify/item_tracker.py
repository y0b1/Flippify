import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import DatabaseManager

class ItemTracker(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.configure(padding=20)
        self.build_ui()

    def build_ui(self):
        ttk.Label(self, text="📦 Item Tracker", font=("Segoe UI", 20, "bold")).pack(pady=(10, 20))

        form = ttk.LabelFrame(self, text="Add New Item", padding=15)
        form.pack(fill="x", padx=10, pady=10)

        self.name_var = tk.StringVar()
        self.source_var = tk.StringVar()
        self.sold_var = tk.StringVar()
        self.date_var = tk.StringVar(value=datetime.today().strftime("%Y-%m-%d"))

        fields = [
            ("Item Name", self.name_var),
            ("Source Price (₱)", self.source_var),
            ("Sold Price (₱)", self.sold_var),
            ("Date (YYYY-MM-DD)", self.date_var),
        ]

        for label, var in fields:
            row = ttk.Frame(form)
            row.pack(pady=5)
            ttk.Label(row, text=label, width=20).pack(side="left")
            ttk.Entry(row, textvariable=var, width=25).pack(side="left")



        button_frame = ttk.Frame(form)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="➕ Add Item", command=self.add_item, width=20).pack(side="left", padx=5)
        ttk.Button(button_frame, text="🧹 Clear", command=self.clear_form, width=10).pack(side="left", padx=5)

        self.list_frame = ttk.LabelFrame(self, text="Sold Inventory", padding=10)
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.load_items()

    def add_item(self):
        name = self.name_var.get().strip()
        source_price = self.source_var.get().strip()
        sold_price = self.sold_var.get().strip()
        date = self.date_var.get().strip()

        try:
            source = float(source_price)
            sold = float(sold_price) if sold_price else 0.0
        except ValueError:
            messagebox.showerror("Error", "Prices must be valid numbers.")
            return

        if not name or not date:
            messagebox.showerror("Error", "Name and Date are required.")
            return

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format.")
            return

        self.db.insert_item(name, source, sold, date)
        self.load_items()
        self.clear_form()

    def clear_form(self):
        self.name_var.set("")
        self.source_var.set("")
        self.sold_var.set("")
        self.date_var.set(datetime.today().strftime("%Y-%m-%d"))

    def load_items(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        data = self.db.fetch_items()
        if not data:
            ttk.Label(self.list_frame, text="No items in inventory.").pack()
            return

        tree = ttk.Treeview(self.list_frame, columns=("Name", "Source", "Sold", "Date"), show="headings")
        tree.heading("Name", text="Item Name")
        tree.heading("Source", text="Source Price")
        tree.heading("Sold", text="Sold Price")
        tree.heading("Date", text="Date")

        for row in data:
            tree.insert("", "end", values=row)

        tree.pack(fill="both", expand=True)
