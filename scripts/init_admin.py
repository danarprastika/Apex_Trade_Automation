import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.core.security import hash_password
from app.database.base import SessionLocal
from app.database.models.identity import User, UserRole


def create_super_admin(email: str, username: str, password: str) -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter((User.email == email) | (User.username == username)).first()
        if existing:
            raise SystemExit(f"User with email '{email}' or username '{username}' already exists.")

        user = User(
            email=email,
            username=username,
            password_hash=hash_password(password),
            role=UserRole.SUPER_ADMIN,
            status="ACTIVE",
        )
        db.add(user)
        db.commit()
        print(f"Super admin created: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize APEX super admin user")
    parser.add_argument("--email", required=True, help="Admin email")
    parser.add_argument("--username", required=True, help="Admin username")
    parser.add_argument("--password", required=True, help="Admin password")
    args = parser.parse_args()

    create_super_admin(args.email, args.username, args.password)
