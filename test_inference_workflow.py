#!/usr/bin/env python3
"""Test the complete inference workflow"""

import requests
import json
from pathlib import Path

# Configuration
API_URL = "http://127.0.0.1:5000/api/predict"
TEST_IMAGE_PATH = Path("test/images/04_JPG.rf.4935d8061ad1c13154d00829b507412c.jpg")

print("=" * 60)
print("TESTING INFERENCE WORKFLOW")
print("=" * 60)

# Check if test image exists
if not TEST_IMAGE_PATH.exists():
    print(f"❌ Test image not found: {TEST_IMAGE_PATH}")
    exit(1)

print(f"\n📸 Using test image: {TEST_IMAGE_PATH.name}")
print(f"   File size: {TEST_IMAGE_PATH.stat().st_size} bytes")

# Upload image and run inference
try:
    print("\n🚀 Uploading image and running inference...")
    with open(TEST_IMAGE_PATH, 'rb') as f:
        files = {'image': f}
        response = requests.post(API_URL, files=files)
    
    print(f"   Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ INFERENCE SUCCESSFUL!")
        print(f"\n📊 Statistics:")
        result = data.get('result', {})
        print(f"   • Void Rate: {result.get('void_rate', 0):.2f}%")
        print(f"   • Chip Area: {result.get('chip_area', 0)} pixels")
        print(f"   • Holes Area: {result.get('holes_area', 0)} pixels")
        print(f"   • Chip Percentage: {result.get('chip_percentage', 0):.2f}%")
        print(f"   • Holes Percentage: {result.get('holes_percentage', 0):.2f}%")
        print(f"   • Number of Chips: {result.get('num_chips', 0)}")
        print(f"   • Number of Holes: {result.get('num_holes', 0)}")
        
        print(f"\n🖼️  URLs:")
        print(f"   • Image URL: {data.get('image_url', 'N/A')}")
        print(f"   • Mask URL: {data.get('mask_url', 'N/A')}")
        
        # Test if mask file is accessible
        mask_url = data.get('mask_url')
        if mask_url:
            mask_full_url = f"http://127.0.0.1:5000{mask_url}"
            print(f"\n🔗 Testing mask file access...")
            print(f"   URL: {mask_full_url}")
            try:
                mask_response = requests.get(mask_full_url)
                print(f"   Status: {mask_response.status_code}")
                if mask_response.status_code == 200:
                    print(f"   Size: {len(mask_response.content)} bytes")
                    print("   ✅ Mask file accessible!")
                else:
                    print(f"   ❌ Failed to access mask file")
            except Exception as e:
                print(f"   ❌ Error accessing mask: {e}")
        
        print("\n✅ All checks passed!")
        
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
