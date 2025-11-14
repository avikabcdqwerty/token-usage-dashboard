import httpx
from typing import Tuple, Dict, Any
import logging
from datetime import datetime

# Configure logger for API client events
logger = logging.getLogger("token_usage_dashboard.api_client")

class TokenUsageApiClient:
    """
    API client for securely fetching token usage data for the authenticated user.
    All requests are sent over TLS and include JWT for RBAC.
    """

    def __init__(self, token: str, base_url: str = "https://api.token-dashboard.local"):
        """
        Args:
            token (str): JWT token for authentication.
            base_url (str): Base URL of the FastAPI backend.
        """
        self.token = token
        self.base_url = base_url.rstrip("/")

    def get_token_usage(
        self,
        start_date: datetime,
        end_date: datetime,
        timeframe: str,
    ) -> Dict[str, Any]:
        """
        Fetch token usage data for the authenticated user.
        Args:
            start_date (datetime): Start of the date range.
            end_date (datetime): End of the date range.
            timeframe (str): Aggregation period ('daily', 'weekly', 'monthly').
        Returns:
            Dict[str, Any]: Usage data and breakdowns.
        Raises:
            Exception: On network or API error.
        """
        url = f"{self.base_url}/api/token-usage"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "timeframe": timeframe,
        }

        try:
            with httpx.Client(http2=True, timeout=10.0, verify=True) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                logger.info(
                    f"Fetched token usage data: {params} | status={response.status_code}"
                )
                return data
        except httpx.HTTPStatusError as e:
            logger.error(
                f"API error fetching token usage: {e.response.status_code} {e.response.text}"
            )
            raise Exception(
                f"API error: {e.response.status_code} {e.response.text}"
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Network error fetching token usage: {e}")
            raise Exception("Network error fetching token usage data.") from e
        except Exception as e:
            logger.error(f"Unexpected error fetching token usage: {e}")
            raise

# Exports
__all__ = ["TokenUsageApiClient"]