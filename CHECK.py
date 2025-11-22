#!/usr/bin/env python
"""
✅ SCRIPT DE VÉRIFICATION RAPIDE
Utilise-le à chaque fois que tu veux vérifier le projet
"""

from pathlib import Path
import json
from datetime import datetime

PROJECT_DIR = Path(__file__).parent

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def check_model():
    """Vérifier le modèle"""
    print_header("🤖 MODÈLE")
    
    model_path = PROJECT_DIR / "models" / "yolov8n-seg_trained.pt"
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024*1024)
        print(f"  ✅ Modèle entraîné: {model_path.name}")
        print(f"     Taille: {size_mb:.1f} MB")
        print(f"     Classes: chip (0), hole (1)")
        return True
    else:
        print(f"  ❌ Modèle non trouvé: {model_path}")
        return False

def check_dataset():
    """Vérifier le dataset"""
    print_header("📦 DATASET")
    
    train_count = len(list((PROJECT_DIR / "train" / "images").glob("*.jpg"))) if (PROJECT_DIR / "train" / "images").exists() else 0
    valid_count = len(list((PROJECT_DIR / "valid" / "images").glob("*.jpg"))) if (PROJECT_DIR / "valid" / "images").exists() else 0
    test_count = len(list((PROJECT_DIR / "test" / "images").glob("*.jpg"))) if (PROJECT_DIR / "test" / "images").exists() else 0
    
    print(f"  ✅ Train: {train_count} images")
    print(f"  ✅ Valid: {valid_count} images")
    print(f"  ✅ Test: {test_count} images")
    print(f"  ✅ Total: {train_count + valid_count + test_count} images")
    
    return train_count > 0

def check_training_results():
    """Vérifier les résultats d'entraînement"""
    print_header("📊 RÉSULTATS D'ENTRAÎNEMENT")
    
    results_file = PROJECT_DIR / "runs" / "segment" / "train2" / "results.csv"
    if results_file.exists():
        with open(results_file) as f:
            lines = f.readlines()
            epochs = len(lines) - 1
            print(f"  ✅ Epochs entraînés: {epochs}")
            
            # Lire la dernière ligne
            if len(lines) > 1:
                last_line = lines[-1].strip().split(',')
                print(f"  ✅ Résultats CSV disponibles")
                print(f"     Fichier: {results_file}")
        return True
    else:
        print(f"  ⏳ Pas encore d'entraînement")
        return False

def check_inference():
    """Vérifier les inférences"""
    print_header("🔮 INFÉRENCES")
    
    inferences_dir = PROJECT_DIR / "inferences"
    if inferences_dir.exists():
        results = list(inferences_dir.glob("*.json"))
        if results:
            print(f"  ✅ {len(results)} résultats d'inférence")
            latest = max(results, key=lambda p: p.stat().st_mtime)
            print(f"     Dernière: {latest.name}")
            return True
    
    print(f"  ⏳ Pas d'inférence encore")
    return False

def check_void_rate():
    """Vérifier les taux de vides"""
    print_header("📐 TAUX DE VIDES")
    
    void_dir = PROJECT_DIR / "void_rate_results"
    if void_dir.exists():
        results = list(void_dir.glob("*.json"))
        if results:
            print(f"  ✅ {len(results)} résultats de taux de vides")
            # Lire le dernier résultat
            latest = max(results, key=lambda p: p.stat().st_mtime)
            try:
                with open(latest) as f:
                    data = json.load(f)
                    if "average_void_rate" in data:
                        avg = data["average_void_rate"]
                        print(f"     Taux moyen: {avg:.2f}%")
            except:
                pass
            return True
    
    print(f"  ⏳ Pas de calcul de taux de vides encore")
    return False

def show_next_steps():
    """Afficher les prochaines étapes"""
    print_header("📌 PROCHAINES ÉTAPES")
    
    print(f"\n  Pour exécuter une inférence:")
    print(f"  $ python inference.py")
    
    print(f"\n  Pour calculer les taux de vides:")
    print(f"  $ python void_rate_calculator.py")
    
    print(f"\n  Pour évaluer le modèle:")
    print(f"  $ python evaluate.py")
    
    print(f"\n  Pour entraîner de nouveau:")
    print(f"  $ python fast_train.py")
    
    print(f"\n  Pour voir TensorBoard:")
    print(f"  $ tensorboard --logdir runs/segment/train2")
    print(f"  Puis ouvre: http://localhost:6006/")

def show_commands():
    """Afficher les commandes rapides"""
    print_header("⚡ COMMANDES RAPIDES")
    
    print(f"\n  Vérifier le projet:")
    print(f"  $ python verify_all_steps.py")
    
    print(f"\n  Vérifier rapidement (ce script):")
    print(f"  $ python CHECK.py")
    
    print(f"\n  Lancer tout le pipeline:")
    print(f"  $ python pipeline.py")
    
    print(f"\n  Guide interactif:")
    print(f"  $ python GET_STARTED.py")

def main():
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + "  ✅ VÉRIFICATION RAPIDE DU PROJET".center(78) + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Vérifications
    model_ok = check_model()
    dataset_ok = check_dataset()
    training_ok = check_training_results()
    inference_ok = check_inference()
    void_rate_ok = check_void_rate()
    
    # Résumé
    print_header("📋 RÉSUMÉ")
    
    print(f"\n  ✅ Modèle entraîné: {'OUI' if model_ok else 'NON'}")
    print(f"  ✅ Dataset disponible: {'OUI' if dataset_ok else 'NON'}")
    print(f"  ✅ Entraînement fait: {'OUI' if training_ok else 'NON'}")
    print(f"  ✅ Inférence faite: {'OUI' if inference_ok else 'NON'}")
    print(f"  ✅ Taux de vides calculé: {'OUI' if void_rate_ok else 'NON'}")
    
    show_commands()
    show_next_steps()
    
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    main()
