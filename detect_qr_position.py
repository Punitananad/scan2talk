#!/usr/bin/env python
"""
Detect the correct QR position in the template.
"""
from PIL import Image
import numpy as np
import os

# Load template
template_path = 'static/tag/fix.jpeg'

if not os.path.exists(template_path):
    print(f"❌ Template not found: {template_path}")
    exit(1)

template = Image.open(template_path)
template = template.convert('RGB')

print(f"Template size: {template.size}")
print(f"Width: {template.width}, Height: {template.height}")

# Convert to numpy
template_array = np.array(template)

# Detect yellow box
r = template_array[:, :, 0]
g = template_array[:, :, 1]
b = template_array[:, :, 2]

# Yellow detection
yellow_mask = (r > 200) & (g > 150) & (b < 100)

# Find yellow pixels
yellow_rows, yellow_cols = np.where(yellow_mask)

if len(yellow_rows) > 0:
    # Get bounds
    row_min, row_max = yellow_rows.min(), yellow_rows.max()
    col_min, col_max = yellow_cols.min(), yellow_cols.max()
    
    print(f"\n✅ Yellow box detected:")
    print(f"   Top-left: ({col_min}, {row_min})")
    print(f"   Bottom-right: ({col_max}, {row_max})")
    print(f"   Width: {col_max - col_min}")
    print(f"   Height: {row_max - row_min}")
    
    # Calculate center
    center_x = (col_min + col_max) // 2
    center_y = (row_min + row_max) // 2
    
    print(f"\n📍 Center of yellow box:")
    print(f"   X: {center_x}")
    print(f"   Y: {center_y}")
    
    # Recommended QR size (80% of box)
    box_width = col_max - col_min
    box_height = row_max - row_min
    qr_size = int(min(box_width, box_height) * 0.80)
    
    print(f"\n📏 Recommended QR size: {qr_size}x{qr_size}")
    
    # Top-left position for QR (centered in box)
    qr_x = center_x - (qr_size // 2)
    qr_y = center_y - (qr_size // 2)
    
    print(f"\n🎯 QR placement (top-left corner):")
    print(f"   X: {qr_x}")
    print(f"   Y: {qr_y}")
    print(f"   Size: {qr_size}x{qr_size}")
    
    print(f"\n💻 Use these values in code:")
    print(f"   QR_X = {qr_x}")
    print(f"   QR_Y = {qr_y}")
    print(f"   QR_SIZE = {qr_size}")
    
else:
    print("❌ No yellow box detected")
    print("\nTrying to find the brightest area...")
    
    # Convert to grayscale
    gray = np.mean(template_array, axis=2)
    
    # Find brightest region
    threshold = np.percentile(gray, 95)
    bright_mask = gray > threshold
    
    bright_rows, bright_cols = np.where(bright_mask)
    
    if len(bright_rows) > 0:
        row_min, row_max = bright_rows.min(), bright_rows.max()
        col_min, col_max = bright_cols.min(), bright_cols.max()
        
        print(f"✅ Bright area detected:")
        print(f"   Top-left: ({col_min}, {row_min})")
        print(f"   Bottom-right: ({col_max}, {row_max})")
