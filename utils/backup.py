import os
import subprocess
import datetime
import shutil
import logging
import zipfile
from configparser import ConfigParser

class DatabaseBackup:
    """Utility class for database backup and restore operations"""
    
    def __init__(self, config_file='config.ini'):
        self.config = ConfigParser()
        self.config.read(config_file)
        
        # Get database configuration
        self.db_config = {
            'host': self.config.get('database', 'host', fallback='localhost'),
            'database': self.config.get('database', 'database', fallback='pharmacy_db'),
            'user': self.config.get('database', 'user', fallback='postgres'),
            'password': self.config.get('database', 'password', fallback='your_new_password'),
            'port': self.config.get('database', 'port', fallback='5432')
        }
        
        # Create backups directory if it doesn't exist
        if not os.path.exists('backups'):
            os.makedirs('backups')
    
    def backup_database(self, backup_file=None):
        """
        Backup the database using pg_dump
        
        Parameters:
        - backup_file: Optional backup file path. If not provided, a default name will be used.
        
        Returns:
        - tuple: (bool: success, str: message, str: backup_file_path)
        """
        try:
            # Generate backup filename if not provided
            if not backup_file:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_file = f"backups/pharmacy_db_backup_{timestamp}.sql"
            
            # Set environment variable for password
            os.environ['PGPASSWORD'] = self.db_config['password']
            
            # Build pg_dump command
            command = [
                'pg_dump',
                f"--host={self.db_config['host']}",
                f"--port={self.db_config['port']}",
                f"--username={self.db_config['user']}",
                f"--dbname={self.db_config['database']}",
                '--format=custom',
                f"--file={backup_file}"
            ]
            
            # Execute pg_dump command
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode != 0:
                return False, f"Backup failed: {result.stderr}", None
            
            # Create ZIP file with backup and config
            zip_file = backup_file.replace('.sql', '.zip')
            with zipfile.ZipFile(zip_file, 'w') as zipf:
                zipf.write(backup_file, os.path.basename(backup_file))
                zipf.write('config.ini', 'config.ini')
            
            # Remove the original SQL file
            os.remove(backup_file)
            
            return True, "Database backup completed successfully", zip_file
            
        except Exception as e:
            logging.error(f"Error during database backup: {e}")
            return False, f"Backup failed: {str(e)}", None
        finally:
            # Clear password environment variable
            if 'PGPASSWORD' in os.environ:
                del os.environ['PGPASSWORD']
    
    def restore_database(self, backup_file):
        """
        Restore the database from a backup file
        
        Parameters:
        - backup_file: Path to the backup file
        
        Returns:
        - tuple: (bool: success, str: message)
        """
        try:
            temp_dir = 'temp_restore'
            
            # Create temporary directory
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # Extract backup files if it's a ZIP
            if backup_file.endswith('.zip'):
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    zipf.extractall(temp_dir)
                
                # Find the SQL file
                sql_files = [f for f in os.listdir(temp_dir) if f.endswith('.sql')]
                if not sql_files:
                    return False, "No SQL backup file found in the ZIP archive"
                
                backup_file = os.path.join(temp_dir, sql_files[0])
            
            # Set environment variable for password
            os.environ['PGPASSWORD'] = self.db_config['password']
            
            # Build pg_restore command
            command = [
                'pg_restore',
                f"--host={self.db_config['host']}",
                f"--port={self.db_config['port']}",
                f"--username={self.db_config['user']}",
                f"--dbname={self.db_config['database']}",
                '--clean',
                '--if-exists',
                backup_file
            ]
            
            # Execute pg_restore command
            result = subprocess.run(command, capture_output=True, text=True)
            
            # Clean up temporary directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            if result.returncode != 0:
                return False, f"Restore failed: {result.stderr}"
            
            return True, "Database restore completed successfully"
            
        except Exception as e:
            logging.error(f"Error during database restore: {e}")
            return False, f"Restore failed: {str(e)}"
        finally:
            # Clear password environment variable
            if 'PGPASSWORD' in os.environ:
                del os.environ['PGPASSWORD']
            
            # Clean up temporary directory if it exists
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def list_backups(self):
        """
        List all available database backups
        
        Returns:
        - list: List of backup files with metadata
        """
        backup_dir = 'backups'
        backup_files = []
        
        try:
            if not os.path.exists(backup_dir):
                return []
            
            for file in os.listdir(backup_dir):
                if file.endswith('.zip') or file.endswith('.sql'):
                    file_path = os.path.join(backup_dir, file)
                    file_size = os.path.getsize(file_path)
                    file_date = os.path.getmtime(file_path)
                    
                    backup_files.append({
                        'name': file,
                        'path': file_path,
                        'size': file_size,
                        'date': datetime.datetime.fromtimestamp(file_date)
                    })
            
            # Sort by date (newest first)
            backup_files.sort(key=lambda x: x['date'], reverse=True)
            
            return backup_files
            
        except Exception as e:
            logging.error(f"Error listing backups: {e}")
            return []