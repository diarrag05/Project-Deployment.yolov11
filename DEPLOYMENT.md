# 🚀 YOLOv8 Segmentation - Deployment & Maintenance Project

> **Projet complet de détection et segmentation de trous dans des composants électroniques**
> 
> Entraînement YOLOv8n | Évaluation | Calcul automatique du taux de vides | Inférence

---

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Installation rapide](#installation-rapide)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Détails techniques](#détails-techniques)
- [Résultats](#résultats)
- [Troubleshooting](#troubleshooting)

---

## 👁️ Vue d'ensemble

Ce projet implémente une **pipeline complète YOLOv8-Segmentation** pour :

1. **Entraînement** : Modèle YOLOv8n sur 2 classes (chip, hole)
2. **Évaluation** : Métriques mAP, Precision, Recall, IoU
2. **Calcul automatique du taux de vides** : `void_rate = (pixels_holes / pixels_chip) × 100`
3. **Inférence** : Sur images individuelles, batch, ou répertoires entiers

### Caractéristiques principales
- ⚡ **Ultra-rapide** : Entraînement en ~50 secondes (YOLOv8n nano)
- 💾 **Léger** : Modèle 6.4 MB, pas de GPU requis (CPU compatible)
- 📊 **Monitoring** : TensorBoard intégré
- 🎯 **Automatisé** : Pipeline complet avec configuration personnalisable
- 🖱️ **Facile** : 6 fichiers `.bat` à double-cliquer

---

## ⚡ Installation rapide

### Prérequis
- Python 3.9+ (Anaconda recommandé)
- Windows 10+

### Étape 1 : Clone le repo
```bash
git clone <your-repo-url>
cd Project-Deployment.yolov11
```

### Étape 2 : Installe les dépendances
```bash
pip install -r requirements.txt
```

Ou simplement double-clic sur : **`simple_setup.py`**

### Étape 3 : Vérifie l'installation
```bash
python CHECK.py
```

---

## 🚀 Utilisation

### Fichiers .BAT (Double-clic pour exécuter)

| Fichier | Description | Durée |
|---------|-------------|-------|
| `1_CHECK.bat` | Vérifier le projet | 2 sec |
| `5_TRAIN.bat` | Entraîner le modèle | 2-3 min |
| `2_INFERENCE.bat` | Faire des prédictions | 1 min |
| `3_VOID_RATE.bat` | Calculer taux de vides | 2 min |
| `4_EVALUATE.bat` | Évaluer le modèle | 1 min |
| `START_TENSORBOARD.bat` | Lancer TensorBoard | Continu |
| `MENU.bat` | Menu interactif | - |

### Utilisation en ligne de commande

```bash
# 1. Vérifier le projet
python CHECK.py

# 2. Entraîner
python fast_train.py

# 3. Faire une inférence
python inference.py

# 4. Calculer les taux de vides
python void_rate_calculator.py

# 5. Évaluer le modèle
python evaluate.py

# 6. Pipeline complet
python pipeline.py

# 7. Voir TensorBoard
tensorboard --logdir runs/segment/train2
# Puis ouvre : http://localhost:6006/
```

---

## 📁 Structure du projet

```
Project-Deployment.yolov11/
├── 📊 DATA
│   ├── data.yaml                 # Configuration dataset
│   ├── train/images/             # 66 images d'entraînement
│   ├── valid/images/             # 20 images de validation
│   └── test/images/              # 11 images de test
│
├── 🤖 MODÈLES
│   ├── yolov8n-seg.pt            # Modèle pré-entraîné (téléchargé auto)
│   └── models/
│       └── yolov8n-seg_trained.pt # Modèle entraîné (6.4 MB)
│
├── 📜 SCRIPTS PYTHON
│   ├── train.py                  # Entraînement principal (235 lignes)
│   ├── fast_train.py             # Entraînement ultra-rapide ⚡
│   ├── simple_train.py           # Version simplifiée
│   ├── inference.py              # Inférence + void_rate (500 lignes)
│   ├── evaluate.py               # Évaluation modèle (200 lignes)
│   ├── void_rate_calculator.py   # Calcul taux de vides (400 lignes)
│   ├── pipeline.py               # Pipeline automatisé (249 lignes)
│   ├── config.py                 # Configurations prédéfinies
│   └── CHECK.py                  # Vérification rapide
│
├── 🎯 SCRIPTS BATCH
│   ├── 1_CHECK.bat               # Vérifier projet
│   ├── 2_INFERENCE.bat           # Inférence
│   ├── 3_VOID_RATE.bat           # Taux de vides
│   ├── 4_EVALUATE.bat            # Évaluation
│   ├── 5_TRAIN.bat               # Entraînement
│   ├── MENU.bat                  # Menu interactif
│   └── START_TENSORBOARD.bat     # TensorBoard
│
├── 📖 DOCUMENTATION
│   ├── README.md                 # Documentation principale
│   ├── QUICKSTART.py             # Guide interactif
│   ├── GET_STARTED.py            # Assistant d'installation
│   ├── COMMANDS.md               # Toutes les commandes
│   ├── TROUBLESHOOTING.md        # Résolution des problèmes
│   └── README_BATCH_FILES.md     # Guide fichiers .bat
│
├── 📊 RÉSULTATS (Généré à l'exécution)
│   ├── runs/segment/train2/      # Résultats d'entraînement
│   ├── inferences/               # Résultats d'inférence (JSON)
│   ├── evaluations/              # Métriques d'évaluation
│   └── void_rate_results/        # Taux de vides calculés
│
└── 📦 CONFIGURATION
    ├── requirements.txt          # Dépendances Python
    ├── .gitignore
    └── config.py                 # Hyperparamètres
```

---

## 🔧 Détails techniques

### Dataset
- **Classes** : 2 (chip: 0, hole: 1)
- **Format** : YOLO (images + labels .txt)
- **Répartition** : 66 train, 20 valid, 11 test (97 total)

### Modèle
- **Architecture** : YOLOv8n-seg (Nano - ultra-léger)
- **Taille** : 6.4 MB (CPU-friendly)
- **Task** : Instance segmentation
- **Epochs** : 3 (configurable)

### Hyperparamètres (fast_train.py)
```python
epochs=3              # 3 epochs (configurable)
imgsz=320            # Image size (petit = rapide)
batch=4              # Batch size (petit pour CPU)
device='cpu'         # CPU ou 0 pour GPU
learning_rate='auto' # AdamW optimizer
momentum=0.9
weight_decay=0.0005
```

### Formule Taux de Vides
```
void_rate = (somme_pixels_holes / somme_pixels_chip) × 100
```

### Métriques d'Évaluation
- **mAP50** : Mean Average Precision @ IoU=0.5
- **mAP50-95** : Mean Average Precision @ IoU=0.5:0.95
- **Precision** : % prédictions correctes
- **Recall** : % objets détectés
- **IoU** : Intersection over Union des masks

---

## 📊 Résultats

### Entraînement
```
Epoch 1/3: loss=1.197, seg_loss=2.464
Epoch 2/3: loss=1.068, seg_loss=1.822
Epoch 3/3: loss=1.006, seg_loss=1.690

Temps total: ~50 secondes
```

### Validation
```
mAP50: 0.355
Precision: 0.227
Recall: 0.461
```

### Inférence (Test)
```
✅ Modèle chargé
✅ Image testée
✅ Résultats sauvegardés en JSON
```

---

## 📌 Configuration personnalisée

### Éditer les hyperparamètres

1. **Ouvre** `config.py`
2. **Modifie** les presets (FAST_TRAINING, BALANCED_TRAINING, etc.)
3. **Utilise** dans le pipeline

Exemple :
```python
FAST_TRAINING = {
    "epochs": 3,
    "imgsz": 320,
    "batch": 4,
}

HIGH_QUALITY_TRAINING = {
    "epochs": 50,
    "imgsz": 640,
    "batch": 16,
}
```

### Augmenter les epochs

Édite `fast_train.py` ligne 28 :
```python
epochs=10  # Au lieu de 3
```

### Ajouter plus d'images

1. Ajoute images dans `train/images/`
2. Ajoute labels correspondants dans `train/labels/`
3. Relance `5_TRAIN.bat`

---

## 🆘 Troubleshooting

### "Module not found: ultralytics"
```bash
pip install ultralytics
```

### "CUDA not available"
C'est normal ! Le projet utilise CPU par défaut. C'est plus lent mais ça fonctionne.

### TensorBoard ne démarre pas
```bash
pip install --upgrade tensorboard
tensorboard --logdir runs/segment/train2 --port 6006
```

### Modèle non trouvé
```bash
python simple_setup.py  # Télécharge le modèle automatiquement
```

### Port 6006 déjà utilisé
```bash
tensorboard --logdir runs/segment/train2 --port 6007  # Utilise 6007 à la place
```

### Erreur de mémoire
Réduis `batch=2` dans `fast_train.py`

### Les prédictions sont nulles (0 détections)
- Normal avec 3 epochs seulement ! 
- Augmente epochs à 10-20 dans `fast_train.py`
- Ajoute plus d'images d'entraînement

---

## 🎓 Apprentissage & Amélioration

### Pour de meilleurs résultats
1. **Augmente les epochs** : 3 → 50 (plus lent mais meilleur)
2. **Ajoute des images** : Plus de données = meilleur modèle
3. **Augmente imgsz** : 320 → 640 (plus précis mais plus lent)
4. **Utilise GPU** : Change `device='cpu'` → `device=0` (50x+ rapide)

### Ressources utiles
- [YOLOv8 Docs](https://docs.ultralytics.com/)
- [Instance Segmentation](https://github.com/ultralytics/ultralytics)
- [PyTorch](https://pytorch.org/)

---

## 📝 Fichiers clés

### Scripts d'entraînement
- **`fast_train.py`** : Recommandé (ultra-rapide ⚡)
- **`train.py`** : Version complète avec plus d'options
- **`simple_train.py`** : Version simplifiée
- **`pipeline.py`** : Entraînement + évaluation + inférence automatiques

### Scripts de test
- **`inference.py`** : Inférence flexible (image/batch/dossier)
- **`void_rate_calculator.py`** : Calcul taux de vides
- **`evaluate.py`** : Métriques complètes

### Documentation
- **`CHECK.py`** : Vérification rapide (à lancer à chaque fois)
- **`GET_STARTED.py`** : Guide interactif pas-à-pas
- **`QUICKSTART.py`** : Démarrage rapide

---

## 📜 Licence & Attribution

- **YOLOv8** : [Ultralytics](https://github.com/ultralytics/ultralytics) (AGPL-3.0)
- **PyTorch** : [Facebook](https://pytorch.org/) (BSD)

---

## 👤 Auteur

Créé comme projet de démonstration pour PGE4 - Deployment & Maintenance

---

## ✅ Checklist de déploiement

- [x] Entraînement fonctionnel
- [x] Inférence testée
- [x] Taux de vides calculé
- [x] Évaluation implémentée
- [x] TensorBoard configuré
- [x] Fichiers .bat créés
- [x] Documentation complète
- [x] Dépendances listées
- [x] .gitignore configuré
- [x] Prêt pour GitHub !

---

**Projet complet et fonctionnel ! 🚀**

Dernière mise à jour : 22/11/2025
