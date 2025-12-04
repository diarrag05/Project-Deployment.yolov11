# 🚀 Complete Deployment Guide

This guide covers local development with Docker and production deployment on Azure.

---

## 📋 Prerequisites

### For Local Development
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose 2.0+
- Python 3.8+ (for testing)
- 8GB RAM minimum

### For Azure Deployment
- Azure subscription (free tier available)
- Azure CLI (`az` command-line tool)
- GitHub account (for CI/CD)
- Docker Hub account (optional, for private registry)

---

## 🏗️ Part 1: Local Development

### 1.1 Quick Start (3 minutes)

```bash
# Navigate to project directory
cd Project-Deployment.yolov11

# Create environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Wait 30 seconds for Flask to start
sleep 30

# Open in browser
# Windows: start http://localhost
# Mac/Linux: open http://localhost
```

### 1.2 Verify Services

```bash
# Check all services are running
docker-compose ps

# Expected output:
# NAME                    STATUS
# yolov11-app            running (healthy)
# yolov11-db             running
# yolov11-nginx          running
```

### 1.3 View Logs

```bash
# Flask app logs
docker-compose logs app -f

# Database logs
docker-compose logs postgres -f

# Nginx logs
docker-compose logs nginx -f

# All logs
docker-compose logs -f
```

### 1.4 Stop Services

```bash
# Stop (keeps volumes)
docker-compose stop

# Stop and remove (keeps volumes)
docker-compose down

# Stop and remove everything (including volumes)
docker-compose down -v
```

### 1.5 Rebuild Services

```bash
# Rebuild Flask app after code changes
docker-compose up -d --build app

# Rebuild everything
docker-compose up -d --build
```

---

## ☁️ Part 2: Deploy to Azure

### 2.1 Prerequisites Setup

#### Install Azure CLI

**Windows**:
```powershell
# Using winget
winget install Microsoft.AzureCLI

# Or download from
# https://aka.ms/installazurecliwindows
```

**Mac**:
```bash
brew install azure-cli
```

**Linux**:
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

#### Install Docker CLI

Available at: https://www.docker.com/products/docker-desktop

---

### 2.2 Manual Deployment (Linux/Mac)

```bash
# Step 1: Login to Azure
az login

# Step 2: Create variables
RESOURCE_GROUP="yolov11-rg"
REGION="eastus"
REGISTRY_NAME="yolov11registry"
APP_NAME="yolov11-app"

# Step 3: Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $REGION

# Step 4: Create container registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $REGISTRY_NAME \
  --sku Basic

# Step 5: Get registry info
REGISTRY_URL=$(az acr show \
  --resource-group $RESOURCE_GROUP \
  --name $REGISTRY_NAME \
  --query loginServer -o tsv)

echo "Registry URL: $REGISTRY_URL"

# Step 6: Build and push Docker image
az acr build \
  --registry $REGISTRY_NAME \
  --image yolov11-segmentation:latest \
  --file Dockerfile \
  .

# Step 7: Create App Service Plan
az appservice plan create \
  --name "$APP_NAME-plan" \
  --resource-group $RESOURCE_GROUP \
  --is-linux \
  --sku B2

# Step 8: Create Web App
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan "$APP_NAME-plan" \
  --name $APP_NAME \
  --deployment-container-image-name "$REGISTRY_URL/yolov11-segmentation:latest"

# Step 9: Create storage account
STORAGE_NAME="yolov11storage$(date +%s | tail -c 6)"

az storage account create \
  --name $STORAGE_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $REGION \
  --sku Standard_LRS

# Step 10: Create storage container
STORAGE_KEY=$(az storage account keys list \
  --resource-group $RESOURCE_GROUP \
  --account-name $STORAGE_NAME \
  --query '[0].value' -o tsv)

az storage container create \
  --name yolov11-data \
  --account-name $STORAGE_NAME \
  --account-key $STORAGE_KEY

# Step 11: Configure environment variables
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --settings \
    FLASK_ENV=production \
    WEBSITES_PORT=5000 \
    AZURE_STORAGE_ACCOUNT_NAME=$STORAGE_NAME \
    AZURE_STORAGE_ACCOUNT_KEY=$STORAGE_KEY

# Step 12: Access your app
echo "✅ Deployment complete!"
echo "App URL: https://$APP_NAME.azurewebsites.net"
```

---

### 2.3 Automated Deployment (PowerShell on Windows)

```powershell
# Run the deployment script
.\deploy_azure.ps1 -ResourceGroup yolov11-rg `
                   -RegistryName yolov11registry `
                   -AppName yolov11-app `
                   -Region eastus

# Or use defaults
.\deploy_azure.ps1
```

---

### 2.4 Automated Deployment (Bash on Linux/Mac)

```bash
# Make script executable
chmod +x deploy_azure.sh

