from __future__ import annotations

from datetime import datetime, timedelta, timezone
from random import choice

from sqlalchemy import Integer, Select, and_, cast, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import BotState, ChatStat, GeneratedMessage, LoreEvent, Message, Personality, User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create(self, chat_id: int, telegram_user_id: int, username: str | None, display_name: str) -> User:
        stmt = select(User).where(and_(User.chat_id == chat_id, User.telegram_user_id == telegram_user_id))
        user = await self.session.scalar(stmt)
        if user:
            user.username = username
            user.display_name = display_name
            return user
        user = User(
            chat_id=chat_id,
            telegram_user_id=telegram_user_id,
            username=username,
            display_name=display_name,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def top_night_user(self, chat_id: int) -> User | None:
        night_start = 0
        night_end = 5
        stmt = (
            select(User)
            .join(Message, Message.user_id == User.id)
            .where(
                User.chat_id == chat_id,
                cast(func.strftime("%H", Message.sent_at), Integer).between(night_start, night_end),
            )
            .group_by(User.id)
            .order_by(desc(func.count(Message.id)))
            .limit(1)
        )
        return await self.session.scalar(stmt)


class MessageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **kwargs) -> Message:
        message = Message(**kwargs)
        self.session.add(message)
        return message

    async def latest_texts(self, chat_id: int, limit: int = 120, thread_id: int | None = None) -> list[str]:
        stmt = select(Message.text).where(Message.chat_id == chat_id)
        if thread_id is not None:
            stmt = stmt.where(Message.message_thread_id == thread_id)
        stmt = stmt.order_by(desc(Message.sent_at)).limit(limit)
        rows = (await self.session.execute(stmt)).all()
        return [row[0] for row in rows if row[0]]

    async def random_quote(self, chat_id: int, thread_id: int | None = None) -> Message | None:
        rows = await self.latest_messages(chat_id, limit=1000, thread_id=thread_id)
        return choice(rows) if rows else None

    async def latest_messages(self, chat_id: int, limit: int = 50, thread_id: int | None = None) -> list[Message]:
        stmt: Select[tuple[Message]] = (
            select(Message).where(Message.chat_id == chat_id)
        )
        if thread_id is not None:
            stmt = stmt.where(Message.message_thread_id == thread_id)
        stmt = stmt.order_by(desc(Message.sent_at)).limit(limit)
        return list((await self.session.scalars(stmt)).all())

    async def oldest_message(self, chat_id: int, thread_id: int | None = None) -> Message | None:
        stmt = select(Message).where(Message.chat_id == chat_id)
        if thread_id is not None:
            stmt = stmt.where(Message.message_thread_id == thread_id)
        stmt = stmt.order_by(Message.sent_at.asc()).limit(1)
        return await self.session.scalar(stmt)

    async def messages_after(self, chat_id: int, dt: datetime) -> int:
        stmt = select(func.count(Message.id)).where(Message.chat_id == chat_id, Message.sent_at >= dt)
        return int((await self.session.scalar(stmt)) or 0)

    async def active_users(self, chat_id: int, hours: int = 24) -> list[tuple[str, int]]:
        dt = datetime.now(timezone.utc) - timedelta(hours=hours)
        stmt = (
            select(User.display_name, func.count(Message.id))
            .join(User, User.id == Message.user_id)
            .where(Message.chat_id == chat_id, Message.sent_at >= dt)
            .group_by(User.display_name)
            .order_by(desc(func.count(Message.id)))
            .limit(10)
        )
        return list((await self.session.execute(stmt)).all())

    async def count_by_chat(self, chat_id: int, thread_id: int | None = None) -> int:
        stmt = select(func.count(Message.id)).where(Message.chat_id == chat_id)
        if thread_id is not None:
            stmt = stmt.where(Message.message_thread_id == thread_id)
        return int((await self.session.scalar(stmt)) or 0)


class BotStateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create(self, chat_id: int, personality_code: str) -> BotState:
        state = await self.session.scalar(select(BotState).where(BotState.chat_id == chat_id))
        if state:
            return state
        state = BotState(chat_id=chat_id, personality_code=personality_code)
        self.session.add(state)
        await self.session.flush()
        return state


class StatsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def set(self, chat_id: int, key: str, value: str) -> None:
        item = await self.session.scalar(select(ChatStat).where(ChatStat.chat_id == chat_id, ChatStat.key == key))
        if item:
            item.value = value
            return
        self.session.add(ChatStat(chat_id=chat_id, key=key, value=value))

    async def get(self, chat_id: int, key: str) -> str | None:
        item = await self.session.scalar(select(ChatStat).where(ChatStat.chat_id == chat_id, ChatStat.key == key))
        return item.value if item else None


class GeneratedRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(
        self,
        chat_id: int,
        text: str,
        generation_mode: str,
        personality_code: str,
        thread_id: int | None = None,
    ) -> None:
        self.session.add(
            GeneratedMessage(
                chat_id=chat_id,
                message_thread_id=thread_id,
                text=text,
                generation_mode=generation_mode,
                personality_code=personality_code,
            )
        )

    async def last_generated(self, chat_id: int, thread_id: int | None = None) -> str | None:
        stmt = (
            select(GeneratedMessage.text)
            .where(GeneratedMessage.chat_id == chat_id)
        )
        if thread_id is not None:
            stmt = stmt.where(GeneratedMessage.message_thread_id == thread_id)
        stmt = stmt.order_by(desc(GeneratedMessage.created_at)).limit(1)
        return await self.session.scalar(stmt)


class LoreRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_event(self, chat_id: int, title: str, body: str, rarity: str = "common") -> LoreEvent:
        event = LoreEvent(chat_id=chat_id, title=title, body=body, rarity=rarity)
        self.session.add(event)
        await self.session.flush()
        return event

    async def random_event(self, chat_id: int) -> LoreEvent | None:
        stmt = select(LoreEvent).where(LoreEvent.chat_id == chat_id).order_by(func.random()).limit(1)
        return await self.session.scalar(stmt)


class PersonalityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, code: str) -> Personality | None:
        return await self.session.scalar(select(Personality).where(Personality.code == code))

    async def seed_defaults(self, payloads: list[dict]) -> None:
        for item in payloads:
            exists = await self.get(item["code"])
            if exists:
                continue
            self.session.add(Personality(**item))
