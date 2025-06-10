from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, 
                            QDateEdit, QSpinBox, QDoubleSpinBox, QFormLayout, 
                            QGroupBox, QMessageBox, QHeaderView, QFrame, QDialog,
                            QCompleter, QSplitter, QTextEdit)
from PyQt5.QtCore import Qt, QDate, QStringListModel, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QColor, QPixmap, QPainter, QPen, QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
import datetime
import math
from database.db_connector import DatabaseConnection
from utils.auth import Authentication

class POSWidget(QWidget):
    """Widget for Point of Sale functionality"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseConnection()
        self.auth = Authentication()
        self.cart_items = []
        self.selected_product = None
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QHBoxLayout(self)
        
        # Left side - Product selection and cart
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Search and product selection section
        search_group = QGroupBox("Product Search")
        search_layout = QVBoxLayout(search_group)
        
        # Search bar
        search_input_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products by name or ID...")
        self.search_input.textChanged.connect(self.filter_products)
        search_input_layout.addWidget(self.search_input)
        
        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_btn.setToolTip("Refresh Products")
        self.refresh_btn.clicked.connect(self.refresh_products)
        search_input_layout.addWidget(self.refresh_btn)
        
        search_layout.addLayout(search_input_layout)
        
        # Category filter
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories", None)
        self.load_categories()
        self.category_filter.currentIndexChanged.connect(self.filter_products)
        search_input_layout.addWidget(self.category_filter)
        
        search_layout.addLayout(search_input_layout)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels(["ID", "Name", "Unit Price", "Stock"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.products_table.itemSelectionChanged.connect(self.product_selected)
        search_layout.addWidget(self.products_table)
        
        left_layout.addWidget(search_group)
        
        # Product details and add to cart
        details_group = QGroupBox("Product Details")
        details_layout = QFormLayout(details_group)
        
        self.product_name_label = QLabel("-")
        details_layout.addRow("Product:", self.product_name_label)
        
        self.product_price_label = QLabel("-")
        details_layout.addRow("Unit Price:", self.product_price_label)
        
        self.product_stock_label = QLabel("-")
        details_layout.addRow("Available Stock:", self.product_stock_label)
        
        # Quantity selector
        quantity_layout = QHBoxLayout()
        
        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setRange(1, 9999)
        self.quantity_spinbox.setValue(1)
        self.quantity_spinbox.setButtonSymbols(QSpinBox.PlusMinus)
        self.quantity_spinbox.setFixedHeight(30)
        quantity_layout.addWidget(self.quantity_spinbox)
        
        self.add_to_cart_btn = QPushButton("Add to Cart")
        self.add_to_cart_btn.setIcon(QIcon("resources/icons/add_cart.png"))
        self.add_to_cart_btn.setEnabled(False)
        self.add_to_cart_btn.clicked.connect(self.add_to_cart)
        self.add_to_cart_btn.setFixedHeight(30)
        quantity_layout.addWidget(self.add_to_cart_btn)
        
        details_layout.addRow("Quantity:", quantity_layout)
        
        left_layout.addWidget(details_group)
        
        # Right side - Cart and checkout
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Cart
        cart_group = QGroupBox("Shopping Cart")
        cart_layout = QVBoxLayout(cart_group)
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(6)
        self.cart_table.setHorizontalHeaderLabels(["ID", "Product", "Unit Price", "Quantity", "Subtotal", "Actions"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.cart_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.cart_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)
        cart_layout.addWidget(self.cart_table)
        
        # Cart actions
        cart_actions_layout = QHBoxLayout()
        
        self.clear_cart_btn = QPushButton("Clear Cart")
        self.clear_cart_btn.setIcon(QIcon("resources/icons/clear_cart.png"))
        self.clear_cart_btn.clicked.connect(self.clear_cart)
        cart_actions_layout.addWidget(self.clear_cart_btn)
        
        cart_layout.addLayout(cart_actions_layout)
        
        right_layout.addWidget(cart_group)
        
        # Checkout section
        checkout_group = QGroupBox("Checkout")
        checkout_layout = QVBoxLayout(checkout_group)
        
        # Totals
        totals_form = QFormLayout()
        
        self.subtotal_label = QLabel("P0.00")
        self.subtotal_label.setAlignment(Qt.AlignRight)
        self.subtotal_label.setFont(QFont("Arial", 10))
        totals_form.addRow("Subtotal:", self.subtotal_label)
        
        checkout_layout.addLayout(totals_form)
                
        # Add after the payment method section in init_ui method
        # Payment method
        payment_layout = QHBoxLayout()
        payment_layout.addWidget(QLabel("Payment Method:"))

        self.payment_method = QComboBox()
        self.payment_method.addItems(["Cash", "Credit Card(Not Available)", "Debit Card(Not Available)", "Mobile Payment(Not Available)"])
        self.payment_method.currentIndexChanged.connect(self.update_payment_method)
        payment_layout.addWidget(self.payment_method)

        checkout_layout.addLayout(payment_layout)

        # Cash tendering section (initially visible)
        self.cash_tendering_frame = QFrame()
        self.cash_tendering_layout = QFormLayout(self.cash_tendering_frame)

        # Cash tendered input
        self.cash_tendered_input = QDoubleSpinBox()
        self.cash_tendered_input.setRange(0, 999999.99)
        self.cash_tendered_input.setDecimals(2)
        self.cash_tendered_input.setPrefix("₱ ")
        self.cash_tendered_input.setFixedHeight(30)
        self.cash_tendered_input.valueChanged.connect(self.calculate_change)
        self.cash_tendering_layout.addRow("Cash Tendered:", self.cash_tendered_input)

        # Change amount display
        self.change_label = QLabel("₱ 0.00")
        self.change_label.setAlignment(Qt.AlignRight)
        self.change_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.change_label.setStyleSheet("color: #e74c3c;")
        self.cash_tendering_layout.addRow("Change:", self.change_label)

        # Quick cash buttons
        quick_cash_layout = QHBoxLayout()
        quick_cash_values = [10, 20, 50, 100, 200, 500, 1000]

        for value in quick_cash_values:
            # Create a function that captures the current value
            def make_button_handler(amount):
                return lambda: self.set_quick_cash(amount)
    
            btn = QPushButton(f"₱{value}")
            btn.setStyleSheet("""
        QPushButton {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #f0f0f0;
            border-color: #e74c3c;
            color: #e74c3c;
        }
    """)
            # Create a new function for each button with the correct captured value
            button_handler = make_button_handler(value)
            btn.clicked.connect(button_handler)
            quick_cash_layout.addWidget(btn)

        self.cash_tendering_layout.addRow("Quick Cash:", quick_cash_layout)

        # Exact cash button
        exact_cash_btn = QPushButton("Exact Cash")
        exact_cash_btn.setStyleSheet("""
    QPushButton {
        background-color: #e74c3c;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #c0392b;
    }
