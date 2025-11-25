#!/bin/bash
# Setup script for containerized PostgreSQL database

set -e

echo "🚀 Setting up Energy Trader PostgreSQL database..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ Created .env file (you may want to edit it)"
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Start PostgreSQL container
echo "🐳 Starting PostgreSQL container..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d postgres
elif docker compose version &> /dev/null; then
    docker compose up -d postgres
else
    echo "❌ Error: docker-compose or docker compose not found"
    exit 1
fi

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Check if container is running
if docker ps | grep -q energy-trader-db; then
    echo "✓ PostgreSQL container is running"
else
    echo "❌ Error: Container failed to start. Check logs with: docker-compose logs postgres"
    exit 1
fi

# Verify connection
echo "🔍 Verifying database connection..."
if docker exec energy-trader-db pg_isready -U postgres > /dev/null 2>&1; then
    echo "✓ Database is ready!"
    echo ""
    echo "📊 Database Information:"
    echo "  Host: localhost"
    echo "  Port: 5432 (or check .env)"
    echo "  Database: energy_trader"
    echo "  User: postgres"
    echo ""
    echo "Next steps:"
    echo "  1. Run migrations (if not auto-run): docker-compose exec postgres psql -U postgres -d energy_trader -f /docker-entrypoint-initdb.d/001_create_futures_prices_schema.sql"
    echo "  2. Load data: python scripts/load_futures_data.py"
    echo ""
    echo "Useful commands:"
    echo "  View logs: docker-compose logs -f postgres"
    echo "  Stop: docker-compose stop postgres"
    echo "  Remove: docker-compose down -v"
else
    echo "⚠️  Warning: Database may not be fully ready yet. Wait a few seconds and check with:"
    echo "   docker exec energy-trader-db pg_isready -U postgres"
fi

