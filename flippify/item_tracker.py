import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import sqlite3
from database import DatabaseManager


class ItemTracker(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.configure(padding=0)
        self.build_modern_ui()

    def build_modern_ui(self):
        # Header section
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 30))

        title_label = ttk.Label(
            header_frame,
            text="📦 Item Tracker",
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(anchor="w")

        subtitle_label = ttk.Label(
            header_frame,
            text="Track your flipping inventory and sales",
            font=("Segoe UI", 12),
            foreground="#888888"
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # Main content container
        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True)

        # Left side - Form
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side="left", fill="y", padx=(0, 20))

        self.build_modern_form(left_frame)

        # Right side - List
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        self.build_modern_list(right_frame)

    def build_modern_form(self, parent):
        # Form container with modern styling
        form_container = ttk.LabelFrame(parent, text="Add New Item", padding=25)
        form_container.pack(fill="x", pady=(0, 20))

        # Configure form width
        form_container.configure(width=350)

        # Initialize variables
        self.name_var = tk.StringVar()
        self.source_var = tk.StringVar()
        self.sold_var = tk.StringVar()
        self.date_var = tk.StringVar(value=datetime.today().strftime("%Y-%m-%d"))

        # Form fields with modern styling
        fields = [
            ("Item Name", self.name_var, "Enter item name"),
            ("Source Price (₱)", self.source_var, "Purchase price"),
            ("Sold Price (₱)", self.sold_var, "Leave empty if unsold"),
            ("Date (YYYY-MM-DD)", self.date_var, "Transaction date"),
        ]

        for i, (label, var, placeholder) in enumerate(fields):
            # Label
            label_widget = ttk.Label(form_container, text=label, font=("Segoe UI", 10, "bold"))
            label_widget.pack(anchor="w", pady=(15 if i > 0 else 0, 5))

            # Entry with modern style
            entry = ttk.Entry(form_container, textvariable=var, font=("Segoe UI", 11), width=30)
            entry.pack(fill="x", pady=(0, 5))

            # Placeholder effect (simplified)
            if placeholder:
                help_label = ttk.Label(
                    form_container,
                    text=placeholder,
                    font=("Segoe UI", 9),
                    foreground="#666666"
                )
                help_label.pack(anchor="w", pady=(0, 10))

        # Button container
        button_frame = ttk.Frame(form_container)
        button_frame.pack(fill="x", pady=(20, 0))

        # Modern buttons
        add_btn = ttk.Button(
            button_frame,
            text="➕ Add Item",
            command=self.add_item,
            style="Accent.TButton"
        )
        add_btn.pack(side="left", padx=(0, 10))

        clear_btn = ttk.Button(
            button_frame,
            text="🧹 Clear",
            command=self.clear_form
        )
        clear_btn.pack(side="left")

        # Quick stats card
        self.build_stats_card(parent)

    def build_stats_card(self, parent):
        stats_frame = ttk.LabelFrame(parent, text="Quick Stats", padding=20)
        stats_frame.pack(fill="x", pady=10)

        data = self.db.fetch_items()

        total_items = len(data)
        sold_items = len([item for item in data if item[2] > 0])
        unsold_items = total_items - sold_items
        total_profit = sum(item[2] - item[1] for item in data if item[2] > 0)

        stats_text = f"📊 Total Items: {total_items}\n"
        stats_text += f"✅ Sold: {sold_items}\n"
        stats_text += f"📦 Unsold: {unsold_items}\n"
        stats_text += f"💰 Total Profit: ₱{total_profit:.2f}"

        stats_label = ttk.Label(
            stats_frame,
            text=stats_text,
            font=("Segoe UI", 10),
            justify="left"
        )
        stats_label.pack(anchor="w")

    def build_modern_list(self, parent):
        # List header
        list_header = ttk.Frame(parent)
        list_header.pack(fill="x", pady=(0, 15))

        ttk.Label(
            list_header,
            text="Recent Items",
            font=("Segoe UI", 16, "bold")
        ).pack(side="left")

        # Refresh button
        refresh_btn = ttk.Button(
            list_header,
            text="🔄 Refresh",
            command=self.load_items
        )
        refresh_btn.pack(side="right")

        # Modern treeview container
        tree_container = ttk.LabelFrame(parent, text="Inventory List", padding=15)
        tree_container.pack(fill="both", expand=True)

        # Create treeview with modern styling
        columns = ("Name", "Source Price", "Sold Price", "Date", "Profit", "Status")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15)

        # Configure column headings and widths
        column_configs = {
            "Name": (150, "Item Name"),
            "Source Price": (100, "Source (₱)"),
            "Sold Price": (100, "Sold (₱)"),
            "Date": (100, "Date"),
            "Profit": (80, "Profit (₱)"),
            "Status": (80, "Status")
        }

        for col, (width, heading) in column_configs.items():
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, minwidth=60)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack scrollbars and treeview
        self.tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")

        # Context menu for treeview
        self.setup_context_menu()

        # Load initial data
        self.load_items()

    def setup_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="✏️ Edit Item", command=self.edit_selected_item)
        self.context_menu.add_command(label="🗑️ Delete Item", command=self.delete_selected_item)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="💰 Mark as Sold", command=self.mark_as_sold)

        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        if self.tree.selection():
            self.context_menu.post(event.x_root, event.y_root)

    def get_selected_item_data(self):
        """Helper method to get the data of the currently selected item"""
        selection = self.tree.selection()
        if not selection:
            return None

        item = selection[0]
        values = self.tree.item(item, 'values')

        if not values:
            return None

        # Extract data from the tree view values
        name = values[0]
        source_price = float(values[1].replace('₱', '').replace(',', ''))
        sold_price_str = values[2]
        sold_price = 0.0 if sold_price_str == '-' else float(sold_price_str.replace('₱', '').replace(',', ''))
        date = values[3]

        return {
            'name': name,
            'source_price': source_price,
            'sold_price': sold_price,
            'date': date
        }

    def edit_selected_item(self):
        item_data = self.get_selected_item_data()
        if not item_data:
            messagebox.showwarning("Warning", "Please select an item to edit.")
            return

        # Create edit dialog
        edit_window = tk.Toplevel(self)
        edit_window.title("Edit Item")
        edit_window.geometry("400x450")
        edit_window.resizable(False, False)
        edit_window.grab_set()  # Make it modal

        # Center the window
        edit_window.transient(self.winfo_toplevel())

        # Variables for edit form
        edit_name = tk.StringVar(value=item_data['name'])
        edit_source = tk.StringVar(value=str(item_data['source_price']))
        edit_sold = tk.StringVar(value=str(item_data['sold_price']) if item_data['sold_price'] > 0 else "")
        edit_date = tk.StringVar(value=item_data['date'])

        # Edit form
        main_frame = ttk.Frame(edit_window, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Edit Item", font=("Segoe UI", 16, "bold")).pack(pady=(0, 20))

        # Form fields
        fields = [
            ("Item Name:", edit_name),
            ("Source Price (₱):", edit_source),
            ("Sold Price (₱):", edit_sold),
            ("Date (YYYY-MM-DD):", edit_date)
        ]

        entries = []
        for label_text, var in fields:
            ttk.Label(main_frame, text=label_text, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 5))
            entry = ttk.Entry(main_frame, textvariable=var, font=("Segoe UI", 11))
            entry.pack(fill="x", pady=(0, 5))
            entries.append(entry)

        # Focus on first entry
        entries[0].focus()

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))

        def save_changes():
            new_name = edit_name.get().strip()
            new_source = edit_source.get().strip()
            new_sold = edit_sold.get().strip()
            new_date = edit_date.get().strip()

            # Validation
            if not new_name:
                messagebox.showerror("Error", "Item name is required.")
                return

            try:
                new_source_price = float(new_source) if new_source else 0.0
                new_sold_price = float(new_sold) if new_sold else 0.0
            except ValueError:
                messagebox.showerror("Error", "Prices must be valid numbers.")
                return

            if not new_date:
                messagebox.showerror("Error", "Date is required.")
                return

            try:
                datetime.strptime(new_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Date must be in YYYY-MM-DD format.")
                return

            # Update in database
            success = self.db.update_item(
                item_data['name'], item_data['source_price'], item_data['sold_price'], item_data['date'],
                new_name, new_source_price, new_sold_price, new_date
            )

            if success:
                edit_window.destroy()
                self.load_items()
                messagebox.showinfo("Success", f"Item '{new_name}' updated successfully!")
            else:
                messagebox.showerror("Error", "Failed to update item. Please try again.")

        def cancel_edit():
            edit_window.destroy()

        # Buttons
        ttk.Button(button_frame, text="💾 Save Changes", command=save_changes).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="❌ Cancel", command=cancel_edit).pack(side="left")

    def delete_selected_item(self):
        item_data = self.get_selected_item_data()
        if not item_data:
            messagebox.showwarning("Warning", "Please select an item to delete.")
            return

        # Confirm deletion
        confirm_msg = f"Are you sure you want to delete '{item_data['name']}'?\n\nThis action cannot be undone."
        if messagebox.askyesno("Confirm Delete", confirm_msg):
            success = self.db.delete_item(
                item_data['name'],
                item_data['source_price'],
                item_data['sold_price'],
                item_data['date']
            )

            if success:
                self.load_items()
                messagebox.showinfo("Success", f"Item '{item_data['name']}' deleted successfully!")
            else:
                messagebox.showerror("Error", "Failed to delete item. Please try again.")

    def mark_as_sold(self):
        item_data = self.get_selected_item_data()
        if not item_data:
            messagebox.showwarning("Warning", "Please select an item to mark as sold.")
            return

        # Check if already sold
        if item_data['sold_price'] > 0:
            messagebox.showinfo("Info", "This item is already marked as sold.")
            return

        # Get sold price from user
        sold_price = simpledialog.askfloat(
            "Mark as Sold",
            f"Enter the sold price for '{item_data['name']}':",
            minvalue=0.01,
            initialvalue=item_data['source_price'] * 1.2  # Suggest 20% markup
        )

        if sold_price is None:  # User cancelled
            return

        if sold_price <= 0:
            messagebox.showerror("Error", "Sold price must be greater than 0.")
            return

        # Update in database
        success = self.db.update_item(
            item_data['name'], item_data['source_price'], item_data['sold_price'], item_data['date'],
            item_data['name'], item_data['source_price'], sold_price, item_data['date']
        )

        if success:
            self.load_items()
            profit = sold_price - item_data['source_price']
            profit_msg = f"Profit: ₱{profit:.2f}" if profit > 0 else f"Loss: ₱{abs(profit):.2f}"
            messagebox.showinfo("Success", f"Item '{item_data['name']}' marked as sold!\n{profit_msg}")
        else:
            messagebox.showerror("Error", "Failed to update item. Please try again.")

    def add_item(self):
        name = self.name_var.get().strip()
        source_price = self.source_var.get().strip()
        sold_price = self.sold_var.get().strip()
        date = self.date_var.get().strip()

        # Validation
        if not name:
            messagebox.showerror("Error", "Item name is required.")
            return

        try:
            source = float(source_price) if source_price else 0.0
            sold = float(sold_price) if sold_price else 0.0
        except ValueError:
            messagebox.showerror("Error", "Prices must be valid numbers.")
            return

        if not date:
            messagebox.showerror("Error", "Date is required.")
            return

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format.")
            return

        # Add to database
        self.db.insert_item(name, source, sold, date)
        self.load_items()
        self.clear_form()

        # Show success message
        messagebox.showinfo("Success", f"Item '{name}' added successfully!")

    def clear_form(self):
        self.name_var.set("")
        self.source_var.set("")
        self.sold_var.set("")
        self.date_var.set(datetime.today().strftime("%Y-%m-%d"))

    def load_items(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load data from database
        data = self.db.fetch_items()

        for row in data:
            name, source, sold, date = row
            profit = sold - source if sold > 0 else 0
            status = "Sold" if sold > 0 else "Unsold"

            # Color coding based on status
            values = (name, f"₱{source:.2f}", f"₱{sold:.2f}" if sold > 0 else "-",
                      date, f"₱{profit:.2f}" if profit != 0 else "-", status)

            item_id = self.tree.insert("", "end", values=values)

            # Add tags for styling
            if status == "Sold":
                self.tree.set(item_id, "Status", "✅ Sold")
            else:
                self.tree.set(item_id, "Status", "📦 Unsold")

        # Update stats
        self.refresh_stats()

    def refresh_stats(self):
        """Helper method to refresh the stats card"""
        try:
            # Find and update stats card
            for widget in self.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Frame):
                            for grandchild in child.winfo_children():
                                if isinstance(grandchild, ttk.LabelFrame) and "Quick Stats" in str(
                                        grandchild.cget("text")):
                                    grandchild.destroy()
                                    self.build_stats_card(child)
                                    break
        except:
            pass  # Ignore if stats update fails


