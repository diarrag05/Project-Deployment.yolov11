#!/usr/bin/env python
"""
GUIDE DE TEST PRATIQUE - YOLOv11 Segmentation Platform
Exécute des tests réels avec des images de test
"""

import os
import sys
import json
from pathlib import Path
import requests
import time
from datetime import datetime

PROJECT_DIR = Path(__file__).parent
API_URL = "http://localhost:5000"

def print_header(title):
    """Afficher un header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_api_health():
    """Test que l'API répond"""
    print_header("TEST 1: Vérifier que l'API répond")
    
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            print("✅ API RÉPOND - Code 200")
            print(f"   Content-Type: {response.headers.get('Content-Type')}")
            return True
        else:
            print(f"❌ API répond avec code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ ERREUR: Impossible de se connecter à l'API")
        print(f"   Assure-toi que l'app Flask tourne sur {API_URL}")
        print("   Lance: py app.py")
        return False
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False


def test_pages_web():
    """Test que les pages web chargent"""
    print_header("TEST 2: Vérifier que les pages web chargent")
    
    pages = [
        ("/", "Home"),
        ("/analysis", "Analysis"),
        ("/dashboard", "Dashboard"),
        ("/feedback", "Feedback"),
    ]
    
    all_ok = True
    for page, name in pages:
        try:
            response = requests.get(f"{API_URL}{page}")
            if response.status_code == 200:
                print(f"✅ {name:15} {page:20} - {len(response.text)} bytes")
            else:
                print(f"❌ {name:15} {page:20} - Code {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"❌ {name:15} {page:20} - ERREUR: {e}")
            all_ok = False
    
    return all_ok


def find_test_image():
    """Trouver une image de test"""
    test_dirs = [
        PROJECT_DIR / "test" / "images",
        PROJECT_DIR / "test/images",
    ]
    
    for test_dir in test_dirs:
        if test_dir.exists():
            images = list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png"))
            if images:
                return images[0]
    
    return None


def test_inference():
    """Test d'inférence (prédiction)"""
    print_header("TEST 3: Test d'inférence (prédiction)")
    
    image_path = find_test_image()
    
    if not image_path:
        print("⚠️  Aucune image de test trouvée dans test/images/")
        print("   Place une image JPG ou PNG dans test/images/")
        return False
    
    print(f"Image trouvée: {image_path.name}")
    print(f"Taille: {image_path.stat().st_size / 1024:.1f}KB")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {'confidence': 0.5}
            
            print("\nEnvoi de l'image à l'API...")
            start_time = time.time()
            response = requests.post(f"{API_URL}/api/predict", files=files, data=data)
            elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prédiction réussie ({elapsed:.2f}s)")
            
            if 'results' in result:
                res = result['results']
                print(f"\n   📊 Résultats:")
                print(f"   - Chip Area: {res.get('chip_area', 0):,} pixels")
                print(f"   - Holes Area: {res.get('holes_area', 0):,} pixels")
                print(f"   - Void Rate: {res.get('void_rate', 0):.2f}%")
                print(f"   - Chip %: {res.get('chip_percentage', 0):.1f}%")
                print(f"   - Holes %: {res.get('holes_percentage', 0):.1f}%")
                print(f"   - Confiance: {res.get('confidence', 0):.2f}")
            
            return True
        else:
            print(f"❌ Erreur API: Code {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False


def test_report_summary():
    """Test du résumé des rapports"""
    print_header("TEST 4: Test du résumé des rapports")
    
    try:
        response = requests.get(f"{API_URL}/api/report/summary")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Résumé récupéré")
            
            if 'summary' in data:
                summary = data['summary']
                print(f"\n   📈 Statistiques globales:")
                print(f"   - Total images: {summary.get('total_images', 0)}")
                print(f"   - Void rate moyen: {summary.get('avg_void_rate', 0):.2f}%")
                print(f"   - Min void rate: {summary.get('min_void_rate', 0):.2f}%")
                print(f"   - Max void rate: {summary.get('max_void_rate', 0):.2f}%")
            
            return True
        else:
            print(f"❌ Erreur: Code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False


def test_feedback_endpoints():
    """Test des endpoints de feedback"""
    print_header("TEST 5: Test des endpoints de feedback")
    
    endpoints = [
        ("GET", "/api/feedback", "Récupérer stats"),
        ("GET", "/api/feedback/pending", "Corrections en attente"),
        ("GET", "/api/feedback/incorrect", "Prédictions incorrectes"),
    ]
    
    all_ok = True
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{API_URL}{endpoint}")
            else:
                response = requests.post(f"{API_URL}{endpoint}")
            
            if response.status_code == 200:
                print(f"✅ {endpoint:30} - {description}")
            else:
                print(f"⚠️  {endpoint:30} - Code {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"❌ {endpoint:30} - ERREUR: {e}")
            all_ok = False
    
    return all_ok


def test_training_status():
    """Test du statut d'entraînement"""
    print_header("TEST 6: Test du statut d'entraînement")
    
    try:
        response = requests.get(f"{API_URL}/api/train/status")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Statut d'entraînement récupéré")
            print(f"   Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"⚠️  Code {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  ERREUR: {e}")
        return False


def test_model_info():
    """Test des infos du modèle"""
    print_header("TEST 7: Test des infos du modèle")
    
    try:
        # Essayer de charger le modèle
        from ultralytics import YOLO
        
        model_path = PROJECT_DIR / "models" / "yolov8n-seg_trained.pt"
        if model_path.exists():
            print(f"✅ Modèle trouvé: {model_path.name}")
            print(f"   Taille: {model_path.stat().st_size / (1024*1024):.1f}MB")
            
            model = YOLO(str(model_path))
            print(f"✅ Modèle chargé avec succès")
            print(f"   Task: segment")
            print(f"   Model: YOLOv8n")
            
            return True
        else:
            print(f"⚠️  Modèle pas trouvé: {model_path}")
            return False
    except Exception as e:
        print(f"⚠️  ERREUR: {e}")
        return False


def test_data_yaml():
    """Test du fichier data.yaml"""
    print_header("TEST 8: Test du fichier data.yaml")
    
    try:
        import yaml
        
        yaml_path = PROJECT_DIR / "data.yaml"
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        
        print(f"✅ data.yaml chargé")
        print(f"   Classes: {data.get('nc', 'unknown')}")
        print(f"   Train: {data.get('train', 'unknown')}")
        print(f"   Val: {data.get('val', 'unknown')}")
        print(f"   Test: {data.get('test', 'unknown')}")
        
        # Vérifier que les images existent
        train_dir = PROJECT_DIR / "train" / "images"
        if train_dir.exists():
            train_images = list(train_dir.glob("*.jpg")) + list(train_dir.glob("*.png"))
            print(f"   ✅ Train images: {len(train_images)} trouvées")
        
        return True
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False


def show_final_summary(results):
    """Afficher un résumé final"""
    print_header("📊 RÉSUMÉ FINAL DES TESTS")
    
    tests_names = [
        "API Health",
        "Pages Web",
        "Inference",
        "Report Summary",
        "Feedback Endpoints",
        "Training Status",
        "Model Info",
        "Data YAML",
    ]
    
    print("Résultats:\n")
    passed = 0
    for i, (name, result) in enumerate(zip(tests_names, results)):
        status = "✅" if result else "❌"
        print(f"  {status} {i+1}. {name}")
        if result:
            passed += 1
    
    total = len(results)
    percentage = (passed / total) * 100 if total > 0 else 0
    
    print(f"\n{'='*70}")
    print(f"  {passed}/{total} tests réussis ({percentage:.0f}%)")
    print(f"{'='*70}\n")
    
    if passed == total:
        print("🎉 SUCCÈS! LE PROJET FONCTIONNE PARFAITEMENT!")
    elif passed >= total * 0.75:
        print("⚠️  Plupart des tests réussis, quelques ajustements peuvent être nécessaires")
    else:
        print("❌ Plusieurs problèmes détectés, vérifie la configuration")


def main():
    """Exécuter tous les tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "GUIDE DE TEST PRATIQUE DU PROJET" + " "*21 + "║")
    print("╚" + "="*68 + "╝")
    
    print("\n⚠️  IMPORTANT:")
    print("   1. Lance l'app Flask dans un autre terminal: py app.py")
    print("   2. Attends que le serveur soit prêt (http://localhost:5000)")
    print("   3. Appuie sur Entrée pour continuer...\n")
    
    input("Appuie sur Entrée pour commencer les tests...")
    
    tests = [
        ("API Health", test_api_health),
        ("Pages Web", test_pages_web),
        ("Inference", test_inference),
        ("Report Summary", test_report_summary),
        ("Feedback Endpoints", test_feedback_endpoints),
        ("Training Status", test_training_status),
        ("Model Info", test_model_info),
        ("Data YAML", test_data_yaml),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ ERREUR non gérée: {e}")
            results.append(False)
    
    show_final_summary(results)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERREUR FATALE: {e}")
        sys.exit(1)
