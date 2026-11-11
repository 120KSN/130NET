from sqlalchemy.orm import Session

from models.conversation import Conversation, ConversationParticipant


class ConversationService:
    @staticmethod
    def get_or_create_conversation(db: Session, user_id: int, contact_id: int) -> Conversation:
        if user_id == contact_id:
            raise ValueError("Você não pode iniciar uma conversa consigo mesmo.")

        for conversation in (
            db.query(Conversation)
            .join(ConversationParticipant)
            .filter(ConversationParticipant.user_id == user_id)
            .distinct()
            .all()
        ):
            ids = {participant.user_id for participant in conversation.participants}
            if contact_id in ids and len(ids) == 2:
                return conversation

        conversation = Conversation()
        db.add(conversation)
        db.flush()

        db.add_all(
            [
                ConversationParticipant(conversation_id=conversation.id, user_id=user_id),
                ConversationParticipant(conversation_id=conversation.id, user_id=contact_id),
            ]
        )
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def list_for_user(db: Session, user_id: int):
        conversations = (
            db.query(Conversation)
            .join(ConversationParticipant)
            .filter(ConversationParticipant.user_id == user_id)
            .distinct()
            .order_by(Conversation.created_at.desc())
            .all()
        )
        return conversations

    @staticmethod
    def get_conversation_between(db: Session, user_id: int, contact_id: int) -> Conversation | None:
        for conversation in ConversationService.list_for_user(db, user_id):
            ids = {participant.user_id for participant in conversation.participants}
            if contact_id in ids and len(ids) == 2:
                return conversation
        return None
