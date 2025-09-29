"""
Unit tests for authentication module
"""
import pytest
from auth import Auth
import streamlit as st

class TestAuthHelpers:
    """Test authentication helper functions"""

    def test_generate_username(self):
        """Test username generation"""
        username = Auth.generate_username("John Doe")
        assert "johndoe" in username.lower()
        assert len(username) > 7  # Should include digits
        assert username[-3:].isdigit()  # Last 3 chars are digits

    def test_generate_username_special_chars(self):
        """Test username generation with special characters"""
        username = Auth.generate_username("María José-Smith")
        assert username.isalnum()  # Only alphanumeric

    def test_generate_password(self):
        """Test password generation"""
        password = Auth.generate_password(12)
        assert len(password) == 12
        assert any(c.isalpha() for c in password)
        assert any(c.isdigit() for c in password)

    def test_generate_password_custom_length(self):
        """Test password generation with custom length"""
        password = Auth.generate_password(20)
        assert len(password) == 20


class TestAuthenticationFlow:
    """Test authentication workflows"""

    def test_login_success(self, auth_instance, db_with_users):
        """Test successful login"""
        # Initialize session state
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False

        result = auth_instance.login("testcore", "password123")
        assert result is True
        assert st.session_state.authenticated is True
        assert st.session_state.user is not None
        assert st.session_state.login_attempts == 0

    def test_login_invalid_password(self, auth_instance, db_with_users):
        """Test login with invalid password"""
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0

        result = auth_instance.login("testcore", "wrongpassword")
        assert result is False
        assert st.session_state.get('authenticated', False) is False

    def test_login_nonexistent_user(self, auth_instance, db_with_users):
        """Test login with nonexistent user"""
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0

        result = auth_instance.login("nonexistent", "password123")
        assert result is False

    def test_login_rate_limiting(self, auth_instance, db_with_users):
        """Test rate limiting after multiple failed attempts"""
        st.session_state.login_attempts = 5

        result = auth_instance.login("testcore", "password123")
        assert result is False  # Should be blocked due to rate limit

    def test_logout(self, auth_instance, db_with_users):
        """Test logout functionality"""
        # Login first
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0

        auth_instance.login("testcore", "password123")
        assert st.session_state.authenticated is True

        # Logout
        auth_instance.logout()
        assert st.session_state.authenticated is False
        assert st.session_state.user is None
        assert st.session_state.login_attempts == 0

    def test_is_authenticated(self, auth_instance):
        """Test authentication check"""
        st.session_state.authenticated = False
        assert Auth.is_authenticated() is False

        st.session_state.authenticated = True
        assert Auth.is_authenticated() is True

    def test_is_admin(self, auth_instance, temp_db):
        """Test admin role check"""
        # Login as admin
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0

        auth_instance.login("admin123", "admin123456")
        assert Auth.is_admin() is True

    def test_is_admin_non_admin_user(self, auth_instance, db_with_users):
        """Test admin check for non-admin user"""
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0

        auth_instance.login("testcore", "password123")
        assert Auth.is_admin() is False

    def test_get_current_user(self, auth_instance, db_with_users):
        """Test getting current user"""
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0

        auth_instance.login("testcore", "password123")
        user = Auth.get_current_user()
        assert user is not None
        assert user["username"] == "testcore"

    def test_get_current_user_not_logged_in(self):
        """Test getting current user when not logged in"""
        st.session_state.user = None
        user = Auth.get_current_user()
        assert user is None


class TestSessionManagement:
    """Test session state management"""

    def test_init_session_state(self):
        """Test session state initialization"""
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        Auth.init_session_state()

        assert 'authenticated' in st.session_state
        assert 'user' in st.session_state
        assert 'login_attempts' in st.session_state
        assert st.session_state.authenticated is False
        assert st.session_state.user is None
        assert st.session_state.login_attempts == 0

    def test_session_state_persistence(self, auth_instance, db_with_users):
        """Test that session state persists across function calls"""
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0

        auth_instance.login("testcore", "password123")

        # Simulate another function call
        assert Auth.is_authenticated() is True
        user = Auth.get_current_user()
        assert user["username"] == "testcore"