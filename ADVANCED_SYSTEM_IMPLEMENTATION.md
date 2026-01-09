# Advanced QR Wallet & Admin System Implementation Guide

## Overview
Complete advanced system with:
- Individual QR wallets
- Category system (Free, Prepaid, Postpaid, Trial)
- Recharge plans
- Super admin dashboard
- Full control over everything

## Files Created

### Models
1. `apps/accounts/recharge_models.py` - New models:
   - `RechargeCategory` - Categories for QR codes
   - `RechargePlan` - Recharge plans
   - `QRWallet` - Individual wallet for each QR
   - `QRWalletTransaction` - Transaction history

### Views
2. `apps/accounts/admin_views.py` - Admin views:
   - `admin_super_dashboard` - Main admin dashboard
   - `manage_categories` - Create/edit categories
   - `manage_plans` - Create/edit plans
   - `manage_qr_wallets` - Manage QR wallets
   - `admin_credit_qr_wallet` - Add credits
   - `admin_assign_category` - Assign category
   - `admin_suspend_wallet` - Suspend/unsuspend
   - `admin_user_management` - User management

### Templates
3. `templates/admin/super_dashboard.html` - Super admin dashboard
4. `templates/admin/manage_categories.html` - Category management
5. `templates/admin/manage_plans.html` - Plan management
6. `templates/admin/manage_qr_wallets.html` - QR wallet management
7. `templates/admin/user_management.html` - User management

### Configuration
8. Updated `apps/accounts/urls.py` - Added admin routes
9. Updated `templates/base.html` - Added Admin dropdown menu

## Implementation Steps

### Step 1: Create Database Migrations

```bash
# Create migrations for new models
python manage.py makemigrations accounts

# Apply migrations
python manage.py migrate
```

### Step 2: Import New Models

Update `apps/accounts/models.py` to import the new models:

```python
# At the end of apps/accounts/models.py
from .recharge_models import (
    RechargeCategory,
    RechargePlan,
    QRWallet,
    QRWalletTransaction
)

__all__ = [
    'User',
    'UserProfile',
    'LoginAttempt',
    'RechargeCategory',
    'RechargePlan',
    'QRWallet',
    'QRWalletTransaction',
]
```

### Step 3: Register Models in Admin

Update `apps/accounts/admin.py`:

```python
from .recharge_models import (
    RechargeCategory,
    RechargePlan,
    QRWallet,
    QRWalletTransaction
)

@admin.register(RechargeCategory)
class RechargeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'is_active', 'is_default']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name']

@admin.register(RechargePlan)
class RechargePlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'message_credits', 'call_minutes', 'is_popular', 'is_active']
    list_filter = ['is_popular', 'is_active']
    search_fields = ['name']

@admin.register(QRWallet)
class QRWalletAdmin(admin.ModelAdmin):
    list_display = ['qr_code', 'category', 'balance', 'message_credits', 'call_minutes', 'is_active', 'is_suspended']
    list_filter = ['category', 'is_active', 'is_suspended']
    search_fields = ['qr_code__qr_code']
    raw_id_fields = ['qr_code']

@admin.register(QRWalletTransaction)
class QRWalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'transaction_type', 'amount', 'message_credits', 'call_minutes', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['wallet__qr_code__qr_code']
    raw_id_fields = ['wallet']
```

### Step 4: Auto-Create QR Wallet on QR Creation

Update `apps/gateways/qr_models.py` - Add signal to auto-create wallet:

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=PreGeneratedQR)
def create_qr_wallet(sender, instance, created, **kwargs):
    """Auto-create wallet when QR is created"""
    if created:
        from apps.accounts.recharge_models import QRWallet, RechargeCategory
        
        # Get default category
        default_category = RechargeCategory.objects.filter(is_default=True).first()
        
        # Create wallet
        QRWallet.objects.create(
            qr_code=instance,
            category=default_category
        )
```

### Step 5: Create Default Categories

Run this in Django shell:

```python
python manage.py shell
```

```python
from apps.accounts.recharge_models import RechargeCategory

# Free Category
RechargeCategory.objects.create(
    name="Free Forever",
    category_type="free",
    description="Unlimited free messages and calls",
    free_messages_limit=0,  # 0 means unlimited
    free_calls_limit=0,
    is_default=True,
    is_active=True,
    color="#10B981",
    icon="🆓"
)

# Trial Category
RechargeCategory.objects.create(
    name="Trial",
    category_type="trial",
    description="Limited free usage, then pay-as-you-go",
    free_messages_limit=10,
    free_calls_limit=5,
    message_cost=2.00,
    call_cost_per_minute=1.50,
    is_active=True,
    color="#F59E0B",
    icon="🎁"
)

