"""
Script d'entraînement YOLOv11-segmentation avec tuning des hyperparamètres
et monitoring tensorboard
"""

import os
import sys
from pathlib import Path
from ultralytics import YOLO
import torch
import yaml
from datetime import datetime

# Configuration
PROJECT_DIR = Path(__file__).parent
DATA_YAML = PROJECT_DIR / "data.yaml"
RUNS_DIR = PROJECT_DIR / "runs"
MODELS_DIR = PROJECT_DIR / "models"

# Créer les répertoires
RUNS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

def get_device():
    """Déterminer le device (GPU ou CPU)"""
    if torch.cuda.is_available():
        device = 0  # GPU par défaut
        print(f"✓ GPU détecté: {torch.cuda.get_device_name(device)}")
    else:
        device = "cpu"
        print("⚠ GPU non détecté, utilisation du CPU")
    return device

def train_yolov11_segmentation(
    model_size: str = "m",  # n, s, m, l, x
    epochs: int = 100,
    batch_size: int = 16,
    img_size: int = 640,
    patience: int = 20,
    learning_rate: float = 0.001,
    lr_scheduler: str = "cosine",
    weight_decay: float = 0.0005,
    mosaic: float = 1.0,
    hsv_h: float = 0.015,
    hsv_s: float = 0.7,
    hsv_v: float = 0.4,
    degrees: float = 10.0,
    translate: float = 0.1,
    scale: float = 0.5,
    flipud: float = 0.5,
    fliplr: float = 0.5,
    perspective: float = 0.0,
):
    """
    Entraîner YOLOv11-segmentation avec hyperparamètres optimisés
    
    Args:
        model_size: Taille du modèle (n, s, m, l, x)
        epochs: Nombre d'epochs
        batch_size: Taille du batch
        img_size: Taille des images
        patience: Early stopping patience
        learning_rate: Taux d'apprentissage initial
        lr_scheduler: Type de scheduler (linear, cosine, poly, constant)
        weight_decay: Coefficient de régularisation L2
        mosaic: Augmentation de données Mosaic (0-1)
        hsv_h, hsv_s, hsv_v: Augmentation HSV
        degrees: Rotation augmentation
        translate: Translation augmentation
        scale: Scale augmentation
        flipud, fliplr: Flip augmentation
        perspective: Perspective augmentation
    """
    
    print("=" * 80)
    print("🚀 ENTRAÎNEMENT YOLOv11-SEGMENTATION")
    print("=" * 80)
    
    # Vérifier le device
    device = get_device()
    
    # Charger le modèle YOLOv11-segmentation pré-entraîné
    print(f"\n📥 Chargement du modèle YOLOv11{model_size}-seg...")
    model = YOLO(f"yolov11{model_size}-seg.pt")
    
    # Créer un nom de run unique
    run_name = f"yolov11{model_size}-seg_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir = RUNS_DIR / run_name
    
    # Afficher la configuration
    print("\n" + "=" * 80)
    print("📋 CONFIGURATION D'ENTRAÎNEMENT")
    print("=" * 80)
    print(f"Model: YOLOv11{model_size}-seg")
    print(f"Device: {device}")
    print(f"Epochs: {epochs}")
    print(f"Batch Size: {batch_size}")
    print(f"Image Size: {img_size}")
    print(f"Learning Rate: {learning_rate}")
    print(f"LR Scheduler: {lr_scheduler}")
    print(f"Weight Decay: {weight_decay}")
    print(f"Patience (Early Stopping): {patience}")
    print(f"Run Directory: {run_dir}")
    print("=" * 80)
    
    # Entraîner le modèle avec hyperparamètres optimisés
    print("\n⏳ Début de l'entraînement...")
    results = model.train(
        data=str(DATA_YAML),
        epochs=epochs,
        imgsz=img_size,
        batch=batch_size,
        patience=patience,
        device=device,
        
        # Learning rate
        lr0=learning_rate,
        lrf=0.001,  # Final learning rate
        
        # Scheduler
        scheduler=lr_scheduler,
        
        # Régularisation
        weight_decay=weight_decay,
        dropout=0.0,
        
        # Augmentation de données
        mosaic=mosaic,
        hsv_h=hsv_h,
        hsv_s=hsv_s,
        hsv_v=hsv_v,
        degrees=degrees,
        translate=translate,
        scale=scale,
        flipud=flipud,
        fliplr=fliplr,
        perspective=perspective,
        
        # Autres paramètres
        name=run_name,
        project=str(RUNS_DIR),
        exist_ok=False,
        pretrained=True,
        optimizer="SGD",  # ou "Adam"
        close_mosaic=10,  # Désactiver Mosaic les 10 derniers epochs
        warmup_epochs=3,
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,
        
        # Validation
        val=True,
        save=True,
        save_period=10,  # Sauvegarder tous les 10 epochs
        
        # Monitoring
        verbose=True,
        plots=True,
        
        # Half precision (si disponible)
        half=torch.cuda.is_available(),
        
        # Augmentation avancée
        copy_paste=0.0,
        fraction=1.0,
    )
    
    print("\n" + "=" * 80)
    print("✅ ENTRAÎNEMENT TERMINÉ")
    print("=" * 80)
    print(f"Résultats sauvegardés dans: {run_dir}")
    
    # Sauvegarder le meilleur modèle
    best_model_path = run_dir / "weights" / "best.pt"
    final_model_path = MODELS_DIR / f"yolov11{model_size}-seg_best_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
    
    if best_model_path.exists():
        # Copier le meilleur modèle vers le dossier models
        import shutil
        shutil.copy(best_model_path, final_model_path)
        print(f"\n💾 Meilleur modèle sauvegardé: {final_model_path}")
    
    return model, results, run_dir