# Run deployment
./deploy_azure.sh yolov11-rg yolov11registry eastus yolov11-app

# Or use defaults
./deploy_azure.sh
```

---

## 🔄 Part 3: CI/CD with GitHub Actions

### 3.1 Setup GitHub Secrets

1. **Create Azure Service Principal**

```bash
# Get subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Create service principal
az ad sp create-for-rbac \
  --name "github-yolov11" \
  --role contributor \
  --scopes "/subscriptions/$SUBSCRIPTION_ID"

# Output will be:
# {
#   "clientId": "...",
#   "clientSecret": "...",
#   "subscriptionId": "...",
#   "tenantId": "..."
# }
```

2. **Add GitHub Secrets**

Go to: `Settings → Secrets and variables → Actions`

Add these secrets:

| Secret | Value |
|--------|-------|
| `AZURE_CREDENTIALS` | Full JSON from step 1 |
| `REGISTRY_LOGIN_SERVER` | `yolov11registry.azurecr.io` |
| `REGISTRY_USERNAME` | From ACR credentials |
| `REGISTRY_PASSWORD` | From ACR credentials |

3. **Get ACR Credentials**

```bash
az acr credential show \
  --name yolov11registry \
  --resource-group yolov11-rg
```

### 3.2 Test GitHub Actions

```bash
# Trigger deployment
git add .
git commit -m "Deploy to Azure"
git push origin main

# Check workflow status
# Go to: https://github.com/yourname/repo/actions
```

---

## 📊 Part 4: Monitoring & Maintenance

### 4.1 Monitor Azure Deployment

```bash
# View app logs
az webapp log tail \
  --resource-group yolov11-rg \
  --name yolov11-app

# Check app status
az webapp show \
  --resource-group yolov11-rg \
  --name yolov11-app

# View metrics
az monitor metrics list \
  --resource-group yolov11-rg \
  --resource yolov11-app \
  --resource-type "Microsoft.Web/sites" \
  --metric "Requests" \
  --interval PT1M
```

### 4.2 Update App

After making code changes:

```bash
# Rebuild and push to Azure
az acr build \
  --registry yolov11registry \
  --image yolov11-segmentation:latest \
  --file Dockerfile \
  .

# Azure will automatically pull and restart
```

### 4.3 Scale Up/Down

```bash
# View current App Service Plan
az appservice plan show \
  --name yolov11-app-plan \
  --resource-group yolov11-rg

# Change to higher tier (production)
az appservice plan update \
  --name yolov11-app-plan \
  --resource-group yolov11-rg \
  --sku P2V2
```

---

## 🧪 Part 5: Testing

### 5.1 Health Check

```bash
# Local
curl http://localhost:5000/api/health

# Azure
curl https://yolov11-app.azurewebsites.net/api/health

# Expected response:
# {"status": "healthy", "message": "API is running"}
```

### 5.2 Test API Endpoints

```bash
# List models (local)
curl http://localhost:5000/api/status

# Upload and predict (example)
curl -X POST http://localhost:5000/api/predict \
  -F "image=@test_image.jpg" \
  -F "confidence=0.5"
```

### 5.3 Load Testing

```bash
# Install Apache Bench
# apt-get install apache2-utils (Linux)
# brew install httpd (Mac)

# Run load test
ab -n 100 -c 10 http://localhost:5000/

# For Azure
ab -n 100 -c 10 https://yolov11-app.azurewebsites.net/
```

---

## 🗑️ Part 6: Cleanup

### 6.1 Stop Local Services

```bash
docker-compose down -v
docker system prune -a
```

### 6.2 Delete Azure Resources

```bash
# Delete everything in resource group
az group delete \
  --name yolov11-rg \
  --yes --no-wait

# Check deletion status
az group show --name yolov11-rg
```

---

## 🐛 Troubleshooting

### Docker Won't Start

```bash
# Clean up
docker-compose down -v
docker system prune -a

# Rebuild
docker-compose up --build
```

### Azure Deployment Fails

```bash
# Check logs
az webapp deployment list \
  --resource-group yolov11-rg \
  --name yolov11-app

# Stream logs
az webapp log tail \
  --resource-group yolov11-rg \
  --name yolov11-app
```

### App is Slow

```bash
# Check resource usage
az webapp show \
  --resource-group yolov11-rg \
  --name yolov11-app \
  --query "{plan:appServicePlanId, state:state}"

# Scale up if needed
az appservice plan update \
  --name yolov11-app-plan \
  --resource-group yolov11-rg \
  --sku P1V2
```

---

## 📚 References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Azure CLI Documentation](https://docs.microsoft.com/cli/azure/)
- [Azure App Service](https://docs.microsoft.com/azure/app-service/)
- [GitHub Actions](https://docs.github.com/actions)

---

**Need help?** Check the troubleshooting section or review logs!
