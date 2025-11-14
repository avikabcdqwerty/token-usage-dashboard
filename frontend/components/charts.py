import streamlit as st
import plotly.graph_objs as go
from typing import List, Dict, Any, Tuple
import logging

# Configure logger for chart events
logger = logging.getLogger("token_usage_dashboard.charts")

def render_token_usage_chart(
    usage_data: List[Dict[str, Any]],
    timeframe: str,
    date_range: Tuple[Any, Any],
    breakdowns: Dict[str, Any],
) -> None:
    """
    Render an interactive, accessible token usage chart using Plotly.
    Args:
        usage_data (List[Dict[str, Any]]): List of token usage records (aggregated per period).
        timeframe (str): Selected timeframe ('daily', 'weekly', 'monthly').
        date_range (Tuple[Any, Any]): (start_date, end_date) for the chart.
        breakdowns (Dict[str, Any]): Detailed breakdowns per activity for tooltips.
    """
    try:
        # Prepare chart data
        periods = [record["period"] for record in usage_data]
        total_tokens = [record["total_tokens"] for record in usage_data]

        # Accessibility: ARIA label for chart
        st.markdown(
            f"""
            <div aria-label="Token usage chart for period {date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}" tabindex="0"></div>
            """,
            unsafe_allow_html=True,
        )

        # Build Plotly figure
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=periods,
                y=total_tokens,
                name="Total Tokens",
                marker_color="#3498db",
                hoverinfo="x+y",
                customdata=[
                    breakdowns.get(record["period"], {})
                    for record in usage_data
                ],
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Total Tokens: %{y}<br>"
                    "%{customdata}"
                ),
            )
        )

        # Add breakdowns to hovertemplate
        def format_breakdown(breakdown: Dict[str, Any]) -> str:
            if not breakdown:
                return "No breakdown available"
            return "<br>".join(
                [
                    f"{activity}: {tokens} tokens"
                    for activity, tokens in breakdown.items()
                ]
            )

        # Update hover text for accessibility and detail
        fig.update_traces(
            hovertemplate=[
                (
                    f"<b>{period}</b><br>"
                    f"Total Tokens: {tokens}<br>"
                    f"{format_breakdown(breakdowns.get(period, {}))}"
                )
                for period, tokens in zip(periods, total_tokens)
            ]
        )

        # Chart layout for accessibility and responsiveness
        fig.update_layout(
            title=f"Token Usage ({timeframe.capitalize()})",
            xaxis_title="Period",
            yaxis_title="Tokens Used",
            bargap=0.2,
            template="plotly_white",
            autosize=True,
            margin=dict(l=40, r=40, t=60, b=40),
            font=dict(size=16),
        )

        # Responsive rendering: ensure chart loads quickly
        st.plotly_chart(fig, use_container_width=True, config={
            "displayModeBar": True,
            "displaylogo": False,
            "responsive": True,
            "staticPlot": False,
            "scrollZoom": True,
            "toImageButtonOptions": {
                "format": "png",
                "filename": "token_usage_chart",
                "height": 600,
                "width": 1000,
                "scale": 2,
            },
        })

        # Detailed breakdown table (optional, for accessibility)
        with st.expander("Show detailed breakdowns per activity", expanded=False):
            for period in periods:
                breakdown = breakdowns.get(period, {})
                if breakdown:
                    st.markdown(f"**{period}**")
                    st.table(
                        [
                            {"Activity": activity, "Tokens": tokens}
                            for activity, tokens in breakdown.items()
                        ]
                    )
                else:
                    st.markdown(f"**{period}**: No breakdown available.")

    except Exception as e:
        logger.error(f"Error rendering token usage chart: {e}")
        st.error("Unable to render token usage chart. Please try again later.")

# Exports
__all__ = ["render_token_usage_chart"]