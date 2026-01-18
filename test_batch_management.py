"""
Test Batch Management System
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.gateways.qr_models import QRBatch, PreGeneratedQR
from apps.accounts.models import User
from django.utils import timezone


def test_batch_management():
    """Test batch management system functionality"""
    
    print("=" * 60)
    print("BATCH MANAGEMENT SYSTEM TEST")
    print("=" * 60)
    
    # 1. Check if batches exist
    print("\n1. Checking existing batches...")
    batches = QRBatch.objects.all()
    print(f"   Total batches: {batches.count()}")
    
    if batches.exists():
        print("\n   Recent batches:")
        for batch in batches[:5]:
            print(f"   - {batch.batch_number}")
            print(f"     Quantity: {batch.quantity}")
            print(f"     Status: {batch.get_print_status_display()}")
            print(f"     Activated: {batch.activated_count}/{batch.quantity}")
            print(f"     Created: {batch.created_at.strftime('%Y-%m-%d %H:%M')}")
            
            # Check timestamps
            if batch.sent_for_print_at:
                print(f"     Sent for print: {batch.sent_for_print_at.strftime('%Y-%m-%d %H:%M')}")
            if batch.printing_started_at:
                print(f"     Printing started: {batch.printing_started_at.strftime('%Y-%m-%d %H:%M')}")
            if batch.printed_at:
                print(f"     Printed: {batch.printed_at.strftime('%Y-%m-%d %H:%M')}")
            if batch.delivered_at:
                print(f"     Delivered: {batch.delivered_at.strftime('%Y-%m-%d %H:%M')}")
            
            print()
    
    # 2. Check status distribution
    print("\n2. Status Distribution:")
    status_counts = {}
    for status_value, status_label in QRBatch.STATUS_CHOICES:
        count = QRBatch.objects.filter(print_status=status_value).count()
        status_counts[status_label] = count
        print(f"   {status_label}: {count}")
    
    # 3. Test status update
    print("\n3. Testing Status Update...")
    test_batch = batches.first()
    if test_batch:
        print(f"   Selected batch: {test_batch.batch_number}")
        print(f"   Current status: {test_batch.get_print_status_display()}")
        
        # Simulate status update
        old_status = test_batch.print_status
        if old_status == 'generated':
            new_status = 'sent_for_print'
            test_batch.print_status = new_status
            test_batch.sent_for_print_at = timezone.now()
            test_batch.print_notes = "Test update from batch management test"
            test_batch.save()
            print(f"   ✓ Updated to: {test_batch.get_print_status_display()}")
            
            # Revert back
            test_batch.print_status = old_status
            test_batch.sent_for_print_at = None
            test_batch.print_notes = ""
            test_batch.save()
            print(f"   ✓ Reverted to: {test_batch.get_print_status_display()}")
        else:
            print(f"   Skipping update (already {old_status})")
    
    # 4. Check QR codes in batches
    print("\n4. QR Codes in Batches:")
    total_qr_codes = PreGeneratedQR.objects.count()
    qr_in_batches = PreGeneratedQR.objects.exclude(batch_number='').count()
    print(f"   Total QR codes: {total_qr_codes}")
    print(f"   QR codes in batches: {qr_in_batches}")
    
    # 5. Statistics
    print("\n5. Overall Statistics:")
    stats = {
        'total_batches': QRBatch.objects.count(),
        'generated': QRBatch.objects.filter(print_status='generated').count(),
        'sent_for_print': QRBatch.objects.filter(print_status='sent_for_print').count(),
        'printing': QRBatch.objects.filter(print_status='printing').count(),
        'printed': QRBatch.objects.filter(print_status='printed').count(),
        'delivered': QRBatch.objects.filter(print_status='delivered').count(),
    }
    
    for key, value in stats.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    # 6. Test batch detail view data
    print("\n6. Testing Batch Detail Data...")
    if test_batch:
        test_batch.update_statistics()
        print(f"   Batch: {test_batch.batch_number}")
        print(f"   Activated: {test_batch.activated_count}")
        print(f"   Reserved: {test_batch.reserved_count}")
        print(f"   Available: {test_batch.available_count}")
        
        # Get QR codes in batch
        qr_codes = PreGeneratedQR.objects.filter(
            batch_number=test_batch.batch_number
        )[:5]
        
        print(f"\n   Sample QR codes (first 5):")
        for qr in qr_codes:
            print(f"   - {qr.qr_code}: {qr.get_status_display()}")
    
    # 7. Check URLs
    print("\n7. Batch Management URLs:")
    print("   Main page: /gateways/batch/management/")
    if test_batch:
        print(f"   Detail page: /gateways/batch/{test_batch.id}/detail/")
        print(f"   Update status: /gateways/batch/{test_batch.id}/update-status/")
    print("   Bulk update: /gateways/batch/bulk-update/")
    
    print("\n" + "=" * 60)
    print("✓ BATCH MANAGEMENT SYSTEM TEST COMPLETE")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Visit: http://localhost:8000/gateways/batch/management/")
    print("2. Test filtering by status")
    print("3. Test search functionality")
    print("4. Test status updates")
    print("5. Test bulk updates")
    print("6. View batch details")
    print("=" * 60)


if __name__ == '__main__':
    test_batch_management()
