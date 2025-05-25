import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
from database import DatabaseManager

class ItemTracker(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.name_var = tk.StringVar()
        self.source_var = tk.StringVar()
        self.sold_var = tk.StringVar()
        self.date_var = tk.StringVar()

        self.build_ui()
        self.load_items()

    def build_ui(self):
        ttk.Label(self, text="📦 Item Tracker", font=("Segoe UI", 18)).pack(pady=(10, 20))
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10)

        labels = ["Item Name", "Source Price", "Sold Price", "Date Sold (YYYY-MM-DD)"]
        vars = [self.name_var, self.source_var, self.sold_var, self.date_var]

        for i, (label, var) in enumerate(zip(labels, vars)):
            ttk.Label(form_frame, text=label).grid(row=i*2, column=0, columnspan=2, sticky="w", pady=(0, 2))
            ttk.Entry(form_frame, textvariable=var, width=40).grid(row=i*2+1, column=0, columnspan=2, pady=(0, 10))

        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(button_frame, text="➕ Add Item", command=self.add_item, width=30).pack(pady=2)
        ttk.Button(button_frame, text="📥 Import CSV/Excel", command=self.import_file, width=30).pack(pady=2)
        ttk.Button(button_frame, text="🗑️ Delete All Data", command=self.delete_all_data, width=30).pack(pady=2)

        self.tree = ttk.Treeview(self, columns=("name", "source", "sold", "date"), show="headings", height=10)
        for col, width in zip(["name", "source", "sold", "date"], [200, 100, 100, 150]):
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, anchor="center", width=width)

        self.tree.pack(fill="both", expand=True, pady=10)
        ttk.Button(self, text="❌ Delete Selected", command=self.delete_selected).pack(pady=5)

    def add_item(self):
        try:
            name = self.name_var.get()
            source = float(self.source_var.get())
            sold = float(self.sold_var.get())
            date = self.date_var.get().strip()
            datetime.strptime(date, "%Y-%m-%d")
            self.db.insert_item(name, source, sold, date)
        except Exception:
            messagebox.showerror("Error", "Please enter valid inputs.")
            return

        self.clear_inputs()
        self.load_items()

    def clear_inputs(self):
        for var in (self.name_var, self.source_var, self.sold_var, self.date_var):
            var.set("")

    def load_items(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in self.db.fetch_items():
            self.tree.insert("", "end", values=row)

    def import_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        if not file_path:
            return

        try:
            df = pd.read_csv(file_path) if file_path.endswith(".csv") else pd.read_excel(file_path)

            required_cols = {"name", "source_price", "sold_price", "date"}
            if not required_cols.issubset(df.columns):
                raise Exception("Missing required columns: name, source_price, sold_price, date.")

            added = 0
            skipped = 0
            for _, row in df.iterrows():
                success = self.db.insert_item(
                    row["name"], float(row["source_price"]), float(row["sold_price"]), row["date"]
                )
                if success:
                    added += 1
                else:
                    skipped += 1

            self.load_items()
            messagebox.showinfo("Import Complete", f"Imported {added} new items.\nSkipped {skipped} duplicate(s).")

        except Exception as e:
            messagebox.showerror("Import Failed", str(e))

    def delete_all_data(self):
        if messagebox.askyesno("Confirm", "Delete all items?"):
            self.db.delete_all_items()
            self.load_items()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a row to delete.")
            return
        if messagebox.askyesno("Delete", "Delete selected item(s)?"):
            for item in selected:
                name, source, sold, date = self.tree.item(item, "values")
                self.db.delete_item(name, float(source), float(sold), date)
            self.load_items()
