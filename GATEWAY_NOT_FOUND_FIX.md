# Gateway Not Found - Complete Fix

## Problem Summary

**Issue**: After activating a QR code once, subsequent scans show "Gateway Not Found" error instead of redirecting to the owner's contact page.

**Root Cause**: The backend logic had a critical flaw where gateways could become inactive after activation, breaking the QR-to-gateway relationship.

---

## Root Cause Analysis

### 1. **Gateway Deactivation Bug**
Located in `apps/core/views.py` (GatewayAccessView.get method):

**Problem Code** (lines 115-120):
```python
if not qr_obj.gateway.is_active:
    logger.error(f"QR code {identifier} gateway is not active")
    return render(request, 'core/gateway_unavailable.html', {
        'message': 'This gateway is currently unavailable.'
    })
```

**Issue**: The code checked if the gateway was inactive and showed an error, but didn't handle the case where the gateway should NEVER be inactive for an activated QR.

### 2. **Missing Validation in Activation**
Located in `apps/gateways/qr_models.py` (PreGeneratedQR.activate method):

**Problem**: The activation method didn't validate that:
- A gateway was provided
- The gateway was active
- The gateway-QR relationship would remain permanent

### 3. **No Auto-Recovery Mechanism**
If a gateway accidentally became inactive (e.g., through admin action or bug), there was no automatic recovery to restore access.

---

## The Fix

### Changes Made

#### 1. **Auto-Reactivation Logic** (`apps/core/views.py`)
```python
# CRITICAL FIX: Activated QRs must ALWAYS have active gateways
# If gateway is inactive, reactivate it automatically
if not qr_obj.gateway.is_active:
    logger.warning(f"QR code {identifier} gateway was inactive - reactivating automatically")
    qr_obj.gateway.is_active = True
    qr_obj.gateway.save(update_fields=['is_active'])
    logger.info(f"Gateway {qr_obj.gateway.id} reactivated successfully")
```

**What it does**: 
- Detects when an activated QR has an inactive gateway
- Automatically reactivates the gateway
- Logs the action for monitoring
- Ensures the user never sees "Gateway Not Found"

#### 2. **Explicit Active State** (`apps/gateways/qr_views.py`)
```python
gateway = Gateway.objects.create(
    owner=user,
    owner_name=name,
    title=f"{vehicle_type.title()} - {vehicle_number}",
    context_type='vehicle',
    description=f"{vehicle_model}",
    identifier_text=vehicle_number,
    is_active=True  # Explicitly set to active
)
```

**What it does**: Ensures all new gateways are created with `is_active=True` explicitly.

#### 3. **Activation Validation** (`apps/gateways/qr_models.py`)
```python
def activate(self, user, gateway=None, by_admin=False):
    """
    Activate this QR code for a user.
    CRITICAL: Once activated, the QR and gateway must remain permanently valid.
    """
    if self.status != 'available':
        raise ValueError(f"QR code is {self.status}, cannot activate")
    
    if not gateway:
        raise ValueError("Gateway is required for activation")
    
    if not gateway.is_active:
        raise ValueError("Gateway must be active for activation")
    
    # ... rest of activation logic
```

**What it does**: 
- Validates gateway exists before activation
- Ensures gateway is active before activation
- Prevents invalid activations

#### 4. **Improved Error Messages**
Added better error context when gateway is missing:
```python
if not qr_obj.gateway:
    logger.error(f"QR code {identifier} is activated but has no gateway - data integrity issue")
    return render(request, 'core/gateway_not_found.html', {
        'message': 'This QR code has a configuration error. Please contact support.'
    })
```

---

## Fix Script

A diagnostic and repair script is provided: `fix_gateway_not_found.py`

### What it does:
1. **Diagnoses** all activated QR codes
2. **Identifies** QRs with inactive or missing gateways
3. **Automatically reactivates** inactive gateways
4. **Reports** data integrity issues
5. **Verifies** the fix

### How to run:
```bash
python fix_gateway_not_found.py
```

### Expected output:
```
================================================================================
DIAGNOSING GATEWAY ISSUES
================================================================================

✓ Total activated QR codes: 15
✗ Activated QRs with INACTIVE gateway: 3
  - ABC12345 -> Gateway uuid-123 (DL01AB1234)
  - XYZ67890 -> Gateway uuid-456 (MH02CD5678)
✓ Activated QRs with ACTIVE gateway: 12

================================================================================
FIXING INACTIVE GATEWAYS
================================================================================

→ Reactivating gateway for QR ABC12345
  Gateway ID: uuid-123
  Vehicle: DL01AB1234
  Owner: John Doe
  ✓ Gateway reactivated successfully!

✓ Fixed 3 inactive gateways

================================================================================
VERIFICATION
================================================================================

✓✓✓ ALL ACTIVATED QRs HAVE ACTIVE GATEWAYS! ✓✓✓
✓ The 'Gateway Not Found' issue should be resolved!
```

