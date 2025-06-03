from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QAction, QStatusBar, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QDate, QTime, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap

from ui.inventory_management import InventoryManagementWidget
from ui.pos import POSWidget
from ui.reports import ReportsWidget
from ui.user_management import UserManagementWidget
from ui.supplier_management import SupplierManagementWidget
from database.db_connector import DatabaseConnection
from ui.settings_dialog import SettingsDialog
from ui.audit_logs_dialog import AuditLogsDialog

class MainWindow(QMainWindow):
    """Main application window with tabbed interface"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseConnection()
        self.init_ui()
        
        # Start clock timer
        self.update_clock()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)  # Update every second
        
        # Show in full screen mode
        self.showMaximized()  # This will maximize the window
    
    def init_ui(self):
        """Initialize the UI components"""
        # Set window properties
        self.setWindowTitle("Aryona DrugHUB")
        self.setMinimumSize(1280, 800)
        self.setWindowIcon(QIcon("resources/icons/pharmacy.png"))
        
        # Apply application-wide stylesheet - simplified
        self.setStyleSheet("""
            * {
                font-family: 'Segoe UI', 'Roboto', sans-serif;
            }
            QMainWindow {
                background-color: white;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                background: white;
            }
            QTabBar::tab {
                background: white;
                border: 1px solid #ddd;
                padding: 8px 16px;
                margin-right: 2px;
                color: #555;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                border-bottom: 2px solid #e74c3c;
                color: #e74c3c;
            }
            QPushButton {
                border: 1px solid #ddd;
                padding: 8px 15px;
                border-radius: 3px;
            }
            QStatusBar {
                color: #333;
                border-top: 1px solid #ddd;
            }
        """)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create simplified header
        header = QFrame()
        header.setObjectName("headerFrame")
        header.setStyleSheet("""
            #headerFrame {
                background-color: white; 
                border-bottom: 1px solid #ddd;
            }
        """)
        header.setMinimumHeight(60)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 5, 15, 5)
        
        # Logo and title section - simplified
        title_layout = QHBoxLayout()
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("resources/icons/aryona_logo.png")
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaledToHeight(40, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        title_layout.addWidget(logo_label)
        
        # App title
        title_label = QLabel("ARYONA DRUGHUB")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setStyleSheet("color: #e74c3c; margin-left: 10px;")
        title_layout.addWidget(title_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch(1)
        
        # Simplified date time section
        date_time_layout = QVBoxLayout()
        date_time_layout.setSpacing(0)
        
        self.date_label = QLabel("")  # Will be set in update_clock
        self.date_label.setFont(QFont("Segoe UI", 9))
        self.date_label.setAlignment(Qt.AlignRight)
        date_time_layout.addWidget(self.date_label)
        
        self.time_label = QLabel("")  # Will be set in update_clock
        self.time_label.setFont(QFont("Segoe UI", 14))
        self.time_label.setAlignment(Qt.AlignRight)
        date_time_layout.addWidget(self.time_label)
        
        header_layout.addLayout(date_time_layout)
        header_layout.addSpacing(20)
        
        # User info and logout - simplified
        user_layout = QHBoxLayout()
        
        # User info
        user_name_label = QLabel(f"{self.user['full_name']} ({self.user['role']})")
        user_name_label.setFont(QFont("Segoe UI", 10))
        user_layout.addWidget(user_name_label)
        
        # Logout button - simplified
        logout_button = QPushButton("Logout")
        logout_button.setIcon(QIcon("resources/icons/logout.png"))
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_button.clicked.connect(self.logout)
        user_layout.addWidget(logout_button)
        
        header_layout.addLayout(user_layout)
        
        main_layout.addWidget(header)
        
        # Main content layout with padding
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(10)
        
        # Create tab widget - simplified
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(True)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(False)
        
        # Add tabs based on user role
        self.add_tabs_based_on_role()
        
        content_layout.addWidget(self.tab_widget)
        
        # Add content layout to main layout
        main_layout.addLayout(content_layout)
        
        # Create status bar - simplified
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("System Ready")
        
        # Add version label to status bar
        version_label = QLabel("Version 1.0.0")
        self.status_bar.addPermanentWidget(version_label)
        
        # Create menu bar
        self.create_menu_bar()
    
    def update_clock(self):
        """Update the date and time display in header"""
        current_date = QDate.currentDate()
        current_time = QTime.currentTime()
        
        # Format date: Monday, June 1, 2025
        formatted_date = current_date.toString("dddd, MMMM d, yyyy")
        self.date_label.setText(formatted_date)
        
        # Format time: 03:28 AM
        formatted_time = current_time.toString("hh:mm AP")
        self.time_label.setText(formatted_time)
    
    def add_tabs_based_on_role(self):
        """Add tabs based on user role"""
        role = self.user['role']
        
        # POS tab - available to all roles
        pos_widget = POSWidget(self.user)
        self.tab_widget.addTab(pos_widget, self.create_tab_icon("resources/icons/pos.png"), "POINT OF SALE")
        
        # Inventory tab - available to Admin and Pharmacist
        if role in ["Admin", "Pharmacist"]:
            inventory_widget = InventoryManagementWidget(self.user)
            self.tab_widget.addTab(inventory_widget, self.create_tab_icon("resources/icons/inventory.png"), "INVENTORY")
        
        # Reports tab - available to Admin and Pharmacist
        if role in ["Admin", "Pharmacist"]:
            reports_widget = ReportsWidget(self.user)
            self.tab_widget.addTab(reports_widget, self.create_tab_icon("resources/icons/reports.png"), "REPORTS")
        
        # User Management tab - available to Admin only
        if role == "Admin":
            user_management_widget = UserManagementWidget(self.user)
            self.tab_widget.addTab(user_management_widget, self.create_tab_icon("resources/icons/users.png"), "USERS")
        
        # Supplier Management tab - available to Admin and Pharmacist
        if role in ["Admin", "Pharmacist"]:
            supplier_widget = SupplierManagementWidget(self.user)
            self.tab_widget.addTab(supplier_widget, self.create_tab_icon("resources/icons/suppliers.png"), "SUPPLIERS")
    
    def create_tab_icon(self, icon_path):
        """Create a properly sized icon for tabs"""
        return QIcon(icon_path)
    
    def create_menu_bar(self):
        """Create the application menu bar - simplified"""
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: white;
                color: #333;
                border-bottom: 1px solid #ddd;
            }
            QMenuBar::item:selected {
                background-color: #f5f5f5;
                color: #e74c3c;
            }
            QMenu {
                background-color: white;
                border: 1px solid #ddd;
            }
            QMenu::item:selected {
                background-color: #f5f5f5;
                color: #e74c3c;
            }
        """)
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        backup_action = QAction(QIcon("resources/icons/backup.png"), "Backup Database", self)
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)
        
        restore_action = QAction(QIcon("resources/icons/restore.png"), "Restore Database", self)
        restore_action.triggered.connect(self.restore_database)
        file_menu.addAction(restore_action)
        
        file_menu.addSeparator()
        
        logout_action = QAction(QIcon("resources/icons/logout.png"), "Logout", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        exit_action = QAction(QIcon("resources/icons/exit.png"), "Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menu_bar.addMenu("&Tools")
        
        settings_action = QAction(QIcon("resources/icons/settings.png"), "Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        audit_action = QAction(QIcon("resources/icons/audit.png"), "Audit Logs", self)
        audit_action.triggered.connect(self.show_audit_logs)
        tools_menu.addAction(audit_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        about_action = QAction(QIcon("resources/icons/about.png"), "About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def backup_database(self):
        """Open the backup database dialog"""
        dialog = SettingsDialog(self)
        dialog.exec_()

    def restore_database(self):
        """Open the restore database dialog"""
        dialog = SettingsDialog(self)
        dialog.exec_()

    def show_settings(self):
        """Open the settings dialog"""
        dialog = SettingsDialog(self)
        dialog.exec_()

    def show_audit_logs(self):
        """Open the audit logs dialog"""
        dialog = AuditLogsDialog(self)
        dialog.exec_()
    
    def show_about(self):
        """Show about dialog - simplified"""
        about_box = QMessageBox(self)
        about_box.setWindowTitle("About Aryona DrugHub")
        
        about_box.setIconPixmap(QPixmap("resources/icons/aryona_logo.png").scaledToWidth(100, Qt.SmoothTransformation))
        
        about_box.setText("<h2>Aryona DrugHub</h2>")
        about_box.setInformativeText(
            "<b>Version 1.0.0</b><br><br>"
            "A pharmacy management system developed for Aryona Drugstore.<br><br>"
            "<b>Features:</b> Inventory Management, Point of Sale, Reporting,<br>"
            "User Management, Supplier Management<br><br>"
            "© 2025 Aryona DrugHub. All rights reserved."
        )
        
        about_box.setStandardButtons(QMessageBox.Ok)
        about_box.exec_()
    
    def logout(self):
        """Log out the current user and return to login screen - simplified"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Logout")
        msg_box.setText("Are you sure you want to logout?")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        reply = msg_box.exec_()
       
        if reply == QMessageBox.Yes:
            # Import the login window and show it
            from ui.login import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()
    
    def closeEvent(self, event):
        """Handle window close event"""
        if not hasattr(self, 'login_window') or not self.login_window.isVisible():
            self.db.close_all_connections()
            event.accept()
        else:
            event.accept()