import argparse
import asyncio

from bot.config import get_settings
from bot.database.migrations.runner import run_sql_migrations
from bot.database.session import build_session_factory
from bot.parser.telegram_export_parser import import_telegram_export


async def run(chat_id: int, path: str) -> None:
    settings = get_settings()
    factory = build_session_factory(settings)
    await run_sql_migrations(factory)
    imported = await import_telegram_export(factory, path, chat_id)
    print(f"Imported {imported} messages into chat_id={chat_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Telegram export JSON into bot DB")
    parser.add_argument("--chat-id", type=int, required=True)
    parser.add_argument("--path", type=str, required=True)
    args = parser.parse_args()
    asyncio.run(run(args.chat_id, args.path))


if __name__ == "__main__":
    main()
