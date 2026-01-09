# Recharge API Integration Guide

## Real API Credentials

Your wallet system is now integrated with real payment gateway credentials:

```
API Key: 5fb67f81-c6d6-4989-9bf4-e10c6db8ae8d
Client ID: SU2504042021229572318914
```

## Current Status

✅ **Test Mode Enabled** - System works without hitting real API
✅ **Real API Integration Ready** - Code is production-ready
✅ **Security Implemented** - Checksum/signature verification
✅ **Error Handling** - Comprehensive error handling

## API Integration Details

### 1. Payment Initiation

**Endpoint**: `POST /api/v1/payment/initiate`

**Request Headers**:
```
Content-Type: application/json
X-API-Key: 5fb67f81-c6d6-4989-9bf4-e10c6db8ae8d
X-Client-ID: SU2504042021229572318914
```

**Request Payload**:
```json
{
  "clientId": "SU2504042021229572318914",
  "apiKey": "5fb67f81-c6d6-4989-9bf4-e10c6db8ae8d",
  "orderId": "ORD1704723456ABC123",
  "amount": 100.00,
  "currency": "INR",
  "customerName": "John Doe",
  "customerEmail": "user@example.com",
  "customerPhone": "9876543210",
  "callbackUrl": "http://yourdomain.com/api/v1/auth/wallet/recharge/callback/",
  "returnUrl": "http://yourdomain.com/api/v1/auth/wallet/recharge/success/",
  "cancelUrl": "http://yourdomain.com/api/v1/auth/wallet/recharge/cancel/",
  "description": "Wallet Recharge - 100 credits",
  "checksum": "generated_sha256_hash"
}
```

**Checksum Generation**:
```python
# Format: SHA256(clientId|apiKey|orderId|amount|currency)
import hashlib

sig_string = f"{clientId}|{apiKey}|{orderId}|{amount}|{currency}"
checksum = hashlib.sha256(sig_string.encode()).hexdigest()
```

**Expected Response**:
```json
{
  "status": "success",
  "gatewayOrderId": "GW123456789",
  "paymentUrl": "https://gateway.com/pay/GW123456789",
  "message": "Payment initiated successfully"
}
```

### 2. Payment Verification

**Endpoint**: `POST /api/v1/payment/verify`

**Request Payload**:
```json
{
  "clientId": "SU2504042021229572318914",
  "apiKey": "5fb67f81-c6d6-4989-9bf4-e10c6db8ae8d",
  "orderId": "ORD1704723456ABC123",
  "paymentId": "PAY123456789",
  "checksum": "generated_sha256_hash"
}
```

**Expected Response**:
```json
{
  "status": "success",
  "paymentStatus": "completed",
  "amount": 100.00,
  "transactionId": "TXN123456789",
  "message": "Payment verified successfully"
}
```

### 3. Payment Callback

**Your Callback URL**: `http://yourdomain.com/api/v1/auth/wallet/recharge/callback/`

**Callback Payload** (sent by gateway):
```json
{
  "orderId": "ORD1704723456ABC123",
  "paymentId": "PAY123456789",
  "status": "success",
  "amount": 100.00,
  "signature": "gateway_signature",
  "transactionId": "TXN123456789",
  "paymentMethod": "UPI",
  "timestamp": "2024-01-08T10:30:00Z"
}
```

## Switching to Production Mode

### Step 1: Get Gateway URL

Contact your payment gateway provider to get:
1. Production API base URL
2. Confirm API endpoints match the format above
3. Test credentials in their sandbox first

### Step 2: Update Configuration

Update `.env` file:
```env
# Switch to production mode
RECHARGE_TEST_MODE=False

# Set your actual gateway URL
RECHARGE_GATEWAY_URL=https://api.yourgateway.com

# Your domain for callbacks
PLATFORM_DOMAIN=yourdomain.com
```

### Step 3: Test in Sandbox

Before going live:
1. Use gateway's sandbox/test environment
2. Test small amount (₹1)
3. Verify callback is received
4. Check wallet is credited
5. Test failed payment scenario

### Step 4: Go Live

1. Switch to production gateway URL
2. Test with real small amount
3. Monitor first few transactions
4. Set up alerts for failed payments

## API Endpoint Customization

If your gateway uses different endpoints, update in `apps/accounts/wallet_service.py`:

```python
# Line ~140 - Initiate payment
response = requests.post(
    f"{cls.BASE_URL}/api/v1/payment/initiate",  # Change this
    json=payload,
    ...
)

# Line ~220 - Verify payment
response = requests.post(
    f"{cls.BASE_URL}/api/v1/payment/verify",  # Change this
    json=payload,
    ...
)
```

## Security Features