def launch_tensorboard(run_dir):
    """Lancer TensorBoard pour monitorer l'entraînement"""
    try:
        import subprocess
        print(f"\n📊 Lancement de TensorBoard...")
        print(f"Exécutez: tensorboard --logdir {run_dir}")
        # Décommenter pour lancer automatiquement
        # subprocess.Popen(["tensorboard", "--logdir", str(run_dir)])
    except Exception as e:
        print(f"⚠ Erreur lors du lancement de TensorBoard: {e}")

def print_metrics(results):
    """Afficher les métriques principales"""
    print("\n" + "=" * 80)
    print("📊 MÉTRIQUES D'ENTRAÎNEMENT")
    print("=" * 80)
    if hasattr(results, 'box') and hasattr(results, 'mask'):
        print(f"mAP50 (Box): {results.box.map50:.4f}")
        print(f"mAP50-95 (Box): {results.box.map:.4f}")
        print(f"mAP50 (Mask): {results.mask.map50:.4f}")
        print(f"mAP50-95 (Mask): {results.mask.map:.4f}")
    print("=" * 80)

if __name__ == "__main__":
    # Configuration par défaut (peut être modifiée)
    CONFIG = {
        "model_size": "m",        # Taille du modèle
        "epochs": 100,            # Nombre d'epochs
        "batch_size": 16,         # Taille du batch (adapter selon GPU)
        "img_size": 640,          # Taille des images
        "patience": 20,           # Early stopping
        "learning_rate": 0.001,   # Taux d'apprentissage
        "lr_scheduler": "cosine", # Scheduler
        "weight_decay": 0.0005,   # Régularisation
    }
    
    try:
        # Entraîner le modèle
        model, results, run_dir = train_yolov11_segmentation(**CONFIG)
        
        # Afficher les métriques
        print_metrics(results)
        
        # Lancer TensorBoard
        launch_tensorboard(run_dir)
        
        print("\n✨ Entraînement réussi!")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'entraînement: {e}")
        sys.exit(1)
