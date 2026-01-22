# ⚠️ IMPORTANT: How to Test the ₹1 Price

## The Problem

You're seeing ₹299 because you're using **OLD session data** from before the code change.

## The Solution

You MUST submit a **NEW order** from the beginning. Here's how:

### Step 1: Clear Browser Session
Choose ONE of these options:

**Option A: Use Incognito/Private Window**
- Chrome: Ctrl+Shift+N
- Firefox: Ctrl+Shift+P
- Edge: Ctrl+Shift+N

**Option B: Clear Browser Cookies**
- Press F12 → Application → Cookies → Delete all

**Option C: Close ALL browser windows and reopen**

### Step 2: Go to Order Form
1. Open: `http://localhost:8000/order-tag/`
2. Fill in ALL the details:
   - Name
   - Phone
   - Email
   - Address
   - City
   - State
   - PIN code
   - Quantity: 1

### Step 3: Check the Total
Before clicking "Proceed to Payment", look at the total on the form.
It should show: **₹1**

### Step 4: Submit the Form
Click "Proceed to Payment"

### Step 5: Verify Payment Page
Now you should see: **Pay ₹1 with Razorpay**

## Why This Happens

When you submitted the form earlier:
1. The backend calculated: 1 tag = ₹299
2. This was stored in your browser session
3. Even after restarting the server, your browser still has this old session

When you submit a NEW order:
1. The backend will calculate: 1 tag = ₹1
2. This new data will be stored in session
3. Payment page will show ₹1

## Quick Test

Run this in your browser console (F12 → Console):
```javascript
// This will show you the current total in the form
document.querySelector('[x-text*="total"]').textContent
```

If it shows "299", you're still on the old page. Refresh and check again.

## Still Not Working?

If you've done all the above and it's still showing ₹299:

1. Run: `clear_cache_and_test.cmd`
2. Restart Django server
3. Use incognito window
4. Go to `/order-tag/` (NOT `/order-tag/payment/`)
5. Submit a completely new order

---

**Remember:** You cannot just refresh the payment page. You must go back to the order form and submit a NEW order!
