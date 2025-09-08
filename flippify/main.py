import tkinter as tk
from tkinter import ttk
import sv_ttk
import os
from item_tracker import ItemTracker
from analytics_dashboard import AnalyticsDashboard
from inventory import InventoryTab
from trends import TrendsTab


class FlippifyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Flippify")
        self.center_window(1200, 700)
        self.minsize(1200, 850)

        # Professional Color System
        self.colors = {
            'background': '#ffffff',
            'surface': '#f8fafc',  # Slightly blue-tinted surface
            'surface_elevated': '#ffffff',  # Elevated surfaces (cards, modals)
            'border': '#e2e8f0',  # Subtle blue-gray borders
            'text_primary': '#1e293b',  # Darker, more readable text
            'text_secondary': '#64748b',  # Professional gray
            'text_muted': '#94a3b8',  # Muted text

            # Professional Brand Colors
            'primary': '#3b82f6',  # Professional blue
            'primary_light': '#dbeafe',  # Light blue background
            'primary_dark': '#1d4ed8',  # Dark blue for emphasis

            # Functional Colors
            'success': '#059669',  # Professional green
            'warning': '#d97706',  # Professional amber
            'danger': '#dc2626',  # Professional red

            # Sidebar specific
            'sidebar_bg': '#f1f5f9',  # Light blue-gray sidebar
            'sidebar_border': '#cbd5e1',  # Subtle sidebar border
        }

        self.configure(bg=self.colors['background'])

        self.last_geometry = "1200x700+100+100"

        # Load icon
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

        try:
            sv_ttk.set_theme("light")
        except:
            style = ttk.Style()
            style.theme_use('clam')
            style.configure('TFrame', background=self.colors['background'])
            style.configure('TLabel', background=self.colors['background'], foreground=self.colors['text_primary'])

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

    def setup_sidebar(self):
        # Professional sidebar with subtle accent
        self.sidebar = tk.Frame(self.main_container, bg=self.colors['sidebar_bg'], width=260)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Professional border
        border_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar_border'], width=1)
        border_frame.pack(side="right", fill="y")

        header_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar_bg'], height=120)
        header_frame.pack(fill="x", pady=(35, 25))
        header_frame.pack_propagate(False)

        # Professional brand section
        brand_container = tk.Frame(header_frame, bg=self.colors['sidebar_bg'])
        brand_container.pack(expand=True)

        logo_label = tk.Label(
            brand_container,
            text="Flippify",
            bg=self.colors['sidebar_bg'],
            fg=self.colors['text_primary'],
            font=("Segoe UI", 22, "bold")
        )
        logo_label.pack()

        tagline_label = tk.Label(
            brand_container,
            text="Smart Inventory Management",
            bg=self.colors['sidebar_bg'],
            fg=self.colors['text_secondary'],
            font=("Segoe UI", 11)
        )
        tagline_label.pack(pady=(5, 0))

        nav_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar_bg'])
        nav_frame.pack(fill="both", expand=True, padx=25, pady=20)

        self.nav_buttons = []

        # Professional navigation with purposeful accents
        nav_items = [
            ("📦", "Item Tracker", self.show_items),
            ("📊", "Analytics", self.show_analytics),
            ("📥", "Inventory", self.show_inventory),
            ("📄", "Profit Report", self.show_profit_report),
            ("📈", "Trends", self.show_trends)
        ]

        for i, (icon, text, command) in enumerate(nav_items):
            # Professional button container
            btn_container = tk.Frame(nav_frame, bg=self.colors['sidebar_bg'])
            btn_container.pack(fill="x", pady=3)

            btn = tk.Button(
                btn_container,
                text=f"{icon}  {text}",
                bg=self.colors['sidebar_bg'],
                fg=self.colors['text_primary'],
                font=("Segoe UI", 12, "normal"),
                bd=0,
                padx=20,
                pady=15,
                anchor="w",
                command=command,
                activebackground=self.colors['primary_light'],
                activeforeground=self.colors['primary_dark'],
                cursor="hand2",
                relief='flat'
            )
            btn.pack(fill="x")
            self.nav_buttons.append(btn)

            btn.bind("<Enter>", lambda e, b=btn: self.on_nav_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self.on_nav_hover(b, False))

        # Professional footer with accent
        footer_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar_bg'], height=100)
        footer_frame.pack(side="bottom", fill="x")
        footer_frame.pack_propagate(False)

        # Subtle accent divider
        divider = tk.Frame(footer_frame, bg=self.colors['primary_light'], height=2)
        divider.pack(fill="x", padx=25, pady=(0, 15))

        # Professional status indicator
        status_frame = tk.Frame(footer_frame, bg=self.colors['sidebar_bg'])
        status_frame.pack(pady=5)

        status_dot = tk.Label(
            status_frame,
            text="●",
            bg=self.colors['sidebar_bg'],
            fg=self.colors['success'],
            font=("Segoe UI", 12)
        )
        status_dot.pack(side="left")

        status_label = tk.Label(
            status_frame,
            text=" System Ready",
            bg=self.colors['sidebar_bg'],
            fg=self.colors['text_secondary'],
            font=("Segoe UI", 10)
        )
        status_label.pack(side="left")

        # Version info
        version_label = tk.Label(
            footer_frame,
            text="Version 1.0.0",
            bg=self.colors['sidebar_bg'],
            fg=self.colors['text_muted'],
            font=("Segoe UI", 9)
        )
        version_label.pack(pady=(5, 15))

    def on_nav_hover(self, button, is_hover):
        if button != self.active_button:
            if is_hover:
                # Professional hover with subtle accent
                button.config(
                    bg=self.colors['surface_elevated'],
                    fg=self.colors['primary'],
                    font=("Segoe UI", 12, "normal")
                )
            else:
                # Default professional state
                button.config(
                    bg=self.colors['sidebar_bg'],
                    fg=self.colors['text_primary'],
                    font=("Segoe UI", 12, "normal")
                )

    def set_active_button(self, button):

        for btn in self.nav_buttons:
            btn.config(
                bg=self.colors['sidebar_bg'],
                fg=self.colors['text_primary'],
                font=("Segoe UI", 12, "normal")
            )

        # Professional active state with purpose
        button.config(
            bg=self.colors['primary'],
            fg=self.colors['surface_elevated'],
            font=("Segoe UI", 12, "bold")
        )
        self.active_button = button

    def setup_content_area(self):
        """Create the main content area with professional styling"""
        self.content_container = tk.Frame(self.main_container, bg=self.colors['surface'])
        self.content_container.pack(side="right", fill="both", expand=True)

        self.content = ttk.Frame(self.content_container)
        self.content.pack(fill="both", expand=True, padx=40, pady=30)

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

    def show_profit_report(self):
        self.clear_frame()
        from profit_report import ProfitReportTab
        self.current_frame = ProfitReportTab(self.content)
        self.current_frame.pack(fill="both", expand=True)
        if self.nav_buttons:
            self.set_active_button(self.nav_buttons[3])

    def show_trends(self):
        self.clear_frame()
        self.current_frame = TrendsTab(self.content)
        self.current_frame.pack(fill="both", expand=True)
        if self.nav_buttons:
            self.set_active_button(self.nav_buttons[4])


if __name__ == "__main__":
    app = FlippifyApp()
    app.mainloop()