-- Migration: Create token_usage table for Token Usage Dashboard
-- Created: 2024-06-01

CREATE TABLE IF NOT EXISTS token_usage (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(128) NOT NULL,
    usage_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    tokens_used INTEGER NOT NULL CHECK (tokens_used >= 0),
    activity VARCHAR(128) NOT NULL,
    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_token_usage_user_id ON token_usage (user_id);
CREATE INDEX IF NOT EXISTS idx_token_usage_usage_time ON token_usage (usage_time);
CREATE INDEX IF NOT EXISTS idx_token_usage_activity ON token_usage (activity);

-- Optional: Table for users if not already present
-- CREATE TABLE IF NOT EXISTS users (
--     id VARCHAR(128) PRIMARY KEY,
--     username VARCHAR(128) UNIQUE NOT NULL,
--     email VARCHAR(256) UNIQUE NOT NULL,
--     password_hash VARCHAR(256) NOT NULL,
--     roles VARCHAR(128)[] NOT NULL DEFAULT ARRAY['user']
-- );