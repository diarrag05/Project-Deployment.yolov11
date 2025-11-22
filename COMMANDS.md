#!/bin/bash
# ========================================================================
# COMMANDES UTILES - YOLOv11 Segmentation Project
# ========================================================================

# ========================================================================
# 🚀 DÉMARRAGE RAPIDE
# ========================================================================

# 1. Setup initial (une seule fois)
python setup.py

# 2. Entraînement automatique (recommandé)
python pipeline.py --config BALANCED

# 3. Voir les résultats
tensorboard --logdir runs/


# ========================================================================
# 📚 ENTRAÎNEMENT
# ========================================================================

# Entraînement basique
python train.py

# Entraînement rapide (prototype)
python pipeline.py --config FAST

# Entraînement de haute qualité
python pipeline.py --config HIGH_QUALITY

# Entraînement pour production
python pipeline.py --config PRODUCTION

# Entraînement avec paramètres personnalisés
# Modifier config.py et lancer train.py


# ========================================================================
# 📊 ÉVALUATION
# ========================================================================

# Évaluer tous les modèles
python evaluate.py

# Évaluer un modèle spécifique
python evaluate.py models/yolov11m-seg_best_20250122_120000.pt

# Voir les résultats d'évaluation
# Fichiers JSON dans: evaluations/


# ========================================================================
# 🔍 CALCUL DU TAUX DE VIDES (VOID RATE)
# ========================================================================

# Calculer sur le test set
python void_rate_calculator.py

# Voir les résultats
# Fichiers JSON dans: void_rate_results/


# ========================================================================
# 🎯 INFÉRENCE
# ========================================================================

# Inférence sur le test set complet
python inference.py

# Inférence sur une image unique
python inference.py -i "path/to/image.jpg"

# Inférence sur un dossier
python inference.py -d "path/to/images/"

# Inférence avec seuil de confiance personnalisé
python inference.py -c 0.6 -d "path/to/images/"

# Sauvegarder les images annotées
python inference.py -d "path/to/images/" -a

# Utiliser un modèle spécifique
python inference.py -m "models/custom_model.pt" -d "path/to/images/"

# Sauvegarder les résultats JSON
python inference.py -d "path/to/images/" -o "results.json"

# Combinaison complète
python inference.py \
  -m "models/best_model.pt" \
  -d "path/to/images/" \
  -c 0.5 \
  -a \
  -o "inference_results.json"


# ========================================================================
# 🔄 PIPELINE AUTOMATIQUE
# ========================================================================

# Automatisation complète (recommandé pour production)
python pipeline.py

# Pipeline avec configuration spécifique
python pipeline.py --config HIGH_QUALITY

# Pipeline en sautant l'entraînement (utilise modèle existant)
python pipeline.py --skip-training

# Pipeline avec un modèle personnalisé
python pipeline.py --skip-training --model "models/my_model.pt"

# Pipeline complet sans inférence
python pipeline.py --skip-inference

# Pipeline pour les métadonnées uniquement
python pipeline.py --skip-training --skip-inference


# ========================================================================
# 📊 TENSORBOARD & MONITORING
# ========================================================================

# Lancer TensorBoard
tensorboard --logdir runs/

# Port personnalisé
tensorboard --logdir runs/ --port 6007

# Lancer en arrière-plan
tensorboard --logdir runs/ --daemon

# Arrêter TensorBoard
# Linux/macOS:
pkill -f tensorboard
# Windows (PowerShell):
Get-Process tensorboard | Stop-Process


# ========================================================================
# 📝 CONFIGURATION & PRÉSETS
# ========================================================================

# Voir toutes les configurations disponibles
python config.py

# Les presets disponibles sont:
# - QUICK_START
# - BALANCED_TRAINING (défaut)
# - HIGH_QUALITY_TRAINING
# - PRODUCTION_TRAINING
# - LIMITED_DATA_PRESET
# - MEMORY_EFFICIENT_PRESET


# ========================================================================
# 📂 GESTION DES FICHIERS
# ========================================================================

# Lister les modèles disponibles
ls models/

# Lister les résultats d'entraînement
ls runs/

# Lister les évaluations
ls evaluations/

# Lister les résultats d'inférence
ls inferences/

# Nettoyer les résultats temporaires
rm -rf runs/*.zip  # Sur Linux/macOS
Remove-Item runs/*.zip  # Sur Windows PowerShell


# ========================================================================
# 🔧 DÉPANNAGE
# ========================================================================

# Vérifier la version Python
python --version

# Vérifier l'installation CUDA
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0)}')"

# Vérifier YOLOv11
python -c "from ultralytics import YOLO; print(YOLO.__version__)"

# Vérifier les packages
pip list | grep -E "torch|ultralytics|opencv"

# Réinstaller les dépendances
pip install -r requirements.txt --upgrade

# Réinstaller CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118


# ========================================================================
# 🧹 NETTOYAGE
# ========================================================================

# Supprimer les modèles (sauf le meilleur)
rm models/*.pt  # À utiliser avec prudence!

# Nettoyer les logs
rm -rf logs/

# Nettoyer complètement
rm -rf runs/ evaluations/ inferences/ void_rate_results/


# ========================================================================
# 📊 INSPECTION DES DONNÉES
# ========================================================================

# Compter les images d'entraînement
find train/images -type f | wc -l

# Compter les images de validation
find valid/images -type f | wc -l

# Compter les images de test
find test/images -type f | wc -l

# Vérifier la structure du YAML
python -c "import yaml; print(yaml.safe_load(open('data.yaml')))"


# ========================================================================
# 📓 NOTEBOOK JUPYTER
# ========================================================================

# Lancer Jupyter Notebook
jupyter notebook

# Lancer Jupyter Lab
jupyter lab

# Ouvrir directement le notebook
jupyter notebook Training_Pipeline.ipynb


# ========================================================================
# 🐳 DOCKER (si besoin)
# ========================================================================

# Construire une image Docker (à adapter)
# docker build -t yolov11-segmentation .

# Lancer le conteneur
# docker run -it --gpus all yolov11-segmentation

# Utiliser avec volumes
# docker run -it --gpus all -v $(pwd):/workspace yolov11-segmentation


# ========================================================================
# ⚡ CONSEILS PERFORMANCE
# ========================================================================

# Augmenter batch size pour plus vite (plus de mémoire GPU)
# CONFIG["batch_size"] = 32

# Diminuer batch size pour moins de mémoire GPU
# CONFIG["batch_size"] = 4

# Utiliser demi-précision (FP16) si GPU supporte
# CONFIG["half"] = True

# Utiliser taille d'image plus petite pour inférence plus rapide
# python inference.py -d "path/" -c 0.5 -i 416


# ========================================================================
# 📈 RÉSULTATS & EXPORTS
# ========================================================================

# Exporter les résultats en CSV
# Les fichiers results.csv sont dans runs/*/

# Exporter les métriques JSON
# Les fichiers sont dans evaluations/ et inferences/

# Analyser les résultats (Python)
# import json
# with open('evaluations/evaluation_*.json') as f:
#     results = json.load(f)
#     print(results)


# ========================================================================
# 📝 NOTES
# ========================================================================

# • Toujours commencer par: python setup.py
# • Pipeline.py automatise tout: python pipeline.py
# • TensorBoard pour monitoring: tensorboard --logdir runs/
# • Consulter README.md pour documentation complète
# • Consulter QUICKSTART.py pour guide rapide
# • Les résultats sont dans: models/, evaluations/, inferences/

# ========================================================================
