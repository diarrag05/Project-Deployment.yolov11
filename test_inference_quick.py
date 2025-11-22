#!/usr/bin/env python
"""
Test rapide d'inférence
"""

from pathlib import Path
from ultralytics import YOLO
import json

PROJECT_DIR = Path(__file__).parent
MODEL_PATH = PROJECT_DIR / "models" / "yolov8n-seg_trained.pt"
TEST_DIR = PROJECT_DIR / "test" / "images"
OUTPUT_DIR = PROJECT_DIR / "inferences"

OUTPUT_DIR.mkdir(exist_ok=True)

print("\n" + "=" * 80)
print("  TEST D'INFÉRENCE RAPIDE")
print("=" * 80)

# Charger le modèle
print(f"\n📥 Chargement du modèle...")
model = YOLO(str(MODEL_PATH))
print(f"✅ Modèle chargé")

# Trouver une image de test
test_images = list(TEST_DIR.glob("*.jpg"))
if not test_images:
    print(f"❌ Aucune image de test trouvée dans {TEST_DIR}")
    exit(1)

test_image = test_images[0]
print(f"\n🖼️  Image test: {test_image.name}")

# Faire une inférence
print(f"\n🔮 Inférence en cours...")
results = model.predict(source=str(test_image), conf=0.5, verbose=False)

if results:
    result = results[0]
    print(f"✅ Inférence terminée")
    
    # Afficher les résultats
    print(f"\n📊 Résultats:")
    print(f"   - Boxes détectées: {len(result.boxes)}")
    print(f"   - Masks détectés: {len(result.masks) if result.masks is not None else 0}")
    
    # Sauvegarder les résultats
    output_file = OUTPUT_DIR / f"test_inference_{test_image.stem}.json"
    results_data = {
        "image": test_image.name,
        "boxes_count": len(result.boxes),
        "masks_count": len(result.masks) if result.masks is not None else 0,
    }
    
    with open(output_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n✅ Résultats sauvegardés: {output_file}")
    print(f"\n" + "=" * 80)
    print(f"  ✅ TEST D'INFÉRENCE RÉUSSI!")
    print(f"=" * 80 + "\n")
else:
    print(f"❌ Pas de résultats")
    exit(1)
