# Prepaid Pay-Per-Use System Implementation

## Overview
For QR codes with "Prepaid - Recharge Required" category, implement a pay-per-use system where:
- Owner's wallet is auto-created (can be ₹0)
- If owner has balance: Deduct from owner's wallet
- If owner has ₹0: Visitor pays ₹1 per call/message
- Owner registers once, then visitors can directly contact

## System Flow

### 1. QR Activation (Owner Registration)
```
Owner scans QR → Enters details → QR Wallet created automatically
- Wallet balance: ₹0 (default)
- Category: Prepaid
- Status: Active
```

### 2. Visitor Contacts Owner

#### Scenario A: Owner Has Balance
```
Visitor scans QR → Contact page → Sends message/call
→ Check owner's wallet balance
→ If balance > 0: Deduct ₹1 from owner's wallet
→ Send message/initiate call
→ Success
```

#### Scenario B: Owner Has ₹0 Balance
```
Visitor scans QR → Contact page → Sends message/call
→ Check owner's wallet balance
→ If balance = 0: Show payment page to visitor
→ Visitor pays ₹1 via PhonePe
→ Payment success → Send message/initiate call
→ Success
```

## Implementation Components

### 1. Auto-Create QR Wallet on Activation
**File**: `apps/gateways/qr_views.py` - `activate_qr_code()` function

```python
# After QR activation, create wallet if category is prepaid
if qr.category and qr.category.category_type == 'prepaid':
    from apps.accounts.recharge_models import QRWallet
    QRWallet.objects.get_or_create(
        qr_code=qr,
        defaults={
            'category': qr.category,
            'balance': 0.00,
            'is_active': True
        }
    )
```

### 2. Check Balance Before Contact
**File**: `apps/core/views.py` - Gateway access view

```python
def gateway_access(request, identifier):
    # Get QR and check category
    qr = get_qr_by_identifier(identifier)
    
    if qr.category and qr.category.category_type == 'prepaid':
        # Check wallet balance
        wallet = qr.qr_wallet
        
        if wallet.balance >= 1.00:
            # Owner has balance - proceed normally
            payment_required = False
            payer = 'owner'
        else:
            # Owner has ₹0 - visitor must pay
            payment_required = True
            payer = 'visitor'
            
        context = {
            'payment_required': payment_required,
            'payer': payer,
            'cost': 1.00
        }
```

### 3. Payment Flow for Visitor

#### Template: Show Payment Option
```html
{% if payment_required and payer == 'visitor' %}
<div class="payment-notice">
    <p>Owner's wallet is empty. Pay ₹1 to send this message.</p>
    <button onclick="initiatePayment()">Pay ₹1 & Send</button>
</div>
{% endif %}
```

#### Process Payment
```python
def process_visitor_payment(request, qr_id):
    # Initiate PhonePe payment for ₹1
    # On success, send message/call
    # Store transaction
```

### 4. Deduct from Owner's Wallet
```python
def deduct_from_owner_wallet(qr, amount=1.00):
    wallet = qr.qr_wallet
    if wallet.balance >= amount:
        wallet.balance -= amount
        wallet.save()
        
        # Create transaction record
        QRWalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='deduction',
            amount=amount,
            description='Message/Call charge'
        )
        return True
    return False
```

## Database Changes

### QRWallet Model (Already exists)
- `balance`: Decimal field (can be 0)
- `category`: ForeignKey to RechargeCategory
- `is_active`: Boolean

### New: VisitorPayment Model
```python
class VisitorPayment(models.Model):
    qr_code = ForeignKey(PreGeneratedQR)
    visitor_phone = CharField(max_length=20)
    amount = DecimalField(default=1.00)
    payment_id = CharField(max_length=100)
    status = CharField(choices=['pending', 'success', 'failed'])
    created_at = DateTimeField(auto_now_add=True)
```

## URL Routes

```python
# Visitor payment
path('pay/<uuid:qr_id>/', views.visitor_payment_page, name='visitor_payment'),
path('pay/<uuid:qr_id>/process/', views.process_visitor_payment, name='process_visitor_payment'),
path('pay/<uuid:qr_id>/callback/', views.visitor_payment_callback, name='visitor_payment_callback'),
```

## Cost Structure

### For Owner (Prepaid Category)
- **Message**: ₹1 per message (deducted from owner's wallet)
- **Call**: ₹1 per call (deducted from owner's wallet)
- **If balance = 0**: Visitor pays instead

### For Visitor (When Owner's Balance = 0)
- **Message**: ₹1 (one-time payment)
- **Call**: ₹1 (one-time payment)

## User Experience

### Owner's Perspective
1. Activates QR code (one-time registration)
2. Wallet created with ₹0 balance
3. Can recharge wallet anytime
4. If balance > 0: Receives messages/calls (₹1 deducted per contact)
5. If balance = 0: Still receives messages/calls (visitor pays)

### Visitor's Perspective
1. Scans QR code
2. Sees contact form
3. If owner has balance: Sends message/call for free
4. If owner has ₹0: Prompted to pay ₹1
5. Pays ₹1 via PhonePe
6. Message/call sent successfully

## Benefits

1. **Low Barrier**: Owner can start with ₹0
2. **Always Available**: Contact always works (visitor pays if needed)
3. **Fair System**: Owner pays when they have balance, visitor pays when owner doesn't
4. **Revenue Model**: Platform earns from both owner recharges and visitor payments
5. **No Spam**: ₹1 charge prevents spam

## Implementation Priority

1. ✅ Auto-create wallet on QR activation
2. ✅ Check balance before contact
3. ⚠️ Visitor payment flow (PhonePe integration)
4. ⚠️ Deduction logic
5. ⚠️ Transaction tracking
6. ⚠️ UI updates for payment prompts

## Testing Scenarios

1. Owner activates QR with prepaid category → Wallet created with ₹0
2. Visitor contacts → Owner has ₹0 → Visitor pays ₹1 → Message sent
3. Owner recharges ₹10 → Visitor contacts → ₹1 deducted from owner → Message sent
4. Owner balance reaches ₹0 → Next visitor pays ₹1 → Message sent
5. Free category QR → No payment required from anyone
