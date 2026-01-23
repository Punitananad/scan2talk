"""
Test distributor login - Check if password was set correctly
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.accounts.models import User
from django.contrib.auth import authenticate

def test_distributor_login():
    """Test distributor login with phone and password."""
    
    print("\n" + "="*60)
    print("🔍 DISTRIBUTOR LOGIN TEST")
    print("="*60)
    
    # Get all distributors
    distributors = User.objects.filter(is_distributor=True)
    
    if not distributors.exists():
        print("\n❌ No distributors found in database")
        return
    
    print(f"\n📋 Found {distributors.count()} distributor(s):\n")
    
    for i, dist in enumerate(distributors, 1):
        phone = dist.get_decrypted_phone()
        verified = "✓ Verified" if dist.distributor_verified else "⏳ Pending"
        
        print(f"{i}. {dist.email}")
        print(f"   Phone: {phone}")
        print(f"   Status: {verified}")
        print(f"   Username: {dist.username}")
        print(f"   Has usable password: {dist.has_usable_password()}")
        print()
    
    # Test login
    print("="*60)
    print("🔐 TEST LOGIN")
    print("="*60)
    
    phone_input = input("\nEnter phone number (10 digits): ").strip()
    password_input = input("Enter password: ").strip()
    
    # Find user by phone
    phone_digits = ''.join(filter(str.isdigit, phone_input))
    
    user_found = None
    for u in distributors:
        if u.get_decrypted_phone() == phone_digits:
            user_found = u
            break
    
    if not user_found:
        print(f"\n❌ No distributor found with phone: {phone_digits}")
        return
    
    print(f"\n✅ Found distributor: {user_found.email}")
    print(f"   Username: {user_found.username}")
    print(f"   Verified: {user_found.distributor_verified}")
    
    if not user_found.distributor_verified:
        print(f"\n⚠️  Distributor is not verified yet!")
        print(f"   Admin needs to verify and assign password first")
        return
    
    # Test authentication
    print(f"\n🔐 Testing authentication...")
    authenticated_user = authenticate(
        username=user_found.username,
        password=password_input
    )
    
    if authenticated_user:
        print(f"\n✅ SUCCESS! Authentication passed")
        print(f"   User: {authenticated_user.email}")
        print(f"   Can login: YES")
        print(f"\n🎉 You can login at: /accounts/distributor/login/")
        print(f"   Phone: {phone_digits}")
        print(f"   Password: {password_input}")
    else:
        print(f"\n❌ FAILED! Authentication failed")
        print(f"   The password is incorrect")
        print(f"\n💡 Possible reasons:")
        print(f"   1. Password was not set correctly")
        print(f"   2. Wrong password entered")
        print(f"   3. User account has issues")
        
        # Check if password is set
        if not user_found.has_usable_password():
            print(f"\n⚠️  User has NO usable password!")
            print(f"   Admin needs to assign a password")
        else:
            print(f"\n✓ User has a password set")
            print(f"   But the password you entered is wrong")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    test_distributor_login()
