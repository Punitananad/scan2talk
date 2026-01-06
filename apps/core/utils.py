# Core utilities - placeholder functions
import random
import string
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

def encrypt_data(data):
    """Placeholder encryption function"""
    return data

def decrypt_data(data):
    """Placeholder decryption function"""
    return data

def generate_short_code(length=8):
    """Generate a random short code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_qr_code(data):
    """Generate QR code image and return as ContentFile"""
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Add data to QR code
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Return as ContentFile
    return ContentFile(buffer.read())