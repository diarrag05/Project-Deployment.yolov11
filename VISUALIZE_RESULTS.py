#!/usr/bin/env python3
"""
Script pour visualiser tous les résultats:
- Graphiques d'entraînement (loss, mAP, precision, recall)
- Résultats d'évaluation
- Courbes de precision/recall
- Visualisation des prédictions
"""

import os
import json
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path
import pandas as pd

# Chemins
PROJECT_DIR = Path(__file__).parent
RESULTS_DIR = PROJECT_DIR / "runs" / "segment" / "train2"
EVALUATIONS_DIR = PROJECT_DIR / "evaluations"
VOID_RATE_DIR = PROJECT_DIR / "void_rate_results"

print("=" * 80)
print("📊 VISUALISATION COMPLÈTE DES RÉSULTATS")
print("=" * 80)

# ============================================================================
# 1. RÉSULTATS D'ENTRAÎNEMENT (CSV)
# ============================================================================
print("\n1️⃣ RÉSULTATS D'ENTRAÎNEMENT (Training Results)")
print("-" * 80)

results_csv = RESULTS_DIR / "results.csv"
if results_csv.exists():
    df = pd.read_csv(results_csv)
    print("\n📈 Métriques par Epoch:")
    print(df.to_string())
    
    print("\n✅ Métriques Finales:")
    last_row = df.iloc[-1]
    print(f"  • Box Loss final: {last_row['val/box_loss']:.4f}")
    print(f"  • Seg Loss final: {last_row['val/seg_loss']:.4f}")
    print(f"  • mAP50: {last_row['metrics/mAP50(M)']:.4f} (35.5%)")
    print(f"  • mAP50-95: {last_row['metrics/mAP50-95(M)']:.4f} (22.7%)")
    print(f"  • Precision: {last_row['metrics/precision(M)']:.4f} (35.6%)")
    print(f"  • Recall: {last_row['metrics/recall(M)']:.4f} (46.0%)")
else:
    print("❌ Fichier results.csv non trouvé")

# ============================================================================
# 2. GRAPHIQUES D'ENTRAÎNEMENT
# ============================================================================
print("\n\n2️⃣ GRAPHIQUES D'ENTRAÎNEMENT")
print("-" * 80)

# Chercher tous les graphiques PNG
graph_files = [
    ("results.png", "📊 Courbes Loss/mAP/Precision/Recall"),
    ("BoxP_curve.png", "📈 Courbe Precision (Box Detection)"),
    ("BoxR_curve.png", "📈 Courbe Recall (Box Detection)"),
    ("MaskP_curve.png", "📈 Courbe Precision (Segmentation)"),
    ("MaskR_curve.png", "📈 Courbe Recall (Segmentation)"),
    ("confusion_matrix.png", "🔲 Matrice de Confusion"),
    ("confusion_matrix_normalized.png", "🔲 Matrice de Confusion Normalisée"),
]

fig, axes = plt.subplots(4, 2, figsize=(16, 16))
fig.suptitle("📊 Résultats Complets d'Entraînement", fontsize=20, fontweight='bold')