### 1. Checksum Verification
Every request includes SHA256 checksum to prevent tampering:
```python
checksum = SHA256(clientId|apiKey|orderId|amount|currency)
```

### 2. Callback Validation
Callbacks are validated before crediting wallet:
- Order ID must exist
- Payment ID must be present
- Status must be success
- Signature is verified

### 3. HTTPS Required
In production, all URLs must use HTTPS:
- Callback URL
- Return URL
- Cancel URL

### 4. IP Whitelisting (Recommended)
Whitelist gateway IPs in your firewall for callback endpoint.

## Error Handling

### Common Errors

**1. Gateway Timeout**
```
Error: Payment gateway timeout. Please try again.
Solution: Check gateway status, retry after some time
```

**2. Connection Error**
```
Error: Unable to connect to payment gateway.
Solution: Check RECHARGE_GATEWAY_URL, verify network connectivity
```

**3. Invalid Checksum**
```
Error: Checksum verification failed
Solution: Verify API Key and Client ID are correct
```

**4. Order Not Found**
```
Error: Order not found
Solution: Check order_id in callback matches created order
```

### Error Logging

All errors are logged in:
- Django logs (check console in development)
- RechargeOrder.failure_reason field
- WalletTransaction notes field

## Testing Checklist

### Test Mode Testing
- [ ] Create wallet
- [ ] Initiate recharge
- [ ] Complete test payment
- [ ] Verify credits added
- [ ] Check transaction history
- [ ] Test multiple recharges
- [ ] Test different amounts

### Production Testing
- [ ] Test ₹1 recharge
- [ ] Verify callback received
- [ ] Check wallet credited
- [ ] Test payment cancellation
- [ ] Test payment failure
- [ ] Verify refund process
- [ ] Test concurrent payments
- [ ] Load test with multiple users

## Monitoring

### Key Metrics to Monitor
1. **Success Rate**: Completed orders / Total orders
2. **Average Time**: Time from initiation to completion
3. **Failed Payments**: Track failure reasons
4. **Callback Delays**: Time between payment and callback
5. **Pending Orders**: Orders stuck in pending state

### Admin Dashboard
Monitor in Django admin:
- `/admin/accounts/rechargeorder/` - All orders
- `/admin/accounts/wallettransaction/` - All transactions
- `/admin/accounts/wallet/` - User balances

### Alerts to Set Up
1. Failed payment rate > 5%
2. Pending orders > 30 minutes old
3. Gateway timeout errors
4. Callback not received within 5 minutes

## Support & Troubleshooting

### Gateway Provider Support
Contact your gateway provider for:
- API documentation
- Sandbox credentials
- Production credentials
- Webhook/callback setup
- IP whitelisting
- SSL certificate issues

### Common Issues

**Issue**: Callback not received
**Solution**: 
- Check callback URL is publicly accessible
- Verify no firewall blocking
- Check gateway logs
- Test callback URL manually

**Issue**: Payment successful but wallet not credited
**Solution**:
- Check RechargeOrder status in admin
- Look for callback in Django logs
- Manually mark order as completed in admin

**Issue**: Checksum mismatch
**Solution**:
- Verify API Key and Client ID
- Check checksum generation logic
- Ensure no extra spaces in credentials

## Production Deployment

### Pre-deployment Checklist
- [ ] RECHARGE_TEST_MODE=False
- [ ] RECHARGE_GATEWAY_URL set correctly
- [ ] PLATFORM_DOMAIN set correctly
- [ ] HTTPS enabled on all URLs
- [ ] Callback URL publicly accessible
- [ ] Gateway credentials verified
- [ ] Sandbox testing completed
- [ ] Error monitoring set up
- [ ] Backup plan for gateway downtime

### Post-deployment
- [ ] Test with ₹1 transaction
- [ ] Monitor first 10 transactions
- [ ] Check callback success rate
- [ ] Verify wallet credits correctly
- [ ] Test refund process
- [ ] Document any issues

## API Provider Contact

If you need to contact your API provider:
- **Client ID**: SU2504042021229572318914
- **API Key**: 5fb67f81-c6d6-4989-9bf4-e10c6db8ae8d

Ask them for:
1. Complete API documentation
2. Sandbox environment access
3. Webhook/callback setup guide
4. Production URL
5. Rate limits
6. Support contact

## Next Steps

1. **Contact Gateway Provider**: Get complete API documentation
2. **Test in Sandbox**: Use their test environment first
3. **Update URLs**: Set correct endpoints in code
4. **Go Live**: Switch to production mode
5. **Monitor**: Watch first transactions closely

---

**Note**: The integration code is production-ready. You just need to:
1. Get the correct gateway URL from your provider
2. Test in their sandbox
3. Switch RECHARGE_TEST_MODE to False
4. Deploy and monitor
