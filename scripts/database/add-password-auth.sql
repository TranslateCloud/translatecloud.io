-- ============================================
-- ADD PASSWORD AUTHENTICATION TO USERS TABLE
-- Migration: Add password_hash column
-- ============================================

-- Add password_hash column to users table
ALTER TABLE users
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- Add words_used_this_month column (rename from monthly_word_count for consistency)
ALTER TABLE users
ADD COLUMN IF NOT EXISTS words_used_this_month INTEGER DEFAULT 0;

-- Add stripe_subscription_id column for Stripe integration
ALTER TABLE users
ADD COLUMN IF NOT EXISTS stripe_subscription_id VARCHAR(255);

-- Add subscription_tier column (separate from plan)
ALTER TABLE users
ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(50) DEFAULT 'free';

-- Make cognito_sub optional (we're using password auth instead)
ALTER TABLE users
ALTER COLUMN cognito_sub DROP NOT NULL;

-- Create index on password_hash for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_password_hash ON users(password_hash);

-- Update existing users to have default values
UPDATE users
SET words_used_this_month = COALESCE(monthly_word_count, 0)
WHERE words_used_this_month IS NULL;

UPDATE users
SET subscription_tier = plan
WHERE subscription_tier = 'free' OR subscription_tier IS NULL;

-- Add Stripe customer ID
ALTER TABLE users
ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255);

-- Add subscription status
ALTER TABLE users
ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(50) DEFAULT 'active';

-- Add email verification columns
ALTER TABLE users
ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;

ALTER TABLE users
ADD COLUMN IF NOT EXISTS verification_token VARCHAR(255);

ALTER TABLE users
ADD COLUMN IF NOT EXISTS verification_token_expires TIMESTAMP;

-- Add timestamps
ALTER TABLE users
ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

ALTER TABLE users
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();

-- Create additional indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_stripe_customer ON users(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_users_verification_token ON users(verification_token);

-- Comments
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hashed password for authentication';
COMMENT ON COLUMN users.words_used_this_month IS 'Word count used in current billing period';
COMMENT ON COLUMN users.stripe_subscription_id IS 'Stripe subscription ID for paid plans';
COMMENT ON COLUMN users.subscription_tier IS 'Current subscription tier (free, professional, business, enterprise)';
COMMENT ON COLUMN users.email_verified IS 'Whether user has verified their email address';
COMMENT ON COLUMN users.verification_token IS 'Token for email verification (expires in 24 hours)';
