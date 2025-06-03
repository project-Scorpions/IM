from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QTabWidget, QWidget, QFormLayout, QLineEdit, QSpinBox,
                           QCheckBox, QComboBox, QGroupBox, QMessageBox, QFileDialog,
                           QDialogButtonBox, QColorDialog, QFontDialog)
from PyQt5.QtCore import Qt, QSettings, QSize
from PyQt5.QtGui import QIcon, QFont, QColor

import os
import datetime
from configparser import ConfigParser
from utils.backup import DatabaseBackup

class SettingsDialog(QDialog):
    """Settings dialog for application configuration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.backup_utility = DatabaseBackup()
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle("Settings")
        self.setMinimumSize(600, 400)
        self.setWindowIcon(QIcon("resources/icons/settings.png"))
        
        main_layout = QVBoxLayout(self)
        
        # Database tab - directly adding to main layout instead of using tabs
        database_widget = QWidget()
        database_layout = QVBoxLayout(database_widget)
        
        # Database connection settings
        db_group = QGroupBox("Database Connection")
        db_form = QFormLayout(db_group)
        
        self.db_host_input = QLineEdit()
        db_form.addRow("Host:", self.db_host_input)
        
        self.db_port_input = QSpinBox()
        self.db_port_input.setRange(1, 65535)
        self.db_port_input.setValue(5432)
        db_form.addRow("Port:", self.db_port_input)
        
        self.db_name_input = QLineEdit()
        db_form.addRow("Database Name:", self.db_name_input)
        
        self.db_user_input = QLineEdit()
        db_form.addRow("Username:", self.db_user_input)
        
        self.db_password_input = QLineEdit()
        self.db_password_input.setEchoMode(QLineEdit.Password)
        db_form.addRow("Password:", self.db_password_input)
        
        database_layout.addWidget(db_group)
        
        # Database pool settings
        pool_group = QGroupBox("Connection Pool")
        pool_form = QFormLayout(pool_group)
        
        self.min_connections_input = QSpinBox()
        self.min_connections_input.setRange(1, 20)
        pool_form.addRow("Minimum Connections:", self.min_connections_input)
        
        self.max_connections_input = QSpinBox()
        self.max_connections_input.setRange(5, 50)
        pool_form.addRow("Maximum Connections:", self.max_connections_input)
        
        database_layout.addWidget(pool_group)
        
        # Backup and restore
        backup_group = QGroupBox("Backup and Restore")
        backup_layout = QVBoxLayout(backup_group)
        
        backup_btn = QPushButton("Backup Database Now")
        backup_btn.setIcon(QIcon("resources/icons/backup.png"))
        backup_btn.clicked.connect(self.backup_database)
        backup_layout.addWidget(backup_btn)
        
        restore_btn = QPushButton("Restore Database from Backup")
        restore_btn.setIcon(QIcon("resources/icons/restore.png"))
        restore_btn.clicked.connect(self.restore_database)
        backup_layout.addWidget(restore_btn)
        
        database_layout.addWidget(backup_group)
        
        # Add database widget to main layout
        main_layout.addWidget(database_widget)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
    
    def load_settings(self):
        """Load settings from config file"""
        try:
            # Database settings
            self.db_host_input.setText(self.config.get('database', 'host', fallback='localhost'))
            self.db_port_input.setValue(self.config.getint('database', 'port', fallback=5432))
            self.db_name_input.setText(self.config.get('database', 'database', fallback='pharmacy_db'))
            self.db_user_input.setText(self.config.get('database', 'user', fallback='postgres'))
            self.db_password_input.setText(self.config.get('database', 'password', fallback='postgres'))
            
            self.min_connections_input.setValue(self.config.getint('database', 'min_connections', fallback=1))
            self.max_connections_input.setValue(self.config.getint('database', 'max_connections', fallback=10))
            
        except Exception as e:
            QMessageBox.warning(self, "Settings Error", f"Error loading settings: {str(e)}")
    
    def save_settings(self):
        """Save settings to config file"""
        try:
            # Ensure database section exists
            if not self.config.has_section('database'):
                self.config.add_section('database')
            
            # Database settings
            self.config.set('database', 'host', self.db_host_input.text())
            self.config.set('database', 'port', str(self.db_port_input.value()))
            self.config.set('database', 'database', self.db_name_input.text())
            self.config.set('database', 'user', self.db_user_input.text())
            self.config.set('database', 'password', self.db_password_input.text())
            
            self.config.set('database', 'min_connections', str(self.min_connections_input.value()))
            self.config.set('database', 'max_connections', str(self.max_connections_input.value()))
            
            # Write to file
            with open('config.ini', 'w') as f:
                self.config.write(f)
            
            QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.\nSome changes may require a restart to take effect.")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Settings Error", f"Error saving settings: {str(e)}")
    
    def backup_database(self):
        """Backup the database"""
        try:
            # Ask for backup file location
            backup_dir = os.path.join(os.getcwd(), 'backups')
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            default_filename = f"pharmacy_db_backup_{timestamp}.zip"
            
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Database Backup",
                os.path.join(backup_dir, default_filename),
                "Backup Files (*.zip)"
            )
            
            if not filename:
                return
            
            # Show progress message
            QMessageBox.information(self, "Backup Started", "Backup process started. This might take a moment...")
            
            # Perform backup
            success, message, backup_file = self.backup_utility.backup_database(filename)
            
            if success:
                QMessageBox.information(self, "Backup Successful", f"Database backup completed successfully.\nBackup saved to: {backup_file}")
            else:
                QMessageBox.critical(self, "Backup Failed", message)
                
        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"An error occurred during backup: {str(e)}")
    
    def restore_database(self):
        """Restore the database from backup"""
        try:
            # Confirm restore
            reply = QMessageBox.warning(
                self, 
                "Confirm Restore", 
                "Restoring from backup will overwrite the current database. This action cannot be undone.\n\nAre you sure you want to continue?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # Ask for backup file
            backup_dir = os.path.join(os.getcwd(), 'backups')
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Select Backup File to Restore",
                backup_dir,
                "Backup Files (*.zip *.sql)"
            )
            
            if not filename:
                return
            
            # Show progress message
            QMessageBox.information(self, "Restore Started", "Restore process started. This might take a moment...")
            
            # Perform restore
            success, message = self.backup_utility.restore_database(filename)
            
            if success:
                QMessageBox.information(self, "Restore Successful", "Database has been restored successfully.\nYou may need to restart the application to see the changes.")
            else:
                QMessageBox.critical(self, "Restore Failed", message)
                
        except Exception as e:
            QMessageBox.critical(self, "Restore Error", f"An error occurred during restore: {str(e)}")