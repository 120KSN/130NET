from sqlalchemy import and_
from sqlalchemy.orm import Session

from models.conversation import ConversationParticipant
from models.message import HiddenMessage, Message


class MessageService:
    @staticmethod
    def send_message(db: Session, conversation_id: int, sender_id: int, content: str, reply_to_id: int | None = None) -> Message:
        cleaned = (content or "").strip()
        if not cleaned:
            raise ValueError("A mensagem não pode ficar vazia.")

        is_participant = (
            db.query(ConversationParticipant)
            .filter_by(conversation_id=conversation_id, user_id=sender_id)
            .first()
            is not None
        )
        if not is_participant:
            raise PermissionError("Você não pode enviar mensagens nesta conversa.")

        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=cleaned,
            reply_to_id=reply_to_id,
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def list_messages(db: Session, conversation_id: int, user_id: int):
        hidden_messages = (
            db.query(HiddenMessage.message_id)
            .filter(HiddenMessage.user_id == user_id)
            .subquery()
        )
        return (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .filter(~Message.id.in_(hidden_messages))
            .order_by(Message.sent_at.asc())
            .all()
        )

    @staticmethod
    def delete_for_user(db: Session, message_id: int, user_id: int, delete_for_all: bool = False):
        message = db.query(Message).filter_by(id=message_id).first()
        if not message:
            raise ValueError("Mensagem não encontrada.")

        if delete_for_all:
            if message.sender_id != user_id:
                raise PermissionError("Apenas o autor pode excluir para todos.")
            participants = [
                participant.user_id
                for participant in db.query(ConversationParticipant)
                .filter_by(conversation_id=message.conversation_id)
                .all()
            ]
            for participant_id in participants:
                existing = (
                    db.query(HiddenMessage)
                    .filter_by(message_id=message.id, user_id=participant_id)
                    .first()
                )
                if not existing:
                    db.add(HiddenMessage(message_id=message.id, user_id=participant_id))
        else:
            existing = db.query(HiddenMessage).filter_by(message_id=message.id, user_id=user_id).first()
            if not existing:
                db.add(HiddenMessage(message_id=message.id, user_id=user_id))

        db.commit()
        return True

    @staticmethod
    def get_message_by_id(db: Session, message_id: int) -> Message | None:
        return db.query(Message).filter_by(id=message_id).first()
