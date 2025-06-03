# db_helper.py
import psycopg2
from configparser import ConfigParser
import os

def get_db_config():
    """Get database configuration from config file"""
    config = ConfigParser()
    config_file = os.path.join(os.path.dirname(__file__), 'config.ini')
    config.read(config_file)
    
    return {
        'host': config.get('database', 'host', fallback='localhost'),
        'database': config.get('database', 'database', fallback='pharmacy_db'),
        'user': config.get('database', 'user', fallback='postgres'),
        'password': config.get('database', 'password', fallback='your_new_password'),  # Change this to a secure passwordp
        'port': config.get('database', 'port', fallback='5432')
    }

def verify_database():
    """Verify database structure and connection"""
    try:
        # Connect to PostgreSQL
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Check if categories table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'categories'
            )
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("Categories table does not exist! Creating it...")
            cursor.execute("""
                CREATE TABLE categories (
                    category_id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            print("Categories table created successfully!")
        
        # Try inserting a test category
        cursor.execute("""
            INSERT INTO categories (name, description)
            VALUES (%s, %s)
            RETURNING category_id
        """, ("Test Category", "Created by db_helper.py"))
        
        result = cursor.fetchone()
        conn.commit()
        
        print(f"Test category inserted successfully! ID: {result[0]}")
        
        # List all categories
        cursor.execute("SELECT category_id, name, description FROM categories")
        categories = cursor.fetchall()
        
        print("\nAll Categories:")
        for cat in categories:
            print(f"ID: {cat[0]}, Name: {cat[1]}, Description: {cat[2]}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Database verification error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Database Verification Utility")
    print("============================")
    success = verify_database()
    print(f"\nVerification {'successful' if success else 'failed'}!")