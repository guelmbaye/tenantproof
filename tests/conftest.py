import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.fixtures import USER_A, USER_B, TENANT_A, TENANT_B
from app.token import make_token

SECRET = "test-only-not-for-deployment-please-replace-123456"

@pytest.fixture
def client():
    api = create_app(database_url="sqlite://", jwt_secret=SECRET, seed_demo=True)
    with TestClient(api) as c:
        yield c

@pytest.fixture
def token_a():
    return make_token(USER_A, TENANT_A, SECRET)

@pytest.fixture
def token_b():
    return make_token(USER_B, TENANT_B, SECRET)
