"""
Generate and save a beautiful demo QR code for direct calling +91 7988269874
Saves as PNG file to static/tag/demo_qr.png
"""
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image, ImageDraw

def generate_and_save_call_qr(phone_number="+917988269874", output_path="static/tag/demo_qr.png"):
    """
    Generate a beautiful QR code with rounded corners and a phone icon in center
    Uses tel: URI scheme and saves as PNG
    """
    # Create tel: URI
    tel_uri = f"tel:{phone_number}"
    
    # Generate QR code with higher quality
    qr = qrcode.QRCode(
        version=4,  # Higher version for better quality
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction for logo overlay
        box_size=20,  # Larger box size for better quality
        border=2,
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
    center_size = int(min(width, height) * 0.22)
    center_x, center_y = width // 2, height // 2
    
    # Draw white circle background
    circle_bbox = [
        center_x - center_size // 2,
        center_y - center_size // 2,
        center_x + center_size // 2,
        center_y + center_size // 2
    ]
    draw.ellipse(circle_bbox, fill='white', outline='black', width=4)
    
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
    draw.polygon(phone_points, fill='#f5c400', outline='black', width=3)
    
    # Save as PNG
    img.save(output_path, format="PNG", quality=95, optimize=True)
    
    return output_path

if __name__ == "__main__":
    # Generate and save beautiful QR code
    output_file = generate_and_save_call_qr()
    
    print("=" * 60)
    print("✨ Beautiful QR Code Generated & Saved! ✨")
    print("=" * 60)
    print(f"\nPhone Number: +91 7988269874")
    print(f"Saved to: {output_file}")
    print(f"\nFeatures:")
    print("  • Rounded corners for modern look")
    print("  • Yellow phone icon in center")
    print("  • High error correction")
    print("  • Print-ready quality (high resolution)")
    print("  • Optimized PNG format")
    print("\n" + "=" * 60)
    print("\n✅ Ready to use in templates with {% static 'tag/demo_qr.png' %}")
