# RÉSUMÉ DES TESTS - LOCAL, DOCKER, AZURE

## 1️⃣ TEST LOCAL (ACTUELLEMENT ACTIF ✅)

### Serveur en cours d'exécution
- **URL**: http://127.0.0.1:5000
- **Statut**: ✅ ACTIVE

### Tester via navigateur
1. Ouvre: http://127.0.0.1:5000
2. Charge une image du dossier `test/images/`
3. Clique sur "Run Inference"
4. Vois les résultats

### Tester via PowerShell (dans nouveau terminal)
```powershell
# Upload et prédiction
$imagePath = "test/images/04_JPG.rf.4935d8061ad1c13154d00829b507412c.jpg"
$form = @{
    image = Get-Item -Path $imagePath
    confidence = 0.5
}

$response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/predict" `
    -Method POST `
    -Form $form

$response.Content | ConvertFrom-Json | ConvertTo-Json
```

### Tester la santé de l'API
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/health" -Method GET
```

---

## 2️⃣ TEST DOCKER (LOCAL)

### Prérequis
- Docker Desktop installé et actif
- Image construite: `yolov11-app:latest`

### Étape 1: Construire l'image (une seule fois)
```bash
docker build -t yolov11-app:latest .
```

### Étape 2: Lancer le conteneur
```bash
# Option A: Command simple
docker run -p 5000:5000 --name yolov11-app yolov11-app:latest

# Option B: Avec volumes (RECOMMANDÉ)
docker run -p 5000:5000 `
    -v $PWD/uploads:/app/uploads `
    -v $PWD/models:/app/models `
    --name yolov11-app `
    yolov11-app:latest

# Option C: Avec docker-compose
docker-compose up -d
```

### Étape 3: Vérifier l'exécution
```bash
# Logs
docker logs -f yolov11-app

# Tester l'API
curl http://localhost:5000/api/health

# Accéder à l'interface
# http://localhost:5000
```

### Étape 4: Arrêter le conteneur
```bash
# Arrêter
docker stop yolov11-app

# Supprimer
docker rm yolov11-app
```

---

## 3️⃣ DÉPLOIEMENT AZURE (PRODUCTION)

### Architecture
```
GitHub Repo
    ↓
Azure Container Registry (ACR)
    ↓
Azure App Service
    ↓
Application URL: https://yolov11-app.azurewebsites.net
```

### Prérequis
- Compte Azure
- Azure CLI
- Docker installé
- Repo GitHub avec code

### Configuration rapide (10 minutes)

#### Étape 1: Variables Azure
```powershell
$resourceGroup = "yolov11-rg"
$acrName = "yolov11registry"
$appName = "yolov11-app"
$location = "westeurope"
```

#### Étape 2: Créer ressources
```powershell
# Groupe de ressources
az group create --name $resourceGroup --location $location

# Container Registry
az acr create --resource-group $resourceGroup `
    --name $acrName `
    --sku Basic

# Login ACR
az acr login --name $acrName

# Build dans ACR
az acr build --registry $acrName `
    --image yolov11-app:latest .
```

#### Étape 3: App Service
```powershell
# Plan
az appservice plan create `
    --name yolov11-plan `
    --resource-group $resourceGroup `
    --sku B1 `
    --is-linux

# App
az webapp create `
    --resource-group $resourceGroup `
    --plan yolov11-plan `
    --name $appName `
    --deployment-container-image-name "$acrName.azurecr.io/yolov11-app:latest"

# Port
az webapp config appsettings set `
    --resource-group $resourceGroup `
    --name $appName `
    --settings WEBSITES_PORT=5000
```

#### Étape 4: Vérifier
```powershell
# URL
"https://$appName.azurewebsites.net"

# Logs
az webapp log tail --name $appName --resource-group $resourceGroup

# Tester
curl "https://$appName.azurewebsites.net/api/health"
```

---

## 📊 COMPARAISON RAPIDE

| Critère | LOCAL | DOCKER | AZURE |
|---------|-------|--------|-------|
| Installation | ✅ Facile | ✅ Facile | ⚠️ Complexe |
| Vitesse | ⚡ Rapide | ⚡ Rapide | 🟡 Moyen |
| Coût | 0€ | 0€ | Facturé |
| Production | ❌ Non | ✅ Oui | ✅ Oui |
| URL publique | ❌ Non | ❌ Non | ✅ Oui |
| Scaling auto | ❌ Non | ❌ Non | ✅ Oui |

---

## ✅ TEST COMPLET (CHECKLIST)

### LOCAL
- [ ] Serveur lancé: `py app.py`
- [ ] Interface accessible: http://127.0.0.1:5000
- [ ] Upload image fonctionne
- [ ] Inférence complète
- [ ] Résultats affichés
- [ ] Export CSV fonctionne

### DOCKER
- [ ] Image construite
- [ ] Conteneur lancé
- [ ] Port 5000 mappé
- [ ] Interface accessible: http://localhost:5000
- [ ] Upload image fonctionne
- [ ] Inférence complète

### AZURE
- [ ] ACR push réussi
- [ ] App Service créée
- [ ] URL accessible: https://yolov11-app.azurewebsites.net
- [ ] API health OK
- [ ] Inférence fonctionne

---

## 🔧 COMMANDES RAPIDES

### LOCAL
```bash
py app.py
# Accès: http://127.0.0.1:5000
```

### DOCKER
```bash
docker build -t yolov11-app:latest .
docker run -p 5000:5000 yolov11-app:latest
# Accès: http://localhost:5000
```

### AZURE
```bash
az acr build --registry yolov11registry --image yolov11-app:latest .
# Accès: https://yolov11-app.azurewebsites.net
```

---

## 📝 NOTES

- **LOCAL**: Parfait pour développement
- **DOCKER**: Prêt pour production local
- **AZURE**: Production avec auto-scaling

Choisir selon les besoins:
- Dev only → LOCAL
- Company internal → DOCKER + On-premises
- Public production → AZURE

