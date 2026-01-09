# 500 Error Fix - After QR Activation

## Problem
After activating a QR code, scanning it for contact gave a 500 server error.

## Root Cause
The wallet check code was using `qr.qr_wallet` which throws an error if the wallet doesn't exist (RelatedObjectDoesNotExist exception).

## Solution
Changed wallet lookup to use proper exception handling:

### Before (Broken):
```python
try:
    wallet = qr.qr_wallet  # ❌ Throws error if wallet doesn't exist
    if wallet.balance >= 1.00:
        # ...
except:
    pass
```

### After (Fixed):
```python
try:
    from apps.accounts.recharge_models import QRWallet
    wallet = QRWallet.objects.get(qr_code=qr)  # ✅ Proper lookup
    if wallet.balance >= 1.00:
        # ...
except QRWallet.DoesNotExist:
    # No wallet found, treat as free
    pass
```

## Files Fixed

### 1. `apps/core/views.py` (GatewayAccessView)
**GET method:**
- Changed `qr.qr_wallet` to `QRWallet.objects.get(qr_code=qr)`
- Added proper `QRWallet.DoesNotExist` exception handling
- Added `select_related('category')` for efficiency

**POST method:**
- Same wallet lookup fix
- Better exception handling
- Added debug logging

### 2. `apps/gateways/call_masking_views.py`
**generate_masked_call_url:**
- Changed `qr.qr_wallet` to `QRWallet.objects.get(qr_code=qr)`
- Added `QRWallet.DoesNotExist` exception handling
- Treats missing wallet as free service

## What Happens Now

### Scenario 1: QR with Wallet
- Wallet exists → Check balance
- Balance >= ₹1 → Deduct and continue
- Balance = ₹0 → Ask visitor to pay

### Scenario 2: QR without Wallet
- Wallet doesn't exist → Treat as FREE
- No error thrown
- Visitor can contact immediately

### Scenario 3: Free Category QR
- No wallet check needed
- Always free
- No errors

## Testing

### Test Case 1: Activated QR with Wallet
```
1. Activate QR with prepaid category
2. Scan QR
3. Expected: Contact page loads ✅
4. Click Call/Message
5. Expected: Works correctly ✅
```

### Test Case 2: Activated QR without Wallet
```
1. Activate QR (wallet creation failed)
2. Scan QR
3. Expected: Contact page loads ✅ (no 500 error)
4. Click Call/Message
5. Expected: Works as free service ✅
```

### Test Case 3: Free Category QR
```
1. Activate QR with free category
2. Scan QR
3. Expected: Contact page loads ✅
4. Click Call/Message
5. Expected: Always free ✅
```

## Key Changes

1. **Proper Exception Handling**
   - Use `QRWallet.DoesNotExist` instead of generic `except:`
   - Specific error messages in logs

2. **Graceful Degradation**
   - Missing wallet → Treat as free
   - Don't break the user experience

3. **Better Logging**
   - Log when wallet not found
   - Log when treating as free
   - Easier debugging

## Result

✅ No more 500 errors after activation
✅ QR codes work with or without wallets
✅ Proper error handling
✅ Better user experience
