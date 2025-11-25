# OCI VM Deployment Steps

## Step 1: Copy Setup Script ✅

```bash
scp -i wellsync-mcp.key scripts/setup_oci_vm.sh ubuntu@170.9.241.171:/tmp/
```

## Step 2: SSH into VM and Run Setup

```bash
# SSH into the VM
ssh -i wellsync-mcp.key ubuntu@170.9.241.171

# Run the setup script
sudo bash /tmp/setup_oci_vm.sh
```

The setup script will:
- Install Docker and Docker Compose
- Create `/opt/energy-trader` directory
- Set up docker-compose.yml and .env files
- Create systemd service for auto-start
- Configure auto-restart

## Step 3: Copy Repository Files

After setup completes, copy your repository files to the VM:

### Option A: Copy entire repository (recommended)

From your local machine:
```bash
# Copy database migrations and scripts
scp -i wellsync-mcp.key -r database/ ubuntu@170.9.241.171:/opt/energy-trader/
scp -i wellsync-mcp.key -r scripts/ ubuntu@170.9.241.171:/opt/energy-trader/
scp -i wellsync-mcp.key docker-compose.yml ubuntu@170.9.241.171:/opt/energy-trader/
```

### Option B: Clone from git (if repo is accessible)

```bash
ssh -i wellsync-mcp.key ubuntu@170.9.241.171
cd /opt/energy-trader
git clone <your-repo-url> .
```

## Step 4: Start Database

```bash
# SSH into VM
ssh -i wellsync-mcp.key ubuntu@170.9.241.171

# Navigate to app directory
cd /opt/energy-trader

# Start the database
docker compose up -d

# Verify it's running
docker ps

# Check logs
docker compose logs postgres
```

## Step 5: Verify Database Setup

```bash
# Test connection
docker compose exec postgres psql -U postgres -d energy_trader -c "SELECT version();"

# Check schemas were created
docker compose exec postgres psql -U postgres -d energy_trader -c "\dn"

# Should show: futures_prices, cftc_cot
```

## Step 6: Load CFTC COT Data (Optional)

```bash
# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=energy_trader
export DB_USER=postgres
export DB_PASSWORD=postgres

# Install Python dependencies (if needed)
pip3 install psycopg2-binary requests beautifulsoup4

# Load CFTC COT data
python3 scripts/load_cftc_cot_data.py --report all
```

## Verify Auto-Restart Works

```bash
# Test container auto-restart
docker stop energy-trader-db
sleep 5
docker ps | grep energy-trader-db  # Should show it restarted

# Test systemd auto-start (after reboot)
sudo reboot
# After reboot, SSH back in:
docker ps | grep energy-trader-db  # Should be running
```

## Useful Commands

```bash
# View logs
docker compose logs -f postgres

# Check service status
sudo systemctl status energy-trader-db

# Restart database
sudo systemctl restart energy-trader-db

# Stop database
sudo systemctl stop energy-trader-db

# Access PostgreSQL shell
docker compose exec postgres psql -U postgres -d energy_trader
```

## Troubleshooting

### If setup script fails:
```bash
# Check Docker installation
docker --version
docker compose version

# Check if directories exist
ls -la /opt/energy-trader
```

### If database won't start:
```bash
# Check logs
docker compose logs postgres

# Check if port is in use
sudo netstat -tlnp | grep 5432

# Check Docker daemon
sudo systemctl status docker
```

### If migrations didn't run:
```bash
# Check if migrations directory is mounted
docker compose exec postgres ls -la /docker-entrypoint-initdb.d/

# Run migrations manually
docker compose exec postgres psql -U postgres -d energy_trader -f /docker-entrypoint-initdb.d/001_create_futures_prices_schema.sql
docker compose exec postgres psql -U postgres -d energy_trader -f /docker-entrypoint-initdb.d/002_create_cftc_cot_schema.sql
```

