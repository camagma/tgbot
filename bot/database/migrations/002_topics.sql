ALTER TABLE messages ADD COLUMN message_thread_id BIGINT;
CREATE INDEX IF NOT EXISTS ix_messages_message_thread_id ON messages (message_thread_id);

ALTER TABLE generated_messages ADD COLUMN message_thread_id BIGINT;
CREATE INDEX IF NOT EXISTS ix_generated_messages_message_thread_id ON generated_messages (message_thread_id);
