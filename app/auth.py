"""
Authentication helpers for the application.
"""

import os
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class User(UserMixin):
    """Simple User class for Flask-Login authentication."""
    
    def __init__(self, user_id):
        self.id = user_id
    
    @staticmethod
    def get(user_id):
        """Get user by ID. Returns User object if valid, None otherwise."""
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        if user_id == admin_username:
            return User(user_id)
        return None
    
    @staticmethod
    def verify_password(username, password):
        """
        Verify username and password against environment variables.
        
        Args:
            username: Username to verify
            password: Plain text password to verify
            
        Returns:
            True if credentials are valid, False otherwise
        """
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_password = os.getenv('ADMIN_PASSWORD', '')
        
        if not admin_password:
            # If no password is set, authentication is disabled
            return False
        
        if username != admin_username:
            return False
        
        # For simplicity, we'll compare plain text passwords
        # In production, you might want to hash the password in env var
        # and use check_password_hash here
        return password == admin_password
