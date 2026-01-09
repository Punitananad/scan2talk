# Wallet System - Quick Start Guide

## What's New?

Your Gateway Platform now has a complete wallet management system! Users can recharge their wallets and pay for calls, while admins have full control over which QRs use paid or free services.

## Key Features

### For Users
- **Wallet Balance**: Track your balance and call credits
- **Easy Recharge**: Multiple payment options (₹10, ₹50, ₹100, ₹200, ₹500, ₹1000 or custom)
- **Simple Pricing**: ₹1 = 1 call credit
- **Transaction History**: See all your recharges and calls
- **No Expiry**: Credits never expire

### For Admins
- **Service Mode Control**: Decide if each QR uses:
  - Direct Service (Free)
  - Wallet Service (Paid - ₹1 per call)
  - Both Services (User choice)
- **Wallet Management**: Freeze/unfreeze wallets, add bonus credits
- **Order Management**: Track and manage all recharge orders
- **Complete Analytics**: View all transactions and usage

## Quick Access

### User URLs
- **Wallet Dashboard**: `/api/v1/auth/wallet/`
- **Recharge Wallet**: `/api/v1/auth/wallet/recharge/`
- **Navigation**: Click "Wallet" in the top menu

### Admin URLs
- **Wallet Admin**: `/admin/accounts/wallet/`
- **Transactions**: `/admin/accounts/wallettransaction/`
- **Recharge Orders**: `/admin/accounts/rechargeorder/`
- **QR Configuration**: `/admin/gateways/pregeneratedqr/`

## Admin Quick Actions

### Configure QR Service Mode
1. Go to `/admin/gateways/pregeneratedqr/`
2. Select QR codes
3. Choose action from dropdown:
   - "Enable wallet service (paid)"
   - "Enable direct service (free)"
   - "Enable both services"
4. Click "Go"

### Manage User Wallets
1. Go to `/admin/accounts/wallet/`
2. View all user balances
3. Actions available:
   - Freeze wallets
   - Unfreeze wallets
   - View transaction history

### Handle Recharge Orders
1. Go to `/admin/accounts/rechargeorder/`
2. Filter by status (pending, completed, failed)
3. Actions available:
   - Mark as completed (manual credit)
   - Mark as failed

## Payment Gateway Configuration

The system is pre-configured with:
- **API Key**: `5fb67f81-c6d6-4989-9bf4-e10c6db8ae8d`
- **Client ID**: `SU2504042021229572318914`

To customize, update in `.env`:
```
RECHARGE_GATEWAY_URL=https://api.recharge-gateway.com
```

## Testing the System

### Test User Wallet
1. Login as any user
2. Click "Wallet" in navigation
3. Click "Recharge Wallet"
4. Select amount and proceed

### Test QR Service Modes
1. Create/select a QR code in admin
2. Set service_mode to "wallet"
3. Set wallet_enabled to True
4. User will need credits to use this QR

### Test Admin Controls
1. Go to wallet admin
2. Select a wallet
3. Try freeze/unfreeze actions
4. View transaction history

## API Integration

### Check Balance
```python
GET /api/v1/auth/wallet/balance/
Authorization: Bearer <token>

Response:
{
  "success": true,
  "data": {
    "balance": 100.00,
    "call_credits": 100,
    "is_frozen": false,
    "can_make_calls": true
  }
}
```

### Create Recharge Order
```python
POST /api/v1/auth/wallet/recharge/create/
Authorization: Bearer <token>
Content-Type: application/json

{
  "amount": 100
}

Response:
{
  "success": true,
  "data": {
    "order_id": "ORD1704723456ABC123",
    "amount": 100.00,
    "credits": 100,
    "payment_url": "https://gateway.com/pay/...",
    "gateway_order_id": "GW123456"
  }
}
```

### Deduct Call Credit
```python
POST /api/v1/auth/wallet/deduct-credit/
Authorization: Bearer <token>
Content-Type: application/json

{
  "qr_code": "ABC12345",
  "notes": "Call initiated"
}

Response:
{
  "success": true,
  "data": {
    "remaining_credits": 99,
    "remaining_balance": 99.00
  }
}
```

## Common Scenarios

### Scenario 1: Free QR Code
```
Admin sets: service_mode = "direct"
Result: Users can call for free, no wallet needed
```

### Scenario 2: Paid QR Code
```
Admin sets: service_mode = "wallet"
Result: Users need ₹1 credit per call
```

### Scenario 3: Hybrid QR Code
```
Admin sets: service_mode = "both"
Result: Users can choose free or paid service
```

### Scenario 4: User Recharge
```
1. User clicks "Recharge Wallet"
2. Selects ₹100
3. Proceeds to payment
4. Completes payment
5. Gets 100 call credits instantly
```

### Scenario 5: Admin Bonus
```
1. Admin goes to wallet admin
2. Finds user wallet
3. Manually adds bonus credits
4. User sees increased balance
```

## Troubleshooting

### User Can't Make Calls
- Check if QR has wallet service enabled
- Verify user has sufficient credits
- Check if wallet is frozen

### Payment Not Credited
- Check recharge order status in admin
- Verify payment gateway response
- Manually complete order if payment verified

### Wallet Frozen
- Check frozen_reason in admin
- Unfreeze using admin action
- User can recharge after unfreezing

## Next Steps

1. **Test the system**: Create a test user and try recharging
2. **Configure QRs**: Set service modes for your QR codes
3. **Monitor usage**: Check wallet admin for analytics
4. **Customize pricing**: Adjust if needed (currently ₹1 = 1 call)

## Support

For detailed documentation, see `WALLET_SYSTEM_GUIDE.md`

For technical issues:
- Check Django admin logs
- Review transaction history
- Contact system administrator
