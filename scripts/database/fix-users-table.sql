-- ============================================
-- FIX users TABLE - Add missing columns
-- ============================================

-- Add password_hash column (for local authentication)
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- Add words_used_this_month column (rename from monthly_word_count)
ALTER TABLE users ADD COLUMN IF NOT EXISTS words_used_this_month INTEGER DEFAULT 0;

-- Optional: Remove monthly_word_count if it exists
-- ALTER TABLE users DROP COLUMN IF EXISTS monthly_word_count;

-- Verify columns
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- Create test user
-- Password: Test123! (hashed with bcrypt)
INSERT INTO users (
    email,
    password_hash,
    full_name,
    plan,
    subscription_status,
    words_used_this_month,
    word_limit
) VALUES (
    'test@translatecloud.io',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIIWU6/bMq',  -- Test123!
    'Test User',
    'free',
    'active',
    0,
    5000
)
ON CONFLICT (email) DO UPDATE SET
    password_hash = EXCLUDED.password_hash,
    full_name = EXCLUDED.full_name;

-- Verify test user was created
SELECT id, email, full_name, plan, subscription_status, word_limit
FROM users
WHERE email = 'test@translatecloud.io';
