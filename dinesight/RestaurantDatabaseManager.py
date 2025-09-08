import sqlite3
from datetime import datetime


class RestaurantDatabaseManager:
    def __init__(self, db_name="dinesight.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Create all necessary tables for restaurant management"""

        # Menu items table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                description TEXT,
                price REAL NOT NULL,
                cost REAL,
                preparation_time INTEGER,
                is_available BOOLEAN DEFAULT 1,
                created_date TEXT,
                last_updated TEXT
            )
        """)

        # Sales transactions table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT,
                category TEXT,
                quantity INTEGER,
                unit_price REAL,
                total_amount REAL,
                order_date TEXT,
                order_time TEXT,
                day_of_week TEXT,
                month TEXT,
                year INTEGER
            )
        """)

        # Inventory table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ingredient_name TEXT NOT NULL,
                current_stock REAL,
                unit TEXT,
                minimum_threshold REAL,
                cost_per_unit REAL,
                supplier TEXT,
                last_restocked TEXT,
                expiry_date TEXT
            )
        """)

        # Customer feedback table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT,
                rating INTEGER,
                comment TEXT,
                feedback_date TEXT
            )
        """)

        self.conn.commit()

    # Menu Items Methods
    def add_menu_item(self, name, category, description, price, cost, prep_time, is_available=True):
        """Add a new menu item"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("""
                INSERT INTO menu_items 
                (name, category, description, price, cost, preparation_time, 
                 is_available, created_date, last_updated) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, category, description, price, cost, prep_time,
                  int(is_available), current_time, current_time))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding menu item: {e}")
            return False

    def get_menu_items(self, available_only=False):
        """Get all menu items or only available ones"""
        try:
            query = "SELECT * FROM menu_items"
            if available_only:
                query += " WHERE is_available = 1"
            query += " ORDER BY category, name"

            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching menu items: {e}")
            return []

    def update_menu_item(self, item_id, name, category, description, price, cost, prep_time, is_available):
        """Update an existing menu item"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("""
                UPDATE menu_items 
                SET name=?, category=?, description=?, price=?, cost=?, 
                    preparation_time=?, is_available=?, last_updated=?
                WHERE id=?
            """, (name, category, description, price, cost, prep_time, is_available, current_time, item_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating menu item: {e}")
            return False

    def delete_menu_item(self, item_id):
        """Delete a menu item"""
        try:
            self.cursor.execute("DELETE FROM menu_items WHERE id=?", (item_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting menu item: {e}")
            return False

    # Sales Methods
    def record_sale(self, item_name, category, quantity, unit_price, total_amount):
        """Record a sale transaction"""
        try:
            now = datetime.now()
            order_date = now.strftime("%Y-%m-%d")
            order_time = now.strftime("%H:%M:%S")
            day_of_week = now.strftime("%A")
            month = now.strftime("%B")
            year = now.year

            self.cursor.execute("""
                INSERT INTO sales 
                (item_name, category, quantity, unit_price, total_amount, 
                 order_date, order_time, day_of_week, month, year) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (item_name, category, quantity, unit_price, total_amount,
                  order_date, order_time, day_of_week, month, year))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error recording sale: {e}")
            return False

    def get_sales_data(self, date_range=None, category=None):
        """Get sales data with optional filtering"""
        try:
            query = "SELECT * FROM sales"
            params = []
            conditions = []

            if date_range:
                conditions.append("order_date BETWEEN ? AND ?")
                params.extend([date_range[0], date_range[1]])

            if category:
                conditions.append("category = ?")
                params.append(category)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY order_date DESC, order_time DESC"

            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching sales data: {e}")
            return []

    def get_sales_summary(self):
        """Get sales summary statistics"""
        try:
            # Today's sales
            today = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute("""
                SELECT COUNT(*), COALESCE(SUM(total_amount), 0) 
                FROM sales WHERE order_date = ?
            """, (today,))
            today_count, today_revenue = self.cursor.fetchone()

            # This month's sales
            this_month = datetime.now().strftime("%Y-%m")
            self.cursor.execute("""
                SELECT COUNT(*), COALESCE(SUM(total_amount), 0) 
                FROM sales WHERE strftime('%Y-%m', order_date) = ?
            """, (this_month,))
            month_count, month_revenue = self.cursor.fetchone()

            # Most popular item
            self.cursor.execute("""
                SELECT item_name, SUM(quantity) as total_sold 
                FROM sales 
                GROUP BY item_name 
                ORDER BY total_sold DESC 
                LIMIT 1
            """)
            popular_item = self.cursor.fetchone()

            return {
                'today': {'count': today_count or 0, 'revenue': today_revenue or 0},
                'month': {'count': month_count or 0, 'revenue': month_revenue or 0},
                'popular_item': popular_item[0] if popular_item else 'N/A'
            }
        except Exception as e:
            print(f"Error getting sales summary: {e}")
            return {'today': {'count': 0, 'revenue': 0},
                    'month': {'count': 0, 'revenue': 0},
                    'popular_item': 'N/A'}

    # Inventory Methods
    def add_inventory_item(self, name, stock, unit, threshold, cost_per_unit, supplier, expiry_date):
        """Add a new inventory item"""
        try:
            last_restocked = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute("""
                INSERT INTO inventory 
                (ingredient_name, current_stock, unit, minimum_threshold, 
                 cost_per_unit, supplier, last_restocked, expiry_date) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, stock, unit, threshold, cost_per_unit, supplier, last_restocked, expiry_date))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding inventory item: {e}")
            return False

    def get_inventory(self, low_stock_only=False):
        """Get inventory items, optionally only low stock items"""
        try:
            query = "SELECT * FROM inventory"
            if low_stock_only:
                query += " WHERE current_stock <= minimum_threshold"
            query += " ORDER BY ingredient_name"

            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching inventory: {e}")
            return []

    def update_inventory_stock(self, item_id, new_stock):
        """Update inventory stock level"""
        try:
            self.cursor.execute("""
                UPDATE inventory SET current_stock=? WHERE id=?
            """, (new_stock, item_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating inventory: {e}")
            return False

    # Analytics Methods
    def get_category_performance(self):
        """Get performance data by category"""
        try:
            self.cursor.execute("""
                SELECT category, 
                       COUNT(*) as orders,
                       SUM(quantity) as items_sold,
                       SUM(total_amount) as revenue
                FROM sales 
                GROUP BY category 
                ORDER BY revenue DESC
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting category performance: {e}")
            return []

    def get_hourly_sales_pattern(self):
        """Get sales pattern by hour of day"""
        try:
            self.cursor.execute("""
                SELECT strftime('%H', order_time) as hour,
                       COUNT(*) as orders,
                       SUM(total_amount) as revenue
                FROM sales 
                GROUP BY hour 
                ORDER BY hour
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting hourly sales pattern: {e}")
            return []

    def get_daily_sales_trend(self, days=30):
        """Get daily sales trend for specified number of days"""
        try:
            self.cursor.execute("""
                SELECT order_date,
                       COUNT(*) as orders,
                       SUM(total_amount) as revenue
                FROM sales 
                WHERE order_date >= date('now', '-{} days')
                GROUP BY order_date 
                ORDER BY order_date
            """.format(days))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting daily sales trend: {e}")
            return []

    def close(self):
        """Close database connection"""
        self.conn.close()


# Alias for compatibility with original Flippify code
DatabaseManager = RestaurantDatabaseManager