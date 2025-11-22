"""
🎯 YOLOv11 SEGMENTATION - BIENVENUE!

Bonjour! Ce projet offre une solution complète pour:

1. ✅ ENTRAÎNER    YOLOv11-segmentation sur vos données
2. ✅ ÉVALUER      Les performances (mAP, precision, recall)
3. ✅ CALCULER     Le taux de vides (void_rate)
4. ✅ INFÉRER      Sur de nouvelles images

═════════════════════════════════════════════════════════════════════════════

🚀 DÉMARRAGE EN 3 ÉTAPES:

    1️⃣  Ouvre PowerShell/Terminal ici
    
    2️⃣  Exécute:
        python setup.py
        
    3️⃣  Lance l'entraînement:
        python pipeline.py --config BALANCED
        
    ✨ Tout est automatique!

═════════════════════════════════════════════════════════════════════════════

📚 FICHIERS IMPORTANTS:

    readme.md               ← Documentation complète
    QUICKSTART.py          ← Guide de démarrage rapide
    COMMANDS.md            ← Tous les commandes utiles
    Training_Pipeline.ipynb ← Notebook Jupyter interactif
    PROJECT_SUMMARY.md     ← Synthèse du projet

═════════════════════════════════════════════════════════════════════════════

📋 FICHIERS PRINCIPAUX:

    train.py               ← Entraîner le modèle
    evaluate.py            ← Évaluer les performances
    void_rate_calculator.py ← Calculer void_rate
    inference.py           ← Inférence sur des images
    pipeline.py            ← Tout automatiquement
    config.py              ← Configurations prédéfinies

═════════════════════════════════════════════════════════════════════════════

🎓 WORKFLOW RECOMMANDÉ:

    # 1. Installation (5 minutes)
    python setup.py

    # 2. Entraînement (30-120 minutes)
    python pipeline.py --config BALANCED

    # 3. Voir les résultats
    tensorboard --logdir runs/
    
    # 4. Inférence sur nouvelles images
    python inference.py -d "path/to/images/"

═════════════════════════════════════════════════════════════════════════════

💡 CONSEILS:

    ✓ Lire README.md pour comprendre la structure
    ✓ Utiliser pipeline.py pour l'automatisation
    ✓ Consulter config.py pour les présets
    ✓ TensorBoard utile pour visualiser l'entraînement
    ✓ Vérifier setup.py fonctionne bien d'abord

═════════════════════════════════════════════════════════════════════════════

🔗 RESSOURCES:

    YOLOv11: https://docs.ultralytics.com/
    PyTorch: https://pytorch.org/
    TensorBoard: https://www.tensorflow.org/tensorboard

═════════════════════════════════════════════════════════════════════════════

Bon courage! 🚀 C'est parti!
"""

if __name__ == "__main__":
    print(__doc__)
