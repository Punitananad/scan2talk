"""
Test creating an order with distributor code
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.core.models import TagOrder
from apps.accounts.models import User

print("\n" + "="*60)
print("🧪 TESTING DISTRIBUTOR ORDER CREATION")
print("="*60 + "\n")

# Find distributor
dist = User.objects.filter(is_distributor=True, distributor_verified=True).first()

if not dist:
    print("❌ No verified distributor found!")
    print("   Please verify a distributor first")
    exit()

dist_phone = dist.get_decrypted_phone()
print(f"✅ Found Distributor: {dist.first_name}")
print(f"📱 Phone: {dist_phone}\n")

# Create test order with distributor code
print("Creating test order with distributor code...")

order = TagOrder.objects.create(
    order_id=f"TEST{django.utils.timezone.now().timestamp()}",
    name="Test Customer",
    phone="9999999999",
    email="test@example.com",
    address="Test Address",
    city="Test City",
    state="Test State",
    pincode="123456",
    quantity=1,
    total_amount=299.00,
    distributor_code=dist_phone,  # Set distributor code
    status='processing',  # Mark as processing (successful payment)
    notes="Test order for distributor commission"
)

print(f"✅ Order Created: {order.order_id}")
print(f"   Distributor Code: '{order.distributor_code}'")
print(f"   Status: {order.status}")
print(f"   Amount: ₹{order.total_amount}\n")

# Check if it shows in distributor dashboard
successful_payments = TagOrder.objects.filter(
    distributor_code=dist_phone,
    status__in=['processing', 'shipped', 'delivered']
)

print(f"📊 Distributor Dashboard Stats:")
print(f"   Successful Payments: {successful_payments.count()}")
print(f"   Commission per payment: ₹{dist.distributor_commission_per_activation}")
print(f"   Total Revenue: ₹{successful_payments.count() * dist.distributor_commission_per_activation}")

print("\n" + "="*60)
print("✅ TEST COMPLETE")
print("="*60 + "\n")

print("Now refresh the distributor dashboard to see the commission!")
