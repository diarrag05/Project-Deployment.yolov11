# Projet de Détection de Chips et Trous (YOLOv11)

Application Flask pour l'analyse d'images de composants électroniques avec détection automatique de chips et de trous, calcul du taux de vide (void rate) et segmentation assistée par SAM (Segment Anything Model).

## 📋 Table des matières

- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Démarrage de l'application](#démarrage-de-lapplication)
- [Scénarios d'utilisation](#scénarios-dutilisation)
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
- Si `models/best.pt` n'existe pas : **entraînement depuis zéro** avec `yolo11s-seg.pt` (téléchargé automatiquement)

**Important** : 
- Le modèle réentraîné **écrase** le précédent `best.pt`
- Il n'y a pas besoin de checkbox pour forcer le modèle pré-entraîné, l'application gère automatiquement

**Lancement du réentraînement** :
- Via l'API : `POST /api/training/retrain`
- Via le script : `python backend/train.py --epochs 100 --batch 8 --patience 30`

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

