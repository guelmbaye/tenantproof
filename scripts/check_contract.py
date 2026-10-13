from pathlib import Path
import yaml

contract = yaml.safe_load(Path("contracts/tenant-boundaries.yaml").read_text())
invoice = contract["resources"]["invoice"]
assert contract["version"] == 1
assert invoice["method"] == "GET"
assert invoice["denied_status"] == 403
assert invoice["owner_field"] == "tenant_id"
print("Boundary contract valid (minimal checks)")
