CREATE DATABASE IF NOT EXISTS wealthtracker;
-- ENUMs
CREATE TYPE risk_profile_enum   AS ENUM ('conservative', 'moderate', 'aggressive');
CREATE TYPE kyc_status_enum     AS ENUM ('unverified', 'verified');
CREATE TYPE goal_type_enum      AS ENUM ('retirement', 'home', 'education', 'custom');
CREATE TYPE goal_status_enum    AS ENUM ('active', 'paused', 'completed');
CREATE TYPE asset_type_enum     AS ENUM ('stock', 'etf', 'mutual_fund', 'bond', 'cash');
CREATE TYPE txn_type_enum       AS ENUM ('buy', 'sell', 'dividend', 'contribution', 'withdrawal');

-- ── Users ────────────────────────────────────────────────────
CREATE TABLE users (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(120)        NOT NULL,
    email        VARCHAR(255)        NOT NULL UNIQUE,
    password     VARCHAR(255)        NOT NULL,           -- bcrypt hash
    risk_profile risk_profile_enum   NOT NULL DEFAULT 'moderate',
    kyc_status   kyc_status_enum     NOT NULL DEFAULT 'unverified',
    created_at   TIMESTAMP           NOT NULL DEFAULT NOW()
);

-- ── Goals ────────────────────────────────────────────────────
CREATE TABLE goals (
    id                   SERIAL PRIMARY KEY,
    user_id              INT              NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    goal_type            goal_type_enum   NOT NULL,
    target_amount        NUMERIC(15, 2)   NOT NULL CHECK (target_amount > 0),
    target_date          DATE             NOT NULL,
    monthly_contribution NUMERIC(12, 2)   NOT NULL CHECK (monthly_contribution >= 0),
    status               goal_status_enum NOT NULL DEFAULT 'active',
    created_at           TIMESTAMP        NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_goals_user_id ON goals(user_id);

-- ── Investments ──────────────────────────────────────────────
CREATE TABLE investments (
    id             SERIAL PRIMARY KEY,
    user_id        INT             NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    asset_type     asset_type_enum NOT NULL,
    symbol         VARCHAR(20)     NOT NULL,
    units          NUMERIC(18, 6)  NOT NULL CHECK (units > 0),
    avg_buy_price  NUMERIC(15, 4)  NOT NULL CHECK (avg_buy_price > 0),
    cost_basis     NUMERIC(15, 2)  NOT NULL,
    current_value  NUMERIC(15, 2)  NOT NULL DEFAULT 0,
    last_price     NUMERIC(15, 4)  NOT NULL DEFAULT 0,
    last_price_at  TIMESTAMP
);

CREATE INDEX idx_investments_user_id ON investments(user_id);
CREATE INDEX idx_investments_symbol  ON investments(symbol);

-- ── Transactions ─────────────────────────────────────────────
CREATE TABLE transactions (
    id          SERIAL PRIMARY KEY,
    user_id     INT           NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol      VARCHAR(20)   NOT NULL,
    type        txn_type_enum NOT NULL,
    quantity    NUMERIC(18, 6) NOT NULL,
    price       NUMERIC(15, 4) NOT NULL,
    fees        NUMERIC(10, 2) NOT NULL DEFAULT 0,
    executed_at TIMESTAMP     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_symbol  ON transactions(symbol);

-- ── Recommendations ──────────────────────────────────────────
CREATE TABLE recommendations (
    id                   SERIAL PRIMARY KEY,
    user_id              INT     NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title                VARCHAR(255) NOT NULL,
    recommendation_text  TEXT,
    suggested_allocation JSONB,
    created_at           TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ── Simulations ──────────────────────────────────────────────
CREATE TABLE simulations (
    id            SERIAL PRIMARY KEY,
    user_id       INT          NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    goal_id       INT          REFERENCES goals(id) ON DELETE SET NULL,
    scenario_name VARCHAR(120) NOT NULL,
    assumptions   JSONB,
    results       JSONB,
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ── Seed data (dev only) ─────────────────────────────────────
INSERT INTO users (name, email, password, risk_profile, kyc_status) VALUES
  ('Demo User', 'demo@wealthtracker.dev', '$2b$12$placeholder_hash', 'moderate', 'verified');