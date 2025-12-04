# 🎯 YOLOv11 Segmentation Platform

Complete ML platform for chip defect detection & void rate calculation.

**Status**: ✅ Production Ready | **100% Complete**

---

## 🚀 Quick Start

```bash
# Install
py -m pip install -r requirements_api.txt

# Run
py app.py

# Open http://localhost:5000
```

---

## 📊 What's Included

| Feature | Status |
|---------|--------|
| Model training & evaluation | ✅ |
| Web interface (4 pages) | ✅ |
| API (25+ endpoints) | ✅ |
| Image upload & prediction | ✅ |
| SAM re-labeling | ✅ |
| Void rate calculation | ✅ |
| Active learning | ✅ |
| CSV export | ✅ |
| Docker support | ✅ |
| Azure deployment | ✅ |

---

## 📁 Structure

```
├── app.py                  # Flask app
├── routes/                 # API (5 modules)
├── utils/                  # ML tools (4 modules)
├── templates/              # Web pages (4)
├── static/                 # CSS + JS
├── models/                 # Trained model
├── Dockerfile              # Docker image
├── docker-compose.yml      # Docker stack
└── requirements_api.txt    # Dependencies
```

---

## 🎮 Features

1. **Upload & Predict** - Drag & drop images
2. **Analyze** - YOLO segmentation + masks
3. **Correct** - SAM-powered re-labeling
4. **Validate** - Store corrected data
5. **Retrain** - Fine-tune model
6. **Feedback** - Active learning
7. **Monitor** - Real-time dashboard
8. **Export** - CSV reports

---

## 🐳 Docker

```bash
docker-compose up -d
# Open http://localhost
```

---

## ☁️ Azure

```bash
.\deploy_azure.ps1
# App at https://yolov11-app.azurewebsites.net
```

---

## 📚 Docs

- `DEPLOYMENT_GUIDE.md` - Setup & deployment
- `PROJET_RESUME_FRANCAIS.md` - French summary
- `FILE_INVENTORY.md` - Complete file list

---

## 🔧 API Endpoints

```
POST   /api/predict              - Inference
POST   /api/predict-batch        - Batch processing
POST   /api/relabel              - SAM segmentation
POST   /api/validate             - Validate masks
POST   /api/train                - Start training
GET    /api/train/status         - Training progress
POST   /api/feedback             - Submit feedback
GET    /api/feedback             - Get statistics
GET    /api/report/csv           - Export CSV
GET    /api/report/json          - Export JSON
```

---

## 📊 Stats

- **50+ files** | **7,000+ lines** code | **25+ endpoints** | **4 pages** | **100% done**

---

## ✅ Status

- ✅ ML model trained
- ✅ Web interface built
- ✅ API complete
- ✅ SAM integrated
- ✅ Active learning working
- ✅ Docker ready
- ✅ Azure scripts ready
- ✅ CI/CD configured

**Ready to use now!**

---

**Tech**: Flask | PyTorch | YOLOv11 | SAM | Docker | Azure | GitHub Actions

Created: Dec 4, 2025 | License: MIT
