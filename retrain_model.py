"""
Retrain YOLOv8n Segmentation Model
Utilise les données du dossier train/ et test/
"""

import os
import yaml
from ultralytics import YOLO
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATA_YAML = "data.yaml"
MODEL_NAME = "yolov8n-seg"  # nano model for segmentation
OUTPUT_MODEL = "models/yolov8n-seg_trained.pt"
EPOCHS = 50  # Entraînement rapide
IMGSZ = 320
BATCH_SIZE = 8
DEVICE = 0  # GPU 0 (or 'cpu' si pas de GPU)

def create_data_yaml():
    """Créer le fichier data.yaml s'il n'existe pas"""
    if os.path.exists(DATA_YAML):
        logger.info(f"{DATA_YAML} déjà existe")
        return
    
    data_config = {
        'path': os.getcwd(),
        'train': 'train/images',
        'val': 'test/images',
        'test': 'test/images',
        'nc': 2,  # 2 classes: chip et hole
        'names': {0: 'chip', 1: 'hole'}
    }
    
    with open(DATA_YAML, 'w') as f:
        yaml.dump(data_config, f, default_flow_style=False)
    
    logger.info(f"✓ Créé {DATA_YAML}")

def train_model():
    """Entraîner le modèle YOLOv8n pour la segmentation"""
    logger.info("🚀 Démarrage de l'entraînement...")
    
    # Charger le modèle pré-entraîné
    model = YOLO(f'{MODEL_NAME}.pt')
    
    # Entraîner
    results = model.train(
        data=DATA_YAML,
        epochs=EPOCHS,
        imgsz=IMGSZ,
        batch=BATCH_SIZE,
        device=DEVICE,
        patience=10,  # Early stopping after 10 epochs sans amélioration
        save=True,
        verbose=True,
        project='runs/segment',
        name='yolov8n-seg-train'
    )
    
    logger.info("✓ Entraînement terminé")
    return results

def copy_best_model():
    """Copier le meilleur modèle vers models/"""
    best_model = 'runs/segment/yolov8n-seg-train/weights/best.pt'
    
    if os.path.exists(best_model):
        os.makedirs('models', exist_ok=True)
        import shutil
        shutil.copy(best_model, OUTPUT_MODEL)
        logger.info(f"✓ Modèle copié vers {OUTPUT_MODEL}")
    else:
        logger.warning(f"Fichier {best_model} non trouvé")

def test_model():
    """Tester le modèle entraîné"""
    logger.info("🧪 Test du modèle...")
    
    model = YOLO(OUTPUT_MODEL)
    
    # Tester sur une image
    test_images = list(Path('test/images').glob('*.jpg'))[:1]
    
    if test_images:
        results = model.predict(
            source=str(test_images[0]),
            conf=0.5,
            verbose=False
        )
        
        if results and len(results) > 0:
            result = results[0]
            if hasattr(result, 'boxes') and len(result.boxes) > 0:
                logger.info(f"✓ Détections trouvées: {len(result.boxes)} objets")
            else:
                logger.warning("⚠ Aucune détection sur l'image de test")
    
    logger.info("✓ Test terminé")

if __name__ == '__main__':
    print("="*60)
    print("YOLOv8n Segmentation Model Retraining")
    print("="*60)
    
    # Créer data.yaml
    create_data_yaml()
    
    # Entraîner
    train_model()
    
    # Copier le meilleur modèle
    copy_best_model()
    
    # Tester
    test_model()
    
    print("="*60)
    print("✓ Réentraînement terminé!")
    print(f"Modèle sauvegardé: {OUTPUT_MODEL}")
    print("="*60)
