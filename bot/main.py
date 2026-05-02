from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import get_settings
from bot.database.migrations.runner import run_sql_migrations
from bot.database.repositories import PersonalityRepository
from bot.database.session import build_session_factory
from bot.handlers import register_handlers
from bot.logging_config import setup_logging
from bot.middlewares.rate_limit import RateLimitMiddleware
from bot.services.achievement_service import AchievementService
from bot.services.economy_service import EconomyService
from bot.services.event_reactor import EventReactor
from bot.services.generation_service import GenerationService
from bot.services.message_ingestor import MessageIngestor
from bot.services.personality import as_seed_payloads
from bot.services.quote_service import QuoteService
from bot.services.scheduler_service import SchedulerService
from bot.services.stats_service import StatsService


_current_dp: Dispatcher | None = None

async def run_bot() -> None:
    global _current_dp
    settings = get_settings()
    setup_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    session_factory = build_session_factory(settings)
    await run_sql_migrations(session_factory)

    async with session_factory() as session:
        await PersonalityRepository(session).seed_defaults(as_seed_payloads())
        await AchievementService().seed(session)
        await session.commit()

    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    _current_dp = dp
    dp.message.middleware(RateLimitMiddleware())

    generation_service = GenerationService(session_factory, settings)
    stats_service = StatsService(session_factory)
    message_ingestor = MessageIngestor(session_factory, AchievementService(), EconomyService())

    dp["session_factory"] = session_factory
    dp["generation_service"] = generation_service
    dp["stats_service"] = stats_service
    dp["quote_service"] = QuoteService()
    dp["event_reactor"] = EventReactor()
    dp["ingestor"] = message_ingestor

    scheduler = SchedulerService(bot, settings, generation_service, stats_service)
    dp["scheduler_service"] = scheduler
    dp["scheduled_chats"] = set()

    register_handlers(dp)

    logger.info("Bot polling started")
    try:
        await dp.start_polling(bot)
    finally:
        _current_dp = None
        scheduler.shutdown()
        await bot.session.close()

async def stop_bot() -> None:
    global _current_dp
    if _current_dp:
        await _current_dp.stop_polling()


if __name__ == "__main__":
    asyncio.run(run_bot())
