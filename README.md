# 🎯 Projet YOLOv11 - Segmentation et Calcul du Taux de Vides

Système complet de détection et segmentation des défauts (puces et trous) avec calcul automatique du taux de vides.

## 📋 Table des matières

1. [Vue d'ensemble](#-vue-densemble)
2. [Installation](#-installation)
3. [Entraînement](#-entraînement)
4. [Évaluation](#-évaluation)
5. [Calcul du taux de vides](#-calcul-du-taux-de-vides)
6. [Inférence](#-inférence)
7. [Architecture](#-architecture)
8. [Résultats](#-résultats)

## 🔍 Vue d'ensemble

Ce projet utilise **YOLOv11-segmentation** pour:
- ✅ Détecter les composants (chips)
- ✅ Détecter les défauts (trous)
- ✅ Segmenter les régions avec masques précis
- ✅ Calculer automatiquement le **taux de vides** (void_rate)

### Formule du taux de vides
```
void_rate = (somme des aires de trous / aire du composant) * 100 [%]
```

## 🚀 Installation

### Prérequis
- Python 3.8+
- CUDA 11.8+ (optionnel, pour GPU)

### Étapes

1. **Cloner/Accéder au projet**
```bash
cd "c:\Users\mdiia\OneDrive\Bureau\AIVANCITY\Cours\PGE4\Deployment n Maintenance\Project-Deployment.yolov11"
```

2. **Créer un environnement virtuel (recommandé)**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
python setup.py
# ou
pip install -r requirements.txt
```

4. **Vérifier l'installation**
```bash
python -c "import ultralytics; print(ultralytics.__version__)"
```

## 🎓 Entraînement

### Script principal: `train.py`

**Démarrer l'entraînement**
```bash
python train.py
```

### Configuration avancée

Modifier les hyperparamètres dans `train.py`:

```python
CONFIG = {
    "model_size": "m",           # Taille: n, s, m, l, x
    "epochs": 100,               # Nombre d'epochs
    "batch_size": 16,            # Taille du batch
    "img_size": 640,             # Taille des images
    "patience": 20,              # Early stopping
    "learning_rate": 0.001,      # Taux d'apprentissage
    "lr_scheduler": "cosine",    # Scheduler: linear, cosine, poly
    "weight_decay": 0.0005,      # Régularisation L2
}
```

### Paramètres d'augmentation disponibles

```python
train_yolov11_segmentation(
    # Mosaic & Mixup
    mosaic=1.0,          # Augmentation Mosaic (0-1)
    
    # HSV
    hsv_h=0.015,         # HSV Hue
    hsv_s=0.7,           # HSV Saturation
    hsv_v=0.4,           # HSV Value
    
    # Transformations géométriques
    degrees=10.0,        # Rotation (degrés)
    translate=0.1,       # Translation
    scale=0.5,           # Scale
    flipud=0.5,          # Flip vertical
    fliplr=0.5,          # Flip horizontal
    perspective=0.0,     # Perspective
)
```

### Monitoring avec TensorBoard

```bash
tensorboard --logdir runs/
```

Puis accédez à: http://localhost:6006

### Résultats de l'entraînement

Les résultats sont sauvegardés dans:
```
runs/
├── yolov11m-seg_20250122_120000/
│   ├── weights/
│   │   ├── best.pt          # Meilleur modèle
│   │   └── last.pt          # Dernier checkpoint
│   ├── events.out.tfevents  # Logs TensorBoard
│   └── results.csv          # Métriques
```

Le meilleur modèle est copié dans: `models/`

## 📊 Évaluation

### Script: `evaluate.py`

**Évaluer tous les modèles**
```bash
python evaluate.py
```

**Évaluer un modèle spécifique**
```bash
python evaluate.py models/yolov11m-seg_best_20250122_120000.pt
```

### Métriques calculées

#### Pour la **Détection** (Box):
- **mAP50**: Précision moyenne à IoU=50%
- **mAP50-95**: Précision moyenne à IoU=50% à 95%
- **Précision**: TP / (TP + FP)
- **Rappel**: TP / (TP + FN)

#### Pour la **Segmentation** (Mask):
- **mAP50 (Mask)**: Précision pour les masques
- **mAP50-95 (Mask)**: Précision globale des masques
- **IoU par classe**: Intersection over Union pour chip et hole

### Résultats

Les résultats JSON sont sauvegardés dans: `evaluations/`

## 🔍 Calcul du Taux de Vides

### Script: `void_rate_calculator.py`

**Calculer le void_rate sur le test set**
```bash
python void_rate_calculator.py
```

### Usage avancé

```python
from void_rate_calculator import VoidRateCalculator

# Initialiser
calculator = VoidRateCalculator("models/best_model.pt")

# Sur une image unique
result = calculator.calculate_void_rate("path/to/image.jpg")
print(f"Void Rate: {result['void_rate']:.2f}%")

# Sur un répertoire
results = calculator.process_directory("path/to/images/")

# Sauvegarder les résultats
calculator.save_results(results)
```

### Résultat d'une image

```json
{
    "image": "path/to/image.jpg",
    "void_rate": 15.35,
    "void_rate_percent": "15.35%",
    "hole_area_pixels": 15000,
    "chip_area_pixels": 97600,
    "num_holes": 3,
    "num_chips": 1,
    "image_resolution": "640x640"
}
```

### Statistiques globales

```json
{
    "num_images": 50,
    "avg_void_rate": 18.45,
    "min_void_rate": 2.10,
    "max_void_rate": 35.80,
    "std_void_rate": 8.23
}
```

## 🎯 Inférence

### Script: `inference.py`

**Inférence sur le test set**
```bash
python inference.py
```

**Inférence sur une image unique**
```bash
python inference.py -i "path/to/image.jpg"
```

**Inférence sur un répertoire**
```bash
python inference.py -d "path/to/images/"
```

**Avec modèle personnalisé**
```bash
python inference.py -m "models/custom_model.pt" -d "path/to/images/"
```

**Avec seuil de confiance personnalisé**
```bash
python inference.py -c 0.6 -d "path/to/images/"
```

**Sauvegarder les images annotées**
```bash
python inference.py -d "path/to/images/" -a
```

**Sauvegarder les résultats**
```bash
python inference.py -d "path/to/images/" -o "results.json"
```

### Résultat d'inférence

```json
{
    "image_path": "test/images/image_001.jpg",
    "image_name": "image_001.jpg",
    "resolution": "640x640",
    "model_used": "yolov11m-seg_best.pt",
    "confidence_threshold": 0.5,
    "num_detections": 4,
    "chip_area_pixels": 98000,
    "hole_area_pixels": 16500,
    "void_rate": 16.84,
    "void_rate_percent": "16.84%",
    "detections": [
        {
            "id": 0,
            "class": "chip",
            "confidence": 0.96,
            "area_pixels": 98000,
            "bbox": {"x1": 10, "y1": 20, "x2": 630, "y2": 640}
        },
        {
            "id": 1,
            "class": "hole",
            "confidence": 0.89,
            "area_pixels": 4500,
            "bbox": {"x1": 100, "y1": 150, "x2": 200, "y2": 250}
        }
    ]
}
```

## 📁 Architecture

```
Project-Deployment.yolov11/
├── data.yaml                      # Configuration du dataset
├── requirements.txt               # Dépendances Python
├── setup.py                       # Script de configuration
│
├── train.py                       # 🎓 Entraînement
├── evaluate.py                    # 📊 Évaluation
├── void_rate_calculator.py        # 🔍 Calcul du taux de vides
├── inference.py                   # 🎯 Inférence
│
├── train/                         # Dataset d'entraînement
│   ├── images/                    # Images
│   └── labels/                    # Annotations YOLO
│
├── valid/                         # Dataset de validation
│   ├── images/
│   └── labels/
│
├── test/                          # Dataset de test
│   ├── images/
│   └── labels/
│
├── models/                        # Modèles entraînés
│   └── yolov11m-seg_best_*.pt
│
├── runs/                          # Résultats d'entraînement
│   └── yolov11m-seg_*/
│       ├── weights/
│       ├── events.out.tfevents
│       └── results.csv
│
├── evaluations/                   # Résultats d'évaluation
│   └── evaluation_*.json
│
├── void_rate_results/             # Résultats void_rate
│   └── void_rate_*.json
│
└── inferences/                    # Résultats d'inférence
    ├── inference_*.json
    └── annotated_*.jpg
```

## 📈 Résultats Attendus

### Performance de détection
- **mAP50 (Box)**: 0.85+
- **mAP50-95 (Box)**: 0.75+
- **Précision**: 0.90+
- **Rappel**: 0.85+

### Performance de segmentation
- **mAP50 (Mask)**: 0.82+
- **mAP50-95 (Mask)**: 0.70+

### Vitesse d'inférence
- **CPU**: ~500-1000ms/image
- **GPU (RTX 3060)**: ~50-100ms/image

## 🔧 Tuning des Hyperparamètres

### Pour améliorer la précision
```python
CONFIG = {
    "epochs": 150,           # Plus d'epochs
    "batch_size": 8,         # Batch plus petit = gradient plus précis
    "learning_rate": 0.0005, # LR plus faible
    "weight_decay": 0.001,   # Régularisation plus forte
}
```

### Pour la vitesse (inférence)
```python
CONFIG = {
    "model_size": "n",       # Plus petit modèle
    "img_size": 416,         # Images plus petites
}
```

### Pour l'équilibre (recommandé)
```python
CONFIG = {
    "model_size": "m",
    "epochs": 100,
    "batch_size": 16,
    "img_size": 640,
    "learning_rate": 0.001,
    "lr_scheduler": "cosine",
}
```

## 🐛 Troubleshooting

### ❌ CUDA out of memory
```python
# Réduire batch_size
CONFIG["batch_size"] = 8

# ou réduire img_size
CONFIG["img_size"] = 416
```

### ❌ Modèle ne converge pas
```python
# Réduire learning_rate
CONFIG["learning_rate"] = 0.0005

# Augmenter epochs
CONFIG["epochs"] = 200
```

### ❌ Pas de GPU détecté
```bash
# Vérifier CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Réinstaller torch pour CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 📚 Ressources

- [YOLOv11 Docs](https://docs.ultralytics.com/models/yolov11/)
- [Ultralytics GitHub](https://github.com/ultralytics/ultralytics)
- [TensorBoard Guide](https://www.tensorflow.org/tensorboard/get_started)

## 📝 Licence

Ce projet utilise des données de Roboflow.

---

**Créé pour**: Cours PGE4 - Deployment & Maintenance  
**Date**: Janvier 2025
