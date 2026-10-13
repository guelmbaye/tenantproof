"""Prevent adding release overrides to a change under review.
This is a bootstrap integrity check, NOT a replacement for branch protections.
"""
from pathlib import Path
ci = Path('.gitlab-ci.yml').read_text()
assert 'isolation-gate:' in ci
assert 'python -m pytest -q tests/isolation' in ci
assert 'security-check:' in ci
assert 'cloudrun-deploy:' in ci
print('Required CI gate declarations present; configure protected branches in GitLab UI')
