# Deploy MCP Servers to OCI VM

This guide walks you through deploying the CFTC COT and Futures Prices MCP servers to your OCI VM as systemd services.

## Recommended Approach: Git Clone

**Why Git Clone?**
- ✅ Version control and easy updates
- ✅ Consistent deployment across environments
- ✅ Easy rollback if needed
- ✅ Track changes and history
- ✅ Same approach as demand-planning-bot

## Prerequisites

- OCI VM with SSH access
- Database already set up (we just did this!)
- Git repository URL (or repository already cloned)

## Quick Deployment

### Option 1: Automated Deployment Script

1. **Copy deployment script to VM:**

```bash
scp -i wellsync-mcp.key scripts/deploy_mcp_servers.sh ubuntu@170.9.241.171:/tmp/
```

2. **SSH into VM and run:**

```bash
ssh -i wellsync-mcp.key ubuntu@170.9.241.171

# If you have a git repo URL:
sudo bash /tmp/deploy_mcp_servers.sh <your-git-repo-url>

# If repository already exists at /opt/energy-trader:
sudo bash /tmp/deploy_mcp_servers.sh
```

3. **Start the services:**

```bash
sudo systemctl start cftc-cot-mcp
sudo systemctl start futures-prices-mcp
```

### Option 2: Manual Deployment

#### Step 1: Clone Repository (if not already done)

```bash
ssh -i wellsync-mcp.key ubuntu@170.9.241.171
cd /opt
sudo git clone <your-repo-url> energy-trader
sudo chown -R ubuntu:ubuntu energy-trader
```

#### Step 2: Set Up CFTC COT MCP Server

```bash
cd /opt/energy-trader/mcp-servers/cftc-cot

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cp .env.example .env
cat >> .env << EOF
DB_HOST=localhost
DB_PORT=5432
DB_NAME=energy_trader
DB_USER=postgres
DB_PASSWORD=postgres
MCP_SERVER_PORT=5223
EOF
```

#### Step 3: Set Up Futures Prices MCP Server

```bash
cd /opt/energy-trader/mcp-servers/futures-prices

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cp .env.example .env
cat >> .env << EOF
DB_HOST=localhost
DB_PORT=5432
DB_NAME=energy_trader
DB_USER=postgres
DB_PASSWORD=postgres
MCP_SERVER_PORT=5224
EOF
```

#### Step 4: Create Systemd Services

**CFTC COT Service:**

```bash
sudo tee /etc/systemd/system/cftc-cot-mcp.service > /dev/null << EOF
[Unit]
Description=CFTC COT MCP Server
After=network.target
Documentation=https://github.com/your-org/energy-trader

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/energy-trader/mcp-servers/cftc-cot
Environment="PATH=/opt/energy-trader/mcp-servers/cftc-cot/.venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/opt/energy-trader/mcp-servers/cftc-cot/.env

ExecStart=/opt/energy-trader/mcp-servers/cftc-cot/.venv/bin/python3 /opt/energy-trader/mcp-servers/cftc-cot/server.py --transport streamable-http --port 5223

Restart=always
RestartSec=10
StartLimitBurst=5
StartLimitIntervalSec=300

NoNewPrivileges=true
PrivateTmp=true

StandardOutput=journal
StandardError=journal
SyslogIdentifier=cftc-cot-mcp

[Install]
WantedBy=multi-user.target
EOF
```

**Futures Prices Service:**

```bash
sudo tee /etc/systemd/system/futures-prices-mcp.service > /dev/null << EOF
[Unit]
Description=Futures Prices MCP Server
After=network.target
Documentation=https://github.com/your-org/energy-trader

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/energy-trader/mcp-servers/futures-prices
Environment="PATH=/opt/energy-trader/mcp-servers/futures-prices/.venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/opt/energy-trader/mcp-servers/futures-prices/.env

ExecStart=/opt/energy-trader/mcp-servers/futures-prices/.venv/bin/python3 /opt/energy-trader/mcp-servers/futures-prices/server.py --transport streamable-http --port 5224

Restart=always
RestartSec=10
StartLimitBurst=5
StartLimitIntervalSec=300

NoNewPrivileges=true
PrivateTmp=true

StandardOutput=journal
StandardError=journal
SyslogIdentifier=futures-prices-mcp

[Install]
WantedBy=multi-user.target
EOF
```

