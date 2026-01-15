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
    """Generate HIGH QUALITY QR code image and return as ContentFile"""
    # Create QR code instance with HIGH quality settings
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Highest error correction
        box_size=20,  # Increased from 10 for higher resolution
        border=2,     # Reduced border for more QR space
    )
    
    # Add data to QR code
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create HIGH RESOLUTION image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO with maximum quality
    buffer = BytesIO()
    img.save(buffer, format='PNG', optimize=False)
    buffer.seek(0)
    
    # Return as ContentFile
    return ContentFile(buffer.read())