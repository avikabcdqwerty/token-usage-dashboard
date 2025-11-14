import streamlit as st
import logging
from typing import Optional, Dict, Any, List

from streamlit_authenticator import Authenticate

# Configure logger for authentication events
logger = logging.getLogger("token_usage_dashboard.auth")

# Example user config (should be loaded securely in production)
USERS = {
    "usernames": {
        "alice": {
            "email": "alice@example.com",
            "name": "Alice",
            "password": "pbkdf2:sha256:260000$abc$...",  # hashed password
            "roles": ["user"],
        },
        "bob": {
            "email": "bob@example.com",
            "name": "Bob",
            "password": "pbkdf2:sha256:260000$xyz$...",  # hashed password
            "roles": ["admin"],
        },
    }
}

COOKIE_NAME = "token_usage_dashboard_auth"
COOKIE_KEY = "supersecretkey"  # Should be securely stored in env/config
COOKIE_EXPIRY_DAYS = 1

# Initialize Streamlit Authenticator
authenticator = Authenticate(
    USERS,
    COOKIE_NAME,
    COOKIE_KEY,
    COOKIE_EXPIRY_DAYS,
    cookie_expiry_days=COOKIE_EXPIRY_DAYS,
)

def authenticate_user() -> Dict[str, Any]:
    """
    Render login form and authenticate user.
    Returns:
        dict: {
            "authenticated": bool,
            "username": str,
            "token": str,
            "error": Optional[str]
        }
    """
    try:
        name, authentication_status, username = authenticator.login("Login", "main")
        if authentication_status:
            logger.info(f"User '{username}' authenticated successfully.")
            token = authenticator.get_cookie()
            st.session_state["user"] = {
                "username": username,
                "name": USERS["usernames"][username]["name"],
                "email": USERS["usernames"][username]["email"],
                "roles": USERS["usernames"][username]["roles"],
                "token": token,
            }
            return {
                "authenticated": True,
                "username": username,
                "token": token,
                "error": None,
            }
        elif authentication_status is False:
            logger.warning(f"Failed login attempt for user '{username}'.")
            return {
                "authenticated": False,
                "username": username,
                "token": None,
                "error": "Invalid username or password.",
            }
        else:
            return {
                "authenticated": False,
                "username": None,
                "token": None,
                "error": None,
            }
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return {
            "authenticated": False,
            "username": None,
            "token": None,
            "error": "Authentication system error.",
        }

def get_user_info() -> Optional[Dict[str, Any]]:
    """
    Retrieve authenticated user info from session state.
    Returns:
        dict or None
    """
    user = st.session_state.get("user")
    if user and user.get("token"):
        return user
    return None

def is_authenticated(user: Optional[Dict[str, Any]]) -> bool:
    """
    Check if user is authenticated.
    Args:
        user (dict or None)
    Returns:
        bool
    """
    return bool(user and user.get("token"))

def logout_user() -> None:
    """
    Log out the current user and clear session state.
    """
    try:
        authenticator.logout("Logout", "sidebar")
        if "user" in st.session_state:
            del st.session_state["user"]
        logger.info("User logged out.")
    except Exception as e:
        logger.error(f"Logout error: {e}")

def get_user_roles(user: Optional[Dict[str, Any]]) -> List[str]:
    """
    Get roles for the authenticated user.
    Args:
        user (dict or None)
    Returns:
        list of roles
    """
    if user and "roles" in user:
        return user["roles"]
    return []

# Exports
__all__ = [
    "authenticate_user",
    "get_user_info",
    "is_authenticated",
    "logout_user",
    "get_user_roles",
]