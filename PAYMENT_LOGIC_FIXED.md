# Payment Logic - Fixed

## How It Works Now

### Rule 1: Owner Has Balance (₹1 or more)
**Visitor contacts for FREE**

- ✅ No payment UI shown to visitor
- ✅ Owner's wallet is automatically deducted ₹1
- ✅ Visitor clicks Call → Directly redirected to call page
- ✅ Visitor clicks Message → Sends message immediately
- ✅ Zero friction for visitor

### Rule 2: Owner Has ₹0 Balance
**Visitor must pay ₹1**

- ⚠️ Payment notice shown to visitor
- ⚠️ Button text changes to "Pay ₹1 & Call/Message"
- ⚠️ Visitor clicks → Redirected to PhonePe payment
- ⚠️ After payment → Action completes

---

## Flow Diagrams

### Call Flow (Owner Has Balance)
```
Visitor scans QR
    ↓
Clicks "Call Owner"
    ↓
Backend checks wallet
    ↓
Balance >= ₹1? YES
    ↓
Deduct ₹1 from owner
    ↓
Generate masked call
    ↓
Redirect visitor to call page
    ↓
Done! (Visitor pays nothing)
```

### Call Flow (Owner Has ₹0)
```
Visitor scans QR
    ↓
Clicks "Call Owner"
    ↓
Backend checks wallet
    ↓
Balance >= ₹1? NO
    ↓
Return payment_required: true
    ↓
Frontend redirects to PhonePe
    ↓
Visitor pays ₹1
    ↓
Payment success
    ↓
Generate masked call
    ↓
Redirect to call page
```

### Message Flow (Owner Has Balance)
```
Visitor scans QR
    ↓
Clicks "Send Message"
    ↓
Fills message form
    ↓
Clicks "Send Message Now"
    ↓
Backend checks wallet
    ↓
Balance >= ₹1? YES
    ↓
Deduct ₹1 from owner
    ↓
Send message
    ↓
Show success page
    ↓
Done! (Visitor pays nothing)
```

### Message Flow (Owner Has ₹0)
```
Visitor scans QR
    ↓
Clicks "Send Message"
    ↓
Sees payment notice (yellow box)
    ↓
Fills message form
    ↓
Clicks "Pay ₹1 & Send Message"
    ↓
Redirected to PhonePe
    ↓
Visitor pays ₹1
    ↓
Payment success
    ↓
Send message
    ↓
Show success page
```

---

## Backend Logic

### File: `apps/core/views.py` (GatewayAccessView)

**GET Request:**
```python
# Check wallet balance
if qr.category.category_type == 'prepaid':
    wallet = qr.qr_wallet
    
    if wallet.balance >= 1.00:
        payment_required = False
        payer = 'owner'
    else:
        payment_required = True
        payer = 'visitor'
        cost_per_action = 1.00
```

**POST Request (Message):**
```python
# Deduct from owner if balance available
if wallet.balance >= 1.00:
    wallet.balance -= 1.00
    wallet.save()
    # Continue with message sending
else:
    # Redirect to payment
```

### File: `apps/gateways/call_masking_views.py`

**POST Request (Call):**
```python
# Check wallet before generating call
if wallet.balance >= 1.00:
    wallet.balance -= 1.00
    wallet.save()
    # Generate masked call
    return JsonResponse({'success': True, 'call_url': ...})
else:
    # Return payment required
    return JsonResponse({
        'success': False,
        'payment_required': True,
        'cost': 1.00
    }, status=402)
```

---

## Frontend Logic

### File: `templates/core/gateway_access.html`

**Payment Notice (Only shown if visitor must pay):**
```django
{% if payment_required and payer == 'visitor' %}
    <div class="payment-notice">
        Payment Required: ₹{{ cost_per_action }}
    </div>
{% endif %}
```

**Button Text:**
```django
{% if payment_required and payer == 'visitor' %}
    Pay ₹{{ cost_per_action }} & Send Message
{% else %}
    Send Message Now
{% endif %}
```

**JavaScript Call Handler:**
```javascript
if (data.success) {
    // Owner paid - redirect to call
    window.location.href = data.call_url;
} else if (data.payment_required) {
    // Visitor must pay - redirect to payment
    window.location.href = paymentData.payment_url;
}
```

---

## Transaction Records

### When Owner Pays:
```python
QRWalletTransaction.objects.create(
    wallet=wallet,
    transaction_type='deduction',
    amount=1.00,
    description='Call charge' or 'SMS charge',
    notes='Masked call to +91XXXXXXXXXX'
)
```

### When Visitor Pays:
- Handled by visitor payment flow
- Creates separate transaction record
- Credits owner's wallet after payment

---

## Key Changes Made

### 1. Backend (views.py)
- ✅ Added wallet balance check in GET request
- ✅ Pass `payment_required`, `payer`, `cost_per_action` to template
- ✅ Deduct from owner wallet in POST if balance available

### 2. Backend (call_masking_views.py)
- ✅ Added wallet balance check before generating call
- ✅ Deduct ₹1 from owner if balance available
- ✅ Return `payment_required: true` if owner has ₹0
- ✅ Create transaction record for deduction

### 3. Frontend (gateway_access.html)
- ✅ Show payment notice only if `payment_required and payer == 'visitor'`
- ✅ Change button text based on payment requirement
- ✅ Handle `payment_required` response in JavaScript
- ✅ Redirect to payment if needed

---

## Testing Scenarios

### Scenario 1: Owner has ₹50 balance
1. Visitor scans QR
2. Clicks "Call Owner"
3. **Expected:** Directly redirected to call page
4. **Owner wallet:** ₹50 → ₹49

### Scenario 2: Owner has ₹0 balance
1. Visitor scans QR
2. Sees payment notice
3. Clicks "Pay ₹1 & Call"
4. **Expected:** Redirected to PhonePe payment
5. After payment → Redirected to call page

### Scenario 3: Owner has ₹1 balance (edge case)
1. Visitor scans QR
2. Clicks "Call Owner"
3. **Expected:** Directly redirected to call page
4. **Owner wallet:** ₹1 → ₹0
5. Next visitor will need to pay

---

## Benefits

✅ **Fair System** - Owner pays if they have balance
✅ **No Surprise Charges** - Visitor only pays if owner has ₹0
✅ **Transparent** - Clear payment notice when required
✅ **Automatic** - No manual intervention needed
✅ **Tracked** - All transactions recorded

---

## Result

**Payment logic now works correctly:**
- Owner has balance → Visitor contacts FREE
- Owner has ₹0 → Visitor pays ₹1
- Calls redirect directly (no intermediate pages)
- Messages send immediately (no delays)
