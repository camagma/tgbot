# Telegram Chat NPC Bot

Асинхронный Telegram-бот для групп, который сохраняет сообщения, анализирует стиль переписки и генерирует локальные мемные фразы как "цифровая сущность чата".

## Stack

- Python 3.12+
- aiogram 3.x
- SQLite
- SQLAlchemy (async)
- APScheduler
- OpenAI API (optional)
- python-dotenv

## Project structure

```text
telegrammbot/
  bot/
    database/
      migrations/
        001_init.sql
        runner.py
      base.py
      models.py
      repositories.py
      session.py
    handlers/
      __init__.py
      common.py
      events.py
      meme.py
    middlewares/
      rate_limit.py
    parser/
      telegram_export_parser.py
    services/
      achievement_service.py
      ai_generator.py
      economy_service.py
      event_reactor.py
      generation_service.py
      markov_generator.py
      message_ingestor.py
      personality.py
      quote_service.py
      scheduler_service.py
      stats_service.py
      style_analyzer.py
    tasks/
      auto_posts.py
      daily_digest.py
    utils/
      text_filters.py
      text_metrics.py
      time_utils.py
    __init__.py
    config.py
    logging_config.py
    main.py
  scripts/
    import_history.py
  .env.example
  docker-compose.yml
  Dockerfile
  requirements.txt
  README.md
```

## Features

- Сбор и хранение групповых сообщений
  - user_id, username, display_name
  - text, date, reply_to
  - message_length, emoji_count, uppercase_count
  - has_links, has_bad_words
- Аналитика чата
  - топ слова/фразы
  - роли: spammer / philosopher / conspiracy theorist / deadline king / nightcore
- Генерация
  - Markov chain (offline)
  - OpenAI-based mode (`/npc ai`)
  - anti-repeat на последнее сгенерированное сообщение
- Personality system
  - sarcastic_archivist
  - sleep_deprived_programmer
  - conspiracy_theorist
  - ancient_ai
  - chaotic_gremlin
- Автопосты и события
  - random interval autopost
  - daily digest
  - night events
  - keyword reactions
- Мемные функции
  - quote rarity
  - lore hooks
  - achievements + XP + coins
- Безопасность
  - rate limit middleware
  - игнор команд при сборе
  - игнор сообщений от ботов
  - защита от recursive reply
- История
  - импорт Telegram export JSON через `scripts/import_history.py`

## Commands

- `/start`, `/help`, `/about`
- `/quote`
- `/lore`
- `/prediction`
- `/chaos`
- `/stats`
- `/nightcore`
- `/ship @user1 @user2`
- `/npc` (Markov)
- `/npc ai` (OpenAI)
- `/mood`
- `/train_stats`

## Inline mode (`@bot`)

После включения inline-режима в BotFather (`/setinline`) бота можно вызывать в любом чате:

- `@your_bot anything` -> генерация из вашей личной базы (chat_id вашего ЛС с ботом)
- `@your_bot chat:-1001234567890` -> генерация из конкретной тренировочной группы
- `@your_bot chat:-1001234567890 ai` -> генерация из группы в AI-режиме
- `@your_bot chat:-1001234567890 thread:42 ai` -> генерация из конкретного топика (thread) в AI-режиме

Рекомендуемый сценарий:

1. Создать приватную "train group".
2. Пересылать туда сообщения из нужных диалогов.
3. Использовать inline-вызов в любом чате с `chat:<train_chat_id>`.

## Local run

1. Установить зависимости:

```bash
pip install -r requirements.txt
```

2. Создать `.env` на основе `.env.example`.

3. Запуск:

```bash
python -m bot.main
```

## Import Telegram history

```bash
python -m scripts.import_history --chat-id -1001234567890 --path ./result.json
```

## Docker

```bash
docker compose up --build -d
```

## Deploy guide

### Render

1. Создать Web Service из репозитория.
2. Build command: `pip install -r requirements.txt`
3. Start command: `python -m bot.main`
4. Добавить env vars из `.env.example`.
5. Persistent disk для `./data` (опционально, но желательно).

### Railway

1. New Project -> Deploy from GitHub.
2. Add variables from `.env.example`.
3. Start command: `python -m bot.main`.
4. Добавить volume или внешний Postgres при масштабировании.

### VPS (systemd)

1. Клонировать проект.
2. Создать venv + установить зависимости.
3. Настроить `.env`.
4. Создать systemd unit:
   - ExecStart: `python -m bot.main`
   - WorkingDirectory: `/srv/telegrammbot`
   - Restart: `always`
5. `sudo systemctl enable --now telegrammbot.service`

## Production notes

- Для high-load лучше заменить SQLite на Postgres.
- Для модерации bad words подключить расширенный словарь/ML-классификатор.
- Для quality AI-generation добавить:
  - prompt templates per personality
  - semantic anti-repeat
  - moderation endpoint before sending.
