#!/usr/bin/env python3
"""
Script pour afficher les SEGMENTATIONS des HOLES et les courbes MASK
Visualisation complète de ce que le modèle a appris
"""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
RESULTS_DIR = PROJECT_DIR / "runs" / "segment" / "train2"

print("\n" + "="*80)
print("🎯 VISUALISATION DES SEGMENTATIONS - HOLES ET MASKS")
print("="*80)

# ============================================================================
# 1. COURBES DE SEGMENTATION (MASK CURVES)
# ============================================================================
print("\n\n1️⃣ COURBES DE SEGMENTATION (MASK Precision/Recall)")
print("-"*80)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("📊 Segmentation Metrics - MASK (Holes Detection)", fontsize=16, fontweight='bold')

mask_files = [
    ("MaskP_curve.png", "Precision Curve - Segmentation", 0, 0),
    ("MaskR_curve.png", "Recall Curve - Segmentation", 0, 1),
    ("MaskF1_curve.png", "F1 Score Curve - Segmentation", 1, 0),
    ("MaskPR_curve.png", "Precision-Recall Curve", 1, 1),
]

for filename, title, row, col in mask_files:
    filepath = RESULTS_DIR / filename
    ax = axes[row, col]
    
    if filepath.exists():
        img = mpimg.imread(filepath)
        ax.imshow(img)
        ax.set_title(title, fontsize=11, fontweight='bold', color='green')
        ax.axis('off')
        print(f"✅ {title}")
    else:
        ax.text(0.5, 0.5, f"❌ {filename}\nnon trouvé", 
                ha='center', va='center', fontsize=11, color='red')
        ax.axis('off')
        print(f"❌ {title}")

plt.tight_layout()
plt.savefig(PROJECT_DIR / "MASK_CURVES_VISUALIZATION.png", dpi=100, bbox_inches='tight')
print("\n✅ Sauvegardé: MASK_CURVES_VISUALIZATION.png")
plt.show()

# ============================================================================
# 2. PRÉDICTIONS ET LABELS - SEGMENTATION VISUELLE
# ============================================================================
print("\n\n2️⃣ VISUALISATION DES SEGMENTATIONS (Predictions vs Labels)")
print("-"*80)

fig, axes = plt.subplots(3, 2, figsize=(14, 15))
fig.suptitle("🎯 Prédictions vs Labels - Segmentation des HOLES", 
             fontsize=16, fontweight='bold')

pred_labels_pairs = [
    ("val_batch0_labels.jpg", "val_batch0_pred.jpg", "Batch 0"),
    ("val_batch1_labels.jpg", "val_batch1_pred.jpg", "Batch 1"),
    ("val_batch2_labels.jpg", "val_batch2_pred.jpg", "Batch 2"),
]

for idx, (labels_file, pred_file, batch_name) in enumerate(pred_labels_pairs):
    # Labels (Vérité Terrain)
    labels_path = RESULTS_DIR / labels_file
    ax_labels = axes[idx, 0]
    
    if labels_path.exists():
        img = mpimg.imread(labels_path)
        ax_labels.imshow(img)
        ax_labels.set_title(f"{batch_name} - LABELS (Vérité Terrain)", 
                           fontsize=10, fontweight='bold', color='blue')
        ax_labels.axis('off')
        print(f"✅ {labels_file}")
    else:
        ax_labels.text(0.5, 0.5, f"❌ {labels_file}\nnon trouvé", 
                      ha='center', va='center', fontsize=10, color='red')
        ax_labels.axis('off')
    
    # Predictions (Ce que le modèle a prédit)
    pred_path = RESULTS_DIR / pred_file
    ax_pred = axes[idx, 1]
    
    if pred_path.exists():
        img = mpimg.imread(pred_path)
        ax_pred.imshow(img)
        ax_pred.set_title(f"{batch_name} - PRÉDICTIONS (Modèle)", 
                         fontsize=10, fontweight='bold', color='green')
        ax_pred.axis('off')
        print(f"✅ {pred_file}")
    else:
        ax_pred.text(0.5, 0.5, f"❌ {pred_file}\nnon trouvé", 
                    ha='center', va='center', fontsize=10, color='red')
        ax_pred.axis('off')

