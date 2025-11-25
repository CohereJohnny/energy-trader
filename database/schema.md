# Database Schema Design

## Schema: futures_prices

### Overview
Normalized schema for storing futures contract prices. The schema uses three main tables:
- `commodities` - Commodity metadata
- `contracts` - Contract metadata (commodity + expiration)
- `prices` - Daily settlement prices

### Table: commodities
Stores commodity metadata.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| code | VARCHAR(10) | UNIQUE, NOT NULL | Commodity code (BRENT, WTI, GO, RBOB) |
| name | VARCHAR(100) | NOT NULL | Full commodity name |
| exchange | VARCHAR(50) | | Exchange (ICE, NYMEX) |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |

### Table: contracts
Stores contract metadata (commodity + expiration year/month).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| commodity_id | INTEGER | FOREIGN KEY (commodities.id), NOT NULL | Reference to commodity |
| expiration_year | INTEGER | NOT NULL | Expiration year (e.g., 2011) |
| expiration_month | INTEGER | NOT NULL | Expiration month (1-12, derived from CME codes) |
| cme_month_code | CHAR(1) | | CME Group month code (F, G, H, J, K, M, N, Q, U, V, X, Z) |
| expiration_date | DATE | | Calculated expiration date (first business day of month) |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| UNIQUE(commodity_id, expiration_year, expiration_month) | | | Prevent duplicate contracts |

### Table: prices
Stores daily settlement prices for each contract.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Unique identifier |
| contract_id | INTEGER | FOREIGN KEY (contracts.id), NOT NULL | Reference to contract |
| trade_date | DATE | NOT NULL | Trading date |
| settlement_price | NUMERIC(10,2) | | Settlement price (NULL if not available) |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |
| UNIQUE(contract_id, trade_date) | | | One price per contract per day |

### Indexes

**Performance indexes:**
- `idx_prices_trade_date` on `prices(trade_date)` - Fast date range queries
- `idx_prices_contract_trade_date` on `prices(contract_id, trade_date)` - Fast contract+date lookups
- `idx_contracts_commodity_expiration` on `contracts(commodity_id, expiration_year, expiration_month)` - Fast contract lookups
- `idx_contracts_expiration_date` on `contracts(expiration_date)` - Fast expiration date queries

**For front month detection:**
- Composite index on `contracts(commodity_id, expiration_date)` - Efficient front month queries

### Front Month Detection Logic

The front month is the nearest expiring contract for a given commodity that has a valid (non-NULL) price on the trade date.

Algorithm:
1. For a given commodity and trade_date
2. Find all contracts where expiration_date >= trade_date
3. Filter to contracts that have a price on trade_date (settlement_price IS NOT NULL)
4. Order by expiration_date ASC
5. Return the first contract (nearest expiration with price)

This will be implemented as a database function or view for efficient querying.

