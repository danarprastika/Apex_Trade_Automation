from sqlalchemy.orm import Session

from app.database.models.identity import User, UserRole


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, email: str, password_hash: str, role: UserRole = UserRole.TRADER, status: str = "ACTIVE") -> User:
    # Generate username from email if not provided
    username = email.split("@")[0]
    user = User(
        email=email,
        username=username,
        password_hash=password_hash,
        role=role,
        status=status,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
