"""Reproduce real source mutation M01 safely in a disposable temp directory.
The script returns success ONLY if conventional tests pass and isolation tests fail.
It never modifies the caller repository, and runs no deployed service.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = 'select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == user.tenant_id)'
MUTATED = 'select(Invoice).where(Invoice.id == invoice_id)'

def execute(args, cwd):
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "--tb=line", *args], cwd=cwd,
                            text=True, capture_output=True, timeout=120,
                            env={**os.environ, "PYTHONPATH": str(cwd)})
    return {"returncode": result.returncode, "stdout": result.stdout[-2500:], "stderr": result.stderr[-800:]}

def main():
    if os.environ.get("APP_ENV") == "production":
        raise RuntimeError("M01 replay prohibited under production APP_ENV")
    with tempfile.TemporaryDirectory(prefix="tenantproof-m01-") as temporary:
        sandbox = Path(temporary)
        for name in ["app", "tests", "contracts"]:
            shutil.copytree(ROOT / name, sandbox / name, ignore=shutil.ignore_patterns("__pycache__"))
        source = sandbox / "app/main.py"
        content = source.read_text()
        if content.count(ORIGINAL) != 1:
            raise RuntimeError("Mutation target changed; refusing to apply M01")
        source.write_text(content.replace(ORIGINAL, MUTATED, 1))
        baseline = execute(["tests/baseline"], sandbox)
        isolation = execute(["tests/isolation"], sandbox)
        output = {"scenario": "M01_missing_tenant_predicate", "baseline": baseline,
                  "isolation": isolation, "baseline_green": baseline["returncode"] == 0,
                  "isolation_red": isolation["returncode"] == 1, "source_mutated_in_tempdir": True,
                  "source_repository_modified": False, "duo_executed": False}
        print(json.dumps(output, indent=2))
        if not (output["baseline_green"] and output["isolation_red"] and "2 failed" in isolation["stdout"]):
            raise SystemExit("EXPECTED CONTRAST NOT OBTAINED")
        print("PASS: baseline green, independent isolation suite red (real mutation)")
if __name__ == "__main__":
    main()
