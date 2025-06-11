import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from database import DatabaseManager
import numpy as np
from calendar import monthrange


class AnalyticsDashboard(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.configure(padding=0)

        # Configure matplotlib for dark theme
        plt.style.use('dark_background')

        self.build_modern_dashboard()

    def build_modern_dashboard(self):
        # Main container with scrollbar
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True)

        # Create canvas and scrollbar for the entire dashboard
        self.canvas = tk.Canvas(main_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Bind frame configure to update scroll region
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Bind canvas configure to update frame width
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_frame_id, width=e.width)
        )

        # Create window and store the ID for width updates
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel to canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<MouseWheel>", self._on_mousewheel)

        # Header section
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill="x", pady=(20, 30), padx=20)

        title_label = ttk.Label(
            header_frame,
            text="📊 Analytics Dashboard",
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(anchor="w")

        subtitle_label = ttk.Label(
            header_frame,
            text="Insights and performance metrics for your flipping business",
            font=("Segoe UI", 12),
            foreground="#888888"
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # Main dashboard container
        dashboard_container = ttk.Frame(self.scrollable_frame)
        dashboard_container.pack(fill="both", expand=True, padx=20)

        # Top section - KPI Cards
        self.build_kpi_cards(dashboard_container)

        # Performance indicators section
        self.build_performance_indicators(dashboard_container)

        # Middle section - Controls
        self.build_controls(dashboard_container)

        # Bottom section - Charts
        self.build_charts_section(dashboard_container)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def get_chart_size(self):
        """Calculate appropriate chart size based on available width"""
        try:
            # Get the canvas width, accounting for scrollbar and padding
            canvas_width = self.canvas.winfo_width()
            available_width = max(canvas_width - 60, 800)  # Minimum width of 800

            # Scale figure size based on available width
            base_width = available_width / 100  # Convert pixels to inches (roughly)
            return min(base_width, 12), 8  # Max width of 12 inches
        except:
            return 10, 8  # Default fallback size

    def get_performance_data(self):
        """Calculate performance metrics for current month and year"""
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month

        # Get current month data
        current_month_start = datetime(current_year, current_month, 1)
        current_month_end = datetime(current_year, current_month, monthrange(current_year, current_month)[1])

        # Get previous month data for comparison
        if current_month == 1:
            prev_month = 12
            prev_year = current_year - 1
        else:
            prev_month = current_month - 1
            prev_year = current_year

        prev_month_start = datetime(prev_year, prev_month, 1)
        prev_month_end = datetime(prev_year, prev_month, monthrange(prev_year, prev_month)[1])

        # Get all sales data
        rows = self.db.cursor.execute(
            "SELECT sold_price, source_price, date FROM items WHERE sold_price > 0"
        ).fetchall()

        current_month_revenue = 0
        current_month_profit = 0
        current_year_revenue = 0
        current_year_profit = 0
        prev_month_revenue = 0
        prev_month_profit = 0
        prev_year_revenue = 0
        prev_year_profit = 0

        for sold, source, date_str in rows:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                profit = sold - source

                # Current month
                if current_month_start <= dt <= current_month_end:
                    current_month_revenue += sold
                    current_month_profit += profit

                # Current year
                if dt.year == current_year:
                    current_year_revenue += sold
                    current_year_profit += profit

                # Previous month
                if prev_month_start <= dt <= prev_month_end:
                    prev_month_revenue += sold
                    prev_month_profit += profit

                # Previous year
                if dt.year == current_year - 1:
                    prev_year_revenue += sold
                    prev_year_profit += profit

            except:
                continue

        # Calculate percentage changes
        month_revenue_change = ((
                                            current_month_revenue - prev_month_revenue) / prev_month_revenue * 100) if prev_month_revenue > 0 else 0
        year_revenue_change = ((
                                           current_year_revenue - prev_year_revenue) / prev_year_revenue * 100) if prev_year_revenue > 0 else 0

        return {
            'current_month_revenue': current_month_revenue,
            'current_month_profit': current_month_profit,
            'current_year_revenue': current_year_revenue,
            'current_year_profit': current_year_profit,
            'month_revenue_change': month_revenue_change,
            'year_revenue_change': year_revenue_change,
            'current_month': current_date.strftime("%B"),
            'current_year': current_year
        }

    def build_performance_indicators(self, parent):
        """Build performance indicators showing if user is doing well"""
        perf_frame = ttk.LabelFrame(parent, text="📈 Performance Status", padding=15)
        perf_frame.pack(fill="x", pady=(0, 20))

        performance_data = self.get_performance_data()

        # Create performance cards
        indicators_frame = ttk.Frame(perf_frame)
        indicators_frame.pack(fill="x")

        # Monthly performance
        month_change = performance_data['month_revenue_change']
        month_status = "📈 Great!" if month_change > 10 else "📊 Good" if month_change > 0 else "📉 Needs Attention"
        month_color = "#4CAF50" if month_change > 10 else "#FF9800" if month_change > 0 else "#F44336"

        month_card = self.create_performance_card(
            indicators_frame,
            f"This Month ({performance_data['current_month']})",
            f"₱{performance_data['current_month_revenue']:,.2f}",
            f"{month_change:+.1f}% vs last month",
            month_status,
            month_color
        )
        month_card.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Yearly performance
        year_change = performance_data['year_revenue_change']
        year_status = "🚀 Excellent!" if year_change > 20 else "📈 Good Progress" if year_change > 0 else "⚠️ Review Needed"
        year_color = "#4CAF50" if year_change > 20 else "#2196F3" if year_change > 0 else "#FF5722"

        year_card = self.create_performance_card(
            indicators_frame,
            f"This Year ({performance_data['current_year']})",
            f"₱{performance_data['current_year_revenue']:,.2f}",
            f"{year_change:+.1f}% vs last year",
            year_status,
            year_color
        )
        year_card.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Profit margins
        month_margin = (performance_data['current_month_profit'] / performance_data['current_month_revenue'] * 100) if \
        performance_data['current_month_revenue'] > 0 else 0
        margin_status = "💰 Excellent!" if month_margin > 30 else "💸 Good" if month_margin > 15 else "⚖️ Check Costs"
        margin_color = "#4CAF50" if month_margin > 30 else "#FF9800" if month_margin > 15 else "#F44336"

        margin_card = self.create_performance_card(
            indicators_frame,
            "Monthly Profit Margin",
            f"{month_margin:.1f}%",
            f"₱{performance_data['current_month_profit']:,.2f} profit",
            margin_status,
            margin_color
        )
        margin_card.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

        # Configure grid weights
        for i in range(3):
            indicators_frame.columnconfigure(i, weight=1)

    def create_performance_card(self, parent, title, main_value, sub_value, status, color):
        """Create a performance indicator card"""
        card = ttk.LabelFrame(parent, padding=15)

        # Title
        title_label = ttk.Label(
            card,
            text=title,
            font=("Segoe UI", 10, "bold"),
            foreground="#CCCCCC"
        )
        title_label.pack(anchor="w")

        # Main value
        main_label = ttk.Label(
            card,
            text=main_value,
            font=("Segoe UI", 16, "bold"),
            foreground=color
        )
        main_label.pack(anchor="w", pady=(5, 0))

        # Sub value
        sub_label = ttk.Label(
            card,
            text=sub_value,
            font=("Segoe UI", 9),
            foreground="#888888"
        )
        sub_label.pack(anchor="w", pady=(2, 0))

        # Status
        status_label = ttk.Label(
            card,
            text=status,
            font=("Segoe UI", 10, "bold"),
            foreground=color
        )
        status_label.pack(anchor="w", pady=(5, 0))

        return card

    def build_kpi_cards(self, parent):
        kpi_frame = ttk.Frame(parent)
        kpi_frame.pack(fill="x", pady=(0, 20))

        data = self.db.fetch_items()

        # Calculate KPIs
        total_items = len(data)
        sold_items = len([item for item in data if item[2] > 0])
        total_revenue = sum(item[2] for item in data if item[2] > 0)
        total_cost = sum(item[1] for item in data)
        net_profit = total_revenue - sum(item[1] for item in data if item[2] > 0)

        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        avg_profit_per_item = net_profit / sold_items if sold_items > 0 else 0

        # Find best performing item
        profits = [(item[0], item[2] - item[1]) for item in data if item[2] > 0]
        best_item = max(profits, key=lambda x: x[1], default=("None", 0))

        # KPI data
        kpis = [
            ("💰 Total Revenue", f"₱{total_revenue:,.2f}", "#4CAF50"),
            ("📈 Net Profit", f"₱{net_profit:,.2f}", "#2196F3"),
            ("📊 Profit Margin", f"{profit_margin:.1f}%", "#FF9800"),
            ("🎯 Avg Profit/Item", f"₱{avg_profit_per_item:,.2f}", "#9C27B0"),
            ("🏆 Best Item", f"{best_item[0][:15]}...", "#F44336"),
            ("📦 Items Sold", f"{sold_items}/{total_items}", "#607D8B")
        ]

        # Create KPI cards in a grid
        for i, (title, value, color) in enumerate(kpis):
            card = self.create_kpi_card(kpi_frame, title, value, color)
            row = i // 3
            col = i % 3
            card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")

        # Configure grid weights
        for i in range(3):
            kpi_frame.columnconfigure(i, weight=1)

    def create_kpi_card(self, parent, title, value, color):
        card = ttk.LabelFrame(parent, padding=20)

        # Title
        title_label = ttk.Label(
            card,
            text=title,
            font=("Segoe UI", 10),
            foreground="#888888"
        )
        title_label.pack(anchor="w")

        # Value
        value_label = ttk.Label(
            card,
            text=value,
            font=("Segoe UI", 16, "bold"),
            foreground=color
        )
        value_label.pack(anchor="w", pady=(5, 0))

        return card

    def build_controls(self, parent):
        controls_frame = ttk.LabelFrame(parent, text="Dashboard Controls", padding=15)
        controls_frame.pack(fill="x", pady=(0, 20))

        # Year filter
        filter_frame = ttk.Frame(controls_frame)
        filter_frame.pack(fill="x")

        ttk.Label(filter_frame, text="Select Year:", font=("Segoe UI", 11)).pack(side="left", padx=(0, 10))

        # Get available years
        years = [r[0] for r in self.db.cursor.execute(
            "SELECT DISTINCT strftime('%Y', date) FROM items ORDER BY date DESC").fetchall()]

        self.year_var = tk.StringVar(value=years[0] if years else str(datetime.now().year))
        year_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.year_var,
            values=years,
            state="readonly",
            width=10
        )
        year_combo.pack(side="left", padx=(0, 20))
        year_combo.bind("<<ComboboxSelected>>", self.update_charts)

        # Chart type selector
        ttk.Label(filter_frame, text="Chart Type:", font=("Segoe UI", 11)).pack(side="left", padx=(0, 10))

        self.chart_type_var = tk.StringVar(value="Daily Revenue")
        chart_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.chart_type_var,
            values=["Daily Revenue", "Monthly Revenue", "Annual Revenue", "Profit Analysis", "Item Performance"],
            state="readonly",
            width=15
        )
        chart_combo.pack(side="left", padx=(0, 20))
        chart_combo.bind("<<ComboboxSelected>>", self.update_charts)

        # Refresh button
        refresh_btn = ttk.Button(
            filter_frame,
            text="🔄 Refresh Data",
            command=self.refresh_dashboard
        )
        refresh_btn.pack(side="right")

    def build_charts_section(self, parent):
        self.charts_frame = ttk.LabelFrame(parent, text="Performance Charts", padding=15)
        self.charts_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Initialize with default chart
        self.update_charts()

    def update_charts(self, event=None):
        # Clear existing charts
        for widget in self.charts_frame.winfo_children():
            widget.destroy()

        chart_type = self.chart_type_var.get() if hasattr(self, 'chart_type_var') else "Daily Revenue"
        year = self.year_var.get() if hasattr(self, 'year_var') else str(datetime.now().year)

        if chart_type == "Daily Revenue":
            self.plot_daily_revenue(year)
        elif chart_type == "Monthly Revenue":
            self.plot_monthly_revenue(year)
        elif chart_type == "Annual Revenue":
            self.plot_annual_revenue()
        elif chart_type == "Profit Analysis":
            self.plot_profit_analysis(year)
        elif chart_type == "Item Performance":
            self.plot_item_performance()

    def plot_daily_revenue(self, year):
        """Plot daily revenue for the selected year"""
        rows = self.db.cursor.execute(
            "SELECT sold_price, date FROM items WHERE sold_price > 0"
        ).fetchall()

        if not rows:
            no_data_label = ttk.Label(
                self.charts_frame,
                text="📊 No sales data available",
                font=("Segoe UI", 14),
                foreground="#888888"
            )
            no_data_label.pack(expand=True, pady=50)
            return

        # Process daily data for the selected year
        daily_sales = {}
        for price, date_str in rows:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                if dt.strftime("%Y") == year:
                    date_key = dt.strftime("%Y-%m-%d")
                    daily_sales[date_key] = daily_sales.get(date_key, 0) + price
            except:
                continue

        if not daily_sales:
            no_data_label = ttk.Label(
                self.charts_frame,
                text=f"📊 No sales data for {year}",
                font=("Segoe UI", 14),
                foreground="#888888"
            )
            no_data_label.pack(expand=True, pady=50)
            return

        # Sort dates and prepare data
        sorted_dates = sorted(daily_sales.keys())
        revenues = [daily_sales[date] for date in sorted_dates]

        # Create chart
        width, height = self.get_chart_size()
        fig, ax = plt.subplots(figsize=(width, height))
        fig.patch.set_facecolor('#1a1a1a')

        # Convert dates for plotting
        dates = [datetime.strptime(date, "%Y-%m-%d") for date in sorted_dates]

        ax.plot(dates, revenues, marker='o', linewidth=2, markersize=4, color='#4CAF50')
        ax.fill_between(dates, revenues, alpha=0.3, color='#4CAF50')

        ax.set_title(f'Daily Revenue - {year}', fontsize=16, color='white', pad=20)
        ax.set_ylabel('Revenue (₱)', color='white', fontsize=12)
        ax.set_xlabel('Date', color='white', fontsize=12)
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3)

        # Format x-axis dates
        fig.autofmt_xdate()

        # Add summary statistics
        total_revenue = sum(revenues)
        avg_daily = total_revenue / len(revenues) if revenues else 0
        max_day = max(revenues) if revenues else 0

        stats_text = f'Total: ₱{total_revenue:,.0f} | Avg Daily: ₱{avg_daily:,.0f} | Best Day: ₱{max_day:,.0f}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', color='white', bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))

        plt.tight_layout(pad=3.0)

        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def plot_monthly_revenue(self, year):
        """Plot monthly revenue with enhanced visualization"""
        rows = self.db.cursor.execute(
            "SELECT sold_price, date FROM items WHERE sold_price > 0"
        ).fetchall()

        if not rows:
            no_data_label = ttk.Label(
                self.charts_frame,
                text="📊 No sales data available",
                font=("Segoe UI", 14),
                foreground="#888888"
            )
            no_data_label.pack(expand=True, pady=50)
            return

        # Process monthly data
        monthly_sales = {m: 0 for m in range(1, 13)}
        monthly_count = {m: 0 for m in range(1, 13)}

        for price, date_str in rows:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                if dt.strftime("%Y") == year:
                    monthly_sales[dt.month] += price
                    monthly_count[dt.month] += 1
            except:
                continue

        # Create the chart with responsive sizing
        width, height = self.get_chart_size()
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(width, height))
        fig.patch.set_facecolor('#1a1a1a')

        months = [datetime(2000, m, 1).strftime("%b") for m in range(1, 13)]
        sales_values = [monthly_sales[m] for m in range(1, 13)]
        count_values = [monthly_count[m] for m in range(1, 13)]

        # Sales chart
        bars1 = ax1.bar(months, sales_values, color='#4CAF50', alpha=0.8)
        ax1.set_title(f'Monthly Revenue - {year}', fontsize=16, color='white', pad=20)
        ax1.set_ylabel('Revenue (₱)', color='white', fontsize=12)
        ax1.tick_params(colors='white')
        ax1.grid(True, alpha=0.3)

        # Add value labels on bars
        for bar, val in zip(bars1, sales_values):
            if val > 0:
                ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(sales_values) * 0.01,
                         f'₱{val:,.0f}', ha='center', va='bottom', color='white', fontsize=10)

        # Items sold chart
        bars2 = ax2.bar(months, count_values, color='#2196F3', alpha=0.8)
        ax2.set_title('Items Sold per Month', fontsize=16, color='white', pad=20)
        ax2.set_ylabel('Items Sold', color='white', fontsize=12)
        ax2.set_xlabel('Month', color='white', fontsize=12)
        ax2.tick_params(colors='white')
        ax2.grid(True, alpha=0.3)

        # Add value labels on bars
        for bar, val in zip(bars2, count_values):
            if val > 0:
                ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(count_values) * 0.02,
                         f'{val}', ha='center', va='bottom', color='white', fontsize=10)

        plt.tight_layout(pad=3.0)

        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def plot_annual_revenue(self):
        """Plot annual revenue comparison across all years"""
        rows = self.db.cursor.execute(
            "SELECT sold_price, date FROM items WHERE sold_price > 0"
        ).fetchall()

        if not rows:
            no_data_label = ttk.Label(
                self.charts_frame,
                text="📊 No sales data available",
                font=("Segoe UI", 14),
                foreground="#888888"
            )
            no_data_label.pack(expand=True, pady=50)
            return

        # Process annual data
        annual_sales = {}
        annual_count = {}

        for price, date_str in rows:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                year = dt.year
                annual_sales[year] = annual_sales.get(year, 0) + price
                annual_count[year] = annual_count.get(year, 0) + 1
            except:
                continue

        if not annual_sales:
            no_data_label = ttk.Label(
                self.charts_frame,
                text="📊 No annual data available",
                font=("Segoe UI", 14),
                foreground="#888888"
            )
            no_data_label.pack(expand=True, pady=50)
            return

        # Create chart
        width, height = self.get_chart_size()
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(width, height))
        fig.patch.set_facecolor('#1a1a1a')

        years = sorted(annual_sales.keys())
        revenues = [annual_sales[year] for year in years]
        counts = [annual_count[year] for year in years]

        # Revenue chart
        bars1 = ax1.bar([str(year) for year in years], revenues, color='#4CAF50', alpha=0.8)
        ax1.set_title('Annual Revenue Comparison', fontsize=16, color='white', pad=20)
        ax1.set_ylabel('Revenue (₱)', color='white', fontsize=12)
        ax1.tick_params(colors='white')
        ax1.grid(True, alpha=0.3)

        # Add value labels
        for bar, val in zip(bars1, revenues):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(revenues) * 0.01,
                     f'₱{val:,.0f}', ha='center', va='bottom', color='white', fontsize=10)

        # Growth rate calculation and display
        if len(revenues) > 1:
            growth_rates = []
            for i in range(1, len(revenues)):
                growth = ((revenues[i] - revenues[i - 1]) / revenues[i - 1] * 100) if revenues[i - 1] > 0 else 0
                growth_rates.append(growth)

            # Add trend line
            ax1_twin = ax1.twinx()
            ax1_twin.plot([str(year) for year in years[1:]], growth_rates,
                          color='#FF9800', marker='o', linewidth=2, markersize=6)
            ax1_twin.set_ylabel('Growth Rate (%)', color='#FF9800', fontsize=12)
            ax1_twin.tick_params(colors='#FF9800')

        # Items sold chart
        bars2 = ax2.bar([str(year) for year in years], counts, color='#2196F3', alpha=0.8)
        ax2.set_title('Annual Items Sold', fontsize=16, color='white', pad=20)
        ax2.set_ylabel('Items Sold', color='white', fontsize=12)
        ax2.set_xlabel('Year', color='white', fontsize=12)
        ax2.tick_params(colors='white')
        ax2.grid(True, alpha=0.3)

        # Add value labels
        for bar, val in zip(bars2, counts):
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(counts) * 0.02,
                     f'{val}', ha='center', va='bottom', color='white', fontsize=10)

        plt.tight_layout(pad=3.0)

        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def plot_profit_analysis(self, year):
        # Get profit data
        rows = self.db.cursor.execute(
            "SELECT name, source_price, sold_price, date FROM items WHERE sold_price > 0"
        ).fetchall()

        if not rows:
            no_data_label = ttk.Label(
                self.charts_frame,
                text="📈 No profit data available",
                font=("Segoe UI", 14),
                foreground="#888888"
            )
            no_data_label.pack(expand=True, pady=50)
            return

        # Process profit data
        year_data = []
        for name, source, sold, date_str in rows:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                if dt.strftime("%Y") == year:
                    profit = sold - source
                    margin = (profit / sold * 100) if sold > 0 else 0
                    year_data.append((name, source, sold, profit, margin))
            except:
                continue

        if not year_data:
            no_data_label = ttk.Label(
                self.charts_frame,
                text=f"📈 No profit data for {year}",
                font=("Segoe UI", 14),
                foreground="#888888"
            )
            no_data_label.pack(expand=True, pady=50)
            return

        # Create profit analysis charts with responsive sizing
        width, height = self.get_chart_size()
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(width, height + 2))
        fig.patch.set_facecolor('#1a1a1a')

        # Sort by profit for top items
        sorted_by_profit = sorted(year_data, key=lambda x: x[3], reverse=True)[:10]

        # Top profitable items
        names = [item[0][:20] + '...' if len(item[0]) > 20 else item[0] for item in sorted_by_profit]
        profits = [item[3] for item in sorted_by_profit]

        bars = ax1.barh(names, profits, color='#4CAF50')
        ax1.set_title('Top 10 Most Profitable Items', color='white', fontsize=14, pad=15)
        ax1.set_xlabel('Profit (₱)', color='white', fontsize=12)
        ax1.tick_params(colors='white')
        ax1.grid(True, alpha=0.3)

        # Add value labels on bars
        for bar, profit in zip(bars, profits):
            width = bar.get_width()
            ax1.text(width + max(profits) * 0.01, bar.get_y() + bar.get_height() / 2,
                     f'₱{profit:.0f}', ha='left', va='center', color='white', fontsize=9)

        # Profit margin distribution
        margins = [item[4] for item in year_data]
        ax2.hist(margins, bins=15, color='#FF9800', alpha=0.7, edgecolor='white')
        ax2.set_title('Profit Margin Distribution', color='white', fontsize=14, pad=15)
        ax2.set_xlabel('Profit Margin (%)', color='white', fontsize=12)
        ax2.set_ylabel('Frequency', color='white', fontsize=12)
        ax2.tick_params(colors='white')
        ax2.grid(True, alpha=0.3)

        # Investment vs Profit scatter
        investments = [item[1] for item in year_data]
        profits_scatter = [item[3] for item in year_data]
        ax3.scatter(investments, profits_scatter, color='#2196F3', alpha=0.6, s=50)
        ax3.set_title('Investment vs Profit', color='white', fontsize=14, pad=15)
        ax3.set_xlabel('Investment (₱)', color='white', fontsize=12)
        ax3.set_ylabel('Profit (₱)', color='white', fontsize=12)
        ax3.tick_params(colors='white')
        ax3.grid(True, alpha=0.3)

        # Add trend line
        if len(investments) > 1:
            z = np.polyfit(investments, profits_scatter, 1)
            p = np.poly1d(z)
            ax3.plot(sorted(investments), p(sorted(investments)), "r--", alpha=0.8, linewidth=2)

        # Monthly profit trend
        monthly_profit = {m: 0 for m in range(1, 13)}
        for item in year_data:
            # Need to get month from original data
            for name, source, sold, date_str in rows:
                if name == item[0] and source == item[1] and sold == item[2]:
                    try:
                        dt = datetime.strptime(date_str, "%Y-%m-%d")
                        monthly_profit[dt.month] += item[3]
                        break
                    except:
                        continue

        months = [datetime(2000, m, 1).strftime("%b") for m in range(1, 13)]
        profit_values = [monthly_profit[m] for m in range(1, 13)]

        ax4.plot(months, profit_values, marker='o', color='#9C27B0', linewidth=3, markersize=8)
        ax4.set_title('Monthly Profit Trend', color='white', fontsize=14, pad=15)
        ax4.set_ylabel('Profit (₱)', color='white', fontsize=12)
        ax4.set_xlabel('Month', color='white', fontsize=12)
        ax4.tick_params(colors='white')
        ax4.grid(True, alpha=0.3)

        # Add value labels on line
        for i, val in enumerate(profit_values):
            if val > 0:
                ax4.text(i, val + max(profit_values) * 0.02, f'₱{val:.0f}',
                         ha='center', va='bottom', color='white', fontsize=9)

        plt.tight_layout(pad=3.0)

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Update scroll region after adding chart
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def plot_item_performance(self):
        # Get all items performance data
        rows = self.db.fetch_items()

        if not rows:
            no_data_label = ttk.Label(
                self.charts_frame,
                text="📋 No item data available",
                font=("Segoe UI", 14),
                foreground="#888888"
            )
            no_data_label.pack(expand=True, pady=50)
            return

        # Separate sold and unsold items
        sold_items = [(name, source, sold, sold - source) for name, source, sold, date in rows if sold > 0]
        unsold_items = [(name, source) for name, source, sold, date in rows if sold == 0]

        # Create responsive figure for better visibility
        width, height = self.get_chart_size()
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(width, height + 2))
        fig.patch.set_facecolor('#1a1a1a')

        # Performance by profit
        if sold_items:
            sold_items_sorted = sorted(sold_items, key=lambda x: x[3], reverse=True)[:15]
            names = [item[0][:18] + '...' if len(item[0]) > 18 else item[0] for item in sold_items_sorted]
            profits = [item[3] for item in sold_items_sorted]

            colors = ['#4CAF50' if p >= 0 else '#F44336' for p in profits]
            bars = ax1.barh(names, profits, color=colors)
            ax1.set_title('Item Performance by Profit', color='white', fontsize=14, pad=15)
            ax1.set_xlabel('Profit (₱)', color='white', fontsize=12)
            ax1.tick_params(colors='white')
            ax1.grid(True, alpha=0.3)

            # Add profit values on bars
            for bar, profit in zip(bars, profits):
                width = bar.get_width()
                ax1.text(width + (max(profits) * 0.01 if width >= 0 else min(profits) * 0.01),
                         bar.get_y() + bar.get_height() / 2,
                         f'₱{profit:.0f}', ha='left' if width >= 0 else 'right',
                         va='center', color='white', fontsize=9)

        # ROI (Return on Investment) analysis
        if sold_items:
            roi_data = [(item[0], (item[3] / item[1] * 100) if item[1] > 0 else 0) for item in sold_items]
            roi_sorted = sorted(roi_data, key=lambda x: x[1], reverse=True)[:10]

            names_roi = [item[0][:18] + '...' if len(item[0]) > 18 else item[0] for item in roi_sorted]
            roi_values = [item[1] for item in roi_sorted]

            ax2.barh(names_roi, roi_values, color='#FF9800')
            ax2.set_title('Top ROI Items (%)', color='white', fontsize=14, pad=15)
            ax2.set_xlabel('ROI (%)', color='white', fontsize=12)
            ax2.tick_params(colors='white')
            ax2.grid(True, alpha=0.3)

            # Add ROI values on bars
            for i, (bar, roi) in enumerate(zip(ax2.patches, roi_values)):
                width = bar.get_width()
                ax2.text(width + max(roi_values) * 0.01, bar.get_y() + bar.get_height() / 2,
                         f'{roi:.1f}%', ha='left', va='center', color='white', fontsize=9)

        # Price range analysis
        if sold_items:
            price_ranges = ['₱0-100', '₱101-500', '₱501-1000', '₱1001-2000', '₱2000+']
            range_counts = [0, 0, 0, 0, 0]

            for item in sold_items:
                price = item[2]  # sold price
                if price <= 100:
                    range_counts[0] += 1
                elif price <= 500:
                    range_counts[1] += 1
                elif price <= 1000:
                    range_counts[2] += 1
                elif price <= 2000:
                    range_counts[3] += 1
                else:
                    range_counts[4] += 1

            # Only show pie chart if there's data
            if sum(range_counts) > 0:
                wedges, texts, autotexts = ax3.pie(range_counts, labels=price_ranges, autopct='%1.1f%%',
                                                   startangle=90,
                                                   colors=['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336'])
                ax3.set_title('Sales by Price Range', color='white', fontsize=14, pad=15)

                # Style the pie chart text
                for text in texts:
                    text.set_color('white')
                    text.set_fontsize(10)
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(9)

        # Status overview
        total_items = len(rows)
        sold_count = len(sold_items)
        unsold_count = len(unsold_items)

        if total_items > 0:
            labels = ['Sold', 'Unsold']
            sizes = [sold_count, unsold_count]
            colors = ['#4CAF50', '#FF5722']

            wedges, texts, autotexts = ax4.pie(sizes, labels=labels, autopct='%1.1f%%',
                                               startangle=90, colors=colors)
            ax4.set_title('Inventory Status', color='white', fontsize=14, pad=15)

            # Style the pie chart text
            for text in texts:
                text.set_color('white')
                text.set_fontsize(10)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)

        plt.tight_layout(pad=3.0)

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Update scroll region after adding chart
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def refresh_dashboard(self):
        # Clear the scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Rebuild dashboard
        self.build_modern_dashboard()

        # Reset scroll position
        self.canvas.yview_moveto(0)