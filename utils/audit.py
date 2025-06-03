from database.db_connector import DatabaseConnection
import logging
from datetime import datetime

class AuditTrail:
    """Utility class for audit trail operations"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def log_activity(self, user_id, action_type, table_affected, record_id, action_details, ip_address=None):
        """
        Log user activity to the audit_logs table
        
        Parameters:
        - user_id: ID of the user performing the action
        - action_type: Type of action (e.g., "insert", "update", "delete", "login")
        - table_affected: Database table affected by the action
        - record_id: ID of the record affected
        - action_details: Details of the action
        - ip_address: Optional IP address of the user
        
        Returns:
        - int: ID of the created log entry
        """
        try:
            query = """
                INSERT INTO audit_logs 
                (user_id, action_type, table_affected, record_id, action_details, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING log_id
            """
            return self.db.execute_query(
                query, 
                (user_id, action_type, table_affected, record_id, action_details, ip_address),
                fetchone=True
            )[0]
        except Exception as e:
            logging.error(f"Error logging activity: {e}")
            # Don't raise the exception, just log it
            return None
    
    def get_audit_logs(self, filters=None, limit=100, offset=0):
        """
        Get audit logs with optional filtering
        
        Parameters:
        - filters: Dictionary of filters (user_id, action_type, table_affected, date_from, date_to)
        - limit: Maximum number of logs to return
        - offset: Offset for pagination
        
        Returns:
        - list: List of audit log records
        """
        try:
            query = """
                SELECT l.log_id, l.timestamp, l.action_type, l.table_affected, 
                       l.record_id, l.action_details, l.ip_address,
                       u.username, u.full_name
                FROM audit_logs l
                JOIN users u ON l.user_id = u.user_id
                WHERE 1=1
            """
            
            params = []
            
            if filters:
                if 'user_id' in filters and filters['user_id']:
                    query += " AND l.user_id = %s"
                    params.append(filters['user_id'])
                
                if 'action_type' in filters and filters['action_type']:
                    query += " AND l.action_type = %s"
                    params.append(filters['action_type'])
                
                if 'table_affected' in filters and filters['table_affected']:
                    query += " AND l.table_affected = %s"
                    params.append(filters['table_affected'])
                
                if 'date_from' in filters and filters['date_from']:
                    query += " AND l.timestamp::date >= %s"
                    params.append(filters['date_from'])
                
                if 'date_to' in filters and filters['date_to']:
                    query += " AND l.timestamp::date <= %s"
                    params.append(filters['date_to'])
            
            query += " ORDER BY l.timestamp DESC"
            query += " LIMIT %s OFFSET %s"
            
            params.extend([limit, offset])
            
            return self.db.execute_query(query, params, fetchall=True)
            
        except Exception as e:
            logging.error(f"Error getting audit logs: {e}")
            raise
    
    def get_user_activity(self, user_id, limit=50):
        """
        Get recent activity for a specific user
        
        Parameters:
        - user_id: ID of the user
        - limit: Maximum number of logs to return
        
        Returns:
        - list: List of user activity records
        """
        try:
            query = """
                SELECT log_id, timestamp, action_type, table_affected, 
                       record_id, action_details, ip_address
                FROM audit_logs
                WHERE user_id = %s
                ORDER BY timestamp DESC
                LIMIT %s
            """
            
            return self.db.execute_query(query, (user_id, limit), fetchall=True)
            
        except Exception as e:
            logging.error(f"Error getting user activity: {e}")
            raise