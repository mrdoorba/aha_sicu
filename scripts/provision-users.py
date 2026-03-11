#!/usr/bin/env python3
"""Provision Firebase Auth user accounts for the BD team.

Provisioning Process:
  1. Copy users-config.example.yaml to users-config.yaml
  2. Fill in real user emails, passwords, and display names
  3. Set FIREBASE_CREDENTIALS_PATH or FIREBASE_CREDENTIALS_JSON env var
  4. Run: python provision-users.py [--config users-config.yaml]
  5. After ALL users have logged in once (to trigger auto-creation in DB),
     run assign-roles.sql against the production database

Prerequisites:
  - pip install firebase-admin pyyaml  (or use backend venv which has firebase-admin)
  - Firebase Admin credentials (service account JSON) for the target project
  - Target the PRODUCTION Firebase project (e.g., aha-coms-sicu-prod)

Credential options (checked in order):
  1. FIREBASE_CREDENTIALS_JSON env var — JSON string (used in production/CI)
  2. FIREBASE_CREDENTIALS_PATH env var — path to service account JSON file
  3. --credentials CLI argument — path to service account JSON file

Security:
  - NEVER commit users-config.yaml (contains real credentials)
  - scripts/users-config.yaml is in .gitignore
  - Distribute initial passwords to users securely (not via email/chat)
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)

try:
    import firebase_admin
    from firebase_admin import auth, credentials
except ImportError:
    print("ERROR: firebase-admin not installed. Run: pip install firebase-admin")
    sys.exit(1)


def init_firebase(cred_path: str | None = None) -> None:
    """Initialize Firebase Admin SDK."""
    if firebase_admin._apps:
        return

    cred_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    cred_file = cred_path or os.environ.get("FIREBASE_CREDENTIALS_PATH")

    if cred_json:
        cred = credentials.Certificate(json.loads(cred_json))
        firebase_admin.initialize_app(cred)
    elif cred_file:
        cred = credentials.Certificate(cred_file)
        firebase_admin.initialize_app(cred)
    else:
        # Fallback: use Application Default Credentials (gcloud auth)
        print("INFO: No explicit credentials found, using Application Default Credentials (gcloud auth)")
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)


def load_config(config_path: str) -> list[dict]:
    """Load user configuration from YAML file."""
    path = Path(config_path)
    if not path.exists():
        print(f"ERROR: Config file not found: {config_path}")
        print("Copy users-config.example.yaml to users-config.yaml and fill in values.")
        sys.exit(1)

    with open(path) as f:
        config = yaml.safe_load(f)

    users = config.get("users", [])
    if not users:
        print("ERROR: No users defined in config file.")
        sys.exit(1)

    return users


def provision_user(user_config: dict) -> str | None:
    """Create a single Firebase Auth user. Returns UID on success, None on skip."""
    email = user_config["email"]
    password = user_config["password"]
    display_name = user_config.get("display_name", "")

    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name,
        )
        print(f"  CREATED: {email} -> UID: {user.uid}")
        return user.uid
    except auth.EmailAlreadyExistsError:
        # User already exists — fetch their UID for role assignment
        existing = auth.get_user_by_email(email)
        print(f"  EXISTS:  {email} -> UID: {existing.uid} (skipped creation)")
        return existing.uid
    except Exception as e:
        print(f"  FAILED:  {email} -> {e}")
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision Firebase Auth user accounts")
    parser.add_argument(
        "--config",
        default="scripts/users-config.yaml",
        help="Path to users config YAML (default: scripts/users-config.yaml)",
    )
    parser.add_argument(
        "--credentials",
        default=None,
        help="Path to Firebase service account JSON file",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Firebase User Provisioning")
    print("=" * 60)

    # Initialize Firebase
    init_firebase(args.credentials)
    print(f"\nFirebase project: {firebase_admin.get_app().project_id}")

    # Load config
    users = load_config(args.config)
    print(f"Users to provision: {len(users)}\n")

    # Provision each user
    results = []
    for user_config in users:
        uid = provision_user(user_config)
        results.append({
            "email": user_config["email"],
            "role": user_config.get("role", "member"),
            "uid": uid,
        })

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    created = sum(1 for r in results if r["uid"])
    failed = sum(1 for r in results if not r["uid"])
    print(f"  Created/Found: {created}")
    print(f"  Failed: {failed}")

    if failed:
        print("\nWARNING: Some accounts failed. Check errors above.")
        sys.exit(1)

    # Print UID mapping for role assignment
    print("\n" + "=" * 60)
    print("UID Mapping (for assign-roles.sql)")
    print("=" * 60)
    for r in results:
        if r["uid"]:
            print(f"  {r['email']:40s} role={r['role']:8s} uid={r['uid']}")

    print("\nNext steps:")
    print("  1. Have ALL users log in once at https://aha-coms-sicu-prod.web.app")
    print("     (this triggers auto-creation of their record in the users table)")
    print("  2. Update assign-roles.sql with the UIDs shown above")
    print("  3. Run assign-roles.sql against the production database")


if __name__ == "__main__":
    main()
