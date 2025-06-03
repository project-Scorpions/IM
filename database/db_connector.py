import psycopg2
from psycopg2 import pool
import os
import logging
from configparser import ConfigParser

class DatabaseConnection:
    """Singleton class to manage database connections using connection pooling"""
    
    _instance = None
    _connection_pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialize_connection_pool()
        return cls._instance
    
    def _initialize_connection_pool(self):
        """Initialize the connection pool from config"""
        try:
            config = ConfigParser()
            config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini')
            config.read(config_file)
            
            # Get database configuration
            db_config = {
                'host': config.get('database', 'host', fallback='localhost'),
                'database': config.get('database', 'database', fallback='pharmacy_db'),
                'user': config.get('database', 'user', fallback='postgres'),
                'password': config.get('database', 'password', fallback='your_new_password'),  # Change this to a secure password
                'port': config.get('database', 'port', fallback='5432')
            }
            
            min_connections = config.getint('database', 'min_connections', fallback=1)
            max_connections = config.getint('database', 'max_connections', fallback=10)
            
            # Create connection pool
            self._connection_pool = pool.ThreadedConnectionPool(
                min_connections,
                max_connections,
                **db_config
            )
            logging.info("Database connection pool initialized successfully")
            
        except (Exception, psycopg2.Error) as error:
            logging.error(f"Error while connecting to PostgreSQL: {error}")
            raise
    
    def ensure_connection_pool(self):
        """Ensure the connection pool is active, reinitialize if closed"""
        if self._connection_pool is None or hasattr(self._connection_pool, '_closed') and self._connection_pool._closed:
            logging.info("Connection pool was closed, reinitializing...")
            self._initialize_connection_pool()
    
    def get_connection(self):
        """Get a connection from the pool"""
        self.ensure_connection_pool()
        return self._connection_pool.getconn()
    
    def release_connection(self, connection):
        """Return a connection to the pool"""
        self.ensure_connection_pool()
        self._connection_pool.putconn(connection)
    
    def close_all_connections(self):
        """Close all connections in the pool"""
        if self._connection_pool:
            self._connection_pool.closeall()
            self._connection_pool = None
            logging.info("All database connections closed")
    
    def execute_query(self, query, params=None, fetchone=False, fetchall=False):
        """Execute a query and return the result"""
        self.ensure_connection_pool()
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            
            result = None
            if fetchone:
                result = cursor.fetchone()
            elif fetchall:
                result = cursor.fetchall()
            else:
                # IMPORTANT: Make sure to commit changes for INSERT, UPDATE, DELETE
                connection.commit()
                result = cursor.rowcount
                
            return result
            
        except (Exception, psycopg2.Error) as error:
            if connection:
                connection.rollback()
            logging.error(f"Error executing query: {error}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.release_connection(connection)