from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, 
                            QDateEdit, QTabWidget, QMessageBox, QHeaderView, QFrame,
                            QFormLayout, QGroupBox, QFileDialog, QSplitter)
from PyQt5.QtGui import QIcon, QFont, QColor, QPixmap, QPainter
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QPieSeries

import datetime
from database.db_connector import DatabaseConnection
from utils.auth import Authentication

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
        
        filters_layout.addLayout(buttons_layout)
        
        sales_layout.addWidget(filters_group)
        
        # Sales report view (split into table and chart)
        sales_splitter = QSplitter(Qt.Vertical)
        
        # Sales table
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(6)
        self.sales_table.setHorizontalHeaderLabels([
            "Invoice", "Date", "Cashier", "Payment Method", "Total Amount", "Items"
        ])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.sales_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.sales_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        sales_splitter.addWidget(self.sales_table)
        
        # Sales chart container
        chart_container = QWidget()
        chart_layout = QVBoxLayout(chart_container)
        
        # Chart selection
        chart_selection_layout = QHBoxLayout()
        chart_selection_layout.addWidget(QLabel("Chart Type:"))
        
        self.sales_chart_type = QComboBox()
        self.sales_chart_type.addItems(["Daily Sales", "Payment Method Distribution"])
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
        
        inv_filters_layout.addLayout(inv_buttons_layout)
        
        inventory_layout.addWidget(inv_filters_group)
        
        # Inventory report view (split into table and chart)
        inventory_splitter = QSplitter(Qt.Vertical)
        
        # Inventory table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(7)
        self.inventory_table.setHorizontalHeaderLabels([
            "ID", "Product Name", "Category", "Unit Price", "Cost Price", 
            "Stock Quantity", "Expiry Date"
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
        self.inv_chart_type.addItems(["Stock by Category", "Value by Category"])
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
    
    def generate_sales_report(self):
        """Generate the sales report"""
        try:
            # Get filter values
            date_from = self.date_from.date().toString("yyyy-MM-dd")
            date_to = self.date_to.date().toString("yyyy-MM-dd")
            payment_method = self.payment_filter.currentText()
            
            # Build query
            query = """
                SELECT s.sale_id, s.invoice_number, s.sale_date, u.full_name as cashier,
                       s.payment_method, s.total_amount, COUNT(si.item_id) as item_count
                FROM sales s
                JOIN users u ON s.user_id = u.user_id
                JOIN sale_items si ON s.sale_id = si.sale_id
                WHERE s.sale_date::date BETWEEN %s AND %s
            """
            
            params = [date_from, date_to]
            
            if payment_method != "All Payment Methods":
                query += " AND s.payment_method = %s"
                params.append(payment_method)
            
            query += " GROUP BY s.sale_id, s.invoice_number, s.sale_date, u.full_name, s.payment_method, s.total_amount"
            query += " ORDER BY s.sale_date DESC"
            
            sales = self.db.execute_query(query, params, fetchall=True)
            
            # Update table
            self.sales_table.setRowCount(0)
            
            for row_idx, sale in enumerate(sales):
                self.sales_table.insertRow(row_idx)
                
                sale_id, invoice, date, cashier, payment, total, item_count = sale
                
                # Invoice
                self.sales_table.setItem(row_idx, 0, QTableWidgetItem(invoice))
                
                # Date
                self.sales_table.setItem(row_idx, 1, QTableWidgetItem(date.strftime("%Y-%m-%d %H:%M")))
                
                # Cashier
                self.sales_table.setItem(row_idx, 2, QTableWidgetItem(cashier))
                
                # Payment Method
                self.sales_table.setItem(row_idx, 3, QTableWidgetItem(payment))
                
                # Total Amount
                total_item = QTableWidgetItem(f"P{float(total):.2f}")
                total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.sales_table.setItem(row_idx, 4, total_item)
                
                # Items
                self.sales_table.setItem(row_idx, 5, QTableWidgetItem(str(item_count)))
            
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
    
    def update_sales_chart(self):
        """Update the sales chart based on selected type"""
        chart_type = self.sales_chart_type.currentText()
        
        try:
            if chart_type == "Daily Sales":
                self.create_daily_sales_chart()
            elif chart_type == "Payment Method Distribution":
                self.create_payment_distribution_chart()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update sales chart: {str(e)}")
    
    def create_daily_sales_chart(self):
        """Create chart showing daily sales"""
        try:
            # Get filter values
            date_from = self.date_from.date().toString("yyyy-MM-dd")
            date_to = self.date_to.date().toString("yyyy-MM-dd")
            payment_method = self.payment_filter.currentText()
            
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
            axis_y.setTitleText("Amount (P)")
            axis_y.setLabelFormat("P%.2f")
            chart.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_y)
            
            # Set the chart in the view
            self.sales_chart_view.setChart(chart)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create daily sales chart: {str(e)}")
    
    def create_payment_distribution_chart(self):
        """Create chart showing distribution by payment method"""
        try:
            # Get filter values
            date_from = self.date_from.date().toString("yyyy-MM-dd")
            date_to = self.date_to.date().toString("yyyy-MM-dd")
            
            # Build query
            query = """
                SELECT s.payment_method, SUM(s.total_amount) as total
                FROM sales s
                WHERE s.sale_date::date BETWEEN %s AND %s
                GROUP BY s.payment_method
                ORDER BY total DESC
            """
            
            params = [date_from, date_to]
            payment_totals = self.db.execute_query(query, params, fetchall=True)
            
            # Create chart
            chart = QChart()
            chart.setTitle("Sales by Payment Method")
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            # Create pie series
            series = QPieSeries()
            
            # Add data to pie series
            for payment_method, total in payment_totals:
                series.append(f"{payment_method}: P{float(total):.2f}", float(total))
            
            # Customize slices
            for slice in series.slices():
                slice.setLabelVisible(True)
            
            # Add series to chart
            chart.addSeries(series)
            
            # Set the chart in the view
            self.sales_chart_view.setChart(chart)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create payment distribution chart: {str(e)}")
    
    def generate_inventory_report(self):
        """Generate the inventory report"""
        try:
            # Get filter values
            category_id = self.category_filter.currentData()
            stock_filter = self.stock_filter.currentData()
            expiry_filter = self.expiry_filter.currentData()
            
            # Build query
            query = """
                SELECT p.product_id, p.product_name, c.name as category_name, 
                       p.unit_price, p.cost_price, p.stock_quantity, p.expiry_date
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                WHERE 1=1
            """
            params = []
            
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
                
                product_id, name, category, unit_price, cost_price, stock, expiry = product
                
                # ID
                self.inventory_table.setItem(row_idx, 0, QTableWidgetItem(str(product_id)))
                
                # Product Name
                self.inventory_table.setItem(row_idx, 1, QTableWidgetItem(name))
                
                # Category
                self.inventory_table.setItem(row_idx, 2, QTableWidgetItem(category or "Uncategorized"))
                # Unit Price
                price_item = QTableWidgetItem(f"P{float(unit_price):.2f}")
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.inventory_table.setItem(row_idx, 3, price_item)
                
                # Cost Price
                cost_item = QTableWidgetItem(f"P{float(cost_price):.2f}")
                cost_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.inventory_table.setItem(row_idx, 4, cost_item)
                
                # Stock Quantity
                stock_item = QTableWidgetItem(str(stock))
                stock_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.inventory_table.setItem(row_idx, 5, stock_item)
                
                # Expiry Date
                expiry_text = expiry.strftime("%Y-%m-%d") if expiry else "N/A"
                self.inventory_table.setItem(row_idx, 6, QTableWidgetItem(expiry_text))
            
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
    
    def update_inventory_chart(self):
        """Update the inventory chart based on selected type"""
        chart_type = self.inv_chart_type.currentText()
        
        try:
            if chart_type == "Stock by Category":
                self.create_stock_by_category_chart()
            elif chart_type == "Value by Category":
                self.create_value_by_category_chart()
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
                series.append(f"{cat_name}: P{float(value):.2f}", float(value))
            
            # Customize slices
            for slice in series.slices():
                slice.setLabelVisible(True)
            
            # Add series to chart
            chart.addSeries(series)
            
            # Set the chart in the view
            self.inventory_chart_view.setChart(chart)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create value by category chart: {str(e)}")
    
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
                df['Total Amount'] = df['Total Amount'].str.replace('P', '').astype(float)
                
                # Write to Excel
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Sales Report', index=False)
                    
                    # Auto-adjust columns' width
                    for column in df:
                        column_width = max(df[column].astype(str).map(len).max(), len(column))
                        col_idx = df.columns.get_loc(column)
                        writer.sheets['Sales Report'].column_dimensions[chr(65 + col_idx)].width = column_width + 2
                
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
                df['Unit Price'] = df['Unit Price'].str.replace('P', '').astype(float)
                df['Cost Price'] = df['Cost Price'].str.replace('P', '').astype(float)

                # Write to Excel
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Inventory Report', index=False)
                    
                    # Auto-adjust columns' width
                    for column in df:
                        column_width = max(df[column].astype(str).map(len).max(), len(column))
                        col_idx = df.columns.get_loc(column)
                        writer.sheets['Inventory Report'].column_dimensions[chr(65 + col_idx)].width = column_width + 2
                
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