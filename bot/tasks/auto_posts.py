from random import randint

from aiogram import Bot

from bot.config import Settings
from bot.services.generation_service import GenerationService
from bot.services.stats_service import StatsService
from bot.utils.time_utils import utc_now


async def maybe_send_autopost(
    bot: Bot,
    chat_id: int,
    generation_service: GenerationService,
    stats_service: StatsService,
    settings: Settings,
) -> None:
    if not settings.autopost_enabled:
        return

    recent_messages = await stats_service.chaos_level(chat_id)
    if recent_messages < 10 and randint(1, 100) > 18:
        return

    if utc_now().hour <= 4 and randint(1, 100) > 65:
        await bot.send_message(chat_id, "03:42 detected. Productivity demon online.")
        return

    mode = "ai" if randint(1, 100) > 67 else "markov"
    text = await generation_service.generate_npc_message(chat_id, mode=mode)
    await bot.send_message(chat_id, text)
