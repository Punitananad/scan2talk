"""
Quick script to reset admin password
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.accounts.models import User

def reset_admin_password():
    """Reset admin password."""
    
    print("\n" + "="*60)
    print("🔧 RESET ADMIN PASSWORD")
    print("="*60)
    
    # Find admin users
    admins = User.objects.filter(is_staff=True, is_superuser=True)
    
    if not admins.exists():
        print("\n❌ No admin users found!")
        return
    
    print(f"\n📋 Admin users:\n")
    
    for i, admin in enumerate(admins, 1):
        print(f"{i}. {admin.email} ({admin.username})")
    
    # Select admin
    if admins.count() == 1:
        admin = admins.first()
        print(f"\n✅ Selected: {admin.email}")
    else:
        choice = input(f"\nSelect admin (1-{admins.count()}): ").strip()
        try:
            admin = list(admins)[int(choice) - 1]
            print(f"\n✅ Selected: {admin.email}")
        except (ValueError, IndexError):
            print("❌ Invalid choice")
            return
    
    # Get new password
    new_password = input("\nEnter new password (min 6 characters): ").strip()
    
    if len(new_password) < 6:
        print("❌ Password must be at least 6 characters")
        return
    
    # Confirm
    confirm = input(f"\nReset password for {admin.email}? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Cancelled")
        return
    
    # Reset password
    admin.set_password(new_password)
    admin.save()
    
    print(f"\n" + "="*60)
    print(f"✅ PASSWORD RESET SUCCESSFUL!")
    print(f"="*60)
    print(f"\nAdmin: {admin.email}")
    print(f"Username: {admin.username}")
    print(f"New password: {new_password}")
    print(f"\nYou can now login at: /admin/")
    print(f"="*60 + "\n")

if __name__ == '__main__':
    reset_admin_password()
