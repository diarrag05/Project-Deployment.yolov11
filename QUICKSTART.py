"""
GUIDE DE DÉMARRAGE RAPIDE
Commence ici si tu es nouveau!
"""

# ============================================================================
# 🚀 DÉMARRAGE RAPIDE EN 5 ÉTAPES
# ============================================================================

# ÉTAPE 1: Installation (5 minutes)
# ─────────────────────────────────────────────────────────────────────────

"""
1. Ouvre PowerShell/Terminal dans le dossier du projet
2. Exécute:
   
   python setup.py
   
   Cela va installer toutes les dépendances nécessaires.
"""

# ÉTAPE 2: Entraîner le modèle (30-120 minutes selon GPU)
# ─────────────────────────────────────────────────────────────────────────

"""
Option A: Pipeline automatique (recommandé)

    python pipeline.py --config BALANCED
    
    Cela va:
    - Entraîner le modèle
    - L'évaluer
    - Calculer le taux de vides sur le test set
    - Sauvegarder tout automatiquement

Option B: Juste l'entraînement

    python train.py
    
    Les résultats seront sauvegardés dans: runs/

Option C: Avec configuration personnalisée

    python pipeline.py --config PRODUCTION  # Pour meilleure qualité
    python pipeline.py --config FAST        # Pour prototype rapide
"""

# ÉTAPE 3: Vérifier les résultats d'entraînement
# ─────────────────────────────────────────────────────────────────────────

"""
Visualiser les graphes d'entraînement avec TensorBoard:

    tensorboard --logdir runs/
    
Puis ouvre: http://localhost:6006

Ou regarder le fichier CSV directement:

    runs/yolov11m-seg_YYYYMMDD_HHMMSS/results.csv
"""

# ÉTAPE 4: Évaluer le modèle
# ─────────────────────────────────────────────────────────────────────────

"""
Évaluer les métriques (mAP, precision, recall, IoU):

    python evaluate.py
    
Résultats sauvegardés dans: evaluations/
"""

# ÉTAPE 5: Inférence et calcul du taux de vides
# ─────────────────────────────────────────────────────────────────────────

"""
Calculer le void_rate sur le test set:

    python void_rate_calculator.py
    
ou utiliser l'inférence complète:

    python inference.py
    python inference.py -i "chemin/vers/image.jpg"
    python inference.py -d "chemin/vers/dossier/"

Résultats sauvegardés dans: inferences/
"""

# ============================================================================
# 📊 RÉSULTATS ET FICHIERS GÉNÉRÉS
# ============================================================================

"""
ENTRAÎNEMENT:
- runs/yolov11m-seg_*/weights/best.pt     ← Meilleur modèle
- runs/yolov11m-seg_*/results.csv         ← Métriques par epoch
- runs/yolov11m-seg_*/events.out.tfevents ← Logs TensorBoard
- models/yolov11m-seg_best_*.pt           ← Copie du meilleur

ÉVALUATION:
- evaluations/evaluation_*.json           ← Résultats d'évaluation

INFÉRENCE & VOID_RATE:
- inferences/inference_*.json             ← Résultats d'inférence
- inferences/annotated_*.jpg              ← Images avec prédictions
- void_rate_results/void_rate_*.json      ← Résultats void_rate
"""

# ============================================================================
# 🔧 COMMANDES UTILES
# ============================================================================

"""
# Voir toutes les commandes disponibles
python train.py --help
python evaluate.py --help
python inference.py --help

# Entraînement avec modèle plus petit (plus rapide, CPU)
python pipeline.py --config FAST

# Entraînement haute qualité (meilleure précision)
python pipeline.py --config HIGH_QUALITY

# Sauter l'entraînement, juste évaluation/inférence
python pipeline.py --skip-training -m models/best.pt

# Inférence sur une image spécifique
python inference.py -i "path/to/image.jpg" -a
# -a pour sauvegarder l'image annotée

# Inférence avec seuil de confiance plus élevé
python inference.py -c 0.7 -d "path/to/images/"

# Voir les configurations disponibles
python config.py
"""

# ============================================================================
# 📈 INTERPRÉTER LES RÉSULTATS
# ============================================================================

"""
TAUX DE VIDES (void_rate):
- 0-5%:   Composant presque parfait
- 5-15%:  Bon composant
- 15-30%: Composant acceptable
- 30%+:   Composant défectueux

MÉTRIQUES D'ENTRAÎNEMENT:
- Loss bas = Modèle apprend bien
- mAP50 > 0.80 = Détection de bonne qualité
- Precision > 0.90 = Peu de faux positifs
- Recall > 0.85 = Peu de faux négatifs

RÉSULTATS JSON:
{
    "void_rate": 15.35,              ← Pourcentage de vides
    "chip_area_pixels": 98000,       ← Aire du composant
    "hole_area_pixels": 15000,       ← Aire des trous
    "num_chips": 1,
    "num_holes": 3,
    "detections": [...]              ← Détails des détections
}
"""

# ============================================================================
# 🐛 TROUBLESHOOTING
# ============================================================================

"""
❌ "CUDA out of memory"
→ Réduire batch_size:
  CONFIG = {"batch_size": 8}

❌ "GPU not found"
→ Vérifier CUDA:
  python -c "import torch; print(torch.cuda.is_available())"

❌ "Modèle ne converge pas"
→ Augmenter epochs et réduire learning_rate:
  CONFIG = {"epochs": 150, "learning_rate": 0.0005}

❌ "TensorBoard ne démarre pas"
→ Essayer:
  tensorboard --logdir . --port 6007

❌ "Images pas trouvées en inférence"
→ Vérifier le chemin:
  python inference.py -d "C:/path/to/images/"  # Utiliser / ou \\
"""

# ============================================================================
# 📚 DOCUMENTATION COMPLÈTE
# ============================================================================

"""
Voir README.md pour la documentation détaillée:
- Configuration complète
- Paramètres avancés
- Tous les scripts
- Ressources supplémentaires
"""

# ============================================================================
# ✨ RÉSUMÉ DES FICHIERS
# ============================================================================

"""
setup.py                  ← Configuration du projet
train.py                  ← Entraîner le modèle
evaluate.py               ← Évaluer les performances
void_rate_calculator.py   ← Calculer le taux de vides
inference.py              ← Inférence sur des images
pipeline.py               ← Tout automatiquement
config.py                 ← Configurations prédéfinies
README.md                 ← Documentation complète
QUICKSTART.py             ← Ce fichier (guide rapide)
"""

# ============================================================================
# 💡 CONSEILS
# ============================================================================

"""
✓ Commencer par setup.py pour vérifier que tout fonctionne
✓ Utiliser pipeline.py pour une solution complète automatique
✓ Consulter les logs dans logs/ pour debugger
✓ TensorBoard est très utile pour monitorer l'entraînement
✓ Sauvegarder régulièrement les modèles entraînés
✓ Tester sur le test set avant production
✓ Ajuster les seuils de confiance selon vos besoins
"""

# ============================================================================

if __name__ == "__main__":
    print(__doc__)
