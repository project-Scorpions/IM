from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, 
                            QDateEdit, QGroupBox, QMessageBox, QHeaderView, QDialog,
                            QFormLayout, QDialogButtonBox, QCheckBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QFont, QColor

from database.db_connector import DatabaseConnection
from utils.auth import Authentication

class UserDialog(QDialog):
    """Dialog for adding or editing users"""
    
    def __init__(self, parent=None, user_id=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.auth = Authentication()
        self.user_id = user_id
        self.admin_user = parent.user
        self.init_ui()
        
        if user_id:
            self.setWindowTitle("Edit User")
            self.load_user_data()
        else:
            self.setWindowTitle("Add New User")
    
    def init_ui(self):
        """Initialize the UI components"""
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Form layout for user details
        form_layout = QFormLayout()
        
        # Full name
        self.full_name_input = QLineEdit()
        form_layout.addRow("Full Name*:", self.full_name_input)
        
        # Username
        self.username_input = QLineEdit()
        form_layout.addRow("Username*:", self.username_input)
        
        # Email
        self.email_input = QLineEdit()
        form_layout.addRow("Email:", self.email_input)
        
        # Password (only for new users)
        if not self.user_id:
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.Password)
            form_layout.addRow("Password*:", self.password_input)
        else:
            # Reset password option for existing users
            self.reset_password_check = QCheckBox("Reset Password")
            self.reset_password_check.stateChanged.connect(self.toggle_password_reset)
            form_layout.addRow("", self.reset_password_check)
            
            self.new_password_input = QLineEdit()
            self.new_password_input.setEchoMode(QLineEdit.Password)
            self.new_password_input.setEnabled(False)
            form_layout.addRow("New Password:", self.new_password_input)
        
        # Role
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Admin", "Pharmacist", "Cashier"])
        form_layout.addRow("Role*:", self.role_combo)
        
        # Active status (only for existing users)
        if self.user_id:
            self.active_check = QCheckBox("Active User")
            self.active_check.setChecked(True)
            form_layout.addRow("Status:", self.active_check)
        
        # Add form layout to main layout
        layout.addLayout(form_layout)
        
        # Add note about required fields
        required_note = QLabel("* Required fields")
        required_note.setStyleSheet("color: red;")
        layout.addWidget(required_note)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def toggle_password_reset(self, state):
        """Toggle password reset field"""
        self.new_password_input.setEnabled(state == Qt.Checked)
        if state != Qt.Checked:
            self.new_password_input.clear()
    
    def load_user_data(self):
        """Load user data if editing existing user"""
        try:
            query = """
                SELECT username, full_name, email, role, is_active
                FROM users
                WHERE user_id = %s
            """
            user = self.db.execute_query(query, (self.user_id,), fetchone=True)
            
            if user:
                self.username_input.setText(user[0])
                self.full_name_input.setText(user[1])
                self.email_input.setText(user[2] or "")
                
                # Set role
                role_index = self.role_combo.findText(user[3])
                if role_index >= 0:
                    self.role_combo.setCurrentIndex(role_index)
                
                # Set active status
                if hasattr(self, 'active_check'):
                    self.active_check.setChecked(user[4])
            else:
                QMessageBox.warning(self, "Warning", "User not found.")
                self.reject()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load user data: {str(e)}")
            self.reject()
    
    def accept(self):
     """Handle dialog acceptance (OK button)"""
     # Validate input
     full_name = self.full_name_input.text().strip()
     username = self.username_input.text().strip()
     email = self.email_input.text().strip()
     role = self.role_combo.currentText()
    
     if not full_name:
        QMessageBox.warning(self, "Validation Error", "Full name is required.")
        return
    
     if not username:
        QMessageBox.warning(self, "Validation Error", "Username is required.")
        return
    
     # Create direct database connection for this operation
     connection = None
     cursor = None
     try:
        # Get a direct connection
        connection = self.db.get_connection()
        cursor = connection.cursor()
        
        # Check if username exists (for new users or changed username)
        if not self.user_id or (self.user_id and self.username_input.isModified()):
            check_query = "SELECT COUNT(*) FROM users WHERE username = %s"
            check_params = [username]
            
            if self.user_id:
                check_query += " AND user_id != %s"
                check_params.append(self.user_id)
            
            cursor.execute(check_query, check_params)
            count = cursor.fetchone()[0]
            
            if count > 0:
                QMessageBox.warning(self, "Validation Error", f"Username '{username}' already exists. Please choose a different username.")
                return
        
        if self.user_id:
            # Update existing user
            is_active = self.active_check.isChecked()
            
            # Check if password reset is requested
            if hasattr(self, 'reset_password_check') and self.reset_password_check.isChecked():
                new_password = self.new_password_input.text()
                if not new_password:
                    QMessageBox.warning(self, "Validation Error", "New password is required when reset password is checked.")
                    return
                
                # Hash the new password
                hashed_password = self.auth.hash_password(new_password)
                
                # Update user with new password
                query = """
                    UPDATE users
                    SET username = %s, full_name = %s, email = %s, role = %s, 
                        is_active = %s, password = %s
                    WHERE user_id = %s
                """
                cursor.execute(
                    query, 
                    (username, full_name, email, role, is_active, hashed_password, self.user_id)
                )
                
                # Log activity
                self.auth.log_activity(
                    self.admin_user['user_id'],
                    "update",
                    "users",
                    self.user_id,
                    f"Updated user: {username} (including password reset)"
                )
            else:
                # Update user without changing password
                query = """
                    UPDATE users
                    SET username = %s, full_name = %s, email = %s, role = %s, 
                        is_active = %s
                    WHERE user_id = %s
                """
                cursor.execute(
                    query, 
                    (username, full_name, email, role, is_active, self.user_id)
                )
                
                # Log activity
                self.auth.log_activity(
                    self.admin_user['user_id'],
                    "update",
                    "users",
                    self.user_id,
                    f"Updated user: {username}"
                )
        else:
            # Create new user
            password = self.password_input.text()
            if not password:
                QMessageBox.warning(self, "Validation Error", "Password is required for new users.")
                return
            
            # Hash the password
            hashed_password = self.auth.hash_password(password)
            
            # Insert new user
            query = """
                INSERT INTO users
                (username, password, full_name, email, role, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING user_id
            """
            cursor.execute(
                query, 
                (username, hashed_password, full_name, email, role, True)
            )
            
            result = cursor.fetchone()
            new_user_id = result[0]
            
            # Log activity
            self.auth.log_activity(
                self.admin_user['user_id'],
                "insert",
                "users",
                new_user_id,
                f"Created new user: {username}"
            )
        
        # Explicitly commit the transaction
        connection.commit()
        
        QMessageBox.information(
            self, 
            "Success", 
            f"User '{username}' {'updated' if self.user_id else 'created'} successfully."
        )
        
        super().accept()
        
     except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error in user accept method: {str(e)}")
        import traceback
        print(traceback.format_exc())
        QMessageBox.critical(self, "Error", f"Failed to save user: {str(e)}")
     finally:
        if cursor:
            cursor.close()
        if connection:
            self.db.release_connection(connection)


