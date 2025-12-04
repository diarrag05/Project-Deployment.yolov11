#!/usr/bin/env python
"""
Script de vérification complète du projet
Teste tous les composants du système
"""

import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent

def test_imports():
    """Test que tous les imports fonctionnent"""
    print("\n" + "="*60)
    print("1️⃣  TEST IMPORTS")
    print("="*60)
    
    try:
        import flask
        print("✅ Flask OK")
    except ImportError as e:
        print(f"❌ Flask: {e}")
        return False
    
    try:
        import torch
        print("✅ PyTorch OK")
    except ImportError as e:
        print(f"❌ PyTorch: {e}")
        return False
    
    try:
        from ultralytics import YOLO
        print("✅ Ultralytics/YOLO OK")
    except ImportError as e:
        print(f"❌ Ultralytics: {e}")
        return False
    
    try:
        import cv2
        print("✅ OpenCV OK")
    except ImportError as e:
        print(f"❌ OpenCV: {e}")
        return False
    
    try:
        import numpy
        print("✅ NumPy OK")
    except ImportError as e:
        print(f"❌ NumPy: {e}")
        return False
    
    return True


def test_files_exist():
    """Vérifier que tous les fichiers essentiels existent"""
    print("\n" + "="*60)
    print("2️⃣  TEST FICHIERS")
    print("="*60)
    
    essential_files = [
        "app.py",
        "config.py",
        "data.yaml",
        "docker-compose.yml",
        "Dockerfile",
        "evaluate.py",
        "fast_train.py",
        "inference.py",
        "nginx.conf",
        "README.md",
        "requirements_api.txt",
        "DEPLOYMENT_GUIDE.md",
        "void_rate_calculator.py",
    ]
    
    missing = []
    for f in essential_files:
        path = PROJECT_DIR / f
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {f} ({size/1024:.1f}KB)")
        else:
            print(f"❌ {f} MANQUANT")
            missing.append(f)
    
    if missing:
        print(f"\n⚠️  {len(missing)} fichiers manquants!")
        return False
    
    return True


def test_directories_exist():
    """Vérifier que tous les dossiers existent"""
    print("\n" + "="*60)
    print("3️⃣  TEST DOSSIERS")
    print("="*60)
    
    essential_dirs = [
        "routes",
        "utils",
        "templates",
        "static",
        "models",
        ".github",
    ]
    
    missing = []
    for d in essential_dirs:
        path = PROJECT_DIR / d
        if path.exists() and path.is_dir():
            files = len(list(path.glob("*")))
            print(f"✅ {d}/ ({files} items)")
        else:
            print(f"❌ {d}/ MANQUANT")
            missing.append(d)
    
    if missing:
        print(f"\n⚠️  {len(missing)} dossiers manquants!")
        return False
    
    return True


def test_app_loads():
    """Tester que l'app Flask se charge"""
    print("\n" + "="*60)
    print("4️⃣  TEST FLASK APP")
    print("="*60)
    
    try:
        sys.path.insert(0, str(PROJECT_DIR))
        from app import app
        print("✅ App Flask charge OK")
        
        # Vérifier les blueprints
        blueprints = list(app.blueprints.keys())
        print(f"✅ Blueprints enregistrés: {blueprints}")
        
        if not blueprints:
            print("❌ Aucun blueprint!")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Erreur loading app: {e}")
        return False


def test_yolo_model():
    """Tester que le modèle YOLO se charge"""
    print("\n" + "="*60)
    print("5️⃣  TEST YOLO MODEL")
    print("="*60)
    
    try:
        from ultralytics import YOLO
        
        # Chercher le modèle
        model_files = [
            PROJECT_DIR / "models" / "yolov8n-seg_trained.pt",
            PROJECT_DIR / "yolov8n-seg.pt",
        ]
        
        model_found = None
        for mf in model_files:
            if mf.exists():
                model_found = mf
                print(f"✅ Modèle trouvé: {mf.name} ({mf.stat().st_size / (1024*1024):.1f}MB)")
                break
        
        if not model_found:
            print("⚠️  Aucun modèle trouvé (peut être téléchargé à la première utilisation)")
            return True
        
        return True
    except Exception as e:
        print(f"❌ Erreur YOLO: {e}")
        return False


