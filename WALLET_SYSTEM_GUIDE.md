# Wallet Management System Guide

## Overview
Complete wallet management system for Gateway Platform with recharge service integration and admin-controlled QR service modes.

## Features

### 1. User Wallet System
- **Balance Management**: Track user balance in rupees
- **Call Credits**: 1 rupee = 1 call credit
- **Transaction History**: Complete audit trail of all transactions
- **Wallet Status**: Active/Frozen status with admin control

### 2. Recharge Integration
- **Payment Gateway**: Integrated with recharge service
  - API Key: `5fb67f81-c6d6-4989-9bf4-e10c6db8ae8d`
  - Client ID: `SU2504042021229572318914`
- **Pricing**: ₹1 = 1 call credit
- **Instant Credit**: Balance updated immediately after successful payment

### 3. QR Service Modes (Admin Controlled)
Admin can configure each QR code with three service modes:

#### Direct Service (Free)
- Traditional free service
- No wallet required
- Unlimited calls

#### Wallet Service (Paid)
- Requires wallet balance
- ₹1 deducted per call
- User must have sufficient credits

#### Both Services
- User can choose between free or paid
- Flexibility for different use cases

## Database Models

### Wallet
```python
- user: OneToOne with User
- balance: Decimal (rupees)
- call_credits: Integer (number of calls)
- total_recharged: Decimal
- total_spent: Decimal
- total_calls_made: Integer
- is_active: Boolean
- is_frozen: Boolean
- frozen_reason: Text
```

### WalletTransaction
```python
- wallet: ForeignKey to Wallet
- transaction_type: Choice (recharge, call, refund, adjustment, bonus, penalty)
- amount: Decimal
- balance_after: Decimal
- credits_after: Integer
- payment_id: String
- payment_status: Choice (pending, completed, failed, cancelled)
- reference: String
- notes: Text
```

### RechargeOrder
```python
- user: ForeignKey to User
- wallet: ForeignKey to Wallet
- order_id: String (unique)
- amount: Decimal
- credits_to_add: Integer
- gateway_order_id: String
- gateway_payment_id: String
- gateway_signature: String
- status: Choice (created, pending, processing, completed, failed, cancelled, refunded)
```

### PreGeneratedQR (Updated)
```python
# New fields added:
- service_mode: Choice (direct, wallet, both)
- wallet_enabled: Boolean
- direct_service_enabled: Boolean
```

## API Endpoints

### Wallet APIs
```
GET  /api/v1/auth/wallet/balance/          - Get wallet balance
GET  /api/v1/auth/wallet/transactions/     - Get transaction history
POST /api/v1/auth/wallet/recharge/create/  - Create recharge order
POST /api/v1/auth/wallet/recharge/callback/ - Payment gateway callback
POST /api/v1/auth/wallet/deduct-credit/    - Deduct call credit (internal)
```

### Web Routes
```
GET  /api/v1/auth/wallet/                  - Wallet dashboard
GET  /api/v1/auth/wallet/recharge/         - Recharge page
POST /api/v1/auth/wallet/recharge/         - Process recharge
GET  /api/v1/auth/wallet/recharge/success/ - Success page
GET  /api/v1/auth/wallet/recharge/cancel/  - Cancel page
```

## Admin Features

### Wallet Management
1. **View All Wallets**: List of all user wallets with balances
2. **Freeze/Unfreeze**: Control wallet access
3. **Add Bonus Credits**: Give free credits to users
4. **View Transactions**: Complete transaction history
5. **Manual Adjustments**: Add/deduct balance manually

### QR Service Mode Control
1. **Enable Wallet Service**: Set QR to paid mode
2. **Enable Direct Service**: Set QR to free mode
3. **Enable Both**: Allow user choice
4. **Bulk Actions**: Update multiple QRs at once

### Recharge Order Management
1. **View All Orders**: Track all recharge attempts
2. **Manual Completion**: Complete failed orders manually
3. **Mark as Failed**: Cancel pending orders
4. **View Payment Details**: Gateway transaction info

## Usage Flow

