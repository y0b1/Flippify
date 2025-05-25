from tkinter import ttk
from database import DatabaseManager

class ProfitLogs(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        ttk.Label(self, text="💵 Profit & Expense Logs", font=("Segoe UI", 20, "bold")).pack(pady=(20, 10))
        self.build_summary()

    def build_summary(self):
        frame = ttk.LabelFrame(self, text="Financial Summary", padding=20)
        frame.pack(fill="x", padx=40, pady=10)

        data = self.db.fetch_items()
        total_cost = sum(row[1] for row in data)
        total_income = sum(row[2] for row in data)
        net = total_income - total_cost

        ttk.Label(frame, text=f"Total Spent: ₱{total_cost:.2f}", font=("Segoe UI", 14)).pack(pady=5)
        ttk.Label(frame, text=f"Total Income: ₱{total_income:.2f}", font=("Segoe UI", 14)).pack(pady=5)
        ttk.Label(frame, text=f"Net Profit: ₱{net:.2f}", font=("Segoe UI", 14), foreground="green" if net >= 0 else "red").pack(pady=5)
