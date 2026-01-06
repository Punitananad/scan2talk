# Unique Vehicle Number Validation

## Overview
Implemented validation to ensure **one vehicle number can only be registered with one QR code**. This prevents duplicate registrations and maintains data integrity.

## The Rule

### ✅ Allowed
- One vehicle number = One QR code
- Same user can have multiple QR codes (for different vehicles)
- Different users can have different vehicle numbers

### ❌ Not Allowed
- Same vehicle number on multiple QR codes
- Duplicate vehicle registrations
- Re-using an already registered vehicle number

## How It Works

### 1. Validation During Activation

When a user tries to activate a QR code:

```python
# Step 3: User enters vehicle details
vehicle_number = "HR12AM7522"  # Example

# System checks if this number already exists
existing_gateway = Gateway.objects.filter(
    identifier_text=vehicle_number,
    is_active=True
).first()

if existing_gateway:
    # REJECT: Show error page
    return "Vehicle Already Registered" page
else:
    # ALLOW: Continue with activation
    create_gateway_and_activate()
```

### 2. Database Index

Added an index for fast lookups:
```python
indexes = [
    models.Index(fields=['identifier_text', 'is_active']),
]
```

This makes the duplicate check very fast, even with millions of records.

## User Experience

### Scenario 1: First Registration ✅
```
User: Activates QR with vehicle "DL-01-AB-1234"
System: ✓ No existing registration found
Result: QR activated successfully
```

### Scenario 2: Duplicate Attempt ❌
```
User: Tries to activate another QR with "DL-01-AB-1234"
System: ✗ Vehicle already registered
Result: Shows error page with options
```

### Scenario 3: Multiple Vehicles ✅
```
User: Has QR for "DL-01-AB-1234" (Car)
User: Activates new QR for "DL-02-CD-5678" (Bike)
System: ✓ Different vehicle numbers
Result: Both QRs activated successfully
```

## Error Page Features

When duplicate is detected, user sees:

### 1. Clear Error Message
```
Vehicle Already Registered
Vehicle number HR12AM7522 is already registered with another QR code.
```

### 2. Explanation
- Why this restriction exists
- Benefits of one QR per vehicle
- System integrity reasons

### 3. Options
1. **Try Different Vehicle Number** - Go back and enter another vehicle
2. **Go to Homepage** - Exit the activation process
3. **Contact Support** - Get help if needed

## Files Modified

### 1. `apps/gateways/models.py`
- Added index on `identifier_text` and `is_active`
- Optimized for fast duplicate checking

### 2. `apps/gateways/qr_views.py`
- Added validation in `activate_qr_code()` function
- Checks for existing vehicle number before creating gateway
- Shows error page if duplicate found

### 3. `templates/gateways/activate_step3_details.html`
- Added warning message under vehicle number field
- "⚠️ Each vehicle number can only be registered once"

### 4. `templates/gateways/vehicle_already_registered.html` (NEW)
- Professional error page
- Clear explanation
- Multiple options for user
- Helpful guidance

## Code Implementation

### Validation Logic
```python
# In activate_qr_code() - Step 3
vehicle_number = request.POST.get('vehicle_number', '').strip().upper()

# Check for duplicates
existing_gateway = Gateway.objects.filter(
    identifier_text=vehicle_number,
    is_active=True
).first()

if existing_gateway:
    # Show error page
    context = {
        'vehicle_number': vehicle_number,
        'qr_code': qr_code,
        'existing_owner': existing_gateway.owner_name or 'Another user'
    }
    return render(request, 'gateways/vehicle_already_registered.html', context)

# Continue with activation...
```

### Database Query
```python
# Fast lookup using index
Gateway.objects.filter(
    identifier_text='HR12AM7522',  # Vehicle number
    is_active=True                  # Only active gateways
).first()
```

## Edge Cases Handled

### 1. Case Insensitive
```python
vehicle_number = vehicle_number.strip().upper()
# "hr12am7522" → "HR12AM7522"
# "Hr12Am7522" → "HR12AM7522"
```

### 2. Empty Vehicle Numbers
```python
# Only checks non-empty vehicle numbers
if not vehicle_number:
    return error("Vehicle number required")
```

### 3. Inactive Gateways
```python
# Only checks active gateways
is_active=True
# Deactivated gateways don't block new registrations
```

### 4. Different Context Types
```python
# Currently checks all active gateways
# Could be restricted to only 'vehicle' type if needed
```

## Testing

### Test Case 1: New Vehicle Number
```bash
# Activate QR with "TEST-001"
Result: ✓ Success
```

### Test Case 2: Duplicate Vehicle Number
```bash
# Activate QR with "TEST-001" (already exists)
Result: ✗ Error page shown
```

### Test Case 3: Same User, Different Vehicles
```bash
# User activates QR with "CAR-001"
# Same user activates QR with "BIKE-002"
Result: ✓ Both succeed
```

### Test Case 4: Case Variations
```bash
# First QR: "dl01ab1234"
# Second QR: "DL01AB1234"
Result: ✗ Detected as duplicate (case insensitive)
```

## Migration

### Created Migration
```
0004_gateway_gateways_identif_b05326_idx.py
```

### What It Does
- Adds database index on `identifier_text` and `is_active`
- Improves query performance
- No data changes

### Apply Migration
```bash
python manage.py migrate gateways
```

## Benefits

### 1. Data Integrity ✅
- No duplicate vehicle registrations
- Clean, consistent data
- Easy to track ownership

### 2. User Experience ✅
- Clear error messages
- Helpful guidance
- Multiple options

### 3. Performance ✅
- Fast duplicate checking
- Database index optimization
- Efficient queries

### 4. Security ✅
- Prevents fraud
- One official QR per vehicle
- Audit trail maintained

## Admin View

Admins can see in the dashboard:
- Vehicle number for each QR
- Owner name
- Activation date
- Access count

This helps identify and resolve any issues.

## Future Enhancements

### Possible Additions
1. **Allow Deactivation** - Let users deactivate old QR to register new one
2. **Transfer Ownership** - Transfer QR to new owner
3. **Temporary QRs** - Allow multiple QRs with expiry dates
4. **Admin Override** - Let admins bypass restriction if needed

## Summary

✅ **One vehicle number = One QR code**
✅ **Fast validation with database index**
✅ **Clear error messages for users**
✅ **Professional error page**
✅ **Case-insensitive checking**
✅ **Optimized performance**

The system now ensures data integrity while providing a great user experience!
