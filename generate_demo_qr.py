"""
Generate a beautiful demo QR code for direct calling +91 7988269874
This QR code will be embedded in the tag design template with a logo overlay
"""
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def generate_beautiful_call_qr(phone_number="+917988269874"):
    """
    Generate a beautiful QR code with rounded corners and a phone icon in center
    Uses tel: URI scheme
    """
    # Create tel: URI
    tel_uri = f"tel:{phone_number}"
    
    # Generate QR code with higher quality
    qr = qrcode.QRCode(
        version=3,  # Higher version for better quality
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction for logo overlay
        box_size=15,
        border=1,
    )
    qr.add_data(tel_uri)
    qr.make(fit=True)
    
    # Create image with rounded modules and color
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(back_color=(255, 255, 255), front_color=(0, 0, 0))
    )
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Add a phone icon in the center
    width, height = img.size
    
    # Create a white circle in the center
    draw = ImageDraw.Draw(img)
    center_size = int(min(width, height) * 0.25)
    center_x, center_y = width // 2, height // 2
    
    # Draw white circle background
    circle_bbox = [
        center_x - center_size // 2,
        center_y - center_size // 2,
        center_x + center_size // 2,
        center_y + center_size // 2
    ]
    draw.ellipse(circle_bbox, fill='white', outline='black', width=3)
    
    # Draw phone icon (simplified)
    icon_size = center_size // 2
    icon_x, icon_y = center_x, center_y
    
    # Phone receiver shape
    phone_points = [
        (icon_x - icon_size//3, icon_y - icon_size//3),
        (icon_x - icon_size//4, icon_y - icon_size//2),
        (icon_x + icon_size//4, icon_y - icon_size//4),
        (icon_x + icon_size//2, icon_y + icon_size//4),
        (icon_x + icon_size//3, icon_y + icon_size//3),
        (icon_x + icon_size//4, icon_y + icon_size//2),
        (icon_x - icon_size//4, icon_y + icon_size//4),
        (icon_x - icon_size//2, icon_y - icon_size//4),
    ]
    draw.polygon(phone_points, fill='#f5c400', outline='black', width=2)
    
    # Convert to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG", quality=95)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str

if __name__ == "__main__":
    # Generate beautiful QR code
    qr_base64 = generate_beautiful_call_qr()
    
    print("=" * 60)
    print("✨ Beautiful QR Code Generated Successfully! ✨")
    print("=" * 60)
    print(f"\nPhone Number: +91 7988269874")
    print(f"Features:")
    print("  • Rounded corners for modern look")
    print("  • Phone icon in center")
    print("  • High error correction")
    print("  • Print-ready quality")
    print(f"\nQR Code Data (Base64): {qr_base64[:50]}...")
    print(f"Total length: {len(qr_base64)} characters")
    print("\n" + "=" * 60)
    
    # Save to file for reference
    with open("demo_qr_base64.txt", "w") as f:
        f.write(qr_base64)
    
    print("\n✅ Beautiful QR code base64 saved to: demo_qr_base64.txt")