# Enhanced Database Manager with update functionality
class DatabaseManager:
    def __init__(self, db_name="flippify.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                source_price REAL,
                sold_price REAL,
                date TEXT
            )
        """)
        self.conn.commit()

    def insert_item(self, name, source_price, sold_price, date):
        try:
            self.cursor.execute(
                "INSERT INTO items (name, source_price, sold_price, date) VALUES (?, ?, ?, ?)",
                (name, source_price, sold_price, date)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting item: {e}")
            return False

    def fetch_items(self):
        try:
            self.cursor.execute("SELECT name, source_price, sold_price, date FROM items ORDER BY id DESC")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching items: {e}")
            return []

    def update_item(self, old_name, old_source, old_sold, old_date, new_name, new_source, new_sold, new_date):
        try:
            # Find the specific item to update
            self.cursor.execute(
                "SELECT id FROM items WHERE name=? AND source_price=? AND sold_price=? AND date=? LIMIT 1",
                (old_name, old_source, old_sold, old_date)
            )
            result = self.cursor.fetchone()

            if result:
                item_id = result[0]
                self.cursor.execute(
                    "UPDATE items SET name=?, source_price=?, sold_price=?, date=? WHERE id=?",
                    (new_name, new_source, new_sold, new_date, item_id)
                )
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Error updating item: {e}")
            return False

    def delete_item(self, name, source_price, sold_price, date):
        try:
            self.cursor.execute(
                "SELECT id FROM items WHERE name=? AND source_price=? AND sold_price=? AND date=? LIMIT 1",
                (name, source_price, sold_price, date)
            )
            result = self.cursor.fetchone()

            if result:
                item_id = result[0]
                self.cursor.execute("DELETE FROM items WHERE id=?", (item_id,))
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Error deleting item: {e}")
            return False

    def delete_all_items(self):
        try:
            self.cursor.execute("DELETE FROM items")
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting all items: {e}")
            return False

    def close(self):
        self.conn.close()


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Flippify - Item Tracker")
    root.geometry("1200x700")

    # Configure the style
    style = ttk.Style()
    style.theme_use('clam')

    app = ItemTracker(root)
    app.pack(fill="both", expand=True, padx=20, pady=20)

    root.mainloop()