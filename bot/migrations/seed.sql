-- Seed data for local development
-- Run via Supabase SQL editor after applying 001_initial_schema.sql

INSERT INTO users (telegram_id, is_active)
VALUES (123456789, true)
ON CONFLICT (telegram_id) DO NOTHING;

INSERT INTO profiles (
    user_id,
    goal_areas,
    why_text,
    path_a,
    path_b,
    accomplishments,
    brief_hour,
    brief_minute,
    timezone
)
SELECT
    id,
    '[
        {"name":"Career Transition","description":"Move from corporate SWE to startup product engineer","weekly_hours":10,"color_emoji":"🟦"},
        {"name":"Side Project","description":"Build and ship Meridian to 100 users","weekly_hours":5,"color_emoji":"🟩"}
    ]'::jsonb,
    'What I''m building toward: Leave the corporate job and build a product that reaches 10,000 people.

My life on current path: Still writing Jira tickets at 35, watching others ship what I imagined. Comfortable, well-paid, and quietly frustrated.

What the hard path unlocks: Financial ownership, the satisfaction of betting on myself, and proof that the peak performance I showed in exams was not a one-off.',
    'Still in the same role at 34. The side project never left Notion. I got comfortable somewhere along the way.',
    'I shipped it. The side project became the main thing. I remember exactly which morning I decided to stop waiting.',
    '["Studied 10 hours daily for board exams and topped the school","Built and deployed a full-stack web app in 2 weeks from scratch"]'::jsonb,
    7,
    0,
    'Asia/Kolkata'
FROM users
WHERE telegram_id = 123456789
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO streaks (user_id, current_streak, longest_streak, last_active_date)
SELECT id, 3, 3, CURRENT_DATE - INTERVAL '1 day'
FROM users
WHERE telegram_id = 123456789
ON CONFLICT (user_id) DO NOTHING;
