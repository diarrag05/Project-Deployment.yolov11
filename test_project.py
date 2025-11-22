#!/usr/bin/env python
"""
TEST SCRIPT - Vérifie que tout fonctionne
"""

from pathlib import Path
import sys

PROJECT_DIR = Path(__file__).parent

def test_imports():
    """Tester les imports critiques"""
    print("🧪 TEST DES IMPORTS")
    print("=" * 60)
    
    tests = {
        "torch": "import torch",
        "numpy": "import numpy",
        "cv2": "import cv2",
        "ultralytics": "from ultralytics import YOLO",
        "pandas": "import pandas",
    }
    
    all_ok = True
    for name, code in tests.items():
        try:
            exec(code)
            print(f"✓ {name:20} OK")
        except ImportError as e:
            print(f"✗ {name:20} MANQUANT")
            all_ok = False
    
    return all_ok

def test_files():
    """Tester que les fichiers existent"""
    print("\n🧪 TEST DES FICHIERS")
    print("=" * 60)
    
    files = [
        "data.yaml",
        "train.py",
        "evaluate.py",
        "inference.py",
        "void_rate_calculator.py",
        "config.py",
        "pipeline.py",
        "requirements.txt",
    ]
    
    all_ok = True
    for filename in files:
        filepath = PROJECT_DIR / filename
        if filepath.exists():
            print(f"✓ {filename:30} OK")
        else:
            print(f"✗ {filename:30} MANQUANT")
            all_ok = False
    
    return all_ok

def test_dataset():
    """Tester que le dataset existe"""
    print("\n🧪 TEST DU DATASET")
    print("=" * 60)
    
    all_ok = True
    for split in ["train", "valid", "test"]:
        images_dir = PROJECT_DIR / split / "images"
        labels_dir = PROJECT_DIR / split / "labels"
        
        images_ok = images_dir.exists() and len(list(images_dir.glob("*"))) > 0
        labels_ok = labels_dir.exists() and len(list(labels_dir.glob("*"))) > 0
        
        status = "✓" if (images_ok and labels_ok) else "✗"
        print(f"{status} {split:15} images={images_ok}, labels={labels_ok}")
        
        if not (images_ok and labels_ok):
            all_ok = False
    
    return all_ok

def main():
    print("\n" + "=" * 60)
    print("🧪 TEST COMPLET DU PROJET")
    print("=" * 60 + "\n")
    
    test1 = test_imports()
    test2 = test_files()
    test3 = test_dataset()
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    
    if test1 and test2 and test3:
        print("✅ TOUS LES TESTS PASSED!")
        print("\n🚀 Vous pouvez maintenant:")
        print("   1. python simple_setup.py")
        print("   2. python simple_train.py")
        return 0
    else:
        print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("\n💡 Solutions:")
        if not test1:
            print("   • Installer les dépendances: python simple_setup.py")
        if not test2:
            print("   • Vérifier les fichiers du projet")
        if not test3:
            print("   • Vérifier que le dataset existe (train/, valid/, test/)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