plt.tight_layout()
plt.savefig(PROJECT_DIR / "SEGMENTATION_PREDICTIONS_VISUALIZATION.png", dpi=100, bbox_inches='tight')
print("\n✅ Sauvegardé: SEGMENTATION_PREDICTIONS_VISUALIZATION.png")
plt.show()

# ============================================================================
# 3. IMAGES D'ENTRAÎNEMENT AVEC MASKS
# ============================================================================
print("\n\n3️⃣ IMAGES D'ENTRAÎNEMENT AVEC MASKS SEGMENTÉS")
print("-"*80)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("📸 Training Batches avec Segmentation des Holes", 
             fontsize=16, fontweight='bold')

train_files = [
    ("train_batch0.jpg", "Training Batch 0", 0, 0),
    ("train_batch1.jpg", "Training Batch 1", 0, 1),
    ("train_batch2.jpg", "Training Batch 2", 1, 0),
    ("labels.jpg", "Dataset Labels Overview", 1, 1),
]

for filename, title, row, col in train_files:
    filepath = RESULTS_DIR / filename
    ax = axes[row, col]
    
    if filepath.exists():
        img = mpimg.imread(filepath)
        ax.imshow(img)
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.axis('off')
        print(f"✅ {title}")
    else:
        ax.text(0.5, 0.5, f"❌ {filename}\nnon trouvé", 
                ha='center', va='center', fontsize=11, color='red')
        ax.axis('off')

plt.tight_layout()
plt.savefig(PROJECT_DIR / "TRAINING_VISUALIZATION.png", dpi=100, bbox_inches='tight')
print("\n✅ Sauvegardé: TRAINING_VISUALIZATION.png")
plt.show()

# ============================================================================
# 4. RÉSUMÉ ET EXPLICATION
# ============================================================================
print("\n\n" + "="*80)
print("✅ EXPLICATION DES VISUALISATIONS")
print("="*80)

print("""
🎯 CE QUE TU VOIS:

1️⃣ MASK CURVES (Courbes de Segmentation):
   • Precision: Quand le modèle dit "c'est un hole", il a raison?
   • Recall: Le modèle trouve combien de holes réels?
   • F1 Score: Combinaison équilibrée de precision et recall
   • PR Curve: Relation entre precision et recall

2️⃣ LABELS vs PRÉDICTIONS (Segmentation):
   • BLEU (Labels): Ce qui est vraiment dans l'image (vérité terrain)
   • VERT (Prédictions): Ce que le modèle a détecté
   • ROUGE: Les erreurs (faux positifs/négatifs)
   • JAUNE/ORANGE: Les segmentations correctes

3️⃣ TRAINING BATCHES:
   • Montre les images d'entraînement avec les masks
   • Les boîtes = localisation (detection)
   • Les polygones/masks = segmentation précise des holes
   • Les couleurs = classes (chip vs hole)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 INTERPRÉTATION DES RÉSULTATS:

✅ Loss qui baisse → Le modèle apprend bien
✅ Precision/Recall qui montent → Le modèle s'améliore
✅ Masks qui correspondent → Segmentation correcte
⚠️  Scores encore faibles → Normal (3 epochs seulement)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 PROCHAINES ÉTAPES:

1. Visualise les 3 fichiers PNG créés:
   • MASK_CURVES_VISUALIZATION.png
   • SEGMENTATION_PREDICTIONS_VISUALIZATION.png
   • TRAINING_VISUALIZATION.png

2. Observe comment la segmentation s'améliore:
   • Batch 0: Premières tentatives
   • Batch 1: Meilleure localisation
   • Batch 2: Plus de précision

3. Pour améliorer la qualité:
   • Augmente epochs: 3 → 50
   • Ajoute plus d'images: 97 → 500+
   • Utilise GPU si possible

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 VOID_RATE = Automatique après!

Une fois que tu lances l'inférence:
   • Le modèle segmente les holes
   • Compte les pixels des holes
   • Compte les pixels du chip
   • void_rate = (holes / chip) × 100

Exemple:
   • Chip = 10,000 pixels
   • Holes = 1,500 pixels
   • void_rate = 15%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

print("\n✅ TOUT EST PRÊT! Ouvre les PNG pour voir les segmentations!")
