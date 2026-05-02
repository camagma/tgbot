from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone

from sqlalchemy import Integer, cast, desc, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.database.models import Message, User
from bot.database.repositories import MessageRepository
from bot.services.style_analyzer import StyleAnalyzer
from bot.utils.text_metrics import normalize_words


class StatsService:
    def __init__(self, session_factory: async_sessionmaker) -> None:
        self.session_factory = session_factory
        self.analyzer = StyleAnalyzer()

    async def chaos_level(self, chat_id: int, thread_id: int | None = None) -> int:
        async with self.session_factory() as session:
            messages = await MessageRepository(session).latest_messages(chat_id, limit=250, thread_id=thread_id)
            return self.analyzer.analyze(messages).chaos_score

    async def mood(self, chat_id: int, thread_id: int | None = None) -> str:
        async with self.session_factory() as session:
            messages = await MessageRepository(session).latest_messages(chat_id, limit=200, thread_id=thread_id)
            return self.analyzer.analyze(messages).mood

    async def top_words(self, chat_id: int, limit: int = 10, thread_id: int | None = None) -> list[tuple[str, int]]:
        async with self.session_factory() as session:
            messages = await MessageRepository(session).latest_messages(chat_id, limit=500, thread_id=thread_id)
            counter: Counter[str] = Counter()
            for msg in messages:
                counter.update(normalize_words(msg.text))
            return counter.most_common(limit)

    async def archetypes(self, chat_id: int, thread_id: int | None = None) -> dict[str, str]:
        async with self.session_factory() as session:
            latest_24h = datetime.now(timezone.utc) - timedelta(hours=24)
            base_filters = [User.chat_id == chat_id]
            if thread_id is not None:
                base_filters.append(Message.message_thread_id == thread_id)

            spammer = await session.scalar(
                select(User.display_name)
                .join(Message, Message.user_id == User.id)
                .where(*base_filters, Message.sent_at >= latest_24h)
                .group_by(User.id)
                .order_by(desc(func.count(Message.id)))
                .limit(1)
            )

            philosopher = await session.scalar(
                select(User.display_name)
                .join(Message, Message.user_id == User.id)
                .where(*base_filters)
                .group_by(User.id)
                .order_by(desc(func.avg(Message.message_length)))
                .limit(1)
            )

            conspiracy = await session.scalar(
                select(User.display_name)
                .join(Message, Message.user_id == User.id)
                .where(*base_filters, Message.text.ilike("%теория%"))
                .group_by(User.id)
                .order_by(desc(func.count(Message.id)))
                .limit(1)
            )

            deadline_king = await session.scalar(
                select(User.display_name)
                .join(Message, Message.user_id == User.id)
                .where(*base_filters, Message.text.ilike("%дедлайн%"))
                .group_by(User.id)
                .order_by(desc(func.count(Message.id)))
                .limit(1)
            )

            night_user = await session.scalar(
                select(User.display_name)
                .join(Message, Message.user_id == User.id)
                .where(*base_filters, cast(func.strftime("%H", Message.sent_at), Integer) <= 5)
                .group_by(User.id)
                .order_by(desc(func.count(Message.id)))
                .limit(1)
            )

            return {
                "spammer": spammer or "unknown entity",
                "philosopher": philosopher or "silent observer",
                "conspiracy_theorist": conspiracy or "nobody suspicious yet",
                "deadline_king": deadline_king or "no deadlines detected",
                "night_core": night_user or "sleep mode",
            }

    async def leaderboard(self, chat_id: int, thread_id: int | None = None) -> list[tuple[str, int, int]]:
        async with self.session_factory() as session:
            stmt = (
                select(User.display_name, func.count(Message.id).label("msg_count"), User.xp)
                .join(Message, Message.user_id == User.id)
                .where(User.chat_id == chat_id)
                .group_by(User.id)
                .order_by(desc(func.count(Message.id)))
                .limit(10)
            )
            if thread_id is not None:
                stmt = stmt.where(Message.message_thread_id == thread_id)
            rows = await session.execute(stmt)
            return list(rows.all())
