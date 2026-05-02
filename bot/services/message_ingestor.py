from __future__ import annotations

import logging

from aiogram.types import Message as TgMessage
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.database.repositories import MessageRepository, UserRepository
from bot.services.achievement_service import AchievementService
from bot.services.economy_service import EconomyService
from bot.utils.text_filters import has_bad_words, has_link, is_command
from bot.utils.text_metrics import emoji_count, uppercase_count

logger = logging.getLogger(__name__)


class MessageIngestor:
    def __init__(
        self,
        session_factory: async_sessionmaker,
        achievement_service: AchievementService,
        economy_service: EconomyService,
    ) -> None:
        self.session_factory = session_factory
        self.achievement_service = achievement_service
        self.economy_service = economy_service

    async def ingest(self, message: TgMessage) -> None:
        if not message.text:
            return
        if is_command(message.text):
            return
        if message.from_user and message.from_user.is_bot:
            return

        async with self.session_factory() as session:
            users = UserRepository(session)
            messages = MessageRepository(session)

            display_name = " ".join(
                [part for part in [message.from_user.first_name, message.from_user.last_name] if part]
            ).strip()
            user = await users.get_or_create(
                chat_id=message.chat.id,
                telegram_user_id=message.from_user.id,  # type: ignore[union-attr]
                username=message.from_user.username,  # type: ignore[union-attr]
                display_name=display_name or (message.from_user.username or "Unknown"),  # type: ignore[union-attr]
            )

            text = message.text.strip()
            await messages.create(
                telegram_message_id=message.message_id,
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                user_id=user.id,
                text=text,
                sent_at=message.date,
                reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None,
                message_length=len(text),
                emoji_count=emoji_count(text),
                uppercase_count=uppercase_count(text),
                has_links=has_link(text),
                has_bad_words=has_bad_words(text),
                metadata_json={"language_code": message.from_user.language_code if message.from_user else None},
            )
            user.total_messages += 1
            self.economy_service.reward_message(user)
            unlocked = await self.achievement_service.evaluate_user(session, user)
            await session.commit()

            if unlocked:
                logger.info("User %s unlocked achievements: %s", user.telegram_user_id, unlocked)
