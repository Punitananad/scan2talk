# Quick Fix: Gateway Not Found Issue

## Problem
When scanning activated QR codes (like XSJFGZWP), users see "Gateway Not Found" error.

## Root Cause
The QR code is activated in the database but doesn't have a gateway linked to it. This can happen if:
- Gateway was deleted after activation
- Activation process failed midway
- Database inconsistency

## Solution

### Step 1: SSH into Production Server
```bash
ssh root@scan2talk.in
cd /root/CPA
source venv/bin/activate
```

### Step 2: Run the Fix Script
```bash
python manage.py shell << 'EOF'
from apps.gateways.qr_models import PreGeneratedQR
from apps.gateways.models import Gateway
from django.db import transaction

# Find activated QR codes without gateways
broken_qrs = PreGeneratedQR.objects.filter(
    status='activated',
    gateway__isnull=True
).select_related('owner')

print(f"Found {broken_qrs.count()} activated QR codes without gateways")

for qr in broken_qrs:
    print(f"\nFixing QR: {qr.qr_code}")
    print(f"Owner: {qr.owner.phone if qr.owner else 'No owner'}")
    
    if qr.owner:
        try:
            with transaction.atomic():
                # Create gateway
                gateway = Gateway.objects.create(
                    owner=qr.owner,
                    owner_name=qr.owner.full_name or 'Vehicle Owner',
                    title=f"Vehicle - {qr.qr_code}",
                    context_type='vehicle',
                    description='Auto-created to fix missing gateway',
                    identifier_text=qr.qr_code
                )
                
                # Link to QR code
                qr.gateway = gateway
                qr.save()
                
                print(f"✅ Created gateway and linked to QR code")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    else:
        print(f"⚠️ Cannot fix - no owner")

print("\n✅ Fix complete!")
EOF
```

### Step 3: Verify the Fix
```bash
python manage.py shell -c "
from apps.gateways.qr_models import PreGeneratedQR
qr = PreGeneratedQR.objects.get(qr_code='XSJFGZWP')
print(f'QR Code: {qr.qr_code}')
print(f'Status: {qr.status}')
print(f'Gateway: {qr.gateway}')
print(f'Gateway Active: {qr.gateway.is_active if qr.gateway else None}')
"
```

### Step 4: Test
Visit: `https://scan2talk.in/g/XSJFGZWP/`

You should now see the contact form instead of "Gateway Not Found".

## Alternative: Quick One-Liner Fix
```bash
ssh root@scan2talk.in "cd /root/CPA && source venv/bin/activate && python manage.py shell < fix_activated_qr_without_gateway.py"
```

## Prevention
This issue shouldn't happen in the future because the activation flow creates gateways atomically. If it does happen again, check:
1. Database transaction failures
2. Manual gateway deletions
3. Migration issues