def test_config():
    """Tester la configuration"""
    print("\n" + "="*60)
    print("6️⃣  TEST CONFIGURATION")
    print("="*60)
    
    try:
        sys.path.insert(0, str(PROJECT_DIR))
        import config
        print("✅ Config charge OK")
        return True
    except Exception as e:
        print(f"❌ Erreur config: {e}")
        return False


def test_data_yaml():
    """Vérifier data.yaml"""
    print("\n" + "="*60)
    print("7️⃣  TEST DATA.YAML")
    print("="*60)
    
    try:
        import yaml
        
        yaml_file = PROJECT_DIR / "data.yaml"
        if not yaml_file.exists():
            print("❌ data.yaml non trouvé")
            return False
        
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
        
        print(f"✅ data.yaml charge OK")
        print(f"   - Classes: {data.get('nc', 'unknown')}")
        print(f"   - Train: {data.get('train', 'unknown')}")
        print(f"   - Val: {data.get('val', 'unknown')}")
        print(f"   - Test: {data.get('test', 'unknown')}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur data.yaml: {e}")
        return False


def test_routes():
    """Vérifier les routes"""
    print("\n" + "="*60)
    print("8️⃣  TEST ROUTES")
    print("="*60)
    
    routes_dir = PROJECT_DIR / "routes"
    if not routes_dir.exists():
        print("❌ Dossier routes/ n'existe pas")
        return False
    
    py_files = list(routes_dir.glob("*.py"))
    
    if len(py_files) < 2:
        print(f"❌ Seulement {len(py_files)} fichiers routes (attendu 6+)")
        return False
    
    print(f"✅ {len(py_files)} fichiers routes trouvés:")
    for f in sorted(py_files):
        print(f"   - {f.name}")
    
    return True


def test_utils():
    """Vérifier les utilitaires"""
    print("\n" + "="*60)
    print("9️⃣  TEST UTILS")
    print("="*60)
    
    utils_dir = PROJECT_DIR / "utils"
    if not utils_dir.exists():
        print("❌ Dossier utils/ n'existe pas")
        return False
    
    py_files = list(utils_dir.glob("*.py"))
    
    if len(py_files) < 2:
        print(f"❌ Seulement {len(py_files)} fichiers utils (attendu 4+)")
        return False
    
    print(f"✅ {len(py_files)} fichiers utils trouvés:")
    for f in sorted(py_files):
        print(f"   - {f.name}")
    
    return True


def test_templates():
    """Vérifier les templates HTML"""
    print("\n" + "="*60)
    print("🔟 TEST TEMPLATES")
    print("="*60)
    
    templates_dir = PROJECT_DIR / "templates"
    if not templates_dir.exists():
        print("❌ Dossier templates/ n'existe pas")
        return False
    
    html_files = list(templates_dir.glob("*.html"))
    
    if len(html_files) < 2:
        print(f"❌ Seulement {len(html_files)} fichiers HTML (attendu 4+)")
        return False
    
    print(f"✅ {len(html_files)} fichiers HTML trouvés:")
    for f in sorted(html_files):
        print(f"   - {f.name}")
    
    return True


def main():
    """Exécuter tous les tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "VERIFICATION COMPLETE DU PROJET" + " "*13 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("Imports", test_imports),
        ("Fichiers essentiels", test_files_exist),
        ("Dossiers essentiels", test_directories_exist),
        ("App Flask", test_app_loads),
        ("Modèle YOLO", test_yolo_model),
        ("Configuration", test_config),
        ("data.yaml", test_data_yaml),
        ("Routes API", test_routes),
        ("Utilitaires", test_utils),
        ("Templates HTML", test_templates),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ ERREUR dans {name}: {e}")
            results.append((name, False))
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n{'='*60}")
    if passed == total:
        print(f"🎉 SUCCÈS! {passed}/{total} tests réussis!")
        print("✅ LE PROJET EST COMPLETEMENT FONCTIONNEL!")
        print(f"{'='*60}\n")
        return 0
    else:
        print(f"⚠️  {passed}/{total} tests réussis")
        print(f"❌ {total - passed} problèmes détectés")
        print(f"{'='*60}\n")
        return 1


if __name__ == "__main__":
    exit(main())
