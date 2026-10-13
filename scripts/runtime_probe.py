"""Post-deploy verifier. Requires two short-lived synthetic JWTs in protected CI.
Never passes from an absent endpoint or an HTTP health-only check.
"""
import json
import os
import sys
import httpx
from app.fixtures import INVOICE_A, INVOICE_B, TENANT_A

url = os.environ.get("TENANTPROOF_DEPLOYED_URL", "").rstrip("/")
token = os.environ.get("TENANTPROOF_SYNTHETIC_A_TOKEN", "")
if not url.startswith("https://") or not token:
    sys.exit("INCONCLUSIVE: secure deployed URL and synthetic token required")
headers = {"Authorization": "Bearer " + token}
with httpx.Client(timeout=20) as client:
    own = client.get(f"{url}/api/v1/invoices/{INVOICE_A}", headers=headers)
    foreign = client.get(f"{url}/api/v1/invoices/{INVOICE_B}", headers=headers)
passed = own.status_code == 200 and own.json().get("tenant_id") == TENANT_A and foreign.status_code == 403 and "BH-SECRET-SYNTHETIC" not in foreign.text
print(json.dumps({"authorized_status": own.status_code, "foreign_status": foreign.status_code, "passed": passed}))
if not passed:
    sys.exit(1)
