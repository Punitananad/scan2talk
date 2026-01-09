#!/bin/bash
# Fix activated QR codes without gateways on production server

echo "=========================================="
echo "Fixing Activated QR Codes Without Gateways"
echo "=========================================="

# SSH into production server and run the fix
ssh root@scan2talk.in << 'ENDSSH'
cd /root/CPA

# Activate virtual environment
source venv/bin/activate

# Run the fix script
python manage.py shell < fix_activated_qr_without_gateway.py

echo ""
echo "Fix completed!"
echo ""
echo "Testing the QR code..."
python manage.py shell -c "
from apps.gateways.qr_models import PreGeneratedQR
qr = PreGeneratedQR.objects.get(qr_code='XSJFGZWP')
print(f'QR Code: {qr.qr_code}')
print(f'Status: {qr.status}')
print(f'Owner: {qr.owner}')
print(f'Gateway: {qr.gateway}')
print(f'Gateway Active: {qr.gateway.is_active if qr.gateway else None}')
print(f'Access URL: /g/{qr.qr_code}/')
"

ENDSSH

echo ""
echo "=========================================="
echo "Done! Try scanning the QR code now."
echo "=========================================="
