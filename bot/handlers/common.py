from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="common")


@router.message(Command("start"))
async def start_handler(message: Message) -> None:
    await message.answer(
        "Я вырос внутри этого чата. Сохраняю lore, анализирую хаос и иногда шепчу пророчества.\n"
        "Работаю и в группе, и в личке. Команды: /help /npc /stats /chaos /quote /lore /mood"
    )


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(
        "/quote - случайная цитата\n"
        "/lore - древнее сообщение\n"
        "/stats - роли и активность\n"
        "/ship @u1 @u2 - совместимость\n"
        "/npc марков/гпт - фраза в стиле чата \n"
        "/train_stats - объем обучающей базы"
    )
