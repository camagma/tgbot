from __future__ import annotations

from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from bot.services.generation_service import GenerationService

router = Router(name="inline")


def _parse_inline_query(query_text: str, fallback_user_id: int) -> tuple[int, int | None, str]:
    text = (query_text or "").strip()
    tokens = text.split()

    source_chat_id = fallback_user_id
    source_thread_id: int | None = None
    mode = "markov"

    for token in tokens:
        lowered = token.lower()
        if lowered == "ai":
            mode = "ai"
            continue
        if lowered.startswith("chat:"):
            raw_chat = lowered.replace("chat:", "").strip()
            if raw_chat.lstrip("-").isdigit():
                source_chat_id = int(raw_chat)
            continue
        if lowered.startswith("thread:"):
            raw_thread = lowered.replace("thread:", "").strip()
            if raw_thread.isdigit():
                source_thread_id = int(raw_thread)

    return source_chat_id, source_thread_id, mode


@router.inline_query()
async def inline_generate(query: InlineQuery, generation_service: GenerationService) -> None:
    source_chat_id, source_thread_id, mode = _parse_inline_query(query.query, query.from_user.id)

    generated = await generation_service.generate_npc_message(
        source_chat_id,
        mode=mode,
        thread_id=source_thread_id,
    )
    prefix = f"[inline/{mode}]"
    scope = f"Source chat: {source_chat_id}"
    if source_thread_id is not None:
        scope += f", thread: {source_thread_id}"

    result = InlineQueryResultArticle(
        id=f"{query.id}-{mode}",
        title="Generate NPC phrase",
        description=scope,
        input_message_content=InputTextMessageContent(message_text=f"{prefix} {generated}"),
    )
    await query.answer([result], cache_time=3, is_personal=True)
