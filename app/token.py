"""Local synthetic token generator for testing; never publishes secrets."""
from datetime import datetime, timedelta, timezone
import jwt

def make_token(user_id: str, tenant_id: str, secret: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": user_id, "tenant_id": tenant_id, "iss": "tenantproof-demo", "aud": "tenantproof-demo", "iat": now, "exp": now + timedelta(minutes=15)}, secret, algorithm="HS256")
