"""Place M01 on a dedicated *local* demo branch to exercise real MR + Duo.
Refuses default/non-demo branches, dirty trees, production context and missing opt-in.
Never pushes or opens MRs automatically.
"""
import argparse
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = 'select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == user.tenant_id)'
MUTATED = 'select(Invoice).where(Invoice.id == invoice_id)'

def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--acknowledge-synthetic', action='store_true')
    args = parser.parse_args()
    if not args.acknowledge_synthetic:
        parser.error('Pass --acknowledge-synthetic after confirming this is a synthetic-only test repository')
    if os.environ.get('APP_ENV', 'development') == 'production':
        raise SystemExit('M01 mutation disallowed in production APP_ENV')
    branch = git('branch', '--show-current')
    if not branch.startswith('demo/m01-'):
        raise SystemExit('Refusing mutation outside demo/m01-* branch')
    if git('status', '--porcelain'):
        raise SystemExit('Working tree must be clean before mutation')
    path = ROOT / 'app/main.py'
    original = path.read_text()
    if original.count(ORIGINAL) != 1:
        raise SystemExit('Mutation target mismatch; source may have changed')
    path.write_text(original.replace(ORIGINAL, MUTATED, 1))
    print('M01 introduced in local branch:', branch)
    print('DO NOT MERGE. Commit and create an MR to be remediated by GitLab Duo.')

if __name__ == '__main__':
    main()
