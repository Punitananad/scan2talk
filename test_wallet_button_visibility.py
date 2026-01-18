"""
Test script to verify wallet button visibility logic.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.gateways.qr_models import PreGeneratedQR

User = get_user_model()

def test_wallet_visibility():
    """Test wallet visibility for different users."""
    print("\n" + "="*60)
    print("WALLET BUTTON VISIBILITY TEST")
    print("="*60)
    
    users = User.objects.all()
    
    for user in users:
        print(f"\n👤 User: {user.email}")
        
        # Get user's QR codes
        qr_codes = PreGeneratedQR.objects.filter(
            owner=user,
            status='activated'
        ).select_related('category')
        
        if not qr_codes.exists():
            print("   ❌ No activated QR codes")
            print("   🔒 Wallet Button: HIDDEN")
            continue
        
        # Check categories
        categories = []
        show_wallet = False
        
        for qr in qr_codes:
            if qr.category:
                categories.append({
                    'name': qr.category.name,
                    'type': qr.category.category_type
                })
                if qr.category.category_type in ['prepaid', 'postpaid']:
                    show_wallet = True
        
        print(f"   📋 QR Codes: {qr_codes.count()}")
        print(f"   📁 Categories:")
        for cat in categories:
            print(f"      - {cat['name']} ({cat['type']})")
        
        if show_wallet:
            print("   ✅ Wallet Button: VISIBLE")
            print("   💰 User can see wallet features")
        else:
            print("   ❌ Wallet Button: HIDDEN")
            print("   🆓 User has free/trial categories only")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_wallet_visibility()
