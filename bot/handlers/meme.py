from random import randint

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.database.repositories import MessageRepository
from bot.services.generation_service import GenerationService
from bot.services.quote_service import QuoteService
from bot.services.stats_service import StatsService

router = Router(name="meme")


@router.message(Command("quote"))
async def quote_handler(message: Message, session_factory, quote_service: QuoteService) -> None:
    async with session_factory() as session:
        quote = await MessageRepository(session).random_quote(
            message.chat.id,
            thread_id=message.message_thread_id,
        )
    if not quote:
        await message.answer("Цитатник еще пуст.")
        return
    rarity = quote_service.rarity_for(quote)
    await message.answer(f"{quote.text}")


@router.message(Command("lore"))
async def lore_handler(message: Message, session_factory) -> None:
    async with session_factory() as session:
        old = await MessageRepository(session).oldest_message(
            message.chat.id,
            thread_id=message.message_thread_id,
        )
    if not old:
        await message.answer("Древний архив пока не найден.")
        return
    await message.answer(f"{old.text}")


@router.message(Command("stats"))
async def stats_handler(message: Message, stats_service: StatsService) -> None:
    roles = await stats_service.archetypes(message.chat.id, thread_id=message.message_thread_id)
    leaders = await stats_service.leaderboard(message.chat.id, thread_id=message.message_thread_id)
    leaderboard = "\n".join([f"- {name}: {msgs} соо, опіта {xp}" for name, msgs, xp in leaders]) or "- no data"
    await message.answer(
        f"спаммеп: {roles['spammer']}\n"
        f"философ: {roles['philosopher']}\n"
        f"ні спід: {roles['night_core']}\n\n"
        f"актівчік:\n{leaderboard}"
    )


@router.message(Command("ship"))
async def ship_handler(message: Message) -> None:
    text = message.text or ""
    parts = text.split()
    if len(parts) < 3:
        await message.answer("Использование: /ship @user1 @user2")
        return
    score = randint(1, 100)
    await message.answer(f"{parts[1]} + {parts[2]} => сходство {score}%")


@router.message(Command("npc"))
async def npc_handler(message: Message, generation_service: GenerationService) -> None:
    text = (message.text or "").lower()
    mode = "ai" if "ai" in text else "markov"
    generated = await generation_service.generate_npc_message(
        message.chat.id,
        mode=mode,
        thread_id=message.message_thread_id,
    )
    await message.answer(generated)


@router.message(Command("train_stats"))
async def train_stats_handler(message: Message, session_factory) -> None:
    async with session_factory() as session:
        total = await MessageRepository(session).count_by_chat(
            message.chat.id,
            thread_id=message.message_thread_id,
        )
    await message.answer(
        f"training messages: {total}\n"
        "рекомендация: 30+ для базового вайба, 100+ для стабильных локальных мемов."
    )


@router.message(F.text.startswith("/"))
async def unknown_command_handler(message: Message) -> None:
    await message.answer("Команда не найдена в этом таймлайне.")
