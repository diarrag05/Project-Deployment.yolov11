# 🧪 GUIDE RAPIDE DE TEST

## Étape 1: Démarrer l'app

Ouvre un terminal et lance:

```bash
cd c:\Users\mdiia\OneDrive\Bureau\AIVANCITY\Cours\PGE4\Deployment\ n\ Maintenance\Project-Deployment.yolov11

py app.py
```

**Tu verras:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: off
```

## Étape 2: Ouvrir navigateur

Ouvre dans ton navigateur:
```
http://localhost:5000
```

Tu verras la page d'accueil avec:
- Zone de drag & drop pour images
- Slider de confiance
- Bouton "Run Inference"

## Étape 3: Tester l'inférence

### Option A: Via l'interface web (SIMPLE)

1. Va sur http://localhost:5000
2. Upload une image (test/images/*.jpg)
3. Clique "Run Inference"
4. Vois les résultats:
   - Image segmentée
   - Void rate %
   - Chip area
   - Holes area

### Option B: Via script de test (COMPLET)

Ouvre un 2e terminal et lance:

```bash
cd c:\Users\mdiia\OneDrive\Bureau\AIVANCITY\Cours\PGE4\Deployment\ n\ Maintenance\Project-Deployment.yolov11

py run_tests.py
```

Ce script teste:
- ✅ API health
- ✅ Pages web
- ✅ Inférence
- ✅ Rapports
- ✅ Feedback
- ✅ Status training
- ✅ Infos modèle
- ✅ data.yaml

## Étape 4: Tester les autres pages

Clique sur les onglets:

### Onglet "Analysis"
- Voir images uploadées
- Historique prédictions
- Détails segmentation

### Onglet "Dashboard"
- Graphiques temps réel
- Statistiques globales
- Void rate moyenne

### Onglet "Feedback"
- Corriger prédictions
- Soumettre feedback
- Voir statistiques corrections

## Étape 5: Tester un cycle complet

**Workflow:**

1. **Prédiction** - Upload image → Run Inference
2. **Correction** - Clique "Je ne suis pas content" → SAM génère masks
3. **Validation** - Valide les masks corrigés
4. **Retraining** - Clique "Retrain" → Model réentraîné

## Étape 6: Tester l'export CSV

1. Va sur Dashboard
2. Clique "Export CSV"
3. Fichier téléchargé: `void_rate_report_*.csv`
4. Contient:
   - Image Name
   - Chip Area
   - Holes Area
   - Void Rate %
   - Confidence
   - Timestamp

---

## 🐛 Troubleshooting

### Erreur: "Connection refused"
**Solution**: Assure-toi que `py app.py` est lancé

### Erreur: "No module named 'flask'"
**Solution**: 
```bash
py -m pip install -r requirements_api.txt
```

### Erreur: "Image not found"
**Solution**: Place une image dans `test/images/`

### App très lente
**Solution**: C'est normal à la première inférence (modèle se charge)

---

## 📊 Commandes utiles

**Vérifier que tout fonctionne:**
```bash
py verify_project.py
```

**Lancer les tests:**
```bash
py run_tests.py
```

**Entraîner le modèle:**
```bash
py fast_train.py
```

**Évaluer le modèle:**
```bash
py evaluate.py
```

**Calculer void rate sur une image:**
```bash
py void_rate_calculator.py
```

---

## ✅ Checklist de test

- [ ] App démarre (py app.py)
- [ ] Page d'accueil charge (http://localhost:5000)
- [ ] Upload image fonctionne
- [ ] Inférence retourne void rate
- [ ] Dashboard affiche stats
- [ ] Feedback fonctionne
- [ ] Export CSV marche
- [ ] Script de test réussit (10/10)
- [ ] Verify project réussit (10/10)

**Tous les tests passent? C'est bon! 🎉**
