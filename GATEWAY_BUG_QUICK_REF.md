# Gateway Not Found Bug - Quick Reference

## The Bug
Activated QR codes showing "Gateway Not Found" even though they exist.

## Root Cause
**File:** `apps/core/views.py`  
**Lines:** 82-88 (GET), 217-220 (POST)  
**Issue:** Database queries filtered by `gateway__is_active=True`, excluding inactive gateways

## The Fix (3 Changes)

### 1. GET Method - EntryPoint Lookup (Lines 100-116)
**Before:**
```python
entry_point = EntryPoint.objects.select_related('gateway').get(
    public_identifier=identifier,
    is_active=True,
    gateway__is_active=True  # ← REMOVED
)
```

**After:**
```python
entry_point = EntryPoint.objects.select_related('gateway').get(
    public_identifier=identifier,
    is_active=True
    # Do NOT filter by gateway__is_active=True
)
gateway = entry_point.gateway

# Reactivate gateway if inactive
if gateway and not gateway.is_active:
    gateway.is_active = True
    gateway.save(update_fields=['is_active'])
```

### 2. POST Method - EntryPoint Lookup (Lines 215-226)
**Before:**
```python
entry_point = EntryPoint.objects.select_related('gateway').get(
    public_identifier=identifier,
    is_active=True,
    gateway__is_active=True  # ← REMOVED
)
```

**After:**
```python
entry_point = EntryPoint.objects.select_related('gateway').get(
    public_identifier=identifier,
    is_active=True
)
gateway = entry_point.gateway

# Reactivate gateway if inactive
if gateway and not gateway.is_active:
    gateway.is_active = True
    gateway.save(update_fields=['is_active'])
```

### 3. POST Method - QR Lookup (Lines 230-243)
**Before:**
```python
qr = PreGeneratedQR.objects.select_related('gateway').get(
    qr_code=identifier.upper(),
    status='activated',
    gateway__is_active=True  # ← REMOVED
)
```

**After:**
```python
qr = PreGeneratedQR.objects.select_related('gateway').get(
    qr_code=identifier.upper(),
    status='activated'
)
gateway = qr.gateway

# Reactivate gateway if inactive
if gateway and not gateway.is_active:
    gateway.is_active = True
    gateway.save(update_fields=['is_active'])
```

## Key Principle
**Once a QR is activated (`status='activated'`), it must ALWAYS work, regardless of `gateway.is_active`.**

## Field Rules

### NEVER Change After Activation
- `PreGeneratedQR.status` (stays `'activated'` forever)
- `PreGeneratedQR.gateway` (never set to `None`)
- `PreGeneratedQR.qr_code` (unique identifier)

### CAN Change (Auto-Restored)
- `Gateway.is_active` (auto-restored to `True` when accessed)

## Testing
```bash
python test_gateway_not_found_fix.py
```

## Deployment
- ✅ No database migration needed
- ✅ No downtime required
- ✅ Backward compatible
- ✅ Self-healing (fixes existing issues automatically)
