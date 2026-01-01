-- Crypto Sniper Database Initialization Script
-- This script runs automatically on first PostgreSQL container start

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- Users Table
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_address VARCHAR(42) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    settings JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_users_wallet ON users(wallet_address);

-- ============================================================
-- Auth Nonces (for wallet signature auth)
-- ============================================================
CREATE TABLE IF NOT EXISTS auth_nonces (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_address VARCHAR(42) NOT NULL,
    nonce VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT false
);

CREATE INDEX idx_nonces_wallet ON auth_nonces(wallet_address);
CREATE INDEX idx_nonces_expires ON auth_nonces(expires_at);

-- ============================================================
-- Portfolios
-- ============================================================
CREATE TABLE IF NOT EXISTS portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    network VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_portfolios_user ON portfolios(user_id);

-- ============================================================
-- Allocation Targets
-- ============================================================
CREATE TABLE IF NOT EXISTS allocation_targets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
    token_address VARCHAR(42) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    target_percent DECIMAL(5,2) NOT NULL,
    min_percent DECIMAL(5,2),
    max_percent DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_allocations_portfolio ON allocation_targets(portfolio_id);

-- ============================================================
-- Transactions Log
-- ============================================================
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    tx_hash VARCHAR(66) UNIQUE NOT NULL,
    network VARCHAR(20) NOT NULL,
    tx_type VARCHAR(50) NOT NULL,
    from_address VARCHAR(42) NOT NULL,
    to_address VARCHAR(42),
    value_wei VARCHAR(78),
    gas_used INTEGER,
    gas_price_wei VARCHAR(78),
    status VARCHAR(20),
    block_number BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_tx_user ON transactions(user_id);
CREATE INDEX idx_tx_hash ON transactions(tx_hash);
CREATE INDEX idx_tx_network ON transactions(network);

-- ============================================================
-- Staking Positions
-- ============================================================
CREATE TABLE IF NOT EXISTS staking_positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    protocol VARCHAR(100) NOT NULL,
    pool_id VARCHAR(100) NOT NULL,
    network VARCHAR(20) NOT NULL,
    staked_amount DECIMAL(36,18) NOT NULL,
    staked_token VARCHAR(42) NOT NULL,
    entry_price DECIMAL(36,18),
    lock_end TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_staking_user ON staking_positions(user_id);
CREATE INDEX idx_staking_protocol ON staking_positions(protocol);

-- ============================================================
-- MultiSig Wallets
-- ============================================================
CREATE TABLE IF NOT EXISTS multisig_wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    address VARCHAR(42) UNIQUE NOT NULL,
    name VARCHAR(100),
    network VARCHAR(20) NOT NULL,
    owners TEXT[] NOT NULL,
    threshold INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_multisig_address ON multisig_wallets(address);

-- ============================================================
-- MultiSig Proposals
-- ============================================================
CREATE TABLE IF NOT EXISTS multisig_proposals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_id UUID REFERENCES multisig_wallets(id) ON DELETE CASCADE,
    proposer VARCHAR(42) NOT NULL,
    to_address VARCHAR(42) NOT NULL,
    value_wei VARCHAR(78) DEFAULT '0',
    data TEXT,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    signatures TEXT[] DEFAULT '{}',
    signers TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP WITH TIME ZONE,
    tx_hash VARCHAR(66)
);

CREATE INDEX idx_proposals_wallet ON multisig_proposals(wallet_id);
CREATE INDEX idx_proposals_status ON multisig_proposals(status);

-- ============================================================
-- Price History (for analytics)
-- ============================================================
CREATE TABLE IF NOT EXISTS price_history (
    id BIGSERIAL PRIMARY KEY,
    token_address VARCHAR(42) NOT NULL,
    network VARCHAR(20) NOT NULL,
    price_usd DECIMAL(36,18) NOT NULL,
    volume_24h DECIMAL(36,18),
    market_cap DECIMAL(36,18),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_price_token ON price_history(token_address, network);
CREATE INDEX idx_price_timestamp ON price_history(timestamp);

-- ============================================================
-- Rate Limiting
-- ============================================================
CREATE TABLE IF NOT EXISTS rate_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id VARCHAR(100) NOT NULL,
    endpoint VARCHAR(200),
    request_count INTEGER DEFAULT 0,
    window_start TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(client_id, endpoint)
);

CREATE INDEX idx_rate_client ON rate_limits(client_id);

-- ============================================================
-- Cleanup job for expired data
-- ============================================================
CREATE OR REPLACE FUNCTION cleanup_expired_nonces() RETURNS void AS $$
BEGIN
    DELETE FROM auth_nonces WHERE expires_at < CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sniper;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sniper;
