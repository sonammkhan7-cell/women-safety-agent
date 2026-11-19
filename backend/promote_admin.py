import argparse
import sys

from app.database import SessionLocal
from app.services.auth_service import promote_user_to_admin


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Grant admin review access to an existing registered account."
    )
    parser.add_argument("email", help="Email address of the trusted reviewer account")
    args = parser.parse_args()

    email = args.email.strip().lower()
    confirmation = input(
        f"Grant admin review access to {email}? Type 'yes' to confirm: "
    ).strip().lower()
    if confirmation != "yes":
        print("Cancelled; no account changes were made.")
        return 1

    db = SessionLocal()
    try:
        user = promote_user_to_admin(db, email)
    except ValueError as exc:
        print(f"Could not grant admin access: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()

    print(f"Admin review access granted to existing account ID {user.id}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
