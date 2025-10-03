#!/usr/bin/env python3
"""
Usage:
  python scripts/jwt_diagnose.py <service_dir_for_issuer> <service_dir_for_verifier>

Example:
  python scripts/jwt_diagnose.py services/iam-service services/catalogo-service
"""
import os, sys, importlib, time, json
from pathlib import Path

def load_shared(cwd, db_name="mysql"):
    # ensure shared path is importable
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "libs" / "shared"))
    os.chdir(root / cwd)
    os.environ.setdefault("DB_NAME", db_name)
    for m in ['ev_shared.config','ev_shared.security']:
        if m in sys.modules:
            del sys.modules[m]
    from ev_shared.config import settings
    from ev_shared import security
    return settings, security

def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    issuer_dir = sys.argv[1]
    verifier_dir = sys.argv[2]

    s1, sec1 = load_shared(issuer_dir, db_name=os.getenv("DB_NAME", "mysql"))
    token = sec1.create_jwt(sub="smoketest", email="smoke@example.com", roles=["CLIENTE"], expires_minutes=1)
    print("Issuer:", issuer_dir)
    print("  JWT_ALG:", s1.JWT_ALG)
    print("  JWT_SECRET (len):", len(s1.JWT_SECRET))
    print("Token (first 60):", token[:60] + "...")

    s2, sec2 = load_shared(verifier_dir, db_name=os.getenv("DB_NAME", "mysql"))
    claims = sec2.decode_jwt(token)
    print("Verifier:", verifier_dir)
    print("  JWT_ALG:", s2.JWT_ALG)
    print("  JWT_SECRET (len):", len(s2.JWT_SECRET))
    print("Claims:", json.dumps(claims, indent=2))

if __name__ == "__main__":
    main()
