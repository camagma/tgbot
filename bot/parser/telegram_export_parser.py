from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.database.repositories import MessageRepository, UserRepository
from bot.utils.text_filters import has_bad_words, has_link
from bot.utils.text_metrics import emoji_count, uppercase_count


def _flatten_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            if isinstance(item, str):
                chunks.append(item)
            elif isinstance(item, dict):
                chunks.append(item.get("text", ""))
        return "".join(chunks)
    return ""


async def import_telegram_export(session_factory: async_sessionmaker, export_path: str | Path, chat_id: int) -> int:
    payload = json.loads(Path(export_path).read_text(encoding="utf-8"))
    messages = payload.get("messages", [])
    imported = 0

    async with session_factory() as session:
        users = UserRepository(session)
        repo = MessageRepository(session)

        for row in messages:
            if row.get("type") != "message":
                continue
            text = _flatten_text(row.get("text", "")).strip()
            if not text:
                continue

            from_id = row.get("from_id", "user0")
            telegram_user_id = int(str(from_id).replace("user", "") or 0)
            username = row.get("from")
            user = await users.get_or_create(
                chat_id=chat_id,
                telegram_user_id=telegram_user_id,
                username=username,
                display_name=username or "Archived User",
            )
            user.total_messages += 1

            iso_date = row.get("date")
            sent_at = datetime.fromisoformat(iso_date.replace("Z", "+00:00")) if iso_date else datetime.now(timezone.utc)
            await repo.create(
                telegram_message_id=int(row.get("id", 0)),
                chat_id=chat_id,
                user_id=user.id,
                text=text,
                sent_at=sent_at,
                reply_to_message_id=None,
                message_length=len(text),
                emoji_count=emoji_count(text),
                uppercase_count=uppercase_count(text),
                has_links=has_link(text),
                has_bad_words=has_bad_words(text),
                metadata_json={"source": "telegram_export"},
            )
            imported += 1
        await session.commit()
    return imported
