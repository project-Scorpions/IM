from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, 
                            QDateEdit, QTabWidget, QMessageBox, QHeaderView, QFrame,
                            QFormLayout, QGroupBox, QFileDialog, QSplitter, QCheckBox,
                            QDialog, QDialogButtonBox)
from PyQt5.QtGui import QIcon, QFont, QColor, QPixmap, QPainter
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QPieSeries

import datetime
from database.db_connector import DatabaseConnection
from utils.auth import Authentication

class SaleDetailsDialog(QDialog):
    """Dialog to show detailed sale items with medication information"""
    def __init__(self, parent=None, sale_id=None, invoice=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.sale_id = sale_id
        self.invoice = invoice
        self.setWindowTitle(f"Sale Details - {invoice}")
        self.setMinimumSize(800, 400)
        self.init_ui()
        self.load_sale_details()
        
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        
        # Sale items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(8)
        self.items_table.setHorizontalHeaderLabels([
            "Product ID", "Product Name", "Type", "Unit", "Unit Price", 
            "Quantity", "Subtotal", "Notes"
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.items_table)
        
        # Summary section
        summary_group = QGroupBox("Sale Summary")
        summary_layout = QFormLayout(summary_group)
        
        self.invoice_label = QLabel(self.invoice)
        summary_layout.addRow("Invoice:", self.invoice_label)
        
        self.date_label = QLabel()
        summary_layout.addRow("Date:", self.date_label)
        
        self.cashier_label = QLabel()
        summary_layout.addRow("Cashier:", self.cashier_label)
        
        self.payment_label = QLabel()
        summary_layout.addRow("Payment Method:", self.payment_label)
        
        self.total_label = QLabel()
        self.total_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        summary_layout.addRow("Total Amount:", self.total_label)
        
        layout.addWidget(summary_group)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def load_sale_details(self):
        """Load sale details from database"""
        if not self.sale_id:
            return
        
        try:
            # Get sale header information
            header_query = """
                SELECT s.sale_date, u.full_name as cashier_name, s.payment_method, s.total_amount, s.notes
                FROM sales s
                JOIN users u ON s.user_id = u.user_id
                WHERE s.sale_id = %s
            """
            header = self.db.execute_query(header_query, [self.sale_id], fetchone=True)
            
            if header:
                self.date_label.setText(header[0].strftime("%Y-%m-%d %H:%M"))
                self.cashier_label.setText(header[1])
                self.payment_label.setText(header[2])
                self.total_label.setText(f"₱{float(header[3]):.2f}")
                
            # Check if sale_items table has the medication details columns
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            try:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'sale_items' AND column_name = 'is_generic'
                """)
                has_med_fields = cursor.fetchone() is not None
            except:
                has_med_fields = False
            finally:
                cursor.close()
                self.db.release_connection(connection)
            
            # Get sale items with product details and medication information if available
            if has_med_fields:
                items_query = """
                    SELECT si.product_id, p.product_name, 
                           COALESCE(si.is_generic, p.is_generic) as is_generic,
                           COALESCE(si.unit_measurement, p.unit_measurement) as unit_measurement,
                           si.unit_price, si.quantity, si.subtotal, si.notes
                    FROM sale_items si
                    JOIN products p ON si.product_id = p.product_id
                    WHERE si.sale_id = %s
                    ORDER BY si.item_id
                """
            else:
                items_query = """
                    SELECT si.product_id, p.product_name, 
                           FALSE as is_generic, '' as unit_measurement,
                           si.unit_price, si.quantity, si.subtotal, si.notes
                    FROM sale_items si
                    JOIN products p ON si.product_id = p.product_id
                    WHERE si.sale_id = %s
                    ORDER BY si.item_id
                """
                
            items = self.db.execute_query(items_query, [self.sale_id], fetchall=True)
            
            # Update table
            self.items_table.setRowCount(0)
            
            for row_idx, item in enumerate(items):
                self.items_table.insertRow(row_idx)
                
                product_id, name, is_generic, unit, price, qty, subtotal, notes = item
                
                # Product ID
                self.items_table.setItem(row_idx, 0, QTableWidgetItem(str(product_id)))
                
                # Product Name
                self.items_table.setItem(row_idx, 1, QTableWidgetItem(name))
                
                # Type (Branded/Generic)
                type_text = "Generic" if is_generic else "Branded"
                self.items_table.setItem(row_idx, 2, QTableWidgetItem(type_text))
                
                # Unit Measurement
                self.items_table.setItem(row_idx, 3, QTableWidgetItem(unit or ""))
                
                # Unit Price
                price_item = QTableWidgetItem(f"₱{float(price):.2f}")
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.items_table.setItem(row_idx, 4, price_item)
                
                # Quantity
                qty_item = QTableWidgetItem(str(qty))
                qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.items_table.setItem(row_idx, 5, qty_item)
                
                # Subtotal
                subtotal_item = QTableWidgetItem(f"₱{float(subtotal):.2f}")
                subtotal_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.items_table.setItem(row_idx, 6, subtotal_item)
                
                # Notes
                self.items_table.setItem(row_idx, 7, QTableWidgetItem(notes or ""))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load sale details: {str(e)}")


class ReportsWidget(QWidget):
    """Widget for reports and analytics"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseConnection()
        self.auth = Authentication()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)
        
        # Create tab widget for different reports
        tab_widget = QTabWidget()
        
        # Sales Report Tab
        sales_tab = QWidget()
        sales_layout = QVBoxLayout(sales_tab)
        
        # Date range and filters
        filters_group = QGroupBox("Filters")
        filters_layout = QHBoxLayout(filters_group)
        
        # Date range
        date_layout = QFormLayout()
        
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-30))  # Last 30 days
        date_layout.addRow("From:", self.date_from)
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        date_layout.addRow("To:", self.date_to)
        
        filters_layout.addLayout(date_layout)
        
        # Payment method filter
        payment_layout = QFormLayout()
        
        self.payment_filter = QComboBox()
        self.payment_filter.addItem("All Payment Methods", None)
        self.payment_filter.addItems(["Cash", "Credit Card", "Debit Card", "Mobile Payment"])
        payment_layout.addRow("Payment Method:", self.payment_filter)
        
        # Medication type filter for sales
        self.sales_med_type_filter = QComboBox()
        self.sales_med_type_filter.addItem("All Types", None)
        self.sales_med_type_filter.addItem("Branded", "branded")
        self.sales_med_type_filter.addItem("Generic", "generic")
        payment_layout.addRow("Medication Type:", self.sales_med_type_filter)
        
        filters_layout.addLayout(payment_layout)
        
        # Buttons
        buttons_layout = QVBoxLayout()
        
        generate_btn = QPushButton("Generate Report")
        generate_btn.setIcon(QIcon("resources/icons/report.png"))
        generate_btn.clicked.connect(self.generate_sales_report)
        buttons_layout.addWidget(generate_btn)
        
        export_btn = QPushButton("Export to Excel")
        export_btn.setIcon(QIcon("resources/icons/excel.png"))
        export_btn.clicked.connect(lambda: self.export_report("sales"))
        buttons_layout.addWidget(export_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        refresh_btn.clicked.connect(self.generate_sales_report)
        refresh_btn.setToolTip("Refresh sales report with current filters")
        buttons_layout.addWidget(refresh_btn)
        
        filters_layout.addLayout(buttons_layout)
        
        sales_layout.addWidget(filters_group)
        
        # Sales report view (split into table and chart)
        sales_splitter = QSplitter(Qt.Vertical)
        
        # Sales table
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(8)  # Added 2 columns for medication type breakdown
        self.sales_table.setHorizontalHeaderLabels([
            "Invoice", "Date", "Cashier", "Payment Method", "Total Amount", "Items",
            "Branded Items", "Generic Items"
        ])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.sales_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.sales_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.sales_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sales_table.doubleClicked.connect(self.show_sale_details)
        
        # Add tooltip to explain double-click functionality
        self.sales_table.setToolTip("Double-click a row to view detailed sale information")
        
        sales_splitter.addWidget(self.sales_table)
        
        # Sales chart container
        chart_container = QWidget()
        chart_layout = QVBoxLayout(chart_container)
        
        # Chart selection
        chart_selection_layout = QHBoxLayout()
        chart_selection_layout.addWidget(QLabel("Chart Type:"))
        
        self.sales_chart_type = QComboBox()
        self.sales_chart_type.addItems([
            "Daily Sales", 
            "Payment Method Distribution",
            "Branded vs Generic Sales"  # New chart type
        ])
        self.sales_chart_type.currentIndexChanged.connect(self.update_sales_chart)
        chart_selection_layout.addWidget(self.sales_chart_type)
        
        chart_layout.addLayout(chart_selection_layout)
        
        # Chart view
        self.sales_chart_view = QChartView()
        self.sales_chart_view.setRenderHint(QPainter.Antialiasing)
        chart_layout.addWidget(self.sales_chart_view)
        
        sales_splitter.addWidget(chart_container)
        sales_splitter.setSizes([300, 300])
        
        sales_layout.addWidget(sales_splitter)
        
        # Add sales tab
        tab_widget.addTab(sales_tab, "Sales Report")
        
        # Inventory Report Tab
        inventory_tab = QWidget()
        inventory_layout = QVBoxLayout(inventory_tab)
        
        # Inventory filters
        inv_filters_group = QGroupBox("Filters")
        inv_filters_layout = QHBoxLayout(inv_filters_group)
        
        # Category filter
        category_layout = QFormLayout()
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories", None)
        self.load_categories()
        category_layout.addRow("Category:", self.category_filter)
        
        inv_filters_layout.addLayout(category_layout)
        
        # Stock level filter
        stock_layout = QFormLayout()
        
        self.stock_filter = QComboBox()
        self.stock_filter.addItem("All Stock Levels", None)
        self.stock_filter.addItem("Low Stock", "low")
        self.stock_filter.addItem("In Stock", "in")
        self.stock_filter.addItem("Out of Stock", "out")
        stock_layout.addRow("Stock Level:", self.stock_filter)
        
        # Medication type filter
        self.med_type_filter = QComboBox()
        self.med_type_filter.addItem("All Types", None)
        self.med_type_filter.addItem("Branded", "branded")
        self.med_type_filter.addItem("Generic", "generic")
        stock_layout.addRow("Medication Type:", self.med_type_filter)
        
        inv_filters_layout.addLayout(stock_layout)
        
        # Expiry filter
        expiry_layout = QFormLayout()
        
        self.expiry_filter = QComboBox()
        self.expiry_filter.addItem("All Expiry Dates", None)
        self.expiry_filter.addItem("Expired", "expired")
        self.expiry_filter.addItem("Expiring Soon (30 days)", "soon")
        self.expiry_filter.addItem("Valid", "valid")
        expiry_layout.addRow("Expiry Status:", self.expiry_filter)
        
        inv_filters_layout.addLayout(expiry_layout)
        
        # Status filter
        status_layout = QFormLayout()
        self.include_inactive_checkbox = QCheckBox("Include inactive products")
        self.include_inactive_checkbox.setChecked(False)
        status_layout.addRow(self.include_inactive_checkbox)
        
        inv_filters_layout.addLayout(status_layout)
        
        # Buttons
        inv_buttons_layout = QVBoxLayout()
        
        inv_generate_btn = QPushButton("Generate Report")
        inv_generate_btn.setIcon(QIcon("resources/icons/report.png"))
        inv_generate_btn.clicked.connect(self.generate_inventory_report)
        inv_buttons_layout.addWidget(inv_generate_btn)
        
        inv_export_btn = QPushButton("Export to Excel")
        inv_export_btn.setIcon(QIcon("resources/icons/excel.png"))
        inv_export_btn.clicked.connect(lambda: self.export_report("inventory"))
        inv_buttons_layout.addWidget(inv_export_btn)
        
        inv_refresh_btn = QPushButton("Refresh")
        inv_refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        inv_refresh_btn.clicked.connect(self.generate_inventory_report)
        inv_refresh_btn.setToolTip("Refresh inventory report with current filters")
        inv_buttons_layout.addWidget(inv_refresh_btn)
        
        inv_filters_layout.addLayout(inv_buttons_layout)
        
        inventory_layout.addWidget(inv_filters_group)
        
        # Inventory report view (split into table and chart)
        inventory_splitter = QSplitter(Qt.Vertical)
        
        # Inventory table - Updated with medication type and unit measurement
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(9)
        self.inventory_table.setHorizontalHeaderLabels([
            "ID", "Product Name", "Type", "Unit Measurement", "Category", 
            "Unit Price", "Cost Price", "Stock Quantity", "Expiry Date"
        ])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.inventory_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.inventory_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        inventory_splitter.addWidget(self.inventory_table)
        
        # Inventory chart container
        inv_chart_container = QWidget()
        inv_chart_layout = QVBoxLayout(inv_chart_container)
        
        # Chart selection
        inv_chart_selection_layout = QHBoxLayout()
        inv_chart_selection_layout.addWidget(QLabel("Chart Type:"))
        
        self.inv_chart_type = QComboBox()
        self.inv_chart_type.addItems([
            "Stock by Category", 
            "Value by Category",
            "Branded vs Generic Distribution"  # New chart type
        ])
        self.inv_chart_type.currentIndexChanged.connect(self.update_inventory_chart)
        inv_chart_selection_layout.addWidget(self.inv_chart_type)
        
        inv_chart_layout.addLayout(inv_chart_selection_layout)
        
        # Chart view
        self.inventory_chart_view = QChartView()
        self.inventory_chart_view.setRenderHint(QPainter.Antialiasing)
        inv_chart_layout.addWidget(self.inventory_chart_view)
        
        inventory_splitter.addWidget(inv_chart_container)
        inventory_splitter.setSizes([300, 300])
        
        inventory_layout.addWidget(inventory_splitter)
        
        # Add inventory tab
        tab_widget.addTab(inventory_tab, "Inventory Report")
        
        # Add tab widget to main layout
        main_layout.addWidget(tab_widget)
        
        # Connect tab changed signal
        tab_widget.currentChanged.connect(self.tab_changed)
    
    def tab_changed(self, index):
        """Handle tab changes"""
        if index == 0:  # Sales report
            self.generate_sales_report()
        elif index == 1:  # Inventory report
            self.generate_inventory_report()
    
    def load_categories(self):
        """Load categories into filter dropdown"""
        try:
            query = "SELECT category_id, name FROM categories ORDER BY name"
            categories = self.db.execute_query(query, fetchall=True)
            
            for category_id, name in categories:
                self.category_filter.addItem(name, category_id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load categories: {str(e)}")
    
    def show_sale_details(self, index):
        """Show detailed sale information when a row is double-clicked"""
        row = index.row()
        invoice = self.sales_table.item(row, 0).text()
        
        # Get sale_id from database using invoice number
        try:
            query = "SELECT sale_id FROM sales WHERE invoice_number = %s"
            result = self.db.execute_query(query, [invoice], fetchone=True)
            
            if result and result[0]:
                sale_id = result[0]
                
                # Show sale details dialog
                details_dialog = SaleDetailsDialog(self, sale_id, invoice)
                details_dialog.exec_()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load sale details: {str(e)}")
    
    def generate_sales_report(self):
        """Generate the sales report"""
        try:
            # Get filter values
            date_from = self.date_from.date().toString("yyyy-MM-dd")
            date_to = self.date_to.date().toString("yyyy-MM-dd")
            payment_method = self.payment_filter.currentText()
            med_type_filter = self.sales_med_type_filter.currentData()
            
            # Check if sale_items table has the medication columns
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            try:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'sale_items' AND column_name = 'is_generic'
                """)
                has_med_fields = cursor.fetchone() is not None
            except:
                has_med_fields = False
            finally:
                cursor.close()
                self.db.release_connection(connection)
            
            # Build query with medication type information
            if has_med_fields:
                query = """
                    SELECT s.sale_id, s.invoice_number, s.sale_date, u.full_name as cashier,
                           s.payment_method, s.total_amount, COUNT(si.item_id) as item_count,
                           SUM(CASE WHEN si.is_generic = FALSE THEN 1 ELSE 0 END) as branded_count,
                           SUM(CASE WHEN si.is_generic = TRUE THEN 1 ELSE 0 END) as generic_count
                    FROM sales s
                    JOIN users u ON s.user_id = u.user_id
                    JOIN sale_items si ON s.sale_id = si.sale_id
                    WHERE s.sale_date::date BETWEEN %s AND %s
                """
            else:
                query = """
                    SELECT s.sale_id, s.invoice_number, s.sale_date, u.full_name as cashier,
                           s.payment_method, s.total_amount, COUNT(si.item_id) as item_count,
                           0 as branded_count, 0 as generic_count
                    FROM sales s
                    JOIN users u ON s.user_id = u.user_id
                    JOIN sale_items si ON s.sale_id = si.sale_id
                    WHERE s.sale_date::date BETWEEN %s AND %s
                """
            
            params = [date_from, date_to]
            
            if payment_method != "All Payment Methods":
                query += " AND s.payment_method = %s"
                params.append(payment_method)
            
            if has_med_fields and med_type_filter:
                if med_type_filter == "branded":
                    query += " AND si.is_generic = FALSE"
                elif med_type_filter == "generic":
                    query += " AND si.is_generic = TRUE"
            
            query += " GROUP BY s.sale_id, s.invoice_number, s.sale_date, u.full_name, s.payment_method, s.total_amount"
            query += " ORDER BY s.sale_date DESC"
            
            sales = self.db.execute_query(query, params, fetchall=True)
            
            # Update table
            self.sales_table.setRowCount(0)
            
            for row_idx, sale in enumerate(sales):
                self.sales_table.insertRow(row_idx)
                
                sale_id, invoice, date, cashier, payment, total, item_count, branded_count, generic_count = sale
                
                # Invoice
                self.sales_table.setItem(row_idx, 0, QTableWidgetItem(invoice))
                
                # Date
                self.sales_table.setItem(row_idx, 1, QTableWidgetItem(date.strftime("%Y-%m-%d %H:%M")))
                
                # Cashier
                self.sales_table.setItem(row_idx, 2, QTableWidgetItem(cashier))
                
                # Payment Method
                self.sales_table.setItem(row_idx, 3, QTableWidgetItem(payment))
                
                # Total Amount
                total_item = QTableWidgetItem(f"₱{float(total):.2f}")
                total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.sales_table.setItem(row_idx, 4, total_item)
                
                # Items
                self.sales_table.setItem(row_idx, 5, QTableWidgetItem(str(item_count)))
                
                # Branded Items Count
                self.sales_table.setItem(row_idx, 6, QTableWidgetItem(str(int(branded_count))))
                
                # Generic Items Count
                self.sales_table.setItem(row_idx, 7, QTableWidgetItem(str(int(generic_count))))
            
            # Update chart
            self.update_sales_chart()
            
            # Log activity
            self.auth.log_activity(
                self.user['user_id'],
                "report",
                "sales",
                None,
                f"Generated sales report from {date_from} to {date_to}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate sales report: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def update_sales_chart(self):
        """Update the sales chart based on selected type"""
        chart_type = self.sales_chart_type.currentText()
        
        try:
            if chart_type == "Daily Sales":
                self.create_daily_sales_chart()
            elif chart_type == "Payment Method Distribution":
                self.create_payment_distribution_chart()
            elif chart_type == "Branded vs Generic Sales":
                self.create_branded_vs_generic_sales_chart()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update sales chart: {str(e)}")
    
    def create_daily_sales_chart(self):
        """Create chart showing daily sales"""
        try:
            # Get filter values
            date_from = self.date_from.date().toString("yyyy-MM-dd")
            date_to = self.date_to.date().toString("yyyy-MM-dd")
            payment_method = self.payment_filter.currentText()
            med_type_filter = self.sales_med_type_filter.currentData()
            
            # Build query
            query = """
                SELECT DATE(s.sale_date) as sale_day, SUM(s.total_amount) as daily_total
                FROM sales s
                WHERE s.sale_date::date BETWEEN %s AND %s
            """
            
            params = [date_from, date_to]
            
            if payment_method != "All Payment Methods":
                query += " AND s.payment_method = %s"
                params.append(payment_method)
            
            # Handle medication type filter
            if med_type_filter:
                query = """
                    SELECT DATE(s.sale_date) as sale_day, SUM(si.subtotal) as daily_total
                    FROM sales s
                    JOIN sale_items si ON s.sale_id = si.sale_id
                    WHERE s.sale_date::date BETWEEN %s AND %s
                """
                
                if payment_method != "All Payment Methods":
                    query += " AND s.payment_method = %s"
                
                if med_type_filter == "branded":
                    query += " AND si.is_generic = FALSE"
                elif med_type_filter == "generic":
                    query += " AND si.is_generic = TRUE"
                
            query += " GROUP BY sale_day ORDER BY sale_day"
            
            daily_sales = self.db.execute_query(query, params, fetchall=True)
            
            # Create chart
            chart = QChart()
            chart.setTitle("Daily Sales")
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            # Create bar series
            bar_set = QBarSet("Sales")
            
            # Categories (dates)
            categories = []
            
            # Add data to bar set
            for day, total in daily_sales:
                bar_set.append(float(total))
                categories.append(day.strftime("%b %d"))
            
            # Create series and add to chart
            series = QBarSeries()
            series.append(bar_set)
            chart.addSeries(series)
            
            # Create axes
            axis_x = QBarCategoryAxis()
            axis_x.append(categories)
            chart.addAxis(axis_x, Qt.AlignBottom)
            series.attachAxis(axis_x)
            
            axis_y = QValueAxis()
            axis_y.setTitleText("Amount (₱)")
            axis_y.setLabelFormat("₱%.2f")
            chart.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_y)
            
            # Set the chart in the view
            self.sales_chart_view.setChart(chart)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create daily sales chart: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def create_payment_distribution_chart(self):
        """Create chart showing distribution by payment method"""
        try:
            # Get filter values
            date_from = self.date_from.date().toString("yyyy-MM-dd")
            date_to = self.date_to.date().toString("yyyy-MM-dd")
            med_type_filter = self.sales_med_type_filter.currentData()
            
            # Build query
            query = """
                SELECT s.payment_method, SUM(s.total_amount) as total
                FROM sales s
            """
            
            params = [date_from, date_to]
            
            # Handle medication type filter
            if med_type_filter:
                query = """
                    SELECT s.payment_method, SUM(si.subtotal) as total
                    FROM sales s
                    JOIN sale_items si ON s.sale_id = si.sale_id
                """
                
                query += " WHERE s.sale_date::date BETWEEN %s AND %s"
                
                if med_type_filter == "branded":
                    query += " AND si.is_generic = FALSE"
                elif med_type_filter == "generic":
                    query += " AND si.is_generic = TRUE"
            else:
                query += " WHERE s.sale_date::date BETWEEN %s AND %s"
                
            query += " GROUP BY s.payment_method ORDER BY total DESC"
            
            payment_totals = self.db.execute_query(query, params, fetchall=True)
            
            # Create chart
            chart = QChart()
            chart.setTitle("Sales by Payment Method")
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            # Create pie series
            series = QPieSeries()
            
            # Add data to pie series
            for payment_method, total in payment_totals:
                series.append(f"{payment_method}: ₱{float(total):.2f}", float(total))
            
            # Customize slices
            for slice in series.slices():
                slice.setLabelVisible(True)
            
            # Add series to chart
            chart.addSeries(series)
            
            # Set the chart in the view
            self.sales_chart_view.setChart(chart)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create payment distribution chart: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def create_branded_vs_generic_sales_chart(self):
        """Create chart showing branded vs generic sales"""
        try:
            # Get filter values
            date_from = self.date_from.date().toString("yyyy-MM-dd")
            date_to = self.date_to.date().toString("yyyy-MM-dd")
            payment_method = self.payment_filter.currentText()
            
            # Check if sale_items table has the medication columns
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            try:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'sale_items' AND column_name = 'is_generic'
                """)
                has_med_fields = cursor.fetchone() is not None
            except:
                has_med_fields = False
            finally:
                cursor.close()
                self.db.release_connection(connection)
            
            if not has_med_fields:
                chart = QChart()
                chart.setTitle("Branded vs Generic Sales")
                chart.setAnimationOptions(QChart.SeriesAnimations)
                
                # Add a message to the chart
                no_data_text = QLabel("Medication type data is not available")
                no_data_text.setAlignment(Qt.AlignCenter)
                no_data_text.setStyleSheet("font-size: 14px; color: #888888;")
                self.sales_chart_view.setChart(chart)
                return
            
            # Build query
            query = """
                SELECT 
                    CASE WHEN si.is_generic THEN 'Generic' ELSE 'Branded' END as med_type,
                    SUM(si.subtotal) as total
                FROM sales s
                JOIN sale_items si ON s.sale_id = si.sale_id
                WHERE s.sale_date::date BETWEEN %s AND %s
            """
            
            params = [date_from, date_to]
            
            if payment_method != "All Payment Methods":
                query += " AND s.payment_method = %s"
                params.append(payment_method)
                
            query += " GROUP BY med_type"
            
            med_type_totals = self.db.execute_query(query, params, fetchall=True)
            
            # Create chart
            chart = QChart()
            chart.setTitle("Branded vs Generic Sales")
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            # Create pie series
            series = QPieSeries()
            
            # Add data to pie series
            for med_type, total in med_type_totals:
                series.append(f"{med_type}: ₱{float(total):.2f}", float(total))
            
            # Customize slices and add colors
            for i, slice in enumerate(series.slices()):
                slice.setLabelVisible(True)
                if i == 0:  # Branded (typically red)
                    slice.setBrush(QColor("#e74c3c"))
                else:  # Generic (typically blue/green)
                    slice.setBrush(QColor("#3498db"))
            
            # Add series to chart
            chart.addSeries(series)
            
            # Set the chart in the view
            self.sales_chart_view.setChart(chart)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create branded vs generic sales chart: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def generate_inventory_report(self):
        """Generate the inventory report"""
        try:
            # Get filter values
            category_id = self.category_filter.currentData()
            stock_filter = self.stock_filter.currentData()
            expiry_filter = self.expiry_filter.currentData()
            med_type_filter = self.med_type_filter.currentData()
            
            # Check if products table has the medication columns
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            try:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'products' AND column_name = 'is_generic'
                """)
                has_med_fields = cursor.fetchone() is not None
            except:
                has_med_fields = False
            finally:
                cursor.close()
                self.db.release_connection(connection)
            
            # Build query
            if has_med_fields:
                query = """
                    SELECT p.product_id, p.product_name, p.is_generic, p.unit_measurement,
                           c.name as category_name, p.unit_price, p.cost_price, 
                           p.stock_quantity, p.expiry_date, p.is_active
                    FROM products p
                    LEFT JOIN categories c ON p.category_id = c.category_id
                    WHERE 1=1
                """
            else:
                query = """
                    SELECT p.product_id, p.product_name, FALSE as is_generic, '' as unit_measurement,
                           c.name as category_name, p.unit_price, p.cost_price, 
                           p.stock_quantity, p.expiry_date, p.is_active
                    FROM products p
                    LEFT JOIN categories c ON p.category_id = c.category_id
                    WHERE 1=1
                """
            
            params = []
            
            # Add active/inactive filter
            if not self.include_inactive_checkbox.isChecked():
                query += " AND p.is_active = TRUE"
            
            # Add category filter
            if category_id is not None:
                query += " AND p.category_id = %s"
                params.append(category_id)
            
            # Add stock filter
            if stock_filter:
                if stock_filter == "low":
                    query += " AND p.stock_quantity <= p.reorder_level AND p.stock_quantity > 0"
                elif stock_filter == "out":
                    query += " AND p.stock_quantity <= 0"
                elif stock_filter == "in":
                    query += " AND p.stock_quantity > p.reorder_level"
            
            # Add medication type filter
            if has_med_fields and med_type_filter:
                if med_type_filter == "branded":
                    query += " AND p.is_generic = FALSE"
                elif med_type_filter == "generic":
                    query += " AND p.is_generic = TRUE"
            
            # Add expiry filter
            current_date = datetime.datetime.now().date()
            if expiry_filter:
                if expiry_filter == "expired":
                    query += " AND p.expiry_date < %s"
                    params.append(current_date)
                elif expiry_filter == "soon":
                    thirty_days_later = current_date + datetime.timedelta(days=30)
                    query += " AND p.expiry_date >= %s AND p.expiry_date <= %s"
                    params.append(current_date)
                    params.append(thirty_days_later)
                elif expiry_filter == "valid":
                    query += " AND p.expiry_date > %s"
                    params.append(current_date)
            
            query += " ORDER BY p.product_name"
            
            products = self.db.execute_query(query, params, fetchall=True)
            
            # Update table
            self.inventory_table.setRowCount(0)
            
            for row_idx, product in enumerate(products):
                self.inventory_table.insertRow(row_idx)
                
                # Unpack all values from the query result
                product_id, name, is_generic, unit_measurement, category, unit_price, cost_price, stock, expiry, is_active = product
                
                # ID
                self.inventory_table.setItem(row_idx, 0, QTableWidgetItem(str(product_id)))
                
                # Product Name
                product_name_item = QTableWidgetItem(name)
                if not is_active:
                    product_name_item.setForeground(QColor("#888888"))
                    font = product_name_item.font()
                    font.setStrikeOut(True)
                    product_name_item.setFont(font)
                self.inventory_table.setItem(row_idx, 1, product_name_item)
                
                # Medication Type (Branded/Generic)
                type_text = "Generic" if is_generic else "Branded"
                type_item = QTableWidgetItem(type_text)
                if is_generic:
                    type_item.setBackground(QColor("#d5f5e3"))  # Light green for generic
                else:
                    type_item.setBackground(QColor("#f5e3e3"))  # Light red for branded
                self.inventory_table.setItem(row_idx, 2, type_item)
                
                # Unit Measurement
                self.inventory_table.setItem(row_idx, 3, QTableWidgetItem(unit_measurement or ""))
                
                # Category
                self.inventory_table.setItem(row_idx, 4, QTableWidgetItem(category or "Uncategorized"))
                
                # Unit Price
                price_item = QTableWidgetItem(f"₱{float(unit_price):.2f}")
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.inventory_table.setItem(row_idx, 5, price_item)
                
                # Cost Price
                cost_item = QTableWidgetItem(f"₱{float(cost_price):.2f}")
                cost_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.inventory_table.setItem(row_idx, 6, cost_item)
                
                # Stock Quantity
                stock_item = QTableWidgetItem(str(stock))
                stock_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.inventory_table.setItem(row_idx, 7, stock_item)
                
                # Expiry Date
                expiry_text = expiry.strftime("%Y-%m-%d") if expiry else "N/A"
                self.inventory_table.setItem(row_idx, 8, QTableWidgetItem(expiry_text))
            
            # Update chart
            self.update_inventory_chart()
            
            # Log activity
            self.auth.log_activity(
                self.user['user_id'],
                "report",
                "inventory",
                None,
                "Generated inventory report"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate inventory report: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def update_inventory_chart(self):
        """Update the inventory chart based on selected type"""
        chart_type = self.inv_chart_type.currentText()
        
        try:
            if chart_type == "Stock by Category":
                self.create_stock_by_category_chart()
            elif chart_type == "Value by Category":
                self.create_value_by_category_chart()
            elif chart_type == "Branded vs Generic Distribution":
                self.create_branded_vs_generic_distribution_chart()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update inventory chart: {str(e)}")
    
    def create_stock_by_category_chart(self):
        """Create chart showing stock levels by category"""
        try:
            # Build query
            query = """
                SELECT c.name, SUM(p.stock_quantity) as total_stock
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                WHERE p.is_active = TRUE
                GROUP BY c.name
                ORDER BY total_stock DESC
            """
            
            category_stock = self.db.execute_query(query, fetchall=True)
            
            # Create chart
            chart = QChart()
            chart.setTitle("Stock Quantity by Category")
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            # Create bar series
            bar_set = QBarSet("Stock")
            
            # Categories
            categories = []
            
            # Add data to bar set
            for category, stock in category_stock:
                bar_set.append(float(stock))
                categories.append(category or "Uncategorized")
            
            # Create series and add to chart
            series = QBarSeries()
            series.append(bar_set)
            chart.addSeries(series)
            
            # Create axes
            axis_x = QBarCategoryAxis()
            axis_x.append(categories)
            chart.addAxis(axis_x, Qt.AlignBottom)
            series.attachAxis(axis_x)
            
            axis_y = QValueAxis()
            axis_y.setTitleText("Stock Quantity")
            axis_y.setLabelFormat("%d")
            chart.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_y)
            
            # Set the chart in the view
            self.inventory_chart_view.setChart(chart)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create stock by category chart: {str(e)}")
    
    def create_value_by_category_chart(self):
        """Create chart showing inventory value by category"""
        try:
            # Build query
            query = """
                SELECT c.name, SUM(p.unit_price * p.stock_quantity) as total_value
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                WHERE p.is_active = TRUE
                GROUP BY c.name
                ORDER BY total_value DESC
            """
            
            category_value = self.db.execute_query(query, fetchall=True)
            
            # Create chart
            chart = QChart()
            chart.setTitle("Inventory Value by Category")
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            # Create pie series
            series = QPieSeries()
            
            # Add data to pie series
            for category, value in category_value:
                cat_name = category or "Uncategorized"
                series.append(f"{cat_name}: ₱{float(value):.2f}", float(value))
            
            # Customize slices
            for slice in series.slices():
                slice.setLabelVisible(True)
            
            # Add series to chart
            chart.addSeries(series)
            
            # Set the chart in the view
            self.inventory_chart_view.setChart(chart)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create value by category chart: {str(e)}")
    
    def create_branded_vs_generic_distribution_chart(self):
        """Create chart showing branded vs generic product distribution"""
        try:
            # Check if products table has the medication columns
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            try:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'products' AND column_name = 'is_generic'
                """)
                has_med_fields = cursor.fetchone() is not None
            except:
                has_med_fields = False
            finally:
                cursor.close()
                self.db.release_connection(connection)
            
            if not has_med_fields:
                chart = QChart()
                chart.setTitle("Branded vs Generic Distribution")
                chart.setAnimationOptions(QChart.SeriesAnimations)
                
                # Add a message to the chart
                no_data_text = QLabel("Medication type data is not available")
                no_data_text.setAlignment(Qt.AlignCenter)
                no_data_text.setStyleSheet("font-size: 14px; color: #888888;")
                self.inventory_chart_view.setChart(chart)
                return
            
            # Build query
            query = """
                SELECT 
                    CASE WHEN p.is_generic THEN 'Generic' ELSE 'Branded' END as med_type,
                    COUNT(*) as count,
                    SUM(p.stock_quantity) as total_stock,
                    SUM(p.unit_price * p.stock_quantity) as total_value
                FROM products p
                WHERE p.is_active = TRUE
                GROUP BY med_type
                ORDER BY med_type
            """
            
            med_type_data = self.db.execute_query(query, fetchall=True)
            
            # Create chart
            chart = QChart()
            chart.setTitle("Branded vs Generic Distribution")
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            # Create bar series for product count
            count_set = QBarSet("Product Count")
            stock_set = QBarSet("Stock Quantity")
            value_set = QBarSet("Inventory Value (₱ '000s)")
            
            # Set colors
            count_set.setColor(QColor("#3498db"))  # Blue
            stock_set.setColor(QColor("#2ecc71"))  # Green
            value_set.setColor(QColor("#e74c3c"))  # Red
            
            # Categories
            categories = []
            
            # Add data to bar sets
            for med_type, count, stock, value in med_type_data:
                categories.append(med_type)
                count_set.append(float(count))
                stock_set.append(float(stock))
                value_set.append(float(value) / 1000)  # Convert to thousands for better display
            
            # Create series and add to chart
            series = QBarSeries()
            series.append(count_set)
            series.append(stock_set)
            series.append(value_set)
            chart.addSeries(series)
            
            # Create axes
            axis_x = QBarCategoryAxis()
            axis_x.append(categories)
            chart.addAxis(axis_x, Qt.AlignBottom)
            series.attachAxis(axis_x)
            
            axis_y = QValueAxis()
            axis_y.setTitleText("Count / Value (₱ '000s)")
            chart.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_y)
            
            # Set the chart in the view
            self.inventory_chart_view.setChart(chart)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create branded vs generic distribution chart: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def export_report(self, report_type):
        """Export report to Excel"""
        try:
            import pandas as pd
            from datetime import datetime
            
            # Get save file location
            filename, _ = QFileDialog.getSaveFileName(
                self,
                f"Export {report_type.capitalize()} Report",
                f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "Excel Files (*.xlsx)"
            )
            
            if not filename:
                return
            
            if report_type == "sales":
                # Get data from sales table
                data = []
                headers = []
                
                for col in range(self.sales_table.columnCount()):
                    headers.append(self.sales_table.horizontalHeaderItem(col).text())
                
                for row in range(self.sales_table.rowCount()):
                    row_data = []
                    for col in range(self.sales_table.columnCount()):
                        item = self.sales_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)
                
                df = pd.DataFrame(data, columns=headers)
                
                # Clean up the Total Amount column for proper formatting
                df['Total Amount'] = df['Total Amount'].str.replace('₱', '').astype(float)
                
                # Export detailed information
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    # Write sales summary sheet
                    df.to_excel(writer, sheet_name='Sales Summary', index=False)
                    
                    # Get detailed sales data with medication information
                    try:
                        detailed_query = """
                            SELECT s.invoice_number, s.sale_date, p.product_name,
                                   CASE WHEN si.is_generic THEN 'Generic' ELSE 'Branded' END as med_type,
                                   si.unit_measurement, si.unit_price, si.quantity, si.subtotal
                            FROM sales s
                            JOIN sale_items si ON s.sale_id = si.sale_id
                            JOIN products p ON si.product_id = p.product_id
                            WHERE s.sale_date::date BETWEEN %s AND %s
                            ORDER BY s.sale_date DESC, s.invoice_number, p.product_name
                        """
                        
                        date_from = self.date_from.date().toString("yyyy-MM-dd")
                        date_to = self.date_to.date().toString("yyyy-MM-dd")
                        payment_method = self.payment_filter.currentText()
                        
                        params = [date_from, date_to]
                        
                        if payment_method != "All Payment Methods":
                            detailed_query += " AND s.payment_method = %s"
                            params.append(payment_method)
                            
                        details = self.db.execute_query(detailed_query, params, fetchall=True)
                        
                        detail_columns = [
                            "Invoice", "Date", "Product Name", "Medication Type", 
                            "Unit Measurement", "Unit Price", "Quantity", "Subtotal"
                        ]
                        
                        details_df = pd.DataFrame(details, columns=detail_columns)
                        
                        # Write details to second sheet
                        details_df.to_excel(writer, sheet_name='Sale Items Details', index=False)
                        
                        # Auto-adjust columns' width for both sheets
                        for sheet_name in writer.sheets:
                            worksheet = writer.sheets[sheet_name]
                            for idx, col in enumerate(worksheet.columns, 1):
                                max_len = 0
                                for cell in col:
                                    if cell.value:
                                        max_len = max(max_len, len(str(cell.value)))
                                worksheet.column_dimensions[worksheet.cell(row=1, column=idx).column_letter].width = max_len + 3
                        
                    except Exception as e:
                        print(f"Could not export detailed sales data: {e}")
                
                # Log activity
                self.auth.log_activity(
                    self.user['user_id'],
                    "export",
                    "sales",
                    None,
                    f"Exported sales report to Excel: {filename}"
                )
                
            elif report_type == "inventory":
                # Get data from inventory table
                data = []
                headers = []
                
                for col in range(self.inventory_table.columnCount()):
                    headers.append(self.inventory_table.horizontalHeaderItem(col).text())
                
                for row in range(self.inventory_table.rowCount()):
                    row_data = []
                    for col in range(self.inventory_table.columnCount()):
                        item = self.inventory_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)
                
                df = pd.DataFrame(data, columns=headers)
                
                # Clean up the price columns for proper formatting
                df['Unit Price'] = df['Unit Price'].str.replace('₱', '').astype(float)
                df['Cost Price'] = df['Cost Price'].str.replace('₱', '').astype(float)

                # Write to Excel
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Inventory Report', index=False)
                    
                    # Calculate summary statistics
                    summary_data = {
                        'Statistic': [
                            'Total Products', 
                            'Total Active Products',
                            'Out of Stock Products',
                            'Low Stock Products',
                            'Branded Products',
                            'Generic Products',
                            'Total Inventory Value',
                            'Branded Inventory Value',
                            'Generic Inventory Value',
                            'Report Date'
                        ],
                        'Value': [
                            len(df),
                            len(df),
                            len(df[df['Stock Quantity'] == '0']),
                            0,  # will calculate 
                            len(df[df['Type'] == 'Branded']),
                            len(df[df['Type'] == 'Generic']),
                            df['Unit Price'].astype(float) * df['Stock Quantity'].astype(int),
                            df[df['Type'] == 'Branded']['Unit Price'].astype(float) * df[df['Type'] == 'Branded']['Stock Quantity'].astype(int),
                            df[df['Type'] == 'Generic']['Unit Price'].astype(float) * df[df['Type'] == 'Generic']['Stock Quantity'].astype(int),
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        ]
                    }
                    
                    # Convert to DataFrame and write to second sheet
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Summary Statistics', index=False)
                    
                    # Auto-adjust columns' width
                    for sheet_name in writer.sheets:
                        worksheet = writer.sheets[sheet_name]
                        for idx, col in enumerate(worksheet.columns, 1):
                            max_len = 0
                            for cell in col:
                                if cell.value:
                                    max_len = max(max_len, len(str(cell.value)))
                            worksheet.column_dimensions[worksheet.cell(row=1, column=idx).column_letter].width = max_len + 3
                
                # Log activity
                self.auth.log_activity(
                    self.user['user_id'],
                    "export",
                    "inventory",
                    None,
                    f"Exported inventory report to Excel: {filename}"
                )
            
            QMessageBox.information(self, "Export Successful", f"Report exported successfully to {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export report: {str(e)}")
            import traceback
            print(traceback.format_exc())