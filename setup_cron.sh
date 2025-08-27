#!/bin/bash

# Crypto Fundraising Monitor Cron Setup Script

echo "🕐 Setting up Cron Job for Crypto Fundraising Monitor"
echo ""

# Get the current directory
CURRENT_DIR=$(pwd)
echo "Current directory: $CURRENT_DIR"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with your Telegram bot token first."
    echo "Run: cp env_template.txt .env"
    exit 1
fi

# Check if Python script exists
if [ ! -f "crypto_fundraising_monitor/run.py" ]; then
    echo "❌ Crypto Fundraising Monitor not found!"
    echo "Please make sure you're in the correct directory."
    exit 1
fi

# Create the cron command
CRON_COMMAND="0 9 * * * cd $CURRENT_DIR && python3 crypto_fundraising_monitor/run.py >> crypto_fundraising_monitor.log 2>&1"

echo "📝 Cron command to be added:"
echo "$CRON_COMMAND"
echo ""

# Ask user if they want to add the cron job
read -p "Do you want to add this cron job? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -
    
    if [ $? -eq 0 ]; then
        echo "✅ Cron job added successfully!"
        echo ""
        echo "📋 Current crontab:"
        crontab -l
        echo ""
        echo "🕐 The monitor will run daily at 9:00 AM (Asia/Seoul time)"
        echo "📝 Logs will be saved to: crypto_fundraising_monitor.log"
    else
        echo "❌ Failed to add cron job"
        exit 1
    fi
else
    echo "ℹ️  Cron job not added."
    echo "You can manually add it later by running:"
    echo "crontab -e"
    echo ""
    echo "And adding this line:"
    echo "$CRON_COMMAND"
fi

echo ""
echo "🔧 Manual execution:"
echo "  python3 crypto_fundraising_monitor/run.py"
echo ""
echo "📖 For more information, see README_crypto_fundraising.md" 