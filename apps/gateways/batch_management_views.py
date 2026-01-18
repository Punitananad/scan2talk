"""
Batch Management Views for QR Code Batches
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Sum, Count, Q

from .qr_models import QRBatch, PreGeneratedQR


@staff_member_required
def batch_management(request):
    """
    Batch Management Dashboard - View all batches with status tracking
    """
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    batches = QRBatch.objects.select_related('created_by', 'category').all()
    
    # Apply filters
    if status_filter != 'all':
        batches = batches.filter(print_status=status_filter)
    
    if search_query:
        batches = batches.filter(
            Q(batch_number__icontains=search_query) |
            Q(purpose__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # Calculate statistics
    stats = {
        'total_batches': QRBatch.objects.count(),
        'generated': QRBatch.objects.filter(print_status='generated').count(),
        'sent_for_print': QRBatch.objects.filter(print_status='sent_for_print').count(),
        'printing': QRBatch.objects.filter(print_status='printing').count(),
        'printed': QRBatch.objects.filter(print_status='printed').count(),
        'delivered': QRBatch.objects.filter(print_status='delivered').count(),
        'total_qr_codes': QRBatch.objects.aggregate(total=Sum('quantity'))['total'] or 0,
        'total_activated': QRBatch.objects.aggregate(total=Sum('activated_count'))['total'] or 0,
    }
    
    # Status choices for filter dropdown
    status_choices = QRBatch.STATUS_CHOICES
    
    context = {
        'batches': batches[:100],  # Limit to 100 for performance
        'stats': stats,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': status_choices,
    }
    
    return render(request, 'gateways/batch_management.html', context)


@staff_member_required
@require_http_methods(["POST"])
def update_batch_status(request, batch_id):
    """
    Update batch print status
    """
    try:
        batch = get_object_or_404(QRBatch, id=batch_id)
        new_status = request.POST.get('status')
        print_notes = request.POST.get('print_notes', '')
        
        if new_status not in dict(QRBatch.STATUS_CHOICES):
            return JsonResponse({'success': False, 'error': 'Invalid status'})
        
        # Update status
        old_status = batch.print_status
        batch.print_status = new_status
        
        # Update timestamps based on status
        if new_status == 'sent_for_print' and not batch.sent_for_print_at:
            batch.sent_for_print_at = timezone.now()
        elif new_status == 'printing' and not batch.printing_started_at:
            batch.printing_started_at = timezone.now()
        elif new_status == 'printed' and not batch.printed_at:
            batch.printed_at = timezone.now()
        elif new_status == 'delivered' and not batch.delivered_at:
            batch.delivered_at = timezone.now()
        
        # Update notes if provided
        if print_notes:
            batch.print_notes = print_notes
        
        batch.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Batch {batch.batch_number} updated from {old_status} to {new_status}',
            'new_status': new_status,
            'status_display': batch.get_print_status_display()
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@staff_member_required
def batch_detail(request, batch_id):
    """
    View detailed information about a specific batch
    """
    batch = get_object_or_404(QRBatch, id=batch_id)
    
    # Update statistics
    batch.update_statistics()
    
    # Get QR codes in this batch
    qr_codes = PreGeneratedQR.objects.filter(
        batch_number=batch.batch_number
    ).select_related('owner', 'gateway', 'category')[:50]  # Limit to 50 for display
    
    # Calculate additional stats
    qr_stats = PreGeneratedQR.objects.filter(batch_number=batch.batch_number).aggregate(
        total=Count('id'),
        activated=Count('id', filter=Q(status='activated')),
        available=Count('id', filter=Q(status='available')),
        reserved=Count('id', filter=Q(status='reserved')),
    )
    
    context = {
        'batch': batch,
        'qr_codes': qr_codes,
        'qr_stats': qr_stats,
        'status_choices': QRBatch.STATUS_CHOICES,
    }
    
    return render(request, 'gateways/batch_detail.html', context)


@staff_member_required
@require_http_methods(["POST"])
def bulk_update_batch_status(request):
    """
    Bulk update status for multiple batches
    """
    try:
        batch_ids = request.POST.getlist('batch_ids[]')
        new_status = request.POST.get('status')
        
        if not batch_ids:
            return JsonResponse({'success': False, 'error': 'No batches selected'})
        
        if new_status not in dict(QRBatch.STATUS_CHOICES):
            return JsonResponse({'success': False, 'error': 'Invalid status'})
        
        # Update all selected batches
        updated_count = 0
        for batch_id in batch_ids:
            try:
                batch = QRBatch.objects.get(id=batch_id)
                batch.print_status = new_status
                
                # Update timestamps
                if new_status == 'sent_for_print' and not batch.sent_for_print_at:
                    batch.sent_for_print_at = timezone.now()
                elif new_status == 'printing' and not batch.printing_started_at:
                    batch.printing_started_at = timezone.now()
                elif new_status == 'printed' and not batch.printed_at:
                    batch.printed_at = timezone.now()
                elif new_status == 'delivered' and not batch.delivered_at:
                    batch.delivered_at = timezone.now()
                
                batch.save()
                updated_count += 1
            except QRBatch.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'Updated {updated_count} batches to {new_status}',
            'updated_count': updated_count
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
