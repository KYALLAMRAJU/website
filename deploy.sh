#!/bin/bash

# ========== ADVAITAM DEPLOYMENT SCRIPT FOR AWS EC2 ==========
# Target: Ubuntu 24.04 LTS ARM64 on EC2 t4g.micro
# Usage: bash deploy.sh
# Run as: ubuntu user (with sudo privileges)

set -e  # Exit on error

echo "========== ADVAITAM DEPLOYMENT STARTED =========="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ========== CONFIGURATION ==========
APP_USER="advaitam"
PROJECT_DIR="/home/advaitam/app"
VENV_DIR="/home/advaitam/venv"
PYTHON="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"
DOMAIN="advaitam.info"
ORIGIN_DOMAIN="origin.advaitam.info"

# Step 1: Update system
echo -e "${YELLOW}[1/12] Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# Step 2: Install system dependencies
echo -e "${YELLOW}[2/12] Installing system dependencies...${NC}"
sudo apt install -y \
  python3.12 python3.12-venv python3.12-dev \
  postgresql-16 postgresql-client-16 libpq-dev \
  nginx certbot python3-certbot-nginx \
  git supervisor build-essential curl

# Step 3: Create app user
echo -e "${YELLOW}[3/12] Creating app user...${NC}"
id -u $APP_USER &>/dev/null || sudo useradd -m -s /bin/bash $APP_USER
sudo usermod -aG www-data $APP_USER

# Step 4: Setup PostgreSQL (local — no RDS)
echo -e "${YELLOW}[4/12] Setting up local PostgreSQL...${NC}"
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Get DB password from environment or use default (you MUST change this)
DB_PASSWORD="${DB_PASSWORD:-CHANGE_THIS_PASSWORD_IMMEDIATELY}"
if [ "$DB_PASSWORD" = "CHANGE_THIS_PASSWORD_IMMEDIATELY" ]; then
    echo -e "${RED}⚠️  WARNING: Using default database password!${NC}"
    echo -e "${RED}   You MUST set DB_PASSWORD environment variable or change it manually after deployment:${NC}"
    echo -e "${RED}   sudo -u postgres psql -c \"ALTER USER advaitam_user WITH PASSWORD 'your-strong-password';\"${NC}"
fi

# Create DB + user (idempotent)
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='advaitam_db'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE DATABASE advaitam_db;"
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='advaitam_user'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE USER advaitam_user WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE advaitam_db TO advaitam_user;"
sudo -u postgres psql -c "ALTER DATABASE advaitam_db OWNER TO advaitam_user;"

# Step 5: Clone or update project
echo -e "${YELLOW}[5/12] Cloning/updating project...${NC}"
sudo mkdir -p "$PROJECT_DIR"
sudo chown $APP_USER:$APP_USER "$PROJECT_DIR"
if [ -d "$PROJECT_DIR/.git" ]; then
    sudo -u $APP_USER git -C "$PROJECT_DIR" pull origin main || { echo -e "${RED}Git pull failed!${NC}"; exit 1; }
else
    sudo -u $APP_USER git clone https://github.com/KYALLAMRAJU/website.git "$PROJECT_DIR" || { echo -e "${RED}Git clone failed! Check repo URL and SSH keys.${NC}"; exit 1; }
fi

# Verify project was cloned successfully
if [ ! -f "$PROJECT_DIR/manage.py" ]; then
    echo -e "${RED}Error: manage.py not found in $PROJECT_DIR — clone/pull may have failed${NC}"
    exit 1
fi

# Step 6: Python virtual environment
echo -e "${YELLOW}[6/12] Setting up Python virtual environment...${NC}"
if [ ! -d "$VENV_DIR" ]; then
    sudo -u $APP_USER python3.12 -m venv "$VENV_DIR"
fi
sudo -u $APP_USER $PIP install --upgrade pip
sudo -u $APP_USER $PIP install -r "$PROJECT_DIR/requirements-prod.txt"

# Step 7: Environment file check
echo -e "${YELLOW}[7/12] Checking .env file...${NC}"
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${RED}⚠️  .env file not found! Create it before continuing:${NC}"
    echo -e "${RED}   sudo -u $APP_USER nano $PROJECT_DIR/.env${NC}"
    echo -e "${RED}   (use deploy/.env.prod.template as reference)${NC}"
    exit 1
