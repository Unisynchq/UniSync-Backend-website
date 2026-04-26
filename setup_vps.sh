#!/bin/bash

# UniSync Backend PRODUCTION Setup Script
# Recommended OS: Ubuntu 22.04 LTS

set -e

echo "🚀 Starting PRODUCTION UniSync Backend Deployment..."

# 1. Update and Install System Dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3-venv python3-pip nginx nodejs npm curl certbot python3-certbot-nginx

# 2. Install Docker & Docker Compose (for LiteLLM)
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="sudo docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="sudo docker-compose"
else
    echo "Installing Docker Compose plugin..."
    sudo apt install -y docker-compose-plugin
    DOCKER_COMPOSE="sudo docker compose"
fi

# 3. Install PM2 Globally
sudo npm install -g pm2

# 4. Project Setup
PROJECT_DIR=$(pwd)
echo "📂 Project Directory: $PROJECT_DIR"

# 5. Backend Setup
echo "📦 Setting up Python Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt gunicorn uvicorn

# Start LiteLLM Infrastructure
echo "🐳 Starting LiteLLM & Postgres (Docker)..."
$DOCKER_COMPOSE up -d

# Start FastAPI with PM2 (Production Mode: Gunicorn + Uvicorn Workers)
echo "⚡ Starting FastAPI App with Gunicorn/PM2..."
# We use Gunicorn with Uvicorn workers for production stability
pm2 start "venv/bin/gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000" --name unisync-backend --update-env
pm2 save
pm2 startup

# 6. Nginx Configuration (Production Grade)
echo "🌐 Configuring Nginx Reverse Proxy..."
cat <<EOF | sudo tee /etc/nginx/sites-available/unisync-api
server {
    listen 80;
    server_name _; # Replace with your domain (e.g., api.unisync.app)

    # Security Headers
    add_header X-Frame-Options "DENY";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Gzip Compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;

    # Backend API
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Increase timeout for AI processing
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    # LiteLLM Proxy (Internal Access)
    location /litellm/ {
        proxy_pass http://127.0.0.1:4000/;
        proxy_set_header Host \$host;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/unisync-api /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default || true
sudo nginx -t
sudo systemctl restart nginx

echo "✅ PRODUCTION Backend Deployment Complete!"
echo "Next Steps:"
echo "1. Run the SQL in 'migrations/consolidated_schema.sql' in your Supabase SQL Editor."
echo "2. Update your .env file with production credentials."
echo "3. Run 'pm2 restart unisync-backend' after updating .env."
echo "4. Run 'sudo certbot --nginx' to enable HTTPS for your domain."
