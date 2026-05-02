CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    username VARCHAR(128),
    display_name VARCHAR(256) NOT NULL,
    total_messages INTEGER DEFAULT 0,
    xp INTEGER DEFAULT 0,
    coins INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_chat UNIQUE (telegram_user_id, chat_id)
);

CREATE INDEX IF NOT EXISTS ix_users_chat_id ON users (chat_id);
CREATE INDEX IF NOT EXISTS ix_users_telegram_user_id ON users (telegram_user_id);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_message_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    user_id INTEGER,
    text TEXT NOT NULL,
    sent_at DATETIME NOT NULL,
    reply_to_message_id BIGINT,
    message_length INTEGER NOT NULL,
    emoji_count INTEGER NOT NULL,
    uppercase_count INTEGER NOT NULL,
    has_links INTEGER DEFAULT 0,
    has_bad_words INTEGER DEFAULT 0,
    metadata_json JSON,
    FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT uq_message_chat UNIQUE (telegram_message_id, chat_id)
);

CREATE INDEX IF NOT EXISTS ix_messages_chat_id ON messages (chat_id);
CREATE INDEX IF NOT EXISTS ix_messages_sent_at ON messages (sent_at);

CREATE TABLE IF NOT EXISTS chat_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id BIGINT NOT NULL,
    key VARCHAR(64) NOT NULL,
    value TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_chat_stats_chat_id ON chat_stats (chat_id);
CREATE INDEX IF NOT EXISTS ix_chat_stats_key ON chat_stats (key);

CREATE TABLE IF NOT EXISTS generated_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id BIGINT NOT NULL,
    text TEXT NOT NULL,
    generation_mode VARCHAR(32) NOT NULL,
    personality_code VARCHAR(64) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bot_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id BIGINT NOT NULL UNIQUE,
    personality_code VARCHAR(64) DEFAULT 'chaotic_gremlin',
    autopost_cooldown_until DATETIME,
    anti_repeat_last_text TEXT,
    mood VARCHAR(64) DEFAULT 'neutral'
);

CREATE TABLE IF NOT EXISTS personalities (
    code VARCHAR(64) PRIMARY KEY,
    title VARCHAR(128) NOT NULL,
    system_prompt TEXT NOT NULL,
    post_frequency_bias INTEGER DEFAULT 1,
    lexicon_json JSON
);

CREATE TABLE IF NOT EXISTS achievements (
    code VARCHAR(64) PRIMARY KEY,
    title VARCHAR(128) NOT NULL,
    description TEXT NOT NULL,
    rarity VARCHAR(32) DEFAULT 'common'
);

CREATE TABLE IF NOT EXISTS user_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    achievement_code VARCHAR(64) NOT NULL,
    awarded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (achievement_code) REFERENCES achievements (code)
);

CREATE TABLE IF NOT EXISTS lore_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id BIGINT NOT NULL,
    title VARCHAR(128) NOT NULL,
    body TEXT NOT NULL,
    rarity VARCHAR(32) DEFAULT 'common',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
