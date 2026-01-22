"""
Quick setup script for Distributor Category.
Run: python setup_distributor_category.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.accounts.recharge_models import RechargeCategory


def setup_distributor_category():
    """Create or update distributor category."""
    print("\n" + "="*60)
    print("🏪 DISTRIBUTOR CATEGORY SETUP")
    print("="*60)
    
    # Check if distributor category exists
    existing = RechargeCategory.objects.filter(category_type='distributor').first()
    
    if existing:
        print(f"\n✅ Distributor category already exists: {existing.name}")
        print(f"   - Activation Fee: ₹{existing.distributor_activation_fee}")
        print(f"   - Status: {'Active' if existing.is_active else 'Inactive'}")
        
        update = input("\n❓ Update activation fee? (y/n): ").lower()
        if update == 'y':
            try:
                new_fee = float(input("   Enter new activation fee (₹): "))
                existing.distributor_activation_fee = new_fee
                existing.save()
                print(f"   ✅ Updated activation fee to ₹{new_fee}")
            except ValueError:
                print("   ❌ Invalid amount")
        
        return existing
    
    # Create new distributor category
    print("\n📝 Creating new Distributor category...")
    print("\nDefault settings:")
    print("   - Name: Distributor")
    print("   - Activation Fee: ₹500")
    print("   - Usage: Unlimited (Free after payment)")
    
    use_defaults = input("\n❓ Use default settings? (y/n): ").lower()
    
    if use_defaults == 'y':
        name = "Distributor"
        fee = 500.00
    else:
        name = input("   Enter category name [Distributor]: ").strip() or "Distributor"
        try:
            fee = float(input("   Enter activation fee (₹) [500]: ") or "500")
        except ValueError:
            print("   ⚠️  Invalid fee, using default ₹500")
            fee = 500.00
    
    # Create category
    category = RechargeCategory.objects.create(
        name=name,
        category_type='distributor',
        description=f'One-time payment of ₹{fee} for lifetime activation. Unlimited free usage after payment.',
        distributor_activation_fee=fee,
        message_cost=0.00,
        call_cost_per_minute=0.00,
        free_messages_limit=0,  # 0 means unlimited
        free_calls_limit=0,  # 0 means unlimited
        is_active=True,
        is_default=False,
        color='#9333EA',  # Purple
        icon='🏪'
    )
    
    print(f"\n✅ Created Distributor category successfully!")
    print(f"\n📋 Category Details:")
    print(f"   - Name: {category.name}")
    print(f"   - Type: {category.get_category_type_display()}")
    print(f"   - Activation Fee: ₹{category.distributor_activation_fee}")
    print(f"   - Message Cost: ₹{category.message_cost} (not used)")
    print(f"   - Call Cost: ₹{category.call_cost_per_minute} (not used)")
    print(f"   - Free Messages: {'Unlimited' if category.free_messages_limit == 0 else category.free_messages_limit}")
    print(f"   - Free Calls: {'Unlimited' if category.free_calls_limit == 0 else category.free_calls_limit}")
    print(f"   - Status: {'Active ✓' if category.is_active else 'Inactive ✗'}")
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Go to admin dashboard")
    print(f"   2. Generate QR batch with '{category.name}' category")
    print(f"   3. Test activation flow:")
    print(f"      - Scan QR → Pay ₹{fee} → Activate → Use Forever")
    
    return category


def show_usage_instructions(category):
    """Show usage instructions."""
    print("\n" + "="*60)
    print("📖 USAGE INSTRUCTIONS")
    print("="*60)
    
    print("\n1️⃣  Generate QR Batch:")
    print("   - Go to: /gqr/")
    print("   - Select category: " + category.name)
    print("   - Generate batch")
    
    print("\n2️⃣  User Flow:")
    print("   - User scans QR code")
    print(f"   - Redirected to payment page")
    print(f"   - Pays ₹{category.distributor_activation_fee} (one-time)")
    print("   - Completes activation (phone + vehicle)")
    print("   - Uses QR forever (unlimited, free)")
    
    print("\n3️⃣  Admin Management:")
    print("   - View payments: Admin → Distributor Payments")
    print("   - Track QR codes: Admin → QR Wallets")
    print("   - Manage category: Admin → Categories")
    
    print("\n4️⃣  Testing:")
    print("   - Run: python test_distributor_category.py")
    print("   - Or manually test activation flow")


def main():
    """Main setup function."""
    try:
        category = setup_distributor_category()
        show_usage_instructions(category)
        
        print("\n" + "="*60)
        print("✅ SETUP COMPLETE!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
