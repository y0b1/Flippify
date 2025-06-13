import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from database import DatabaseManager
from docx import Document
from docx.shared import Inches
import os

class ProfitReportTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.configure(padding=20)

        ttk.Label(self, text="📄 Profit Report", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(10, 10))

        # Filter selection
        filter_frame = ttk.Frame(self)
        filter_frame.pack(anchor="w", pady=(0, 10))

        ttk.Label(filter_frame, text="Report Type:", font=("Segoe UI", 11)).pack(side="left", padx=(0, 10))

        self.report_type = tk.StringVar(value="Day")
        report_options = ["Day", "Week", "Month", "Year"]
        dropdown = ttk.Combobox(filter_frame, textvariable=self.report_type, values=report_options, state="readonly", width=10)
        dropdown.pack(side="left")
        dropdown.bind("<<ComboboxSelected>>", self.update_report)

        ttk.Label(filter_frame, text="Select Date (YYYY-MM-DD):", font=("Segoe UI", 11)).pack(side="left", padx=(20, 10))
        self.date_entry = ttk.Entry(filter_frame, width=15)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.date_entry.pack(side="left")

        export_btn = ttk.Button(filter_frame, text="📝 Export to Word", command=self.export_to_word)
        export_btn.pack(side="right")

        self.report_frame = ttk.LabelFrame(self, text="Report Summary", padding=15)
        self.report_frame.pack(fill="both", expand=True)

        self.filtered_items = []
        self.update_report()

    def update_report(self, event=None):
        for widget in self.report_frame.winfo_children():
            widget.destroy()

        try:
            selected_date = datetime.strptime(self.date_entry.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter a valid date in YYYY-MM-DD format.")
            return

        report_type = self.report_type.get()

        if report_type == "Day":
            start_date = selected_date
        elif report_type == "Week":
            start_date = selected_date - timedelta(days=selected_date.weekday())
        elif report_type == "Month":
            start_date = selected_date.replace(day=1)
        elif report_type == "Year":
            start_date = selected_date.replace(month=1, day=1)

        self.filtered_items = []
        total_cost = total_revenue = profit = sold_count = 0

        for name, source, sold, date_str in self.db.fetch_items():
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                if sold > 0 and date_obj >= start_date:
                    self.filtered_items.append((name, source, sold, date_str))
                    total_cost += source
                    total_revenue += sold
                    profit += (sold - source)
                    sold_count += 1
            except:
                continue

        lines = [
            f"🗓️ Period: {report_type} starting {start_date.strftime('%Y-%m-%d')}",
            f"📦 Items Sold: {sold_count}",
            f"💸 Total Revenue: ₱{total_revenue:,.2f}",
            f"💰 Total Cost: ₱{total_cost:,.2f}",
            f"📈 Net Profit: ₱{profit:,.2f}",
            f"📊 Profit Margin: {((profit / total_revenue) * 100):.1f}%" if total_revenue else "📊 Profit Margin: N/A"
        ]

        for line in lines:
            ttk.Label(self.report_frame, text=line, font=("Segoe UI", 12)).pack(anchor="w", pady=2)

    def export_to_word(self):
        if not self.filtered_items:
            messagebox.showwarning("No Data", "There is no data to export for the selected period.")
            return

        document = Document()
        document.add_heading('Profit Report', 0)

        report_type = self.report_type.get()
        try:
            selected_date = datetime.strptime(self.date_entry.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter a valid date in YYYY-MM-DD format.")
            return

        document.add_paragraph(f'Report Type: {report_type}')
        document.add_paragraph(f'Starting Date: {selected_date.strftime("%Y-%m-%d")}')
        document.add_paragraph('')

        table = document.add_table(rows=1, cols=5)
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Item Name'
        hdr_cells[1].text = 'Source Price'
        hdr_cells[2].text = 'Sold Price'
        hdr_cells[3].text = 'Profit'
        hdr_cells[4].text = 'Date'

        total_profit = 0
        for name, source, sold, date in self.filtered_items:
            profit = sold - source
            total_profit += profit
            row_cells = table.add_row().cells
            row_cells[0].text = name
            row_cells[1].text = f"₱{source:.2f}"
            row_cells[2].text = f"₱{sold:.2f}"
            row_cells[3].text = f"₱{profit:.2f}"
            row_cells[4].text = date

        document.add_paragraph('')
        document.add_paragraph(f'Total Net Profit: ₱{total_profit:,.2f}')

        save_path = os.path.join(os.getcwd(), f"Profit_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx")
        document.save(save_path)

        messagebox.showinfo("Exported", f"Profit report has been saved to:\n{save_path}")