#### Step 5: Enable and Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable cftc-cot-mcp
sudo systemctl enable futures-prices-mcp
sudo systemctl start cftc-cot-mcp
sudo systemctl start futures-prices-mcp
```

## Verify Deployment

### Check Service Status

```bash
sudo systemctl status cftc-cot-mcp
sudo systemctl status futures-prices-mcp
```

### Check Logs

```bash
# CFTC COT logs
sudo journalctl -u cftc-cot-mcp -f

# Futures Prices logs
sudo journalctl -u futures-prices-mcp -f
```

### Test Endpoints

```bash
# Test CFTC COT (port 5223)
curl http://localhost:5223/mcp

# Test Futures Prices (port 5224)
curl http://localhost:5224/mcp
```

### Verify Ports Are Listening

```bash
sudo netstat -tlnp | grep -E '5223|5224'
# OR
sudo ss -tlnp | grep -E '5223|5224'
```

## Port Configuration

- **CFTC COT MCP Server**: Port `5223`
- **Futures Prices MCP Server**: Port `5224`
- **Demand Planning Bot** (existing): Port `5222`

## Service Management

### Start Services

```bash
sudo systemctl start cftc-cot-mcp
sudo systemctl start futures-prices-mcp
```

### Stop Services

```bash
sudo systemctl stop cftc-cot-mcp
sudo systemctl stop futures-prices-mcp
```

### Restart Services

```bash
sudo systemctl restart cftc-cot-mcp
sudo systemctl restart futures-prices-mcp
```

### Check Status

```bash
sudo systemctl status cftc-cot-mcp
sudo systemctl status futures-prices-mcp
```

### View Logs

```bash
# Real-time logs
sudo journalctl -u cftc-cot-mcp -f
sudo journalctl -u futures-prices-mcp -f

# Last 100 lines
sudo journalctl -u cftc-cot-mcp -n 100
sudo journalctl -u futures-prices-mcp -n 100
```

## Updating Services

### Update from Git

```bash
cd /opt/energy-trader
git pull

# Restart services to pick up changes
sudo systemctl restart cftc-cot-mcp
sudo systemctl restart futures-prices-mcp
```

### Update Dependencies

```bash
# CFTC COT
cd /opt/energy-trader/mcp-servers/cftc-cot
source .venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart cftc-cot-mcp

# Futures Prices
cd /opt/energy-trader/mcp-servers/futures-prices
source .venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart futures-prices-mcp
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u cftc-cot-mcp -n 50
sudo journalctl -u futures-prices-mcp -n 50

# Check if port is in use
sudo netstat -tlnp | grep -E '5223|5224'

# Check database connection
cd /opt/energy-trader/mcp-servers/cftc-cot
source .venv/bin/activate
python3 -c "from db import get_db; db = get_db(); print('DB OK')"
```

### Database Connection Issues

```bash
# Verify database is running
docker ps | grep energy-trader-db

# Test connection
docker compose -f /opt/energy-trader/docker-compose.yml exec postgres psql -U postgres -d energy_trader -c "SELECT 1;"

# Check .env files
cat /opt/energy-trader/mcp-servers/cftc-cot/.env
cat /opt/energy-trader/mcp-servers/futures-prices/.env
```

### Port Already in Use

```bash
# Find what's using the port
sudo lsof -i :5223
sudo lsof -i :5224

# Kill process if needed (be careful!)
sudo kill <PID>
```

## Security Considerations

1. **Change Default Passwords**: Update `DB_PASSWORD` in `.env` files
2. **Firewall Rules**: Configure OCI security rules to restrict access to ports 5223 and 5224
3. **MCP Server Secret**: Consider setting `MCP_SERVER_SECRET` in `.env` files for authentication
4. **Network Access**: Only expose ports to trusted IPs/networks

## Summary

After deployment, you'll have:

- ✅ **CFTC COT MCP Server** running on port `5223`
- ✅ **Futures Prices MCP Server** running on port `5224`
- ✅ Both services auto-start on system reboot
- ✅ Both services auto-restart on failure
- ✅ Logs managed by systemd journal
- ✅ Same deployment pattern as demand-planning-bot

All three MCP servers will be running:
- Port 5222: Demand Planning Bot
- Port 5223: CFTC COT
- Port 5224: Futures Prices

