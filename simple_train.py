#!/usr/bin/env python
"""
SIMPLE TRAINING SCRIPT
Version simplifiée et testable du train.py
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
    print("🚀 ENTRAÎNEMENT YOLOv11-SEGMENTATION (Version simplifiée)")
    print("=" * 80)
    
    # Vérifier dataset
    if not DATA_YAML.exists():
        print(f"❌ Fichier manquant: {DATA_YAML}")
        exit(1)
    
    print(f"✓ Dataset config: {DATA_YAML}")
    
    # Device
    device = 0 if torch.cuda.is_available() else "cpu"
    device_name = torch.cuda.get_device_name(0) if device == 0 else "CPU"
    print(f"✓ Device: {device_name}")
    
    # Charger le modèle de segmentation
    print("\n📥 Chargement du modèle YOLOv11m-seg...")
    try:
        # Essayer YOLOv11m d'abord
        print("   Tentative 1: YOLOv11m...")
        model = YOLO("yolov11m.pt")
    except:
        try:
            # Essayer avec YOLOv8m en fallback (plus stable)
            print("   Tentative 2: YOLOv8m (fallback)...")
            model = YOLO("yolov8m-seg.pt")
        except:
            # Si rien ne fonctionne, créer un modèle vide
            print("   Création d'un modèle depuis zéro...")
            model = YOLO("yolov11m.yaml")  # Créer à partir du YAML
    
    print("✓ Modèle chargé avec succès")
    
    # Configuration d'entraînement simple
    config = {
        "data": str(DATA_YAML),
        "epochs": 10,  # Peu d'epochs pour test
        "imgsz": 640,
        "batch": 16,
        "device": device,
        "patience": 3,
        "save": True,
        "val": True,
        "verbose": True,
    }
    
    print("\n⚙️  Configuration:")
    for key, val in config.items():
        print(f"   {key:15} = {val}")
    
    # Entraînement
    print("\n" + "=" * 80)
    print("⏳ Entraînement en cours...")
    print("=" * 80)
    
    try:
        results = model.train(**config)
        print("\n✅ Entraînement terminé!")
        print(f"📁 Résultats: {RUNS_DIR}")
        
        # Sauvegarder le meilleur modèle
        best_model_src = list(RUNS_DIR.glob("*/weights/best.pt"))
        if best_model_src:
            import shutil
            best_model_dst = MODELS_DIR / f"yolov11m-seg_best_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
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