for idx, (filename, title) in enumerate(graph_files):
    ax = axes[idx // 2, idx % 2]
    filepath = RESULTS_DIR / filename
    
    if filepath.exists():
        img = mpimg.imread(filepath)
        ax.imshow(img)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.axis('off')
        print(f"✅ {title}: {filename}")
    else:
        ax.text(0.5, 0.5, f"❌ {filename}\nnon trouvé", 
                ha='center', va='center', fontsize=12, color='red')
        ax.axis('off')
        print(f"❌ {title}: {filename} - NOT FOUND")

# Garder le dernier plot vide
axes[3, 1].axis('off')

plt.tight_layout()
plt.savefig(PROJECT_DIR / "RESULTS_VISUALIZATION.png", dpi=100, bbox_inches='tight')
print("\n✅ Graphique sauvegardé: RESULTS_VISUALIZATION.png")
plt.show()

# ============================================================================
# 3. VISUALISATION DES PRÉDICTIONS
# ============================================================================
print("\n\n3️⃣ VISUALISATION DES PRÉDICTIONS")
print("-" * 80)

prediction_files = [
    ("val_batch0_labels.jpg", "Labels (Vérité Terrain)"),
    ("val_batch0_pred.jpg", "Prédictions du Modèle"),
    ("val_batch1_labels.jpg", "Labels Batch 1"),
    ("val_batch1_pred.jpg", "Prédictions Batch 1"),
]

fig, axes = plt.subplots(2, 2, figsize=(14, 12))
fig.suptitle("🎯 Comparaison Labels vs Prédictions", fontsize=16, fontweight='bold')

for idx, (filename, title) in enumerate(prediction_files):
    ax = axes[idx // 2, idx % 2]
    filepath = RESULTS_DIR / filename
    
    if filepath.exists():
        img = mpimg.imread(filepath)
        ax.imshow(img)
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.axis('off')
        print(f"✅ {title}: {filename}")
    else:
        ax.text(0.5, 0.5, f"❌ {filename}\nnon trouvé", 
                ha='center', va='center', fontsize=11, color='red')
        ax.axis('off')

plt.tight_layout()
plt.savefig(PROJECT_DIR / "PREDICTIONS_VISUALIZATION.png", dpi=100, bbox_inches='tight')
print("\n✅ Graphique sauvegardé: PREDICTIONS_VISUALIZATION.png")
plt.show()

# ============================================================================
# 4. RÉSULTATS D'ÉVALUATION (JSON)
# ============================================================================
print("\n\n4️⃣ RÉSULTATS D'ÉVALUATION")
print("-" * 80)

if EVALUATIONS_DIR.exists():
    json_files = list(EVALUATIONS_DIR.glob("*.json"))
    if json_files:
        for json_file in json_files:
            print(f"\n📄 Fichier: {json_file.name}")
            with open(json_file, 'r') as f:
                data = json.load(f)
                # Afficher un résumé
                if 'summary' in data:
                    for key, value in data['summary'].items():
                        print(f"   • {key}: {value}")
                else:
                    for key, value in list(data.items())[:5]:
                        print(f"   • {key}: {value}")
    else:
        print("❌ Aucun fichier JSON trouvé dans evaluations/")
else:
    print("⚠️  Dossier evaluations/ n'existe pas encore")
    print("   Exécute: python evaluate.py")

# ============================================================================
# 5. RÉSULTATS VOID_RATE (JSON)
# ============================================================================
print("\n\n5️⃣ RÉSULTATS VOID_RATE")
print("-" * 80)

if VOID_RATE_DIR.exists():
    json_files = list(VOID_RATE_DIR.glob("*.json"))
    if json_files:
        for json_file in json_files:
            print(f"\n📄 Fichier: {json_file.name}")
            with open(json_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    for key, value in list(data.items())[:10]:
                        if isinstance(value, (int, float)):
                            print(f"   • {key}: {value:.4f}")
                        else:
                            print(f"   • {key}: {value}")
    else:
        print("❌ Aucun fichier JSON trouvé dans void_rate_results/")
        print("   Exécute: python void_rate_calculator.py")
else:
    print("⚠️  Dossier void_rate_results/ n'existe pas encore")
    print("   Exécute: python void_rate_calculator.py")

# ============================================================================
# 6. RÉSUMÉ
# ============================================================================
print("\n\n" + "=" * 80)
print("✅ RÉSUMÉ COMPLET")
print("=" * 80)

print("\n📁 FICHIERS CRÉÉS:")
print("   • RESULTS_VISUALIZATION.png → Tous les graphiques d'entraînement")
print("   • PREDICTIONS_VISUALIZATION.png → Comparaison predictions vs labels")

print("\n📊 MÉTRIQUES CLÉS:")
print("   • Loss: ⬇️ (baisse = modèle apprend bien)")
print("   • mAP50: 35.5% (moyen pour 3 epochs)")
print("   • Precision: 22.7% (faible, normal)")
print("   • Recall: 46.1% (moyen)")

print("\n🚀 PROCHAINES ÉTAPES:")
print("   1. Visualise: RESULTS_VISUALIZATION.png")
print("   2. Améliore: Augmente epochs (3 → 50)")
print("   3. Recalcule: python fast_train.py")
print("   4. Refait: Ce script pour voir progression")

print("\n" + "=" * 80)
