import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from backend.main import app
from backend.services.token_usage_service import get_token_usage_aggregated
from backend.models.models import TokenUsage, Base, User

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database setup (use a separate test DB or in-memory for isolation)
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Patch the service to use the test DB
import backend.services.token_usage_service as service_module
service_module.engine = engine
service_module.SessionLocal = TestingSessionLocal

# Create tables
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Yield a SQLAlchemy session for test isolation."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def test_user():
    """Return a mock user object."""
    return User(id="testuser", username="testuser", roles=["user"])

@pytest.fixture(scope="function")
def populate_token_usage(db_session):
    """Populate the test DB with sample token usage data."""
    now = datetime.utcnow()
    records = [
        TokenUsage(
            user_id="testuser",
            usage_time=now - timedelta(days=2),
            tokens_used=100,
            activity="chat"
        ),
        TokenUsage(
            user_id="testuser",
            usage_time=now - timedelta(days=1),
            tokens_used=200,
            activity="api"
        ),
        TokenUsage(
            user_id="testuser",
            usage_time=now,
            tokens_used=150,
            activity="chat"
        ),
        TokenUsage(
            user_id="otheruser",
            usage_time=now,
            tokens_used=999,
            activity="api"
        ),
    ]
    db_session.add_all(records)
    db_session.commit()

def test_get_token_usage_aggregated_daily(db_session, test_user, populate_token_usage):
    """Test aggregation of token usage by day for a user."""
    now = datetime.utcnow()
    start_date = now - timedelta(days=3)
    end_date = now
    usage_data, breakdowns = get_token_usage_aggregated(
        user_id=test_user.id,
        start_date=start_date,
        end_date=end_date,
        timeframe="daily",
    )
    # Should only include testuser's data
    assert len(usage_data) >= 1
    for entry in usage_data:
        assert "period" in entry
        assert "total_tokens" in entry
    # Breakdown keys should match periods
    for period, activities in breakdowns.items():
        assert isinstance(activities, dict)
        for activity, tokens in activities.items():
            assert isinstance(tokens, int)

def test_get_token_usage_aggregated_rbac(db_session, populate_token_usage):
    """Ensure no data is returned for other users."""
    now = datetime.utcnow()
    start_date = now - timedelta(days=3)
    end_date = now
    usage_data, breakdowns = get_token_usage_aggregated(
        user_id="nonexistentuser",
        start_date=start_date,
        end_date=end_date,
        timeframe="daily",
    )
    assert usage_data == []
    assert breakdowns == {}

def get_jwt_token_for_user(user_id="testuser", username="testuser", roles=["user"]):
    """Return a dummy JWT for test purposes (bypassing real signing)."""
    # In real tests, use a JWT library and the same secret as the backend
    import jwt
    payload = {
        "sub": user_id,
        "username": username,
        "roles": roles,
    }
    return jwt.encode(payload, "supersecretkey", algorithm="HS256")

def test_api_token_usage_endpoint(monkeypatch, db_session, populate_token_usage):
    """Integration test for the /api/token-usage endpoint."""
    client = TestClient(app)
    token = get_jwt_token_for_user()
    now = datetime.utcnow()
    start_date = (now - timedelta(days=3)).strftime("%Y-%m-%d")
    end_date = now.strftime("%Y-%m-%d")

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(
        "/api/token-usage",
        params={
            "start_date": start_date,
            "end_date": end_date,
            "timeframe": "daily",
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "breakdowns" in data
    # Ensure only testuser's data is returned
    for entry in data["data"]:
        assert isinstance(entry["total_tokens"], int)

def test_api_token_usage_endpoint_rbac(monkeypatch, db_session, populate_token_usage):
    """Ensure RBAC prevents access for users without required roles."""
    client = TestClient(app)
    # User with no valid roles
    token = get_jwt_token_for_user(roles=["guest"])
    now = datetime.utcnow()
    start_date = (now - timedelta(days=3)).strftime("%Y-%m-%d")
    end_date = now.strftime("%Y-%m-%d")

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(
        "/api/token-usage",
        params={
            "start_date": start_date,
            "end_date": end_date,
            "timeframe": "daily",
        },
        headers=headers,
    )
    assert response.status_code == 403

def test_api_token_usage_endpoint_unauthenticated(db_session, populate_token_usage):
    """Ensure unauthenticated requests are rejected."""
    client = TestClient(app)
    now = datetime.utcnow()
    start_date = (now - timedelta(days=3)).strftime("%Y-%m-%d")
    end_date = now.strftime("%Y-%m-%d")

    response = client.get(
        "/api/token-usage",
        params={
            "start_date": start_date,
            "end_date": end_date,
            "timeframe": "daily",
        },
    )
    assert response.status_code == 401