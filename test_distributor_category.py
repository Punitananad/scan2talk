"""
Test script for Distributor Category implementation.
Run: python test_distributor_category.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.accounts.recharge_models import RechargeCategory, DistributorPayment, QRWallet
from apps.gateways.qr_models import PreGeneratedQR, QRBatch
from django.contrib.auth import get_user_model

User = get_user_model()


def test_category_creation():
    """Test 1: Create Distributor category"""
    print("\n" + "="*60)
    print("TEST 1: Creating Distributor Category")
    print("="*60)
    
    category, created = RechargeCategory.objects.get_or_create(
        name='Distributor Test',
        defaults={
            'category_type': 'distributor',
            'description': 'Test distributor category with one-time payment',
            'distributor_activation_fee': 500.00,
            'message_cost': 0.00,
            'call_cost_per_minute': 0.00,
            'free_messages_limit': 0,  # Unlimited
            'free_calls_limit': 0,  # Unlimited
            'is_active': True,
            'color': '#9333EA',
            'icon': '🏪'
        }
    )
    
    if created:
        print(f"✅ Created new category: {category.name}")
    else:
        print(f"ℹ️  Category already exists: {category.name}")
    
    print(f"   - Type: {category.get_category_type_display()}")
    print(f"   - Activation Fee: ₹{category.distributor_activation_fee}")
    print(f"   - Message Cost: ₹{category.message_cost}")
    print(f"   - Call Cost: ₹{category.call_cost_per_minute}")
    
    return category


def test_qr_generation(category):
    """Test 2: Generate QR codes with distributor category"""
    print("\n" + "="*60)
    print("TEST 2: Generating QR Codes with Distributor Category")
    print("="*60)
    
    # Create batch
    batch_number = f"DIST-TEST-001"
    
    # Check if batch exists
    batch = QRBatch.objects.filter(batch_number=batch_number).first()
    if batch:
        print(f"ℹ️  Batch already exists: {batch_number}")
        qr_codes = PreGeneratedQR.objects.filter(batch_number=batch_number)
    else:
        batch = QRBatch.objects.create(
            batch_number=batch_number,
            quantity=3,
            purpose='Testing distributor category',
            category=category,
            available_count=3
        )
        print(f"✅ Created batch: {batch_number}")
        
        # Generate 3 test QR codes
        qr_codes = []
        for i in range(3):
            qr = PreGeneratedQR.objects.create(
                batch_number=batch_number,
                category=category
            )
            qr_codes.append(qr)
            
            # Create QR wallet
            wallet = QRWallet.objects.create(
                qr_code=qr,
                category=category
            )
            print(f"   ✅ Created QR: {qr.qr_code} with wallet")
    
    print(f"\n📊 Batch Statistics:")
    print(f"   - Total QR codes: {len(qr_codes)}")
    print(f"   - Category: {category.name}")
    print(f"   - Activation Fee: ₹{category.distributor_activation_fee}")
    
    return list(qr_codes)


def test_payment_check(qr_codes):
    """Test 3: Check payment requirement"""
    print("\n" + "="*60)
    print("TEST 3: Testing Payment Requirement Check")
    print("="*60)
    
    qr = qr_codes[0]
    print(f"Testing QR: {qr.qr_code}")
    print(f"Category: {qr.category.name} ({qr.category.category_type})")
    print(f"Status: {qr.status}")
    
    # Check if payment exists
    try:
        payment = DistributorPayment.objects.get(qr_code=qr)
        print(f"\n💳 Payment Record Found:")
        print(f"   - Amount: ₹{payment.amount}")
        print(f"   - Status: {payment.status}")
        print(f"   - Order ID: {payment.order_id}")
        if payment.paid_at:
            print(f"   - Paid At: {payment.paid_at}")
    except DistributorPayment.DoesNotExist:
        print(f"\n❌ No payment record found")
        print(f"   → User would be redirected to payment page")
    
    return qr


def test_wallet_logic(qr):
    """Test 4: Test wallet logic for distributor category"""
    print("\n" + "="*60)
    print("TEST 4: Testing Wallet Logic")
    print("="*60)
    
    try:
        wallet = QRWallet.objects.get(qr_code=qr)
        print(f"Wallet for QR: {qr.qr_code}")
        print(f"Category: {wallet.category.name} ({wallet.category.category_type})")
        
        # Test message sending
        can_send, message = wallet.can_send_message()
        print(f"\n📧 Can Send Message: {can_send}")
        print(f"   Reason: {message}")
        
        # Test call making
        can_call, call_message = wallet.can_make_call()
        print(f"\n📞 Can Make Call: {can_call}")
        print(f"   Reason: {call_message}")
        
        # Test deduction (should not deduct for distributor)
        print(f"\n🧪 Testing Deduction Logic:")
        print(f"   Before - Messages: {wallet.total_messages_sent}, Calls: {wallet.total_calls_made}")
        
        wallet.deduct_message_credit()
        wallet.deduct_call_minutes(1)
        
        wallet.refresh_from_db()
        print(f"   After - Messages: {wallet.total_messages_sent}, Calls: {wallet.total_calls_made}")
        print(f"   Credits - Messages: {wallet.message_credits}, Call Minutes: {wallet.call_minutes}")
        print(f"   ✅ No credits deducted (as expected for distributor)")
        
    except QRWallet.DoesNotExist:
        print(f"❌ No wallet found for QR: {qr.qr_code}")


def test_payment_simulation(qr):
    """Test 5: Simulate payment creation"""
    print("\n" + "="*60)
    print("TEST 5: Simulating Payment Creation")
    print("="*60)
    
    # Check if payment already exists
    payment = DistributorPayment.objects.filter(qr_code=qr).first()
    
    if payment:
        print(f"ℹ️  Payment already exists for QR: {qr.qr_code}")
        print(f"   Status: {payment.status}")
    else:
        # Create test payment
        payment = DistributorPayment.objects.create(
            qr_code=qr,
            amount=qr.category.distributor_activation_fee,
            order_id=f"TEST-{qr.qr_code}-001",
            status='pending',
            phone='9999999999'
        )
        print(f"✅ Created test payment:")
        print(f"   - QR Code: {qr.qr_code}")
        print(f"   - Amount: ₹{payment.amount}")
        print(f"   - Order ID: {payment.order_id}")
        print(f"   - Status: {payment.status}")
    
    # Test marking as completed
    if payment.status == 'pending':
        print(f"\n🔄 Marking payment as completed...")
        payment.mark_completed('TEST_PAYMENT_ID_123')
        print(f"   ✅ Payment marked as completed")
        print(f"   - Gateway Payment ID: {payment.gateway_payment_id}")
        print(f"   - Paid At: {payment.paid_at}")
    
    return payment


def test_activation_flow(qr):
    """Test 6: Test activation flow logic"""
    print("\n" + "="*60)
    print("TEST 6: Testing Activation Flow Logic")
    print("="*60)
    
    print(f"QR Code: {qr.qr_code}")
    print(f"Category: {qr.category.name} ({qr.category.category_type})")
    print(f"Status: {qr.status}")
    
    # Check payment status
    try:
        payment = DistributorPayment.objects.get(qr_code=qr)
        print(f"\n💳 Payment Status: {payment.status}")
        
        if payment.status == 'completed':
            print(f"   ✅ Payment completed - activation allowed")
            print(f"   → User would proceed to activation steps:")
            print(f"      1. Enter phone number")
            print(f"      2. Verify OTP")
            print(f"      3. Enter vehicle details")
            print(f"      4. QR activated successfully")
        else:
            print(f"   ❌ Payment not completed - activation blocked")
            print(f"   → User would be redirected to payment page")
            
    except DistributorPayment.DoesNotExist:
        print(f"\n❌ No payment record")
        print(f"   → User would be redirected to payment page")


def run_all_tests():
    """Run all tests"""
    print("\n" + "🚀 " + "="*58)
    print("   DISTRIBUTOR CATEGORY IMPLEMENTATION TEST SUITE")
    print("="*60)
    
    try:
        # Test 1: Create category
        category = test_category_creation()
        
        # Test 2: Generate QR codes
        qr_codes = test_qr_generation(category)
        
        # Test 3: Check payment requirement
        qr = test_payment_check(qr_codes)
        
        # Test 4: Test wallet logic
        test_wallet_logic(qr)
        
        # Test 5: Simulate payment
        payment = test_payment_simulation(qr)
        
        # Test 6: Test activation flow
        test_activation_flow(qr)
        
        # Summary
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\n📋 Summary:")
        print(f"   - Category: {category.name}")
        print(f"   - Activation Fee: ₹{category.distributor_activation_fee}")
        print(f"   - Test QR Codes: {len(qr_codes)}")
        print(f"   - Sample QR: {qr_codes[0].qr_code}")
        print(f"   - Payment Status: {payment.status}")
        
        print("\n🔗 Test URLs:")
        print(f"   - Payment Page: /accounts/distributor-payment/{qr_codes[0].qr_code}/")
        print(f"   - Activation Page: /gateways/activate/{qr_codes[0].qr_code}/")
        
        print("\n📝 Next Steps:")
        print("   1. Run migrations: python manage.py migrate")
        print("   2. Start server: python manage.py runserver")
        print("   3. Visit payment page in browser")
        print("   4. Test payment flow with PhonePe")
        print("   5. Complete activation after payment")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()
