import streamlit as st
from typing import Dict, Any
import logging
from datetime import datetime, timedelta

from frontend.components.date_picker import render_date_picker
from frontend.components.charts import render_token_usage_chart
from frontend.api.api_client import TokenUsageApiClient

# Configure logger for dashboard events
logger = logging.getLogger("token_usage_dashboard.dashboard")

def render_dashboard(api_client: TokenUsageApiClient, user: Dict[str, Any]) -> None:
    """
    Render the main dashboard UI for token usage analytics.
    Includes timeframe/date filters, chart, and detailed breakdowns.
    Args:
        api_client (TokenUsageApiClient): Authenticated API client for data fetching.
        user (Dict[str, Any]): Authenticated user info.
    """
    st.title("Your Token Usage Analytics")
    st.markdown(
        """
        <section aria-label="Token usage dashboard" tabindex="0">
            <p>
                Visualize and analyze your token consumption over time. Use the filters below to select a timeframe or custom date range.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar: Filters for timeframe and date range
    with st.sidebar:
        st.header("Filters")
        timeframe, date_range = render_date_picker()

    # Fetch and display token usage data
    try:
        # Show a spinner while loading data
        with st.spinner("Loading token usage data..."):
            # API call: fetch token usage for selected period
            usage_data = api_client.get_token_usage(
                start_date=date_range[0],
                end_date=date_range[1],
                timeframe=timeframe,
            )
    except Exception as e:
        logger.error(f"Failed to fetch token usage data: {e}")
        st.error("An error occurred while loading your token usage data. Please try again later.")
        return

    # Handle empty data
    if not usage_data or not usage_data.get("data"):
        st.info(
            f"No token usage data available for the selected period ({date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}).",
            icon="ℹ️",
        )
        return

    # Render the interactive chart
    try:
        render_token_usage_chart(
            usage_data=usage_data["data"],
            timeframe=timeframe,
            date_range=date_range,
            breakdowns=usage_data.get("breakdowns", {}),
        )
    except Exception as e:
        logger.error(f"Failed to render token usage chart: {e}")
        st.error("An error occurred while rendering the chart. Please contact support.")

    # Accessibility: ARIA live region for updates
    st.markdown(
        """
        <div aria-live="polite" style="position: absolute; left: -9999px; top: auto; width: 1px; height: 1px; overflow: hidden;">
            Dashboard updated for selected period.
        </div>
        """,
        unsafe_allow_html=True,
    )

# Exports
__all__ = ["render_dashboard"]