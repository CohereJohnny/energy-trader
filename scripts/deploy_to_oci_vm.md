# Deploy Energy Trader Database to OCI VM

This guide walks you through setting up a PostgreSQL database on an OCI VM with Docker, ensuring it always runs and restarts automatically.

## Prerequisites

- OCI VM running Ubuntu 22.04 (or similar)
- SSH access to the VM
- Sudo/root access on the VM

## Quick Setup

### Option 1: Automated Setup Script

1. **Copy the setup script to your VM:**

```bash
# From your local machine
scp scripts/setup_oci_vm.sh ubuntu@<VM_IP>:/tmp/
```

2. **SSH into the VM and run the setup:**

```bash
ssh ubuntu@<VM_IP>
sudo bash /tmp/setup_oci_vm.sh
```

3. **Copy your repository to the VM:**

```bash
# Option A: Clone from git
cd /opt/energy-trader
git clone <your-repo-url> .

# Option B: Copy from local machine
# From your local machine:
scp -r database/ ubuntu@<VM_IP>:/opt/energy-trader/
```

4. **Start the database:**

```bash
cd /opt/energy-trader
docker compose up -d
```

### Option 2: Manual Setup

#### Step 1: Install Docker

```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Set up Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to docker group (optional, for non-sudo access)
sudo usermod -aG docker ubuntu
# Log out and back in for group changes to take effect
```

#### Step 2: Set Up Application Directory

```bash
# Create application directory
sudo mkdir -p /opt/energy-trader
sudo chown ubuntu:ubuntu /opt/energy-trader
cd /opt/energy-trader

# Copy your repository files
# Option A: Clone from git
git clone <your-repo-url> .

# Option B: Copy from local machine
# From your local machine:
# scp -r . ubuntu@<VM_IP>:/opt/energy-trader/
```

#### Step 3: Configure Environment

```bash
cd /opt/energy-trader

# Create .env file (or copy from .env.example)
cat > .env << EOF
DB_HOST=localhost
DB_PORT=5432
DB_NAME=energy_trader
DB_USER=postgres
DB_PASSWORD=postgres
EOF

# IMPORTANT: Change DB_PASSWORD for production!
chmod 600 .env
```

#### Step 4: Start PostgreSQL Container

```bash
cd /opt/energy-trader

# Start the database
docker compose up -d

# Verify it's running
docker ps

# Check logs
docker compose logs postgres
```

#### Step 5: Verify Database Setup

```bash
# Test connection
docker compose exec postgres psql -U postgres -d energy_trader -c "SELECT version();"

# Check if migrations ran
docker compose exec postgres psql -U postgres -d energy_trader -c "\dn"

# Should show schemas like: futures_prices, cftc_cot
```

#### Step 6: Set Up Auto-Restart

The `docker-compose.yml` already has `restart: always`, but we'll also create a systemd service for system-level auto-start:

```bash
# Create systemd service
sudo tee /etc/systemd/system/energy-trader-db.service > /dev/null << EOF
[Unit]
Description=Energy Trader PostgreSQL Database
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/energy-trader
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0
User=ubuntu
Group=docker

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable energy-trader-db.service
sudo systemctl start energy-trader-db.service

# Verify service status
sudo systemctl status energy-trader-db.service
```

## Loading Data

After the database is set up, you can load data:

### Load CFTC COT Data

```bash
cd /opt/energy-trader

# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=energy_trader
export DB_USER=postgres
export DB_PASSWORD=postgres

# Load CFTC COT data
python3 scripts/load_cftc_cot_data.py --report all
```

### Load Futures Prices Data

```bash
# If you have futures price data
python3 scripts/load_futures_data.py
```

## Monitoring and Maintenance

### Check Database Status

```bash
# Check if container is running
docker ps | grep energy-trader-db

# Check logs
docker compose -f /opt/energy-trader/docker-compose.yml logs -f postgres

# Check systemd service status
sudo systemctl status energy-trader-db
```

### Database Backup

```bash
# Create backup
docker compose exec postgres pg_dump -U postgres energy_trader > backup_$(date +%Y%m%d).sql

# Restore backup
docker compose exec -T postgres psql -U postgres energy_trader < backup_20251125.sql
```

### Restart Database

```bash
# Using docker compose
cd /opt/energy-trader
docker compose restart postgres

# Using systemd
sudo systemctl restart energy-trader-db
```

### Stop Database

```bash
# Using docker compose
cd /opt/energy-trader
docker compose stop postgres

# Using systemd
sudo systemctl stop energy-trader-db
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs postgres

# Check if port is already in use
sudo netstat -tlnp | grep 5432

# Check Docker daemon
sudo systemctl status docker
```

### Database Connection Issues

```bash
# Test connection from inside container
docker compose exec postgres psql -U postgres -d energy_trader -c "SELECT 1;"

# Check if database exists
docker compose exec postgres psql -U postgres -l

# Check network connectivity
docker network ls
docker network inspect energy-trader_energy-trader-network
```

### Migrations Not Running

```bash
# Check if migrations directory is mounted correctly
docker compose exec postgres ls -la /docker-entrypoint-initdb.d/

# Run migrations manually
docker compose exec postgres psql -U postgres -d energy_trader -f /docker-entrypoint-initdb.d/001_create_futures_prices_schema.sql
docker compose exec postgres psql -U postgres -d energy_trader -f /docker-entrypoint-initdb.d/002_create_cftc_cot_schema.sql
```

### Auto-Restart Not Working

```bash
# Check systemd service
sudo systemctl status energy-trader-db

# Check service logs
sudo journalctl -u energy-trader-db -f

# Verify service is enabled
sudo systemctl is-enabled energy-trader-db
```

## Security Considerations

1. **Change Default Password**: Update `DB_PASSWORD` in `.env` file
2. **Firewall**: Configure OCI security rules to restrict database access
3. **SSL/TLS**: Consider enabling SSL for PostgreSQL connections
4. **Backup Strategy**: Set up regular automated backups
5. **Monitoring**: Consider setting up monitoring and alerting

## Production Recommendations

1. **Use Strong Passwords**: Change default `postgres` password
2. **Restrict Network Access**: Only allow connections from trusted IPs
3. **Enable PostgreSQL Logging**: Configure logging for audit trails
4. **Set Resource Limits**: Configure Docker resource limits
5. **Regular Updates**: Keep Docker and PostgreSQL images updated
6. **Backup Strategy**: Implement automated daily backups
7. **Monitoring**: Set up health checks and alerting

## Useful Commands Reference

```bash
# Start database
sudo systemctl start energy-trader-db
# OR
cd /opt/energy-trader && docker compose up -d

# Stop database
sudo systemctl stop energy-trader-db
# OR
cd /opt/energy-trader && docker compose stop

# View logs
docker compose -f /opt/energy-trader/docker-compose.yml logs -f

# Access PostgreSQL shell
docker compose exec postgres psql -U postgres -d energy_trader

# Check database size
docker compose exec postgres psql -U postgres -d energy_trader -c "SELECT pg_size_pretty(pg_database_size('energy_trader'));"

# List all tables
docker compose exec postgres psql -U postgres -d energy_trader -c "\dt"

# List all schemas
docker compose exec postgres psql -U postgres -d energy_trader -c "\dn"
```

