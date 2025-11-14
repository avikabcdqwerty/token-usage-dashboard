import streamlit as st
import logging
from typing import Optional, Dict, Any
from streamlit.runtime.scriptrunner import get_script_run_ctx

from frontend.auth.auth import (
    authenticate_user,
    get_user_info,
    is_authenticated,
    logout_user,
    get_user_roles,
)
from frontend.api.api_client import TokenUsageApiClient
from frontend.components.dashboard import render_dashboard

# Configure logging for audit and error tracking
logger = logging.getLogger("token_usage_dashboard")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# Streamlit page config for accessibility and responsiveness
st.set_page_config(
    page_title="Token Usage Dashboard",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
)

def log_access(user: Optional[Dict[str, Any]], event: str) -> None:
    """
    Log dashboard access and data retrieval for audit.
    """
    ctx = get_script_run_ctx()
    session_id = getattr(ctx, "session_id", "unknown")
    user_id = user.get("username") if user else "anonymous"
    logger.info(
        f"ACCESS_LOG | session_id={session_id} | user_id={user_id} | event={event}"
    )

def show_login():
    """
    Render login form and handle authentication.
    """
    st.title("Token Usage Dashboard")
    st.markdown(
        """
        <div role="alert" aria-live="polite">
            <strong>Secure Access:</strong> Please log in to view your token usage.
        </div>
        """,
        unsafe_allow_html=True,
    )
    auth_result = authenticate_user()
    if auth_result["authenticated"]:
        st.success("Authentication successful. Redirecting to dashboard...")
        st.experimental_rerun()
    elif auth_result["error"]:
        st.error(auth_result["error"])

def show_dashboard(user: Dict[str, Any]):
    """
    Render the main dashboard for authenticated users.
    """
    # RBAC: Only allow users with 'user' or 'admin' roles
    roles = get_user_roles(user)
    if not any(role in roles for role in ["user", "admin"]):
        st.error("Access denied: insufficient permissions.")
        log_access(user, "access_denied")
        return

    # Audit log for dashboard access
    log_access(user, "dashboard_access")

    # Initialize API client with user JWT
    api_client = TokenUsageApiClient(token=user["token"])

    # Render dashboard component
    render_dashboard(api_client=api_client, user=user)

def show_header(user: Optional[Dict[str, Any]]):
    """
    Render the header with user info and logout button.
    """
    st.markdown(
        """
        <nav aria-label="Main navigation" style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 1.5em; font-weight: bold;">🔒 Token Usage Dashboard</span>
            </div>
            <div>
                {user_info}
                <form action="" method="post" style="display: inline;">
                    <button type="submit" name="logout" style="background: #e74c3c; color: white; border: none; padding: 0.5em 1em; border-radius: 4px; cursor: pointer;">Logout</button>
                </form>
            </div>
        </nav>
        """.format(
            user_info=f"<span aria-label='Logged in user' style='margin-right: 1em;'>👤 {user['username']}</span>"
            if user
            else ""
        ),
        unsafe_allow_html=True,
    )

def main():
    """
    Main Streamlit app entry point.
    Handles authentication, routing, and context setup.
    """
    # Check authentication state
    user = get_user_info()
    authenticated = is_authenticated(user)

    # Handle logout
    if st.session_state.get("logout", False):
        logout_user()
        st.session_state["logout"] = False
        st.experimental_rerun()

    # Header (always visible for accessibility)
    show_header(user if authenticated else None)

    # Routing: show login or dashboard
    if not authenticated:
        show_login()
    else:
        show_dashboard(user)

if __name__ == "__main__":
    main()