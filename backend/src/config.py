"""
Configuration module for the chip-and-hole detection system.
Centralizes all configuration settings for easy management and future API integration.
"""
from pathlib import Path
from typing import Optional
import os
import yaml
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Central configuration class."""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent.parent
    MODELS_DIR = BASE_DIR / os.getenv("MODELS_DIR", "models")
    DATASET_DIR = BASE_DIR / os.getenv("DATASET_DIR", "dataset")
    OUTPUT_DIR = BASE_DIR / os.getenv("OUTPUT_DIR", "outputs")
    RESULTS_DIR = OUTPUT_DIR / os.getenv("RESULTS_DIR", "results")
    INFERENCE_DIR = OUTPUT_DIR / os.getenv("INFERENCE_DIR", "inference")
    SAM_OUTPUT_DIR = OUTPUT_DIR / os.getenv("SAM_OUTPUT_DIR", "sam_segmentation")
    LOGS_DIR = BASE_DIR / os.getenv("LOGS_DIR", "logs")
    LOG_FILE = LOGS_DIR / os.getenv("LOG_FILE", "app.log")
    LOG_TRAINING = LOGS_DIR / os.getenv("LOG_TRAINING", "training.log")
    
    # Model paths
    DEFAULT_MODEL = MODELS_DIR / os.getenv("DEFAULT_MODEL", "best.pt")
    DATA_YAML = DATASET_DIR / os.getenv("DATA_YAML", "data.yaml")
    
    # Dataset paths
    TRAIN_IMAGES_DIR = DATASET_DIR / os.getenv("TRAIN_IMAGES_DIR", "train/images")
    TRAIN_LABELS_DIR = DATASET_DIR / os.getenv("TRAIN_LABELS_DIR", "train/labels")
    
    # YOLO inference settings - convert to float/int
    YOLO_CONF_THRESHOLD = float(os.getenv("YOLO_CONF_THRESHOLD", "0.25"))
    YOLO_IOU_THRESHOLD = float(os.getenv("YOLO_IOU_THRESHOLD", "0.7"))
    YOLO_IMG_SIZE = int(os.getenv("YOLO_IMG_SIZE", "640"))
    
    # Void rate calculation settings - convert to float/int
    VOID_RATE_THRESHOLD = float(os.getenv("VOID_RATE_THRESHOLD", "5.0"))  # Percentage threshold for chip usability
    CHIP_CLASS_ID = int(os.getenv("CHIP_CLASS_ID", "0"))
    HOLE_CLASS_ID = int(os.getenv("HOLE_CLASS_ID", "1"))
    
    # SAM settings
    SAM_MODEL_TYPE = os.getenv("SAM_MODEL_TYPE", "vit_h")
    SAM_CHECKPOINT_URL = os.getenv("SAM_CHECKPOINT_URL", "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth")
    
    # Training settings - Initial training (full training)
    TRAINING_EPOCHS = int(os.getenv("TRAINING_EPOCHS", "100"))
    TRAINING_BATCH_SIZE = int(os.getenv("TRAINING_BATCH_SIZE", "8"))
    TRAINING_PATIENCE = int(os.getenv("TRAINING_PATIENCE", "30"))
    
    # Retraining settings - Optimized for speed (active learning)
    TRAINING_RETRAIN_EPOCHS = int(os.getenv("TRAINING_RETRAIN_EPOCHS", "15"))  # Reduced from 100 to 15 for faster retraining
    TRAINING_RETRAIN_PATIENCE = int(os.getenv("TRAINING_RETRAIN_PATIENCE", "5"))  # Aggressive early stopping
    TRAINING_RETRAIN_LR = float(os.getenv("TRAINING_RETRAIN_LR", "0.0003"))  # Slightly higher LR for faster convergence
    
    # FastAPI settings
    FASTAPI_ENV = os.getenv("FASTAPI_ENV", "development")
    FASTAPI_DEBUG = os.getenv("FASTAPI_DEBUG", "True").lower() in ("true", "1", "yes", "on")
    
    # Azure provides PORT environment variable, fallback to FASTAPI_PORT or default
    FASTAPI_PORT = int(os.getenv("PORT", os.getenv("FASTAPI_PORT", "5001")))
    FASTAPI_MAX_UPLOAD_SIZE = int(os.getenv("FASTAPI_MAX_UPLOAD_SIZE", "16"))  # MB
    
    # Host configuration: Azure uses 0.0.0.0, local uses localhost
    # Detect Azure deployment by checking for WEBSITE_HOSTNAME or PORT env vars
    if os.getenv("WEBSITE_HOSTNAME") or os.getenv("PORT"):
        # Azure deployment: use 0.0.0.0 to listen on all interfaces
        FASTAPI_HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
    else:
        # Local development: use localhost
        FASTAPI_HOST = os.getenv("FASTAPI_HOST", "localhost")
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "").strip() or None
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        directories = [
            cls.MODELS_DIR,
            cls.OUTPUT_DIR,
            cls.RESULTS_DIR,
            cls.INFERENCE_DIR,
            cls.SAM_OUTPUT_DIR,
            cls.TRAIN_IMAGES_DIR,
            cls.TRAIN_LABELS_DIR,
            cls.LOGS_DIR,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def load_data_config(cls) -> dict:
        """Load data.yaml configuration."""
        if not cls.DATA_YAML.exists():
            raise FileNotFoundError(f"data.yaml not found at {cls.DATA_YAML}")
        
        with open(cls.DATA_YAML, 'r') as f:
            return yaml.safe_load(f)
    
    @classmethod
    def get_class_names(cls) -> dict:
        """Get class names from data.yaml."""
        data_config = cls.load_data_config()
        return data_config.get('names', {})
    
    @classmethod
    def get_num_classes(cls) -> int:
        """Get number of classes from data.yaml."""
        data_config = cls.load_data_config()
        return data_config.get('nc', 2)


# Initialize directories on import
Config.ensure_directories()