class UserManagementWidget(QWidget):
    """Widget for managing users"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseConnection()
        self.auth = Authentication()
        self.init_ui()
        self.load_users()
    
    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)
        
        # Filter section
        filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout(filter_group)
        
        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by username or full name...")
        self.search_input.textChanged.connect(self.filter_users)
        search_layout.addWidget(self.search_input)
        
        filter_layout.addLayout(search_layout)
        
        # Role filter
        role_layout = QHBoxLayout()
        role_layout.addWidget(QLabel("Role:"))
        
        self.role_filter = QComboBox()
        self.role_filter.addItem("All Roles", None)
        self.role_filter.addItems(["Admin", "Pharmacist", "Cashier"])
        self.role_filter.currentIndexChanged.connect(self.filter_users)
        role_layout.addWidget(self.role_filter)
        
        filter_layout.addLayout(role_layout)
        
        # Status filter
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        
        self.status_filter = QComboBox()
        self.status_filter.addItem("All", None)
        self.status_filter.addItem("Active", True)
        self.status_filter.addItem("Inactive", False)
        self.status_filter.currentIndexChanged.connect(self.filter_users)
        status_layout.addWidget(self.status_filter)
        
        filter_layout.addLayout(status_layout)
        
        main_layout.addWidget(filter_group)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "Username", "Full Name", "Role", "Status", "Actions"
        ])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.users_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.users_table)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        add_user_btn = QPushButton("Add User")
        add_user_btn.setIcon(QIcon("resources/icons/add_user.png"))
        add_user_btn.clicked.connect(self.add_user)
        buttons_layout.addWidget(add_user_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        refresh_btn.clicked.connect(self.load_users)
        buttons_layout.addWidget(refresh_btn)
        
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)
    
    def load_users(self):
     """Load users from database into table"""
     connection = None
     cursor = None
     try:
        # Get a direct connection
        connection = self.db.get_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT user_id, username, full_name, role, is_active, last_login
            FROM users
            ORDER BY username
        """
        cursor.execute(query)
        users = cursor.fetchall()
        
        self.users_table.setRowCount(0)
        
        for row_idx, user in enumerate(users):
            self.users_table.insertRow(row_idx)
            
            user_id, username, full_name, role, is_active, last_login = user
            
            # User ID
            self.users_table.setItem(row_idx, 0, QTableWidgetItem(str(user_id)))
            
            # Username
            self.users_table.setItem(row_idx, 1, QTableWidgetItem(username))
            
            # Full Name
            self.users_table.setItem(row_idx, 2, QTableWidgetItem(full_name))
            
            # Role
            self.users_table.setItem(row_idx, 3, QTableWidgetItem(role))
            
            # Status
            status_text = "Active" if is_active else "Inactive"
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QColor("#008800" if is_active else "#CC0000"))
            self.users_table.setItem(row_idx, 4, status_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(2)
            
            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon("resources/icons/edit.png"))
            edit_btn.setToolTip("Edit User")
            edit_btn.setMaximumWidth(30)
            edit_btn.clicked.connect(lambda _, uid=user_id: self.edit_user(uid))
            actions_layout.addWidget(edit_btn)
            
            # Only allow admins to be deleted by other admins
            # Don't allow users to delete themselves
            if user_id != self.user['user_id'] and (role != "Admin" or self.user['role'] == "Admin"):
                delete_btn = QPushButton()
                delete_btn.setIcon(QIcon("resources/icons/delete.png"))
                delete_btn.setToolTip("Delete User")
                delete_btn.setMaximumWidth(30)
                delete_btn.clicked.connect(lambda _, uid=user_id, uname=username: self.delete_user(uid, uname))
                actions_layout.addWidget(delete_btn)
            
            self.users_table.setCellWidget(row_idx, 5, actions_widget)
        
        self.users_table.resizeColumnsToContents()
        self.users_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
     except Exception as e:
        print(f"Error loading users: {str(e)}")
        import traceback
        print(traceback.format_exc())
        QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")
     finally:
        if cursor:
            cursor.close()
        if connection:
            self.db.release_connection(connection)
    
    def filter_users(self):
        """Filter users based on search criteria"""
        search_text = self.search_input.text().lower()
        role_filter = self.role_filter.currentText()
        status_filter = self.status_filter.currentData()
        
        for row in range(self.users_table.rowCount()):
            show_row = True
            
            # Filter by search text
            username = self.users_table.item(row, 1).text().lower()
            full_name = self.users_table.item(row, 2).text().lower()
            
            if search_text and search_text not in username and search_text not in full_name:
                show_row = False
            
            # Filter by role
            if role_filter != "All Roles":
                role = self.users_table.item(row, 3).text()
                if role != role_filter:
                    show_row = False
            
            # Filter by status
            if status_filter is not None:
                status = self.users_table.item(row, 4).text()
                is_active = (status == "Active")
                if is_active != status_filter:
                    show_row = False
            
            self.users_table.setRowHidden(row, not show_row)
    
    def add_user(self):
        """Add a new user"""
        dialog = UserDialog(self)
        if dialog.exec_():
            self.load_users()
    
    def edit_user(self, user_id):
        """Edit an existing user"""
        dialog = UserDialog(self, user_id)
        if dialog.exec_():
            self.load_users()
    
    def delete_user(self, user_id, username):
     """Delete a user"""
     reply = QMessageBox.question(
        self, 
        "Confirm Delete", 
        f"Are you sure you want to delete user '{username}'?\nThis action cannot be undone.",
        QMessageBox.Yes | QMessageBox.No, 
        QMessageBox.No
    )
    
     if reply == QMessageBox.Yes:
        # Create direct database connection for this operation
        connection = None
        cursor = None
        try:
            # Get a direct connection
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            # Check if user has any sales
            check_query = """
                SELECT COUNT(*) FROM sales 
                WHERE user_id = %s
            """
            cursor.execute(check_query, (user_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                # Don't allow deletion, just deactivate
                reply = QMessageBox.question(
                    self, 
                    "Cannot Delete", 
                    f"Cannot delete '{username}' because they have {count} sales recorded.\nWould you like to deactivate this user instead?",
                    QMessageBox.Yes | QMessageBox.No, 
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    # Deactivate user
                    update_query = """
                        UPDATE users
                        SET is_active = FALSE
                        WHERE user_id = %s
                    """
                    cursor.execute(update_query, (user_id,))
                    
                    # Commit the transaction
                    connection.commit()
                    
                    # Log activity
                    self.auth.log_activity(
                        self.user['user_id'],
                        "deactivate",
                        "users",
                        user_id,
                        f"Deactivated user: {username}"
                    )
                    
                    QMessageBox.information(self, "Success", f"User '{username}' has been deactivated.")
                    self.load_users()
                
                return
            
            # Delete the user
            query = "DELETE FROM users WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            
            # Commit the transaction
            connection.commit()
            
            # Log activity
            self.auth.log_activity(
                self.user['user_id'],
                "delete",
                "users",
                user_id,
                f"Deleted user: {username}"
            )
            
            QMessageBox.information(self, "Success", f"User '{username}' deleted successfully.")
            self.load_users()
            
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"Error deleting user: {str(e)}")
            import traceback
            print(traceback.format_exc())
            QMessageBox.critical(self, "Error", f"Failed to delete user: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.db.release_connection(connection)