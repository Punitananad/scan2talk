# QR Code Scan Flow Fix

## Problem
When users scanned an activated QR code, they were being redirected to the owner's login page instead of the contact page.

## Solution
Fixed the QR code scanning flow to properly handle different scenarios:

## Updated Flow

### Scenario 1: QR Code Not Activated (Owner First Time)
**URL**: `/g/<qr_code>/` or `/gateways/activate/<qr_code>/`

1. User scans QR code
2. System checks: QR status = 'available'
3. **Redirect to activation page** (`/gateways/activate/<qr_code>/`)
4. Owner enters phone number
5. Owner enters vehicle details
6. QR code gets activated
7. Owner is auto-logged in
8. Redirect to dashboard

### Scenario 2: QR Code Already Activated (Visitor Scanning)
**URL**: `/g/<qr_code>/`

1. Visitor scans QR code
2. System checks: QR status = 'activated'
3. **Redirect directly to contact page** (`/gateway/<qr_code>/`)
4. Visitor sees contact form to reach vehicle owner
5. Visitor can send message/call without login

### Scenario 3: Owner Scans Their Own Activated QR
**URL**: `/gateways/activate/<qr_code>/`

1. Owner scans their own QR code
2. System checks: QR status = 'activated' AND user is owner
3. If logged in: Show message "Already activated by you" → Redirect to dashboard
4. If not logged in: Show login option for owner

## Code Changes

### File: `apps/gateways/qr_views.py`

#### 1. `public_qr_access()` function
**Before**: Showed "not activated" template
**After**: Redirects to activation page for unactivated QR, contact page for activated QR

```python
def public_qr_access(request, qr_code):
    # If not activated, redirect to activation page (for owner)
    if qr.status != 'activated':
        return redirect('gateways:activate_qr', qr_code=qr_code)
    
    # If activated, show contact form (for visitors)
    if qr.gateway:
        return redirect('core:gateway_access', identifier=qr.qr_code)
```

#### 2. `activate_qr_code()` function
**Updated**: Better handling of already-activated QR codes

```python
# If already activated
if qr.status == 'activated':
    # Owner logged in → Dashboard
    if request.user.is_authenticated and request.user == qr.owner:
        return redirect('accounts:dashboard')
    
    # Owner not logged in → Show login option
    if qr.owner and not request.user.is_authenticated:
        return render(request, 'gateways/qr_already_activated.html', context)
    
    # Visitor → Contact page
    return redirect('core:gateway_access', identifier=qr.qr_code)
```

## URL Routes

### Public Access (Main Entry Point)
- `/g/<qr_code>/` → `public_qr_access()` → Routes to activation or contact page

### Activation Flow
- `/gateways/activate/<qr_code>/` → `activate_qr_code()` → Multi-step activation

### Contact Page
- `/gateway/<qr_code>/` → `GatewayAccessView` → Contact form (no login required)

## Benefits

1. **Visitors don't need to login** - They can directly contact vehicle owners
2. **Clear separation** - Activation flow for owners, contact flow for visitors
3. **Owner convenience** - Owners can access their dashboard when scanning their own QR
4. **No confusion** - Each user type gets the appropriate page

## Testing Scenarios

### Test 1: New QR Code
1. Scan unactivated QR → Should show activation page
2. Complete activation → Should redirect to dashboard

### Test 2: Visitor Scans Activated QR
1. Scan activated QR → Should show contact form
2. No login required
3. Can send message to owner

### Test 3: Owner Scans Own QR
1. Owner scans their activated QR
2. If logged in → Dashboard
3. If not logged in → Login option

### Test 4: Multiple Visitors
1. Multiple people scan same activated QR
2. All should see contact form
3. No interference between visitors
