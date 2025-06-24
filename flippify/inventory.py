import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import DatabaseManager


class InventoryTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.pack(fill="both", expand=True)

        # Header section with title and search
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=20, pady=(20, 0))

        # Title and search in same row
        title_search_frame = ttk.Frame(header_frame)
        title_search_frame.pack(fill="x", pady=(0, 20))

        ttk.Label(title_search_frame, text="📦 Inventory", font=("Segoe UI", 20, "bold")).pack(side="left")

        # Search box on the right side
        search_container = ttk.Frame(title_search_frame)
        search_container.pack(side="right")

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search)
        search_entry = ttk.Entry(search_container, textvariable=self.search_var,
                                 font=("Segoe UI", 10), width=25)
        search_entry.pack(side="right", padx=(10, 0))
        search_entry.insert(0, "🔍 Search items...")
        search_entry.bind("<FocusIn>", self.on_search_focus_in)
        search_entry.bind("<FocusOut>", self.on_search_focus_out)
        self.search_entry = search_entry

        self.build_inventory_list()

    def on_search_focus_in(self, event):
        """Clear placeholder text when search box is focused"""
        if self.search_entry.get() == "🔍 Search items...":
            self.search_entry.delete(0, tk.END)

    def on_search_focus_out(self, event):
        """Restore placeholder text if search box is empty"""
        if not self.search_entry.get():
            self.search_entry.insert(0, "🔍 Search items...")

    def on_search(self, *args):
        """Called when search text changes"""
        if self.search_var.get() != "🔍 Search items...":
            self.build_inventory_list()

    def build_inventory_list(self):
        # Remove existing inventory frame
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Frame) and widget != self.winfo_children()[0]:  # Keep header frame
                widget.destroy()

        data = self.db.fetch_items()
        unsold_items = [item for item in data if item[2] == 0.0]  # sold_price == 0

        # Filter items based on search text
        search_text = self.search_var.get().lower()
        if search_text and search_text != "🔍 search items...":
            unsold_items = [item for item in unsold_items if search_text in item[0].lower()]

        # Main content area
        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        if not unsold_items:
            empty_frame = ttk.Frame(content_frame)
            empty_frame.pack(expand=True)
            if search_text and search_text != "🔍 search items...":
                ttk.Label(empty_frame, text=f"No items found matching '{search_text}'",
                          font=("Segoe UI", 12), foreground="gray").pack(pady=50)
            else:
                ttk.Label(empty_frame, text="No unsold items in inventory",
                          font=("Segoe UI", 12), foreground="gray").pack(pady=50)
            return

        # Items list with cleaner styling
        for i, item in enumerate(unsold_items):
            row = ttk.Frame(content_frame)
            row.pack(fill="x", pady=2)

            name, source, sold, date = item

            # Item info
            info_text = f"{name} • ₱{source:.2f} • {date}"
            ttk.Label(row, text=info_text, font=("Segoe UI", 11)).pack(side="left", expand=True, anchor="w")

            # Sold button with better styling
            sold_btn = ttk.Button(row, text="Mark as Sold",
                                  command=lambda i=item: self.open_sold_popup(i))
            sold_btn.pack(side="right", padx=(10, 0))

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