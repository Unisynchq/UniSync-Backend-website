#!/bin/bash

echo "Starting deployment of UniSync Backend..."

# 1. Pull latest changes
echo "Pulling latest code from git..."
git pull origin main

# 2. Activate virtual environment (Assuming it's named 'venv')
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
fi

# 3. Install/upgrade dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# 4. Restart the FastAPI service using Systemd or PM2
# Replace 'unisync-backend' with the actual service name in your hostinger setup.
echo "Restarting application server..."
# Using systemctl if it's a systemd service:
# sudo systemctl restart unisync-backend

# Using PM2 if pm2 is used for python:
# pm2 restart unisync-backend

echo "Deployment finished. Check logs to ensure service is running smoothly."
