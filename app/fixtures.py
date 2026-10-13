from sqlalchemy.orm import Session
from app.models import Tenant, User, Invoice

TENANT_A = "00000000-0000-4000-8000-000000000001"
TENANT_B = "00000000-0000-4000-8000-000000000002"
USER_A = "00000000-0000-4000-8000-000000000011"
USER_B = "00000000-0000-4000-8000-000000000012"
INVOICE_A = "00000000-0000-4000-8000-000000000101"
INVOICE_B = "00000000-0000-4000-8000-000000000102"

def seed(session: Session) -> None:
    if session.get(Tenant, TENANT_A):
        return
    session.add_all([
        Tenant(id=TENANT_A, code="NORTHSTAR", name="Northstar Synthetic LLC"),
        Tenant(id=TENANT_B, code="BLUEHARBOR", name="Blueharbor Synthetic LLC"),
        User(id=USER_A, tenant_id=TENANT_A, email="a@example.invalid"),
        User(id=USER_B, tenant_id=TENANT_B, email="b@example.invalid"),
        Invoice(id=INVOICE_A, tenant_id=TENANT_A, reference="NS-001", amount_cents=2700, currency="USD"),
        Invoice(id=INVOICE_B, tenant_id=TENANT_B, reference="BH-SECRET-SYNTHETIC", amount_cents=9400, currency="USD"),
    ])
    session.commit()
