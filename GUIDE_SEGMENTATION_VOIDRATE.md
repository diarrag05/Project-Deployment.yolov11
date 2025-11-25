# 🎯 GUIDE COMPLET - Visualisation Segmentation + Void_Rate

## **PARTIE 1: Voir les graphiques de segmentation**

### **Option 1: Depuis VS Code (Facile!)**

1. Ouvre le dossier: `runs/segment/train2/`
2. Tu verras les fichiers PNG:
   - ✅ `val_batch0_labels.jpg` → Vérité terrain (labels originaux)
   - ✅ `val_batch0_pred.jpg` → Prédictions du modèle
   - ✅ `val_batch1_labels.jpg` → Batch 2
   - ✅ `val_batch1_pred.jpg` → Prédictions Batch 2
   - ✅ `confusion_matrix.png` → Matrice de confusion
   - ✅ `MaskP_curve.png` → Courbe Precision segmentation
   - ✅ `MaskR_curve.png` → Courbe Recall segmentation

3. Double-clic sur chaque image pour voir la segmentation!

### **Ce que tu vas voir:**
```
LABELS (Bleu/Original):
- Le chip en gris clair
- Les holes en noir
- Les contours précis (vérité terrain)

PRÉDICTIONS (Vert/Modèle):
- Ce que le modèle a détecté
- Les boîtes bleues = holes détectés
- Les polygones = segmentation des holes
- CYAN = Prédictions correctes
- ROUGE = Erreurs/faux positifs
```

---

## **PARTIE 2: Calculer le VOID_RATE**

### **Option 1: Script automatique (Recommandé)**

**Étape 1:** Double-clic sur `3_VOID_RATE.bat`

C'est tout! Le script va:
1. ✅ Charger le modèle entraîné
2. ✅ Prédire sur toutes les images du dossier `test/images/`
3. ✅ Créer les masks (hole + chip)
4. ✅ Compter les pixels
5. ✅ Calculer void_rate = (holes_pixels / chip_pixels) × 100
6. ✅ Sauvegarder résultats dans `void_rate_results/`

**Résultat attendu:**
```json
{
  "image_name": "04_JPG.rf.4935d8061ad1c13154d00829b507412c.jpg",
  "chip_area_pixels": 45230,
  "holes_area_pixels": 6845,
  "void_rate": 15.13
}
```

### **Option 2: Inférence + Void_rate intégrés**

**Étape 1:** Double-clic sur `2_INFERENCE.bat`

Le script va:
1. ✅ Demander le chemin de l'image
2. ✅ Faire la prédiction
3. ✅ Calculer automatiquement le void_rate
4. ✅ Afficher le résultat JSON

**Exemple:**
```
Entrez le chemin de l'image: test/images/04_JPG.rf.4935d8061ad1c13154d00829b507412c.jpg

✅ Prédiction réussie!
  • Holes détectés: 12
  • Chip trouvé: Oui
  • Void rate: 15.13%
```

---

## **PARTIE 3: Visualiser les résultats VOID_RATE**

### **Étape 1: Lancer le calcul**
```bash
Double-clic: 3_VOID_RATE.bat
```

### **Étape 2: Consulter les résultats**

Les résultats sont dans: `void_rate_results/`

**Fichiers créés:**
- `void_rate_results_YYYYMMDD_HHMMSS.json` → Résultats détaillés
- `void_rate_statistics_YYYYMMDD_HHMMSS.json` → Statistiques globales

**Exemple de JSON:**
```json
{
  "results": [
    {
      "image": "image1.jpg",
      "chip_pixels": 45230,
      "holes_pixels": 6845,
      "void_rate": 15.13
    },
    {
      "image": "image2.jpg",
      "chip_pixels": 52100,
      "holes_pixels": 8342,
      "void_rate": 16.01
    }
  ],
  "statistics": {
    "mean_void_rate": 15.57,
    "min_void_rate": 15.13,
    "max_void_rate": 16.01,
    "std_void_rate": 0.44,
    "total_images": 2
  }
}
```

---

## **PARTIE 4: Formule VOID_RATE Expliquée**

### **La formule exacte demandée:**
```
void_rate = (somme des aires de trous / aire du composant) × 100
void_rate = (pixels_holes / pixels_chip) × 100
```

