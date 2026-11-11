from datetime import datetime

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from models.block import Block
from models.contact import Contact
from models.friendship import FriendshipRequest
from models.user import User


class ContactService:
    @staticmethod
    def normalize_target(db: Session, user_input: str | int, current_user_id: int | None = None):
        text = str(user_input).strip()
        if text.isdigit():
            target = db.query(User).filter_by(id=int(text)).first()
            if target and current_user_id is not None and target.id == current_user_id:
                return None
            return target

        if text:
            target = db.query(User).filter(User.username.ilike(text)).first()
            if target and current_user_id is not None and target.id == current_user_id:
                return None
            return target
        return None

    @staticmethod
    def get_contacts(db: Session, user_id: int):
        return (
            db.query(User)
            .join(Contact, Contact.contact_id == User.id)
            .filter(Contact.user_id == user_id)
            .order_by(User.username.asc())
            .all()
        )

    @staticmethod
    def get_requests(db: Session, user_id: int, status: str | None = None):
        query = (
            db.query(FriendshipRequest)
            .join(User, User.id == FriendshipRequest.sender_id)
            .filter(FriendshipRequest.receiver_id == user_id)
        )
        if status is not None:
            query = query.filter(FriendshipRequest.status == status)
        return query.order_by(FriendshipRequest.sent_at.desc()).all()

    @staticmethod
    def send_friend_request(db: Session, sender_id: int, target_identifier: str | int):
        if sender_id is None:
            raise ValueError("Usuário inválido.")

        target_user = ContactService.normalize_target(db, target_identifier, current_user_id=sender_id)
        if not target_user:
            raise ValueError("Usuário não encontrado.")
        if target_user.id == sender_id:
            raise ValueError("Você não pode enviar solicitação para si mesmo.")
        if ContactService.is_blocked(db, sender_id, target_user.id):
            raise ValueError("Você não pode interagir com este usuário por estar bloqueado.")
        if ContactService.is_blocked(db, target_user.id, sender_id):
            raise ValueError("Este usuário bloqueou você. Solicitação não permitida.")

        existing = (
            db.query(FriendshipRequest)
            .filter(
                or_(
                    and_(FriendshipRequest.sender_id == sender_id, FriendshipRequest.receiver_id == target_user.id),
                    and_(FriendshipRequest.sender_id == target_user.id, FriendshipRequest.receiver_id == sender_id),
                )
            )
            .first()
        )
        if existing:
            raise ValueError("Já existe uma solicitação entre os usuários.")

        if ContactService.are_friends(db, sender_id, target_user.id):
            raise ValueError("Este usuário já é seu contato.")

        request = FriendshipRequest(sender_id=sender_id, receiver_id=target_user.id, status="pending")
        db.add(request)
        db.commit()
        db.refresh(request)
        return request

    @staticmethod
    def accept_friend_request(db: Session, request_id: int, user_id: int):
        request = (
            db.query(FriendshipRequest)
            .filter(FriendshipRequest.id == request_id, FriendshipRequest.receiver_id == user_id)
            .first()
        )
        if not request:
            raise ValueError("Solicitação não encontrada.")

        request.status = "accepted"

        if not ContactService.are_friends(db, request.sender_id, request.receiver_id):
            db.add(Contact(user_id=request.sender_id, contact_id=request.receiver_id))
            db.add(Contact(user_id=request.receiver_id, contact_id=request.sender_id))

        db.commit()
        return request

    @staticmethod
    def reject_friend_request(db: Session, request_id: int, user_id: int):
        request = (
            db.query(FriendshipRequest)
            .filter(FriendshipRequest.id == request_id, FriendshipRequest.receiver_id == user_id)
            .first()
        )
        if not request:
            raise ValueError("Solicitação não encontrada.")
        request.status = "rejected"
        db.commit()
        return request

    @staticmethod
    def are_friends(db: Session, user_id: int, contact_id: int) -> bool:
        return (
            db.query(Contact)
            .filter(Contact.user_id == user_id, Contact.contact_id == contact_id)
            .first()
            is not None
        )

    @staticmethod
    def remove_contact(db: Session, user_id: int, contact_id: int):
        db.query(Contact).filter(
            or_(
                and_(Contact.user_id == user_id, Contact.contact_id == contact_id),
                and_(Contact.user_id == contact_id, Contact.contact_id == user_id),
            )
        ).delete(synchronize_session=False)
        db.commit()

    @staticmethod
    def block_user(db: Session, blocker_id: int, blocked_id: int):
        if blocker_id == blocked_id:
            raise ValueError("Você não pode bloquear a si mesmo.")
        existing = db.query(Block).filter_by(blocker_id=blocker_id, blocked_id=blocked_id).first()
        if existing:
            return existing
        block = Block(blocker_id=blocker_id, blocked_id=blocked_id)
        db.add(block)
        db.commit()
        db.refresh(block)
        return block

    @staticmethod
    def unblock_user(db: Session, blocker_id: int, blocked_id: int):
        db.query(Block).filter_by(blocker_id=blocker_id, blocked_id=blocked_id).delete(synchronize_session=False)
        db.commit()

    @staticmethod
    def is_blocked(db: Session, blocker_id: int, blocked_id: int) -> bool:
        return db.query(Block).filter_by(blocker_id=blocker_id, blocked_id=blocked_id).first() is not None

    @staticmethod
    def get_blocked_users(db: Session, user_id: int):
        return db.query(User).join(Block, Block.blocked_id == User.id).filter(Block.blocker_id == user_id).all()

    @staticmethod
    def search_contacts(db: Session, user_id: int, search_text: str):
        text = (search_text or "").strip()
        if not text:
            return ContactService.get_contacts(db, user_id)
        return (
            db.query(User)
            .join(Contact, Contact.contact_id == User.id)
            .filter(Contact.user_id == user_id)
            .filter((User.username.ilike(f"%{text}%")) | (User.full_name.ilike(f"%{text}%")))
            .order_by(User.username.asc())
            .all()
        )
