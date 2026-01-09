# Wallet System - Test Mode Guide

## Test Mode is Now Enabled!

The wallet system is now running in **TEST MODE** which allows you to test all functionality without needing the actual payment gateway.

## How to Test

### 1. Access Wallet
- Login to your account
- Click "Wallet" in the top navigation
- You'll see your current balance (₹0.00 initially)

### 2. Test Recharge
1. Click "Recharge Wallet"
2. Select an amount (e.g., ₹100)
3. Click "Proceed to Payment"
4. You'll be redirected to a **Test Payment Page**
5. Click "Simulate Successful Payment"
6. Your wallet will be credited instantly!

### 3. Check Balance
- Return to wallet dashboard
- You'll see your new balance and call credits
- View transaction history

## Test Mode Features

### What Works in Test Mode
✅ Wallet creation
✅ Balance display
✅ Recharge simulation
✅ Transaction history
✅ Call credit tracking
✅ Admin wallet management
✅ QR service mode configuration

### What's Simulated
- Payment gateway connection
- Payment processing
- Payment verification
- Gateway callbacks

## Switching to Production Mode

When you're ready to use the real payment gateway:

### 1. Update `.env` file:
```env
RECHARGE_TEST_MODE=False
RECHARGE_GATEWAY_URL=https://your-actual-gateway.com
```

### 2. Configure Payment Gateway
- Ensure API Key and Client ID are correct in `wallet_service.py`
- Test gateway connection
- Verify callback URLs are accessible

### 3. Test Production
- Try a small recharge first
- Verify payment completion
- Check wallet credit

## Current Configuration

### Test Mode Settings
```python
RECHARGE_TEST_MODE = True  # Enabled by default
RECHARGE_GATEWAY_URL = 'https://api.recharge-gateway.com'
```

### Payment Gateway Credentials
```python
API_KEY = '5fb67f81-c6d6-4989-9bf4-e10c6db8ae8d'
CLIENT_ID = 'SU2504042021229572318914'
```

## Testing Scenarios

### Scenario 1: New User Recharge
1. Create new user account
2. Go to wallet (auto-created with ₹0)
3. Recharge ₹50
4. Verify 50 credits added

### Scenario 2: Multiple Recharges
1. Recharge ₹10
2. Check balance (₹10, 10 credits)
3. Recharge ₹20
4. Check balance (₹30, 30 credits)

### Scenario 3: Admin Management
1. Login to admin panel
2. Go to Wallets
3. View user balances
4. Try freeze/unfreeze actions

### Scenario 4: QR Service Modes
1. Go to PreGeneratedQR admin
2. Select a QR code
3. Set service_mode to "wallet"
4. User will need credits to use this QR

## URLs for Testing

### User URLs
- Wallet Dashboard: `http://localhost:8000/api/v1/auth/wallet/`
- Recharge: `http://localhost:8000/api/v1/auth/wallet/recharge/`
- Test Payment: `http://localhost:8000/api/v1/auth/wallet/test-payment/{order_id}/`

### Admin URLs
- Wallets: `http://localhost:8000/admin/accounts/wallet/`
- Transactions: `http://localhost:8000/admin/accounts/wallettransaction/`
- Orders: `http://localhost:8000/admin/accounts/rechargeorder/`
- QR Codes: `http://localhost:8000/admin/gateways/pregeneratedqr/`

## API Testing

### Get Balance
```bash
curl -X GET http://localhost:8000/api/v1/auth/wallet/balance/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Recharge Order
```bash
curl -X POST http://localhost:8000/api/v1/auth/wallet/recharge/create/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100}'
```

## Troubleshooting

### Issue: Payment page shows error
**Solution**: Make sure you're logged in and the order belongs to your user

### Issue: Credits not added after payment
**Solution**: Check RechargeOrder status in admin - it should be "completed"

### Issue: Can't access wallet
**Solution**: Wallet is auto-created on first access - just refresh the page

### Issue: Test payment button doesn't work
**Solution**: Make sure CSRF token is valid - try logging out and back in

## Production Checklist

Before going live:

- [ ] Set `RECHARGE_TEST_MODE=False` in `.env`
- [ ] Configure actual payment gateway URL
- [ ] Verify API credentials
- [ ] Test with small amount
- [ ] Set up payment gateway webhooks
- [ ] Configure SSL certificates
- [ ] Test callback URLs are accessible
- [ ] Set up monitoring for failed payments
- [ ] Configure email notifications
- [ ] Test refund process

## Support

For issues:
1. Check Django logs
2. Review transaction history in admin
3. Verify order status in RechargeOrder admin
4. Check wallet balance in Wallet admin

## Next Steps

1. **Test the system**: Try recharging your wallet
2. **Configure QRs**: Set service modes in admin
3. **Monitor usage**: Check wallet admin for analytics
4. **Plan production**: When ready, switch to production mode

Enjoy testing the wallet system! 🎉
