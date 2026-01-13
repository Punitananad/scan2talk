# Order Tag Feature - Complete Guide

## Overview
Added a complete order flow for customers to purchase physical QR tags with delivery to their address and fake payment for testing.

## Features Implemented

### 1. Order Page (`/order-tag/`)
- **Form Fields:**
  - Full Name
  - Phone Number (10 digits)
  - Email Address
  - Street Address
  - City
  - State
  - PIN Code (6 digits)
  - Quantity (1, 2, 3, or 5 tags)

- **Pricing:**
  - 1 Tag: ₹299
  - 2 Tags: ₹549 (Save ₹49)
  - 3 Tags: ₹799 (Save ₹98)
  - 5 Tags: ₹1,299 (Save ₹196)
  - Free Shipping

- **Tag Preview:**
  - Shows image from `static/tag/final-poster.jpeg`
  - Lists features (waterproof, UV-resistant, easy installation, etc.)
  - Customer testimonial

### 2. Payment Page (`/order-tag/payment/`)
- **Fake Payment Form:**
  - Card Number (16 digits)
  - Expiry Date (MM/YY)
  - CVV (3 digits)
  - Cardholder Name

- **Test Mode Notice:**
  - Clear indication this is fake payment
  - No real charges made

- **Order Summary:**
  - Shows customer details
  - Displays total amount
  - Delivery location

### 3. Success Page (`/order-tag/success/`)
- **Order Confirmation:**
  - Unique Order ID (e.g., ORD12AB34CD)
  - Order details summary
  - Expected delivery date (7 days from order)

- **What's Next:**
  - Step-by-step guide:
    1. Order confirmation email
    2. Tag preparation
    3. Shipping (5-7 days)
    4. Activation instructions

- **Actions:**
  - Back to Home button
  - Email confirmation link
  - Support contact

## URLs Added

```python
/order-tag/              # Order form page
/order-tag/payment/      # Fake payment page
/order-tag/success/      # Order confirmation page
```

## Home Page Updates

Both "Get Your QR Code" buttons now link to `/order-tag/`:
1. Hero section button
2. CTA section button

## Technical Implementation

### Views (`apps/core/views.py`)

**OrderTagView:**
- GET: Shows order form
- POST: Stores order data in session, redirects to payment

**OrderPaymentView:**
- GET: Shows fake payment form with order summary
- POST: Generates order ID, stores completed order, redirects to success

**OrderSuccessView:**
- GET: Shows order confirmation with delivery date
- Requires completed order in session

### Session Data Flow

1. **Order Form** → Stores `order_data` in session
2. **Payment** → Reads `order_data`, generates order ID
3. **Success** → Reads `completed_order`, shows confirmation

### Data Stored in Session

```python
order_data = {
    'name': 'Customer Name',
    'phone': '9876543210',
    'email': 'customer@email.com',
    'address': 'Street Address',
    'city': 'City',
    'state': 'State',
    'pincode': '123456',
    'quantity': 1,
    'total': 299,
    'order_id': 'ORD12AB34CD'  # Added after payment
}
```

## Testing

### Test the Complete Flow:

1. **Visit Home Page:**
   ```
   http://192.168.1.75:8000/
   ```

2. **Click "Get Your QR Code"**

3. **Fill Order Form:**
   - Name: Test User
   - Phone: 9876543210
   - Email: test@example.com
   - Address: 123 Test Street
   - City: Mumbai
   - State: Maharashtra
   - PIN: 400001
   - Quantity: 1

4. **Click "Proceed to Payment"**

5. **Fill Fake Payment:**
   - Card: 1234567890123456
   - Expiry: 12/25
   - CVV: 123
   - Name: Test User

6. **Click "Pay ₹299"**

7. **See Success Page:**
   - Order ID displayed
   - Delivery date shown
   - Order summary visible

## Tag Preview Image

The order page displays the tag preview from:
```
static/tag/final-poster.jpeg
```

Make sure this image exists in your static files.

## Features

✅ Complete order flow (Form → Payment → Success)  
✅ Session-based data storage  
✅ Fake payment for testing  
✅ Order ID generation  
✅ Delivery date calculation  
✅ Tag preview with image  
✅ Responsive design  
✅ Form validation  
✅ Price calculation based on quantity  
✅ Free shipping included  

## Future Enhancements

- Email confirmation sending
- Order tracking system
- Admin panel for order management
- Real payment gateway integration
- Inventory management
- Shipping partner integration

## Notes

- This is a **fake payment system** for testing only
- No real charges are made
- No actual orders are stored in database (session only)
- Order data is cleared after viewing success page
- Delivery date is calculated as 7 days from order date