""")
        exact_cash_btn.clicked.connect(self.set_exact_cash)
        self.cash_tendering_layout.addRow("", exact_cash_btn)

        checkout_layout.addWidget(self.cash_tendering_frame)

        # Notes
        checkout_layout.addWidget(QLabel("Notes:"))

        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        checkout_layout.addWidget(self.notes_input)
        
        # Checkout button
        self.checkout_btn = QPushButton("Checkout")
        self.checkout_btn.setIcon(QIcon("resources/icons/checkout.png"))
        self.checkout_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.checkout_btn.clicked.connect(self.process_checkout)
        checkout_layout.addWidget(self.checkout_btn)
        
        right_layout.addWidget(checkout_group)
        
        # Add widgets to splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([500, 500])
        
        main_layout.addWidget(splitter)
        
        # Set default focus to search
        self.search_input.setFocus()
        
    def update_payment_method(self):
        """Update UI based on selected payment method"""
        payment_method = self.payment_method.currentText()
        # Only show cash tendering for Cash payment method
        self.cash_tendering_frame.setVisible(payment_method == "Cash")
    
        # Reset cash tendered and change when switching payment methods
        if payment_method == "Cash":
            self.cash_tendered_input.setValue(0)
            self.calculate_change()

    def calculate_change(self):
        """Calculate change based on cash tendered"""
        if not self.cart_items:
            self.change_label.setText("₱ 0.00")
            return
        
        subtotal = sum(item['subtotal'] for item in self.cart_items)
        cash_tendered = self.cash_tendered_input.value()
    
        if cash_tendered < subtotal:
            self.change_label.setText("₱ 0.00")
            self.checkout_btn.setEnabled(False)
        else:
            change = cash_tendered - subtotal
            self.change_label.setText(f"₱ {change:.2f}")
            self.checkout_btn.setEnabled(True)

    def set_quick_cash(self, amount):
        """Set cash tendered to a quick cash amount"""
        self.cash_tendered_input.setValue(amount)
    
    def set_exact_cash(self):
        """Set cash tendered to exact amount of the sale"""
        if not self.cart_items:
            return
        
        subtotal = sum(item['subtotal'] for item in self.cart_items)
        self.cash_tendered_input.setValue(subtotal)
        
    def refresh_products(self):
        """Refresh the product list and categories"""
        # Clear selection and product details
        self.selected_product = None
        self.product_name_label.setText("-")
        self.product_price_label.setText("-")
        self.product_stock_label.setText("-")
        self.add_to_cart_btn.setEnabled(False)
    
        # Clear the search input
        self.search_input.clear()
    
        # Reset category filter to "All Categories"
        self.category_filter.setCurrentIndex(0)
    
        try:
            # Reload categories
            self.category_filter.clear()
            self.category_filter.addItem("All Categories", None)
            self.load_categories()
        
            # Reload products
            self.load_products()
        
            # Show success message
            QMessageBox.information(self, "Refresh Complete", "Product list has been refreshed successfully.")
        
        except Exception as e:
            QMessageBox.critical(self, "Refresh Error", f"Failed to refresh products: {str(e)}")
    
    def load_products(self):
        """Load products from database into table"""
        connection = None
        cursor = None
        try:
            # Clear the table first
            self.products_table.setRowCount(0)
    
            # Get a direct connection
            connection = self.db.get_connection()
            cursor = connection.cursor()
    
            # Get products with stock > 0 AND is_active = TRUE
            query = """
                SELECT p.product_id, p.product_name, p.unit_price, p.stock_quantity, c.name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                WHERE p.stock_quantity > 0 AND p.is_active = TRUE
                ORDER BY p.product_name
            """
            cursor.execute(query)
            products = cursor.fetchall()
    
            # Build product name completer
            product_names = []
    
            for row_idx, product in enumerate(products):
                self.products_table.insertRow(row_idx)
            
                product_id, name, price, stock, category = product
            
                # Add to autocomplete list
                product_names.append(name)
            
                # Product ID
                self.products_table.setItem(row_idx, 0, QTableWidgetItem(str(product_id)))
            
                # Product Name
                self.products_table.setItem(row_idx, 1, QTableWidgetItem(name))
            
                # Unit Price
                price_item = QTableWidgetItem(f"P{float(price):.2f}")
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.products_table.setItem(row_idx, 2, price_item)
            
                # Stock
                stock_item = QTableWidgetItem(str(stock))
                stock_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.products_table.setItem(row_idx, 3, stock_item)
            
                # Store the category in a hidden role
                self.products_table.item(row_idx, 0).setData(Qt.UserRole, category)
        
            # Setup autocomplete
            completer = QCompleter(product_names)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.search_input.setCompleter(completer)
        
            # Reset the selection
            self.products_table.clearSelection()
        
            print(f"Loaded {self.products_table.rowCount()} products")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load products: {str(e)}")
            print(f"Error loading products: {str(e)}")
            import traceback
            print(traceback.format_exc())
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.db.release_connection(connection)
    
    def load_categories(self):
        """Load categories into filter dropdown"""
        try:
            query = "SELECT category_id, name FROM categories ORDER BY name"
            categories = self.db.execute_query(query, fetchall=True)
            
            for category_id, name in categories:
                self.category_filter.addItem(name, category_id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load categories: {str(e)}")
    
    def filter_products(self):
        """Filter products based on search criteria"""
        search_text = self.search_input.text().lower()
        category_id = self.category_filter.currentData()
        
        for row in range(self.products_table.rowCount()):
            show_row = True
            
            # Filter by product name or ID
            product_id = self.products_table.item(row, 0).text()
            product_name = self.products_table.item(row, 1).text().lower()
            
            if search_text and search_text not in product_name and search_text != product_id:
                show_row = False
            
            # Filter by category
            if category_id is not None:
                category = self.products_table.item(row, 0).data(Qt.UserRole)
                if category != self.category_filter.currentText():
                    show_row = False
            
            self.products_table.setRowHidden(row, not show_row)
    
    def product_selected(self):
        """Handle product selection in the table"""
        selected_rows = self.products_table.selectedItems()
        if not selected_rows:
            self.selected_product = None
            self.product_name_label.setText("-")
            self.product_price_label.setText("-")
            self.product_stock_label.setText("-")
            self.add_to_cart_btn.setEnabled(False)
            return
        
        row = selected_rows[0].row()
        
        product_id = int(self.products_table.item(row, 0).text())
        product_name = self.products_table.item(row, 1).text()
        price_text = self.products_table.item(row, 2).text()
        unit_price = float(price_text.replace('P', ''))
        stock = int(self.products_table.item(row, 3).text())
        
        self.selected_product = {
            'id': product_id,
            'name': product_name,
            'price': unit_price,
            'stock': stock
        }
        
        self.product_name_label.setText(product_name)
        self.product_price_label.setText(f"P{unit_price:.2f}")
        self.product_stock_label.setText(str(stock))
        
        # Limit quantity spinner to available stock
        self.quantity_spinbox.setMaximum(stock)
        self.quantity_spinbox.setValue(1)
        
        # Enable add to cart button
        self.add_to_cart_btn.setEnabled(True)
    
    def add_to_cart(self):
        """Add selected product to cart"""
        if not self.selected_product:
            return
        
        quantity = self.quantity_spinbox.value()
        
        if quantity <= 0:
            QMessageBox.warning(self, "Invalid Quantity", "Please enter a quantity greater than zero.")
            return
        
        if quantity > self.selected_product['stock']:
            QMessageBox.warning(self, "Insufficient Stock", 
                               f"Only {self.selected_product['stock']} units available.")
            return
        
        # Check if product already in cart
        for i, item in enumerate(self.cart_items):
            if item['id'] == self.selected_product['id']:
                new_quantity = item['quantity'] + quantity
                
                if new_quantity > self.selected_product['stock']:
                    QMessageBox.warning(self, "Insufficient Stock", 
                                      f"Cannot add {quantity} more units. Only {self.selected_product['stock'] - item['quantity']} more units available.")
                    return
                
                # Update quantity and subtotal
                item['quantity'] = new_quantity
                item['subtotal'] = item['price'] * new_quantity
                
                # Update cart table
                self.cart_table.item(i, 3).setText(str(new_quantity))
                self.cart_table.item(i, 4).setText(f"P{item['subtotal']:.2f}")
                
                self.update_totals()
                return
        
        # Add new item to cart
        subtotal = self.selected_product['price'] * quantity
        cart_item = {
            'id': self.selected_product['id'],
            'name': self.selected_product['name'],
            'price': self.selected_product['price'],
            'quantity': quantity,
            'subtotal': subtotal
        }
        
        self.cart_items.append(cart_item)
        
        # Add to cart table
        row = self.cart_table.rowCount()
        self.cart_table.insertRow(row)
        
        # Product ID
        self.cart_table.setItem(row, 0, QTableWidgetItem(str(cart_item['id'])))
        
        # Product Name
        self.cart_table.setItem(row, 1, QTableWidgetItem(cart_item['name']))
        
        # Unit Price
        price_item = QTableWidgetItem(f"P{cart_item['price']:.2f}")
        price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.cart_table.setItem(row, 2, price_item)
        
        # Quantity
        qty_item = QTableWidgetItem(str(cart_item['quantity']))
        qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.cart_table.setItem(row, 3, qty_item)
        
        # Subtotal
        subtotal_item = QTableWidgetItem(f"P{cart_item['subtotal']:.2f}")
        subtotal_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.cart_table.setItem(row, 4, subtotal_item)
        
        # Actions
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(2, 2, 2, 2)
        actions_layout.setSpacing(2)
        
        remove_btn = QPushButton()
        remove_btn.setIcon(QIcon("resources/icons/delete.png"))
        remove_btn.setToolTip("Remove Item")
        remove_btn.setMaximumWidth(30)
        remove_btn.clicked.connect(lambda _, row=row: self.remove_from_cart(row))
        actions_layout.addWidget(remove_btn)
        
        self.cart_table.setCellWidget(row, 5, actions_widget)
        
        # Update totals
        self.update_totals()
        
        # Reset quantity
        self.quantity_spinbox.setValue(1)
    
    def remove_from_cart(self, row):
        """Remove item from cart"""
        self.cart_items.pop(row)
        self.cart_table.removeRow(row)
        
        # Update actions for remaining rows
        for i in range(row, self.cart_table.rowCount()):
            remove_btn = QPushButton()
            remove_btn.setIcon(QIcon("resources/icons/delete.png"))
            remove_btn.setToolTip("Remove Item")
            remove_btn.setMaximumWidth(30)
            remove_btn.clicked.connect(lambda _, row=i: self.remove_from_cart(row))
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.addWidget(remove_btn)
            
            self.cart_table.setCellWidget(i, 5, actions_widget)
        
        # Update totals
        self.update_totals()
    
    def clear_cart(self):
        """Clear all items from cart"""
        if not self.cart_items:
            return
        
        reply = QMessageBox.question(
            self, 
            "Clear Cart", 
            "Are you sure you want to clear the cart?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.cart_items = []
            self.cart_table.setRowCount(0)
            self.update_totals()
    
    def update_totals(self):
        """Update the total amounts"""
        subtotal = sum(item['subtotal'] for item in self.cart_items)
        self.subtotal_label.setText(f"₱{subtotal:.2f}")

        # Call calculate_change if cash tendering UI elements are present.
        # calculate_change handles the change display and checkout button state for cash payments.
        if hasattr(self, 'cash_tendering_frame') and self.cash_tendering_frame.isVisible():
            # REMOVED: self.cash_tendered_input.setMaximum(subtotal * 10) 
            self.calculate_change()
        else:
            # For non-cash payment methods, checkout button state depends on whether cart has items.
            self.checkout_btn.setEnabled(len(self.cart_items) > 0)

        # If the cart is empty, ensure the checkout button is disabled.
        # And if cash tendering is visible, reset the change label.
        if not self.cart_items:
            self.checkout_btn.setEnabled(False)
            if hasattr(self, 'cash_tendering_frame') and self.cash_tendering_frame.isVisible():
                if hasattr(self, 'change_label'): # Ensure change_label exists
                    self.change_label.setText("₱ 0.00")
    
    def process_checkout(self):
        """Process the checkout"""
        if not self.cart_items:
            QMessageBox.warning(self, "Empty Cart", "The cart is empty. Please add items before checkout.")
            return
    
        try:
            # Begin transaction
            connection = self.db.get_connection()
            cursor = connection.cursor()
        
            try:
                # Insert sale record
                payment_method = self.payment_method.currentText()
                notes = self.notes_input.toPlainText()
                subtotal = sum(item['subtotal'] for item in self.cart_items)
            
                # Get cash tendered and change for cash payments
                cash_tendered = 0
                change_amount = 0
                if payment_method == "Cash":
                    cash_tendered = self.cash_tendered_input.value()
                    change_amount = cash_tendered - subtotal
            
                # Generate invoice number (format: INV-YYYYMMDD-XXXX)
                today = datetime.datetime.now()
                date_part = today.strftime("%Y%m%d")
            
                # Get latest invoice number
                cursor.execute(
                    "SELECT invoice_number FROM sales WHERE invoice_number LIKE %s ORDER BY invoice_number DESC LIMIT 1",
                    (f"INV-{date_part}-%",)
                )
                result = cursor.fetchone()
            
                if result:
                    last_number = int(result[0].split('-')[-1])
                    invoice_number = f"INV-{date_part}-{last_number + 1:04d}"
                else:
                    invoice_number = f"INV-{date_part}-0001"
            
                # Insert sale
                cursor.execute(
                    """
                    INSERT INTO sales 
                    (invoice_number, user_id, total_amount, payment_method, notes, cash_tendered, change_amount)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING sale_id
                    """,
                    (invoice_number, self.user['user_id'], subtotal, payment_method, notes, 
                     cash_tendered if payment_method == "Cash" else None,
                     change_amount if payment_method == "Cash" else None)
                )
            
                sale_id = cursor.fetchone()[0]
            
                # Insert sale items and update stock
                for item in self.cart_items:
                    # Insert sale item
                    cursor.execute(
                        """
                        INSERT INTO sale_items
                        (sale_id, product_id, quantity, unit_price, subtotal)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (sale_id, item['id'], item['quantity'], item['price'], item['subtotal'])
                    )
                
                    # Update stock
                    cursor.execute(
                        """
                        UPDATE products
                        SET stock_quantity = stock_quantity - %s
                        WHERE product_id = %s
                        """,
                        (item['quantity'], item['id'])
                    )
            
                # Commit transaction
                connection.commit()
            
                # Log activity
                self.auth.log_activity(
                    self.user['user_id'],
                    "sale",
                    "sales",
                    sale_id,
                    f"Created new sale: {invoice_number}, amount: ₱{subtotal:.2f}"
                )
            
                # Create a success message
                message = f"Sale completed successfully!\nInvoice Number: {invoice_number}\nTotal Amount: ₱{subtotal:.2f}"
            
                if payment_method == "Cash":
                    message += f"\nCash Tendered: ₱{cash_tendered:.2f}\nChange: ₱{change_amount:.2f}"
            
                # Show dialog with Print Receipt or Cancel options
                receipt_dialog = QMessageBox(self)
                receipt_dialog.setWindowTitle("Sale Complete")
                receipt_dialog.setText(message)
                receipt_dialog.setIcon(QMessageBox.Information)
            
                print_btn = receipt_dialog.addButton("Print Receipt", QMessageBox.AcceptRole)
                cancel_btn = receipt_dialog.addButton("Close", QMessageBox.RejectRole)
            
                receipt_dialog.exec_()
            
                clicked_button = receipt_dialog.clickedButton()
            
                if clicked_button == print_btn:
                    # Print the receipt
                    self.print_receipt(sale_id, invoice_number)
            
                # Clear cart and refresh products regardless of which button was clicked
                self.cart_items = []
                self.cart_table.setRowCount(0)
                self.update_totals()
                self.notes_input.clear()
                if payment_method == "Cash":
                    self.cash_tendered_input.setValue(0)
                self.load_products()
            
            except Exception as e:
                connection.rollback()
                raise e
        
            finally:
                cursor.close()
                self.db.release_connection(connection)
            
        except Exception as e:
            QMessageBox.critical(self, "Checkout Error", f"Failed to process checkout: {str(e)}")
    
    def print_receipt(self, sale_id, invoice_number):
        """Print the sales receipt as PDF"""
        try:
            # Get sale details
            connection = self.db.get_connection()
            cursor = connection.cursor()
        
            query = """
                SELECT s.sale_id, s.invoice_number, s.sale_date, s.total_amount, 
                       s.payment_method, u.full_name as cashier_name,
                       s.cash_tendered, s.change_amount, s.notes
                FROM sales s
                JOIN users u ON s.user_id = u.user_id
                WHERE s.sale_id = %s
            """
            cursor.execute(query, (sale_id,))
            sale = cursor.fetchone()
        
            # Get sale items
            items_query = """
                SELECT si.quantity, si.unit_price, si.subtotal, p.product_name
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                WHERE si.sale_id = %s
            """
            cursor.execute(items_query, (sale_id,))
            items = cursor.fetchall()
        
            cursor.close()
            self.db.release_connection(connection)
        
            # Create PDF receipt
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A5
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import mm
            import tempfile
            import os
        
            # Create a temporary file for the PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_filename = temp_file.name
        
            # Create PDF document
            doc = SimpleDocTemplate(
                temp_filename,
                pagesize=A5,
                rightMargin=10*mm,
                leftMargin=10*mm,
                topMargin=10*mm,
                bottomMargin=10*mm
            )
        
            # Get the standard styles
            styles = getSampleStyleSheet()
        
            # Elements to build the PDF
            elements = []
        
            # Company header
            heading_style = styles['Heading1']
            heading_style.alignment = 1  # Center
            heading_style.textColor = colors.HexColor('#e74c3c')
            elements.append(Paragraph("ARYONA DRUGHUB", heading_style))
            elements.append(Spacer(1, 2*mm))
        
            normal_center = styles['Normal']
            normal_center.alignment = 1  # Center
            elements.append(Paragraph("Pharmacy & Medical Supplies", normal_center))
            elements.append(Spacer(1, 2*mm))
        
            small_text = styles['Normal']
            small_text.fontSize = 8
            small_text.alignment = 1  # Center
            elements.append(Paragraph("Bontores, Basak San Nicolas, Cebu City, Philippines<br/>Tel: (02) 8-123-4567 | www.aryonadrughub.com", small_text))
            elements.append(Spacer(1, 5*mm))
        
            # Invoice information
            info_data = [
                ["Invoice:", invoice_number],
                ["Date:", sale[2].strftime('%Y-%m-%d %H:%M')],
                ["Cashier:", sale[5]],
                ["Payment:", sale[4]]
            ]
        
            info_table = Table(info_data, colWidths=[40*mm, 90*mm])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9f9f9')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#eeeeee')),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 5*mm))
        
            # Items table
            items_data = [["Item", "Qty", "Price", "Amount"]]
        
            for item in items:
                quantity, unit_price, subtotal, product_name = item
                items_data.append([
                    product_name,
                    str(quantity),
                    f"P{float(unit_price):.2f}",
                    f"P{float(subtotal):.2f}"
                ])
        
            items_table = Table(
                items_data, 
                colWidths=[70*mm, 15*mm, 25*mm, 25*mm],
                repeatRows=1
            )
        
            items_table.setStyle(TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                # Data styling
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'), # Qty centered
                ('ALIGN', (2, 0), (3, -1), 'RIGHT'),  # Price and Amount right-aligned
                # Borders
                ('GRID', (0, 0), (-1, 0), 1, colors.white),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.white),
                ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.HexColor('#dddddd')),
            ]))
        
            elements.append(items_table)
            elements.append(Spacer(1, 5*mm))
        
            # Totals, Cash Tendered, and Change
            has_cash_details = sale[4] == "Cash" and sale[6] is not None
        
            totals_data = [
                ["Total:", f"P{float(sale[3]):.2f}"]
            ]
        
            if has_cash_details:
                totals_data.append(["Cash Tendered:", f"P{float(sale[6]):.2f}"])
                totals_data.append(["Change:", f"P{float(sale[7]):.2f}"])

            totals_table = Table(
                totals_data, 
                colWidths=[100*mm, 35*mm]
            )
        
            totals_table.setStyle(TableStyle([
                # Basic styling
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                # Total row
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#e74c3c')),
                ('FONTSIZE', (1, 0), (1, 0), 12),
            ]))
            
            # Notes section (if notes exist)
            if sale[8] and sale[8].strip():  # Index 8 contains the notes from our updated query
                elements.append(Spacer(1, 5*mm))
                
                # Create a paragraph for notes
                notes_style = styles['Normal']
                notes_style.fontSize = 9
                notes_style.alignment = 0  # Left-aligned
                
                elements.append(Paragraph("<b>Notes:</b>", notes_style))
                elements.append(Spacer(1, 2*mm))
                elements.append(Paragraph(sale[8], notes_style))
        
            elements.append(totals_table)
            elements.append(Spacer(1, 8*mm))
        
            # Barcode/Invoice number
            elements.append(Paragraph(f"<para align='center'>{invoice_number}</para>", styles['Normal']))
            elements.append(Spacer(1, 10*mm))
        
            # Footer with standard styles
            footer_style = styles['Normal']
            footer_style.fontSize = 8
            footer_style.alignment = 1  # Center
            elements.append(Paragraph("<b>Thank you for your purchase!</b>", footer_style))
            elements.append(Spacer(1, 2*mm))
            elements.append(Paragraph("Aryona DrugHUB - Your Health, Our Priority", footer_style))
            elements.append(Spacer(1, 2*mm))
            elements.append(Paragraph("This receipt is your proof of purchase.<br/>For returns or exchanges, please present this receipt<br/>within 7 days of purchase with items in original condition.", footer_style))
        
            # Build PDF
            doc.build(elements)
        
            # Open the PDF receipt
            import subprocess
            import sys
            import os
        
            if sys.platform == 'win32':
                os.startfile(temp_filename)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', temp_filename], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', temp_filename], check=True)
        
        except Exception as e:
            QMessageBox.critical(self, "Print Error", f"Failed to print receipt: {str(e)}")
            import traceback
            print(traceback.format_exc())