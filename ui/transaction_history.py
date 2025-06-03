from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                           QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                           QDateEdit, QComboBox, QMessageBox, QHeaderView, QFrame,QWidget)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QIcon
import datetime
# Add to your imports

class TransactionHistoryDialog(QDialog):
    """Dialog for viewing transaction history, voiding sales, and reprinting receipts"""
    
    transaction_cancelled = pyqtSignal(int)  # Signal when a transaction is cancelled
    
    def __init__(self, parent=None, db=None, user=None, auth=None):
        super().__init__(parent)
        self.db = db
        self.user = user
        self.auth = auth
        self.parent_widget = parent
        
        self.setWindowTitle("Transaction History")
        self.setMinimumSize(900, 600)
        self.setWindowIcon(QIcon("resources/icons/history.png"))
        
        self.init_ui()
        self.load_transactions()
        
    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)
        
        # Filter section
        filter_frame = QFrame()
        filter_frame.setFrameShape(QFrame.StyledPanel)
        filter_layout = QHBoxLayout(filter_frame)
        
        # Date range
        filter_layout.addWidget(QLabel("From:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-7))  # Default to last 7 days
        filter_layout.addWidget(self.date_from)
        
        filter_layout.addWidget(QLabel("To:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        filter_layout.addWidget(self.date_to)
        
        # Invoice number search
        filter_layout.addWidget(QLabel("Invoice #:"))
        self.invoice_search = QLineEdit()
        self.invoice_search.setPlaceholderText("Search by invoice number...")
        filter_layout.addWidget(self.invoice_search)
        
        # Status filter
        filter_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Completed", "Voided"])
        filter_layout.addWidget(self.status_filter)
        
        # Search button
        self.search_btn = QPushButton("Search")
        self.search_btn.setIcon(QIcon("resources/icons/search.png"))
        self.search_btn.clicked.connect(self.load_transactions)
        filter_layout.addWidget(self.search_btn)
        
        main_layout.addWidget(filter_frame)
        
        # Transactions table
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(8)
        self.transactions_table.setHorizontalHeaderLabels([
            "ID", "Invoice #", "Date", "Cashier", "Amount", "Payment Method", "Status", "Actions"
        ])
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.transactions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.transactions_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.transactions_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.transactions_table)
        
        # Button row
        button_layout = QHBoxLayout()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.setIcon(QIcon("resources/icons/close.png"))
        self.close_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(button_layout)
        
    def load_transactions(self):
        """Load transactions based on filters"""
        try:
            # Clear the table
            self.transactions_table.setRowCount(0)
            
            # Get filter values
            date_from = self.date_from.date().toString("yyyy-MM-dd")
            date_to = self.date_to.date().toString("yyyy-MM-dd")
            invoice_number = self.invoice_search.text().strip()
            status_filter = self.status_filter.currentText()
            
            # Build query
            query = """
                SELECT s.sale_id, s.invoice_number, s.sale_date, u.full_name, 
                       s.total_amount, s.payment_method, s.status
                FROM sales s
                JOIN users u ON s.user_id = u.user_id
                WHERE s.sale_date BETWEEN %s AND %s
            """
            params = [f"{date_from} 00:00:00", f"{date_to} 23:59:59"]
            
            if invoice_number:
                query += " AND s.invoice_number LIKE %s"
                params.append(f"%{invoice_number}%")
            
            if status_filter != "All":
                query += " AND s.status = %s"
                params.append(status_filter)
            
            query += " ORDER BY s.sale_date DESC"
            
            # Execute query
            connection = self.db.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            transactions = cursor.fetchall()
            cursor.close()
            self.db.release_connection(connection)
            
            # Populate table
            for row_idx, transaction in enumerate(transactions):
                sale_id, invoice_number, sale_date, cashier, total_amount, payment_method, status = transaction
                
                self.transactions_table.insertRow(row_idx)
                
                # ID
                self.transactions_table.setItem(row_idx, 0, QTableWidgetItem(str(sale_id)))
                
                # Invoice Number
                self.transactions_table.setItem(row_idx, 1, QTableWidgetItem(invoice_number))
                
                # Date
                date_item = QTableWidgetItem(sale_date.strftime('%Y-%m-%d %H:%M'))
                self.transactions_table.setItem(row_idx, 2, date_item)
                
                # Cashier
                self.transactions_table.setItem(row_idx, 3, QTableWidgetItem(cashier))
                
                # Amount
                amount_item = QTableWidgetItem(f"₱{float(total_amount):.2f}")
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.transactions_table.setItem(row_idx, 4, amount_item)
                
                # Payment Method
                self.transactions_table.setItem(row_idx, 5, QTableWidgetItem(payment_method))
                
                # Status
                status_item = QTableWidgetItem(status)
                if status == "Voided":
                    status_item.setForeground(Qt.red)
                self.transactions_table.setItem(row_idx, 6, status_item)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(2, 2, 2, 2)
                actions_layout.setSpacing(5)
                
                # View details button
                view_btn = QPushButton()
                view_btn.setIcon(QIcon("resources/icons/view.png"))
                view_btn.setToolTip("View Details")
                view_btn.setMaximumWidth(30)
                view_btn.clicked.connect(lambda _, id=sale_id: self.view_transaction_details(id))
                actions_layout.addWidget(view_btn)
                
                # Print receipt button
                print_btn = QPushButton()
                print_btn.setIcon(QIcon("resources/icons/print.png"))
                print_btn.setToolTip("Print Receipt")
                print_btn.setMaximumWidth(30)
                print_btn.clicked.connect(lambda _, id=sale_id, inv=invoice_number: self.print_receipt(id, inv))
                actions_layout.addWidget(print_btn)
                
                # Void transaction button (only for completed transactions)
                if status == "Completed":
                    void_btn = QPushButton()
                    void_btn.setIcon(QIcon("resources/icons/cancel.png"))
                    void_btn.setToolTip("Void Transaction")
                    void_btn.setMaximumWidth(30)
                    void_btn.clicked.connect(lambda _, id=sale_id, row=row_idx: self.void_transaction(id, row))
                    actions_layout.addWidget(void_btn)
                
                self.transactions_table.setCellWidget(row_idx, 7, actions_widget)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load transactions: {str(e)}")
    
    def view_transaction_details(self, sale_id):
        """View the details of a transaction"""
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            # Get sale details
            cursor.execute("""
                SELECT s.sale_id, s.invoice_number, s.sale_date, u.full_name, 
                       s.total_amount, s.payment_method, s.status, 
                       s.cash_tendered, s.change_amount, s.notes
                FROM sales s
                JOIN users u ON s.user_id = u.user_id
                WHERE s.sale_id = %s
            """, (sale_id,))
            
            sale = cursor.fetchone()
            
            if not sale:
                QMessageBox.warning(self, "Not Found", "Transaction not found.")
                return
            
            # Get sale items
            cursor.execute("""
                SELECT si.sale_item_id, p.product_name, si.quantity, 
                       si.unit_price, si.subtotal
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                WHERE si.sale_id = %s
            """, (sale_id,))
            
            items = cursor.fetchall()
            
            cursor.close()
            self.db.release_connection(connection)
            
            # Create and show details dialog
            details_dialog = TransactionDetailsDialog(self, sale, items)
            details_dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load transaction details: {str(e)}")
    
    def print_receipt(self, sale_id, invoice_number):
        """Print the receipt for a transaction"""
        try:
            # Call the print_receipt method from POSWidget
            if hasattr(self.parent_widget, 'print_receipt'):
                self.parent_widget.print_receipt(sale_id, invoice_number)
            else:
                QMessageBox.warning(self, "Print Error", "Receipt printing functionality not available.")
        except Exception as e:
            QMessageBox.critical(self, "Print Error", f"Failed to print receipt: {str(e)}")
    
    def void_transaction(self, sale_id, row):
        """Void a transaction"""
        # Check user permissions
        if not self.auth.check_permission(self.user['user_id'], 'cancel_transaction'):
            QMessageBox.warning(self, "Permission Denied", 
                               "You do not have permission to void transactions.")
            return
        
        # Confirm void
        reply = QMessageBox.question(
            self, 
            "Void Transaction", 
            "Are you sure you want to void this transaction?\nThis will return items to inventory and mark the sale as voided.",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                connection = self.db.get_connection()
                cursor = connection.cursor()
                
                try:
                    # Begin transaction
                    connection.begin()
                    
                    # Get sale items to restore inventory
                    cursor.execute("""
                        SELECT product_id, quantity FROM sale_items
                        WHERE sale_id = %s
                    """, (sale_id,))
                    
                    items = cursor.fetchall()
                    
                    # Restore inventory
                    for product_id, quantity in items:
                        cursor.execute("""
                            UPDATE products
                            SET stock_quantity = stock_quantity + %s
                            WHERE product_id = %s
                        """, (quantity, product_id))
                    
                    # Mark sale as voided
                    cursor.execute("""
                        UPDATE sales
                        SET status = 'Voided', void_date = NOW(), voided_by = %s
                        WHERE sale_id = %s
                    """, (self.user['user_id'], sale_id))
                    
                    # Commit transaction
                    connection.commit()
                    
                    # Log activity
                    self.auth.log_activity(
                        self.user['user_id'],
                        "void",
                        "sales",
                        sale_id,
                        f"Voided sale #{sale_id}"
                    )
                    
                    # Update table row
                    self.transactions_table.item(row, 6).setText("Voided")
                    self.transactions_table.item(row, 6).setForeground(Qt.red)
                    
                    # Remove void button
                    actions_widget = self.transactions_table.cellWidget(row, 7)
                    for i in reversed(range(actions_widget.layout().count())):
                        widget = actions_widget.layout().itemAt(i).widget()
                        if widget and widget.toolTip() == "Void Transaction":
                            widget.deleteLater()
                    
                    # Emit signal
                    self.transaction_cancelled.emit(sale_id)
                    
                    QMessageBox.information(self, "Success", "Transaction has been voided successfully.")
                    
                except Exception as e:
                    connection.rollback()
                    raise e
                
                finally:
                    cursor.close()
                    self.db.release_connection(connection)
                
            except Exception as e:
                QMessageBox.critical(self, "Void Error", f"Failed to void transaction: {str(e)}")

class TransactionDetailsDialog(QDialog):
    """Dialog for viewing transaction details"""
    
    def __init__(self, parent=None, sale=None, items=None):
        super().__init__(parent)
        self.sale = sale
        self.items = items
        
        self.setWindowTitle(f"Transaction Details - {sale[1]}")  # sale[1] is invoice_number
        self.setMinimumSize(600, 400)
        self.setWindowIcon(QIcon("resources/icons/receipt.png"))
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)
        
        # Sale information
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_layout = QVBoxLayout(info_frame)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel(f"<h2>{self.sale[1]}</h2>"))  # Invoice number
        
        status_label = QLabel(f"<b>Status: {self.sale[6]}</b>")  # Status
        if self.sale[6] == "Voided":
            status_label.setStyleSheet("color: red;")
        header_layout.addWidget(status_label, alignment=Qt.AlignRight)
        
        info_layout.addLayout(header_layout)
        
        # Sale details
        details_layout = QHBoxLayout()
        
        left_details = QVBoxLayout()
        left_details.addWidget(QLabel(f"<b>Date:</b> {self.sale[2].strftime('%Y-%m-%d %H:%M')}"))  # Date
        left_details.addWidget(QLabel(f"<b>Cashier:</b> {self.sale[3]}"))  # Cashier
        left_details.addWidget(QLabel(f"<b>Payment Method:</b> {self.sale[5]}"))  # Payment method
        details_layout.addLayout(left_details)
        
        right_details = QVBoxLayout()
        right_details.addWidget(QLabel(f"<b>Total Amount:</b> ₱{float(self.sale[4]):.2f}"))  # Total
        
        if self.sale[5] == "Cash" and self.sale[7] is not None:  # If cash payment with tendered amount
            right_details.addWidget(QLabel(f"<b>Cash Tendered:</b> ₱{float(self.sale[7]):.2f}"))
            right_details.addWidget(QLabel(f"<b>Change:</b> ₱{float(self.sale[8]):.2f}"))
        
        details_layout.addLayout(right_details)
        info_layout.addLayout(details_layout)
        
        # Notes if any
        if self.sale[9]:  # Notes field
            info_layout.addWidget(QLabel("<b>Notes:</b>"))
            notes_label = QLabel(self.sale[9])
            notes_label.setWordWrap(True)
            info_layout.addWidget(notes_label)
        
        main_layout.addWidget(info_frame)
        
        # Items table
        main_layout.addWidget(QLabel("<b>Items:</b>"))
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels([
            "ID", "Product", "Quantity", "Unit Price", "Subtotal"
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Populate items
        for row_idx, item in enumerate(self.items):
            self.items_table.insertRow(row_idx)
            
            self.items_table.setItem(row_idx, 0, QTableWidgetItem(str(item[0])))  # ID
            self.items_table.setItem(row_idx, 1, QTableWidgetItem(item[1]))  # Product
            
            qty_item = QTableWidgetItem(str(item[2]))  # Quantity
            qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.items_table.setItem(row_idx, 2, qty_item)
            
            price_item = QTableWidgetItem(f"₱{float(item[3]):.2f}")  # Unit price
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.items_table.setItem(row_idx, 3, price_item)
            
            subtotal_item = QTableWidgetItem(f"₱{float(item[4]):.2f}")  # Subtotal
            subtotal_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.items_table.setItem(row_idx, 4, subtotal_item)
        
        main_layout.addWidget(self.items_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setIcon(QIcon("resources/icons/close.png"))
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)