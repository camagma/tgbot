from aiogram import Bot

from bot.services.stats_service import StatsService


async def send_daily_digest(bot: Bot, chat_id: int, stats_service: StatsService) -> None:
    archetypes = await stats_service.archetypes(chat_id)
    top_words = await stats_service.top_words(chat_id, limit=5)
    words = ", ".join([f"{word}({count})" for word, count in top_words]) or "тишина"

    text = (
        "[CHAT.DAILY]\n"
        f"spammer: {archetypes['spammer']}\n"
        f"philosopher: {archetypes['philosopher']}\n"
        f"deadline king: {archetypes['deadline_king']}\n"
        f"top words: {words}"
    )
    await bot.send_message(chat_id, text)
