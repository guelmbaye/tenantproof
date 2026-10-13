"""Reference SaaS API. The tenant predicate is an executable security invariant."""
import os
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError, decode, encode
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from app.fixtures import seed
from app.models import Base, Invoice, User

bearer = HTTPBearer(auto_error=False)

def create_app(database_url: str | None = None, jwt_secret: str | None = None, seed_demo: bool | None = None) -> FastAPI:
    url = database_url or os.environ.get("DATABASE_URL", "sqlite:///./tenantproof-local.db")
    secret = jwt_secret or os.environ.get("JWT_SECRET")
    if not secret or len(secret) < 32:
        raise RuntimeError("JWT_SECRET must be set to a secret of at least 32 characters")
    if os.environ.get("APP_ENV") == "production" and url.startswith("sqlite"):
        raise RuntimeError("Production requires DATABASE_URL pointing to PostgreSQL")
    kwargs = {}
    if url == "sqlite://":
        kwargs = {"connect_args": {"check_same_thread": False}, "poolclass": StaticPool}
    elif url.startswith("sqlite"):
        kwargs = {"connect_args": {"check_same_thread": False}}
    engine = create_engine(url, **kwargs)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    should_seed = seed_demo if seed_demo is not None else os.environ.get("DEMO_SEED", "false").lower() == "true"

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        Base.metadata.create_all(engine)
        if should_seed:
            with SessionLocal() as db:
                seed(db)
        yield
        engine.dispose()

    api = FastAPI(title="TENANTPROOF Reference API", version="0.1.0", lifespan=lifespan)
    api.state.session_factory = SessionLocal
    api.state.jwt_secret = secret

    def db_session():
        with SessionLocal() as db:
            yield db

    def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(db_session)) -> User:
        if credentials is None:
            raise HTTPException(401, "Authentication required")
        try:
            claims = decode(credentials.credentials, secret, algorithms=["HS256"], audience="tenantproof-demo", issuer="tenantproof-demo", options={"require": ["sub", "exp", "iat", "iss", "aud"]})
            user = db.get(User, claims["sub"])
            if not user or claims.get("tenant_id") != user.tenant_id:
                raise InvalidTokenError("Identity mismatch")
            return user
        except (InvalidTokenError, KeyError):
            raise HTTPException(401, "Invalid token") from None

    @api.get("/health")
    def health():
        return {"status": "ok"}

    @api.get("/api/v1/invoices/{invoice_id}")
    def get_invoice(invoice_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
        # IMPORTANT: Reproduce M01 only inside an isolated temporary worktree.
        invoice = db.scalar(select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == user.tenant_id))
        if invoice is None:
            # This demo contract uses 403 for existing foreign-tenant invoices.
            existing = db.get(Invoice, invoice_id)
            if existing is not None:
                raise HTTPException(403, {"code": "TENANT_ACCESS_DENIED"})
            raise HTTPException(404, "Invoice not found")
        return {"id": invoice.id, "tenant_id": invoice.tenant_id, "reference": invoice.reference, "amount_cents": invoice.amount_cents, "currency": invoice.currency}

    return api

# Imported by the container server; test suites call create_app with isolated databases.
app = None
# Intentionally lazy for tests and one-off tools without configured credentials.
if os.environ.get("JWT_SECRET"):
    app = create_app()
