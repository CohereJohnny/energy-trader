# Database Setup Guide

## Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ with psycopg2 installed

## Setup Steps

### 1. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` if you want to change default values:
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=energy_trader
DB_USER=postgres
DB_PASSWORD=postgres
```

### 2. Start PostgreSQL Container

```bash
docker-compose up -d postgres
```

This will:
- Start a PostgreSQL 16 container
- Create the database automatically
- Run migrations from `database/migrations/` on first startup
- Expose PostgreSQL on port 5432 (or your configured port)

### 3. Verify Container is Running

```bash
# Docker Compose v1
docker-compose ps

# Docker Compose v2
docker compose ps
```

Check logs:
```bash
# Docker Compose v1
docker-compose logs postgres

# Docker Compose v2
docker compose logs postgres
```

### 4. Verify Database Connection

```bash
# Docker Compose v1
docker-compose exec postgres psql -U postgres -d energy_trader -c "SELECT version();"

# Docker Compose v2
docker compose exec postgres psql -U postgres -d energy_trader -c "SELECT version();"
```

### 5. Run Migration (if not auto-run)

Migrations in `database/migrations/` are automatically run on container startup. If you need to run manually:

```bash
# Docker Compose v1
docker-compose exec postgres psql -U postgres -d energy_trader -f /docker-entrypoint-initdb.d/001_create_futures_prices_schema.sql

# Docker Compose v2
docker compose exec postgres psql -U postgres -d energy_trader -f /docker-entrypoint-initdb.d/001_create_futures_prices_schema.sql
```

Or from host:
```bash
psql -h localhost -p 5432 -U postgres -d energy_trader -f database/migrations/001_create_futures_prices_schema.sql
```

## Helper Scripts

- `./scripts/setup_db.sh` - Start PostgreSQL container and verify setup
- `./scripts/stop_db.sh` - Stop PostgreSQL container
- `./scripts/reset_db.sh` - Remove container and volumes (WARNING: deletes all data)

## Alternative: Local PostgreSQL Setup

If you prefer to run PostgreSQL locally instead of Docker:

### 1. Create Database

```bash
createdb energy_trader
```

Or using psql:
```sql
CREATE DATABASE energy_trader;
```

### 2. Set Environment Variables

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=energy_trader
export DB_USER=postgres
export DB_PASSWORD=postgres
```

### 3. Run Migration

```bash
psql -d energy_trader -f database/migrations/001_create_futures_prices_schema.sql
```

### 4. Install Python Dependencies

```bash
pip install psycopg2-binary
```

### 5. Load Data

```bash
python scripts/load_futures_data.py
```

The script will:
- Parse all CSV files in the `data/` directory
- Extract contract metadata using CME Group month codes
- Load data into normalized tables
- Handle missing/null prices gracefully

## Verification

Check that data loaded correctly:

```sql
-- Check commodity counts
SELECT code, name FROM futures_prices.commodities;

-- Check contract counts per commodity
SELECT c.code, COUNT(DISTINCT ct.id) as contract_count
FROM futures_prices.commodities c
LEFT JOIN futures_prices.contracts ct ON c.id = ct.commodity_id
GROUP BY c.code;

-- Check price counts
SELECT c.code, COUNT(p.id) as price_count
FROM futures_prices.commodities c
JOIN futures_prices.contracts ct ON c.id = ct.commodity_id
JOIN futures_prices.prices p ON ct.id = p.contract_id
GROUP BY c.code;

-- Test front month price lookup
SELECT * FROM futures_prices.get_front_month_price('BRENT', '2010-01-04');
```

## Schema Overview

See `database/schema.md` for detailed schema documentation.

## Troubleshooting

### Connection Errors
- Verify PostgreSQL is running: `pg_isready`
- Check connection parameters match your setup
- Verify database exists: `psql -l | grep energy_trader`

### Data Loading Issues
- Check CSV files exist in `data/` directory
- Verify file permissions
- Check database logs for errors
- Ensure migration ran successfully

