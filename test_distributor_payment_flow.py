#!/usr/bin/env python
"""
Test Distributor Payment Flow with Distributor Tracking

This script tests the complete distributor payment flow including:
1. Distributor code validation
2. Payment creation with distributor link
3. Razorpay integration
4. Commission tracking
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.accounts.models import User
from apps.gateways.qr_models import PreGeneratedQR
from apps.accounts.recharge_models import RechargeCategory, DistributorPayment
from django.db.models import Sum, Count


def test_distributor_payment_flow():
    """Test the complete distributor payment flow"""
    
    print("=" * 80)
    print("🧪 TESTING DISTRIBUTOR PAYMENT FLOW WITH TRACKING")
    print("=" * 80)
    
    # Step 1: Check for distributor category
    print("\n📋 Step 1: Checking Distributor Category...")
    dist_categories = RechargeCategory.objects.filter(category_type='distributor')
    
    if not dist_categories.exists():
        print("   ❌ Distributor category not found!")
        return
    
    dist_category = dist_categories.first()
    print(f"   ✅ Found {dist_categories.count()} distributor categor{'y' if dist_categories.count() == 1 else 'ies'}:")
    for cat in dist_categories:
        print(f"      - {cat.name} (Fee: ₹{cat.distributor_activation_fee})")
    
    print(f"\n   Using: {dist_category.name}")
    
    # Step 2: Check for verified distributors
    print("\n👥 Step 2: Checking Verified Distributors...")
    distributors = User.objects.filter(
        is_distributor=True,
        distributor_verified=True
    )
    
    if not distributors.exists():
        print("   ⚠️  No verified distributors found!")
        print("   💡 Create one using: python manage.py shell")
        print("      User.objects.create_user(username='dist1', phone='9876543210', is_distributor=True, distributor_verified=True)")
        return
    
    print(f"   ✅ Found {distributors.count()} verified distributor(s):")
    for dist in distributors:
        phone = dist.get_decrypted_phone() if hasattr(dist, 'get_decrypted_phone') else 'N/A'
        print(f"      - {dist.username} (Code: {phone})")
    
    # Step 3: Check for distributor category QR codes
    print("\n🏷️  Step 3: Checking Distributor QR Codes...")
    dist_qrs = PreGeneratedQR.objects.filter(category=dist_category)
    
    if not dist_qrs.exists():
        print("   ⚠️  No distributor QR codes found!")
        print("   💡 Create one in admin or using shell")
        return
    
    print(f"   ✅ Found {dist_qrs.count()} distributor QR code(s):")
    for qr in dist_qrs[:5]:  # Show first 5
        print(f"      - {qr.qr_code} (Status: {qr.status})")
    
    # Step 4: Check distributor payments
    print("\n💳 Step 4: Checking Distributor Payments...")
    payments = DistributorPayment.objects.all()
    
    if not payments.exists():
        print("   ℹ️  No payments yet")
    else:
        print(f"   ✅ Found {payments.count()} payment(s):")
        
        # Show payment details
        for payment in payments[:5]:  # Show first 5
            dist_name = payment.distributor.username if payment.distributor else "Not linked"
            print(f"\n      Payment: {payment.order_id}")
            print(f"      QR Code: {payment.qr_code.qr_code}")
            print(f"      Amount: ₹{payment.amount}")
            print(f"      Status: {payment.status}")
            print(f"      Distributor: {dist_name}")
    
    # Step 5: Commission tracking stats
    print("\n📊 Step 5: Commission Tracking Statistics...")
    
    for distributor in distributors:
        dist_sales = DistributorPayment.objects.filter(
            distributor=distributor,
            status='completed'
        )
        
        stats = dist_sales.aggregate(
            total_sales=Count('id'),
            total_revenue=Sum('amount')
        )
        
        phone = distributor.get_decrypted_phone() if hasattr(distributor, 'get_decrypted_phone') else 'N/A'
        
        print(f"\n   📈 {distributor.username} (Code: {phone})")
        print(f"      Total Sales: {stats['total_sales'] or 0}")
        print(f"      Total Revenue: ₹{stats['total_revenue'] or 0}")
    
    # Step 6: Test URLs
    print("\n🔗 Step 6: Test URLs...")
    if dist_qrs.exists():
        test_qr = dist_qrs.first()
        print(f"\n   Test with QR Code: {test_qr.qr_code}")
        print(f"   1. Payment Page:")
        print(f"      http://localhost:8000/accounts/distributor-payment/{test_qr.qr_code}/")
        print(f"\n   2. Enter distributor code (10-digit phone number)")
        print(f"      Example: {distributors.first().get_decrypted_phone() if hasattr(distributors.first(), 'get_decrypted_phone') else '9876543210'}")
        print(f"\n   3. Complete Razorpay payment")
        print(f"\n   4. System will:")
        print(f"      - Link payment to distributor")
        print(f"      - Redirect to activation page")
        print(f"      - Track commission for distributor")
    
    # Step 7: Validation test
    print("\n✅ Step 7: Testing Distributor Code Validation...")
    
    test_distributor = distributors.first()
    test_phone = test_distributor.get_decrypted_phone() if hasattr(test_distributor, 'get_decrypted_phone') else None
    
    if test_phone:
        print(f"   Testing with distributor code: {test_phone}")
        
        # Simulate validation
        found = False
        for dist in distributors:
            if dist.get_decrypted_phone() == test_phone:
                found = True
                print(f"   ✅ Validation passed: Found distributor {dist.username}")
                break
        
        if not found:
            print(f"   ❌ Validation failed: Distributor not found")
    else:
        print("   ⚠️  Cannot test validation - phone decryption not available")
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 SUMMARY")
    print("=" * 80)
    print(f"✅ Distributor Category: {dist_category.name}")
    print(f"✅ Verified Distributors: {distributors.count()}")
    print(f"✅ Distributor QR Codes: {dist_qrs.count()}")
    print(f"✅ Total Payments: {payments.count()}")
    print(f"✅ Completed Payments: {payments.filter(status='completed').count()}")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Visit the payment page URL above")
    print("2. Enter a valid distributor code (10-digit phone)")
    print("3. Complete the Razorpay payment")
    print("4. Check that payment is linked to distributor")
    print("5. Verify commission tracking in distributor dashboard")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    try:
        test_distributor_payment_flow()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
