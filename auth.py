import streamlit as st
from database import Database
from typing import Optional, Dict, Any
import secrets
import string

class Auth:
    def __init__(self, db: Database):
        self.db = db

    @staticmethod
    def init_session_state():
        """Initialize session state variables"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0

    @staticmethod
    def generate_username(name: str) -> str:
        """Generate username from name"""
        # Remove spaces and special characters, convert to lowercase
        base_username = ''.join(c.lower() for c in name if c.isalnum())
        # Add random digits
        random_digits = ''.join(secrets.choice(string.digits) for _ in range(3))
        return f"{base_username}{random_digits}"

    @staticmethod
    def generate_password(length: int = 12) -> str:
        """Generate a random secure password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password

    def login(self, username: str, password: str) -> bool:
        """Authenticate user and set session state"""
        # Rate limiting
        if st.session_state.login_attempts >= 5:
            st.error("Too many failed login attempts. Please try again later.")
            return False

        user = self.db.authenticate_user(username, password)

        if user:
            st.session_state.authenticated = True
            st.session_state.user = user
            st.session_state.login_attempts = 0
            return True
        else:
            st.session_state.login_attempts += 1
            return False

    def logout(self):
        """Clear session state and logout"""
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.login_attempts = 0

    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)

    @staticmethod
    def is_admin() -> bool:
        """Check if current user is admin"""
        user = st.session_state.get('user')
        return user and user.get('role') == 'Admin'

    @staticmethod
    def get_current_user() -> Optional[Dict[str, Any]]:
        """Get current logged in user"""
        return st.session_state.get('user')

    @staticmethod
    def require_auth(func):
        """Decorator to require authentication"""
        def wrapper(*args, **kwargs):
            if not Auth.is_authenticated():
                st.warning("Please login to access this page")
                st.stop()
            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def require_admin(func):
        """Decorator to require admin role"""
        def wrapper(*args, **kwargs):
            if not Auth.is_admin():
                st.error("Access denied. Admin privileges required.")
                st.stop()
            return func(*args, **kwargs)
        return wrapper