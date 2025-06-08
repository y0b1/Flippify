import tkinter as tk
from tkinter import ttk
import sv_ttk
from item_tracker import ItemTracker
from profit_logs import ProfitLogs
from analytics_dashboard import AnalyticsDashboard
from inventory import InventoryTab


class FlippifyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Flippify")
        self.geometry("1000x600")
        self.minsize(800, 1000)
        self.iconbitmap(r"Icon.ico")
        

        sv_ttk.set_theme("dark")

        self.navbar = ttk.Frame(self, padding=10)
        self.navbar.pack(side="top", fill="x")

        ttk.Button(self.navbar, text="📦 Items", command=self.show_items).pack(side="left", padx=10)
        ttk.Button(self.navbar, text="💵 Profits", command=self.show_profits).pack(side="left", padx=10)
        ttk.Button(self.navbar, text="📊 Analytics", command=self.show_analytics).pack(side="left", padx=10)
        ttk.Button(self.navbar, text="📥 Inventory", command=self.show_inventory).pack(side="left", padx=10)


        self.content = ttk.Frame(self, padding=20)
        self.content.pack(fill="both", expand=True)

        self.current_frame = None
        self.show_items()

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def show_items(self):
        self.clear_frame()
        self.current_frame = ItemTracker(self.content)
        self.current_frame.pack(fill="both", expand=True)

    def show_profits(self):
        self.clear_frame()
        self.current_frame = ProfitLogs(self.content)
        self.current_frame.pack(fill="both", expand=True)

    def show_analytics(self):
        self.clear_frame()
        self.current_frame = AnalyticsDashboard(self.content)
        self.current_frame.pack(fill="both", expand=True)
    def show_inventory(self):
        self.clear_frame()
        self.current_frame = InventoryTab(self.content)
        self.current_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = FlippifyApp()
    app.mainloop()
