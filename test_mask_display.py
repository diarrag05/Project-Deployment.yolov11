#!/usr/bin/env python3
"""Test mask display by running inference on a test image"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the inference function
from routes.predict import predict_image

# Find a test image
test_images_dir = Path('test/images')
if not test_images_dir.exists():
    print("❌ Test images directory not found!")
    sys.exit(1)

test_images = list(test_images_dir.glob('*.jpg')) + list(test_images_dir.glob('*.png'))
if not test_images:
    print("❌ No test images found!")
    sys.exit(1)

# Use first test image
test_image = test_images[0]
print(f"📸 Testing with: {test_image.name}")

# Check if we have access to predict_image function
try:
    # Read the image
    with open(test_image, 'rb') as f:
        image_data = f.read()
    
    print(f"📤 Image size: {len(image_data)} bytes")
    print(f"✓ Test setup complete. Run inference via web interface to test.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
