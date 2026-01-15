#!/usr/bin/env python
"""
Detect ONLY the RIGHT-side yellow box for QR placement.
"""
from PIL import Image
import numpy as np
import os

template_path = 'static/tag/fix.jpeg'
template = Image.open(template_path).convert('RGB')

print(f"Template size: {template.size}")
width, height = template.size

# Convert to numpy
template_array = np.array(template)

# Detect yellow
r = template_array[:, :, 0]
g = template_array[:, :, 1]
b = template_array[:, :, 2]

yellow_mask = (r > 200) & (g > 150) & (b < 100)

# CRITICAL: Only look at RIGHT HALF of template
mid_point = width // 2
print(f"\nMid point: {mid_point}")
print(f"Looking only at RIGHT half (x > {mid_point})")

# Mask out left half
right_yellow_mask = yellow_mask.copy()
right_yellow_mask[:, :mid_point] = False

# Find yellow in right half
right_yellow_rows, right_yellow_cols = np.where(right_yellow_mask)

if len(right_yellow_rows) > 0:
    row_min, row_max = right_yellow_rows.min(), right_yellow_rows.max()
    col_min, col_max = right_yellow_cols.min(), right_yellow_cols.max()
    
    print(f"\n✅ RIGHT-side yellow box detected:")
    print(f"   Top-left: ({col_min}, {row_min})")
    print(f"   Bottom-right: ({col_max}, {row_max})")
    print(f"   Width: {col_max - col_min}")
    print(f"   Height: {row_max - row_min}")
    
    # Calculate center
    center_x = (col_min + col_max) // 2
    center_y = (row_min + row_max) // 2
    
    print(f"\n📍 Center: ({center_x}, {center_y})")
    
    # QR size (75% of box for margins)
    box_width = col_max - col_min
    box_height = row_max - row_min
    qr_size = int(min(box_width, box_height) * 0.75)
    
    print(f"\n📏 Recommended QR size: {qr_size}x{qr_size}")
    
    # Top-left position (centered)
    qr_x = center_x - (qr_size // 2)
    qr_y = center_y - (qr_size // 2)
    
    print(f"\n🎯 QR placement (top-left):")
    print(f"   X: {qr_x}")
    print(f"   Y: {qr_y}")
    
    print(f"\n💻 Use in code:")
    print(f"   QR_X = {qr_x}")
    print(f"   QR_Y = {qr_y}")
    print(f"   QR_SIZE = {qr_size}")
    
    # Visual check
    print(f"\n✓ Verification:")
    print(f"   QR right edge: {qr_x + qr_size} (should be < {col_max})")
    print(f"   QR bottom edge: {qr_y + qr_size} (should be < {row_max})")
    
else:
    print("❌ No yellow box found on RIGHT side")
