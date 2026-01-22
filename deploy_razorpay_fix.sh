#!/bin/bash
# Deploy Razorpay configuration fix to production server

echo "=========================================="
echo "Razorpay Configuration Deployment"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}✗ .env file not found!${NC}"
    echo "Please create .env file with Razorpay credentials"
    exit 1
fi

# Check if Razorpay credentials are in .env
if ! grep -q "RAZORPAY_KEY_ID" .env; then
    echo -e "${RED}✗ RAZORPAY_KEY_ID not found in .env${NC}"
    echo "Please add: RAZORPAY_KEY_ID=rzp_live_iBh2Pp5ymtg0RS"
    exit 1
fi

if ! grep -q "RAZORPAY_KEY_SECRET" .env; then
    echo -e "${RED}✗ RAZORPAY_KEY_SECRET not found in .env${NC}"
    echo "Please add: RAZORPAY_KEY_SECRET=kaFVBMGJHj5GhXIoFH34WgsO"
    exit 1
fi

echo -e "${GREEN}✓ .env file found with Razorpay credentials${NC}"

# Run diagnostic check
echo ""
echo "Running diagnostic check..."
python check_razorpay_config.py

# Ask for confirmation
echo ""
read -p "Do you want to restart the server? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Restarting Django application..."
    
    # Try different restart methods
    if command -v systemctl &> /dev/null; then
        echo "Using systemctl..."
        sudo systemctl restart gunicorn || sudo systemctl restart uwsgi || echo "Manual restart required"
    elif [ -f "restart_server.sh" ]; then
        echo "Using restart_server.sh..."
        ./restart_server.sh
    else
        echo -e "${YELLOW}Please restart your Django application manually${NC}"
        echo "Common commands:"
        echo "  - sudo systemctl restart gunicorn"
        echo "  - sudo systemctl restart uwsgi"
        echo "  - pkill -HUP gunicorn"
    fi
    
    echo -e "${GREEN}✓ Deployment complete!${NC}"
    echo ""
    echo "Test the payment gateway at:"
    echo "https://scan2talk.in/order-tag/"
else
    echo "Deployment cancelled"
fi

echo "=========================================="
