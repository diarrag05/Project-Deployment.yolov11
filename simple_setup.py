#!/usr/bin/env python
"""
🚀 SIMPLE SETUP & LAUNCH SCRIPT
Étape 1 pour démarrer le projet
"""

import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent

def main():
    print("=" * 80)
    print("🚀 YOLOv11 SEGMENTATION - SETUP")
    print("=" * 80)
    
    # Vérification Python
    print(f"\n✓ Python version: {sys.version.split()[0]}")
    
    # Installation des packages
    print("\n📦 Installation des dépendances...")
    print("   Cela peut prendre quelques minutes...\n")
    
    packages = [
        "ultralytics",
        "torch",
        "torchvision",
        "opencv-python",
        "numpy",
        "pandas",
        "matplotlib",
        "tensorboard",
    ]
    
    failed = []
    for pkg in packages:
        try:
            print(f"   Installant {pkg}...", end=" ", flush=True)
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", pkg],
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL
            )
            print("✓")
        except:
            print("⚠ (peut être déjà installé)")
            failed.append(pkg)
    
    # Vérification imports
    print("\n✓ Vérification des imports...")
    try:
        import torch
        print(f"   ✓ PyTorch {torch.__version__}")
        if torch.cuda.is_available():
            print(f"   ✓ GPU disponible: {torch.cuda.get_device_name(0)}")
        else:
            print("   ℹ GPU non disponible (utilisera CPU)")
    except:
        print("   ⚠ PyTorch non disponible")
    
    try:
        from ultralytics import YOLO
        print("   ✓ YOLOv11 (Ultralytics)")
    except:
        print("   ✗ YOLOv11 non disponible - installez: pip install ultralytics")
    
    # Création des répertoires
    print("\n📁 Création des répertoires...")
    dirs = [
        PROJECT_DIR / "models",
        PROJECT_DIR / "runs",
        PROJECT_DIR / "evaluations",
        PROJECT_DIR / "inferences",
        PROJECT_DIR / "void_rate_results",
        PROJECT_DIR / "logs",
    ]
    
    for d in dirs:
        d.mkdir(exist_ok=True)
        print(f"   ✓ {d.name}/")
    
    # Vérification dataset
    print("\n📊 Vérification du dataset...")
    for split in ["train", "valid", "test"]:
        images_dir = PROJECT_DIR / split / "images"
        if images_dir.exists():
            count = len(list(images_dir.glob("*")))
            print(f"   ✓ {split}: {count} images")
        else:
            print(f"   ⚠ {split}: répertoire non trouvé")
    
    print("\n" + "=" * 80)
    print("✅ SETUP TERMINÉ!")
    print("=" * 80)
    print("\n📚 Prochaines étapes:")
    print("   1. Entraînement simple:")
    print("      python train.py")
    print("\n   2. Ou utiliser le pipeline automatique:")
    print("      python pipeline.py --config BALANCED")
    print("\n   3. Ou utiliser le notebook:")
    print("      jupyter notebook Training_Pipeline.ipynb")
    print("\n💡 Pour plus d'aide: python QUICKSTART.py")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
