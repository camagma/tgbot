from __future__ import annotations

import logging
from random import randint

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from bot.config import Settings
from bot.services.generation_service import GenerationService
from bot.services.stats_service import StatsService
from bot.tasks.auto_posts import maybe_send_autopost
from bot.tasks.daily_digest import send_daily_digest

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(
        self,
        bot: Bot,
        settings: Settings,
        generation_service: GenerationService,
        stats_service: StatsService,
    ) -> None:
        self.bot = bot
        self.settings = settings
        self.generation_service = generation_service
        self.stats_service = stats_service
        self.scheduler = AsyncIOScheduler()

    def start_for_chat(self, chat_id: int) -> None:
        auto_interval = randint(self.settings.autopost_min_interval_sec, self.settings.autopost_max_interval_sec)
        self.scheduler.add_job(
            maybe_send_autopost,
            IntervalTrigger(seconds=auto_interval),
            kwargs={
                "bot": self.bot,
                "chat_id": chat_id,
                "generation_service": self.generation_service,
                "stats_service": self.stats_service,
                "settings": self.settings,
            },
            id=f"autopost_{chat_id}",
            replace_existing=True,
        )
        self.scheduler.add_job(
            send_daily_digest,
            trigger="cron",
            hour=self.settings.daily_stats_hour_utc,
            kwargs={"bot": self.bot, "chat_id": chat_id, "stats_service": self.stats_service},
            id=f"daily_digest_{chat_id}",
            replace_existing=True,
        )
        self.scheduler.start()
        logger.info("Scheduler initialized for chat_id=%s", chat_id)

    def shutdown(self) -> None:
        self.scheduler.shutdown(wait=False)
