#!/bin/bash

# Tracker Monitor Setup Script
# This script helps you set up the tracker monitor service

set -e

echo "================================================"
echo "  Private Tracker Signup Monitor - Setup"
echo "================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Create config directory if it doesn't exist
if [ ! -d "config" ]; then
    echo "📁 Creating config directory..."
    mkdir -p config
fi

# Copy example config if config doesn't exist
if [ ! -f "config/config.yaml" ]; then
    echo "📝 Creating default configuration file..."
    cp config.yaml config/config.yaml
    echo "✅ Configuration file created at: config/config.yaml"
    echo ""
    echo "⚠️  IMPORTANT: You need to edit config/config.yaml before starting the service!"
    echo ""
    echo "Please configure:"
    echo "  1. Enable at least one notification method (Discord, Telegram, Email, or Webhook)"
    echo "  2. Enable the trackers you want to monitor"
    echo "  3. Adjust check intervals if needed"
    echo ""
    read -p "Press Enter to open the config file in nano editor (or Ctrl+C to exit)..."
    nano config/config.yaml
else
    echo "✅ Configuration file already exists at: config/config.yaml"
fi

echo ""
echo "================================================"
echo "  Configuration Tips"
echo "================================================"
echo ""
echo "Discord Webhook:"
echo "  1. Go to Server Settings → Integrations → Webhooks"
echo "  2. Create New Webhook"
echo "  3. Copy Webhook URL"
echo ""
echo "Telegram Bot:"
echo "  1. Message @BotFather to create a bot"
echo "  2. Get bot token from BotFather"
echo "  3. Message @userinfobot to get your chat_id"
echo ""
echo "Email (Gmail):"
echo "  1. Enable 2FA on your Google account"
echo "  2. Generate an App Password"
echo "  3. Use the App Password in the config"
echo ""
read -p "Press Enter to continue..."

# Build the Docker image
echo ""
echo "🔨 Building Docker image..."
if docker compose version &> /dev/null; then
    docker compose build
else
    docker-compose build
fi

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Review your configuration:"
echo "   nano config/config.yaml"
echo ""
echo "2. Start the service:"
echo "   docker-compose up -d"
echo ""
echo "3. View logs:"
echo "   docker-compose logs -f"
echo ""
echo "4. Stop the service:"
echo "   docker-compose down"
echo ""
echo "For more information, see README.md"
echo ""
