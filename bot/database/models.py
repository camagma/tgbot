from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    username: Mapped[str | None] = mapped_column(String(128), nullable=True)
    display_name: Mapped[str] = mapped_column(String(256))
    total_messages: Mapped[int] = mapped_column(Integer, default=0)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    coins: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    messages: Mapped[list[Message]] = relationship(back_populates="user")

    __table_args__ = (UniqueConstraint("telegram_user_id", "chat_id", name="uq_user_chat"),)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_message_id: Mapped[int] = mapped_column(BigInteger, index=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    message_thread_id: Mapped[int | None] = mapped_column(BigInteger, index=True, nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    text: Mapped[str] = mapped_column(Text)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    reply_to_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    message_length: Mapped[int] = mapped_column(Integer)
    emoji_count: Mapped[int] = mapped_column(Integer)
    uppercase_count: Mapped[int] = mapped_column(Integer)
    has_links: Mapped[bool] = mapped_column(Boolean, default=False)
    has_bad_words: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)

    user: Mapped[User | None] = relationship(back_populates="messages")

    __table_args__ = (UniqueConstraint("telegram_message_id", "chat_id", name="uq_message_chat"),)


class ChatStat(Base):
    __tablename__ = "chat_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    key: Mapped[str] = mapped_column(String(64), index=True)
    value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class GeneratedMessage(Base):
    __tablename__ = "generated_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    message_thread_id: Mapped[int | None] = mapped_column(BigInteger, index=True, nullable=True)
    text: Mapped[str] = mapped_column(Text)
    generation_mode: Mapped[str] = mapped_column(String(32))
    personality_code: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BotState(Base):
    __tablename__ = "bot_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True, unique=True)
    personality_code: Mapped[str] = mapped_column(String(64), default="chaotic_gremlin")
    autopost_cooldown_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    anti_repeat_last_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    mood: Mapped[str] = mapped_column(String(64), default="neutral")


class Personality(Base):
    __tablename__ = "personalities"

    code: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(128))
    system_prompt: Mapped[str] = mapped_column(Text)
    post_frequency_bias: Mapped[int] = mapped_column(Integer, default=1)
    lexicon_json: Mapped[dict] = mapped_column(JSON, default=dict)


class Achievement(Base):
    __tablename__ = "achievements"

    code: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(Text)
    rarity: Mapped[str] = mapped_column(String(32), default="common")


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    achievement_code: Mapped[str] = mapped_column(ForeignKey("achievements.code"), index=True)
    awarded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LoreEvent(Base):
    __tablename__ = "lore_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    title: Mapped[str] = mapped_column(String(128))
    body: Mapped[str] = mapped_column(Text)
    rarity: Mapped[str] = mapped_column(String(32), default="common")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
