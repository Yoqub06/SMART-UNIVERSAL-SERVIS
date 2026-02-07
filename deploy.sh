#!/bin/bash

# Deployment script for Home Services Bot

echo "🚀 Home Services Bot - Deployment Script"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (sudo)${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Installing system dependencies...${NC}"
apt-get update
apt-get install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib

echo -e "${YELLOW}🗄️ Setting up PostgreSQL...${NC}"
sudo -u postgres psql -c "CREATE DATABASE home_services_bot;" 2>/dev/null || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER bot_user WITH PASSWORD 'secure_password_here';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE home_services_bot TO bot_user;"

echo -e "${YELLOW}📝 Importing database schema...${NC}"
sudo -u postgres psql -d home_services_bot -f schema.sql

echo -e "${YELLOW}🐍 Creating Python virtual environment...${NC}"
python3.11 -m venv venv
source venv/bin/activate

echo -e "${YELLOW}📚 Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${YELLOW}⚙️ Creating .env file...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️ Please edit .env file with your credentials${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

echo -e "${YELLOW}🔧 Creating systemd service...${NC}"
cat > /etc/systemd/system/home-services-bot.service << EOF
[Unit]
Description=Home Services Telegram Bot
After=network.target postgresql.service

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${YELLOW}🔄 Enabling and starting service...${NC}"
systemctl daemon-reload
systemctl enable home-services-bot
systemctl start home-services-bot

echo ""
echo -e "${GREEN}✅ Deployment completed!${NC}"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file: nano .env"
echo "2. Restart service: sudo systemctl restart home-services-bot"
echo "3. Check status: sudo systemctl status home-services-bot"
echo "4. View logs: sudo journalctl -u home-services-bot -f"
echo ""
echo "🎉 Your bot should be running now!"
