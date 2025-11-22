"""
Script d'évaluation du modèle YOLOv11-segmentation
Calcule: mAP, précision, rappel, IoU sur le test set
"""

import os
from pathlib import Path
from ultralytics import YOLO
import torch
import json
from datetime import datetime

PROJECT_DIR = Path(__file__).parent
DATA_YAML = PROJECT_DIR / "data.yaml"
MODELS_DIR = PROJECT_DIR / "models"
EVAL_DIR = PROJECT_DIR / "evaluations"

# Créer le répertoire d'évaluation
EVAL_DIR.mkdir(exist_ok=True)

def evaluate_model(model_path: str, task: str = "segment"):
    """
    Évaluer le modèle YOLOv11
    
    Args:
        model_path: Chemin vers le modèle .pt
        task: Type de tâche (segment pour segmentation)
    
    Returns:
        Résultats d'évaluation
    """
    
    print("=" * 80)
    print("📊 ÉVALUATION DU MODÈLE YOLOv11-SEGMENTATION")
    print("=" * 80)
    
    # Vérifier le device
    device = 0 if torch.cuda.is_available() else "cpu"
    print(f"\nDevice: {device}")
    
    # Charger le modèle
    print(f"\n📥 Chargement du modèle: {model_path}")
    model = YOLO(model_path, task=task)
    
    # Évaluer sur le test set
    print("\n⏳ Évaluation sur le test set...")
    results = model.val(
        data=str(DATA_YAML),
        device=device,
        imgsz=640,
        batch=16,
        half=torch.cuda.is_available(),
        verbose=True,
    )
    
    # Afficher les résultats
    print("\n" + "=" * 80)
    print("📋 RÉSULTATS D'ÉVALUATION")
    print("=" * 80)
    
    metrics_dict = {
        "timestamp": datetime.now().isoformat(),
        "model_path": str(model_path),
        "device": str(device),
    }
    
    # Métriques de segmentation
    if hasattr(results, 'box'):
        print("\n🎯 MÉTRIQUES DE DÉTECTION (Box):")
        print(f"  mAP50: {results.box.map50:.4f}")
        print(f"  mAP50-95: {results.box.map:.4f}")
        print(f"  Précision: {results.box.mp:.4f}")
        print(f"  Rappel: {results.box.mr:.4f}")
        
        metrics_dict['detection'] = {
            'mAP50': float(results.box.map50),
            'mAP50-95': float(results.box.map),
            'precision': float(results.box.mp),
            'recall': float(results.box.mr),
        }
    
    if hasattr(results, 'mask'):
        print("\n🎭 MÉTRIQUES DE SEGMENTATION (Mask):")
        print(f"  mAP50: {results.mask.map50:.4f}")
        print(f"  mAP50-95: {results.mask.map:.4f}")
        print(f"  Précision: {results.mask.mp:.4f}")
        print(f"  Rappel: {results.mask.mr:.4f}")
        
        metrics_dict['segmentation'] = {
            'mAP50': float(results.mask.map50),
            'mAP50-95': float(results.mask.map),
            'precision': float(results.mask.mp),
            'recall': float(results.mask.mr),
        }
    
    # IoU par classe
    if hasattr(results, 'ious'):
        print("\n📐 IoU PAR CLASSE:")
        for i, iou in enumerate(results.ious):
            class_name = results.names[i] if hasattr(results, 'names') else f"Class {i}"
            print(f"  {class_name}: {iou:.4f}")
    
    # Confusion matrix
    if hasattr(results, 'confusion_matrix'):
        print("\n🔢 CONFUSION MATRIX:")
        print(results.confusion_matrix)
    
    print("=" * 80)
    
    # Sauvegarder les résultats en JSON
    results_file = EVAL_DIR / f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(metrics_dict, f, indent=4)
    print(f"\n💾 Résultats sauvegardés: {results_file}")
    
    return results, metrics_dict

def evaluate_all_models():
    """Évaluer tous les modèles disponibles"""
    if not MODELS_DIR.exists():
        print(f"❌ Dossier models n'existe pas: {MODELS_DIR}")
        return
    
    models = list(MODELS_DIR.glob("*.pt"))
    if not models:
        print(f"⚠ Aucun modèle trouvé dans: {MODELS_DIR}")
        return
    
    print(f"\n📋 {len(models)} modèle(s) trouvé(s):")
    for i, model in enumerate(models, 1):
        print(f"  {i}. {model.name}")
    
    # Évaluer chaque modèle
    results_summary = {}
    for model_path in models:
        print(f"\n{'=' * 80}")
        print(f"Évaluation de: {model_path.name}")
        print(f"{'=' * 80}")
        
        try:
            results, metrics = evaluate_model(str(model_path))
            results_summary[model_path.name] = metrics
        except Exception as e:
            print(f"❌ Erreur lors de l'évaluation: {e}")
    
    # Sauvegarder le résumé
    summary_file = EVAL_DIR / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w') as f:
        json.dump(results_summary, f, indent=4)
    print(f"\n💾 Résumé sauvegardé: {summary_file}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Évaluer un modèle spécifique
        model_path = sys.argv[1]
        evaluate_model(model_path)
    else:
        # Évaluer tous les modèles
        evaluate_all_models()
