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


def create_composite_tag_image(qr_code_text, template_path, settings):
    """
    SHARED FUNCTION: Create composite tag with QR overlaid on template.
    Used by BOTH preview and PDF to ensure they look IDENTICAL.
    
    Args:
        qr_code_text: The QR code string
        template_path: Path to template image
        settings: Django settings object
        
    Returns:
        PIL Image object (composite)
    """
    from PIL import Image, ImageDraw, ImageFilter
    
    # Load template
    template = Image.open(template_path)
    template = template.convert('RGB')
    
    # Generate QR code
    protocol = 'http' if settings.DEBUG else 'https'
    url = f"{protocol}://{settings.PLATFORM_DOMAIN}/gateways/activate/{qr_code_text}/"
    qr_image_file = generate_qr_code(url)
    
    # Load QR
    qr_img = Image.open(qr_image_file)
    qr_img = qr_img.convert('RGBA')
    
    # FIXED COORDINATES for RIGHT-side yellow box
    QR_SIZE = 333
    QR_X = 860
    QR_Y = 79
    
    # Resize QR
    qr_img = qr_img.resize((QR_SIZE, QR_SIZE), Image.LANCZOS)
    
    # Create rounded corner mask
    mask = Image.new('L', (QR_SIZE, QR_SIZE), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (QR_SIZE, QR_SIZE)], radius=30, fill=255)
    
    # Apply mask to QR
    qr_rounded = Image.new('RGBA', (QR_SIZE, QR_SIZE), (255, 255, 255, 0))
    qr_rounded.paste(qr_img, (0, 0))
    qr_rounded.putalpha(mask)
    
    # Add subtle shadow for depth
    shadow = Image.new('RGBA', (QR_SIZE + 20, QR_SIZE + 20), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle([(10, 10), (QR_SIZE + 10, QR_SIZE + 10)], radius=30, fill=(0, 0, 0, 40))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    
    # Paste shadow first, then QR
    template.paste(shadow, (QR_X - 10, QR_Y - 10), shadow)
    template.paste(qr_rounded, (QR_X, QR_Y), qr_rounded)
    
    return template


@staff_member_required
@require_http_methods(["GET"])
def preview_batch_sample(request, batch_number):
    """
    Preview a 2x4 grid (8 tags) showing how the A4 page will look.
    Shows the first 8 QR codes overlaid on template in the same layout as PDF.
    """
    from django.conf import settings
    from PIL import Image, ImageDraw, ImageFilter
    import os
    
    batch = get_object_or_404(QRBatch, batch_number=batch_number)
    qr_codes = list(PreGeneratedQR.objects.filter(batch_number=batch_number)[:8])
    
    if not qr_codes:
        return HttpResponse("No QR codes in this batch", status=404)
    
    # Template path
    template_path = os.path.join(settings.BASE_DIR, 'static', 'tag', 'clean.jpeg')
    
    if not os.path.exists(template_path):
        return HttpResponse("Template not found", status=404)
    
    try:
        # Load template once
        template_original = Image.open(template_path).convert('RGB')
        template_width, template_height = template_original.size
        
        # Layout: 2 columns x 4 rows = 8 tags
        cols = 2
        rows = 4
        margin = 20  # pixels between tags
        
        # Calculate preview size (smaller for web display)
        tag_width = 600  # pixels per tag
        tag_height = int(tag_width * template_height / template_width)
        
        # Create canvas for 2x4 grid
        canvas_width = (tag_width * cols) + (margin * (cols + 1))
        canvas_height = (tag_height * rows) + (margin * (rows + 1))
        canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
        
        protocol = 'http' if settings.DEBUG else 'https'
        
        # QR positioning (proportional to template size)
        QR_SIZE_RATIO = 333 / template_width
        QR_X_RATIO = 860 / template_width
        QR_Y_RATIO = 79 / template_height
        
        for idx, qr in enumerate(qr_codes):
            row = idx // cols
            col = idx % cols
            
            # Position on canvas
            x = margin + (col * (tag_width + margin))
            y = margin + (row * (tag_height + margin))
            
            # Create tag with QR
            tag = template_original.copy()
            tag = tag.resize((tag_width, tag_height), Image.LANCZOS)
            
            # Generate QR code
            url = f"{protocol}://{settings.PLATFORM_DOMAIN}/gateways/activate/{qr.qr_code}/"
            qr_image_file = generate_qr_code(url)
            qr_img = Image.open(qr_image_file).convert('RGBA')
            
            # Scale QR size to match resized template
            qr_size = int(tag_width * QR_SIZE_RATIO)
            qr_x = int(tag_width * QR_X_RATIO)
            qr_y = int(tag_height * QR_Y_RATIO)
            
            qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)
            
            # Add rounded corners
            mask = Image.new('L', (qr_size, qr_size), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([(0, 0), (qr_size, qr_size)], radius=int(30 * tag_width / template_width), fill=255)
            
            qr_rounded = Image.new('RGBA', (qr_size, qr_size), (255, 255, 255, 0))
            qr_rounded.paste(qr_img, (0, 0))
            qr_rounded.putalpha(mask)
            
            # Paste QR on tag
            tag.paste(qr_rounded, (qr_x, qr_y), qr_rounded)
            
            # Paste tag on canvas
            canvas.paste(tag, (x, y))
        
        # Return as PNG
        buffer = io.BytesIO()
        canvas.save(buffer, format='PNG', quality=95)
        buffer.seek(0)
        
        return HttpResponse(buffer.read(), content_type='image/png')
        
    except Exception as e:
        return HttpResponse(f"Error generating preview: {str(e)}", status=500)


@staff_member_required
@require_http_methods(["GET"])
def download_batch_pdf(request, batch_number):
    """
    Download all QR codes overlaid on template as printable A4 sheets.
    Layout: 2 columns x 4 rows = 8 tags per A4 page.
    """
    from django.conf import settings
    from PIL import Image, ImageDraw, ImageFilter
    import os
    import tempfile
    
    batch = get_object_or_404(QRBatch, batch_number=batch_number)
    qr_codes = PreGeneratedQR.objects.filter(batch_number=batch_number)
    
    # Create PDF in memory
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Template path
    template_path = os.path.join(settings.BASE_DIR, 'static', 'tag', 'clean.jpeg')
    
    if not os.path.exists(template_path):
        return HttpResponse("Template not found", status=404)
    
    # Load template once
    template_original = Image.open(template_path).convert('RGB')
    template_width, template_height = template_original.size
    
    # Layout: 2 columns x 4 rows = 8 tags per page
    cols = 2
    rows = 4
    tags_per_page = cols * rows
    
    # Calculate tag size to fit A4 (in points)
    margin = 0.3 * inch
    tag_width_pts = (width - (margin * 2) - (margin * (cols - 1))) / cols
    tag_height_pts = (height - (margin * 2) - (margin * (rows - 1))) / rows
    
    # QR positioning ratios (based on original template)
    QR_SIZE_RATIO = 333 / template_width
    QR_X_RATIO = 860 / template_width
    QR_Y_RATIO = 79 / template_height
    
    protocol = 'http' if settings.DEBUG else 'https'
    
    for idx, qr in enumerate(qr_codes):
        # New page if needed
        if idx > 0 and idx % tags_per_page == 0:
            p.showPage()
        
        # Calculate position on PDF
        row = (idx % tags_per_page) // cols
        col = idx % cols
        
        x = margin + (col * (tag_width_pts + margin))
        y = height - margin - ((row + 1) * (tag_height_pts + margin))
        
        try:
            # Create tag with QR overlay
            tag = template_original.copy()
            
            # Generate QR code
            url = f"{protocol}://{settings.PLATFORM_DOMAIN}/gateways/activate/{qr.qr_code}/"
            qr_image_file = generate_qr_code(url)
            qr_img = Image.open(qr_image_file).convert('RGBA')
            
            # Calculate QR size and position
            qr_size = int(template_width * QR_SIZE_RATIO)
            qr_x = int(template_width * QR_X_RATIO)
            qr_y = int(template_height * QR_Y_RATIO)
            
            qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)
            
            # Add rounded corners
            mask = Image.new('L', (qr_size, qr_size), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([(0, 0), (qr_size, qr_size)], radius=30, fill=255)
            
            qr_rounded = Image.new('RGBA', (qr_size, qr_size), (255, 255, 255, 0))
            qr_rounded.paste(qr_img, (0, 0))
            qr_rounded.putalpha(mask)
            
            # Paste QR on tag
            tag.paste(qr_rounded, (qr_x, qr_y), qr_rounded)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                tag.save(tmp, format='PNG', dpi=(300, 300))
                tmp_path = tmp.name
            
            # Draw on PDF
            p.drawImage(tmp_path, x, y, width=tag_width_pts, height=tag_height_pts, 
                       preserveAspectRatio=True, mask='auto')
            
            # Clean up
            os.unlink(tmp_path)
            
        except Exception as e:
            # Fallback: just draw QR code
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                qr_image_file.seek(0)
                tmp.write(qr_image_file.read())
                tmp_path = tmp.name
            
            p.drawImage(tmp_path, x, y, width=tag_width_pts, height=tag_height_pts)
            p.setFont("Helvetica-Bold", 10)
            p.drawString(x, y - 0.2*inch, qr.qr_code)
            
            os.unlink(tmp_path)
    
    # Finalize PDF
    p.showPage()
    p.save()
    
    # Return PDF
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="PrintReady_Batch_{batch_number}.pdf"'
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
def download_qr_image(request, qr_id):
    """
    Download a single QR code image as a file.
    """
    qr = get_object_or_404(PreGeneratedQR, id=qr_id)
    
    from django.conf import settings
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
    
    from django.conf import settings
    protocol = 'http' if settings.DEBUG else 'https'
    url = f"{protocol}://{settings.PLATFORM_DOMAIN}/gateways/activate/{qr.qr_code}/"
    qr_image_file = generate_qr_code(url)
    
    return HttpResponse(qr_image_file.read(), content_type='image/png')
