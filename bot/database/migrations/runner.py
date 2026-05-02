from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker


async def run_sql_migrations(session_factory: async_sessionmaker) -> None:
    async with session_factory() as session:
        async with session.begin():
            await session.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        name TEXT PRIMARY KEY,
                        applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            )

            migration_dir = Path(__file__).resolve().parent
            files = sorted(migration_dir.glob("*.sql"))

            for migration_file in files:
                migration_name = migration_file.name
                already_applied = await session.scalar(
                    text("SELECT name FROM schema_migrations WHERE name = :name"),
                    {"name": migration_name},
                )
                if already_applied:
                    continue

                sql = migration_file.read_text(encoding="utf-8")
                chunks = [chunk.strip() for chunk in sql.split(";") if chunk.strip()]
                for chunk in chunks:
                    await session.execute(text(chunk))

                await session.execute(
                    text("INSERT INTO schema_migrations(name) VALUES (:name)"),
                    {"name": migration_name},
                )
