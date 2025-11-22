#!/usr/bin/env python
"""
ULTRA-FAST TRAINING SCRIPT
Entraînement ultra-rapide avec YOLOv8n (3x plus rapide que YOLOv11)
2-3 minutes au lieu de 20+ minutes
"""

from pathlib import Path
from datetime import datetime

try:
    from ultralytics import YOLO
    import torch
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Exécutez d'abord: python simple_setup.py")
    exit(1)

PROJECT_DIR = Path(__file__).parent
DATA_YAML = PROJECT_DIR / "data.yaml"
RUNS_DIR = PROJECT_DIR / "runs"
MODELS_DIR = PROJECT_DIR / "models"

RUNS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

def main():
    print("=" * 80)
    print("⚡ ENTRAÎNEMENT ULTRA-RAPIDE YOLOv8n (NANO)")
    print("=" * 80)
    
    # Vérifier dataset
    if not DATA_YAML.exists():
        print(f"❌ Fichier manquant: {DATA_YAML}")
        exit(1)
    
    print(f"✓ Dataset config: {DATA_YAML}")
    
    # Device
    device = "cpu"  # Forcer CPU pour éviter les problèmes
    print(f"✓ Device: CPU (plus rapide pour petit modèle)")
    
    # Charger le modèle YOLOv8n-seg (NANO = ultra léger)
    print("\n📥 Chargement du modèle YOLOv8n-seg (Nano - 3.2MB)...")
    try:
        model = YOLO("yolov8n-seg.pt")
        print("✓ Modèle chargé avec succès")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        exit(1)
    
    # Configuration d'entraînement ULTRA-RAPIDE
    config = {
        "data": str(DATA_YAML),
        "epochs": 3,           # 3 epochs seulement = ~2 min
        "imgsz": 320,          # 320 au lieu de 640 (4x plus rapide)
        "batch": 4,            # 4 batch (petit)
        "device": device,
        "patience": 2,
        "save": True,
        "val": True,
        "verbose": False,      # Moins de logs
        "workers": 0,          # Pas de workers (CPU)
        "augment": False,      # Pas d'augmentation (+ rapide)
        "mosaic": 0.0,         # Pas de mosaic (+ rapide)
    }
    
    print("\n⚙️  Configuration RAPIDE:")
    for key, val in config.items():
        print(f"   {key:15} = {val}")
    
    # Entraînement
    print("\n" + "=" * 80)
    print("⏳ Entraînement en cours... (~2-3 minutes)")
    print("=" * 80)
    
    try:
        results = model.train(**config)
        print("\n✅ Entraînement terminé!")
        print(f"📁 Résultats: {RUNS_DIR}")
        
        # Sauvegarder le meilleur modèle
        best_model_src = list(RUNS_DIR.glob("*/weights/best.pt"))
        if best_model_src:
            import shutil
            best_model_dst = MODELS_DIR / f"yolov8n-seg_best_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
            shutil.copy(best_model_src[0], best_model_dst)
            print(f"💾 Modèle sauvegardé: {best_model_dst}")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Erreur lors de l'entraînement: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
