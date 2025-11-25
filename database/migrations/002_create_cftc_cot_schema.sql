-- Migration: Create CFTC COT schema
-- Description: Creates schema for storing CFTC Disaggregated Commitment of Traders data
-- Date: 2025-01-20

-- Create schema
CREATE SCHEMA IF NOT EXISTS cftc_cot;

-- Set search path
SET search_path TO cftc_cot;

-- Reports table: Track report metadata
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    report_type VARCHAR(50) NOT NULL, -- 'disaggregated_futures_options'
    format VARCHAR(20) NOT NULL, -- 'long' or 'short'
    source_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(report_date, report_type, format)
);

-- Markets table: Store market/exchange information
CREATE TABLE markets (
    id SERIAL PRIMARY KEY,
    cftc_code VARCHAR(20) UNIQUE NOT NULL, -- CFTC contract market code (e.g., '02141B')
    market_name VARCHAR(200) NOT NULL,
    exchange VARCHAR(100) NOT NULL, -- Exchange name (e.g., 'ICE FUTURES ENERGY DIV')
    commodity_group VARCHAR(50), -- 'Petroleum and Products', 'Natural Gas and Products', 'Electricity'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Trader categories table: Reference table for trader categories
CREATE TABLE trader_categories (
    id SERIAL PRIMARY KEY,
    category_code VARCHAR(50) UNIQUE NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    category_type VARCHAR(50), -- 'commercial', 'non-commercial', 'nonreportable'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert trader categories
INSERT INTO trader_categories (category_code, category_name, category_type) VALUES
    ('PRODUCER', 'Producer/Merchant/Processor/User', 'commercial'),
    ('SWAP', 'Swap Dealers', 'commercial'),
    ('MANAGED_MONEY', 'Managed Money', 'non-commercial'),
    ('OTHER_REPORTABLE', 'Other Reportables', 'non-commercial'),
    ('NONREPORTABLE', 'Nonreportable Positions', NULL)
ON CONFLICT (category_code) DO NOTHING;

-- Positions table: Store position data for each commodity/report/category
CREATE TABLE positions (
    id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    market_id INTEGER NOT NULL REFERENCES markets(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES trader_categories(id) ON DELETE CASCADE,
    position_type VARCHAR(10) NOT NULL, -- 'all' (Futures+Options), 'old' (Futures only), 'other' (Options only)
    long_positions BIGINT,
    short_positions BIGINT,
    spreading_positions BIGINT, -- NULL for categories that don't have spreading
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(report_id, market_id, category_id, position_type)
);

-- Changes table: Store week-over-week changes
CREATE TABLE changes (
    id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    market_id INTEGER NOT NULL REFERENCES markets(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES trader_categories(id) ON DELETE CASCADE,
    change_open_interest INTEGER, -- Change in Open Interest
    change_long INTEGER,
    change_short INTEGER,
    change_spreading INTEGER, -- NULL for categories that don't have spreading
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(report_id, market_id, category_id)
);

-- Percentages table: Store percentage of Open Interest
CREATE TABLE percentages (
    id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    market_id INTEGER NOT NULL REFERENCES markets(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES trader_categories(id) ON DELETE CASCADE,
    position_type VARCHAR(10) NOT NULL, -- 'all', 'old', 'other'
    pct_long DECIMAL(5,2), -- Percentage of Open Interest
    pct_short DECIMAL(5,2),
    pct_spreading DECIMAL(5,2), -- NULL for categories that don't have spreading
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(report_id, market_id, category_id, position_type)
);

-- Trader counts table: Store number of traders in each category
CREATE TABLE trader_counts (
    id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    market_id INTEGER NOT NULL REFERENCES markets(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES trader_categories(id) ON DELETE CASCADE,
    position_type VARCHAR(10) NOT NULL, -- 'all', 'old', 'other'
    num_traders_long INTEGER,
    num_traders_short INTEGER,
    num_traders_spreading INTEGER, -- NULL for categories that don't have spreading
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(report_id, market_id, category_id, position_type)
);

-- Concentration table: Store concentration data (largest traders)
CREATE TABLE concentration (
    id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    market_id INTEGER NOT NULL REFERENCES markets(id) ON DELETE CASCADE,
    position_type VARCHAR(10) NOT NULL, -- 'all', 'old', 'other'
    -- Gross position concentration
    gross_4_long DECIMAL(5,2), -- % held by 4 or less traders (Long)
    gross_4_short DECIMAL(5,2), -- % held by 4 or less traders (Short)
    gross_8_long DECIMAL(5,2), -- % held by 8 or less traders (Long)
    gross_8_short DECIMAL(5,2), -- % held by 8 or less traders (Short)
    -- Net position concentration
    net_4_long DECIMAL(5,2), -- % held by 4 or less traders (Net Long)
    net_4_short DECIMAL(5,2), -- % held by 4 or less traders (Net Short)
    net_8_long DECIMAL(5,2), -- % held by 8 or less traders (Net Long)
    net_8_short DECIMAL(5,2), -- % held by 8 or less traders (Net Short)
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(report_id, market_id, position_type)
);

-- Open interest table: Store Open Interest for each commodity/report
CREATE TABLE open_interest (
    id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    market_id INTEGER NOT NULL REFERENCES markets(id) ON DELETE CASCADE,
    position_type VARCHAR(10) NOT NULL, -- 'all', 'old', 'other'
    open_interest BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(report_id, market_id, position_type)
);

-- Loading log table: Track data loading progress
CREATE TABLE loading_log (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    format VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'pending', 'downloading', 'parsing', 'loading', 'completed', 'failed'
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    records_loaded INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(report_date, report_type, format)
);

-- Create indexes for common queries
CREATE INDEX idx_reports_date ON reports(report_date);
CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_markets_code ON markets(cftc_code);
CREATE INDEX idx_markets_group ON markets(commodity_group);
CREATE INDEX idx_positions_report_market ON positions(report_id, market_id);
CREATE INDEX idx_positions_category ON positions(category_id);
CREATE INDEX idx_changes_report_market ON changes(report_id, market_id);
CREATE INDEX idx_percentages_report_market ON percentages(report_id, market_id);
CREATE INDEX idx_trader_counts_report_market ON trader_counts(report_id, market_id);
CREATE INDEX idx_concentration_report_market ON concentration(report_id, market_id);
CREATE INDEX idx_open_interest_report_market ON open_interest(report_id, market_id);
CREATE INDEX idx_loading_log_status ON loading_log(status);
CREATE INDEX idx_loading_log_date ON loading_log(report_date);

-- Create updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_reports_updated_at BEFORE UPDATE ON reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_markets_updated_at BEFORE UPDATE ON markets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_positions_updated_at BEFORE UPDATE ON positions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_loading_log_updated_at BEFORE UPDATE ON loading_log
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create view for easy querying of complete position data
CREATE OR REPLACE VIEW position_summary AS
SELECT 
    r.report_date,
    m.market_name,
    m.exchange,
    m.cftc_code,
    m.commodity_group,
    tc.category_name,
    p.position_type,
    p.long_positions,
    p.short_positions,
    p.spreading_positions,
    oi.open_interest,
    ch.change_open_interest,
    ch.change_long,
    ch.change_short,
    ch.change_spreading,
    pct.pct_long,
    pct.pct_short,
    pct.pct_spreading,
    tc_counts.num_traders_long,
    tc_counts.num_traders_short,
    tc_counts.num_traders_spreading
FROM positions p
JOIN reports r ON p.report_id = r.id
JOIN markets m ON p.market_id = m.id
JOIN trader_categories tc ON p.category_id = tc.id
LEFT JOIN open_interest oi ON oi.report_id = r.id AND oi.market_id = m.id AND oi.position_type = p.position_type
LEFT JOIN changes ch ON ch.report_id = r.id AND ch.market_id = m.id AND ch.category_id = tc.id
LEFT JOIN percentages pct ON pct.report_id = r.id AND pct.market_id = m.id AND pct.category_id = tc.id AND pct.position_type = p.position_type
LEFT JOIN trader_counts tc_counts ON tc_counts.report_id = r.id AND tc_counts.market_id = m.id AND tc_counts.category_id = tc.id AND tc_counts.position_type = p.position_type;

