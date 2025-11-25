# Quick Start: Deploy Database to OCI VM

## Fastest Method (5 minutes)

### 1. Copy setup script to VM

```bash
# From your local machine
scp scripts/setup_oci_vm.sh ubuntu@170.9.241.171:/tmp/
```

### 2. Run setup on VM

```bash
# SSH into VM
ssh ubuntu@170.9.241.171

# Run setup script
sudo bash /tmp/setup_oci_vm.sh
```

### 3. Copy repository to VM

```bash
# Option A: Clone from git (if repo is public or you have SSH keys)
cd /opt/energy-trader
git clone <your-repo-url> .

# Option B: Copy from local machine
# From your local machine:
cd /path/to/energy-trader
scp -r database/ scripts/load_cftc_cot_data.py scripts/cftc_parser.py ubuntu@170.9.241.171:/opt/energy-trader/
```

### 4. Start database

```bash
cd /opt/energy-trader
docker compose up -d
```

### 5. Verify it's working

```bash
# Check container is running
docker ps

# Test database connection
docker compose exec postgres psql -U postgres -d energy_trader -c "SELECT version();"

# Check schemas were created
docker compose exec postgres psql -U postgres -d energy_trader -c "\dn"
```

### 6. Load CFTC COT data (optional)

```bash
cd /opt/energy-trader
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=energy_trader
export DB_USER=postgres
export DB_PASSWORD=postgres

# Install Python dependencies if needed
pip3 install psycopg2-binary requests beautifulsoup4

# Load data
python3 scripts/load_cftc_cot_data.py --report all
```

## Done! ✅

Your database is now:
- ✅ Running in Docker
- ✅ Auto-restarts on container failure (`restart: always`)
- ✅ Auto-starts on system reboot (systemd service)
- ✅ Migrations automatically applied
- ✅ Ready to use

## Verify Auto-Restart

```bash
# Test auto-restart on failure
docker stop energy-trader-db
sleep 5
docker ps | grep energy-trader-db  # Should show it restarted

# Test auto-start on reboot
sudo reboot
# After reboot, SSH back in and check:
docker ps | grep energy-trader-db  # Should be running
```

## Connection Details

- **Host**: `localhost` (from VM) or `<VM_IP>` (from external)
- **Port**: `5432`
- **Database**: `energy_trader`
- **User**: `postgres`
- **Password**: `postgres` (change in `/opt/energy-trader/.env`)

## Troubleshooting

```bash
# View logs
docker compose logs postgres

# Check service status
sudo systemctl status energy-trader-db

# Restart database
sudo systemctl restart energy-trader-db
```

