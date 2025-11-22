"""
🎯 COMMENCEZ ICI - GET STARTED GUIDE

Ce guide vous aidera à démarrer en 5 minutes!
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║          🎯 BIENVENUE - YOLOv11 SEGMENTATION PROJECT                       ║
║                                                                            ║
║                  Détection & Segmentation des Défauts                      ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 ÉTAPE 1: VÉRIFIER L'ENVIRONNEMENT (1 minute)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Exécutez ce script pour vérifier que tout fonctionne:

    python test_project.py

✓ Cela teste:
  • Les imports Python (torch, YOLOv11, etc.)
  • La présence des fichiers du projet
  • La présence du dataset

Si tout est OK, allez à l'étape 2!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 ÉTAPE 2: SETUP (5 minutes)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Installez les dépendances:

    python simple_setup.py

✓ Cela va:
  • Installer ultralytics, torch, opencv, etc.
  • Vérifier que YOLOv11 fonctionne
  • Créer les répertoires nécessaires

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 ÉTAPE 3: ENTRAÎNER (30-120 minutes selon votre PC)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Option A: Entraînement SIMPLE (recommandé pour tester)

    python simple_train.py

✓ 10 epochs, résultats rapides
✓ Idéal pour vérifier que ça marche

Option B: Entraînement COMPLET (meilleure qualité)

    python train.py

✓ 100 epochs, meilleurs résultats
✓ Plus long mais plus précis

Option C: Entraînement AUTOMATIQUE (tout inclus!)

    python pipeline.py --config BALANCED

✓ Entraînement + Évaluation + Inférence
✓ Configuration optimisée

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 ÉTAPE 4: VISUALISER LES RÉSULTATS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Voir les graphiques d'entraînement avec TensorBoard:

    tensorboard --logdir runs/

Puis ouvrir: http://localhost:6006

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ÉTAPE 5: INFÉRENCE & VOID_RATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Calculer le taux de vides sur le test set:

    python void_rate_calculator.py

ou faire de l'inférence:

    python inference.py -d "chemin/vers/images/"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 DOCUMENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

README.md              - Documentation complète
QUICKSTART.py         - Guide rapide
COMMANDS.md           - Tous les commandes
TROUBLESHOOTING.md    - Guide de dépannage
Training_Pipeline.ipynb - Notebook Jupyter interactif

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ J'AI UNE ERREUR!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Consultez: TROUBLESHOOTING.md

Ou exécutez le test:

    python test_project.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏭️ PROCHAINES ÉTAPES (après l'entraînement)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ✅ Évaluer les performances:
   python evaluate.py

2. ✅ Calculer le taux de vides:
   python void_rate_calculator.py

3. ✅ Faire de l'inférence:
   python inference.py

4. ✅ Utiliser le notebook interactif:
   jupyter notebook Training_Pipeline.ipynb

5. ✅ Affiner les paramètres:
   Modifier config.py et relancer

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 CONSEILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Commencez par simple_train.py (plus rapide pour tester)
✓ Utilisez pipeline.py pour la production
✓ Consultez README.md pour les détails
✓ TensorBoard est votre ami pour visualiser l'entraînement
✓ Lisez TROUBLESHOOTING.md si ça ne marche pas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 C'EST PARTI!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Exécutez ces 3 commandes:

    1️⃣  python test_project.py       (vérifier)
    2️⃣  python simple_setup.py       (installer)
    3️⃣  python simple_train.py       (entraîner)

Puis visualiser:

    tensorboard --logdir runs/

✨ Bon entraînement! ✨
""")