### User Recharge Flow
1. User goes to wallet dashboard
2. Clicks "Recharge Wallet"
3. Selects amount (quick buttons or custom)
4. Proceeds to payment gateway
5. Completes payment
6. Redirected to success page
7. Wallet credited automatically

### Call Deduction Flow (Wallet Mode)
1. User scans QR code
2. System checks if QR has wallet service enabled
3. If yes, check user's wallet balance
4. If sufficient credits, deduct 1 credit
5. Process the call
6. Record transaction

### Admin Configuration Flow
1. Admin goes to Django admin
2. Selects PreGeneratedQR
3. Chooses QR codes to configure
4. Selects action:
   - "Enable wallet service (paid)"
   - "Enable direct service (free)"
   - "Enable both services"
5. QR codes updated instantly

## Setup Instructions

### 1. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Configure Payment Gateway
Add to `.env`:
```
RECHARGE_GATEWAY_URL=https://api.recharge-gateway.com
PLATFORM_DOMAIN=yourdomain.com
```

### 3. Create Superuser (if needed)
```bash
python manage.py createsuperuser
```

### 4. Access Admin Panel
```
http://localhost:8000/admin/
```

## Testing

### Test Wallet Creation
```python
from apps.accounts.wallet_service import WalletService
from apps.accounts.models import User

user = User.objects.first()
wallet = WalletService.get_or_create_wallet(user)
print(f"Balance: ₹{wallet.balance}, Credits: {wallet.call_credits}")
```

### Test Recharge
```python
# Create order
order = WalletService.create_recharge_order(user, amount=100)
print(f"Order ID: {order.order_id}")

# Simulate successful payment
order.mark_completed()
print(f"New balance: ₹{wallet.balance}, Credits: {wallet.call_credits}")
```

### Test Call Deduction
```python
# Deduct call credit
result = WalletService.process_call_charge(user, qr_code='TEST123')
print(f"Remaining credits: {result['remaining_credits']}")
```

## Security Features

1. **Encrypted Phone Numbers**: User phone numbers encrypted in database
2. **Transaction Audit**: Complete audit trail of all transactions
3. **Payment Verification**: Gateway signature verification
4. **Frozen Wallets**: Admin can freeze suspicious accounts
5. **IP Tracking**: All transactions logged with IP address

## Pricing Model

- **Base Rate**: ₹1 = 1 call credit
- **No Expiry**: Credits never expire
- **Minimum Recharge**: ₹1
- **Instant Credit**: Balance updated immediately

## Admin Actions

### Freeze Wallet
```python
# In admin, select wallets and choose "Freeze selected wallets"
# Or programmatically:
wallet.freeze(reason='Suspicious activity')
```

### Add Bonus Credits
```python
WalletService.add_admin_credit(user, amount=50, notes='Welcome bonus')
```

### Configure QR Service Mode
```python
# In admin, select QR codes and choose action:
# - "Enable wallet service (paid)"
# - "Enable direct service (free)"
# - "Enable both services"
```

## Monitoring

### Key Metrics
- Total wallet balance across platform
- Total recharges today/week/month
- Average recharge amount
- Call credit usage rate
- Failed payment rate

### Reports Available in Admin
1. Wallet balances by user
2. Transaction history
3. Recharge orders by status
4. QR service mode distribution

## Troubleshooting

### Payment Not Credited
1. Check RechargeOrder status in admin
2. Verify gateway_payment_id received
3. Manually mark order as completed if payment verified

### Wallet Frozen
1. Check frozen_reason in admin
2. Unfreeze using admin action
3. User can recharge after unfreezing

### Insufficient Credits Error
1. User needs to recharge wallet
2. Check if wallet is frozen
3. Verify QR has wallet service enabled

## Future Enhancements

1. **Bulk Recharge**: Corporate bulk credit purchase
2. **Referral Bonus**: Credits for referring users
3. **Auto-Recharge**: Automatic recharge when balance low
4. **Credit Packages**: Discounted bulk credit packages
5. **Wallet Transfer**: Transfer credits between users
6. **Refund System**: Automated refund processing

## Support

For issues or questions:
- Check transaction history in wallet dashboard
- Contact admin for wallet issues
- Review payment gateway logs for failed payments
