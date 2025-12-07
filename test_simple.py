#!/usr/bin/env python3
"""Test simple d'upload et d'inference"""
import requests
from pathlib import Path
import json

# Configuration
API_URL = "http://127.0.0.1:5000/api/predict"
TEST_IMAGE = Path("test/images/04_JPG.rf.4935d8061ad1c13154d00829b507412c.jpg")

if not TEST_IMAGE.exists():
    print(f"❌ Image non trouvée: {TEST_IMAGE}")
    exit(1)

print(f"📸 Envoi de l'image: {TEST_IMAGE.name}")
print(f"   Taille: {TEST_IMAGE.stat().st_size} bytes\n")

try:
    with open(TEST_IMAGE, 'rb') as f:
        files = {'image': f}
        print("⏳ Envoi de la requête...")
        response = requests.post(API_URL, files=files, timeout=30)
    
    print(f"✅ Réponse: HTTP {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        print("📊 Résultats:")
        result = data.get('result', {})
        print(f"   • Void Rate: {result.get('void_rate', 0):.2f}%")
        print(f"   • Chip Area: {result.get('chip_area', 0)} pixels")
        print(f"   • Holes Area: {result.get('holes_area', 0)} pixels")
        
        print(f"\n🔗 URLs:")
        mask_url = data.get('mask_url')
        print(f"   • Mask URL: {mask_url}")
        
        if mask_url:
            full_url = f"http://127.0.0.1:5000{mask_url}"
            print(f"\n🔍 Test d'accès au fichier masque...")
            mask_response = requests.get(full_url, timeout=5)
            print(f"   HTTP {mask_response.status_code}")
            print(f"   Taille: {len(mask_response.content)} bytes")
    else:
        print("❌ Erreur:", response.text[:500])
        
except Exception as e:
    print(f"❌ Erreur: {e}")
