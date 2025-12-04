"""
Test rapidement le modèle existant avec une image
"""

import os
from pathlib import Path

# Vérifier si le modèle existe
model_path = "models/yolov8n-seg_trained.pt"

print(f"Modèle existe: {os.path.exists(model_path)}")

if os.path.exists(model_path):
    print(f"Taille: {os.path.getsize(model_path) / (1024*1024):.1f} MB")
    print("✓ Prêt à l'utilisation")
else:
    print("✗ Le modèle n'existe pas encore - l'entraînement est probablement en cours")
    print("Attendez que retrain_model.py se termine")
