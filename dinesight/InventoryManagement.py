import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from RestaurantDatabaseManager import RestaurantDatabaseManager


class InventoryManagement(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = RestaurantDatabaseManager()
        self.configure(padding=0)
        self.selected_item_id = None
        self.build_modern_ui()
        self.refresh_inventory_list()

    def build_modern_ui(self):
        # Header section
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 30))

        title_label = ttk.Label(
            header_frame,
            text="📦 Inventory Management",
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(anchor="w")

        subtitle_label = ttk.Label(
            header_frame,
            text="Track ingredients, stock levels, and manage suppliers",
            font=("Segoe UI", 12),
            foreground="#888888"
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # Main content container
        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True)

        # Left side - Form and alerts
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side="left", fill="y", padx=(0, 20))

        self.build_inventory_form(left_frame)
        self.build_low_stock_alerts(left_frame)

        # Right side - Inventory list
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        self.build_inventory_list(right_frame)

    def build_inventory_form(self, parent):
        # Form container
        form_container = ttk.LabelFrame(parent, text="Add/Update Inventory Item", padding=20)
        form_container.pack(fill="x", pady=(0, 20))
        form_container.configure(width=350)

        # Initialize variables
        self.ingredient_name_var = tk.StringVar()
        self.current_stock_var = tk.StringVar()
        self.unit_var = tk.StringVar(value="kg")
        self.threshold_var = tk.StringVar()
        self.cost_per_unit_var = tk.StringVar()
        self.supplier_var = tk.StringVar()
        self.expiry_date_var = tk.StringVar()

        # Form fields
        fields = [
            ("Ingredient Name *", self.ingredient_name_var, "e.g., Chicken Breast"),
            ("Current Stock *", self.current_stock_var, "Current quantity"),
            ("Unit", self.unit_var, None),  # Dropdown
            ("Min Threshold *", self.threshold_var, "Reorder level"),
            ("Cost per Unit ($)", self.cost_per_unit_var, "Unit cost"),
            ("Supplier", self.supplier_var, "Supplier name"),
            ("Expiry Date", self.expiry_date_var, "YYYY-MM-DD format"),
        ]

        for i, (label, var, placeholder) in enumerate(fields):
            # Label
            label_widget = ttk.Label(form_container, text=label, font=("Segoe UI", 10, "bold"))
            label_widget.pack(anchor="w", pady=(15 if i > 0 else 0, 5))

            # Special handling for unit dropdown
            if label == "Unit":
                units = ["kg", "lbs", "liters", "pieces", "boxes", "bags"]
                unit_combo = ttk.Combobox(form_container, textvariable=var,
                                          values=units, state="readonly",
                                          font=("Segoe UI", 11), width=28)
                unit_combo.pack(fill="x", pady=(0, 5))
            else:
                # Regular entry
                entry = ttk.Entry(form_container, textvariable=var, font=("Segoe UI", 11), width=30)
                entry.pack(fill="x", pady=(0, 5))

            # Placeholder text
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

        # Buttons
        add_btn = ttk.Button(
            button_frame,
            text="➕ Add Item",
            command=self.add_inventory_item,
            style="Accent.TButton"
        )
        add_btn.pack(side="left", padx=(0, 10))

        update_btn = ttk.Button(
            button_frame,
            text="✏️ Update",
            command=self.update_inventory_item
        )
        update_btn.pack(side="left", padx=(0, 10))

        clear_btn = ttk.Button(
            button_frame,
            text="🧹 Clear",
            command=self.clear_form
        )
        clear_btn.pack(side="left")

    def build_low_stock_alerts(self, parent):
        alerts_frame = ttk.LabelFrame(parent, text="⚠️ Low Stock Alerts", padding=15)
        alerts_frame.pack(fill="x", pady=10)

        # Get low stock items
        low_stock_items = self.db.get_inventory(low_stock_only=True)

        if not low_stock_items:
            no_alerts_label = ttk.Label(
                alerts_frame,
                text="✅ All items are adequately stocked",
                font=("Segoe UI", 10),
                foreground="#059669"
            )
            no_alerts_label.pack()
        else:
            # Create scrollable alerts list
            alerts_text = tk.Text(
                alerts_frame,
                height=6,
                width=40,
                font=("Segoe UI", 9),
                bg="#fef2f2",
                fg="#dc2626",
                wrap=tk.WORD,
                state=tk.DISABLED
            )
            alerts_text.pack(fill="both")

            # Populate alerts
            alerts_text.config(state=tk.NORMAL)
            for item in low_stock_items:
                name = item[1]
                current = item[2]
                threshold = item[4]
                unit = item[3]
                alerts_text.insert(tk.END, f"🔴 {name}: {current} {unit} (min: {threshold})\n")
            alerts_text.config(state=tk.DISABLED)

    def build_inventory_list(self, parent):
        # List header
        list_header = ttk.Frame(parent)
        list_header.pack(fill="x", pady=(0, 15))

        ttk.Label(
            list_header,
            text="Current Inventory",
            font=("Segoe UI", 16, "bold")
        ).pack(side="left")

        # Control buttons
        control_frame = ttk.Frame(list_header)
        control_frame.pack(side="right")

        refresh_btn = ttk.Button(
            control_frame,
            text="🔄 Refresh",
            command=self.refresh_inventory_list
        )
        refresh_btn.pack(side="left", padx=(0, 10))

        delete_btn = ttk.Button(
            control_frame,
            text="🗑️ Delete",
            command=self.delete_inventory_item
        )
        delete_btn.pack(side="left")

        # Inventory treeview
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill="both", expand=True)

        # Create treeview with scrollbars
        self.inventory_tree = ttk.Treeview(
            tree_frame,
            columns=("name", "stock", "unit", "threshold", "cost", "supplier", "expiry"),
            show="headings",
            height=15
        )

        # Define headings
        headings = [
            ("name", "Ingredient", 150),
            ("stock", "Stock", 80),
            ("unit", "Unit", 60),
            ("threshold", "Min", 60),
            ("cost", "Cost/Unit", 80),
            ("supplier", "Supplier", 120),
            ("expiry", "Expiry", 100)
        ]

        for col, heading, width in headings:
            self.inventory_tree.heading(col, text=heading, anchor="w")
            self.inventory_tree.column(col, width=width, anchor="w")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.inventory_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.inventory_tree.xview)

        self.inventory_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack treeview and scrollbars
        self.inventory_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")

        # Bind selection event
        self.inventory_tree.bind("<<TreeviewSelect>>", self.on_item_select)

    def add_inventory_item(self):
        """Add new inventory item"""
        try:
            name = self.ingredient_name_var.get().strip()
            stock = float(self.current_stock_var.get())
            unit = self.unit_var.get()
            threshold = float(self.threshold_var.get())
            cost = float(self.cost_per_unit_var.get() or 0)
            supplier = self.supplier_var.get().strip()
            expiry = self.expiry_date_var.get().strip()

            if not name or stock < 0 or threshold < 0:
                messagebox.showerror("Error", "Please fill in all required fields with valid values")
                return

            if self.db.add_inventory_item(name, stock, unit, threshold, cost, supplier, expiry):
                messagebox.showinfo("Success", "Inventory item added successfully!")
                self.clear_form()
                self.refresh_inventory_list()
            else:
                messagebox.showerror("Error", "Failed to add inventory item")

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for stock, threshold, and cost")

    def update_inventory_item(self):
        """Update existing inventory item stock"""
        if not self.selected_item_id:
            messagebox.showwarning("Warning", "Please select an item to update")
            return

        try:
            new_stock = float(self.current_stock_var.get())

            if self.db.update_inventory_stock(self.selected_item_id, new_stock):
                messagebox.showinfo("Success", "Inventory updated successfully!")
                self.refresh_inventory_list()
            else:
                messagebox.showerror("Error", "Failed to update inventory")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid stock quantity")

    def delete_inventory_item(self):
        """Delete selected inventory item"""
        if not self.selected_item_id:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this inventory item?"):
            # Note: This would require adding a delete method to the database class
            messagebox.showinfo("Info", "Delete functionality would be implemented here")

    def on_item_select(self, event):
        """Handle item selection in treeview"""
        selection = self.inventory_tree.selection()
        if selection:
            item = self.inventory_tree.item(selection[0])
            values = item['values']

            # Store the selected item ID (would need to be added to treeview data)
            # For now, we'll use the ingredient name to identify items
            self.selected_item_id = values[0]  # This is a simplification

            # Populate form with selected item data
            self.ingredient_name_var.set(values[0])
            self.current_stock_var.set(values[1])
            self.unit_var.set(values[2])
            self.threshold_var.set(values[3])
            self.cost_per_unit_var.set(values[4])
            self.supplier_var.set(values[5])
            self.expiry_date_var.set(values[6])

    def refresh_inventory_list(self):
        """Refresh the inventory list display"""
        # Clear existing items
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)

        # Get inventory data
        inventory_items = self.db.get_inventory()

        # Populate treeview
        for item in inventory_items:
            # item structure: (id, ingredient_name, current_stock, unit, minimum_threshold, 
            #                  cost_per_unit, supplier, last_restocked, expiry_date)
            item_id = item[0]
            name = item[1]
            stock = item[2]
            unit = item[3]
            threshold = item[4]
            cost = f"${item[5]:.2f}" if item[5] else "N/A"
            supplier = item[6] or "N/A"
            expiry = item[8] or "N/A"

            # Color coding for low stock
            tag = "low_stock" if stock <= threshold else "normal"

            self.inventory_tree.insert(
                "",
                "end",
                values=(name, stock, unit, threshold, cost, supplier, expiry),
                tags=(tag,)
            )

        # Configure tags for visual feedback
        self.inventory_tree.tag_configure("low_stock", background="#fef2f2")
        self.inventory_tree.tag_configure("normal", background="#ffffff")

    def clear_form(self):
        """Clear all form fields"""
        self.ingredient_name_var.set("")
        self.current_stock_var.set("")
        self.unit_var.set("kg")
        self.threshold_var.set("")
        self.cost_per_unit_var.set("")
        self.supplier_var.set("")
        self.expiry_date_var.set("")
        self.selected_item_id = None