from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from models.user import User


class AuthService:
    @staticmethod
    def register(db: Session, full_name: str, username: str, password: str) -> User:
        normalized_full_name = (full_name or "").strip()
        normalized_username = (username or "").strip()
        if not normalized_full_name:
            raise ValueError("Informe o nome completo.")
        if len(normalized_full_name) < 2:
            raise ValueError("O nome completo deve ter pelo menos 2 caracteres.")
        if not normalized_username:
            raise ValueError("Informe um nome de usuário.")
        if len(normalized_username) < 3:
            raise ValueError("O nome de usuário deve ter pelo menos 3 caracteres.")
        if len(password or "") < 6:
            raise ValueError("A senha deve ter pelo menos 6 caracteres.")
        if db.query(User).filter_by(username=normalized_username).first():
            raise ValueError("Nome de usuário já cadastrado.")

        user = User(
            full_name=normalized_full_name,
            username=normalized_username,
            password_hash=generate_password_hash(password),
            description="",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> User | None:
        normalized_username = (username or "").strip()
        if not normalized_username:
            return None

        user = db.query(User).filter_by(username=normalized_username).first()
        if not user:
            return None
        if check_password_hash(user.password_hash, password):
            return user
        return None
