from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, 
                            QDateEdit, QGroupBox, QMessageBox, QHeaderView, QDialog,
                            QFormLayout, QDialogButtonBox, QCheckBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QFont, QColor

from database.db_connector import DatabaseConnection # Assuming this path is correct for your project
from utils.auth import Authentication             # Assuming this path is correct for your project
import datetime                                   # For created_at timestamp
import traceback                                  # For detailed error logging

class UserDialog(QDialog):
    """Dialog for adding or editing users."""
    
    def __init__(self, parent=None, user_id_to_edit=None): 
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.auth = Authentication()
        self.user_id_being_edited = user_id_to_edit 
        
        self.current_admin_user = parent.user if parent and hasattr(parent, 'user') else None 
        
        if not self.current_admin_user or not isinstance(self.current_admin_user, dict) or 'user_id' not in self.current_admin_user:
            QMessageBox.critical(self, "Initialization Error", 
                                 "Admin user context is missing or invalid. Cannot proceed safely. Please contact support.")
            print(f"CRITICAL ERROR ({datetime.datetime.utcnow().isoformat()}): UserDialog initialized without valid admin_user context. Parent: {parent}")
            self.current_admin_user = {'user_id': -1, 'username': 'system_error_user'} # Fallback

        self.init_ui()
        
        if self.user_id_being_edited:
            self.setWindowTitle(f"Edit User (ID: {self.user_id_being_edited})")
            self.load_user_data_for_edit()
        else:
            self.setWindowTitle("Add New User")
    
    def init_ui(self):
        """Initialize the UI components of the dialog."""
        self.setMinimumWidth(450) 
        self.setWindowIcon(QIcon("resources/icons/user_edit.png")) # Replace with your actual icon path

        layout = QVBoxLayout(self)
        
        form_group_box = QGroupBox("User Details")
        form_layout = QFormLayout(form_group_box)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("Enter user's full name")
        form_layout.addRow("Full Name*:", self.full_name_input)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter unique username")
        form_layout.addRow("Username*:", self.username_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter user's email (optional)")
        form_layout.addRow("Email:", self.email_input)
        
        if not self.user_id_being_edited: 
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.Password)
            self.password_input.setPlaceholderText("Enter password (min 6 chars)")
            form_layout.addRow("Password*:", self.password_input)
        else: 
            self.reset_password_check = QCheckBox("Reset Password for this User")
            self.reset_password_check.stateChanged.connect(self.toggle_password_reset_fields)
            form_layout.addRow("", self.reset_password_check) 
            
            self.new_password_input = QLineEdit()
            self.new_password_input.setEchoMode(QLineEdit.Password)
            self.new_password_input.setPlaceholderText("Enter new password (min 6 chars)")
            self.new_password_input.setEnabled(False) 
            form_layout.addRow("New Password:", self.new_password_input)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Admin", "Pharmacist", "Cashier"]) 
        form_layout.addRow("Role*:", self.role_combo)
        
        if self.user_id_being_edited: 
            self.active_check = QCheckBox("User Account is Active")
            self.active_check.setChecked(True) 
            form_layout.addRow("Status:", self.active_check)
        
        layout.addWidget(form_group_box)
        
        required_note = QLabel("* Indicates a required field.")
        required_note.setStyleSheet("color: #D32F2F; font-style: italic;") 
        layout.addWidget(required_note, 0, Qt.AlignRight) 
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Ok).setText("Save User")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Cancel")
        self.button_box.accepted.connect(self.process_save_user) 
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
    
    def toggle_password_reset_fields(self, state):
        """Enable/disable the new password input field based on checkbox state."""
        is_checked = (state == Qt.Checked)
        self.new_password_input.setEnabled(is_checked)
        if not is_checked:
            self.new_password_input.clear() 
    
    def load_user_data_for_edit(self):
        """Load data for an existing user into the dialog fields."""
        if not self.user_id_being_edited: return 

        connection = None
        cursor = None
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            query = "SELECT username, full_name, email, role, is_active FROM users WHERE user_id = %s"
            cursor.execute(query, (self.user_id_being_edited,))
            user_data = cursor.fetchone()
            
            if user_data:
                self.username_input.setText(user_data[0])
                self.full_name_input.setText(user_data[1])
                self.email_input.setText(user_data[2] or "") 
                
                role_index = self.role_combo.findText(user_data[3], Qt.MatchFixedString)
                if role_index >= 0:
                    self.role_combo.setCurrentIndex(role_index)
                else:
                    print(f"Warning: Role '{user_data[3]}' not found in ComboBox for user ID {self.user_id_being_edited}.")
                
                if hasattr(self, 'active_check'): 
                    self.active_check.setChecked(bool(user_data[4])) 
            else:
                QMessageBox.warning(self, "User Not Found", 
                                    f"The user with ID {self.user_id_being_edited} could not be found.")
                self.button_box.button(QDialogButtonBox.Ok).setEnabled(False) 
        except Exception as e:
            QMessageBox.critical(self, "Database Load Error", 
                                 f"An error occurred while loading user data: {str(e)}\n\n{traceback.format_exc()}")
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        finally:
            if cursor: cursor.close()
            if connection: self.db.release_connection(connection)
    
    def process_save_user(self):
        """Validate input and save user data (create new or update existing)."""
        full_name = self.full_name_input.text().strip()
        username = self.username_input.text().strip()
        email = self.email_input.text().strip() 
        role = self.role_combo.currentText()
    
        if not full_name:
            QMessageBox.warning(self, "Input Required", "Full Name cannot be empty.")
            self.full_name_input.setFocus()
            return
    
        if not username:
            QMessageBox.warning(self, "Input Required", "Username cannot be empty.")
            self.username_input.setFocus()
            return
        
        if not username.isalnum() and '_' not in username and '-' not in username:
             QMessageBox.warning(self, "Invalid Username", "Username can only contain letters, numbers, underscores, and hyphens.")
             self.username_input.setFocus()
             return

        password_for_db = None 
        if not self.user_id_being_edited: 
            password_input_text = self.password_input.text() 
            if not password_input_text:
                QMessageBox.warning(self, "Input Required", "Password is required for new users.")
                self.password_input.setFocus()
                return
            if len(password_input_text) < 6: 
                QMessageBox.warning(self, "Password Too Short", "Password must be at least 6 characters long.")
                self.password_input.setFocus()
                return
            password_for_db = password_input_text
        elif self.reset_password_check.isChecked(): 
            new_password_text = self.new_password_input.text()
            if not new_password_text:
                QMessageBox.warning(self, "Input Required", "New Password is required when 'Reset Password' is checked.")
                self.new_password_input.setFocus()
                return
            if len(new_password_text) < 6:
                QMessageBox.warning(self, "Password Too Short", "New Password must be at least 6 characters long.")
                self.new_password_input.setFocus()
                return
            password_for_db = new_password_text

        connection = None
        cursor = None
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            username_check_query = "SELECT user_id FROM users WHERE LOWER(username) = LOWER(%s)"
            username_check_params = [username]
            if self.user_id_being_edited: 
                username_check_query += " AND user_id != %s"
                username_check_params.append(self.user_id_being_edited)
            
            cursor.execute(username_check_query, tuple(username_check_params))
            existing_user_with_same_name = cursor.fetchone()
            if existing_user_with_same_name:
                QMessageBox.warning(self, "Username Exists", 
                                    f"The username '{username}' is already in use. Please choose a different one.")
                self.username_input.setFocus()
                return

            log_message_action_details = ""
            target_user_id_for_log = self.user_id_being_edited

            if self.user_id_being_edited: 
                is_active_status = self.active_check.isChecked()
                if password_for_db: 
                    hashed_password = self.auth.hash_password(password_for_db)
                    update_query = """
                        UPDATE users SET username=%s, full_name=%s, email=%s, role=%s, is_active=%s, password=%s
                        WHERE user_id=%s
                    """ 
                    cursor.execute(update_query, (
                        username, full_name, email, role, is_active_status, hashed_password, 
                        self.user_id_being_edited
                    ))
                    log_message_action_details = f"Updated user (ID: {self.user_id_being_edited}) '{username}' details and reset password."
                else: 
                    update_query = """
                        UPDATE users SET username=%s, full_name=%s, email=%s, role=%s, is_active=%s
                        WHERE user_id=%s
                    """ 
                    cursor.execute(update_query, (
                        username, full_name, email, role, is_active_status, 
                        self.user_id_being_edited
                    ))
                    log_message_action_details = f"Updated user (ID: {self.user_id_being_edited}) '{username}' details."
            else: 
                hashed_password = self.auth.hash_password(password_for_db)
                insert_query = """
                    INSERT INTO users (username, password, full_name, email, role, is_active, created_at)
                    VALUES (%s, %s, %s, %s, %s, TRUE, %s) RETURNING user_id 
                """ 
                current_time_utc = datetime.datetime.utcnow()
                cursor.execute(insert_query, (
                    username, hashed_password, full_name, email, role, 
                    current_time_utc 
                ))
                newly_created_user_id = cursor.fetchone()[0]
                target_user_id_for_log = newly_created_user_id 
                log_message_action_details = f"Created new user (ID: {newly_created_user_id}) '{username}'."
            
            connection.commit()
            
            if self.current_admin_user and self.current_admin_user.get('user_id') != -1 :
                 self.auth.log_activity(
                     self.current_admin_user['user_id'], 
                     "save_user_details", 
                     "users",
                     target_user_id_for_log,
                     log_message_action_details
                 )
            else:
                print(f"Warning: Admin context invalid or missing for logging activity: {log_message_action_details}")

            QMessageBox.information(self, "Success", f"User '{username}' details have been saved successfully.")
            super().accept() 
            
        except Exception as e:
            if connection: connection.rollback()
            QMessageBox.critical(self, "Database Operation Error", 
                                 f"An error occurred while saving user data: {str(e)}\n\n{traceback.format_exc()}")
        finally:
            if cursor: cursor.close()
            if connection: self.db.release_connection(connection)


