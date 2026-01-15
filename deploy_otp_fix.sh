#!/bin/bash
# Bash script to deploy OTP verification fix
# Run this directly on your production server

echo "========================================"
echo "OTP Verification Fix Deployment"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Step 1: Pull latest code
echo -e "${GREEN}Step 1: Pulling latest code...${NC}"
git pull origin main

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Git pull failed. Fix the error and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Code updated${NC}"
echo ""

# Step 2: Activate virtual environment
echo -e "${GREEN}Step 2: Activating virtual environment...${NC}"

if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "env" ]; then
    source env/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo -e "${RED}❌ Virtual environment not found. Please activate it manually.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Step 3: Install dependencies
echo -e "${GREEN}Step 3: Installing new dependencies...${NC}"
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Dependency installation failed.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Step 4: Run test script (optional)
echo -e "${YELLOW}Step 4: Running tests (optional)...${NC}"
read -p "Run test script? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    python test_otp_verification_fix.py
fi

echo ""

# Step 5: Restart server
echo -e "${GREEN}Step 5: Restarting Django server...${NC}"

# Try gunicorn first
if systemctl is-active --quiet gunicorn; then
    echo "Restarting gunicorn..."
    sudo systemctl restart gunicorn
    sleep 2
    sudo systemctl status gunicorn --no-pager -l
    echo -e "${GREEN}✅ Gunicorn restarted${NC}"
# Try supervisor
elif command -v supervisorctl &> /dev/null; then
    echo "Restarting via supervisor..."
    sudo supervisorctl restart all
    sleep 2
    sudo supervisorctl status
    echo -e "${GREEN}✅ Supervisor restarted${NC}"
else
    echo -e "${YELLOW}⚠️  Could not detect process manager.${NC}"
    echo "Please restart your Django server manually."
fi

echo ""
echo "========================================"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE${NC}"
echo "========================================"
echo ""
echo -e "${YELLOW}What was fixed:${NC}"
echo "  1. OTP verification now properly saves session data"
echo "  2. Added numpy for PDF template overlay"
echo "  3. Added reportlab for PDF generation"
echo "  4. Enhanced debug logging for troubleshooting"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Test OTP flow: Visit /gateways/activate/<QR_CODE>/"
echo "  2. Check logs: tail -f /var/log/gunicorn/error.log"
echo "  3. Test PDF: Generate batch with 'Download PDF' option"
echo ""
echo -e "${YELLOW}Debug Commands:${NC}"
echo "  View logs: sudo journalctl -u gunicorn -f"
echo "  Restart: sudo systemctl restart gunicorn"
echo "  Test: python test_otp_verification_fix.py"
echo ""
