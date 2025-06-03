from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, 
                            QGroupBox, QMessageBox, QHeaderView, QDialog, QFormLayout,
                            QDialogButtonBox, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont

from database.db_connector import DatabaseConnection
from utils.auth import Authentication

class SupplierDialog(QDialog):
    """Dialog for adding or editing suppliers"""
    
    def __init__(self, parent=None, supplier_id=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.auth = Authentication()
        self.supplier_id = supplier_id
        self.user = parent.user
        self.init_ui()
        
        if supplier_id:
            self.setWindowTitle("Edit Supplier")
            self.load_supplier_data()
        else:
            self.setWindowTitle("Add New Supplier")
    
    def init_ui(self):
        """Initialize the UI components"""
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout(self)
        
        # Form layout for supplier details
        form_layout = QFormLayout()
        
        # Supplier name
        self.name_input = QLineEdit()
        form_layout.addRow("Supplier Name*:", self.name_input)
        
        # Contact person
        self.contact_person_input = QLineEdit()
        form_layout.addRow("Contact Person:", self.contact_person_input)
        
        # Phone
        self.phone_input = QLineEdit()
        form_layout.addRow("Phone:", self.phone_input)
        
        # Email
        self.email_input = QLineEdit()
        form_layout.addRow("Email:", self.email_input)
        
        # Address
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(80)
        form_layout.addRow("Address:", self.address_input)
        
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
    
    def load_supplier_data(self):
        """Load supplier data if editing existing supplier"""
        try:
            query = """
                SELECT name, contact_person, phone, email, address
                FROM suppliers
                WHERE supplier_id = %s
            """
            supplier = self.db.execute_query(query, (self.supplier_id,), fetchone=True)
            
            if supplier:
                self.name_input.setText(supplier[0])
                self.contact_person_input.setText(supplier[1] or "")
                self.phone_input.setText(supplier[2] or "")
                self.email_input.setText(supplier[3] or "")
                self.address_input.setText(supplier[4] or "")
            else:
                QMessageBox.warning(self, "Warning", "Supplier not found.")
                self.reject()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load supplier data: {str(e)}")
            self.reject()
    
    def accept(self):
     """Handle dialog acceptance (OK button)"""
     # Validate input
     name = self.name_input.text().strip()
     if not name:
        QMessageBox.warning(self, "Validation Error", "Supplier name is required.")
        return
    
    # Create direct database connection for this operation
     connection = None
     cursor = None
     try:
        # Get values
        contact_person = self.contact_person_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        address = self.address_input.toPlainText().strip()
        
        # Get a direct connection
        connection = self.db.get_connection()
        cursor = connection.cursor()
        
        if self.supplier_id:
            # Update existing supplier
            query = """
                UPDATE suppliers
                SET name = %s, contact_person = %s, phone = %s, email = %s, 
                    address = %s, updated_at = CURRENT_TIMESTAMP
                WHERE supplier_id = %s
            """
            cursor.execute(
                query, 
                (name, contact_person, phone, email, address, self.supplier_id)
            )
            
            # Log activity
            self.auth.log_activity(
                self.user['user_id'],
                "update",
                "suppliers",
                self.supplier_id,
                f"Updated supplier: {name}"
            )
        else:
            # Insert new supplier
            query = """
                INSERT INTO suppliers
                (name, contact_person, phone, email, address)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING supplier_id
            """
            cursor.execute(
                query, 
                (name, contact_person, phone, email, address)
            )
            
            result = cursor.fetchone()
            new_supplier_id = result[0]
            
            # Log activity
            self.auth.log_activity(
                self.user['user_id'],
                "insert",
                "suppliers",
                new_supplier_id,
                f"Created new supplier: {name}"
            )
        
        # Explicitly commit the transaction
        connection.commit()
        
        QMessageBox.information(
            self, 
            "Success", 
            f"Supplier '{name}' {'updated' if self.supplier_id else 'created'} successfully."
        )
        
        super().accept()
        
     except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error in supplier accept method: {str(e)}")
        import traceback
        print(traceback.format_exc())
        QMessageBox.critical(self, "Error", f"Failed to save supplier: {str(e)}")
     finally:
        if cursor:
            cursor.close()
        if connection:
            self.db.release_connection(connection)


class SupplierManagementWidget(QWidget):
    """Widget for managing suppliers"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseConnection()
        self.auth = Authentication()
        self.init_ui()
        self.load_suppliers()
    
    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)
        
        # Search section
        search_group = QGroupBox("Search")
        search_layout = QHBoxLayout(search_group)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search suppliers by name, contact, phone, or email...")
        self.search_input.textChanged.connect(self.filter_suppliers)
        search_layout.addWidget(self.search_input)
        
        main_layout.addWidget(search_group)
        
        # Suppliers table
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(6)
        self.suppliers_table.setHorizontalHeaderLabels([
            "ID", "Name", "Contact Person", "Phone", "Email", "Actions"
        ])
        self.suppliers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.suppliers_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.suppliers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.suppliers_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.suppliers_table)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        add_supplier_btn = QPushButton("Add Supplier")
        add_supplier_btn.setIcon(QIcon("resources/icons/add.png"))
        add_supplier_btn.clicked.connect(self.add_supplier)
        buttons_layout.addWidget(add_supplier_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        refresh_btn.clicked.connect(self.load_suppliers)
        buttons_layout.addWidget(refresh_btn)
        
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)
    
    def load_suppliers(self):
     """Load suppliers from database into table"""
     connection = None
     cursor = None
     try:
        # Get a direct connection
        connection = self.db.get_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT supplier_id, name, contact_person, phone, email, address
            FROM suppliers
            ORDER BY name
        """
        cursor.execute(query)
        suppliers = cursor.fetchall()
        
        self.suppliers_table.setRowCount(0)
        
        for row_idx, supplier in enumerate(suppliers):
            self.suppliers_table.insertRow(row_idx)
            
            supplier_id, name, contact_person, phone, email, address = supplier
            
            # Supplier ID
            self.suppliers_table.setItem(row_idx, 0, QTableWidgetItem(str(supplier_id)))
            
            # Name
            self.suppliers_table.setItem(row_idx, 1, QTableWidgetItem(name))
            
            # Contact Person
            self.suppliers_table.setItem(row_idx, 2, QTableWidgetItem(contact_person or ""))
            
            # Phone
            self.suppliers_table.setItem(row_idx, 3, QTableWidgetItem(phone or ""))
            
            # Email
            self.suppliers_table.setItem(row_idx, 4, QTableWidgetItem(email or ""))
            
            # Store address in a hidden role for tooltip
            if address:
                self.suppliers_table.item(row_idx, 1).setToolTip(f"Address: {address}")
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(2)
            
            view_btn = QPushButton()
            view_btn.setIcon(QIcon("resources/icons/view.png"))
            view_btn.setToolTip("View Supplier Details")
            view_btn.setMaximumWidth(30)
            view_btn.clicked.connect(lambda _, sid=supplier_id: self.view_supplier(sid))
            actions_layout.addWidget(view_btn)
            
            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon("resources/icons/edit.png"))
            edit_btn.setToolTip("Edit Supplier")
            edit_btn.setMaximumWidth(30)
            edit_btn.clicked.connect(lambda _, sid=supplier_id: self.edit_supplier(sid))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon("resources/icons/delete.png"))
            delete_btn.setToolTip("Delete Supplier")
            delete_btn.setMaximumWidth(30)
            delete_btn.clicked.connect(lambda _, sid=supplier_id, sname=name: self.delete_supplier(sid, sname))
            actions_layout.addWidget(delete_btn)
            
            self.suppliers_table.setCellWidget(row_idx, 5, actions_widget)
        
        self.suppliers_table.resizeColumnsToContents()
        self.suppliers_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
     except Exception as e:
        print(f"Error loading suppliers: {str(e)}")
        import traceback
        print(traceback.format_exc())
        QMessageBox.critical(self, "Error", f"Failed to load suppliers: {str(e)}")
     finally:
        if cursor:
            cursor.close()
        if connection:
            self.db.release_connection(connection)
    
    def filter_suppliers(self):
        """Filter suppliers based on search text"""
        search_text = self.search_input.text().lower()
        
        for row in range(self.suppliers_table.rowCount()):
            show_row = True
            
            if search_text:
                # Check all columns for a match
                match_found = False
                for col in range(1, 5):  # Skip ID column
                    cell_text = self.suppliers_table.item(row, col).text().lower()
                    if search_text in cell_text:
                        match_found = True
                        break
                
                if not match_found:
                    show_row = False
            
            self.suppliers_table.setRowHidden(row, not show_row)
    
    def add_supplier(self):
        """Add a new supplier"""
        dialog = SupplierDialog(self)
        if dialog.exec_():
            self.load_suppliers()
    
    def view_supplier(self, supplier_id):
     """View supplier details"""
     connection = None
     cursor = None
     try:
        # Get a direct connection
        connection = self.db.get_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT name, contact_person, phone, email, address
            FROM suppliers
            WHERE supplier_id = %s
        """
        cursor.execute(query, (supplier_id,))
        supplier = cursor.fetchone()
        
        if supplier:
            name, contact_person, phone, email, address = supplier
            
            details = f"<b>Name:</b> {name}<br>"
            if contact_person:
                details += f"<b>Contact Person:</b> {contact_person}<br>"
            if phone:
                details += f"<b>Phone:</b> {phone}<br>"
            if email:
                details += f"<b>Email:</b> {email}<br>"
            if address:
                details += f"<b>Address:</b> {address}<br>"
            
            QMessageBox.information(self, "Supplier Details", details)
        else:
            QMessageBox.warning(self, "Not Found", "Supplier details not found.")
            
     except Exception as e:
        print(f"Error viewing supplier: {str(e)}")
        import traceback
        print(traceback.format_exc())
        QMessageBox.critical(self, "Error", f"Failed to load supplier details: {str(e)}")
     finally:
        if cursor:
            cursor.close()
        if connection:
            self.db.release_connection(connection)
    
    def edit_supplier(self, supplier_id):
        """Edit an existing supplier"""
        dialog = SupplierDialog(self, supplier_id)
        if dialog.exec_():
            self.load_suppliers()
    
    def delete_supplier(self, supplier_id, supplier_name):
     """Delete a supplier"""
     reply = QMessageBox.question(
        self, 
        "Confirm Delete", 
        f"Are you sure you want to delete supplier '{supplier_name}'?\nThis action cannot be undone.",
        QMessageBox.Yes | QMessageBox.No, 
        QMessageBox.No
    )
    
     if reply == QMessageBox.Yes:
        connection = None
        cursor = None
        try:
            # Get a direct connection
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            # Check if supplier is used in any products
            check_query = """
                SELECT COUNT(*) FROM products 
                WHERE supplier_id = %s
            """
            cursor.execute(check_query, (supplier_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                QMessageBox.warning(
                    self, 
                    "Cannot Delete", 
                    f"Cannot delete '{supplier_name}' because it is associated with {count} products.\nPlease update these products first."
                )
                return
            
            # Delete the supplier
            query = "DELETE FROM suppliers WHERE supplier_id = %s"
            cursor.execute(query, (supplier_id,))
            
            # Explicitly commit the transaction
            connection.commit()
            
            # Log activity
            self.auth.log_activity(
                self.user['user_id'],
                "delete",
                "suppliers",
                supplier_id,
                f"Deleted supplier: {supplier_name}"
            )
            
            QMessageBox.information(self, "Success", f"Supplier '{supplier_name}' deleted successfully.")
            self.load_suppliers()
            
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"Error deleting supplier: {str(e)}")
            import traceback
            print(traceback.format_exc())
            QMessageBox.critical(self, "Error", f"Failed to delete supplier: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.db.release_connection(connection)