from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from typing import List, Optional
import logging

# Configure logger for model events
logger = logging.getLogger("token_usage_dashboard.models")

Base = declarative_base()

class TokenUsage(Base):
    """
    ORM model for the token_usage table.
    Represents a single token usage event.
    """
    __tablename__ = "token_usage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    usage_time = Column(DateTime, nullable=False, index=True)
    tokens_used = Column(Integer, nullable=False)
    activity = Column(String, nullable=False)

    def __repr__(self):
        return (
            f"<TokenUsage(id={self.id}, user_id={self.user_id}, "
            f"usage_time={self.usage_time}, tokens_used={self.tokens_used}, "
            f"activity={self.activity})>"
        )

class User:
    """
    Lightweight user object for RBAC and authentication context.
    Not persisted in the database.
    """
    def __init__(self, id: str, username: str, roles: Optional[List[str]] = None):
        self.id = id
        self.username = username
        self.roles = roles or []

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, roles={self.roles})>"

# Exports
__all__ = ["Base", "TokenUsage", "User"]