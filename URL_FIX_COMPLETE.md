# URL Routing Fix - Complete

## Problem
The login page was redirecting to `/api/v1/auth/login/` instead of `/accounts/login/` because:
1. All accounts URLs were mounted under `/api/v1/auth/` in the main URL config
2. This made web views (login, dashboard, wallet) accessible only via API paths
3. The API and web login routes had the same path pattern, causing conflicts

## Solution
Reorganized URL structure to separate web views from API endpoints:

### Main URLs (`gateway_platform/urls.py`)
**BEFORE:**
```python
path('api/v1/auth/', include('apps.accounts.urls')),
```

**AFTER:**
```python
path('accounts/', include('apps.accounts.urls')),  # Web views
# API routes moved to individual endpoints
```

### Accounts URLs (`apps/accounts/urls.py`)
Reorganized to clearly separate:
- **Web views** at root level (e.g., `login/`, `dashboard/`, `wallet/`)
- **API endpoints** under `api/` prefix (e.g., `api/login/`, `api/register/`)

## New URL Structure

### Web Views (User-facing pages)
- `/accounts/login/` - Phone login page
- `/accounts/logout/` - Logout
- `/accounts/dashboard/` - User dashboard
- `/accounts/profile/` - User profile
- `/accounts/wallet/` - Wallet dashboard
- `/accounts/wallet/recharge/` - Recharge wallet
- `/accounts/admin/dashboard/` - Admin super dashboard
- `/accounts/admin/categories/` - Manage categories
- `/accounts/admin/plans/` - Manage plans
- `/accounts/admin/qr-wallets/` - Manage QR wallets
- `/accounts/admin/users/` - User management

### API Endpoints (For programmatic access)
- `/accounts/api/register/` - User registration API
- `/accounts/api/login/` - User login API
- `/accounts/api/logout/` - User logout API
- `/accounts/api/profile/` - User profile API
- `/accounts/api/password/change/` - Password change API
- `/accounts/api/wallet/balance/` - Wallet balance API
- `/accounts/api/wallet/transactions/` - Wallet transactions API
- `/accounts/api/wallet/recharge/create/` - Create recharge order API
- `/accounts/api/wallet/deduct-credit/` - Deduct call credit API

## Benefits
1. ✅ Clear separation between web views and API endpoints
2. ✅ Web pages accessible at intuitive URLs (`/accounts/login/`)
3. ✅ API endpoints clearly marked with `/api/` prefix
4. ✅ No more URL conflicts
5. ✅ Better organization and maintainability

## Testing
Run these commands to verify:
```bash
python manage.py check
python manage.py shell -c "from django.urls import reverse; print(reverse('accounts:phone_login'))"
```

Expected output:
```
/accounts/login/
```

## Status
✅ **FIXED** - Login page now accessible at `/accounts/login/`
