from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    contacts: Mapped[list["Contact"]] = relationship(
        "Contact", foreign_keys="Contact.user_id", back_populates="user"
    )
    contacted_by: Mapped[list["Contact"]] = relationship(
        "Contact", foreign_keys="Contact.contact_id", back_populates="contact_user"
    )
    sent_requests: Mapped[list["FriendshipRequest"]] = relationship(
        "FriendshipRequest", foreign_keys="FriendshipRequest.sender_id", back_populates="sender"
    )
    received_requests: Mapped[list["FriendshipRequest"]] = relationship(
        "FriendshipRequest", foreign_keys="FriendshipRequest.receiver_id", back_populates="receiver"
    )
    blocked_users: Mapped[list["Block"]] = relationship(
        "Block", foreign_keys="Block.blocker_id", back_populates="blocker"
    )
    blocked_by: Mapped[list["Block"]] = relationship(
        "Block", foreign_keys="Block.blocked_id", back_populates="blocked_user"
    )
