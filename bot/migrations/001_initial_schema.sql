-- Meridian initial schema
-- Run via Supabase SQL editor or: supabase db push

-- ─── Enum ────────────────────────────────────────────────────────────────────

CREATE TYPE framing_type AS ENUM ('fear', 'aspiration', 'accomplishment', 'urgency');

-- ─── Tables ──────────────────────────────────────────────────────────────────

CREATE TABLE users (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id bigint      UNIQUE NOT NULL,
    created_at  timestamptz DEFAULT now(),
    is_active   boolean     DEFAULT true
);

CREATE TABLE profiles (
    user_id          uuid    PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    goal_areas       jsonb   NOT NULL DEFAULT '[]',
    why_text         text    NOT NULL DEFAULT '',
    path_a           text    NOT NULL DEFAULT '',
    path_b           text    NOT NULL DEFAULT '',
    accomplishments  jsonb   NOT NULL DEFAULT '[]',
    brief_hour       integer NOT NULL CHECK (brief_hour BETWEEN 0 AND 23),
    brief_minute     integer NOT NULL DEFAULT 0 CHECK (brief_minute BETWEEN 0 AND 59),
    timezone         text    NOT NULL DEFAULT 'Asia/Kolkata',
    updated_at       timestamptz DEFAULT now()
);

CREATE TABLE daily_logs (
    id                      uuid    PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 uuid    NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date                    date    NOT NULL,
    blocks                  jsonb   NOT NULL DEFAULT '[]',
    completed_block_indices integer[] DEFAULT '{}',
    skipped_block_indices   integer[] DEFAULT '{}',
    framing_type            text    NOT NULL,
    brief_sent_at           timestamptz,
    UNIQUE (user_id, date)
);

CREATE TABLE streaks (
    user_id          uuid PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    current_streak   integer DEFAULT 0,
    longest_streak   integer DEFAULT 0,
    last_active_date date
);

-- ─── Indexes ─────────────────────────────────────────────────────────────────

CREATE INDEX idx_users_telegram_id    ON users (telegram_id);
CREATE INDEX idx_daily_logs_user_date ON daily_logs (user_id, date DESC);

-- ─── Row Level Security ───────────────────────────────────────────────────────
-- All bot and web server operations use the service role key, which bypasses RLS
-- automatically. These policies define the intended access model for any future
-- Supabase Auth integration and prevent direct anon API access.

ALTER TABLE users      ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles   ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE streaks    ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_own_row"       ON users      FOR ALL USING (auth.uid() = id);
CREATE POLICY "profiles_own_row"    ON profiles   FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "daily_logs_own_rows" ON daily_logs FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "streaks_own_row"     ON streaks    FOR ALL USING (auth.uid() = user_id);
