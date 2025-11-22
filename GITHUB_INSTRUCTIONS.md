# 📤 INSTRUCTIONS POUR GITHUB

## ✅ Fichiers à pousser sur GitHub

```bash
# 1. Initialise le git (si pas déjà fait)
git init
git add .
git commit -m "Initial commit: YOLOv8 Segmentation Pipeline"

# 2. Ajoute le remote (remplace par ton URL)
git remote add origin https://github.com/tonusername/Project-Deployment.yolov11.git

# 3. Pousse sur GitHub
git branch -M main
git push -u origin main
```

---

## 📁 CE QUI EST INCLUS

### ✅ À pousser (important)
- ✅ Tous les scripts Python (train, inference, evaluate, etc.)
- ✅ Fichiers .bat (MENU.bat, 1_CHECK.bat, etc.)
- ✅ Fichiers de configuration (data.yaml, config.py, requirements.txt)
- ✅ Documentation (README.md, DEPLOYMENT.md, QUICKSTART.py, etc.)
- ✅ .gitignore (pour exclure les gros fichiers)

### ❌ À NE PAS pousser (lourd/généré)
- ❌ `yolov8n-seg.pt` (poids pré-entraînés - 6.7 MB) → Téléchargé auto
- ❌ `models/yolov8n-seg_trained.pt` (poids entraînés) → Régénéré à chaque entraînement
- ❌ `runs/` (résultats d'entraînement) → Généré à l'exécution
- ❌ `inferences/` → Généré à l'exécution
- ❌ `evaluations/` → Généré à l'exécution
- ❌ `void_rate_results/` → Généré à l'exécution
- ❌ `__pycache__/` → Fichiers compilés Python

**→ Le .gitignore gère tout cela automatiquement !**

---

## 🚀 ÉTAPES FINALES AVANT GITHUB

### 1. Nettoie les fichiers générés (facultatif)
```bash
# Supprime les résultats précédents
Remove-Item models/yolov8n-seg_trained.pt -Force
Remove-Item runs -Recurse -Force
Remove-Item inferences -Recurse -Force
Remove-Item evaluations -Recurse -Force
Remove-Item void_rate_results -Recurse -Force
```

### 2. Vérifie que tout est OK
```bash
python CHECK.py
```

### 3. Crée le repo sur GitHub
- Ouvre https://github.com/new
- Crée un repo nommé `Project-Deployment.yolov11`
- NE coche PAS "Initialize with README" (tu en as déjà un)
- Clique "Create repository"

### 4. Pousse le code
```bash
cd "c:\Users\mdiia\OneDrive\Bureau\AIVANCITY\Cours\PGE4\Deployment n Maintenance\Project-Deployment.yolov11"

git config user.name "Ton Nom"
git config user.email "ton.email@gmail.com"

git init
git add .
git commit -m "🚀 YOLOv8 Segmentation Pipeline - Initial commit"
git branch -M main
git remote add origin https://github.com/tonusername/Project-Deployment.yolov11.git
git push -u origin main
```

---

## 📊 FICHIERS À VÉRIFIER AVANT PUSH

```
✅ CHECK.py
✅ requirements.txt
✅ data.yaml
✅ config.py
✅ train.py
✅ fast_train.py
✅ inference.py
✅ evaluate.py
✅ void_rate_calculator.py
✅ pipeline.py
✅ README.md
✅ DEPLOYMENT.md
✅ QUICKSTART.py
✅ GET_STARTED.py
✅ COMMANDS.md
✅ TROUBLESHOOTING.md
✅ README_BATCH_FILES.md
✅ 1_CHECK.bat
✅ 2_INFERENCE.bat
✅ 3_VOID_RATE.bat
✅ 4_EVALUATE.bat
✅ 5_TRAIN.bat
✅ MENU.bat
✅ START_TENSORBOARD.bat
✅ .gitignore
✅ test/images/ (images de test)
✅ train/images/ + train/labels/ (dataset)
✅ valid/images/ + valid/labels/ (validation)
```

---

## 🔐 CONFIGURATION GIT (Premiers pas)

Si c'est ta première fois avec Git :

```bash
# Configure Git globalement
git config --global user.name "Ton Nom Complet"
git config --global user.email "ton.email@gmail.com"

# Génère une clé SSH (optionnel mais recommandé)
ssh-keygen -t ed25519 -C "ton.email@gmail.com"
```

---

## 📝 MESSAGE DE COMMIT RECOMMANDÉ

```
🚀 YOLOv8 Segmentation Pipeline - Initial Release

Features:
- ✅ YOLOv8n segmentation training (ultra-fast)
- ✅ Automatic void rate calculation
- ✅ Model evaluation (mAP, Precision, Recall, IoU)
- ✅ Inference on single images, batches, or folders
- ✅ TensorBoard monitoring
- ✅ Windows .bat files for easy use
- ✅ Complete documentation

Specifications:
- Model: YOLOv8n-seg (6.4 MB, CPU-compatible)
- Dataset: 2 classes (chip, hole), 97 images
- Training: ~50 seconds (3 epochs)
- Framework: PyTorch 2.1.1 + Ultralytics

Ready for deployment and maintenance!
```

---

## 🎯 APRÈS LE PUSH

### Checklist finale
- [ ] Repo créé sur GitHub
- [ ] Code poussé avec succès
- [ ] README.md s'affiche correctement
- [ ] Tous les fichiers .py sont visibles
- [ ] Fichiers .bat visibles
- [ ] Documentation accessible

### Partage du repo
```
https://github.com/tonusername/Project-Deployment.yolov11
```

**Remplace `tonusername` par ton vrai username GitHub !**

---

## 🆘 PROBLÈMES COURANTS

### "Authentication failed"
```bash
# Utilise une Personal Access Token au lieu du mot de passe
# https://github.com/settings/tokens
```

### "Please tell me who you are"
```bash
git config user.name "Ton Nom"
git config user.email "ton.email@gmail.com"
```

### "Fatal: not a git repository"
```bash
git init
```

### Les fichiers .pt sont énormes
```bash
# Ajoute les au .gitignore (déjà fait!)
# Ils seront téléchargés auto à la première exécution
```

---

## 📌 NOTES IMPORTANTES

1. **Les modèles .pt ne sont PAS dans le repo** 
   - Ils se téléchargent automatiquement à la première exécution
   - Gestion automatique via `.gitignore`

2. **Le dataset est inclus** (petit dataset = OK pour GitHub)
   - `train/images/` : 66 images
   - `valid/images/` : 20 images
   - `test/images/` : 11 images

3. **Les résultats d'entraînement ne sont PAS stockés**
   - `runs/`, `inferences/`, `evaluations/`, `void_rate_results/`
   - Tous générés à l'exécution

4. **Documentation complète**
   - README.md : Vue d'ensemble
   - DEPLOYMENT.md : Guide complet
   - QUICKSTART.py : Démonstration interactive
   - TROUBLESHOOTING.md : Solutions d'erreurs

---

**Projet prêt pour GitHub ! 🚀**

Dernière mise à jour : 22/11/2025
