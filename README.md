# Projet de Détection de Chips et Trous (YOLOv11)

Application Flask pour l'analyse d'images de composants électroniques avec détection automatique de chips et de trous, calcul du taux de vide (void rate) et segmentation assistée par SAM (Segment Anything Model).

## 📋 Table des matières

- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Démarrage de l'application](#démarrage-de-lapplication)
- [Scénarios d'utilisation](#scénarios-dutilisation)
- [YOLOv11 Fine-tuning: Complete Guide](#-yolov11-fine-tuning-complete-guide)
- [Scripts d'entraînement et d'évaluation](#-scripts-dentraînement-et-dévaluation)
- [Explication des calculs](#explication-des-calculs)
- [Structure du projet](#structure-du-projet)
- [Notes importantes](#notes-importantes)
- [Endpoints API](#endpoints-api-principaux)

## 🔧 Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- GPU NVIDIA avec CUDA (recommandé pour l'entraînement et l'inférence rapide)
  - Alternative : CPU (plus lent mais fonctionnel)
  - Alternative : Apple Silicon avec MPS (supporté)

## 📦 Installation

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd Project-Deployment.yolov11
```

### 2. Créer un environnement virtuel (recommandé)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

**Note importante** : L'installation peut prendre plusieurs minutes car elle inclut :
- PyTorch et ses dépendances
- Ultralytics (YOLOv11)
- Segment Anything Model (SAM) depuis GitHub

### 4. Vérifier la configuration

Le fichier `.env` est déjà présent dans le projet avec les paramètres par défaut. Vous pouvez le modifier si nécessaire (voir section [Configuration](#configuration)).

## ⚙️ Configuration

Le projet utilise un fichier `.env` pour la configuration. Les valeurs par défaut sont déjà définies, mais vous pouvez les personnaliser :

### Variables principales

- `FLASK_HOST` : Adresse IP du serveur (défaut: `127.0.0.1`)
- `FLASK_PORT` : Port du serveur (défaut: `5000`)
- `FLASK_DEBUG` : Mode debug (défaut: `True`)
- `TRAINING_EPOCHS` : Nombre d'époques pour l'entraînement (défaut: `100`)
- `TRAINING_BATCH_SIZE` : Taille du batch (défaut: `8`)
- `TRAINING_PATIENCE` : Patience pour l'early stopping (défaut: `30`)
- `VOID_RATE_THRESHOLD` : Seuil de void rate en pourcentage (défaut: `5.0`)

Voir `backend/src/config.py` pour la liste complète des variables configurables.

## 🚀 Démarrage de l'application

### Option 1 : Via le script de démarrage (recommandé)

```bash
python api/run_api.py
```

### Option 2 : Via le module Flask directement

```bash
python api/app.py
```

### Option 3 : Via Flask CLI

```bash
cd api
flask run
```

L'application sera accessible sur `http://127.0.0.1:5000` (ou l'adresse configurée dans `.env`).

### Interface web

Ouvrez votre navigateur et accédez à :
- **Interface principale** : `http://127.0.0.1:5000/`
- **Health check** : `http://127.0.0.1:5000/health`
- **API endpoints** : `http://127.0.0.1:5000/api/...`

## 📊 Scénarios d'utilisation

### Scénario 1 : Premier démarrage (aucun modèle)

**Situation** : Vous clonez le projet pour la première fois, le dossier `models/` ne contient pas de modèle finetuné (`best.pt`).

**Comportement automatique** :
1. L'utilisateur tente une analyse d'image via l'API
2. L'API détecte l'absence de `models/best.pt`
3. **L'entraînement initial est lancé automatiquement en arrière-plan**
4. L'API retourne une erreur **503** avec le message :
   ```json
   {
     "error": "No model found. Initial training has been started automatically.",
     "training_id": "<uuid>",
     "message": "Please wait for training to complete, then try again."
   }
   ```
5. L'utilisateur doit attendre la fin de l'entraînement avant de pouvoir analyser des images

**Durée estimée** : L'entraînement initial peut prendre de 30 minutes à plusieurs heures selon :
- La puissance du GPU/CPU
- Le nombre d'époques configuré
- La taille du dataset

**Suivi de l'entraînement** :
- Consultez les logs dans `logs/training.log`
- Utilisez l'endpoint `/api/training/status/<training_id>` pour vérifier le statut

### Scénario 2 : Modèle existant

**Situation** : Le fichier `models/best.pt` existe déjà.

**Comportement** :
- L'analyse fonctionne normalement avec le modèle finetuné
- Aucun entraînement n'est déclenché
- Les performances sont optimales

### Scénario 3 : Réentraînement

**Situation** : L'utilisateur souhaite réentraîner le modèle avec de nouvelles données.

**Comportement automatique** :
- Si `models/best.pt` existe : **fine-tuning** (entraînement continu depuis le modèle existant)
- Si `models/best.pt` n'existe pas : **entraînement depuis zéro** avec `models/yolo11s-seg.pt` (téléchargé automatiquement)

**Important** : 
- Le modèle réentraîné **écrase** le précédent `best.pt`
- Il n'y a pas besoin de checkbox pour forcer le modèle pré-entraîné, l'application gère automatiquement

**Lancement du réentraînement** :
- Via l'API : `POST /api/training/retrain`
- Via le script : `python backend/train.py --epochs 100 --batch 8 --patience 30`

## 🎓 YOLOv11 Fine-tuning: Complete Guide

### Introduction

This project implements an **automatic defect detection and segmentation system** for electronic components using the **YOLOv11-segmentation** model. The main objective is to identify components (chips) and defects (holes/voids) present in these components, then automatically calculate the **void rate** for quality assessment.

### Why this project?

In the electronics industry, **voids in solder joints** can cause component failures. Automatic detection of these defects is crucial for:
- 🔍 Automated quality control
- 📊 Void rate calculation
- ⚡ Reduction of manual inspection costs
- 🎯 Improvement of product reliability

### Dataset and Data Preparation

#### Data Source
- **Origin**: Custom dataset of electronic components with defects
- **Annotation Tool**: Roboflow platform
- **Annotation Process**: Manual polygon-based annotation for each component (chip) and defect (hole/void)
- **Export Format**: YOLOv11 segmentation format (normalized polygon coordinates)

#### Annotation Format

**YOLO Segmentation Format** (normalized polygons):
```
class_id x1 y1 x2 y2 x3 y3 ... xn yn
```

Example of a hole annotation:
```
1 0.4527 0.3892 0.4634 0.3901 0.4729 0.3987 0.4527 0.3892
```
- `1` = class "hole-JsHt"
- (x, y) coordinates normalized between 0 and 1

#### Dataset Distribution

| Split | Number of images | Percentage |
|-------|-----------------|------------|
| **Train** | 66 | 68% |
| **Validation** | 20 | 21% |
| **Test** | 11 | 11% |
| **Total** | **97** | **100%** |

#### Classes

| ID | Class name | Description |
|----|------------|-------------|
| 0 | `chip` | Electronic components |
| 1 | `hole-JsHt` | Holes/voids in components |

### Architecture and Technologies

#### Technologies Used

| Technology | Version | Usage |
|-----------|---------|-------|
| **Python** | 3.8+ | Main language |
| **Ultralytics** | ≥8.0.0 | YOLOv11 framework |
| **PyTorch** | ≥2.0.0 | Deep learning backend |
| **OpenCV** | ≥4.8.0 | Image processing |
| **Matplotlib** | ≥3.7.0 | Visualization |

#### YOLOv11-Segmentation Model

**Why YOLOv11-seg?**
- 🚀 **Fast**: Real-time inference
- 🎯 **Accurate**: State-of-the-art for instance segmentation
- 📦 **Compact**: Small model (11s) with 11.6M parameters
- 🔄 **Pre-trained**: On COCO dataset (80 classes)

**Architecture**:
- **Backbone**: CSPDarknet with P2-P5 feature pyramids
- **Neck**: PAN (Path Aggregation Network)
- **Head**: Dual heads for detection + segmentation
- **Output**: Bounding boxes + segmentation masks

### Work Completed

#### Step 1: Exploration and Understanding
**Objective**: Understand YOLOv11 fine-tuning and analyze data

**Actions performed**:
- 📹 Study of video tutorial on YOLOv11 fine-tuning
- 📂 Analysis of dataset structure (97 images, segmentation format)
- 🔍 Verification of annotations (polygons vs bounding boxes)
- 📊 Statistics: 2 classes, train/val/test distribution

**Results**:
```
Dataset Statistics:
- Total images: 97
- Train: 66 images (68%)
- Validation: 20 images (21%)
- Test: 11 images (11%)
- Classes: chip, hole-JsHt
- Format: YOLOv11 segmentation (polygons)
```

#### Step 2: Model Selection
**Problem**: Choose between YOLOv11n/s/m/l/x

**Decision**:
- Initially: **YOLOv11m** (medium, more accurate)
- Finally: **YOLOv11s** (small, faster)

**Reason for change**:
```
YOLOv11m: ~3.3 hours training time (CPU)
YOLOv11s: ~1.5 hours training time (CPU)
```
→ Time savings with acceptable performance for 97 images

#### Step 3: Training Configuration

**File created**: `train.py`

**Optimal configuration found**:
```python
model = YOLO("models/yolo11s-seg.pt")  # ⚠️ Important: -seg for segmentation

config = {
    'data': 'dataset/data.yaml',
    'epochs': 100,
    'batch': 8,              # Reduced from 16 → 8 for stability
    'imgsz': 640,
    'device': 'cpu',         # CPU instead of MPS (see issues)
    'optimizer': 'AdamW',
    'lr0': 0.001,
    'patience': 30,          # Early stopping
    'amp': False,            # Disabled for MPS compatibility
}
```

**Configuration file**: `data.yaml`
```yaml
train: ../dataset/train/images
val: ../dataset/valid/images
test: ../dataset/test/images
nc: 2
names:
  0: chip
  1: hole-JsHt
```

#### Step 4: Model Training

**Execution command**:
```bash
python train.py
# or
python backend/train.py
```

**Training duration**: ~1.067 hours (64 minutes)

**Early stopping**:
- Configured: 30 epochs patience
- Stopped at: Epoch 62 (out of 100 max)
- Best model: Epoch 32

**Metrics monitored during training**:
- Box Loss (bounding box localization)
- Seg Loss (segmentation mask quality)
- Class Loss (chip vs hole classification)
- mAP50 and mAP50-95

**Generated files**:
```
runs/segment/train/
├── weights/
│   ├── best.pt          # Best model (epoch 32)
│   └── last.pt          # Last model (epoch 62)
├── results.csv          # Metrics per epoch
├── confusion_matrix.png # Confusion matrix
├── results.png          # Training curves
├── PR_curve.png         # Precision-Recall curves
├── F1_curve.png         # F1-Score curves
└── val_batch*.jpg       # Prediction examples
```

#### Step 5: Model Evaluation

**File created**: `evaluate.py`

**Evaluation command**:
```bash
python evaluate.py --model runs/segment/train/weights/best.pt
```

**Metrics calculated**:
- mAP50 and mAP50-95 (box & mask)
- Precision and Recall per class
- F1-Score per class
- Confusion matrix

#### Step 6: Inference Script

**File created**: `inference.py`

**Usage**:
```bash
# Prediction on one image
python inference.py --source dataset/test/images/image.jpg

# With custom confidence threshold
python inference.py --source dataset/test/images/image.jpg --conf 0.5 --iou 0.7
```

### Results and Analysis

#### Overall Performance

**Successful training** with the following metrics:

| Metric Type | mAP50 | mAP50-95 | Precision | Recall |
|-------------|-------|----------|-----------|--------|
| **Bounding Box** | 88.0% | 72.7% | 96.8% | 72.0% |
| **Segmentation Mask** | 87.3% | 64.1% | 96.2% | 72.0% |

#### Per-Class Analysis

##### Class "chip" (Components)
```
✅ Precision: 95.6%  → Model makes few false detections
✅ Recall: 100%      → Model detects all components
✅ F1-Score: 97.73%  → Excellent balance
```

**Interpretation**:
The model is **excellent** at detecting electronic components. It doesn't miss any component (100% recall) and makes very few errors (95.6% precision).

##### Class "hole-JsHt" (Holes/Voids)
```
✅ Precision: 97.8%  → Model makes very few false detections
⚠️  Recall: 43.9%    → Model misses 56% of holes
⚠️  F1-Score: 60.60% → Moderate performance
```

**Interpretation**:
The model is **very conservative** in detecting holes:
- When it detects a hole, it's correct 97.8% of the time (excellent precision)
- **BUT** it misses more than half of the holes present (low recall)

**Why this imbalance?**
1. 🔢 **Class imbalance**: Likely more chips than holes in dataset
2. 📏 **Object size**: Holes are smaller and harder to detect
3. 📊 **Limited data**: Only 97 images total

#### Results Visualization

**Precision-Recall Curve (PR Curve)**:
```
runs/segment/train/PR_curve.png
```
- Area under curve = mAP
- Closer the curve to top-right corner, the better

**F1-Score Curve**:
```
runs/segment/train/F1_curve.png
```
- Shows best precision-recall trade-off
- Peak of curve = optimal confidence threshold

**Confusion Matrix**:
```
runs/segment/train/confusion_matrix.png
```

Example confusion matrix:
```
                Predicted
              chip   hole   background
Actual chip     50     0        0      ← Perfect!
Actual hole      0    15       19      ← 19 holes missed
       BG        1     2       --
```

#### Training Curves

**Loss Evolution**:
```
runs/segment/train/results.png
```

Expected observation:
- ✅ Box Loss ↓ : Localization improvement
- ✅ Seg Loss ↓ : Mask improvement
- ✅ Class Loss ↓ : Classification improvement
- ✅ Stable convergence without overfitting

### Improvement Recommendations

**To improve hole recall**:

1. **Collect more data**:
   ```
   Current dataset: 97 images
   Recommended: 300-500 images
   ```

2. **Increase data augmentation** (in `train.py`):
   ```python
   mosaic=1.0,        # Mix 4 images
   mixup=0.1,         # Add mixup
   copy_paste=0.1,    # Copy-paste objects
   ```

3. **Adjust confidence threshold** (inference):
   ```bash
   # More permissive for holes
   python inference.py --source dataset/test/images/image.jpg --conf 0.15  # instead of 0.25
   ```

4. **Use larger model**:
   ```python
   model = YOLO("models/yolo11m-seg.pt")  # Medium instead of Small
   ```

### Issues Encountered and Solutions

#### Issue 1: Shape Mismatch Error

**Error encountered**:
```
RuntimeError: shape mismatch: value tensor of shape [156542]
cannot be broadcast to indexing result of shape [142122]
```

**Cause**:
- Used **detection** model (`models/yolo11s.pt`)
- While annotations were in **segmentation** format (polygons)

**Solution applied**:
```python
# ❌ Incorrect
model = YOLO("models/yolo11s.pt")  # Detection model

# ✅ Correct
model = YOLO("models/yolo11s-seg.pt")  # Segmentation model
```

**Lesson learned**:
- `.pt` = detection (bounding boxes)
- `-seg.pt` = segmentation (polygon masks)

#### Issue 2: MPS Error on Apple Silicon

**Error encountered**:
```
RuntimeError: view size is not compatible with input tensor's
size and stride (at least one dimension spans across two
contiguous subspaces). Use .reshape(...) instead.
```

**Context**:
- MacBook with M1/M2 chip (Apple Silicon)
- Attempted use of MPS backend (Metal Performance Shaders)

**Solutions attempted**:

1. **First attempt**: Disable AMP
   ```python
   amp=False  # Automatic Mixed Precision
   ```
   **Result**: ❌ Failed, error persists

2. **Second attempt**: Reduce batch size
   ```python
   batch=8  # instead of 16
   ```
   **Result**: ❌ Failed, error persists

3. **Final solution**: Use CPU
   ```python
   device='cpu'  # instead of 'mps'
   ```
   **Result**: ✅ Success

**Technical explanation**:
YOLOv11-segmentation uses complex tensor operations that aren't yet fully supported by PyTorch's MPS backend for segmentation.

**Impact**:
- ⏱️ Slower training (~1h on CPU vs ~20min on GPU)
- ✅ But works stably

**Future alternative**:
```python
# If you have NVIDIA GPU
device='cuda'  # Much faster
```

#### Issue 3: Relative Paths in data.yaml

**Error encountered**:
```
FileNotFoundError: [Errno 2] No such file or directory:
'../train/images'
```

**Cause**:
Using relative paths in `data.yaml`:
```yaml
# ❌ Problematic
path: .
train: ../train/images
```

**Solution applied**:
```yaml
# ✅ Correct
train: ../dataset/train/images
val: ../dataset/valid/images
test: ../dataset/test/images
```

**Best practice**:
- `train/val/test` = **relative** paths from `data.yaml` file location
- Paths are resolved relative to the `data.yaml` file location

### Development Notes

#### Important Technical Decisions

1. **Choice of YOLOv11s instead of YOLOv11m**
   - Reason: Training time savings (1h vs 3.3h)
   - Trade-off: Slight accuracy decrease acceptable for 97 images

2. **Using CPU instead of MPS**
   - Reason: MPS incompatibility with segmentation operations
   - Impact: Longer training time but stable

3. **Early stopping at 30 epochs**
   - Reason: Avoid overfitting on small dataset
   - Result: Stopped at epoch 62, best model at epoch 32

#### Lessons Learned

1. ✅ **Always verify annotation format** before choosing model
2. ✅ **Use relative paths** in configuration files
3. ✅ **Test on small batch** before launching complete training
4. ✅ **Document encountered issues** for future reference

## 🔬 Scripts d'entraînement et d'évaluation

Le projet inclut plusieurs scripts pour l'entraînement, l'évaluation et l'inférence :

### Entraînement (`backend/train.py`)

Script d'entraînement complet avec gestion automatique des modèles et détection de device.

```bash
# Entraînement avec paramètres par défaut
python backend/train.py

# Entraînement avec paramètres personnalisés
python backend/train.py --epochs 150 --batch 16 --patience 50
```

**Fonctionnalités** :
- Détection automatique GPU/CPU/MPS
- Utilise `models/best.pt` s'il existe (fine-tuning), sinon `models/yolo11s-seg.pt` (entraînement depuis zéro)
- Copie automatique du meilleur modèle dans `models/best.pt`
- Logging détaillé dans `logs/training.log`

### Évaluation (`evaluate.py`)

Script pour évaluer les performances du modèle sur les datasets de validation ou de test.

```bash
# Évaluation sur le set de validation (défaut)
python evaluate.py

# Évaluation sur le set de test
python evaluate.py --split test

# Évaluation avec un modèle spécifique
python evaluate.py --model models/best.pt --split val

# Évaluation avec paramètres personnalisés
python evaluate.py --batch 16 --imgsz 640
```

**Métriques affichées** :
- mAP50 et mAP50-95 (bounding boxes et masks)
- Precision et Recall globaux
- Métriques par classe (chip, hole-JsHt)
- Génération de graphiques dans `runs/segment/eval_*/`

### Inférence (`inference.py`)

Script pour faire des prédictions sur de nouvelles images.

```bash
# Prédiction sur une image
python inference.py --source dataset/test/images/image.jpg

# Prédiction sur un dossier d'images
python inference.py --source dataset/test/images/

# Avec seuils personnalisés
python inference.py --source dataset/test/images/image.jpg --conf 0.5 --iou 0.7

# Sauvegarder les labels au format YOLO
python inference.py --source dataset/test/images/image.jpg --save-txt
```

**Options disponibles** :
- `--model` : Chemin vers le modèle (défaut: `models/best.pt`)
- `--source` : Image, vidéo ou dossier (requis)
- `--conf` : Seuil de confiance (défaut: 0.25)
- `--iou` : Seuil IoU pour NMS (défaut: 0.7)
- `--save-txt` : Sauvegarder les labels au format YOLO
- `--imgsz` : Taille d'image (défaut: 640)

**Résultats** :
- Images annotées sauvegardées dans `runs/segment/predict/`
- Labels (si `--save-txt`) dans `runs/segment/predict/labels/`

### Gestion automatique de SAM

**Comportement** : Si le modèle SAM (`models/sam_vit_h_4b8939.pth`) n'est pas présent :
- Le modèle est **téléchargé automatiquement** lors de la première utilisation de la segmentation SAM
- Taille du fichier : ~2.4 GB
- Téléchargement depuis : `https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth`

**Note** : Dans un contexte de production, les modèles finetunés (`best.pt`) et SAM seront déjà présents, donc l'utilisateur n'aura pas à faire face à ces lourdes installations. Ce sont des **fallbacks extrêmes** pour les cas de développement ou de déploiement initial.

## 📐 Explication des calculs

L'application calcule plusieurs métriques importantes pour l'analyse des composants :

### 1. **Area (Aire)**

- **Définition** : Surface totale des chips détectées en pixels
- **Calcul** : Somme des aires de tous les masques de classe "chip" (class_id = 0)
- **Unité** : Pixels²

### 2. **Void Rate (Taux de vide)**

- **Définition** : Pourcentage de la surface totale des chips occupée par les trous
- **Formule** : `Void Rate (%) = (Surface totale des trous / Surface totale des chips) × 100`
- **Interprétation** :
  - Plus le void rate est élevé, plus la chip est endommagée
  - Un void rate supérieur au seuil configuré (`VOID_RATE_THRESHOLD`, défaut: 5%) indique une chip non utilisable

### 3. **Void % (Pourcentage de vide)**

- **Définition** : Identique au Void Rate, exprimé en pourcentage
- **Utilisation** : Métrique principale pour déterminer si une chip est utilisable

### 4. **Max.void % (Pourcentage de vide maximum)**

- **Définition** : Pourcentage de la surface de la chip occupée par le **plus grand trou individuel**
- **Formule** : `Max.void % = (Aire du plus grand trou / Aire totale des chips) × 100`
- **Interprétation** :
  - Indique la taille du défaut le plus important
  - Utile pour identifier des trous critiques même si le void rate global est acceptable
  - Peut être calculé par chip individuelle ou globalement sur l'image

### Exemple de calcul

```
Image avec :
- 2 chips détectées : Chip A (1000 px²), Chip B (800 px²)
- 3 trous détectés : Trou 1 (20 px²), Trou 2 (30 px²), Trou 3 (50 px²)

Calculs globaux :
- Area = 1000 + 800 = 1800 px²
- Void % = (20 + 30 + 50) / 1800 × 100 = 5.56%
- Max.void % = 50 / 1800 × 100 = 2.78%

Calculs par chip :
Chip A :
- Area = 1000 px²
- Void % = (20 + 30) / 1000 × 100 = 5.0%
- Max.void % = 30 / 1000 × 100 = 3.0%

Chip B :
- Area = 800 px²
- Void % = 50 / 800 × 100 = 6.25%
- Max.void % = 50 / 800 × 100 = 6.25%
```

## 📁 Structure du projet

```
Project-Deployment.yolov11/
├── api/                    # Application Flask et routes API
│   ├── app.py             # Configuration Flask principale
│   ├── routes.py          # Endpoints API
│   ├── run_api.py         # Script de démarrage
│   ├── storage.py         # Gestion du stockage des images validées
│   └── training_job.py    # Gestion des jobs d'entraînement
│
├── backend/               # Logique métier
│   ├── src/
│   │   ├── config.py      # Configuration centralisée
│   │   ├── services/      # Services métier
│   │   │   ├── yolo_inference.py
│   │   │   ├── void_rate_calculator.py
│   │   │   ├── sam_segmentation.py
│   │   │   ├── training_service.py
│   │   │   └── label_manager.py
│   │   ├── schemas/       # Modèles de données
│   │   └── utils/         # Utilitaires
│   └── train.py           # Script d'entraînement
│
├── dataset/               # Dataset d'entraînement (inclus)
│   ├── data.yaml          # Configuration YOLO
│   ├── train/             # Images et labels d'entraînement
│   ├── valid/             # Images et labels de validation
│   └── test/              # Images et labels de test
│
├── models/                # Modèles entraînés
│   ├── best.pt            # Modèle YOLO finetuné (généré après entraînement)
│   └── sam_vit_h_4b8939.pth  # Modèle SAM (téléchargé automatiquement)
│
├── outputs/               # Résultats et sorties
│   ├── uploads/           # Images uploadées temporairement
│   ├── inference/         # Images avec inférence YOLO
│   ├── sam_segmentation/  # Résultats de segmentation SAM
│   ├── results/           # Résultats d'analyse
│   └── validated_images/  # Images validées et leurs labels
│
├── logs/                  # Fichiers de logs
│   ├── app.log            # Logs de l'application
│   └── training.log       # Logs d'entraînement
│
├── frontend/              # Interface web
│   └── index.html         # Interface utilisateur
│
├── evaluate.py            # Script d'évaluation du modèle
├── inference.py           # Script d'inférence standalone
├── requirements.txt       # Dépendances Python
├── .env                   # Variables d'environnement (inclus)
└── README.md             # Ce fichier
```

## ⚠️ Notes importantes

### Modèle réentraîné

- **Le modèle issu du réentraînement écrase le précédent `best.pt`**
- Il n'y a pas de sauvegarde automatique des versions précédentes
- Pour conserver une version, copiez `best.pt` avant un nouveau réentraînement

### Dataset et configuration

- Le dossier `dataset/` est **inclus** dans le projet pour faciliter la passation
- Le fichier `.env` est **inclus** avec les paramètres par défaut
- **Aucune donnée sensible ou confidentielle** n'est présente dans ces fichiers

### Production vs Développement

- **En production** : Les modèles finetunés (`best.pt`) et SAM seront déjà présents
- Les fallbacks (téléchargement automatique, entraînement initial) sont prévus pour :
  - Le développement local
  - Les déploiements initiaux
  - Les environnements de test

### Logs et débogage

- Consultez `logs/app.log` pour les erreurs de l'application
- Consultez `logs/training.log` pour suivre l'entraînement
- Les logs incluent des informations détaillées sur les opérations

### Performance

- **GPU recommandé** : L'entraînement et l'inférence sont beaucoup plus rapides avec un GPU NVIDIA
- **CPU** : Fonctionne mais peut être très lent pour l'entraînement (plusieurs heures)
- **Apple Silicon** : Support MPS pour accélération sur Mac avec puce Apple

## 🔗 Endpoints API principaux

- `POST /api/analyze` : Analyser une image
- `POST /api/segment` : Segmentation SAM guidée
- `POST /api/validate/from-segmentation` : Valider une image depuis SAM
- `POST /api/training/retrain` : Lancer un réentraînement
- `GET /api/training/status/<training_id>` : Statut d'un entraînement
- `POST /api/analyze/export-csv` : Exporter les résultats en CSV

## 📝 Licence

Voir le fichier de licence du projet.

## 👥 Support

Pour toute question ou problème, consultez les logs dans `logs/` ou contactez l'équipe de développement.

