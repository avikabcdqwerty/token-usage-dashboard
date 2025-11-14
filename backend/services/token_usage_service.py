from datetime import datetime
from typing import List, Dict, Any, Tuple
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.models.models import TokenUsage

# Configure logger for service events
logger = logging.getLogger("token_usage_dashboard.token_usage_service")

# Database connection (should be configured via environment variables in production)
DATABASE_URL = "postgresql+psycopg2://dashboard_user:dashboard_pass@db:5432/token_dashboard"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_token_usage_aggregated(
    user_id: str,
    start_date: datetime,
    end_date: datetime,
    timeframe: str,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Query and aggregate token usage data for a user over a date range and timeframe.
    Args:
        user_id (str): The user's unique identifier.
        start_date (datetime): Start of the date range.
        end_date (datetime): End of the date range.
        timeframe (str): Aggregation period ('daily', 'weekly', 'monthly').
    Returns:
        Tuple[List[Dict], Dict]: (usage_data, breakdowns)
            usage_data: [{period, total_tokens}]
            breakdowns: {period: {activity: tokens, ...}, ...}
    """
    session = SessionLocal()
    try:
        # Determine SQL date_trunc granularity
        if timeframe == "daily":
            trunc_unit = "day"
        elif timeframe == "weekly":
            trunc_unit = "week"
        elif timeframe == "monthly":
            trunc_unit = "month"
        else:
            trunc_unit = "day"

        # Main aggregation query: total tokens per period
        usage_query = text(f"""
            SELECT
                date_trunc(:trunc_unit, usage_time) AS period,
                SUM(tokens_used) AS total_tokens
            FROM token_usage
            WHERE user_id = :user_id
              AND usage_time >= :start_date
              AND usage_time <= :end_date
            GROUP BY period
            ORDER BY period ASC
        """)

        usage_result = session.execute(
            usage_query,
            {
                "trunc_unit": trunc_unit,
                "user_id": user_id,
                "start_date": start_date,
                "end_date": end_date,
            },
        ).fetchall()

        usage_data = [
            {
                "period": row["period"].strftime("%Y-%m-%d"),
                "total_tokens": int(row["total_tokens"]),
            }
            for row in usage_result
        ]

        # Detailed breakdowns per activity per period
        breakdown_query = text(f"""
            SELECT
                date_trunc(:trunc_unit, usage_time) AS period,
                activity,
                SUM(tokens_used) AS tokens
            FROM token_usage
            WHERE user_id = :user_id
              AND usage_time >= :start_date
              AND usage_time <= :end_date
            GROUP BY period, activity
            ORDER BY period ASC, activity ASC
        """)

        breakdown_result = session.execute(
            breakdown_query,
            {
                "trunc_unit": trunc_unit,
                "user_id": user_id,
                "start_date": start_date,
                "end_date": end_date,
            },
        ).fetchall()

        breakdowns: Dict[str, Dict[str, int]] = {}
        for row in breakdown_result:
            period = row["period"].strftime("%Y-%m-%d")
            activity = row["activity"]
            tokens = int(row["tokens"])
            if period not in breakdowns:
                breakdowns[period] = {}
            breakdowns[period][activity] = tokens

        logger.info(
            f"Aggregated token usage for user {user_id}: {len(usage_data)} periods, timeframe={timeframe}"
        )
        return usage_data, breakdowns

    except Exception as e:
        logger.error(f"Error aggregating token usage: {e}")
        raise
    finally:
        session.close()

# Exports
__all__ = ["get_token_usage_aggregated"]