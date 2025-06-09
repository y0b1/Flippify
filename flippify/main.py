import tkinter as tk
from tkinter import ttk
import sv_ttk
import os
from item_tracker import ItemTracker
from analytics_dashboard import AnalyticsDashboard
from inventory import InventoryTab


class FlippifyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Flippify")
        self.center_window(1200, 700)
        self.minsize(1200, 850)

        self.configure(bg='#1a1a1a')
        self.overrideredirect(True)


        self.is_fullscreen = False
        self.last_geometry = "1200x700+100+100"

        self.setup_custom_titlebar()

        
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except tk.TclError:
                print(f"Warning: Could not load icon from {icon_path}")
        elif os.path.exists("Icon.ico"):
            try:
                self.iconbitmap("Icon.ico")
            except tk.TclError:
                print("Warning: Could not load icon Icon.ico")

        
        sv_ttk.set_theme("dark")

        
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill="both", expand=True)

        
        self.setup_sidebar()
        self.setup_content_area()

        
        self.current_frame = None
        self.active_button = None
        self.show_items()

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_custom_titlebar(self):
        self.title_bar = tk.Frame(self, bg='#181818', height=35)
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.pack_propagate(False)

        
        title_label = tk.Label(
            self.title_bar,
            text="Flippify",
            bg='#181818',
            fg='#ffffff',
            font=("Segoe UI", 12, "bold")
        )
        title_label.pack(side="left", padx=15, pady=8)

        
        controls_frame = tk.Frame(self.title_bar, bg='#181818')
        controls_frame.pack(side="right", pady=5, padx=5)

        
        fullscreen_btn = tk.Button(
            controls_frame,
            text="⛶",
            bg='#181818',
            fg='#ffffff',
            font=("Segoe UI", 8),
            bd=0,
            padx=10,
            pady=2,
            command=self.toggle_fullscreen,
            activebackground='#404040'
        )
        fullscreen_btn.pack(side="left", padx=2)

        
        close_btn = tk.Button(
            controls_frame,
            text="✕",
            bg='#181818',
            fg='#ffffff',
            font=("Segoe UI", 8),
            bd=0,
            padx=10,
            pady=2,
            command=self.quit,
            activebackground='#e74c3c'
        )
        close_btn.pack(side="left", padx=2)

        
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.on_move)
        self.title_bar.bind("<Double-Button-1>", self.toggle_fullscreen)
        title_label.bind("<Button-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.on_move)
        title_label.bind("<Double-Button-1>", self.toggle_fullscreen)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        if not self.is_fullscreen:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.winfo_x() + deltax
            y = self.winfo_y() + deltay
            self.geometry(f"+{x}+{y}")

    def toggle_fullscreen(self, event=None):
        """Toggle between fullscreen and windowed mode"""
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.geometry(self.last_geometry)

        else:
            
            self.last_geometry = self.geometry()
            self.is_fullscreen = True
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")


    def setup_sidebar(self):
        self.sidebar = tk.Frame(self.main_container, bg='#181818', width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        
        header_frame = tk.Frame(self.sidebar, bg='#181818', height=80)
        header_frame.pack(fill="x", pady=20)
        header_frame.pack_propagate(False)

        logo_label = tk.Label(
            header_frame,
            text="💰 Flippify",
            bg='#181818',
            fg='#3498db',  # Changed from #4CAF50 to light blue
            font=("Segoe UI", 18, "bold")
        )
        logo_label.pack(pady=15)

        
        nav_frame = tk.Frame(self.sidebar, bg='#181818')
        nav_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.nav_buttons = []

        nav_items = [
            ("📦 Item Tracker", self.show_items),
            ("📊 Analytics", self.show_analytics),
            ("📥 Inventory", self.show_inventory)
        ]

        for text, command in nav_items:
            btn = tk.Button(
                nav_frame,
                text=text,
                bg='#181818',
                fg='#ffffff',
                font=("Segoe UI", 11),
                bd=0,
                padx=20,
                pady=15,
                anchor="w",
                command=command,
                activebackground='#3498db',  # Changed from #4CAF50 to light blue
                activeforeground='#ffffff',
                cursor="hand2"
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons.append(btn)

            
            btn.bind("<Enter>", lambda e, b=btn: self.on_nav_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self.on_nav_hover(b, False))

    def on_nav_hover(self, button, is_hover):
        if button != self.active_button:
            if is_hover:
                button.config(bg='#5dade2')  
            else:
                button.config(bg='#181818')

    def set_active_button(self, button):
        
        for btn in self.nav_buttons:
            btn.config(bg='#181818', fg='#ffffff')

        
        button.config(bg='#3498db', fg='#ffffff')  # Changed from #4CAF50 to light blue
        self.active_button = button

    def setup_content_area(self):
        """Create the main content area with modern styling"""
        self.content_container = tk.Frame(self.main_container, bg='#1a1a1a')
        self.content_container.pack(side="right", fill="both", expand=True)

        
        self.content = ttk.Frame(self.content_container)
        self.content.pack(fill="both", expand=True, padx=30, pady=20)

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def show_items(self):
        self.clear_frame()
        self.current_frame = ItemTracker(self.content)
        self.current_frame.pack(fill="both", expand=True)
        if self.nav_buttons:
            self.set_active_button(self.nav_buttons[0])

    def show_analytics(self):
        self.clear_frame()
        self.current_frame = AnalyticsDashboard(self.content)
        self.current_frame.pack(fill="both", expand=True)
        if self.nav_buttons:
            self.set_active_button(self.nav_buttons[1])

    def show_inventory(self):
        self.clear_frame()
        self.current_frame = InventoryTab(self.content)
        self.current_frame.pack(fill="both", expand=True)
        if self.nav_buttons:
            self.set_active_button(self.nav_buttons[2])


if __name__ == "__main__":
    app = FlippifyApp()
    app.mainloop()