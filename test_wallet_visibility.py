"""
Test Wallet Visibility Based on Category
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.accounts.models import User
from apps.gateways.qr_models import PreGeneratedQR
from apps.accounts.recharge_models import RechargeCategory


def test_wallet_visibility():
    """Test wallet visibility logic for different category types"""
    
    print("=" * 60)
    print("WALLET VISIBILITY TEST")
    print("=" * 60)
    
    # Get all categories
    categories = RechargeCategory.objects.all()
    print(f"\n1. Available Categories ({categories.count()}):")
    for cat in categories:
        print(f"   - {cat.name} ({cat.get_category_type_display()})")
    
    # Get users with activated QR codes
    users_with_qr = User.objects.filter(
        qr_codes__status='activated'
    ).distinct()
    
    print(f"\n2. Users with Activated QR Codes: {users_with_qr.count()}")
    
    # Test each user
    print("\n3. Testing Wallet Visibility Logic:")
    print("-" * 60)
    
    for user in users_with_qr[:10]:  # Test first 10 users
        print(f"\n   User: {user.email}")
        
        # Get user's QR codes
        user_qr_codes = PreGeneratedQR.objects.filter(
            owner=user,
            status='activated'
        ).select_related('category')
        
        print(f"   QR Codes: {user_qr_codes.count()}")
        
        # Check categories
        categories_found = set()
        show_wallet = False
        
        for qr in user_qr_codes:
            if qr.category:
                categories_found.add(qr.category.name)
                if qr.category.category_type in ['prepaid', 'postpaid']:
                    show_wallet = True
        
        print(f"   Categories: {', '.join(categories_found) if categories_found else 'None'}")
        print(f"   Show Wallet: {'✅ YES' if show_wallet else '❌ NO'}")
        
        if show_wallet:
            print(f"   → User will see wallet features")
        else:
            print(f"   → User will see 'Free Service Active' message")
    
    # Category breakdown
    print("\n" + "=" * 60)
    print("4. Category Type Breakdown:")
    print("-" * 60)
    
    free_categories = RechargeCategory.objects.filter(category_type='free')
    trial_categories = RechargeCategory.objects.filter(category_type='trial')
    prepaid_categories = RechargeCategory.objects.filter(category_type='prepaid')
    postpaid_categories = RechargeCategory.objects.filter(category_type='postpaid')
    
    print(f"\n   Free Categories ({free_categories.count()}):")
    for cat in free_categories:
        qr_count = PreGeneratedQR.objects.filter(
            category=cat,
            status='activated'
        ).count()
        print(f"   - {cat.name}: {qr_count} activated QR codes")
        print(f"     Wallet Visibility: ❌ Hidden")
    
    print(f"\n   Trial Categories ({trial_categories.count()}):")
    for cat in trial_categories:
        qr_count = PreGeneratedQR.objects.filter(
            category=cat,
            status='activated'
        ).count()
        print(f"   - {cat.name}: {qr_count} activated QR codes")
        print(f"     Wallet Visibility: ❌ Hidden")
    
    print(f"\n   Prepaid Categories ({prepaid_categories.count()}):")
    for cat in prepaid_categories:
        qr_count = PreGeneratedQR.objects.filter(
            category=cat,
            status='activated'
        ).count()
        print(f"   - {cat.name}: {qr_count} activated QR codes")
        print(f"     Wallet Visibility: ✅ Shown")
    
    print(f"\n   Postpaid Categories ({postpaid_categories.count()}):")
    for cat in postpaid_categories:
        qr_count = PreGeneratedQR.objects.filter(
            category=cat,
            status='activated'
        ).count()
        print(f"   - {cat.name}: {qr_count} activated QR codes")
        print(f"     Wallet Visibility: ✅ Shown")
    
    # Summary
    print("\n" + "=" * 60)
    print("5. Summary:")
    print("-" * 60)
    
    total_users = users_with_qr.count()
    users_with_wallet = 0
    users_without_wallet = 0
    
    for user in users_with_qr:
        user_qr_codes = PreGeneratedQR.objects.filter(
            owner=user,
            status='activated'
        ).select_related('category')
        
        show_wallet = False
        for qr in user_qr_codes:
            if qr.category and qr.category.category_type in ['prepaid', 'postpaid']:
                show_wallet = True
                break
        
        if show_wallet:
            users_with_wallet += 1
        else:
            users_without_wallet += 1
    
    print(f"\n   Total Users with QR Codes: {total_users}")
    print(f"   Users who will see wallet: {users_with_wallet} ({users_with_wallet/total_users*100:.1f}%)" if total_users > 0 else "   No users")
    print(f"   Users who won't see wallet: {users_without_wallet} ({users_without_wallet/total_users*100:.1f}%)" if total_users > 0 else "   No users")
    
    print("\n" + "=" * 60)
    print("✓ WALLET VISIBILITY TEST COMPLETE")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Login as a user with free category QR codes")
    print("2. Visit: http://localhost:8000/accounts/dashboard/")
    print("3. Verify wallet card is NOT shown")
    print("4. Visit: http://localhost:8000/accounts/profile/")
    print("5. Verify 'Free Service Active' message is shown")
    print("6. Verify no wallet button in quick actions")
    print("=" * 60)


if __name__ == '__main__':
    test_wallet_visibility()
