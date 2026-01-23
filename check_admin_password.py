"""
Check admin password and diagnose issues
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.accounts.models import User
from django.contrib.auth import authenticate

def check_admin_password():
    """Check admin account and test password."""
    
    print("\n" + "="*60)
    print("🔍 ADMIN PASSWORD DIAGNOSTIC")
    print("="*60)
    
    # Find admin users
    admins = User.objects.filter(is_staff=True, is_superuser=True)
    
    if not admins.exists():
        print("\n❌ No admin users found!")
        return
    
    print(f"\n📋 Found {admins.count()} admin user(s):\n")
    
    for i, admin in enumerate(admins, 1):
        print(f"{i}. {admin.email}")
        print(f"   Username: {admin.username}")
        print(f"   Is staff: {admin.is_staff}")
        print(f"   Is superuser: {admin.is_superuser}")
        print(f"   Is active: {admin.is_active}")
        print(f"   Is distributor: {admin.is_distributor}")
        print(f"   Has usable password: {admin.has_usable_password()}")
        print()
    
    # Test password
    print("="*60)
    print("🔐 TEST ADMIN PASSWORD")
    print("="*60)
    
    email_input = input("\nEnter admin email: ").strip()
    password_input = input("Enter password: ").strip()
    
    # Find admin by email
    try:
        admin = User.objects.get(email=email_input, is_staff=True)
    except User.DoesNotExist:
        print(f"\n❌ No admin found with email: {email_input}")
        return
    
    print(f"\n✅ Found admin: {admin.email}")
    print(f"   Username: {admin.username}")
    
    # Test authentication
    print(f"\n🔐 Testing authentication...")
    authenticated_user = authenticate(
        username=admin.username,
        password=password_input
    )
    
    if authenticated_user:
        print(f"\n✅ SUCCESS! Password is correct")
        print(f"   You can login with:")
        print(f"   Email: {email_input}")
        print(f"   Password: {password_input}")
    else:
        print(f"\n❌ FAILED! Password is incorrect")
        print(f"\n💡 Possible reasons:")
        print(f"   1. Wrong password")
        print(f"   2. Password was changed accidentally")
        print(f"   3. Account has issues")
        
        # Offer to reset password
        print(f"\n🔧 Would you like to reset the password?")
        reset = input("Enter 'yes' to reset password: ").strip().lower()
        
        if reset == 'yes':
            new_password = input("Enter new password: ").strip()
            if len(new_password) < 6:
                print("❌ Password must be at least 6 characters")
                return
            
            admin.set_password(new_password)
            admin.save()
            
            print(f"\n✅ Password reset successfully!")
            print(f"   Email: {email_input}")
            print(f"   New password: {new_password}")
            print(f"\n   You can now login at /admin/")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    check_admin_password()
