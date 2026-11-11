from sqlalchemy import func
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from models.user import User


class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        return db.query(User).filter_by(id=user_id).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> User | None:
        if not username:
            return None
        return db.query(User).filter(func.lower(User.username) == func.lower(username.strip())).first()

    @staticmethod
    def update_profile(db: Session, user_id: int, *, full_name: str | None = None, username: str | None = None, description: str | None = None) -> User:
        user = db.query(User).filter_by(id=user_id).first()
        if user is None:
            raise ValueError("Usuário não encontrado.")

        if full_name is not None:
            clean_name = (full_name or "").strip()
            if not clean_name:
                raise ValueError("O nome completo não pode ficar vazio.")
            user.full_name = clean_name

        if username is not None:
            clean_username = (username or "").strip()
            if not clean_username:
                raise ValueError("O nome de usuário não pode ficar vazio.")
            existing = db.query(User).filter(User.username == clean_username, User.id != user_id).first()
            if existing:
                raise ValueError("Esse nome de usuário já está em uso.")
            user.username = clean_username

        if description is not None:
            user.description = (description or "")[:500]

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_password(db: Session, user_id: int, new_password: str) -> User:
        user = db.query(User).filter_by(id=user_id).first()
        if user is None:
            raise ValueError("Usuário não encontrado.")
        if len(new_password or "") < 6:
            raise ValueError("A nova senha deve ter pelo menos 6 caracteres.")

        user.password_hash = generate_password_hash(new_password)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def search_users(db: Session, query: str, current_user_id: int | None = None):
        trimmed = (query or "").strip()
        if not trimmed:
            return []
        q = db.query(User).filter(
            (User.username.ilike(f"%{trimmed}%")) | (User.full_name.ilike(f"%{trimmed}%"))
        )
        if current_user_id is not None:
            q = q.filter(User.id != current_user_id)
        return q.order_by(User.username.asc()).limit(20).all()