### **Pas à pas:**

**Exemple avec une image:**

1. **Modèle prédit** → Crée 2 masks:
   ```
   mask_chip (classe 0):
   ████████████████████████████
   ████████████████████████████
   ████████████████████████████
   (tous les pixels du composant)

   mask_holes (classe 1):
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░
   ░░░░██████░░░░░░██████░░░░░░
   ░░░░██████░░░░░░██████░░░░░░
   (seulement les trous)
   ```

2. **Compte les pixels:**
   ```
   chip_pixels = 10,000 pixels
   holes_pixels = 1,500 pixels
   ```

3. **Calcule le ratio:**
   ```
   void_rate = (1,500 / 10,000) × 100 = 15%
   ```

4. **Interprétation:**
   ```
   ✅ 15% de vide → Composant de bonne qualité
   ⚠️ 30% de vide → Composant dégradé
   ❌ 50%+ de vide → Composant défectueux
   ```

---

## **PARTIE 5: Où voir les résultats finaux?**

### **Fichiers de résultats:**

```
📁 Project-Deployment.yolov11/
├── 📁 void_rate_results/           ← RÉSULTATS VOID_RATE
│   ├── void_rate_results_*.json
│   └── void_rate_statistics_*.json
│
├── 📁 inferences/                  ← RÉSULTATS INFÉRENCE
│   └── *.json (prédictions détaillées)
│
├── 📁 evaluations/                 ← RÉSULTATS ÉVALUATION
│   ├── evaluation_*.json
│   └── summary_*.json
│
└── 📁 runs/segment/train2/         ← RÉSULTATS ENTRAÎNEMENT
    ├── val_batch0_labels.jpg       ← Labels (vérité terrain)
    ├── val_batch0_pred.jpg         ← Prédictions modèle
    ├── MaskP_curve.png             ← Courbe Precision
    ├── MaskR_curve.png             ← Courbe Recall
    └── results.csv                 ← Métriques par epoch
```

---

## **PARTIE 6: Commandes rapides**

### **Voir les segmentations:**
```bash
# Ouvre le dossier dans VS Code
code runs/segment/train2/

# Puis double-clic sur les images pour les voir
```

### **Calculer void_rate sur toutes les images:**
```bash
# Double-clic
3_VOID_RATE.bat
```

### **Calculer void_rate sur une image spécifique:**
```bash
# Double-clic
2_INFERENCE.bat
# Puis entre le chemin: test/images/mon_image.jpg
```

### **Voir TensorBoard (monitoring entraînement):**
```bash
# Double-clic
START_TENSORBOARD.bat
# Va à: http://localhost:6006/
```

---

## **PARTIE 7: Résumé COMPLET du workflow**

### **Étape 1: Entraînement ✅ (Déjà fait)**
```
Input: 97 images (66 train + 20 val + 11 test)
       ↓
Process: YOLOv8n-seg entraîné 3 epochs
       ↓
Output: models/yolov8n-seg_trained.pt (6.4 MB)
```

### **Étape 2: Segmentation ✅ (Déjà fait)**
```
Input: Image d'une puce (chip)
       ↓
Process: Modèle détecte chip + holes
       ↓
Output: 2 masks (chip_mask + holes_mask)
```

### **Étape 3: Calcul void_rate ✅ (À exécuter)**
```
Input: masks créés par étape 2
       ↓
Process: Compte pixels holes / pixels chip
       ↓
Output: void_rate = X%
```

### **Étape 4: Résultats ✅ (À consulter)**
```
JSON avec:
- Image name
- Chip area (pixels)
- Holes area (pixels)
- Void rate (%)
```

---

## **QUICK START (3 étapes)**

### **1. Voir les prédictions du modèle:**
```bash
Ouvre: runs/segment/train2/
Voir: val_batch0_pred.jpg, val_batch1_pred.jpg
```

### **2. Calculer void_rate sur toutes les images:**
```bash
Double-clic: 3_VOID_RATE.bat
Attends: ~2-5 minutes
```

### **3. Voir les résultats:**
```bash
Ouvre: void_rate_results/
Vois: JSON avec void_rate% pour chaque image
```

---

**✅ C'EST TOUT! Le modèle va faire tout automatiquement!**
