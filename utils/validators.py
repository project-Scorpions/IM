import re
from datetime import datetime

class Validators:
    """Utility class for validating input data"""
    
    @staticmethod
    def validate_email(email):
        """
        Validate email format
        
        Parameters:
        - email: Email string to validate
        
        Returns:
        - bool: True if valid, False otherwise
        """
        if not email:  # Empty email is considered valid (optional field)
            return True
            
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone):
        """
        Validate phone number format
        
        Parameters:
        - phone: Phone string to validate
        
        Returns:
        - bool: True if valid, False otherwise
        """
        if not phone:  # Empty phone is considered valid (optional field)
            return True
            
        # Remove common separators
        clean_phone = re.sub(r'[\s\-\(\)\.]', '', phone)
        
        # Check if it's a valid phone number (at least 7 digits)
        return bool(re.match(r'^\+?[0-9]{7,15}$', clean_phone))
    
    @staticmethod
    def validate_username(username):
        """
        Validate username format
        
        Parameters:
        - username: Username string to validate
        
        Returns:
        - bool: True if valid, False otherwise
        """
        if not username:
            return False
            
        # Username should be 3-20 characters, alphanumeric and underscore
        return bool(re.match(r'^[a-zA-Z0-9_]{3,20}$', username))
    
    @staticmethod
    def validate_password_strength(password):
        """
        Validate password strength
        
        Parameters:
        - password: Password string to validate
        
        Returns:
        - tuple: (bool: is_valid, str: message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one digit"
        
        return True, "Password is strong"
    
    @staticmethod
    def validate_date_format(date_str, format="%Y-%m-%d"):
        """
        Validate date string format
        
        Parameters:
        - date_str: Date string to validate
        - format: Expected date format
        
        Returns:
        - bool: True if valid, False otherwise
        """
        try:
            datetime.strptime(date_str, format)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_price(price_str):
        """
        Validate price format
        
        Parameters:
        - price_str: Price string to validate
        
        Returns:
        - bool: True if valid, False otherwise
        """
        try:
            # Remove currency symbol if present
            clean_price = price_str.replace('$', '').replace('€', '').replace('£', '').strip()
            
            # Parse as float
            price = float(clean_price)
            
            # Check if price is positive
            return price >= 0
        except ValueError:
            return False
    
    @staticmethod
    def validate_integer(int_str):
        """
        Validate integer format
        
        Parameters:
        - int_str: Integer string to validate
        
        Returns:
        - bool: True if valid, False otherwise
        """
        try:
            int(int_str)
            return True
        except ValueError:
            return False