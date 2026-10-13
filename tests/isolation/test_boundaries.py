from app.fixtures import INVOICE_A, INVOICE_B, TENANT_A, TENANT_B

def auth(token):
    return {"Authorization": f"Bearer {token}"}

def test_a_cannot_read_b(client, token_a):
    result = client.get(f"/api/v1/invoices/{INVOICE_B}", headers=auth(token_a))
    assert result.status_code == 403, f"Cross-tenant access leaked: HTTP {result.status_code}"
    assert "BH-SECRET-SYNTHETIC" not in result.text
    assert TENANT_B not in result.text

def test_b_cannot_read_a(client, token_b):
    result = client.get(f"/api/v1/invoices/{INVOICE_A}", headers=auth(token_b))
    assert result.status_code == 403
    assert "NS-001" not in result.text
    assert TENANT_A not in result.text

def test_b_can_read_b(client, token_b):
    result = client.get(f"/api/v1/invoices/{INVOICE_B}", headers=auth(token_b))
    assert result.status_code == 200
    assert result.json()["tenant_id"] == TENANT_B

def test_unknown_invoice_not_found(client, token_a):
    assert client.get("/api/v1/invoices/does-not-exist", headers=auth(token_a)).status_code == 404
