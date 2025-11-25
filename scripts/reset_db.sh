#!/bin/bash
# Reset PostgreSQL database (removes container and volumes)

set -e

echo "⚠️  WARNING: This will remove the PostgreSQL container and all data!"
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

echo "🗑️  Removing PostgreSQL container and volumes..."

if command -v docker-compose &> /dev/null; then
    docker-compose down -v postgres
elif docker compose version &> /dev/null; then
    docker compose down -v postgres
else
    echo "❌ Error: docker-compose or docker compose not found"
    exit 1
fi

echo "✓ Database reset complete"
echo ""
echo "To start fresh, run: ./scripts/setup_db.sh"

