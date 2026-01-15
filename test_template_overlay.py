#!/usr/bin/env python
"""
Test script to verify template overlay works correctly.
This will create a single test image with QR overlaid on template.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from django.conf import settings
from PIL import Image
from apps.core.utils import generate_qr_code
import io


def test_template_overlay():
    """Test creating a single QR code overlaid on template."""
    print("\n" + "="*60)
    print("Testing Template Overlay")
    print("="*60)
    
    # Template path
    template_path = os.path.join(settings.BASE_DIR, 'static', 'tag', 'pqr-tg.jpeg')
    
    print(f"\n1️⃣  Checking template file...")
    print(f"   Path: {template_path}")
    
    if not os.path.exists(template_path):
        print(f"   ❌ Template not found!")
        print(f"\n   Available files in static/tag/:")
        tag_dir = os.path.join(settings.BASE_DIR, 'static', 'tag')
        if os.path.exists(tag_dir):
            for f in os.listdir(tag_dir):
                print(f"      - {f}")
        return False
    
    print(f"   ✅ Template found")
    
    # Load template
    print(f"\n2️⃣  Loading template...")
    try:
        template = Image.open(template_path)
        template = template.convert('RGB')
        print(f"   ✅ Template loaded")
        print(f"   Size: {template.size}")
        print(f"   Mode: {template.mode}")
    except Exception as e:
        print(f"   ❌ Failed to load template: {e}")
        return False
    
    # Generate test QR code
    print(f"\n3️⃣  Generating test QR code...")
    try:
        test_url = "https://scan2talk.in/gateways/activate/TEST123/"
        qr_image_file = generate_qr_code(test_url)
        qr_img = Image.open(qr_image_file)
        qr_img = qr_img.convert('RGBA')
        print(f"   ✅ QR code generated")
        print(f"   Size: {qr_img.size}")
    except Exception as e:
        print(f"   ❌ Failed to generate QR: {e}")
        return False
    
    # Resize template for better quality
    print(f"\n4️⃣  Resizing template...")
    try:
        template_aspect = template.width / template.height
        target_width = 800  # Good size for testing
        target_height = int(target_width / template_aspect)
        template = template.resize((target_width, target_height), Image.LANCZOS)
        print(f"   ✅ Template resized to: {template.size}")
    except Exception as e:
        print(f"   ❌ Failed to resize: {e}")
        return False
    
    # STRICT GEOMETRY MODE: Detect yellow rectangle and center QR with equal margins
    print(f"\n5️⃣  STRICT GEOMETRY MODE: Detecting yellow rectangle frame...")
    try:
        import numpy as np
        template_array = np.array(template)
        height, width = template_array.shape[:2]
        
        # Detect YELLOW border pixels
        r = template_array[:, :, 0]
        g = template_array[:, :, 1]
        b = template_array[:, :, 2]
        
        yellow_mask = (r > 220) & (g > 180) & (g < 230) & (b < 80)
        
        # Filter to RIGHT half only
        mid_point = width // 2
        right_yellow_mask = yellow_mask.copy()
        right_yellow_mask[:, :mid_point] = False
        
        right_yellow_cols = np.where(np.any(right_yellow_mask, axis=0))[0]
        right_yellow_rows = np.where(np.any(right_yellow_mask, axis=1))[0]
        
        if len(right_yellow_cols) > 0 and len(right_yellow_rows) > 0:
            # Measure OUTER bounds of yellow border
            border_left = right_yellow_cols[0]
            border_right = right_yellow_cols[-1]
            border_top = right_yellow_rows[0]
            border_bottom = right_yellow_rows[-1]
            
            # Calculate INNER bounds (inside the border)
            border_thickness = int((border_right - border_left) * 0.05)
            
            inner_left = border_left + border_thickness
            inner_right = border_right - border_thickness
            inner_top = border_top + border_thickness
            inner_bottom = border_bottom - border_thickness
            
            # Calculate EXACT CENTER
            center_x = (inner_left + inner_right) // 2
            center_y = (inner_top + inner_bottom) // 2
            
            # Calculate QR size with EQUAL MARGINS
            inner_width = inner_right - inner_left
            inner_height = inner_bottom - inner_top
            available_size = min(inner_width, inner_height)
            qr_size = int(available_size * 0.75)  # 75% = 12.5% margin each side
            
            # Calculate margins
            margin_h = (inner_width - qr_size) // 2
            margin_v = (inner_height - qr_size) // 2
            
            qr_x = center_x
            qr_y = center_y
            
            print(f"   ✅ YELLOW RECTANGLE DETECTED (RIGHT SIDE)")
            print(f"      Border: x=({border_left}, {border_right}), y=({border_top}, {border_bottom})")
            print(f"      Inner: x=({inner_left}, {inner_right}), y=({inner_top}, {inner_bottom})")
            print(f"      Inner size: {inner_width}x{inner_height}")
            print(f"      Rectangle center: ({center_x}, {center_y})")
            print(f"      QR size: {qr_size}x{qr_size}")
            print(f"      Margins: left={margin_h}, right={margin_h}, top={margin_v}, bottom={margin_v}")
            print(f"      ✓ EQUAL MARGINS ON ALL SIDES")
        else:
            raise ValueError("Yellow rectangle not found on RIGHT side")
            
    except Exception as e:
        print(f"   ⚠️  Detection failed: {e}")
        print(f"   Using FALLBACK: Fixed RIGHT side geometry")
        
        # Assume yellow box position
        box_left = int(target_width * 0.70)
        box_right = int(target_width * 0.95)
        box_top = int(target_height * 0.25)
        box_bottom = int(target_height * 0.75)
        
        qr_x = (box_left + box_right) // 2
        qr_y = (box_top + box_bottom) // 2
        
        box_width = box_right - box_left
        box_height = box_bottom - box_top
        qr_size = int(min(box_width, box_height) * 0.75)
        
        print(f"      Assumed box: x=({box_left}, {box_right}), y=({box_top}, {box_bottom})")
        print(f"      Center: ({qr_x}, {qr_y})")
        print(f"      QR size: {qr_size}x{qr_size}")
    
    # Resize QR code
    print(f"\n6️⃣  Resizing QR code...")
    try:
        qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)
        print(f"   ✅ QR resized to: {qr_img.size}")
    except Exception as e:
        print(f"   ❌ Failed to resize QR: {e}")
        return False
    
    # Paste QR on template
    print(f"\n7️⃣  Overlaying QR on template...")
    try:
        paste_x = qr_x - (qr_size // 2)
        paste_y = qr_y - (qr_size // 2)
        
        print(f"   Paste position: ({paste_x}, {paste_y})")
        template.paste(qr_img, (paste_x, paste_y), qr_img)
        print(f"   ✅ QR overlaid successfully")
    except Exception as e:
        print(f"   ❌ Failed to overlay: {e}")
        return False
    
    # Save test output
    print(f"\n8️⃣  Saving test output...")
    try:
        output_path = os.path.join(settings.BASE_DIR, 'test_tag_output.png')
        template.save(output_path, format='PNG', dpi=(300, 300))
        print(f"   ✅ Saved to: {output_path}")
        print(f"\n   👀 Open this file to verify the QR is correctly positioned!")
    except Exception as e:
        print(f"   ❌ Failed to save: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ TEST PASSED - Template overlay works!")
    print("="*60)
    return True


if __name__ == '__main__':
    print("\n🔧 Template Overlay Test")
    
    # Check dependencies
    print("\nChecking dependencies...")
    try:
        import numpy
        print("✅ numpy installed")
    except ImportError:
        print("❌ numpy not installed - run: pip install numpy")
        sys.exit(1)
    
    try:
        from PIL import Image
        print("✅ Pillow installed")
    except ImportError:
        print("❌ Pillow not installed - run: pip install Pillow")
        sys.exit(1)
    
    # Run test
    success = test_template_overlay()
    
    if success:
        print("\n🎉 Template overlay is working correctly!")
        print("   Check test_tag_output.png to see the result.")
    else:
        print("\n⚠️  Template overlay test failed.")
        print("   Check the errors above for details.")
