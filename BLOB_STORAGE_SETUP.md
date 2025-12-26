# Azure Blob Storage Setup Guide

This guide explains how to set up Azure Blob Storage to store the YOLO model (`best.pt`) and make it available to the application.

## Step 1: Create Azure Storage Account

Run these commands in **Azure Cloud Shell**:

```bash
# Create storage account
az storage account create \
  --name chipvoidmodels \
  --resource-group chip-void-detection-rg \
  --location francecentral \
  --sku Standard_LRS \
  --kind StorageV2

# Create container for models
az storage container create \
  --name models \
  --account-name chipvoidmodels \
  --auth-mode login \
  --public-access off
```

## Step 2: Get Storage Account Key

```bash
# Get the storage account key
az storage account keys list \
  --account-name chipvoidmodels \
  --resource-group chip-void-detection-rg \
  --query "[0].value" \
  --output tsv
```

**Save this key** - you'll need it for Step 4.

## Step 3: Upload Model to Blob Storage

### Option A: From Azure Cloud Shell (if model is accessible)

```bash
# Upload the model
az storage blob upload \
  --account-name chipvoidmodels \
  --container-name models \
  --name best.pt \
  --file /path/to/your/best.pt \
  --auth-mode login
```

### Option B: From Your Local Machine (Mac)

First, install Azure CLI if not already installed:
```bash
brew install azure-cli
az login
```

Then upload:
```bash
# Navigate to your project directory
cd "/Users/johannafokui/Documents/PGE4/Deployment & Maintenance of AI Models/project/chip_and_void/Project-Deployment.yolov11"

# Upload the model (replace with actual path to best.pt)
az storage blob upload \
  --account-name chipvoidmodels \
  --container-name models \
  --name best.pt \
  --file models/best.pt \
  --account-key YOUR_STORAGE_KEY
```

Replace `YOUR_STORAGE_KEY` with the key from Step 2.

### Option C: Via Azure Portal

1. Go to https://portal.azure.com
2. Navigate to your storage account: `chipvoidmodels`
3. Click on "Containers" → `models`
4. Click "Upload"
5. Select your `best.pt` file
6. Click "Upload"

## Step 4: Configure Environment Variables in Azure Web App

### Via Azure Portal:

1. Go to https://portal.azure.com
2. Navigate to your Web App: `chip-void-detection`
3. Go to **Configuration** → **Application settings**
4. Click **+ New application setting** and add:

   - **Name**: `AZURE_STORAGE_ACCOUNT`
   - **Value**: `chipvoidmodels`

   - **Name**: `AZURE_STORAGE_KEY`
   - **Value**: `YOUR_STORAGE_KEY` (from Step 2)

   - **Name**: `AZURE_STORAGE_CONTAINER`
   - **Value**: `models`

   - **Name**: `AZURE_MODEL_BLOB_NAME` (optional, defaults to `best.pt`)
   - **Value**: `best.pt`

5. Click **Save**
6. Restart the Web App

### Via Azure CLI:

```bash
az webapp config appsettings set \
  --name chip-void-detection \
  --resource-group chip-void-detection-rg \
  --settings \
    AZURE_STORAGE_ACCOUNT=chipvoidmodels \
    AZURE_STORAGE_KEY="YOUR_STORAGE_KEY" \
    AZURE_STORAGE_CONTAINER=models \
    AZURE_MODEL_BLOB_NAME=best.pt

# Restart the app
az webapp restart \
  --name chip-void-detection \
  --resource-group chip-void-detection-rg
```

Replace `YOUR_STORAGE_KEY` with the actual key from Step 2.

## Step 5: Verify Setup

1. Check that the model is in Blob Storage:
```bash
az storage blob list \
  --account-name chipvoidmodels \
  --container-name models \
  --auth-mode login
```

2. Check application logs after deployment:
```bash
az webapp log tail \
  --name chip-void-detection \
  --resource-group chip-void-detection-rg
```

Look for:
- "Model already exists" (if model was downloaded)
- "Downloading model from Azure Blob Storage" (if downloading)
- "Model downloaded successfully" (if download succeeded)

## Step 6: Test the Application

1. Go to your application URL
2. Upload an image
3. The model should be downloaded automatically on first use
4. Analysis should work!

## Troubleshooting

### Model not downloading:
- Check environment variables are set correctly
- Verify storage account key is correct
- Check blob exists: `az storage blob exists --account-name chipvoidmodels --container-name models --name best.pt --auth-mode login`
- Check application logs for errors

### Download fails:
- Verify `azure-storage-blob` package is installed (in requirements.txt)
- Check network connectivity from Web App to Blob Storage
- Verify storage account name and key are correct

### Model exists but analysis fails:
- Check model file size (should be > 0)
- Verify model is valid YOLO format
- Check YOLOInferenceService logs

## Cost

Azure Blob Storage Standard LRS:
- **Storage**: ~$0.018 per GB/month
- **Transactions**: First 10,000 free, then $0.004 per 10,000
- **For a 100-500 MB model**: Essentially free (well within free tier)

## Security Notes

- Storage account key is stored as environment variable (encrypted at rest)
- Container is private (public-access off)
- Only the Web App can access the model
- Consider using Managed Identity in the future for better security

