from aiogram import F, Router
from aiogram.types import Message

from bot.services.event_reactor import EventReactor
from bot.services.message_ingestor import MessageIngestor
from bot.services.scheduler_service import SchedulerService

router = Router(name="events")


@router.message(F.chat.type.in_({"group", "supergroup"}), F.text)
async def collect_and_react_group(
    message: Message,
    ingestor: MessageIngestor,
    event_reactor: EventReactor,
    scheduler_service: SchedulerService,
    scheduled_chats: set[int],
) -> None:
    if message.chat.id not in scheduled_chats:
        scheduler_service.start_for_chat(message.chat.id)
        scheduled_chats.add(message.chat.id)

    await ingestor.ingest(message)

    if message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.is_bot:
        return

    reaction = event_reactor.react(message.text or "")
    if reaction:
        await message.answer(reaction)


@router.message(F.chat.type == "private", F.text)
async def collect_and_react_private(
    message: Message,
    ingestor: MessageIngestor,
    event_reactor: EventReactor,
) -> None:
    await ingestor.ingest(message)

    # Private mode should feel alive, but without aggressive spam behavior.
    if message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.is_bot:
        return

    reaction = event_reactor.react(message.text or "")
    if reaction and "anomaly detected" in reaction.lower():
        await message.answer(reaction)
