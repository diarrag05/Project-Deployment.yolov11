# Chip and Void Detection System (YOLOv11)

FastAPI application for automatic detection and segmentation of electronic components (chips) and defects (holes/voids) using YOLOv11 segmentation, with manual correction via SAM (Segment Anything Model) and active learning capabilities.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Getting Started](#getting-started)
- [Usage Workflow](#usage-workflow)
- [API Endpoints](#api-endpoints)
- [Calculations Explained](#calculations-explained)
- [Project Structure](#project-structure)
- [Training](#training)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This is a **complete integrated system** for automatic defect detection and quality control in electronic component manufacturing. The project combines YOLOv11 segmentation fine-tuning with an active learning web application.

### Complete Project Workflow

```
1. Initial Dataset Preparation (Roboflow)
   ↓
   • Label images on Roboflow platform
   • Export in YOLO segmentation format
   • Download dataset (train/val/test splits)
   ↓
2. YOLO Model Fine-tuning
   ↓
   • Fine-tune YOLOv11-segmentation on labeled dataset
   • Generate best.pt model
   ↓
3. Web Application (FastAPI + Frontend)
   ↓
   • Upload images for analysis
   • YOLO automatic detection and segmentation
   • SAM manual correction (if needed)
   • Validation and save corrected images
   ↓
4. Active Learning Loop
   ↓
   • Retrain model with validated images
   • Improve model performance iteratively
```

### Key Components

- **YOLOv11 Segmentation**: Pre-trained model fine-tuned on your labeled dataset from Roboflow
- **SAM (Segment Anything Model)**: Manual correction tool for refining segmentation masks
- **Active Learning**: Continuous improvement through user corrections and model retraining
- **Void Rate Calculation**: Automatic quality assessment (USABLE/NOT USABLE) based on defect percentage

## ✨ Features

- ✅ **Automatic Detection**: YOLOv11-segmentation for real-time chip and hole detection
- ✅ **Manual Correction**: SAM-guided segmentation for precise mask correction
- ✅ **Active Learning**: Validated images automatically added to training dataset
- ✅ **Quality Assessment**: Automatic void rate calculation and usability determination
- ✅ **Model Retraining**: One-click retraining with validated data
- ✅ **CSV Export**: Export analysis results in standardized format
- ✅ **Web Interface**: Modern, user-friendly interface
- ✅ **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## 🔧 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- **Recommended**: NVIDIA GPU with CUDA (for faster training and inference)
- **Alternative**: CPU (slower but functional)
- **Note**: Apple Silicon (MPS) is disabled for training due to compatibility issues with YOLO segmentation

## 📦 Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd Project-Deployment.yolov11
```

### 2. Create a virtual environment (recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

**Note**: Installation may take several minutes as it includes:
- PyTorch and dependencies
- Ultralytics (YOLOv11)
- Segment Anything Model (SAM) from GitHub

### 4. Verify configuration

The `.env` file is already present with default settings. You can modify it if needed (see [Configuration](#configuration)).

## ⚙️ Configuration

The project uses a `.env` file for configuration. Default values are already set, but you can customize them:

### Main Variables

- `FASTAPI_HOST`: Server IP address (default: `localhost`)
- `FASTAPI_PORT`: Server port (default: `5001`)
- `FASTAPI_DEBUG`: Debug mode (default: `True`)
- `TRAINING_EPOCHS`: Number of training epochs (default: `100`)
- `TRAINING_BATCH_SIZE`: Batch size (default: `8`)
- `TRAINING_PATIENCE`: Early stopping patience (default: `30`)
- `VOID_RATE_THRESHOLD`: Void rate threshold percentage (default: `5.0`)
- `YOLO_CONF_THRESHOLD`: YOLO confidence threshold (default: `0.25`)

See `backend/src/config.py` for the complete list of configurable variables.

## 🚀 Getting Started

### Start the Application

```bash
python api/run_api.py
```

The application will be available at:
- **Web Interface**: `http://localhost:5001/`
- **API Documentation**: `http://localhost:5001/docs`
- **Health Check**: `http://localhost:5001/health`

### First-Time Setup

**Scenario 1: No trained model exists**

If `models/best.pt` doesn't exist:
1. The first image analysis will trigger automatic initial training
2. You'll receive a 503 response with a training ID
3. Wait for training to complete (check status via `/api/training/status/<training_id>`)
4. Once complete, you can analyze images normally

**Scenario 2: Trained model exists**

If `models/best.pt` exists:
- Analysis works immediately with the fine-tuned model
- No training is triggered automatically

## 📊 Usage Workflow

### Step 1: YOLO Analysis

1. Upload an image via the web interface
2. YOLO automatically detects and segments:
   - **Chips** (class 0): Electronic components
   - **Holes** (class 1): Defects/voids within components
3. Results displayed:
   - Number of components found
   - Number of defects found
   - Defect rate (void %)
   - Component status (USABLE / NOT USABLE)
   - Visualized masks and bounding boxes

### Step 2: SAM Correction (Optional)

If YOLO results need correction:

1. Select the class to segment (Chip or Hole)
2. Click on the image to add points:
   - **Foreground points** (green): Areas to include in the mask
   - **Background points** (red): Areas to exclude from the mask
3. SAM generates corrected segmentation masks
4. Review and adjust as needed

### Step 3: Validation

1. Click "Validate and Continue" to save the corrected image
2. The image and its labels are saved to `outputs/validated_images/`
3. These images will be used for the next retraining

### Step 4: Retraining

1. Click "Start Retraining" when you have enough validated images
2. The training process:
   - Moves validated images to the training dataset
   - Retrains the YOLO model (fine-tuning from `best.pt` if it exists)
   - Saves the new model as `models/best.pt`
3. Monitor progress via the training status section

## 🔗 API Endpoints

### Analysis

- `POST /api/analyze` - Analyze an image with YOLO
  - Input: Image file (multipart/form-data), optional threshold
  - Output: Detection results, masks, statistics

- `POST /api/analyze/batch` - Analyze multiple images with YOLO
  - Input: Multiple image files (multipart/form-data), optional threshold
  - Output: List of analysis results

- `POST /api/analyze/export-csv` - Export analysis results to CSV
  - Input: Analysis data (JSON)
  - Output: CSV file

### Segmentation

- `POST /api/segment` - Segment image using SAM
  - Input: Image file, points, point labels, optional class_id
  - Output: Segmentation masks

### Validation

- `POST /api/validate/from-segmentation` - Validate and save corrected image from SAM
  - Input: Image path, points, labels, class ID (FormData)
  - Output: Validation confirmation

- `POST /api/validate` - Validate and save an image with corrected labels
  - Input: Image file or path, labels (JSON), metadata (FormData)
  - Output: Validation confirmation

### Training

- `POST /api/retrain` - Start model retraining
  - Input: Optional epochs, batch_size, patience, move_validated (JSON body)
  - Output: Training ID

- `GET /api/training/status` - Get training status
  - Input: Training ID (query parameter, optional - returns latest if not provided)
  - Output: Status, progress, metrics

### Data Management

- `GET /api/validated-images` - Get list of validated images waiting for retraining
  - Output: List of validated images with metadata

- `GET /api/results/export` - Export results (CSV or JSON)
  - Input: Format query parameter (csv or json, default: csv)
  - Output: Exported file

- `GET /api/images/{image_path:path}` - Serve image files
  - Input: Relative path to image
  - Output: Image file

### Health

- `GET /health` - Health check endpoint

### Documentation

- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation
- `GET /openapi.json` - OpenAPI schema

## 📐 Calculations Explained

### Void Rate Calculation

The **void rate** determines whether a component is **USABLE** or **NOT USABLE**.

**Formula:**
```
Void Rate (%) = (Total Holes Area / Total Chips Area) × 100
```

**Determination:**
- If `Void Rate < Threshold` (default: 5%) → **USABLE** ✅
- If `Void Rate ≥ Threshold` (default: 5%) → **NOT USABLE** ❌
- If no chips detected → **NOT USABLE** ❌

**Important**: The status is **NOT** based on model confidence. It's purely based on the void rate calculation.

### Example Calculation

```
Image with:
- 2 chips detected: Chip A (1000 px²), Chip B (800 px²)
- 3 holes detected: Hole 1 (20 px²), Hole 2 (30 px²), Hole 3 (50 px²)

Global calculations:
- Total Area = 1000 + 800 = 1800 px²
- Void % = (20 + 30 + 50) / 1800 × 100 = 5.56%
- Max.void % = 50 / 1800 × 100 = 2.78%

Per-component calculations:
Chip A:
- Area = 1000 px²
- Void % = (20 + 30) / 1000 × 100 = 5.0%
- Status: USABLE (5.0% < 5.0% threshold)

Chip B:
- Area = 800 px²
- Void % = 50 / 800 × 100 = 6.25%
- Status: NOT USABLE (6.25% > 5.0% threshold)
```

### Metrics

- **Area**: Total chip area in pixels²
- **Void %**: Percentage of chip area occupied by holes
- **Max.void %**: Percentage of chip area occupied by the largest single hole
- **Average Confidence**: Average model confidence (informational only, not used for status)

## 📁 Project Structure

```
Project-Deployment.yolov11/
├── api/                    # FastAPI application and routes
│   ├── main.py            # FastAPI app configuration
│   ├── routes.py          # API endpoints
│   ├── run_api.py         # Startup script
│   ├── storage.py         # Validated image storage management
│   ├── training_job.py    # Training job management
│   └── sam_manager.py     # SAM model singleton manager
│
├── backend/               # Business logic
│   ├── src/
│   │   ├── config.py      # Centralized configuration
│   │   ├── services/      # Business services
│   │   │   ├── yolo_inference.py
│   │   │   ├── void_rate_calculator.py
│   │   │   ├── sam_segmentation.py
│   │   │   ├── training_service.py
│   │   │   └── label_manager.py
│   │   ├── schemas/       # Data models
│   │   └── utils/         # Utilities
│   └── train.py           # Training script
│
├── dataset/               # Training dataset (included)
│   ├── data.yaml          # YOLO configuration
│   ├── train/             # Training images and labels
│   ├── valid/             # Validation images and labels
│   └── test/              # Test images and labels
│
├── models/                # Trained models
│   ├── best.pt            # Fine-tuned YOLO model (generated after training)
│   └── sam_vit_h_4b8939.pth  # SAM model (downloaded automatically)
│
├── outputs/               # Results and outputs
│   ├── uploads/           # Temporarily uploaded images
│   ├── inference/         # YOLO inference results
│   ├── sam_segmentation/  # SAM segmentation results
│   ├── results/           # Analysis results
│   └── validated_images/  # Validated images and labels
│
├── logs/                  # Log files
│   ├── app.log            # Application logs
│   └── training.log       # Training logs
│
├── frontend/              # Web interface
│   └── index.html         # User interface
│
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (included)
└── README.md             # This file
```

## 🎓 Project Workflow: From Roboflow to Production

### Step 1: Dataset Preparation with Roboflow

**Initial Setup**:
1. Upload your images to Roboflow platform
2. Label images manually:
   - Draw polygons around **chips** (components)
   - Draw polygons around **holes** (defects/voids)
3. Export dataset in YOLO segmentation format
4. Download the dataset (already included in `dataset/` folder)

**Dataset Structure** (from Roboflow export):
```
dataset/
├── data.yaml          # YOLO configuration (classes, paths)
├── train/
│   ├── images/       # Training images
│   └── labels/       # YOLO format labels (polygons)
├── valid/
│   ├── images/       # Validation images
│   └── labels/       # YOLO format labels
└── test/
    ├── images/       # Test images
    └── labels/       # YOLO format labels
```

**Annotation Format** (YOLO Segmentation):
```
class_id x1 y1 x2 y2 x3 y3 ... xn yn
```
- Coordinates are normalized (0.0 to 1.0)
- Example: `1 0.4527 0.3892 0.4634 0.3901 ...` (hole annotation)

### Step 2: YOLO Model Fine-tuning

Once you have the labeled dataset from Roboflow, fine-tune the YOLOv11-segmentation model:

```bash
python backend/train.py
```

**What happens**:
- Loads pre-trained YOLOv11s-seg model
- Fine-tunes on your labeled dataset
- Saves best model to `models/best.pt`
- This model will be used by the web application

### Step 3: Web Application Deployment

Start the FastAPI application:

```bash
python api/run_api.py
```

**The application**:
- Uses the fine-tuned `models/best.pt` for automatic detection
- Provides web interface for image analysis
- Allows manual correction with SAM
- Implements active learning workflow

### Step 4: Active Learning Loop

**Continuous Improvement**:
1. User uploads images → YOLO detects chips and holes
2. If detection is incorrect → User corrects with SAM
3. User validates corrected image → Saved to `outputs/validated_images/`
4. When enough images validated → Retrain model
5. New model improves → Better detection on future images

### Why This Project?

In the electronics industry, **voids in solder joints** can cause component failures. This integrated system provides:
- 🔍 Automated quality control
- 📊 Void rate calculation
- ⚡ Reduction of manual inspection costs
- 🎯 Continuous model improvement through active learning

#### Current Dataset (from Roboflow)

| Split | Number of images | Percentage |
|-------|-----------------|------------|
| **Train** | 72 | ~70% |
| **Validation** | 20 | ~20% |
| **Test** | 11 | ~10% |
| **Total** | **~103** | **100%** |

#### Classes

| ID | Class name | Description |
|----|------------|-------------|
| 0 | `chip` | Electronic components |
| 1 | `hole-JsHt` | Holes/voids in components |

**Note**: The dataset in `dataset/` folder is the initial labeled dataset from Roboflow. As you use the application and validate corrected images, new images are added to the training set for continuous improvement.

### Architecture and Technologies

#### Technologies Used

| Technology | Version | Usage |
|-----------|---------|-------|
| **Python** | 3.8+ | Main language |
| **Ultralytics** | ≥8.0.0 | YOLOv11 framework |
| **PyTorch** | ≥2.0.0 | Deep learning backend |
| **OpenCV** | ≥4.8.0 | Image processing |
| **FastAPI** | ≥0.104.0 | Web framework |
| **SAM** | Latest | Segment Anything Model |

#### YOLOv11-Segmentation Model

**Why YOLOv11-seg?**
- 🚀 **Fast**: Real-time inference
- 🎯 **Accurate**: State-of-the-art for instance segmentation
- 📦 **Compact**: Small model (11s) with 11.6M parameters
- 🔄 **Pre-trained**: On COCO dataset (80 classes)

**Architecture**:
- **Backbone**: CSPDarknet with P2-P5 feature pyramids
- **Neck**: PAN (Path Aggregation Network)
- **Head**: Dual heads for detection + segmentation
- **Output**: Bounding boxes + segmentation masks

### Initial Model Training (One-Time Setup)

After downloading your labeled dataset from Roboflow, train the initial model:

**Training command**:
```bash
python backend/train.py
```

**What the training script does**:
1. Loads pre-trained YOLOv11s-seg model (`models/yolo11s-seg.pt`)
2. Fine-tunes on your Roboflow-labeled dataset
3. Saves best model to `models/best.pt`
4. This model is then used by the web application

**Training configuration** (in `backend/train.py`):
- Model: YOLOv11s-segmentation (small, fast)
- Epochs: 100 (with early stopping at 30 epochs patience)
- Batch size: 8
- Device: CPU (MPS disabled for stability)
- Optimizer: AdamW
- Learning rate: 0.001

**Training output**:
- Best model: `models/best.pt` (used by the API)
- Training metrics: `runs/segment/train/results.csv`
- Visualizations: confusion matrix, PR curves, training curves

**Note**: This initial training is done once. After that, the web application handles retraining with new validated images through the active learning loop.

## 🎓 Model Training

### Initial Training (From Roboflow Dataset)

**First-time setup** - Train the model on your Roboflow-labeled dataset:

```bash
python backend/train.py
```

This will:
- Use the dataset from `dataset/` (exported from Roboflow)
- Fine-tune YOLOv11s-segmentation model
- Save `models/best.pt` for use by the web application

### Retraining (Active Learning)

**After using the application** - Retrain with validated images:

1. Use the web interface to analyze and correct images
2. Validate corrected images (saved to `outputs/validated_images/`)
3. Click "Start Retraining" in the web interface
4. The system automatically:
   - Moves validated images to `dataset/train/`
   - Retrains the model (fine-tuning from `models/best.pt`)
   - Updates `models/best.pt` with improved model

**Retraining via API**:
```bash
# Via web interface (recommended)
# Or via API:
POST /api/retrain
```

**Retraining via command line**:
```bash
python backend/train.py --epochs 100 --batch 8 --patience 30
```

**Note**: When `models/best.pt` exists, the training script automatically uses it for fine-tuning (continues training), otherwise it starts from the pre-trained YOLOv11s-seg model.

### Training Configuration

- **Model Selection**: 
  - If `models/best.pt` exists → Fine-tuning (continues from existing model)
  - If not → Training from scratch with pre-trained YOLOv11s-seg
- **Device**: Automatically detects CUDA, otherwise uses CPU (MPS disabled for stability)
- **Early Stopping**: Configured with patience (default: 30 epochs)
- **Logging**: Detailed logs saved to `logs/training.log`

### Training Metrics

Monitor these metrics during training:
- **Box Loss**: Bounding box localization accuracy
- **Seg Loss**: Segmentation mask quality
- **Class Loss**: Classification accuracy (chip vs hole)
- **mAP50**: Mean Average Precision at IoU=0.5
- **mAP50-95**: Mean Average Precision at IoU=0.5:0.95

### Evaluation Script

**File**: `evaluate.py`

Script for evaluating model performance on validation or test datasets.

```bash
# Evaluate on validation set (default)
python evaluate.py

# Evaluate on test set
python evaluate.py --split test

# Evaluate with specific model
python evaluate.py --model models/best.pt --split val

# Evaluate with custom parameters
python evaluate.py --batch 16 --imgsz 640
```

**Metrics displayed**:
- mAP50 and mAP50-95 (bounding boxes and masks)
- Global Precision and Recall
- Per-class metrics (chip, hole-JsHt)
- Generates plots in `runs/segment/eval_*/`

### Inference Script

**File**: `inference.py`

Script for making predictions on new images.

```bash
# Prediction on one image
python inference.py --source dataset/test/images/image.jpg

# Prediction on a directory of images
python inference.py --source dataset/test/images/

# With custom thresholds
python inference.py --source dataset/test/images/image.jpg --conf 0.5 --iou 0.7

# Save labels in YOLO format
python inference.py --source dataset/test/images/image.jpg --save-txt
```

**Available options**:
- `--model`: Path to model (default: `models/best.pt`)
- `--source`: Image, video, or directory (required)
- `--conf`: Confidence threshold (default: 0.25)
- `--iou`: IoU threshold for NMS (default: 0.7)
- `--save-txt`: Save labels in YOLO format
- `--imgsz`: Image size (default: 640)

**Results**:
- Annotated images saved in `runs/segment/predict/`
- Labels (if `--save-txt`) in `runs/segment/predict/labels/`

### Automatic SAM Management

**Behavior**: If the SAM model (`models/sam_vit_h_4b8939.pth`) is not present:
- The model is **automatically downloaded** on first use of SAM segmentation
- File size: ~2.4 GB
- Downloaded from: `https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth`

**Note**: In production, fine-tuned models (`best.pt`) and SAM will already be present. These are **extreme fallbacks** for development or initial deployment cases.

## ⚠️ Important Notes

### Model Retraining

- **The retrained model overwrites the previous `best.pt`**
- No automatic backup of previous versions
- To preserve a version, copy `best.pt` before retraining

### Dataset and Configuration

- The `dataset/` folder structure is **included** in the project (with `data.yaml` configuration)
- **Dataset images are NOT committed to Git** for the following reasons:
  - **File size**: Image datasets can be very large (hundreds of MB to GB)
  - **Git limitations**: Git is not optimized for large binary files
  - **Storage efficiency**: Avoid bloating the repository size
  - **Download from Roboflow**: Users should download the dataset from Roboflow using the URL in `dataset/data.yaml`
- The `.env` file is **NOT committed** to Git (security best practice)
- **No sensitive or confidential data** is present in committed files

**To get the dataset**:
1. Use the Roboflow URL in `dataset/data.yaml`: `https://universe.roboflow.com/projet-deployment-and-maintenance/project-deployment-1hkdn/dataset/1`
2. Download the dataset and extract it to the `dataset/` folder
3. The structure should match: `dataset/train/images/`, `dataset/valid/images/`, `dataset/test/images/`

### Production vs Development

- **In production**: Fine-tuned models (`best.pt`) and SAM will already be present
- Automatic fallbacks (model download, initial training) are for:
  - Local development
  - Initial deployments
  - Testing environments

### Performance

- **GPU Recommended**: Training and inference are much faster with NVIDIA GPU
- **CPU**: Works but can be very slow for training (several hours)
- **Apple Silicon**: MPS is disabled for training due to compatibility issues with YOLO segmentation

### SAM Model

- SAM model is loaded once at startup (singleton pattern)
- First request may be slower as the model loads
- Subsequent requests are fast as the model is reused

## 🐛 Issues Encountered and Solutions

### Issue 1: Shape Mismatch Error

**Error encountered**:
```
RuntimeError: shape mismatch: value tensor of shape [156542]
cannot be broadcast to indexing result of shape [142122]
```

**Cause**:
- Used **detection** model (`models/yolo11s.pt`)
- While annotations were in **segmentation** format (polygons)

**Solution applied**:
```python
# ❌ Incorrect
model = YOLO("models/yolo11s.pt")  # Detection model

# ✅ Correct
model = YOLO("models/yolo11s-seg.pt")  # Segmentation model
```

**Lesson learned**:
- `.pt` = detection (bounding boxes)
- `-seg.pt` = segmentation (polygon masks)

### Issue 2: MPS Error on Apple Silicon

**Error encountered**:
```
RuntimeError: view size is not compatible with input tensor's
size and stride (at least one dimension spans across two
contiguous subspaces). Use .reshape(...) instead.
```

**Context**:
- MacBook with M1/M2/M4 chip (Apple Silicon)
- Attempted use of MPS backend (Metal Performance Shaders)

**Solutions attempted**:

1. **First attempt**: Disable AMP
   ```python
   amp=False  # Automatic Mixed Precision
   ```
   **Result**: ❌ Failed, error persists

2. **Second attempt**: Reduce batch size
   ```python
   batch=8  # instead of 16
   ```
   **Result**: ❌ Failed, error persists

3. **Final solution**: Use CPU
   ```python
   device='cpu'  # instead of 'mps'
   ```
   **Result**: ✅ Success

**Technical explanation**:
YOLOv11-segmentation uses complex tensor operations that aren't yet fully supported by PyTorch's MPS backend for segmentation.

**Impact**:
- ⏱️ Slower training (~1-2h on CPU vs ~20min on GPU)
- ✅ But works stably

**Future alternative**:
```python
# If you have NVIDIA GPU
device='cuda'  # Much faster
```

### Issue 3: Relative Paths in data.yaml

**Error encountered**:
```
FileNotFoundError: [Errno 2] No such file or directory:
'../train/images'
```

**Cause**:
Using relative paths in `data.yaml` without proper `path:` field.

**Solution applied**:
```yaml
# ✅ Correct
path: /absolute/path/to/dataset
train: train/images
val: valid/images
test: test/images
```

**Best practice**:
- `path:` = **absolute** path to dataset root
- `train/val/test` = **relative** paths from `path:` field

### Issue 4: TensorBoard Compatibility

**Error encountered**:
```
ImportError: cannot import name 'notf' from 'tensorboard.compat'
AttributeError: 'MessageFactory' object has no attribute 'GetPrototype'
```

**Solution applied**:
- Completely disable TensorBoard via environment variables
- Create dummy `tensorboard.compat` module to prevent errors
- Filter TensorBoard warnings

**Code**:
```python
os.environ['TENSORBOARD_DISABLE'] = '1'
os.environ['YOLO_TENSORBOARD'] = 'False'
```

## 🐛 Troubleshooting

### Training Fails with TensorBoard Error

**Solution**: TensorBoard is automatically disabled. If you still see errors, ensure:
- Environment variables `TENSORBOARD_DISABLE=1` and `YOLO_TENSORBOARD=False` are set
- The dummy `tensorboard.compat` module is in place

### Training Fails with MPS Error

**Error**: `RuntimeError: view size is not compatible with input tensor's size`

**Solution**: MPS is automatically disabled. Training uses CPU instead (slower but stable).

### SAM Segmentation is Slow

**Solution**: SAM model is loaded once at startup. First request may take time, but subsequent requests are fast.

### No Model Found Error

**Solution**: 
1. Check if `models/best.pt` exists
2. If not, trigger initial training via `/api/training/retrain`
3. Wait for training to complete before analyzing images

### Dataset Path Errors

**Solution**: Ensure `dataset/data.yaml` has correct absolute path in the `path:` field:
```yaml
path: /absolute/path/to/dataset
train: train/images
val: valid/images
test: test/images
```

## 📝 Development Notes

### Important Technical Decisions

1. **Choice of YOLOv11s instead of YOLOv11m**
   - Reason: Training time savings (1-2h vs 3-4h)
   - Trade-off: Slight accuracy decrease acceptable for dataset size

2. **Using CPU instead of MPS**
   - Reason: MPS incompatibility with segmentation operations
   - Impact: Longer training time but stable

3. **Early stopping at 30 epochs**
   - Reason: Avoid overfitting on small dataset
   - Result: Automatic stopping when no improvement

4. **FastAPI instead of Flask**
   - Reason: Modern, async, auto-generated documentation
   - Benefits: Better performance, type hints, OpenAPI support

### Lessons Learned

1. ✅ **Always verify annotation format** before choosing model
2. ✅ **Use absolute paths** in `data.yaml` `path:` field
3. ✅ **Test on small batch** before full training
4. ✅ **Document encountered issues** for future reference
5. ✅ **Use segmentation model** (`-seg.pt`) for polygon annotations

## 📝 License

See the project license file.

## 👥 Support

For questions or issues:
- Check logs in `logs/` directory
- Review API documentation at `/docs`
- Contact the development team

## ☁️ Azure Deployment

The application automatically detects Azure deployment and configures itself:
- **Host**: Automatically set to `0.0.0.0` when `WEBSITE_HOSTNAME` or `PORT` env vars are detected
- **Port**: Uses Azure's `PORT` environment variable (automatically provided)
- **Configuration**: Set `FASTAPI_ENV=production` and `FASTAPI_DEBUG=False` in Azure App Service settings

**Deployment Steps**:
1. Create Azure App Service (Linux, Python 3.12)
2. Configure environment variables in Azure Portal:
   - `FASTAPI_ENV=production`
   - `FASTAPI_DEBUG=False`
3. Deploy code via GitHub Actions (see CI/CD section) or Azure CLI
4. Upload models (`models/best.pt`, `models/sam_vit_h_4b8939.pth`) to Azure Storage or include in deployment

## 🔄 CI/CD Pipeline

**GitHub Actions** (`.github/workflows/ci-cd.yml`):
- ✅ Automated testing on push/PR
- ✅ Code linting and formatting checks
- ✅ Automatic deployment to Azure on main branch

**Setup**:
1. Create Azure Service Principal and add as GitHub secret `AZURE_CREDENTIALS`
2. Add `AZURE_RESOURCE_GROUP` and update `AZURE_WEBAPP_NAME` in workflow file
3. Push to `main` branch to trigger deployment

---

**Built with**: FastAPI, YOLOv11, SAM, PyTorch, Ultralytics
