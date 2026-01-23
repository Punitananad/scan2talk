"""
Views for downloading and displaying QR codes using HTML templates.
"""
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.conf import settings
import io
import base64

from .qr_models import PreGeneratedQR, QRBatch
from apps.core.utils import generate_qr_code


def generate_qr_base64(qr_code_text):
    """
    Generate QR code and return as base64 string for embedding in HTML.
    """
    protocol = 'http' if settings.DEBUG else 'https'
    url = f"{protocol}://{settings.PLATFORM_DOMAIN}/gateways/activate/{qr_code_text}/"
    qr_image_file = generate_qr_code(url)
    qr_image_file.seek(0)
    return base64.b64encode(qr_image_file.read()).decode('utf-8')


@staff_member_required
@require_http_methods(["GET"])
def preview_batch_sample(request, batch_number):
    """
    Preview the complete batch layout with all QR codes.
    Shows exactly what the PDF will look like.
    - For SINGLE type: 1 tag per QR code (8 tags per page)
    - For PAIR type: 2 tags per QR code (8 tags per page = 4 unique QRs with 2 copies each)
    """
    batch = get_object_or_404(QRBatch, batch_number=batch_number)
    qr_codes = list(PreGeneratedQR.objects.filter(batch_number=batch_number).select_related('category'))
    
    if not qr_codes:
        return HttpResponse("No QR codes in this batch", status=404)
    
    # Detect QR type from batch notes
    qr_type = 'single'  # default
    if batch.notes and '[QR Type: PAIR' in batch.notes:
        qr_type = 'pair'
    
    print(f"🔍 Preview batch {batch_number}: QR Type = {qr_type}, Total QR codes = {len(qr_codes)}")
    
    # Generate QR codes with base64 data
    qr_data_list = []
    for qr in qr_codes:
        qr_data = {
            'qr_code': qr.qr_code,
            'qr_code_data': generate_qr_base64(qr.qr_code),
            'category': qr.category  # Include category for visual indicator
        }
        
        # For SINGLE type: add once
        # For PAIR type: add twice (duplicate for front/back)
        qr_data_list.append(qr_data)
        if qr_type == 'pair':
            qr_data_list.append(qr_data)  # Add duplicate
    
    print(f"   - Total tags to display: {len(qr_data_list)}")
    
    # Split into pages (8 tags per page: 2 cols x 4 rows)
    tags_per_page = 8
    qr_pages = [qr_data_list[i:i + tags_per_page] for i in range(0, len(qr_data_list), tags_per_page)]
    
    print(f"   - Total pages: {len(qr_pages)}")
    
    # Render the batch print template (same as PDF but as HTML)
    context = {
        'qr_pages': qr_pages,
        'batch_number': batch_number,
        'qr_type': qr_type,
        'is_preview': True,  # Flag to indicate this is preview mode
    }
    
    return render(request, 'gateways/tag_print_design.html', context)


# PDF download functionality removed - use preview_batch_sample instead


@staff_member_required
@require_http_methods(["GET"])
def download_qr_zip(request, batch_number):
    """
    Download all QR codes in a batch as a ZIP file.
    """
    import zipfile
    
    batch = get_object_or_404(QRBatch, batch_number=batch_number)
    qr_codes = PreGeneratedQR.objects.filter(batch_number=batch_number)
    
    protocol = 'http' if settings.DEBUG else 'https'
    
    # Create ZIP in memory
    buffer = io.BytesIO()
    
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for qr in qr_codes:
            # Generate QR code image
            url = f"{protocol}://{settings.PLATFORM_DOMAIN}/gateways/activate/{qr.qr_code}/"
            qr_image_file = generate_qr_code(url)
            
            # Add to ZIP
            zip_file.writestr(f'QR_{qr.qr_code}.png', qr_image_file.read())
    
    # Return ZIP
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="QR_Batch_{batch_number}.zip"'
    return response


@staff_member_required
@require_http_methods(["GET"])
def download_qr_image(request, qr_id):
    """
    Download a single QR code image as a file.
    """
    qr = get_object_or_404(PreGeneratedQR, id=qr_id)
    
    protocol = 'http' if settings.DEBUG else 'https'
    url = f"{protocol}://{settings.PLATFORM_DOMAIN}/gateways/activate/{qr.qr_code}/"
    qr_image_file = generate_qr_code(url)
    
    response = HttpResponse(qr_image_file.read(), content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="QR_{qr.qr_code}.png"'
    return response


@staff_member_required
@require_http_methods(["GET"])
def view_qr_image(request, qr_id):
    """
    View a single QR code image in browser.
    """
    qr = get_object_or_404(PreGeneratedQR, id=qr_id)
    
    protocol = 'http' if settings.DEBUG else 'https'
    url = f"{protocol}://{settings.PLATFORM_DOMAIN}/gateways/activate/{qr.qr_code}/"
    qr_image_file = generate_qr_code(url)
    
    return HttpResponse(qr_image_file.read(), content_type='image/png')


@staff_member_required
def tag_clean_view(request):
    """
    Display the clean tag design page.
    """
    return render(request, 'gateways/tag_clean.html')


def tag_print_design(request):
    """
    Display the print-ready tag design (HTML/CSS only, no images).
    """
    return render(request, 'gateways/tag_print_design.html')
