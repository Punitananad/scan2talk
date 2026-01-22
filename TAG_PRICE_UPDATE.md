# ✅ Tag Price Updated to ₹1

## Changes Made

The QR tag price has been updated from ₹299 to **₹1** for testing purposes.

## Files Updated

### 1. `templates/core/order_tag.html`
**Status:** ✅ Updated

JavaScript pricing:
```javascript
basePrice: 1,
subtotal: 1,
total: 1,
```

### 2. `apps/core/views.py` - `OrderTagView.post()`
**Status:** ✅ Updated

**Before:**
```python
prices = {1: 299, 2: 549, 3: 799, 5: 1299}
order_data['total'] = prices.get(order_data['quantity'], 299)
```

**After:**
```python
BASE_PRICE = 1
order_data['total'] = BASE_PRICE * quantity
```

### 3. `templates/core/home_new.html`
**Status:** ✅ Updated

FAQ section now mentions ₹1 instead of ₹299.

## How It Works

### Single Tag:
- Quantity: 1
- Price: ₹1 per tag
- Total: **₹1**

### Multiple Tags:
- Quantity: 2
- Price per tag: ₹1
- Total: **₹2**

### Custom Quantity:
- Quantity: 10
- Price per tag: ₹1
- Total: **₹10**

## Razorpay Integration

The Razorpay payment will now charge:
- Formula: ₹1 × quantity
- Minimum: ₹1 (for 1 tag)
- Example: 5 tags = ₹5

## Testing

1. Go to `/order-tag/`
2. Fill in delivery details
3. Select quantity (e.g., 1)
4. See total: **₹1**
5. Click "Proceed to Payment"
6. Razorpay will show: **Pay ₹1**

## Important Note

**You need to clear your browser session or start a new order** because the old order data (with ₹299) is stored in the session. 

To test the new ₹1 pricing:
1. Clear browser cookies/session, OR
2. Open in incognito/private window, OR
3. Go back to `/order-tag/` and submit a new order

## To Change Price Later

### Frontend (JavaScript):
Edit `templates/core/order_tag.html` line ~285:
```javascript
basePrice: 1,  // Change to desired price
```

### Backend (Python):
Edit `apps/core/views.py` in `OrderTagView.post()`:
```python
BASE_PRICE = 1  # Change to desired price
order_data['total'] = BASE_PRICE * quantity
```

**Make sure both match!**

Examples:
- `BASE_PRICE = 299` for ₹299 per tag
- `BASE_PRICE = 499` for ₹499 per tag
- `BASE_PRICE = 99` for ₹99 per tag

---

**Current Status:** ✅ Tag price is now ₹1 per tag throughout the system (frontend + backend)!
