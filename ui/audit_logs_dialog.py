from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QTableWidget, QTableWidgetItem, QDateEdit, QComboBox,
                           QGroupBox, QFormLayout, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon

import datetime
from utils.audit import AuditTrail
from utils.export import ExportUtility
from database.db_connector import DatabaseConnection

class AuditLogsDialog(QDialog):
    """Dialog for viewing audit logs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.audit_trail = AuditTrail()
        self.export_utility = ExportUtility()
        self.init_ui()
        self.load_filters()
        self.load_logs()
    
    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle("Audit Logs")
        self.setMinimumSize(800, 500)
        self.setWindowIcon(QIcon("resources/icons/audit.png"))
        
        main_layout = QVBoxLayout(self)
        
        # Filters section
        filters_group = QGroupBox("Filters")
        filters_layout = QHBoxLayout(filters_group)
        
        # Date range
        date_form = QFormLayout()
        
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-7))  # Last 7 days
        date_form.addRow("From:", self.date_from)
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        date_form.addRow("To:", self.date_to)
        
        filters_layout.addLayout(date_form)
        
        # User filter
        user_form = QFormLayout()
        
        self.user_filter = QComboBox()
        self.user_filter.addItem("All Users", None)
        user_form.addRow("User:", self.user_filter)
        
        filters_layout.addLayout(user_form)
        
        # Action type filter
        action_form = QFormLayout()
        
        self.action_filter = QComboBox()
        self.action_filter.addItem("All Actions", None)
        action_form.addRow("Action Type:", self.action_filter)
        
        filters_layout.addLayout(action_form)
        
        # Table filter
        table_form = QFormLayout()
        
        self.table_filter = QComboBox()
        self.table_filter.addItem("All Tables", None)
        table_form.addRow("Table:", self.table_filter)
        
        filters_layout.addLayout(table_form)
        
        # Filter button
        filter_btn_layout = QVBoxLayout()
        filter_btn_layout.addStretch()
        
        filter_btn = QPushButton("Apply Filters")
        filter_btn.clicked.connect(self.load_logs)
        filter_btn_layout.addWidget(filter_btn)
        
        filters_layout.addLayout(filter_btn_layout)
        
        main_layout.addWidget(filters_group)
        
        # Logs table
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(8)
        self.logs_table.setHorizontalHeaderLabels([
            "ID", "Timestamp", "User", "Action Type", "Table", "Record ID", "Details", "IP Address"
        ])
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.logs_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.logs_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.logs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.logs_table)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        export_btn = QPushButton("Export to Excel")
        export_btn.setIcon(QIcon("resources/icons/excel.png"))
        export_btn.clicked.connect(self.export_logs)
        buttons_layout.addWidget(export_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        refresh_btn.clicked.connect(self.load_logs)
        buttons_layout.addWidget(refresh_btn)
        
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def load_filters(self):
        """Load filter options from database"""
        try:
            # Load users
            user_query = """
                SELECT DISTINCT u.user_id, u.username
                FROM audit_logs l
                JOIN users u ON l.user_id = u.user_id
                ORDER BY u.username
            """
            users = self.db.execute_query(user_query, fetchall=True)
            
            for user_id, username in users:
                self.user_filter.addItem(username, user_id)
            
            # Load action types
            action_query = """
                SELECT DISTINCT action_type
                FROM audit_logs
                ORDER BY action_type
            """
            actions = self.db.execute_query(action_query, fetchall=True)
            
            for action in actions:
                self.action_filter.addItem(action[0], action[0])
            
            # Load tables
            table_query = """
                SELECT DISTINCT table_affected
                FROM audit_logs
                WHERE table_affected IS NOT NULL
                ORDER BY table_affected
            """
            tables = self.db.execute_query(table_query, fetchall=True)
            
            for table in tables:
                self.table_filter.addItem(table[0], table[0])
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load filter options: {str(e)}")
    
    def load_logs(self):
        """Load audit logs based on filters"""
        try:
            # Get filter values
            date_from = self.date_from.date().toString("yyyy-MM-dd")
            date_to = self.date_to.date().toString("yyyy-MM-dd")
            user_id = self.user_filter.currentData()
            action_type = self.action_filter.currentData()
            table_affected = self.table_filter.currentData()
            
            # Build filters
            filters = {
                'date_from': date_from,
                'date_to': date_to
            }
            
            if user_id is not None:
                filters['user_id'] = user_id
            
            if action_type is not None:
                filters['action_type'] = action_type
            
            if table_affected is not None:
                filters['table_affected'] = table_affected
            
            # Get logs
            logs = self.audit_trail.get_audit_logs(filters, limit=1000)
            
            # Update table
            self.logs_table.setRowCount(0)
            
            for row_idx, log in enumerate(logs):
                self.logs_table.insertRow(row_idx)
                
                log_id, timestamp, action_type, table_affected, record_id, details, ip, username, full_name = log
                
                # Log ID
                self.logs_table.setItem(row_idx, 0, QTableWidgetItem(str(log_id)))
                
                # Timestamp
                self.logs_table.setItem(row_idx, 1, QTableWidgetItem(timestamp.strftime("%Y-%m-%d %H:%M:%S")))
                
                # User
                user_item = QTableWidgetItem(f"{username} ({full_name})")
                self.logs_table.setItem(row_idx, 2, user_item)
                
                # Action Type
                self.logs_table.setItem(row_idx, 3, QTableWidgetItem(action_type))
                
                # Table
                self.logs_table.setItem(row_idx, 4, QTableWidgetItem(table_affected or ""))
                
                # Record ID
                self.logs_table.setItem(row_idx, 5, QTableWidgetItem(str(record_id) if record_id else ""))
                
                # Details
                self.logs_table.setItem(row_idx, 6, QTableWidgetItem(details or ""))
                
                # IP Address
                self.logs_table.setItem(row_idx, 7, QTableWidgetItem(ip or ""))
            
            self.logs_table.resizeColumnsToContents()
            self.logs_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load audit logs: {str(e)}")
    
    def export_logs(self):
        """Export audit logs to Excel"""
        try:
            # Get data from table
            data = []
            headers = []
            
            for col in range(self.logs_table.columnCount()):
                headers.append(self.logs_table.horizontalHeaderItem(col).text())
            
            for row in range(self.logs_table.rowCount()):
                row_data = []
                for col in range(self.logs_table.columnCount()):
                    item = self.logs_table.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)
            
            # Export to Excel
            self.export_utility.export_to_excel(
                self,
                data,
                headers,
                "audit_logs",
                "Audit Logs"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export audit logs: {str(e)}")