#!/bin/bash
# Setup script for OCI VM - Install Docker and PostgreSQL container
# This script sets up a production-ready PostgreSQL database with auto-restart

set -e

echo "🚀 Setting up Energy Trader Database on OCI VM..."
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script requires sudo privileges. Please run with sudo."
    exit 1
fi

# Step 1: Install Docker
echo "📦 Step 1: Installing Docker..."
if command -v docker &> /dev/null; then
    echo "✓ Docker is already installed"
    docker --version
else
    echo "Installing Docker..."
    apt-get update
    apt-get install -y ca-certificates curl gnupg lsb-release
    
    # Add Docker's official GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    
    # Set up Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    echo "✓ Docker installed successfully"
    docker --version
fi

# Step 2: Install Docker Compose (if not already installed)
echo ""
echo "📦 Step 2: Checking Docker Compose..."
if docker compose version &> /dev/null; then
    echo "✓ Docker Compose is already installed"
    docker compose version
else
    echo "Installing Docker Compose..."
    apt-get install -y docker-compose-plugin
    echo "✓ Docker Compose installed"
fi

# Step 3: Create non-root user for Docker (if needed)
echo ""
echo "👤 Step 3: Setting up Docker user permissions..."
if id "ubuntu" &>/dev/null; then
    usermod -aG docker ubuntu
    echo "✓ Added ubuntu user to docker group"
    echo "⚠️  Note: User may need to log out and back in for group changes to take effect"
fi

# Step 4: Create application directory
echo ""
echo "📁 Step 4: Setting up application directory..."
APP_DIR="/opt/energy-trader"
mkdir -p "$APP_DIR"
echo "✓ Created directory: $APP_DIR"

# Step 5: Create docker-compose.yml
echo ""
echo "📝 Step 5: Creating docker-compose.yml..."
cat > "$APP_DIR/docker-compose.yml" << 'EOF'
services:
  postgres:
    image: postgres:16-alpine
    container_name: energy-trader-db
    environment:
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
      POSTGRES_DB: ${DB_NAME:-energy_trader}
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - "${DB_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/migrations:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: always
    networks:
      - energy-trader-network

volumes:
  postgres_data:
    driver: local

networks:
  energy-trader-network:
    driver: bridge
EOF
chmod 644 "$APP_DIR/docker-compose.yml"
echo "✓ Created docker-compose.yml"

# Step 6: Create .env file
echo ""
echo "📝 Step 6: Creating .env file..."
cat > "$APP_DIR/.env" << 'EOF'
DB_HOST=localhost
DB_PORT=5432
DB_NAME=energy_trader
DB_USER=postgres
DB_PASSWORD=postgres
EOF
chmod 600 "$APP_DIR/.env"
echo "✓ Created .env file"
echo "⚠️  IMPORTANT: Change DB_PASSWORD in $APP_DIR/.env for production use!"

# Step 7: Create migrations directory structure
echo ""
echo "📁 Step 7: Setting up migrations directory..."
mkdir -p "$APP_DIR/database/migrations"
echo "✓ Created migrations directory"
echo "⚠️  Note: Copy your migration files to $APP_DIR/database/migrations/"

# Step 8: Create systemd service for auto-start
echo ""
echo "⚙️  Step 8: Creating systemd service for auto-start..."
cat > /etc/systemd/system/energy-trader-db.service << EOF
[Unit]
Description=Energy Trader PostgreSQL Database
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0
User=ubuntu
Group=docker

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable energy-trader-db.service
echo "✓ Created and enabled systemd service"

# Step 9: Instructions for next steps
echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Copy your git repository to the VM:"
echo "   git clone <your-repo-url> $APP_DIR"
echo "   OR"
echo "   scp -r /path/to/energy-trader/* ubuntu@$(hostname -I | awk '{print $1}'):$APP_DIR/"
echo ""
echo "2. Ensure migration files are in place:"
echo "   ls -la $APP_DIR/database/migrations/"
echo ""
echo "3. Start the database:"
echo "   cd $APP_DIR"
echo "   docker compose up -d"
echo ""
echo "   OR use the systemd service:"
echo "   sudo systemctl start energy-trader-db"
echo ""
echo "4. Verify the database is running:"
echo "   docker ps"
echo "   docker compose logs postgres"
echo ""
echo "5. Test connection:"
echo "   docker compose exec postgres psql -U postgres -d energy_trader -c 'SELECT version();'"
echo ""
echo "6. The database will automatically restart on system reboot thanks to:"
echo "   - Docker restart: always policy"
echo "   - Systemd service: energy-trader-db.service"
echo ""
echo "📝 Useful Commands:"
echo "   Start:   sudo systemctl start energy-trader-db"
echo "   Stop:    sudo systemctl stop energy-trader-db"
echo "   Status:  sudo systemctl status energy-trader-db"
echo "   Logs:    docker compose -f $APP_DIR/docker-compose.yml logs -f"
echo "   Shell:   docker compose -f $APP_DIR/docker-compose.yml exec postgres psql -U postgres -d energy_trader"
echo ""

