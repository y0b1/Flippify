import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from RestaurantDatabaseManager import RestaurantDatabaseManager


class SalesAnalytics(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = RestaurantDatabaseManager()
        self.configure(padding=0)
        self.build_modern_ui()
        self.refresh_analytics()

    def build_modern_ui(self):
        # Header section
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 30))

        title_label = ttk.Label(
            header_frame,
            text="📊 Sales Analytics",
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(anchor="w")

        subtitle_label = ttk.Label(
            header_frame,
            text="Real-time sales performance and revenue insights",
            font=("Segoe UI", 12),
            foreground="#888888"
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # Main content container
        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True)

        # Top section - KPI Cards
        self.build_kpi_section(content_frame)

        # Bottom section - Charts
        charts_frame = ttk.Frame(content_frame)
        charts_frame.pack(fill="both", expand=True, pady=(20, 0))

        # Left chart - Revenue trends
        left_chart_frame = ttk.LabelFrame(charts_frame, text="Daily Revenue Trend (Last 30 Days)", padding=15)
        left_chart_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.create_revenue_chart(left_chart_frame)

        # Right chart - Category performance
        right_chart_frame = ttk.LabelFrame(charts_frame, text="Sales by Category", padding=15)
        right_chart_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.create_category_chart(right_chart_frame)

    def build_kpi_section(self, parent):
        kpi_frame = ttk.Frame(parent)
        kpi_frame.pack(fill="x", pady=(0, 20))

        # Get sales summary data
        sales_summary = self.db.get_sales_summary()

        # Calculate additional metrics
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        yesterday_sales = self.db.get_sales_data([yesterday, yesterday])
        yesterday_revenue = sum(sale[5] for sale in yesterday_sales) if yesterday_sales else 0

        today_revenue = sales_summary['today']['revenue']
        revenue_change = ((today_revenue - yesterday_revenue) / yesterday_revenue * 100) if yesterday_revenue > 0 else 0

        # KPI Cards
        kpi_cards = [
            {
                "title": "Today's Revenue",
                "value": f"${today_revenue:.2f}",
                "change": f"{revenue_change:+.1f}%",
                "icon": "💰",
                "color": "#059669" if revenue_change >= 0 else "#dc2626"
            },
            {
                "title": "Orders Today",
                "value": str(sales_summary['today']['count']),
                "change": "Active",
                "icon": "🛍️",
                "color": "#059669"
            },
            {
                "title": "Monthly Revenue",
                "value": f"${sales_summary['month']['revenue']:.2f}",
                "change": f"{sales_summary['month']['count']} orders",
                "icon": "📈",
                "color": "#059669"
            },
            {
                "title": "Top Selling Item",
                "value": sales_summary['popular_item'][:20],
                "change": "Most popular",
                "icon": "⭐",
                "color": "#f59e0b"
            }
        ]

        for i, card in enumerate(kpi_cards):
            self.create_kpi_card(kpi_frame, card, i)

    def create_kpi_card(self, parent, card_data, position):
        card_frame = ttk.Frame(parent)
        card_frame.pack(side="left", fill="both", expand=True, padx=(0, 15 if position < 3 else 0))

        # Card container with border simulation
        card_container = tk.Frame(card_frame, bg="#ffffff", relief="solid", bd=1)
        card_container.pack(fill="both", expand=True, padx=2, pady=2)

        # Inner padding
        inner_frame = tk.Frame(card_container, bg="#ffffff")
        inner_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Icon and title row
        header_frame = tk.Frame(inner_frame, bg="#ffffff")
        header_frame.pack(fill="x", pady=(0, 10))

        icon_label = tk.Label(
            header_frame,
            text=card_data["icon"],
            bg="#ffffff",
            font=("Segoe UI", 20)
        )
        icon_label.pack(side="left")

        title_label = tk.Label(
            header_frame,
            text=card_data["title"],
            bg="#ffffff",
            fg="#64748b",
            font=("Segoe UI", 11),
            anchor="w"
        )
        title_label.pack(side="left", padx=(10, 0), fill="x")

        # Value
        value_label = tk.Label(
            inner_frame,
            text=card_data["value"],
            bg="#ffffff",
            fg="#1e293b",
            font=("Segoe UI", 18, "bold"),
            anchor="w"
        )
        value_label.pack(fill="x", pady=(0, 5))

        # Change indicator
        change_label = tk.Label(
            inner_frame,
            text=card_data["change"],
            bg="#ffffff",
            fg=card_data["color"],
            font=("Segoe UI", 10),
            anchor="w"
        )
        change_label.pack(fill="x")

    def create_revenue_chart(self, parent):
        # Get daily sales data for the last 30 days
        daily_data = self.db.get_daily_sales_trend(30)

        if not daily_data:
            no_data_label = ttk.Label(parent, text="No sales data available",
                                      font=("Segoe UI", 12), foreground="#888888")
            no_data_label.pack(expand=True)
            return

        # Create matplotlib figure
        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)

        dates = [datetime.strptime(row[0], "%Y-%m-%d") for row in daily_data]
        revenues = [row[2] for row in daily_data]

        ax.plot(dates, revenues, color="#f59e0b", linewidth=2, marker='o', markersize=4)
        ax.fill_between(dates, revenues, alpha=0.3, color="#fef3c7")

        ax.set_xlabel("Date", fontsize=10)
        ax.set_ylabel("Revenue ($)", fontsize=10)
        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.grid(True, alpha=0.3)

        # Rotate x-axis labels for better readability
        fig.autofmt_xdate()

        # Embed plot in tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_category_chart(self, parent):
        # Get category performance data
        category_data = self.db.get_category_performance()

        if not category_data:
            no_data_label = ttk.Label(parent, text="No category data available",
                                      font=("Segoe UI", 12), foreground="#888888")
            no_data_label.pack(expand=True)
            return

        # Create matplotlib figure
        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)

        categories = [row[0] for row in category_data]
        revenues = [row[3] for row in category_data]

        colors = ['#f59e0b', '#059669', '#dc2626', '#3b82f6', '#8b5cf6']

        bars = ax.bar(categories, revenues, color=colors[:len(categories)])

        ax.set_xlabel("Category", fontsize=10)
        ax.set_ylabel("Revenue ($)", fontsize=10)
        ax.tick_params(axis='both', which='major', labelsize=8)

        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + height * 0.01,
                    f'${height:.0f}', ha='center', va='bottom', fontsize=8)

        # Embed plot in tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def refresh_analytics(self):
        """Refresh all analytics data"""
        # This would typically refresh the charts and KPIs
        # For now, we'll just update after a delay
        self.after(5000, self.refresh_analytics)  # Refresh every 5 seconds