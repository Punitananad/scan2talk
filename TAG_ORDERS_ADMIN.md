# Tag Orders Admin Panel - Complete Guide

## Overview
Added a complete admin panel for managing physical QR tag orders with database storage, status tracking, and delivery management.

## Features Implemented

### 1. Database Model (`TagOrder`)
**Location:** `apps/core/models.py`

**Fields:**
- `order_id`: Unique order identifier (e.g., ORD12AB34CD)
- `name`, `phone`, `email`: Customer details
- `address`, `city`, `state`, `pincode`: Delivery address
- `quantity`: Number of tags ordered
- `total_amount`: Order total
- `status`: Order status (pending, processing, shipped, delivered, cancelled)
- `tracking_number`: Shipping tracking number
- `notes`: Admin notes
- `created_at`, `updated_at`: Timestamps
- `shipped_at`, `delivered_at`: Status timestamps

### 2. Admin Orders Page (`/api/v1/auth/admin/orders/`)
**Location:** `templates/admin/manage_tag_orders.html`

**Features:**
- **Statistics Dashboard:**
  - Total orders count
  - Pending orders count
  - Total tags sold
  - Total revenue

- **Filters:**
  - Status filter (All, Pending, Processing, Shipped, Delivered, Cancelled)
  - Search by Order ID, Name, Phone, or Email

- **Orders Table:**
  - Order ID
  - Customer details (name, phone, email)
  - Full delivery address
  - Quantity
  - Amount
  - Status badge (color-coded)
  - Order date
  - Update action button

- **Update Modal:**
  - Change order status
  - Add tracking number
  - Add admin notes
  - AJAX update (no page reload)

### 3. Order Status Flow

```
pending → processing → shipped → delivered
                    ↓
                cancelled
```

**Status Colors:**
- Pending: Yellow
- Processing: Blue
- Shipped: Indigo
- Delivered: Green
- Cancelled: Gray

### 4. Admin Dashboard Integration

Added "Tag Orders" card to admin dashboard:
- Icon: 📦
- Link: `/api/v1/auth/admin/orders/`
- Shows in secondary actions grid

## How to Use

### For Admin:

1. **Access Orders Page:**
   - Login as admin/staff
   - Go to Admin Dashboard
   - Click "Tag Orders" card

2. **View Orders:**
   - See all orders in table format
   - Check statistics at top
   - Use filters to find specific orders

3. **Update Order Status:**
   - Click "Update" button on any order
   - Select new status from dropdown
   - Add tracking number (optional)
   - Add notes (optional)
   - Click "Update Order"

4. **Track Deliveries:**
   - Filter by "Shipped" status
   - See all orders awaiting delivery
   - Update to "Delivered" when confirmed

### For Customers:

Orders are automatically created when they complete payment on the order page. The flow is:

1. Customer fills order form
2. Completes fake payment
3. Order saved to database with status "pending"
4. Customer sees success page with order ID

## API Endpoints

### View Orders
```
GET /api/v1/auth/admin/orders/
```
Query parameters:
- `status`: Filter by status (all, pending, processing, shipped, delivered, cancelled)
- `search`: Search by order ID, name, phone, or email

### Update Order Status
```
POST /api/v1/auth/admin/orders/<order_id>/update/
```
Body:
- `status`: New status
- `tracking_number`: Tracking number (optional)
- `notes`: Admin notes (optional)

Returns JSON:
```json
{
  "success": true,
  "message": "Order ORD12AB34CD updated to Shipped"
}
```

## Database Schema

```sql
CREATE TABLE tag_orders (
    id UUID PRIMARY KEY,
    order_id VARCHAR(20) UNIQUE,
    name VARCHAR(200),
    phone VARCHAR(15),
    email VARCHAR(254),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    quantity INTEGER,
    total_amount DECIMAL(10, 2),
    status VARCHAR(20),
    tracking_number VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    shipped_at TIMESTAMP NULL,
    delivered_at TIMESTAMP NULL
);

CREATE INDEX idx_order_id ON tag_orders(order_id);
CREATE INDEX idx_status_created ON tag_orders(status, created_at);
CREATE INDEX idx_phone ON tag_orders(phone);
CREATE INDEX idx_email ON tag_orders(email);
```

## Testing

### Test Order Creation:

1. Visit: `http://192.168.1.75:8000/order-tag/`
2. Fill form with test data
3. Complete fake payment
4. Check admin panel for new order

### Test Order Management:

1. Login as admin
2. Go to Tag Orders page
3. Find the test order
4. Click "Update"
5. Change status to "Processing"
6. Add tracking number: "TEST123456"
7. Add note: "Test order for verification"
8. Click "Update Order"
9. Verify order updated in table

## Statistics Tracked

- **Total Orders**: All orders ever placed
- **Pending Orders**: Orders awaiting processing
- **Total Tags**: Sum of all quantities ordered
- **Total Revenue**: Sum of all order amounts

## Features

✅ Complete order management system  
✅ Database storage with migrations  
✅ Admin panel with filters and search  
✅ Status tracking with timestamps  
✅ AJAX updates (no page reload)  
✅ Color-coded status badges  
✅ Tracking number support  
✅ Admin notes field  
✅ Statistics dashboard  
✅ Integrated with admin dashboard  

## Future Enhancements

- Email notifications to customers on status change
- Bulk status updates
- Export orders to CSV/Excel
- Print shipping labels
- Integration with shipping APIs
- Customer order tracking page
- SMS notifications
- Automated status updates

## Notes

- Orders are stored permanently in database
- Status changes are logged with timestamps
- Admin can add notes for internal tracking
- Tracking numbers can be added when order ships
- All orders start with "pending" status
- Delivered orders show delivery timestamp
