#!/bin/bash
# Stop PostgreSQL container

set -e

echo "🛑 Stopping Energy Trader PostgreSQL database..."

if command -v docker-compose &> /dev/null; then
    docker-compose stop postgres
elif docker compose version &> /dev/null; then
    docker compose stop postgres
else
    echo "❌ Error: docker-compose or docker compose not found"
    exit 1
fi

echo "✓ PostgreSQL container stopped"

