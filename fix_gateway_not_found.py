#!/usr/bin/env python
"""
Fix script for "Gateway Not Found" issue.

This script:
1. Finds all activated QR codes with inactive or missing gateways
2. Reactivates gateways that were incorrectly deactivated
3. Reports any data integrity issues
4. Ensures all activated QRs have valid, active gateways

Run with: python fix_gateway_not_found.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.gateways.qr_models import PreGeneratedQR
from apps.gateways.models import Gateway
from django.db import transaction


def diagnose_issues():
    """Diagnose all gateway-related issues."""
    print("=" * 80)
    print("DIAGNOSING GATEWAY ISSUES")
    print("=" * 80)
    
    # Find activated QRs
    activated_qrs = PreGeneratedQR.objects.filter(status='activated')
    print(f"\n✓ Total activated QR codes: {activated_qrs.count()}")
    
    # Find QRs with no gateway
    qrs_no_gateway = activated_qrs.filter(gateway__isnull=True)
    print(f"✗ Activated QRs with NO gateway: {qrs_no_gateway.count()}")
    if qrs_no_gateway.exists():
        for qr in qrs_no_gateway:
            print(f"  - {qr.qr_code} (Owner: {qr.owner})")
    
    # Find QRs with inactive gateway
    qrs_inactive_gateway = activated_qrs.filter(gateway__is_active=False)
    print(f"✗ Activated QRs with INACTIVE gateway: {qrs_inactive_gateway.count()}")
    if qrs_inactive_gateway.exists():
        for qr in qrs_inactive_gateway:
            print(f"  - {qr.qr_code} -> Gateway {qr.gateway.id} ({qr.gateway.identifier_text})")
    
    # Find QRs with active gateway (good)
    qrs_active_gateway = activated_qrs.filter(gateway__is_active=True)
    print(f"✓ Activated QRs with ACTIVE gateway: {qrs_active_gateway.count()}")
    
    return {
        'total_activated': activated_qrs.count(),
        'no_gateway': qrs_no_gateway,
        'inactive_gateway': qrs_inactive_gateway,
        'active_gateway': qrs_active_gateway
    }


def fix_inactive_gateways(qrs_with_inactive_gateway):
    """Reactivate gateways that were incorrectly deactivated."""
    print("\n" + "=" * 80)
    print("FIXING INACTIVE GATEWAYS")
    print("=" * 80)
    
    if not qrs_with_inactive_gateway.exists():
        print("\n✓ No inactive gateways to fix!")
        return 0
    
    fixed_count = 0
    with transaction.atomic():
        for qr in qrs_with_inactive_gateway:
            try:
                gateway = qr.gateway
                print(f"\n→ Reactivating gateway for QR {qr.qr_code}")
                print(f"  Gateway ID: {gateway.id}")
                print(f"  Vehicle: {gateway.identifier_text}")
                print(f"  Owner: {gateway.owner_name or gateway.owner}")
                
                gateway.is_active = True
                gateway.save(update_fields=['is_active'])
                
                print(f"  ✓ Gateway reactivated successfully!")
                fixed_count += 1
            except Exception as e:
                print(f"  ✗ Error reactivating gateway: {e}")
    
    print(f"\n✓ Fixed {fixed_count} inactive gateways")
    return fixed_count


def fix_missing_gateways(qrs_with_no_gateway):
    """Report QRs with missing gateways (requires manual intervention)."""
    print("\n" + "=" * 80)
    print("CHECKING MISSING GATEWAYS")
    print("=" * 80)
    
    if not qrs_with_no_gateway.exists():
        print("\n✓ No missing gateways!")
        return
    
    print(f"\n✗ Found {qrs_with_no_gateway.count()} QRs with missing gateways")
    print("  These require manual intervention:")
    
    for qr in qrs_with_no_gateway:
        print(f"\n  QR Code: {qr.qr_code}")
        print(f"  Owner: {qr.owner}")
        print(f"  Activated: {qr.activated_at}")
        print(f"  Status: {qr.status}")
        print(f"  → This QR should be reset to 'available' or have a gateway created")


def verify_fix():
    """Verify that all issues are resolved."""
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    activated_qrs = PreGeneratedQR.objects.filter(status='activated')
    qrs_with_issues = activated_qrs.filter(
        gateway__isnull=True
    ) | activated_qrs.filter(
        gateway__is_active=False
    )
    
    if qrs_with_issues.count() == 0:
        print("\n✓✓✓ ALL ACTIVATED QRs HAVE ACTIVE GATEWAYS! ✓✓✓")
        print("✓ The 'Gateway Not Found' issue should be resolved!")
        return True
    else:
        print(f"\n✗ Still {qrs_with_issues.count()} QRs with issues")
        return False


def main():
    """Main execution."""
    print("\n" + "=" * 80)
    print("GATEWAY NOT FOUND - FIX SCRIPT")
    print("=" * 80)
    print("\nThis script will:")
    print("1. Diagnose all gateway-related issues")
    print("2. Automatically reactivate inactive gateways")
    print("3. Report any data integrity issues")
    print("4. Verify the fix")
    
    input("\nPress ENTER to continue...")
    
    # Step 1: Diagnose
    issues = diagnose_issues()
    
    # Step 2: Fix inactive gateways
    if issues['inactive_gateway'].exists():
        print("\n" + "-" * 80)
        response = input("\nFix inactive gateways? (yes/no): ").strip().lower()
        if response == 'yes':
            fix_inactive_gateways(issues['inactive_gateway'])
        else:
            print("Skipped fixing inactive gateways")
    
    # Step 3: Report missing gateways
    if issues['no_gateway'].exists():
        fix_missing_gateways(issues['no_gateway'])
    
    # Step 4: Verify
    verify_fix()
    
    print("\n" + "=" * 80)
    print("SCRIPT COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Test by scanning a QR code")
    print("2. Verify it shows the contact page (not 'Gateway Not Found')")
    print("3. If issues persist, check the logs for specific error messages")
    print("\n")


if __name__ == '__main__':
    main()
