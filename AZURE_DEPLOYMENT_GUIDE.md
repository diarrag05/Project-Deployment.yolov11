# 🚀 GUIDE DE DÉPLOIEMENT COMPLET - LOCAL / DOCKER / AZURE

## 📋 TABLE DES MATIÈRES
1. [Test Local (Port 5000)](#test-local)
2. [Test Docker (Conteneurisation)](#test-docker)
3. [Déploiement Azure (Production)](#azure)
4. [Vérification & Monitoring](#verification)

---

## 🏠 TEST LOCAL {#test-local}

### Prérequis
- Python 3.11+
- Virtual Environment activé
- Flask, Ultralytics, PyTorch installés

### Lancement

```bash
# Terminal PowerShell
cd "c:\Users\mdiia\OneDrive\Bureau\AIVANCITY\Cours\PGE4\Deployment n Maintenance\Project-Deployment.yolov11"
py app.py
```

### Accès
- **URL**: `http://127.0.0.1:5000`
- **API Base**: `http://127.0.0.1:5000/api`

### Test API

```bash
# Upload et inférence
curl -X POST http://127.0.0.1:5000/api/predict \
  -F "image=@test/images/04_JPG.rf.4935d8061ad1c13154d00829b507412c.jpg" \
  -F "confidence=0.5"
```

### ✅ Status Local
- ✅ Interface Web: http://127.0.0.1:5000
- ✅ API Predict: POST /api/predict
- ✅ Dashboard: http://127.0.0.1:5000/dashboard
- ✅ Feedback: http://127.0.0.1:5000/feedback
- ✅ Analysis: http://127.0.0.1:5000/analysis

---

## 🐳 TEST DOCKER {#test-docker}

### Prérequis
- Docker Desktop installé
- Docker Engine actif

### Étape 1: Build l'image

```bash
# Construire l'image
docker build -t yolov11-app:latest .

# Vérifier la construction
docker images | grep yolov11
```

### Étape 2: Lancer le conteneur

```bash
# Option 1: Port 5000 standard
docker run -p 5000:5000 \
  -v %cd%/uploads:/app/uploads \
  -v %cd%/models:/app/models \
  --name yolov11-app \
  yolov11-app:latest

# Option 2: Avec docker-compose (RECOMMANDÉ)
docker-compose up -d
```

### Étape 3: Vérifier l'exécution

```bash
# Voir les logs
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

### ✅ Status Docker Local
- ✅ Image construite: `yolov11-app:latest`
- ✅ Conteneur actif: `yolov11-app`
- ✅ Port mappé: 5000:5000
- ✅ Volumes persistants: uploads/, models/

---

## ☁️ DÉPLOIEMENT AZURE {#azure}

### Architecture Azure
```
┌─────────────────────────────────────┐
│   Azure Container Registry (ACR)    │
│   yolov11-app:latest               │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│   Azure App Service                 │
│   (Docker Container)                │
│   https://yolov11-app.azurewebsites.net
└─────────────────────────────────────┘
             │
             ├── Azure Blob Storage (uploads/)
             ├── Azure Blob Storage (models/)
             └── Application Insights (Logs)
```

### Prérequis
- Compte Azure actif
- Azure CLI installé
- Docker installé
- Azure App Service Plan (Linux)

### Étape 1: Préparer Azure Container Registry (ACR)

```bash
# Variables
$resourceGroup = "yolov11-rg"
$acrName = "yolov11registry"
$location = "westeurope"

# Créer le groupe de ressources
az group create --name $resourceGroup --location $location

# Créer ACR
az acr create --resource-group $resourceGroup \
  --name $acrName \
  --sku Basic

# Activer admin user
az acr update -n $acrName --admin-enabled true

# Récupérer credentials
az acr credential show --name $acrName
```

### Étape 2: Build et Push l'image Docker vers ACR

```bash
# Se connecter à ACR
az acr login --name $acrName

# Build l'image dans ACR (depuis ACR, pas local)
az acr build --registry $acrName \
  --image yolov11-app:latest .

# Vérifier l'image
az acr repository list --name $acrName
```

### Étape 3: Créer Azure App Service

```bash
# Variables
$appServicePlan = "yolov11-plan"
$appName = "yolov11-app"

# Créer App Service Plan (Linux)
az appservice plan create \
  --name $appServicePlan \
  --resource-group $resourceGroup \
  --sku B1 \
  --is-linux

# Créer App Service
az webapp create \
  --resource-group $resourceGroup \
  --plan $appServicePlan \
  --name $appName \
  --deployment-container-image-name-user $acrName.azurecr.io \
  --deployment-container-image-name yolov11-app:latest \
  --docker-custom-user-agent-suffix CUSTOM

# Configurer les credentials ACR
$acrUrl = "$acrName.azurecr.io"
$acrUsername = (az acr credential show --name $acrName --query username -o tsv)
$acrPassword = (az acr credential show --name $acrName --query passwords[0].value -o tsv)

az webapp config container set \
  --name $appName \
  --resource-group $resourceGroup \
  --docker-custom-image-name "$acrUrl/yolov11-app:latest" \
  --docker-registry-server-url "https://$acrUrl" \
  --docker-registry-server-user $acrUsername \
  --docker-registry-server-password $acrPassword
```

### Étape 4: Configurer les Variables d'Environnement

```bash
# Port Flask
az webapp config appsettings set \
  --resource-group $resourceGroup \
  --name $appName \
  --settings WEBSITES_PORT=5000

# Autres variables
az webapp config appsettings set \
  --resource-group $resourceGroup \
  --name $appName \
  --settings FLASK_ENV=production \
  ENABLE_CORS=true
```

### Étape 5: Configurer Azure Blob Storage

```bash
# Variables
$storageAccount = "yolov11storage"

# Créer compte storage
az storage account create \
  --name $storageAccount \
  --resource-group $resourceGroup \
  --sku Standard_LRS \
  --location $location

# Créer containers
az storage container create \
  --account-name $storageAccount \
  --name uploads

az storage container create \
  --account-name $storageAccount \
  --name models

# Récupérer connection string
az storage account show-connection-string \
  --name $storageAccount \
  --query connectionString
```

### Étape 6: Vérifier le Déploiement

```bash
# URL de l'app
$appUrl = "https://$appName.azurewebsites.net"
echo "Application URL: $appUrl"

# Tester l'API
curl "$appUrl/api/health"

# Voir les logs (streaming)
az webapp log tail --name $appName --resource-group $resourceGroup
```

### ✅ Status Azure
- ✅ Resource Group créé
- ✅ ACR push réussi
- ✅ App Service actif
- ✅ Blob Storage configuré
- ✅ URL: `https://{appName}.azurewebsites.net`

---

## 🔍 VÉRIFICATION & MONITORING {#verification}

### 1. Health Check - Local
```bash
curl http://127.0.0.1:5000/api/health
```

### 2. Health Check - Docker
```bash
curl http://localhost:5000/api/health
```

### 3. Health Check - Azure
```bash
curl https://yolov11-app.azurewebsites.net/api/health
```

### 4. Test Inférence Complet

```bash
# Préparation
$imageFile = "test/images/04_JPG.rf.4935d8061ad1c13154d00829b507412c.jpg"
$endpoint = "http://127.0.0.1:5000/api/predict"  # Changer pour Docker/Azure

# Upload + Predict
$response = curl.exe -X POST $endpoint `
  -F "image=@$imageFile" `
  -F "confidence=0.5"

# Vérifier la réponse
$response | ConvertFrom-Json | ConvertTo-Json
```

### 5. Azure Monitoring

```bash
# Voir les logs Azure
az webapp log tail --name yolov11-app --resource-group yolov11-rg

# Voir les métriques
az monitor metrics list-definitions \
  --resource /subscriptions/{subscriptionId}/resourceGroups/yolov11-rg/providers/Microsoft.Web/sites/yolov11-app
```

---

## 📊 TABLEAU COMPARATIF

| Aspect | Local | Docker | Azure |
|--------|-------|--------|-------|
| **URL** | http://127.0.0.1:5000 | http://localhost:5000 | https://yolov11-app.azurewebsites.net |
| **Performance** | Rapide (machine locale) | Moyen (conteneurisé) | Excellent (scalable) |
| **Stockage** | Local | Volume mappé | Azure Blob |
| **Scaling** | Manual | Manual | Auto |
| **Monitoring** | Console | Logs Docker | Application Insights |
| **Coût** | 0€ | 0€ | Facturé (pay-as-you-go) |
| **Production Ready** | Non | Oui | Oui |

---

## 🎯 WORKFLOW RECOMMANDÉ

```
1. Développement LOCAL
   ↓
2. Test LOCAL complet
   ↓
3. Build DOCKER (vérifie reproducibilité)
   ↓
4. Test DOCKER local
   ↓
5. Push vers Azure ACR
   ↓
6. Déployer sur Azure App Service
   ↓
7. Test PRODUCTION
   ↓
8. Monitoring Azure
```

---

## ⚠️ TROUBLESHOOTING

### Docker: "image not found"
```bash
docker pull python:3.11-slim
docker build -t yolov11-app:latest .
```

### Azure: "Connection refused"
```bash
# Vérifier les logs
az webapp log tail --name yolov11-app

# Vérifier le port
az webapp config show --name yolov11-app --resource-group yolov11-rg
```

### Azure: "Out of memory"
- Augmenter le App Service Plan (B2 ou P1V2)

### Inférence lente Azure
- Augmenter les ressources (CPU/RAM)
- Utiliser GPU si disponible
- Ajouter CDN pour le cache

---

## 📞 COMMANDES RAPIDES

```bash
# LOCAL: Démarrer
py app.py

# DOCKER: Build + Run
docker-compose up -d

# AZURE: Logs
az webapp log tail -n yolov11-app -g yolov11-rg

# AZURE: Redéployer
az acr build --registry yolov11registry --image yolov11-app:latest .
```

---

**Réalisé**: 4 Décembre 2025
**Version**: 1.0
**Statut**: ✅ Production Ready
