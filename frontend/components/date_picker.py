import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple

import logging

logger = logging.getLogger("token_usage_dashboard.date_picker")

def get_default_date_range(timeframe: str) -> Tuple[datetime, datetime]:
    """
    Returns default start and end dates for the given timeframe.
    """
    today = datetime.today()
    if timeframe == "daily":
        start = today - timedelta(days=6)
    elif timeframe == "weekly":
        start = today - timedelta(weeks=11)
    elif timeframe == "monthly":
        start = today.replace(day=1) - timedelta(days=365)
    else:
        start = today - timedelta(days=29)
    return (start.replace(hour=0, minute=0, second=0, microsecond=0), today.replace(hour=23, minute=59, second=59, microsecond=999999))

def render_date_picker() -> Tuple[str, Tuple[datetime, datetime]]:
    """
    Renders timeframe and date range pickers for dashboard filtering.
    Returns:
        timeframe (str): Selected timeframe ('daily', 'weekly', 'monthly', 'custom')
        date_range (Tuple[datetime, datetime]): (start_date, end_date)
    """
    try:
        timeframe = st.radio(
            "Select timeframe",
            options=["daily", "weekly", "monthly", "custom"],
            index=0,
            horizontal=True,
            help="Choose how to aggregate your token usage data.",
        )

        if "date_picker_state" not in st.session_state:
            st.session_state["date_picker_state"] = {}

        # Set default date range based on timeframe
        if timeframe != "custom":
            start_date, end_date = get_default_date_range(timeframe)
            st.session_state["date_picker_state"]["start_date"] = start_date
            st.session_state["date_picker_state"]["end_date"] = end_date
        else:
            # For custom, allow user to pick start and end dates
            min_date = datetime.today() - timedelta(days=365 * 2)
            max_date = datetime.today()
            start_date = st.date_input(
                "Start date",
                value=st.session_state["date_picker_state"].get("start_date", max_date - timedelta(days=29)),
                min_value=min_date,
                max_value=max_date,
                key="custom_start_date",
                help="Select the start date for your custom range.",
            )
            end_date = st.date_input(
                "End date",
                value=st.session_state["date_picker_state"].get("end_date", max_date),
                min_value=start_date,
                max_value=max_date,
                key="custom_end_date",
                help="Select the end date for your custom range.",
            )
            # Convert to datetime for consistency
            start_date = datetime.combine(start_date, datetime.min.time())
            end_date = datetime.combine(end_date, datetime.max.time())
            st.session_state["date_picker_state"]["start_date"] = start_date
            st.session_state["date_picker_state"]["end_date"] = end_date

        # Accessibility: ARIA live region for filter changes
        st.markdown(
            """
            <div aria-live="polite" style="position: absolute; left: -9999px; top: auto; width: 1px; height: 1px; overflow: hidden;">
                Filters updated: {timeframe}, {start} to {end}
            </div>
            """.format(
                timeframe=timeframe.capitalize(),
                start=st.session_state["date_picker_state"]["start_date"].strftime("%Y-%m-%d"),
                end=st.session_state["date_picker_state"]["end_date"].strftime("%Y-%m-%d"),
            ),
            unsafe_allow_html=True,
        )

        return (
            timeframe,
            (
                st.session_state["date_picker_state"]["start_date"],
                st.session_state["date_picker_state"]["end_date"],
            ),
        )
    except Exception as e:
        logger.error(f"Error rendering date picker: {e}")
        st.error("Unable to render date picker. Please try again later.")
        # Fallback to safe defaults
        fallback_timeframe = "daily"
        fallback_range = get_default_date_range(fallback_timeframe)
        return fallback_timeframe, fallback_range

# Exports
__all__ = ["render_date_picker"]