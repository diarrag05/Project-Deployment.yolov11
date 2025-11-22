# 🆘 GUIDE DE DÉPANNAGE - ERREURS COURANTS

## ✅ DÉMARRAGE RECOMMANDÉ

Exécutez ces commandes dans l'ordre:

```bash
# 1. Test du projet (vérifier tout)
python test_project.py

# 2. Setup simple (installer dépendances)
python simple_setup.py

# 3. Entraîner (version simple pour tester)
python simple_train.py

# 4. Si ça marche, utiliser le pipeline complet
python pipeline.py --config BALANCED
```

---

## ❌ ERREURS COMMUNES & SOLUTIONS

### 1. **ModuleNotFoundError: No module named 'ultralytics'**

**Cause**: YOLOv11 n'est pas installé

**Solution**:
```bash
pip install ultralytics
# ou
python simple_setup.py
```

---

### 2. **ModuleNotFoundError: No module named 'torch'**

**Cause**: PyTorch n'est pas installé

**Solution**:
```bash
# CPU uniquement
pip install torch torchvision

# GPU (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

### 3. **CUDA out of memory**

**Cause**: Le GPU n'a pas assez de mémoire

**Solution**: Réduire la taille du batch dans `config.py` ou `simple_train.py`:
```python
config = {
    "batch": 8,  # Réduire de 16 à 8
    "imgsz": 416,  # Ou réduire la taille des images
}
```

---

### 4. **FileNotFoundError: data.yaml**

**Cause**: Le fichier `data.yaml` est manquant

**Solution**: Vérifier que `data.yaml` existe dans le répertoire du projet
```bash
ls data.yaml
```

---

### 5. **Import error dans pipeline.py**

**Cause**: Les imports sont mal configurés

**Solution**: Utiliser les scripts simplifiés à la place:
```bash
python simple_train.py       # Au lieu de python train.py
python pipeline.py            # Utilise train.py automatiquement
```

---

### 6. **No CUDA device found**

**Cause**: GPU n'est pas détecté

**Solution**: C'est OK, utilisez le CPU:
```python
# Automatiquement détecté par les scripts
# Si vous voulez forcer CPU:
# device = "cpu"
```

---

### 7. **Permission denied**

**Cause**: Fichier verrouillé ou droits d'accès insuffisant

**Solution**:
```bash
# Fermer tous les processus Python
# Puis réessayer

# Ou utiliser l'interpréteur Python directement
python -c "from ultralytics import YOLO; print('OK')"
```

---

## 🧪 TESTER PAS À PAS

### Étape 1: Tester les imports

```bash
python test_project.py
```

### Étape 2: Tester PyTorch et GPU

```bash
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

### Étape 3: Tester YOLOv11

```bash
python -c "from ultralytics import YOLO; print('YOLOv11 OK')"
```

### Étape 4: Tester le dataset

```bash
python -c "from pathlib import Path; print(f'Train images: {len(list(Path(\"train/images\").glob(\"*\")))}')"
```

### Étape 5: Entraîner de test

```bash
python simple_train.py
```

---

## 🔧 CONFIGURATION PAR PROBLÈME

### Problème: Entraînement très lent

**Solution 1 - Réduire la taille du modèle**:
```python
# Dans simple_train.py, changer:
model = YOLO("yolov11s-seg.pt")  # De 'm' à 's' (small)
```

**Solution 2 - Réduire la résolution**:
```python
config = {
    "imgsz": 416,  # Au lieu de 640
}
```

**Solution 3 - Moins d'epochs pour tester**:
```python
config = {
    "epochs": 5,  # Au lieu de 10
}
```

---

### Problème: Erreur "File not found: yolov11m-seg.pt"

**Solution**: Laisser YOLOv11 télécharger automatiquement
```python
# C'est automatique, attendez un peu au premier lancement
model = YOLO("yolov11m-seg.pt")
```

---

### Problème: JSON decode error

**Cause**: Fichier config corrompu

**Solution**:
```bash
# Supprimer les fichiers générés
rm -rf runs/ evaluations/ inferences/

# Puis réessayer
python simple_train.py
```

---

## 📋 CHECKLIST DE DIAGNOSTIC

- [ ] `python test_project.py` passe tous les tests
- [ ] `python -c "import torch; print(torch.__version__)"`  fonctionne
- [ ] `python -c "from ultralytics import YOLO; YOLO('yolov11m-seg.pt')"` fonctionne
- [ ] `ls train/images/` retourne des fichiers
- [ ] `ls valid/images/` retourne des fichiers
- [ ] `ls test/images/` retourne des fichiers
- [ ] `cat data.yaml` retourne du YAML valide

---

## 🆘 SI RIEN NE FONCTIONNE

### Option 1: Réinstaller l'environnement

```bash
# Supprimer l'ancienne installation
python -m pip uninstall -y ultralytics torch torchvision

# Réinstaller
python simple_setup.py
```

### Option 2: Utiliser un nouvel environnement Python

```bash
# Créer un nouvel environnement virtuel
python -m venv venv_yolo

# Activer
# Windows:
venv_yolo\Scripts\activate
# Linux/macOS:
source venv_yolo/bin/activate

# Installer
python simple_setup.py
```

### Option 3: Utiliser Docker (si disponible)

```dockerfile
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install ultralytics torch torchvision
WORKDIR /app
COPY . .
CMD ["python", "simple_train.py"]
```

---

## 📞 INFORMATIONS UTILES POUR LE SUPPORT

Si vous demandez de l'aide, fournissez:

```bash
# Exécutez ceci et partagez le résultat
echo "=== SYSTÈME ===" && \
python --version && \
echo "=== TORCH ===" && \
python -c "import torch; print(f'Version: {torch.__version__}, CUDA: {torch.cuda.is_available()}')" && \
echo "=== YOLO ===" && \
python -c "from ultralytics import YOLO; print('OK')" && \
echo "=== DATASET ===" && \
ls -la train/images/ | head -5
```

---

## ✅ TOUT FONCTIONNE? PARFAIT!

Maintenant vous pouvez:

```bash
# Entraîner
python simple_train.py

# Ou utiliser le pipeline complet
python pipeline.py --config BALANCED

# Ou utiliser le notebook
jupyter notebook Training_Pipeline.ipynb
```

**Bon entraînement! 🚀**
