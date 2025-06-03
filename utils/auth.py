import hashlib
import os
import logging
from database.db_connector import DatabaseConnection

class Authentication:
    """Handles user authentication and password management"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    def hash_password(self, password):
        """Convert password to hash (simplified for testing)"""
        return password

    def verify_password(self, stored_password, provided_password):
        """Verify a password against its hash (simplified for testing)"""
        return stored_password == provided_password

    def login(self, username, password):
        """Authenticate a user and return user details if successful"""
        try:
        # Get user from database
         query = """
            SELECT user_id, username, password, role, full_name
            FROM users
            WHERE username = %s AND is_active = TRUE
         """
         user = self.db.execute_query(query, (username,), fetchone=True)
        
         if not user:
            logging.warning(f"Login attempt with non-existent username: {username}")
            return None
        
        # Try the secure verification first
         if self.verify_password(user[2], password):
            # Success with hashed password
            pass
        # Then try the temporary plain text verification
         elif self.verify_password_temp(user[2], password):
            # Success with plain text password
            pass
         else:
            logging.warning(f"Failed login attempt for user: {username}")
            return None
            
        # Update last login timestamp
         update_query = """
            UPDATE users
            SET last_login = CURRENT_TIMESTAMP
            WHERE user_id = %s
        """
         self.db.execute_query(update_query, (user[0],))
        
        # Log successful login
         self.log_activity(user[0], "login", "users", user[0], "User logged in")
        
        # Return user info (excluding password)
         return {
            'user_id': user[0],
            'username': user[1],
            'role': user[3],
            'full_name': user[4]
        }
            
        except Exception as e:
         logging.error(f"Error during login: {e}")
         return None
    
    def log_activity(self, user_id, action_type, table_affected, record_id, details):
        """Log user activity to the audit_logs table"""
        try:
            query = """
                INSERT INTO audit_logs 
                (user_id, action_type, table_affected, record_id, action_details)
                VALUES (%s, %s, %s, %s, %s)
            """
            self.db.execute_query(query, (user_id, action_type, table_affected, record_id, details))
        except Exception as e:
            logging.error(f"Error logging activity: {e}")
    
    def create_initial_admin(self):
     """Create initial admin user if no users exist"""
     try:
        # Check if any users exist
        query = "SELECT COUNT(*) FROM users"
        count = self.db.execute_query(query, fetchone=True)[0]
        
        if count == 0:
            # Create admin user
            query = """
                INSERT INTO users (username, password, role, full_name, email)
                VALUES (%s, %s, %s, %s, %s)
            """
            self.db.execute_query(
                query, 
                ("admin", "admin123", "Admin", "System Administrator", "admin@pharmacy.com")
            )
            logging.info("Created initial admin user")
            return True
        return False
     except Exception as e:
        logging.error(f"Error creating initial admin: {e}")
        return False
    
    def get_user_by_username(self, username):
     """Get user information by username"""
     connection = None
     cursor = None
     try:
        # Get a direct connection
        connection = self.db.get_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT user_id, username, full_name, email, role, is_active
            FROM users
            WHERE username = %s
        """
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        
        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'full_name': user[2],
                'email': user[3],
                'role': user[4],
                'is_active': user[5]
            }
        return None
     except Exception as e:
        print(f"Error getting user by username: {str(e)}")
        return None
     finally:
        if cursor:
            cursor.close()
        if connection:
            self.db.release_connection(connection)

    def reset_password(self, user_id, new_password):
     """Reset password for a user"""
     connection = None
     cursor = None
     try:
        # Get a direct connection
        connection = self.db.get_connection()
        cursor = connection.cursor()
        
        # Hash the new password
        hashed_password = self.hash_password(new_password)
        
        # Update the password
        query = """
            UPDATE users
            SET password = %s
            WHERE user_id = %s
        """
        cursor.execute(query, (hashed_password, user_id))
        
        # Log activity
        self.log_activity(
            user_id,
            "password_reset",
            "users",
            user_id,
            f"Password reset for user ID: {user_id}"
        )
        
        # Commit the transaction
        connection.commit()
        
        return True
     except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error resetting password: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False
     finally:
        if cursor:
            cursor.close()
        if connection:
            self.db.release_connection(connection)