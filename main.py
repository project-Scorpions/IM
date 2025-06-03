import sys
import os
import logging
from configparser import ConfigParser
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Import UI components
from ui.login import LoginWindow
from database.db_connector import DatabaseConnection

def create_config_if_not_exists():
    """Create default config.ini if it doesn't exist"""
    config_file = 'config.ini'
    if not os.path.exists(config_file):
        config = ConfigParser()
        
        # Database section
        config['database'] = {
            'host': 'localhost',
            'database': 'pharmacy_db',
            'user': 'postgres',
            'password': 'your_new_password',  # Change this to a secure password
            'port': '5432',
            'min_connections': '1',
            'max_connections': '10'
        }
        
        # Application section
        config['application'] = {
            'name': 'Pharmacy Management System',
            'company': 'Scorpions Pharmacy',
            'version': '1.0.0',
            'currency_symbol': '₱'  # Set default currency symbol to Philippine Peso
        }
        
        # Write to file
        with open(config_file, 'w') as f:
            config.write(f)
        
        logging.info(f"Created default configuration file: {config_file}")

def test_database_connection():
    """Test database connection and initialize schema if needed"""
    try:
        # Create a database connection instance
        db = DatabaseConnection()
        
        # Test basic connection
        query = "SELECT current_timestamp as time, current_user as user"
        result = db.execute_query(query, fetchone=True)
        logging.info(f"Database connection successful! Time: {result[0]}, User: {result[1]}")
        
        # Check if essential tables exist
        tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """
        tables = db.execute_query(tables_query, fetchall=True)
        table_names = [t[0] for t in tables]
        logging.info(f"Existing tables: {table_names}")
        
        # Check if categories table exists
        if 'categories' not in table_names:
            logging.warning("Categories table not found, creating it...")
            create_tables(db)
        
        return True
    except Exception as e:
        logging.error(f"Database connection failed: {str(e)}")
        return False

def create_tables(db):
    """Create essential tables if they don't exist"""
    try:
        # Categories table
        categories_query = """
            CREATE TABLE IF NOT EXISTS categories (
                category_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        db.execute_query(categories_query)
        logging.info("Categories table created successfully")
        
        # Products table (if needed)
        products_query = """
            CREATE TABLE IF NOT EXISTS products (
                product_id SERIAL PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                category_id INTEGER REFERENCES categories(category_id),
                description TEXT,
                unit_price NUMERIC(10,2) NOT NULL,
                cost_price NUMERIC(10,2) NOT NULL,
                stock_quantity INTEGER NOT NULL DEFAULT 0,
                expiry_date DATE,
                reorder_level INTEGER NOT NULL DEFAULT 10,
                supplier_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        db.execute_query(products_query)
        logging.info("Products table created successfully")
        
        # Add other essential tables here as needed
        
        return True
    except Exception as e:
        logging.error(f"Error creating tables: {str(e)}")
        return False

def main():
    """Main application entry point"""
    try:
        # Create default config if it doesn't exist
        create_config_if_not_exists()

        # Enable High DPI Scaling BEFORE creating QApplication
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

        # Initialize application
        app = QApplication(sys.argv)
        app.setApplicationName("Pharmacy Management System")
        app.setStyle("Fusion")  # Modern style
        
        # Test database connection
        if not test_database_connection():
            # Show error message box
            QMessageBox.critical(
                None, 
                "Database Connection Error",
                "Failed to connect to the database. Please check your configuration and ensure PostgreSQL is running."
            )
            sys.exit(1)
            
        # Show login window
        login_window = LoginWindow()
        login_window.show()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        logging.critical(f"Application failed to start: {e}")
        
        # Show error message if application is initialized
        if 'app' in locals():
            QMessageBox.critical(
                None, 
                "Application Error",
                f"Application failed to start: {str(e)}"
            )
        raise

if __name__ == "__main__":
    main()