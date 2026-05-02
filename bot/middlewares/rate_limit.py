from __future__ import annotations

from collections import defaultdict
from time import monotonic
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit_per_window: int = 6, window_sec: float = 4.0) -> None:
        self.limit_per_window = limit_per_window
        self.window_sec = window_sec
        self.hits: dict[int, list[float]] = defaultdict(list)

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        user = event.from_user
        if not user:
            return await handler(event, data)

        now = monotonic()
        history = [hit for hit in self.hits[user.id] if now - hit < self.window_sec]
        history.append(now)
        self.hits[user.id] = history

        if len(history) > self.limit_per_window:
            return None
        return await handler(event, data)
