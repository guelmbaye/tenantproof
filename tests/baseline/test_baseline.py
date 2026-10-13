from app.fixtures import INVOICE_A, INVOICE_B

def auth(token):
    return {"Authorization": f"Bearer {token}"}

def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}

def test_authorized_a(client, token_a):
    response = client.get(f"/api/v1/invoices/{INVOICE_A}", headers=auth(token_a))
    assert response.status_code == 200
    assert response.json()["reference"] == "NS-001"

def test_missing_auth(client):
    assert client.get(f"/api/v1/invoices/{INVOICE_A}").status_code == 401

def test_invalid_auth(client):
    assert client.get(f"/api/v1/invoices/{INVOICE_A}", headers=auth("invalid")).status_code == 401
