"""Local declaration check only; GitLab protected branch policies are external."""
from validate_gitlab_config import validate_ci
issues = validate_ci()
if issues:
    raise SystemExit("CI configuration INVALID: " + "; ".join(issues))
print("PASS: required gate declarations found; verify branch protection externally")
