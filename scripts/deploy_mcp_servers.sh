#!/bin/bash
# Deploy CFTC COT and Futures Prices MCP Servers to OCI VM
# This script sets up both MCP servers as systemd services

set -e

REPO_URL="${1:-}"
INSTALL_DIR="/opt/energy-trader"
CFTC_COT_DIR="$INSTALL_DIR/mcp-servers/cftc-cot"
FUTURES_PRICES_DIR="$INSTALL_DIR/mcp-servers/futures-prices"

echo "🚀 Deploying MCP Servers to OCI VM..."
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script requires sudo privileges. Please run with sudo."
    exit 1
fi

# Step 1: Clone or update repository
echo "📦 Step 1: Setting up repository..."
if [ -z "$REPO_URL" ]; then
    echo "⚠️  No repository URL provided. Assuming repository already exists at $INSTALL_DIR"
    if [ ! -d "$INSTALL_DIR" ]; then
        echo "❌ Error: $INSTALL_DIR does not exist and no repo URL provided"
        echo "Usage: sudo $0 <git-repo-url>"
        exit 1
    fi
else
    if [ -d "$INSTALL_DIR/.git" ]; then
        echo "✓ Repository exists, updating..."
        cd "$INSTALL_DIR"
        sudo -u ubuntu git pull
    else
        echo "Cloning repository from $REPO_URL..."
        if [ -d "$INSTALL_DIR" ]; then
            echo "⚠️  $INSTALL_DIR exists but is not a git repo. Backing up..."
            mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
        fi
        sudo -u ubuntu git clone "$REPO_URL" "$INSTALL_DIR"
    fi
fi

# Step 2: Set up CFTC COT MCP Server
echo ""
echo "📦 Step 2: Setting up CFTC COT MCP Server..."
if [ ! -d "$CFTC_COT_DIR" ]; then
    echo "❌ Error: $CFTC_COT_DIR not found"
    exit 1
fi

cd "$CFTC_COT_DIR"
chown -R ubuntu:ubuntu "$CFTC_COT_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    sudo -u ubuntu python3 -m venv .venv
fi

# Install dependencies
echo "Installing dependencies..."
sudo -u ubuntu .venv/bin/pip install --upgrade pip
sudo -u ubuntu .venv/bin/pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    sudo -u ubuntu cp .env.example .env
    cat >> .env << EOF

# Production settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=energy_trader
DB_USER=postgres
DB_PASSWORD=postgres
MCP_SERVER_PORT=5223
EOF
    chmod 600 .env
    chown ubuntu:ubuntu .env
    echo "⚠️  IMPORTANT: Review and update DB_PASSWORD in $CFTC_COT_DIR/.env"
fi

# Step 3: Set up Futures Prices MCP Server
echo ""
echo "📦 Step 3: Setting up Futures Prices MCP Server..."
if [ ! -d "$FUTURES_PRICES_DIR" ]; then
    echo "❌ Error: $FUTURES_PRICES_DIR not found"
    exit 1
fi

cd "$FUTURES_PRICES_DIR"
chown -R ubuntu:ubuntu "$FUTURES_PRICES_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    sudo -u ubuntu python3 -m venv .venv
fi

# Install dependencies
echo "Installing dependencies..."
sudo -u ubuntu .venv/bin/pip install --upgrade pip
sudo -u ubuntu .venv/bin/pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    sudo -u ubuntu cp .env.example .env
    cat >> .env << EOF

# Production settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=energy_trader
DB_USER=postgres
DB_PASSWORD=postgres
MCP_SERVER_PORT=5224
EOF
    chmod 600 .env
    chown ubuntu:ubuntu .env
    echo "⚠️  IMPORTANT: Review and update DB_PASSWORD in $FUTURES_PRICES_DIR/.env"
fi

# Step 4: Create systemd service for CFTC COT
echo ""
echo "⚙️  Step 4: Creating systemd service for CFTC COT MCP Server..."
cat > /etc/systemd/system/cftc-cot-mcp.service << EOF
[Unit]
Description=CFTC COT MCP Server
After=network.target postgresql.service
Documentation=https://github.com/your-org/energy-trader

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=$CFTC_COT_DIR
Environment="PATH=$CFTC_COT_DIR/.venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=$CFTC_COT_DIR/.env

# Start server on port 5223 with streamable-http transport
ExecStart=$CFTC_COT_DIR/.venv/bin/python3 $CFTC_COT_DIR/server.py --transport streamable-http --port 5223

# Restart policy
Restart=always
RestartSec=10
StartLimitBurst=5
StartLimitIntervalSec=300

# Security hardening
NoNewPrivileges=true
PrivateTmp=true

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=cftc-cot-mcp

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable cftc-cot-mcp.service
echo "✓ Created and enabled CFTC COT MCP service"

# Step 5: Create systemd service for Futures Prices
echo ""
echo "⚙️  Step 5: Creating systemd service for Futures Prices MCP Server..."
cat > /etc/systemd/system/futures-prices-mcp.service << EOF
[Unit]
Description=Futures Prices MCP Server
After=network.target postgresql.service
Documentation=https://github.com/your-org/energy-trader

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=$FUTURES_PRICES_DIR
Environment="PATH=$FUTURES_PRICES_DIR/.venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=$FUTURES_PRICES_DIR/.env

# Start server on port 5224 with streamable-http transport
ExecStart=$FUTURES_PRICES_DIR/.venv/bin/python3 $FUTURES_PRICES_DIR/server.py --transport streamable-http --port 5224

# Restart policy
Restart=always
RestartSec=10
StartLimitBurst=5
StartLimitIntervalSec=300

# Security hardening
NoNewPrivileges=true
PrivateTmp=true

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=futures-prices-mcp

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable futures-prices-mcp.service
echo "✓ Created and enabled Futures Prices MCP service"

# Step 6: Summary
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Summary:"
echo "  CFTC COT MCP Server:"
echo "    Directory: $CFTC_COT_DIR"
echo "    Port: 5223"
echo "    Service: cftc-cot-mcp.service"
echo ""
echo "  Futures Prices MCP Server:"
echo "    Directory: $FUTURES_PRICES_DIR"
echo "    Port: 5224"
echo "    Service: futures-prices-mcp.service"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Review and update database passwords in:"
echo "   - $CFTC_COT_DIR/.env"
echo "   - $FUTURES_PRICES_DIR/.env"
echo ""
echo "2. Start the services:"
echo "   sudo systemctl start cftc-cot-mcp"
echo "   sudo systemctl start futures-prices-mcp"
echo ""
echo "3. Check service status:"
echo "   sudo systemctl status cftc-cot-mcp"
echo "   sudo systemctl status futures-prices-mcp"
echo ""
echo "4. View logs:"
echo "   sudo journalctl -u cftc-cot-mcp -f"
echo "   sudo journalctl -u futures-prices-mcp -f"
echo ""
echo "5. Test endpoints:"
echo "   curl http://localhost:5223/mcp"
echo "   curl http://localhost:5224/mcp"
echo ""