fi
sudo chmod 600 "$PROJECT_DIR/.env"
sudo chown $APP_USER:$APP_USER "$PROJECT_DIR/.env"

# Validate critical .env variables
echo -e "${YELLOW}Validating .env file...${NC}"
REQUIRED_VARS=("DEBUG" "SECRET_KEY" "ALLOWED_HOSTS" "DB_HOST" "DB_NAME" "DB_USER" "DB_PASSWORD")
for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "^${var}=" "$PROJECT_DIR/.env"; then
        echo -e "${RED}⚠️  Missing required variable in .env: $var${NC}"
        echo -e "${RED}   Check deploy/.env.prod.template for all required variables${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✅ .env file validated${NC}"

# Step 8: Django setup
echo -e "${YELLOW}[8/12] Running Django setup...${NC}"
sudo mkdir -p "$PROJECT_DIR/logs"
sudo chown $APP_USER:$APP_USER "$PROJECT_DIR/logs"

sudo -u $APP_USER bash -c "cd $PROJECT_DIR && $PYTHON manage.py migrate --noinput"
sudo -u $APP_USER bash -c "cd $PROJECT_DIR && $PYTHON manage.py collectstatic --noinput"

# ── Upload audio files to S3 separately (mp3s are NOT in git) ───────────────
# Audio files must be manually placed in $PROJECT_DIR/static/audio/ on the server
# OR synced from your local machine before running this script:
#   aws s3 sync static/audio/ s3://advaitam-assets/static/audio/ --exclude "*.md"
#
# This step syncs whatever .mp3 files exist locally on EC2 → S3
echo -e "${YELLOW}[8b] Syncing audio files to S3 (skipped if no .mp3 files present)...${NC}"
AUDIO_DIR="$PROJECT_DIR/static/audio"
if compgen -G "$AUDIO_DIR/**/*.mp3" > /dev/null 2>&1 || find "$AUDIO_DIR" -name "*.mp3" | grep -q .; then
    USE_S3_VAL=$(grep "^USE_S3=" "$PROJECT_DIR/.env" | cut -d'=' -f2 | tr -d '[:space:]')
    if [ "$USE_S3_VAL" = "True" ] || [ "$USE_S3_VAL" = "true" ]; then
        S3_BUCKET=$(grep "^AWS_STORAGE_BUCKET_NAME=" "$PROJECT_DIR/.env" | cut -d'=' -f2 | tr -d '[:space:]')
        S3_BUCKET="${S3_BUCKET:-advaitam-assets}"
        echo -e "${YELLOW}   Uploading .mp3 files to s3://$S3_BUCKET/static/audio/ ...${NC}"
        aws s3 sync "$AUDIO_DIR/" "s3://$S3_BUCKET/static/audio/" \
            --exclude "*.md" \
            --exclude ".gitkeep" \
            --content-type "audio/mpeg" \
            --cache-control "max-age=31536000" \
            --only-show-errors
        echo -e "${GREEN}   ✅ Audio files uploaded to S3${NC}"
    else
        echo -e "${YELLOW}   USE_S3=False — skipping S3 audio upload (dev/local mode)${NC}"
    fi
else
    echo -e "${YELLOW}   ⚠️  No .mp3 files found in $AUDIO_DIR — audio files must be uploaded to S3 manually${NC}"
    echo -e "${YELLOW}   Run this from your LOCAL machine:${NC}"
    echo -e "${GREEN}   aws s3 sync static/audio/ s3://advaitam-assets/static/audio/ --exclude \"*.md\" --content-type audio/mpeg${NC}"
fi

# Step 9: Gunicorn socket directory
echo -e "${YELLOW}[9/12] Creating Gunicorn socket directory...${NC}"
sudo mkdir -p /run/advaitam
sudo chown $APP_USER:www-data /run/advaitam
sudo chmod 770 /run/advaitam

# Make it persistent across reboots
sudo tee /etc/tmpfiles.d/advaitam.conf > /dev/null <<EOF
d /run/advaitam 0770 $APP_USER www-data -
EOF

# Step 10: Configure Gunicorn systemd service
echo -e "${YELLOW}[10/12] Configuring Gunicorn systemd service...${NC}"
sudo tee /etc/systemd/system/advaitam.socket > /dev/null <<EOF
[Unit]
Description=Advaitam Gunicorn Socket

