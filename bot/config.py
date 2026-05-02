from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = Field(alias="BOT_TOKEN")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")
    database_url: str = Field(default="sqlite+aiosqlite:///./data/bot.db", alias="DATABASE_URL")
    default_personality: str = Field(default="chaotic_gremlin", alias="DEFAULT_PERSONALITY")
    autopost_enabled: bool = Field(default=True, alias="AUTOPOST_ENABLED")
    autopost_min_interval_sec: int = Field(default=900, alias="AUTOPOST_MIN_INTERVAL_SEC")
    autopost_max_interval_sec: int = Field(default=3600, alias="AUTOPOST_MAX_INTERVAL_SEC")
    daily_stats_hour_utc: int = Field(default=19, alias="DAILY_STATS_HOUR_UTC")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
