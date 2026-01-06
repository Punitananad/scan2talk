"""
Views for downloading and displaying QR codes.
"""
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, FileResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch

from .qr_models import PreGeneratedQR, QRBatch
from apps.core.utils import generate_qr_code


@staff_member_required
@require_http_methods(["GET"])
def download_qr_image(request, qr_id):
    """
    Download a single QR code image.
    """
    qr = get_object_or_404(PreGeneratedQR, id=qr_id)
    
    # If QR image doesn't exist, generate it
    if not qr.qr_image:
        qr.generate_qr_image()
        qr.refresh_from_db()
    
    # If still no image, generate on-the-fly
    if not qr.qr_image:
        from django.conf import settings
        protocol = 'http' if settings.DEBUG else 'https'
        url = f"{protocol}://{settings.PLATFORM_DOMAIN}/gateways/activate/{qr.qr_code}/"
        qr_image_file = generate_qr_code(url)
        
        response = HttpResponse(qr_image_file.read(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="QR_{qr.qr_code}.png"'
        return response
    
    # Return existing image
    response = FileResponse(qr.qr_image.open('rb'), content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="QR_{qr.qr_code}.png"'
    return response


@staff_member_required
@require_http_methods(["GET"])
def download_batch_pdf(request, batch_number):
    """
    Download all QR codes in a batch as a PDF.
    """
    from django.conf import settings
    
    batch = get_object_or_404(QRBatch, batch_number=batch_number)
    qr_codes = PreGeneratedQR.objects.filter(batch_number=batch_number)
    
    # Create PDF in memory
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(1*inch, height - 1*inch, f"QR Codes - Batch: {batch_number}")
    p.setFont("Helvetica", 10)
    p.drawString(1*inch, height - 1.3*inch, f"Total: {qr_codes.count()} codes")
    
    # QR codes grid (4 per row, 6 rows per page)
    x_start = 0.5 * inch
    y_start = height - 2 * inch
    qr_size = 1.5 * inch
    x_spacing = 2 * inch
    y_spacing = 2.5 * inch
    
    codes_per_row = 4
    rows_per_page = 6
    
    protocol = 'http' if settings.DEBUG else 'https'
    
    for idx, qr in enumerate(qr_codes):
        # Calculate position
        row = (idx % (codes_per_row * rows_per_page)) // codes_per_row
        col = idx % codes_per_row
        
        # New page if needed
        if idx > 0 and idx % (codes_per_row * rows_per_page) == 0:
            p.showPage()
            p.setFont("Helvetica", 10)
            y_start = height - 1 * inch
        
        x = x_start + (col * x_spacing)
        y = y_start - (row * y_spacing)
        
        # Generate QR code image
        url = f"{protocol}://{settings.PLATFORM_DOMAIN}/gateways/activate/{qr.qr_code}/"
        qr_image_file = generate_qr_code(url)
        
        # Save to temp file for reportlab
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            tmp.write(qr_image_file.read())
            tmp_path = tmp.name
        
        # Draw QR code
        try:
            p.drawImage(tmp_path, x, y, width=qr_size, height=qr_size)
        except:
            pass  # Skip if image fails
        
        # Draw QR code text
        p.setFont("Helvetica-Bold", 12)
        p.drawString(x, y - 0.2*inch, qr.qr_code)
        p.setFont("Helvetica", 8)
        p.drawString(x, y - 0.4*inch, f"Scan to activate")
        
        # Clean up temp file
        import os
        try:
            os.unlink(tmp_path)
        except:
            pass
    
    # Finalize PDF
    p.showPage()
    p.save()
    
    # Return PDF
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="QR_Batch_{batch_number}.pdf"'
    return response


@staff_member_required
@require_http_methods(["GET"])
def download_qr_zip(request, batch_number):
    """
    Download all QR codes in a batch as a ZIP file.
    """
    import zipfile
    from django.conf import settings
    
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
def view_qr_image(request, qr_id):
    """
    View a single QR code image in browser.
    """
    qr = get_object_or_404(PreGeneratedQR, id=qr_id)
    
    from django.conf import settings
    protocol = 'http' if settings.DEBUG else 'https'
    url = f"{protocol}://{settings.PLATFORM_DOMAIN}/gateways/activate/{qr.qr_code}/"
    qr_image_file = generate_qr_code(url)
    
    return HttpResponse(qr_image_file.read(), content_type='image/png')