[Socket]
ListenStream=/run/advaitam/gunicorn.sock
SocketUser=$APP_USER
SocketGroup=www-data
SocketMode=0660

[Install]
WantedBy=sockets.target
EOF

sudo tee /etc/systemd/system/advaitam.service > /dev/null <<EOF
[Unit]
Description=Advaitam Django Gunicorn
Requires=advaitam.socket
After=network.target postgresql.service

[Service]
User=$APP_USER
Group=www-data
WorkingDirectory=$PROJECT_DIR
EnvironmentFile=$PROJECT_DIR/.env
Environment=DJANGO_ENV=production
ExecStart=$VENV_DIR/bin/gunicorn \
ExecStart=$VENV_DIR/bin/gunicorn \\
          --config $PROJECT_DIR/gunicorn.conf.py \\
          webProject.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=30
PrivateTmp=true
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable advaitam.socket advaitam.service
sudo systemctl start advaitam.socket
# Use 'reload' (SIGHUP → graceful worker replacement, zero downtime) not 'restart' (kills workers immediately)
sudo systemctl reload advaitam.service 2>/dev/null || sudo systemctl restart advaitam.service

# Step 11: Configure Nginx
echo -e "${YELLOW}[11/12] Configuring Nginx...${NC}"
sudo tee /etc/nginx/sites-available/advaitam > /dev/null <<'NGINXEOF'
# HTTP Server (Certbot will upgrade this to HTTPS automatically)
server {
    listen 80;
    server_name origin.advaitam.info;

    client_max_body_size 100M;
    keepalive_timeout    65;

    # Proxy to Gunicorn via Unix socket
    location / {
        proxy_pass          http://unix:/run/advaitam/gunicorn.sock;
        proxy_set_header    Host              $host;
        proxy_set_header    X-Real-IP         $remote_addr;
        proxy_set_header    X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header    X-Forwarded-Proto $http_x_forwarded_proto;
        proxy_read_timeout  120s;
        proxy_connect_timeout 10s;
        proxy_send_timeout  120s;
        proxy_buffering     on;
        proxy_buffer_size   8k;
        proxy_buffers       16 8k;
    }

    # Static fallback (normally served by CloudFront → S3 directly)
    location /static/ {
        alias /home/advaitam/app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml application/json
               application/javascript application/xml+rss
               application/atom+xml image/svg+xml;

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    access_log /home/advaitam/app/logs/nginx_access.log;
    error_log  /home/advaitam/app/logs/nginx_error.log;
}
NGINXEOF

sudo ln -sf /etc/nginx/sites-available/advaitam /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx

# Step 12: SSL Certificate
echo -e "${YELLOW}[12/12] SSL Certificate setup...${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Run this command AFTER DNS propagation (typically 5-30 minutes):${NC}"
echo ""
echo -e "${GREEN}   1. First, verify DNS is ready:${NC}"
echo -e "${GREEN}      nslookup origin.advaitam.info${NC}"
echo -e "${GREEN}      (should return your EC2 IP)${NC}"
echo ""
echo -e "${GREEN}   2. Then run:${NC}"
echo -e "${GREEN}      sudo certbot --nginx -d origin.advaitam.info${NC}"
echo ""
echo -e "${GREEN}   3. Certbot will auto-renew 30 days before expiry (systemd timer)${NC}"
echo ""
echo -e "${GREEN}========== DEPLOYMENT COMPLETED ==========${NC}"
echo -e "${GREEN}✅ Services running:${NC}"
sudo systemctl status advaitam.service --no-pager -l | head -5
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo -e "  1. Set up Route 53, S3, CloudFront, ACM (see deploy/05-AWS/AWS_PRODUCTION_DEPLOYMENT_GUIDE.md)"
echo -e "  2. Run: sudo certbot --nginx -d origin.advaitam.info"
echo -e "  3. Set AWS_S3_CUSTOM_DOMAIN in .env to your CloudFront domain"
echo -e "  4. Run: python manage.py collectstatic --noinput (uploads CSS/JS/images to S3)"
echo -e "  5. Upload audio files from LOCAL machine:"
echo -e "     aws s3 sync static/audio/ s3://advaitam-assets/static/audio/ --exclude \"*.md\" --content-type audio/mpeg"
echo -e "  6. Test: curl https://advaitam.info/"