class UserManagementWidget(QWidget):
    """Widget for managing users (listing, adding, editing, deleting)."""
    
    def __init__(self, current_user_session): 
        super().__init__()
        self.user = current_user_session 
        self.db = DatabaseConnection()
        self.auth = Authentication()
        self.init_ui()
        self.load_users() 
    
    def init_ui(self):
        """Initialize the UI components for user management."""
        main_layout = QVBoxLayout(self)
        self.setWindowIcon(QIcon("resources/icons/users.png")) # Replace with your actual icon path

        filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout(filter_group)
        
        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("By Username or Full Name...")
        self.search_input.textChanged.connect(self.filter_users) 
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addSpacing(20) 

        filter_layout.addWidget(QLabel("Role:"))
        self.role_filter = QComboBox()
        self.role_filter.addItem("All Roles", None) 
        self.role_filter.addItems(["Admin", "Pharmacist", "Cashier"]) 
        self.role_filter.currentIndexChanged.connect(self.filter_users)
        filter_layout.addWidget(self.role_filter)

        filter_layout.addSpacing(20)

        filter_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Statuses", None) 
        self.status_filter.addItem("Active", True) 
        self.status_filter.addItem("Inactive", False)
        self.status_filter.currentIndexChanged.connect(self.filter_users)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addStretch() 
        main_layout.addWidget(filter_group)
        
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6) 
        self.users_table.setHorizontalHeaderLabels([
            "User ID", "Username", "Full Name", "Role", "Status", "Actions"
        ])
        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch) 
        header.setStretchLastSection(False) 
        
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers) 
        self.users_table.setAlternatingRowColors(True) 
        self.users_table.setSelectionMode(QTableWidget.SingleSelection) 
        self.users_table.setShowGrid(True) 
        main_layout.addWidget(self.users_table)
        
        buttons_layout = QHBoxLayout()
        add_user_btn = QPushButton(" Add New User") 
        add_user_btn.setIcon(QIcon("resources/icons/add_user.png")) # Replace with your actual icon path
        add_user_btn.clicked.connect(self.add_user) 
        buttons_layout.addWidget(add_user_btn)
        
        refresh_btn = QPushButton(" Refresh List")
        refresh_btn.setIcon(QIcon("resources/icons/refresh.png")) # Replace with your actual icon path
        refresh_btn.clicked.connect(self.load_users)
        buttons_layout.addWidget(refresh_btn)
        
        buttons_layout.addStretch() 
        main_layout.addLayout(buttons_layout)
    
    def load_users(self): 
        """Load users from the database and populate the table."""
        connection = None
        cursor = None
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            query = "SELECT user_id, username, full_name, role, is_active FROM users ORDER BY username ASC"
            cursor.execute(query)
            all_users_data = cursor.fetchall()
            
            self.users_table.setRowCount(0) 
            self.users_table.setSortingEnabled(False)

            for row_idx, user_record_tuple in enumerate(all_users_data):
                self.users_table.insertRow(row_idx)
                user_id, username, full_name, role, is_active_db_val = user_record_tuple
                
                self.users_table.setItem(row_idx, 0, QTableWidgetItem(str(user_id)))
                self.users_table.setItem(row_idx, 1, QTableWidgetItem(username))
                self.users_table.setItem(row_idx, 2, QTableWidgetItem(full_name))
                self.users_table.setItem(row_idx, 3, QTableWidgetItem(role))
                
                is_active_bool = bool(is_active_db_val)
                status_text = "Active" if is_active_bool else "Inactive"
                status_item = QTableWidgetItem(status_text)
                status_item.setForeground(QColor("#2ECC71") if is_active_bool else QColor("#E74C3C"))
                status_item.setData(Qt.UserRole, is_active_bool) 
                self.users_table.setItem(row_idx, 4, status_item)
                
                actions_widget_container = QWidget()
                actions_layout_hbox = QHBoxLayout(actions_widget_container)
                actions_layout_hbox.setContentsMargins(5,2,5,2) 
                actions_layout_hbox.setSpacing(5) 
                
                edit_btn = QPushButton()
                edit_btn.setIcon(QIcon("resources/icons/edit.png")) # Replace with your actual icon path
                edit_btn.setToolTip(f"Edit details for user: {username}")
                edit_btn.setFixedSize(28, 28) 
                edit_btn.clicked.connect(lambda checked=False, uid_to_edit=user_id: self.edit_user(uid_to_edit)) 
                actions_layout_hbox.addWidget(edit_btn)
                
                allow_delete = True
                if user_id == self.user['user_id']:
                    allow_delete = False
                if role == "Admin" and self.user['role'] != "Admin":
                    allow_delete = False
                
                if allow_delete:
                    delete_btn = QPushButton()
                    delete_btn.setIcon(QIcon("resources/icons/delete.png")) # Replace with your actual icon path
                    delete_btn.setToolTip(f"Delete user: {username}")
                    delete_btn.setFixedSize(28, 28)
                    delete_btn.clicked.connect(lambda checked=False, uid=user_id, uname=username: \
                                               self.delete_user(uid, uname)) 
                    actions_layout_hbox.addWidget(delete_btn)
                
                actions_layout_hbox.addStretch() 
                self.users_table.setCellWidget(row_idx, 5, actions_widget_container)
            
            self.users_table.setSortingEnabled(True)
            self.filter_users() 

        except Exception as e:
            QMessageBox.critical(self, "Error Loading Users", 
                                 f"An unexpected error occurred while loading the user list: {str(e)}\n\n{traceback.format_exc()}")
        finally:
            if cursor: cursor.close()
            if connection: self.db.release_connection(connection)
    
    def filter_users(self): 
        """Filter the visibility of rows in the users table based on current filter settings."""
        search_text = self.search_input.text().lower()
        selected_role_filter = self.role_filter.currentText() 
        selected_status_filter = self.status_filter.currentData() 

        for row_num in range(self.users_table.rowCount()):
            username_cell_item = self.users_table.item(row_num, 1)
            full_name_cell_item = self.users_table.item(row_num, 2)
            role_cell_item = self.users_table.item(row_num, 3)
            status_cell_item = self.users_table.item(row_num, 4) 

            if not all([username_cell_item, full_name_cell_item, role_cell_item, status_cell_item]):
                self.users_table.setRowHidden(row_num, True)
                continue

            username_in_table = username_cell_item.text().lower()
            full_name_in_table = full_name_cell_item.text().lower()
            role_in_table = role_cell_item.text()
            is_active_in_table = status_cell_item.data(Qt.UserRole) 

            show_this_row = True
            
            if search_text and not (search_text in username_in_table or search_text in full_name_in_table):
                show_this_row = False
            
            if selected_role_filter != "All Roles" and role_in_table != selected_role_filter:
                show_this_row = False
            
            if selected_status_filter is not None and is_active_in_table != selected_status_filter:
                show_this_row = False
            
            self.users_table.setRowHidden(row_num, not show_this_row)
    
    def add_user(self): 
        """Open the UserDialog for adding a new user."""
        add_dialog = UserDialog(parent=self) 
        if add_dialog.exec_() == QDialog.Accepted: 
            self.load_users() 
    
    def edit_user(self, user_id_to_edit): 
        """Open the UserDialog for editing an existing user."""
        edit_dialog = UserDialog(parent=self, user_id_to_edit=user_id_to_edit)
        if edit_dialog.exec_() == QDialog.Accepted:
            self.load_users()
    
    def delete_user(self, user_id_to_delete, username_to_delete): 
        """Handles logic for deleting or deactivating a user based on sales and audit log records."""
        
        if user_id_to_delete == self.user['user_id']:
            QMessageBox.warning(self, "Action Not Allowed", "You cannot delete your own account.")
            return

        connection = None
        cursor = None
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()

            # Get current status and role of the user to be deleted
            cursor.execute("SELECT is_active, role FROM users WHERE user_id = %s", (user_id_to_delete,))
            user_to_delete_info = cursor.fetchone()

            if not user_to_delete_info:
                QMessageBox.warning(self, "User Not Found", f"User '{username_to_delete}' (ID: {user_id_to_delete}) not found.")
                return
            
            is_user_to_delete_active = bool(user_to_delete_info[0])
            role_of_user_to_delete = user_to_delete_info[1]

            # Prevent non-admin from deleting admin
            if role_of_user_to_delete == "Admin" and self.user['role'] != "Admin":
                QMessageBox.warning(self, "Permission Denied", "Only other Admins can delete an Admin account.")
                return

            # Initial confirmation for any action
            initial_confirm_reply = QMessageBox.question(self, "Confirm Action",
                f"Proceed with actions for user '{username_to_delete}' (ID: {user_id_to_delete})?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if initial_confirm_reply == QMessageBox.No:
                return 

            # Check for associated sales records
            cursor.execute("SELECT COUNT(*) FROM sales WHERE user_id = %s", (user_id_to_delete,))
            sales_count = cursor.fetchone()[0]

            # Check for associated audit log entries
            cursor.execute("SELECT COUNT(*) FROM audit_logs WHERE user_id = %s", (user_id_to_delete,))
            audit_logs_count = cursor.fetchone()[0]

            log_action_type = ""
            log_details = ""
            action_performed = False

            # If user has sales OR audit logs, they cannot be hard-deleted.
            # Offer deactivation if they are currently active.
            if sales_count > 0 or audit_logs_count > 0:
                reason_parts = []
                if sales_count > 0:
                    reason_parts.append(f"{sales_count} sales record(s)")
                if audit_logs_count > 0:
                    reason_parts.append(f"{audit_logs_count} audit log entries")
                reason_str = " and ".join(reason_parts)

                if is_user_to_delete_active:
                    deactivate_reply = QMessageBox.question(self, "User Has Dependent Records",
                        f"User '{username_to_delete}' has {reason_str} and cannot be deleted while active.\n"
                        "Would you like to DEACTIVATE this user's account instead?",
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

                    if deactivate_reply == QMessageBox.Yes:
                        cursor.execute("UPDATE users SET is_active = FALSE WHERE user_id = %s", (user_id_to_delete,))
                        connection.commit()
                        log_action_type = "deactivate_user_with_dependencies"
                        log_details = f"Deactivated user '{username_to_delete}' (ID: {user_id_to_delete}) due to {reason_str}."
                        QMessageBox.information(self, "User Deactivated", f"User '{username_to_delete}' has been deactivated.")
                        action_performed = True
                    else:
                        QMessageBox.information(self, "Action Cancelled", f"No action taken for user '{username_to_delete}'.")
                else:
                    # User is already INACTIVE and has sales/audit logs
                    QMessageBox.information(self, "Cannot Delete User",
                        f"User '{username_to_delete}' is already INACTIVE and has {reason_str}.\n"
                        "Users with existing sales or audit trail records cannot be permanently deleted to maintain data integrity.")
                    action_performed = False 
            else:
                # User has NO sales records AND NO audit logs - Can be deleted
                standard_delete_reply = QMessageBox.question(self, "Confirm Permanent Deletion",
                    f"User '{username_to_delete}' has no sales or audit log records.\n"
                    "Are you sure you want to permanently delete this user? This action cannot be undone.",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No) 
                
                if standard_delete_reply == QMessageBox.Yes:
                    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id_to_delete,))
                    connection.commit()
                    log_action_type = "delete_user_no_dependencies"
                    log_details = f"Permanently deleted user '{username_to_delete}' (ID: {user_id_to_delete}). User had no sales or audit logs. Was active: {is_user_to_delete_active}."
                    QMessageBox.information(self, "User Deleted", f"User '{username_to_delete}' has been permanently deleted.")
                    action_performed = True
                else:
                    QMessageBox.information(self, "Deletion Cancelled", f"Deletion of user '{username_to_delete}' was cancelled.")
            
            if action_performed and log_action_type and self.user and 'user_id' in self.user:
                 self.auth.log_activity(
                     self.user['user_id'], 
                     log_action_type, 
                     "users", 
                     user_id_to_delete, 
                     log_details
                 )
            
            if action_performed: 
                self.load_users() 

        except Exception as e:
            if connection: connection.rollback() 
            QMessageBox.critical(self, "Operation Error", 
                                 f"An error occurred while processing user '{username_to_delete}': {str(e)}\n\n{traceback.format_exc()}")
        finally:
            if cursor: cursor.close()
            if connection: self.db.release_connection(connection)