# Prepaid Category
RechargeCategory.objects.create(
    name="Prepaid",
    category_type="prepaid",
    description="Recharge and use",
    message_cost=1.50,
    call_cost_per_minute=1.00,
    is_active=True,
    color="#3B82F6",
    icon="💳"
)

# Postpaid Category
RechargeCategory.objects.create(
    name="Postpaid",
    category_type="postpaid",
    description="Use now, pay later",
    message_cost=2.00,
    call_cost_per_minute=1.50,
    is_active=True,
    color="#8B5CF6",
    icon="📱"
)
```

### Step 6: Create Sample Plans

```python
from apps.accounts.recharge_models import RechargePlan

# Starter Plan
RechargePlan.objects.create(
    name="Starter",
    description="Perfect for occasional use",
    amount=99.00,
    message_credits=50,
    call_minutes=30,
    validity_days=30,
    bonus_message_credits=10,
    bonus_call_minutes=5,
    display_order=1,
    is_active=True,
    color="#3B82F6"
)

# Popular Plan
RechargePlan.objects.create(
    name="Popular",
    description="Most popular choice",
    amount=299.00,
    message_credits=200,
    call_minutes=120,
    validity_days=30,
    bonus_message_credits=50,
    bonus_call_minutes=30,
    is_popular=True,
    display_order=2,
    is_active=True,
    color="#10B981"
)

# Premium Plan
RechargePlan.objects.create(
    name="Premium",
    description="Unlimited everything",
    amount=999.00,
    message_credits=1000,
    call_minutes=600,
    validity_days=30,
    bonus_message_credits=200,
    bonus_call_minutes=100,
    display_order=3,
    is_active=True,
    color="#8B5CF6"
)
```

### Step 7: Update Communication Services

Update message/call services to check QR wallet before sending:

```python
# In apps/communications/services.py or wherever you send messages

def send_message_via_qr(qr_code, message):
    """Send message and deduct from QR wallet"""
    from apps.accounts.recharge_models import QRWallet
    
    # Get QR wallet
    wallet = QRWallet.objects.get(qr_code=qr_code)
    
    # Check if can send
    can_send, reason = wallet.can_send_message()
    if not can_send:
        raise Exception(f"Cannot send message: {reason}")
    
    # Send message
    # ... your message sending code ...
    
    # Deduct credit
    wallet.deduct_message_credit()
    
    return True

def make_call_via_qr(qr_code, duration_minutes):
    """Make call and deduct from QR wallet"""
    from apps.accounts.recharge_models import QRWallet
    
    # Get QR wallet
    wallet = QRWallet.objects.get(qr_code=qr_code)
    
    # Check if can call
    can_call, reason = wallet.can_make_call(duration_minutes)
    if not can_call:
        raise Exception(f"Cannot make call: {reason}")
    
    # Make call
    # ... your call code ...
    
    # Deduct minutes
    wallet.deduct_call_minutes(duration_minutes)
    
    return True
```

## Features

### Admin Can:
1. ✅ Create/Edit/Delete Categories
2. ✅ Create/Edit/Delete Recharge Plans
3. ✅ View all QR wallets
4. ✅ Add credits to any QR wallet
5. ✅ Assign categories to QR codes
6. ✅ Suspend/Unsuspend wallets
7. ✅ View all users
8. ✅ See complete analytics
9. ✅ Track all transactions
10. ✅ Monitor low balance QRs

### Category Types:
1. **Free** - No recharge needed, unlimited usage
2. **Trial** - Limited free usage, then paid
3. **Prepaid** - Recharge required before use
4. **Postpaid** - Use now, bill later

### Each QR Has:
- Own wallet with balance
- Message credits
- Call minutes
- Usage tracking
- Transaction history
- Category assignment
- Suspension capability

## Access URLs

### Admin URLs:
- Super Dashboard: `/accounts/admin/dashboard/`
- Manage Categories: `/accounts/admin/categories/`
- Manage Plans: `/accounts/admin/plans/`
- Manage QR Wallets: `/accounts/admin/qr-wallets/`
- User Management: `/accounts/admin/users/`

### User URLs:
- User Dashboard: `/accounts/dashboard/`
- Wallet: `/accounts/wallet/`

## Testing

1. Login as admin
2. Go to `/accounts/admin/dashboard/`
3. Create categories
4. Create plans
5. Assign categories to QR codes
6. Add credits to QR wallets
7. Test message/call functionality

## Next Steps

1. Integrate with payment gateway for plan purchases
2. Add auto-recharge functionality
3. Add email notifications for low balance
4. Add usage reports and analytics
5. Add bulk operations for admin
6. Add API endpoints for mobile apps

## Notes

- All admin views require `@staff_member_required` decorator
- QR wallets are auto-created when QR is generated
- Default category is assigned automatically
- Admin can override any setting
- Full audit trail via transactions
- Supports both free and paid models
