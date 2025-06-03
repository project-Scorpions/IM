import sys
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QMessageBox, QFrame,
                            QCheckBox, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette, QLinearGradient
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from utils.auth import Authentication
from ui.main_window import MainWindow

class LoginWindow(QWidget):
    """Login window for the Pharmacy Management System"""
    
    def __init__(self):
        super().__init__()
        self.auth = Authentication()
        # Try to create initial admin user if no users exist
        self.auth.create_initial_admin()
        self.init_ui()
    
    def load_image_safely(self, path, default_width=200):
        """Load an image with error handling and return a scaled QPixmap"""
        pixmap = QPixmap(path)
        if pixmap.isNull():
            print(f"Warning: Could not load image from {path}")
            # Create a blank pixmap as fallback
            blank_pixmap = QPixmap(default_width, 100)
            blank_pixmap.fill(Qt.white)
            return blank_pixmap
        return pixmap.scaledToWidth(default_width, Qt.SmoothTransformation)
    
    def init_ui(self):
        """Initialize the UI components"""
        # Set window properties
        self.setWindowTitle("Aryona DrugHUB - Login")
        self.setMinimumSize(800, 500)  # Wider window for horizontal layout
        self.setWindowIcon(QIcon("resources/icons/pharmacy.png"))
        
        # Set application-wide font
        self.setStyleSheet("""
            * {
                font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
            }
        """)
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # LEFT SIDE - LOGIN FORM (WITH RED BACKGROUND)
        left_widget = QWidget()
        left_widget.setObjectName("leftPanel")
        left_widget.setStyleSheet("""
            #leftPanel {
                background-color: #e74c3c;
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
            }
        """)
        
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(40, 40, 40, 40)
        left_layout.setSpacing(15)
        
        # Login header
        login_header = QLabel("WELCOME BACK")
        login_header.setFont(QFont("Segoe UI", 26, QFont.Bold))
        login_header.setStyleSheet("color: white; letter-spacing: 2px; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);")
        left_layout.addWidget(login_header)
        
        subtitle_label = QLabel("Sign in to your account")
        subtitle_label.setFont(QFont("Segoe UI", 13, QFont.Normal))
        subtitle_label.setStyleSheet("color: white; margin-bottom: 5px;")
        left_layout.addWidget(subtitle_label)
        
        # Add a subtle decorative line
        header_line = QFrame()
        header_line.setFrameShape(QFrame.HLine)
        header_line.setFrameShadow(QFrame.Sunken)
        header_line.setStyleSheet("background-color: rgba(255,255,255,0.5); max-height: 1px; margin: 5px 0 20px 0;")
        left_layout.addWidget(header_line)
        
        # Username
        username_label = QLabel("USERNAME")
        username_label.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        username_label.setStyleSheet("color: white; letter-spacing: 1px;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(50)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid rgba(255,255,255,0.8);
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.15);
                font-size: 14px;
                color: white;
                font-weight: bold;
            }
            QLineEdit::placeholder {
                color: rgba(255,255,255,0.6);
            }
            QLineEdit:focus {
                background-color: rgba(255, 255, 255, 0.25);
                border: 2px solid white;
            }
        """)
        left_layout.addWidget(username_label)
        left_layout.addWidget(self.username_input)
        
        left_layout.addSpacing(15)
        
        # Password
        password_label = QLabel("PASSWORD")
        password_label.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        password_label.setStyleSheet("color: white; letter-spacing: 1px;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(50)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid rgba(255,255,255,0.8);
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.15);
                font-size: 14px;
                color: white;
                font-weight: bold;
            }
            QLineEdit::placeholder {
                color: rgba(255,255,255,0.6);
            }
            QLineEdit:focus {
                background-color: rgba(255, 255, 255, 0.25);
                border: 2px solid white;
            }
        """)
        left_layout.addWidget(password_label)
        left_layout.addWidget(self.password_input)
        
        # Show password checkbox
        password_toggle_layout = QHBoxLayout()
        self.show_password_checkbox = QCheckBox("SHOW PASSWORD")
        self.show_password_checkbox.setFont(QFont("Segoe UI", 10))
        self.show_password_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 11px;
                letter-spacing: 1px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                background-color: rgba(255,255,255,0.15);
                border: 2px solid white;
            }
            QCheckBox::indicator:checked {
                background-color: white;
                image: url(resources/icons/check.png);
            }
        """)
        self.show_password_checkbox.toggled.connect(self.toggle_password_visibility)
        password_toggle_layout.addWidget(self.show_password_checkbox)
        
        left_layout.addLayout(password_toggle_layout)
        
        left_layout.addSpacing(25)
        
        # Login button
        self.login_button = QPushButton("LOGIN")
        self.login_button.setMinimumHeight(55)
        self.login_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #e74c3c;
                border: none;
                border-radius: 8px;
                padding: 12px;
                letter-spacing: 2px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.9);
                color: #c0392b;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.8);
            }
        """)
        self.login_button.clicked.connect(self.handle_login)
        left_layout.addWidget(self.login_button)
        
        # Footer
        left_layout.addStretch()
        
        # Current date and user info
        info_container = QWidget()
        info_container.setStyleSheet("background-color: rgba(0,0,0,0.1); border-radius: 8px; padding: 10px;")
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(10, 10, 10, 10)
        info_layout.setSpacing(5)
        
        # Footer copyright
        footer_label = QLabel("© 2025 ARYONA DRUGSTORE. ALL RIGHTS RESERVED.")
        footer_label.setFont(QFont("Segoe UI", 8))
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: white; letter-spacing: 1px;")
        info_layout.addWidget(footer_label)
        
        left_layout.addWidget(info_container)
        
        # RIGHT SIDE - LOGO AND DECORATION (WITH WHITE BACKGROUND)
        right_widget = QWidget()
        right_widget.setObjectName("rightPanel")
        right_widget.setStyleSheet("""
            #rightPanel {
                background-color: white;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(30, 30, 30, 30)
        right_layout.setSpacing(15)
        right_layout.setAlignment(Qt.AlignCenter)
        
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = self.load_image_safely("resources/icons/aryona_logo.png", 420)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("background-color: transparent;")
        right_layout.addWidget(logo_label)
        
        # Decorative line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #e74c3c; min-height: 3px; margin: 20px 0;")
        right_layout.addWidget(line)
        
        # Pharmacy tagline
        tagline = QLabel("INVENTORY & SALES MANAGEMENT SYSTEM")
        tagline.setFont(QFont("Segoe UI", 16, QFont.Bold))
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setStyleSheet("color: #e74c3c; background-color: transparent; letter-spacing: 2px;")
        right_layout.addWidget(tagline)
        
        # Add decorative medical icons or description
        description = QLabel("YOUR HEALTH, OUR PRIORITY")
        description.setFont(QFont("Segoe UI", 12))
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("color: #333333; background-color: transparent; letter-spacing: 1px; margin-top: 10px;")
        right_layout.addWidget(description)
        
        
        # Add left and right widgets to main layout
        main_layout.addWidget(left_widget, 1)  # 1 part for login
        main_layout.addWidget(right_widget, 1)  # 1 part for logo/decoration
        
        # Set tab order
        self.setTabOrder(self.username_input, self.password_input)
        self.setTabOrder(self.password_input, self.show_password_checkbox)
        self.setTabOrder(self.show_password_checkbox, self.login_button)
        
        # Set focus to username input
        self.username_input.setFocus()
        
        # Connect enter key press to login
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
    
    def toggle_password_visibility(self, checked):
        """Toggle password visibility based on checkbox state"""
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
            return
        
        user = self.auth.login(username, password)
        
        if user:
            # Open main window
            self.main_window = MainWindow(user)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.critical(self, "Login Failed", 
                               "Invalid username or password.", 
                               QMessageBox.Ok)
            self.password_input.clear()
            self.password_input.setFocus()
            
    def open_forgot_password_dialog(self, event):
     """Open the forgot password dialog when the link is clicked"""
     dialog = ForgotPasswordDialog(self)
     dialog.exec_()

class ForgotPasswordDialog(QDialog):
    """Dialog for resetting a forgotten password"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth = Authentication()
        self.init_ui()
    
    def init_ui(self):
        """Set up the dialog UI"""
        # Set window properties
        self.setWindowTitle("Reset Password")
        self.setFixedSize(450, 280)
        self.setStyleSheet("""
            * {
                font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
            }
            QDialog {
                background-color: white;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QLabel("RESET YOUR PASSWORD")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #e74c3c; letter-spacing: 1px; margin-bottom: 5px;")
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel("Enter your username to reset your password. If the username exists in our system, you will be able to create a new password.")
        instructions.setFont(QFont("Segoe UI", 10))
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #555; margin-bottom: 10px;")
        layout.addWidget(instructions)
        
        # Username
        username_label = QLabel("USERNAME")
        username_label.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        username_label.setStyleSheet("color: #333; letter-spacing: 1px; margin-top: 10px;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(40)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #e74c3c;
            }
        """)
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        
        # Reset button
        self.reset_button = QPushButton("VERIFY USERNAME")
        self.reset_button.setMinimumHeight(45)
        self.reset_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a5281b;
            }
        """)
        self.reset_button.clicked.connect(self.verify_username)
        layout.addWidget(self.reset_button)
        
        # Cancel button
        self.cancel_button = QPushButton("CANCEL")
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.setFont(QFont("Segoe UI", 10))
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #555;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 8px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)
        
        # Set focus to username input
        self.username_input.setFocus()
    
    def verify_username(self):
        """Verify if the username exists and show the reset password dialog"""
        username = self.username_input.text().strip()
        
        if not username:
            QMessageBox.warning(self, "Error", "Please enter a username.")
            return
        
        # Check if username exists
        user = self.auth.get_user_by_username(username)
        
        if user:
            self.open_reset_password_dialog(username, user['user_id'])
        else:
            QMessageBox.warning(self, "User Not Found", 
                               "No account found with this username.\nPlease check your username and try again.")
    
    def open_reset_password_dialog(self, username, user_id):
        """Open the reset password dialog if username is verified"""
        # Close this dialog
        self.accept()
        
        # Open the reset password dialog
        reset_dialog = ResetPasswordDialog(self.parent(), username, user_id)
        reset_dialog.exec_()

class ResetPasswordDialog(QDialog):
    """Dialog for creating a new password"""
    
    def __init__(self, parent=None, username="", user_id=None):
        super().__init__(parent)
        self.auth = Authentication()
        self.username = username
        self.user_id = user_id
        self.init_ui()
    
    def init_ui(self):
        """Set up the dialog UI"""
        # Set window properties
        self.setWindowTitle("Create New Password")
        self.setFixedSize(550, 450)
        self.setStyleSheet("""
            * {
                font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
            }
            QDialog {
                background-color: white;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QLabel("CREATE NEW PASSWORD")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #e74c3c; letter-spacing: 1px; margin-bottom: 5px;")
        layout.addWidget(title)
        
        # User info
        user_info = QLabel(f"Creating new password for user: {self.username}")
        user_info.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        user_info.setStyleSheet("color: #333; margin-bottom: 10px;")
        layout.addWidget(user_info)
        
        # New password
        new_password_label = QLabel("NEW PASSWORD")
        new_password_label.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        new_password_label.setStyleSheet("color: #333; letter-spacing: 1px;")
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("Enter new password")
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setMinimumHeight(40)
        self.new_password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #e74c3c;
            }
        """)
        layout.addWidget(new_password_label)
        layout.addWidget(self.new_password_input)
        
        # Confirm password
        confirm_password_label = QLabel("CONFIRM PASSWORD")
        confirm_password_label.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        confirm_password_label.setStyleSheet("color: #333; letter-spacing: 1px;")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm new password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setMinimumHeight(40)
        self.confirm_password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #e74c3c;
            }
        """)
        layout.addWidget(confirm_password_label)
        layout.addWidget(self.confirm_password_input)
        
        # Show password checkbox
        self.show_password_checkbox = QCheckBox("Show passwords")
        self.show_password_checkbox.setFont(QFont("Segoe UI", 10))
        self.show_password_checkbox.setStyleSheet("""
            QCheckBox {
                color: #555;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid #ddd;
            }
            QCheckBox::indicator:checked {
                background-color: #e74c3c;
                border: 1px solid #e74c3c;
            }
        """)
        self.show_password_checkbox.toggled.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password_checkbox)
        
        # Reset button
        self.reset_button = QPushButton("RESET PASSWORD")
        self.reset_button.setMinimumHeight(45)
        self.reset_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a5281b;
            }
        """)
        self.reset_button.clicked.connect(self.reset_password)
        layout.addWidget(self.reset_button)
        
        # Cancel button
        self.cancel_button = QPushButton("CANCEL")
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.setFont(QFont("Segoe UI", 10))
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #555;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 8px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)
        
        # Set focus to new password input
        self.new_password_input.setFocus()
    
    def toggle_password_visibility(self, checked):
        """Toggle password visibility based on checkbox state"""
        if checked:
            self.new_password_input.setEchoMode(QLineEdit.Normal)
            self.confirm_password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.new_password_input.setEchoMode(QLineEdit.Password)
            self.confirm_password_input.setEchoMode(QLineEdit.Password)