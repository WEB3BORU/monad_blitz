-- Crypto Graves Database Initialization Script

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create enum types
CREATE TYPE loss_status AS ENUM ('pending', 'verified', 'rejected');
CREATE TYPE user_role AS ENUM ('user', 'admin', 'moderator');
CREATE TYPE trade_status AS ENUM ('listed', 'sold', 'cancelled');

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    wallet_address VARCHAR(42) UNIQUE NOT NULL,
    username VARCHAR(100),
    email VARCHAR(255),
    role user_role DEFAULT 'user',
    total_loss DECIMAL(20, 8) DEFAULT 0.0,
    total_gain DECIMAL(20, 8) DEFAULT 0.0,
    profile_image_url TEXT,
    bio TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create losses table
CREATE TABLE IF NOT EXISTS losses (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_uuid UUID NOT NULL REFERENCES users(uuid) ON DELETE CASCADE,
    asset_name VARCHAR(100) NOT NULL,
    asset_ticker VARCHAR(20) NOT NULL,
    loss_amount DECIMAL(20, 8) NOT NULL,
    loss_amount_mon DECIMAL(20, 8) NOT NULL,
    transaction_hash VARCHAR(66) NOT NULL,
    transaction_data JSONB NOT NULL,
    signature TEXT NOT NULL,
    status loss_status DEFAULT 'pending',
    verified_at TIMESTAMP WITH TIME ZONE,
    verified_by INTEGER REFERENCES users(id),
    verified_by_uuid UUID REFERENCES users(uuid),
    nft_token_id INTEGER,
    nft_contract_address VARCHAR(42),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create rankings table
CREATE TABLE IF NOT EXISTS rankings (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_uuid UUID NOT NULL REFERENCES users(uuid) ON DELETE CASCADE,
    period_type VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly'
    period_date DATE NOT NULL,
    total_loss DECIMAL(20, 8) NOT NULL,
    total_gain DECIMAL(20, 8) NOT NULL,
    net_pnl DECIMAL(20, 8) NOT NULL,
    rank_position INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, period_type, period_date)
);

-- Create nfts table
CREATE TABLE IF NOT EXISTS nfts (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    loss_id INTEGER NOT NULL REFERENCES losses(id) ON DELETE CASCADE,
    loss_uuid UUID NOT NULL REFERENCES losses(uuid) ON DELETE CASCADE,
    token_id INTEGER NOT NULL,
    contract_address VARCHAR(42) NOT NULL,
    metadata_uri TEXT,
    image_url TEXT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    attributes JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create trades table
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    seller_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    seller_uuid UUID NOT NULL REFERENCES users(uuid) ON DELETE CASCADE,
    buyer_id INTEGER REFERENCES users(id),
    buyer_uuid UUID REFERENCES users(uuid),
    nft_id INTEGER NOT NULL REFERENCES nfts(id) ON DELETE CASCADE,
    nft_uuid UUID NOT NULL REFERENCES nfts(uuid) ON DELETE CASCADE,
    price DECIMAL(20, 8) NOT NULL,
    status trade_status DEFAULT 'listed',
    transaction_hash VARCHAR(66),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_wallet_address ON users(wallet_address);
CREATE INDEX IF NOT EXISTS idx_users_uuid ON users(uuid);
CREATE INDEX IF NOT EXISTS idx_losses_user_id ON losses(user_id);
CREATE INDEX IF NOT EXISTS idx_losses_user_uuid ON losses(user_uuid);
CREATE INDEX IF NOT EXISTS idx_losses_status ON losses(status);
CREATE INDEX IF NOT EXISTS idx_losses_created_at ON losses(created_at);
CREATE INDEX IF NOT EXISTS idx_losses_uuid ON losses(uuid);
CREATE INDEX IF NOT EXISTS idx_rankings_user_id ON rankings(user_id);
CREATE INDEX IF NOT EXISTS idx_rankings_user_uuid ON rankings(user_uuid);
CREATE INDEX IF NOT EXISTS idx_rankings_period ON rankings(period_type, period_date);
CREATE INDEX IF NOT EXISTS idx_nfts_loss_id ON nfts(loss_id);
CREATE INDEX IF NOT EXISTS idx_nfts_loss_uuid ON nfts(loss_uuid);
CREATE INDEX IF NOT EXISTS idx_nfts_uuid ON nfts(uuid);
CREATE INDEX IF NOT EXISTS idx_trades_seller_id ON trades(seller_id);
CREATE INDEX IF NOT EXISTS idx_trades_seller_uuid ON trades(seller_uuid);
CREATE INDEX IF NOT EXISTS idx_trades_buyer_id ON trades(buyer_id);
CREATE INDEX IF NOT EXISTS idx_trades_buyer_uuid ON trades(buyer_uuid);
CREATE INDEX IF NOT EXISTS idx_trades_nft_id ON trades(nft_id);
CREATE INDEX IF NOT EXISTS idx_trades_nft_uuid ON trades(nft_uuid);
CREATE INDEX IF NOT EXISTS idx_trades_uuid ON trades(uuid);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_losses_updated_at BEFORE UPDATE ON losses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trades_updated_at BEFORE UPDATE ON trades
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (optional)
-- INSERT INTO users (wallet_address, username, role) 
-- VALUES ('0x0000000000000000000000000000000000000000', 'admin', 'admin')
-- ON CONFLICT (wallet_address) DO NOTHING; 