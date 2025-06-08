import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import DatabaseManager

class InventoryTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.configure(padding=20)
        ttk.Label(self, text="📦 Inventory (Unsold Items)", font=("Segoe UI", 20, "bold")).pack(pady=(10, 20))
        self.build_inventory_list()

    def build_inventory_list(self):
        for widget in self.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                widget.destroy()

        data = self.db.fetch_items()
        unsold_items = [item for item in data if item[2] == 0.0]  # sold_price == 0

        frame = ttk.LabelFrame(self, text="Unsold Items", padding=10)
        frame.pack(fill="both", expand=True)

        if not unsold_items:
            ttk.Label(frame, text="No unsold items.").pack()
            return

        for item in unsold_items:
            row = ttk.Frame(frame)
            row.pack(fill="x", pady=5)
            name, source, sold, date = item
            ttk.Label(row, text=f"{name} | ₱{source:.2f} | {date}", anchor="w").pack(side="left", expand=True)
            ttk.Button(row, text="Sold", command=lambda i=item: self.open_sold_popup(i)).pack(side="right")

    def open_sold_popup(self, item):
        popup = tk.Toplevel(self)
        popup.title("Mark as Sold")
        popup.geometry("300x180")
        popup.transient(self)

        ttk.Label(popup, text=f"Item: {item[0]}", font=("Segoe UI", 12)).pack(pady=10)

        sold_price_var = tk.StringVar()
        sold_date_var = tk.StringVar(value=datetime.today().strftime("%Y-%m-%d"))

        ttk.Label(popup, text="Sold Price (₱):").pack()
        ttk.Entry(popup, textvariable=sold_price_var).pack()

        ttk.Label(popup, text="Date Sold (YYYY-MM-DD):").pack(pady=(10, 0))
        ttk.Entry(popup, textvariable=sold_date_var).pack()

        def save_sold():
            try:
                sold_price = float(sold_price_var.get())
                sold_date = sold_date_var.get()
                datetime.strptime(sold_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid sold price or date.")
                return

            self.db.delete_item(*item)
            self.db.insert_item(item[0], item[1], sold_price, sold_date)
            popup.destroy()
            self.build_inventory_list()

        ttk.Button(popup, text="✅ Mark as Sold", command=save_sold).pack(pady=10)
