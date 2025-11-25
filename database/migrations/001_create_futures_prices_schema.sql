-- Migration: Create futures_prices schema
-- Description: Creates the normalized schema for storing futures contract prices
-- Date: 2025-01-20

-- Create schema
CREATE SCHEMA IF NOT EXISTS futures_prices;

-- Set search path
SET search_path TO futures_prices;

-- Create commodities table
CREATE TABLE commodities (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    exchange VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create contracts table
CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    commodity_id INTEGER NOT NULL REFERENCES commodities(id) ON DELETE CASCADE,
    expiration_year INTEGER NOT NULL,
    expiration_month INTEGER NOT NULL CHECK (expiration_month >= 1 AND expiration_month <= 12),
    cme_month_code CHAR(1),
    expiration_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_contract UNIQUE (commodity_id, expiration_year, expiration_month)
);

-- Create prices table
CREATE TABLE prices (
    id BIGSERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    trade_date DATE NOT NULL,
    settlement_price NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_price UNIQUE (contract_id, trade_date)
);

-- Create indexes for performance
CREATE INDEX idx_prices_trade_date ON prices(trade_date);
CREATE INDEX idx_prices_contract_trade_date ON prices(contract_id, trade_date);
CREATE INDEX idx_contracts_commodity_expiration ON contracts(commodity_id, expiration_year, expiration_month);
CREATE INDEX idx_contracts_expiration_date ON contracts(expiration_date);
CREATE INDEX idx_contracts_commodity_expiration_date ON contracts(commodity_id, expiration_date);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER update_commodities_updated_at BEFORE UPDATE ON commodities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prices_updated_at BEFORE UPDATE ON prices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create view for front month prices
-- Front month is the nearest expiring contract with a valid price on the trade date
CREATE OR REPLACE VIEW futures_prices.front_month_prices AS
SELECT DISTINCT ON (p.trade_date, c.commodity_id)
    p.trade_date,
    c.commodity_id,
    com.code AS commodity_code,
    c.id AS contract_id,
    c.expiration_year,
    c.expiration_month,
    c.expiration_date,
    p.settlement_price,
    p.id AS price_id
FROM futures_prices.prices p
JOIN futures_prices.contracts c ON p.contract_id = c.id
JOIN futures_prices.commodities com ON c.commodity_id = com.id
WHERE p.settlement_price IS NOT NULL
    AND c.expiration_date >= p.trade_date
ORDER BY p.trade_date, c.commodity_id, c.expiration_date ASC;

-- Create function to get front month price for a commodity and date
CREATE OR REPLACE FUNCTION get_front_month_price(
    p_commodity_code VARCHAR(10),
    p_trade_date DATE
)
RETURNS TABLE (
    trade_date DATE,
    commodity_code VARCHAR(10),
    contract_id INTEGER,
    expiration_year INTEGER,
    expiration_month INTEGER,
    expiration_date DATE,
    settlement_price NUMERIC(10,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        fmp.trade_date,
        fmp.commodity_code,
        fmp.contract_id,
        fmp.expiration_year,
        fmp.expiration_month,
        fmp.expiration_date,
        fmp.settlement_price
    FROM futures_prices.front_month_prices fmp
    WHERE fmp.commodity_code = p_commodity_code
        AND fmp.trade_date = p_trade_date
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Insert initial commodities
INSERT INTO commodities (code, name, exchange) VALUES
    ('BRENT', 'Brent Crude Oil', 'ICE'),
    ('WTI', 'West Texas Intermediate', 'NYMEX'),
    ('GO', 'Gas Oil', 'ICE'),
    ('RBOB', 'Reformulated Blendstock for Oxygenate Blending', 'NYMEX')
ON CONFLICT (code) DO NOTHING;

