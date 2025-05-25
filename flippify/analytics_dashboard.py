import tkinter as tk
from tkinter import ttk
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from database import DatabaseManager

class AnalyticsDashboard(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.configure(padding=20)
        ttk.Label(self, text="📊 Analytics Dashboard", font=("Segoe UI", 20, "bold")).pack(pady=(10, 20))

        self.build_summary()
        self.build_filter()

        self.chart_frame = ttk.Frame(self)
        self.chart_frame.pack(fill="both", expand=True)
        self.plot_sales_chart(self.year_var.get())

    def build_summary(self):
        frame = ttk.LabelFrame(self, text="Flip Summary", padding=10)
        frame.pack(fill="x", pady=10)
        data = self.db.fetch_items()
        profits = [(r[0], r[2] - r[1]) for r in data]
        best = max(profits, key=lambda x: x[1], default=("None", 0))
        avg = sum(p[1] for p in profits) / len(profits) if profits else 0

        ttk.Label(frame, text=f"Total Flips: {len(profits)}", font=("Segoe UI", 13)).pack()
        ttk.Label(frame, text=f"Best Flip: {best[0]} (₱{best[1]:.2f})", font=("Segoe UI", 13)).pack()
        ttk.Label(frame, text=f"Average Profit per Flip: ₱{avg:.2f}", font=("Segoe UI", 13)).pack()

    def build_filter(self):
        f = ttk.Frame(self)
        f.pack(pady=10)
        ttk.Label(f, text="Select Year:").pack(side="left", padx=5)
        years = [r[0] for r in self.db.cursor.execute("SELECT DISTINCT strftime('%Y', date) FROM items").fetchall()]
        self.year_var = tk.StringVar(value=years[0] if years else "")
        combo = ttk.Combobox(f, textvariable=self.year_var, values=years, state="readonly")
        combo.pack(side="left")
        combo.bind("<<ComboboxSelected>>", self.update_chart)

    def update_chart(self, _=None):
        for w in self.chart_frame.winfo_children():
            w.destroy()
        self.plot_sales_chart(self.year_var.get())

    def plot_sales_chart(self, year):
        rows = self.db.cursor.execute("SELECT sold_price, date FROM items").fetchall()
        if not rows:
            ttk.Label(self.chart_frame, text="No sales data.").pack()
            return

        monthly_sales = {m: 0 for m in range(1, 13)}
        for price, d in rows:
            try:
                dt = datetime.strptime(d, "%Y-%m-%d")
                if dt.strftime("%Y") == year:
                    monthly_sales[dt.month] += price
            except:
                continue

        labels = [datetime(2000, m, 1).strftime("%b") for m in range(1, 13)]
        values = [monthly_sales[m] for m in range(1, 13)]

        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.bar(labels, values, color="#4CAF50")
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"₱{val:.2f}", ha="center", va="bottom", fontsize=8)
        ax.set_title(f"Monthly Sales in {year}")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
