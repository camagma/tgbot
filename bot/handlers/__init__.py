from aiogram import Dispatcher

from bot.handlers.common import router as common_router
from bot.handlers.events import router as events_router
from bot.handlers.inline import router as inline_router
from bot.handlers.meme import router as meme_router


def register_handlers(dp: Dispatcher) -> None:
    dp.include_router(common_router)
    dp.include_router(meme_router)
    dp.include_router(events_router)
    dp.include_router(inline_router)
