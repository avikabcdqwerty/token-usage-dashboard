from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
from typing import Dict, Any
from datetime import datetime
import logging

from backend.services.token_usage_service import get_token_usage_aggregated
from backend.models.models import User

router = APIRouter()
logger = logging.getLogger("token_usage_dashboard.api.token_usage")

def get_current_user(request: Request) -> User:
    """
    Dependency to extract the authenticated user from the request.
    Assumes AuthMiddleware sets request.state.user.
    """
    user = getattr(request.state, "user", None)
    if not user:
        logger.warning("Unauthorized access attempt: no user in request state.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user

@router.get(
    "/token-usage",
    response_model=Dict[str, Any],
    summary="Get token usage for the authenticated user",
    tags=["Token Usage"],
)
async def get_token_usage(
    request: Request,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    timeframe: str = Query("daily", regex="^(daily|weekly|monthly)$", description="Aggregation period"),
    user: User = Depends(get_current_user),
):
    """
    Fetch token usage data for the authenticated user, aggregated by the selected timeframe.
    Only the authenticated user's data is returned (RBAC enforced).
    """
    try:
        # Parse and validate dates
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            logger.warning(f"Invalid date format: start={start_date}, end={end_date}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid date format. Use YYYY-MM-DD.",
            )
        if start_dt > end_dt:
            logger.warning(f"Start date after end date: start={start_date}, end={end_date}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Start date must be before or equal to end date.",
            )

        # RBAC: Only allow access to own data
        user_id = user.id
        logger.info(f"User {user_id} requests token usage: {start_date} to {end_date}, timeframe={timeframe}")

        # Query and aggregate token usage
        usage_data, breakdowns = get_token_usage_aggregated(
            user_id=user_id,
            start_date=start_dt,
            end_date=end_dt,
            timeframe=timeframe,
        )

        return {
            "data": usage_data,
            "breakdowns": breakdowns,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching token usage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch token usage data.",
        )

# Exports
__all__ = ["router"]