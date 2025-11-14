import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

import streamlit as st

from frontend.components.dashboard import render_dashboard
from frontend.components.charts import render_token_usage_chart
from frontend.components.date_picker import render_date_picker

# --- Fixtures and Mocks ---

@pytest.fixture
def mock_api_client():
    """Mock API client with get_token_usage method."""
    client = MagicMock()
    now = datetime.now()
    client.get_token_usage.return_value = {
        "data": [
            {"period": (now - timedelta(days=2)).strftime("%Y-%m-%d"), "total_tokens": 100},
            {"period": (now - timedelta(days=1)).strftime("%Y-%m-%d"), "total_tokens": 200},
            {"period": now.strftime("%Y-%m-%d"), "total_tokens": 150},
        ],
        "breakdowns": {
            (now - timedelta(days=2)).strftime("%Y-%m-%d"): {"chat": 100},
            (now - timedelta(days=1)).strftime("%Y-%m-%d"): {"api": 200},
            now.strftime("%Y-%m-%d"): {"chat": 150},
        },
    }
    return client

@pytest.fixture
def mock_user():
    return {
        "username": "alice",
        "name": "Alice",
        "email": "alice@example.com",
        "roles": ["user"],
        "token": "dummy-jwt-token",
    }

# --- Dashboard Rendering Tests ---

def test_dashboard_renders_with_data(mock_api_client, mock_user):
    """Test dashboard renders chart when data is available."""
    with patch("frontend.components.dashboard.render_token_usage_chart") as mock_chart:
        render_dashboard(api_client=mock_api_client, user=mock_user)
        mock_chart.assert_called_once()
        # Check that the chart is rendered with correct data
        args, kwargs = mock_chart.call_args
        assert "usage_data" in kwargs
        assert len(kwargs["usage_data"]) == 3

def test_dashboard_renders_no_data_message(mock_user):
    """Test dashboard shows 'no data available' message when API returns empty data."""
    empty_api_client = MagicMock()
    empty_api_client.get_token_usage.return_value = {"data": [], "breakdowns": {}}
    with patch("streamlit.info") as mock_info:
        render_dashboard(api_client=empty_api_client, user=mock_user)
        mock_info.assert_called()
        assert "No token usage data available" in str(mock_info.call_args)

def test_dashboard_handles_api_error(mock_user):
    """Test dashboard displays error message on API error."""
    error_api_client = MagicMock()
    error_api_client.get_token_usage.side_effect = Exception("API failure")
    with patch("streamlit.error") as mock_error:
        render_dashboard(api_client=error_api_client, user=mock_user)
        mock_error.assert_called()
        assert "An error occurred while loading your token usage data" in str(mock_error.call_args)

def test_chart_accessibility_and_breakdown():
    """Test chart renders with accessible ARIA label and breakdown expander."""
    usage_data = [
        {"period": "2024-06-01", "total_tokens": 100},
        {"period": "2024-06-02", "total_tokens": 200},
    ]
    breakdowns = {
        "2024-06-01": {"chat": 100},
        "2024-06-02": {"api": 200},
    }
    with patch("streamlit.plotly_chart") as mock_plotly, \
         patch("streamlit.expander") as mock_expander, \
         patch("streamlit.markdown") as mock_markdown:
        render_token_usage_chart(
            usage_data=usage_data,
            timeframe="daily",
            date_range=(datetime(2024, 6, 1), datetime(2024, 6, 2)),
            breakdowns=breakdowns,
        )
        mock_plotly.assert_called_once()
        mock_markdown.assert_any_call(
            pytest.helpers.contains("aria-label"), unsafe_allow_html=True
        )

def test_date_picker_default_and_custom(monkeypatch):
    """Test date picker returns correct defaults and custom range."""
    # Patch st.radio and st.date_input to simulate user input
    monkeypatch.setattr(st, "radio", lambda *a, **k: "daily")
    # Should return default daily range
    timeframe, date_range = render_date_picker()
    assert timeframe == "daily"
    assert isinstance(date_range, tuple)
    # Now test custom
    monkeypatch.setattr(st, "radio", lambda *a, **k: "custom")
    today = datetime.today()
    monkeypatch.setattr(st, "date_input", lambda *a, **k: today.date())
    timeframe, date_range = render_date_picker()
    assert timeframe == "custom"
    assert date_range[0].date() == today.date()
    assert date_range[1].date() == today.date()