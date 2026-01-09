"""
Setup script for Advanced QR Wallet System
Run this after migrations: python manage.py shell < setup_advanced_system.py
"""

from apps.accounts.recharge_models import RechargeCategory, RechargePlan

print("=" * 60)
print("Setting up Advanced QR Wallet System")
print("=" * 60)

# Create Categories
print("\n1. Creating Categories...")

categories_data = [
    {
        "name": "Free Forever",
        "category_type": "free",
        "description": "Unlimited free messages and calls - perfect for personal use",
        "free_messages_limit": 0,  # 0 means unlimited
        "free_calls_limit": 0,
        "is_default": True,
        "is_active": True,
        "color": "#10B981",
        "icon": "🆓"
    },
    {
        "name": "Trial",
        "category_type": "trial",
        "description": "Try before you buy - limited free usage then pay-as-you-go",
        "free_messages_limit": 10,
        "free_calls_limit": 5,
        "message_cost": 2.00,
        "call_cost_per_minute": 1.50,
        "is_active": True,
        "color": "#F59E0B",
        "icon": "🎁"
    },
    {
        "name": "Prepaid Standard",
        "category_type": "prepaid",
        "description": "Recharge and use - best for regular users",
        "message_cost": 1.50,
        "call_cost_per_minute": 1.00,
        "is_active": True,
        "color": "#3B82F6",
        "icon": "💳"
    },
    {
        "name": "Postpaid Business",
        "category_type": "postpaid",
        "description": "Use now, pay later - ideal for businesses",
        "message_cost": 2.00,
        "call_cost_per_minute": 1.50,
        "is_active": True,
        "color": "#8B5CF6",
        "icon": "📱"
    }
]

for cat_data in categories_data:
    category, created = RechargeCategory.objects.get_or_create(
        name=cat_data["name"],
        defaults=cat_data
    )
    if created:
        print(f"   ✓ Created: {category.name}")
    else:
        print(f"   - Already exists: {category.name}")

# Create Plans
print("\n2. Creating Recharge Plans...")

plans_data = [
    {
        "name": "Starter Pack",
        "description": "Perfect for occasional use - try it out!",
        "amount": 99.00,
        "message_credits": 50,
        "call_minutes": 30,
        "validity_days": 30,
        "bonus_message_credits": 10,
        "bonus_call_minutes": 5,
        "display_order": 1,
        "is_active": True,
        "color": "#3B82F6"
    },
    {
        "name": "Popular Choice",
        "description": "Most popular - best value for money!",
        "amount": 299.00,
        "message_credits": 200,
        "call_minutes": 120,
        "validity_days": 30,
        "bonus_message_credits": 50,
        "bonus_call_minutes": 30,
        "is_popular": True,
        "display_order": 2,
        "is_active": True,
        "color": "#10B981"
    },
    {
        "name": "Premium Unlimited",
        "description": "For power users - unlimited everything!",
        "amount": 999.00,
        "message_credits": 1000,
        "call_minutes": 600,
        "validity_days": 30,
        "bonus_message_credits": 200,
        "bonus_call_minutes": 100,
        "display_order": 3,
        "is_active": True,
        "color": "#8B5CF6"
    },
    {
        "name": "Business Pro",
        "description": "Enterprise solution with priority support",
        "amount": 2499.00,
        "message_credits": 5000,
        "call_minutes": 3000,
        "validity_days": 90,
        "bonus_message_credits": 1000,
        "bonus_call_minutes": 500,
        "display_order": 4,
        "is_active": True,
        "color": "#EF4444"
    }
]

for plan_data in plans_data:
    plan, created = RechargePlan.objects.get_or_create(
        name=plan_data["name"],
        defaults=plan_data
    )
    if created:
        print(f"   ✓ Created: {plan.name} - ₹{plan.amount}")
    else:
        print(f"   - Already exists: {plan.name}")

print("\n" + "=" * 60)
print("Setup Complete!")
print("=" * 60)
print("\nNext Steps:")
print("1. Access admin dashboard: /accounts/admin/dashboard/")
print("2. Manage categories: /accounts/admin/categories/")
print("3. Manage plans: /accounts/admin/plans/")
print("4. Manage QR wallets: /accounts/admin/qr-wallets/")
print("\nNote: You need to be logged in as admin (staff user)")
print("=" * 60)
