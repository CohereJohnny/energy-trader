# Database Migrations

This directory contains SQL migration scripts that are automatically executed when the PostgreSQL container starts for the first time.

## Migration Files

- `001_create_futures_prices_schema.sql` - Creates the initial schema with commodities, contracts, and prices tables

## Auto-Execution

When using Docker Compose, migrations in this directory are automatically executed in alphabetical order when the container is first created. The `/docker-entrypoint-initdb.d` directory in the container is mapped to this directory.

## Manual Execution

To run migrations manually:

```bash
# Using Docker Compose
docker-compose exec postgres psql -U postgres -d energy_trader -f /docker-entrypoint-initdb.d/001_create_futures_prices_schema.sql

# Or from host
psql -h localhost -p 5432 -U postgres -d energy_trader -f database/migrations/001_create_futures_prices_schema.sql
```

## Adding New Migrations

1. Create new migration file with format: `XXX_description.sql` (where XXX is sequential number)
2. Place in this directory
3. Migrations will run automatically on next container creation
4. For existing containers, run manually