---

## Correct Behavior After Fix

### First Scan (Not Activated)
1. User scans QR code
2. System detects status = 'available'
3. Redirects to activation page
4. User enters phone + vehicle details
5. Gateway created with `is_active=True`
6. QR status set to 'activated'
7. QR-gateway relationship established

### All Subsequent Scans (Activated)
1. User scans QR code
2. System detects status = 'activated'
3. System checks gateway exists ✓
4. System checks gateway is active:
   - If active: Continue ✓
   - If inactive: **Auto-reactivate** ✓
5. Show contact page to visitor
6. Visitor can send message/call

### Key Guarantees
- ✓ QR code NEVER becomes invalid after activation
- ✓ Gateway NEVER becomes permanently inactive
- ✓ Auto-recovery if gateway is accidentally deactivated
- ✓ Clear error messages for data integrity issues
- ✓ Logging for monitoring and debugging

---

## Testing

### Test Case 1: Normal Flow
```bash
# Scan QR first time
curl http://localhost:8000/g/ABC12345/
# Expected: Redirect to activation page

# Activate QR
# (Complete activation form)

# Scan QR second time
curl http://localhost:8000/g/ABC12345/
# Expected: Show contact page ✓

# Scan QR third time
curl http://localhost:8000/g/ABC12345/
# Expected: Show contact page ✓
```

### Test Case 2: Accidentally Deactivated Gateway
```python
# Simulate accidental deactivation
gateway = Gateway.objects.get(identifier_text='DL01AB1234')
gateway.is_active = False
gateway.save()

# Scan QR
curl http://localhost:8000/g/ABC12345/
# Expected: Auto-reactivate and show contact page ✓
```

### Test Case 3: Missing Gateway (Data Integrity Issue)
```python
# Simulate missing gateway
qr = PreGeneratedQR.objects.get(qr_code='ABC12345')
qr.gateway = None
qr.save()

# Scan QR
curl http://localhost:8000/g/ABC12345/
# Expected: Show error with support message ✓
```

---

## Admin Deregistration (Only Legitimate Deactivation)

The ONLY way a gateway should become inactive is through explicit admin action:

**Route**: `/gateways/registrations/` → Click "Deregister" button

**What happens**:
1. Admin explicitly chooses to deregister a vehicle
2. Gateway set to `is_active=False`
3. QR code reset to `status='available'`
4. QR-gateway relationship removed
5. QR can be reactivated by a new user

**Important**: This is intentional deactivation, not a bug.

---

## Production Deployment

### Steps:
1. **Deploy code changes**:
   ```bash
   git pull origin main
   ```

2. **Run fix script**:
   ```bash
   python fix_gateway_not_found.py
   ```

3. **Restart server**:
   ```bash
   sudo systemctl restart gunicorn
   ```

4. **Test**:
   - Scan an activated QR code
   - Verify contact page appears
   - Check logs for auto-reactivation messages

### Monitoring:
Check logs for these messages:
```
# Good - auto-recovery working
WARNING: QR code ABC12345 gateway was inactive - reactivating automatically
INFO: Gateway uuid-123 reactivated successfully

# Bad - data integrity issue
ERROR: QR code ABC12345 is activated but has no gateway - data integrity issue
```

---

## Summary

### What was broken:
- Gateways could become inactive after activation
- No recovery mechanism for inactive gateways
- QR codes became permanently broken

### What is fixed:
- ✓ Auto-reactivation of inactive gateways
- ✓ Validation during activation
- ✓ Explicit active state on creation
- ✓ Better error messages
- ✓ Diagnostic and repair script
- ✓ Comprehensive logging

### Result:
**QR codes remain permanently valid after activation, with automatic recovery if issues occur.**

---

## Files Modified

1. `apps/core/views.py` - Auto-reactivation logic
2. `apps/gateways/qr_views.py` - Explicit active state
3. `apps/gateways/qr_models.py` - Activation validation
4. `fix_gateway_not_found.py` - Diagnostic script (NEW)
5. `GATEWAY_NOT_FOUND_FIX.md` - This documentation (NEW)

---

## Contact

If issues persist after applying this fix:
1. Check server logs for specific error messages
2. Run the diagnostic script: `python fix_gateway_not_found.py`
3. Verify database integrity
4. Contact development team with QR code and error details
