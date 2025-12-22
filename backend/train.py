"""
Training script for YOLOv11 segmentation with GPU detection and proper model management.
Designed for a scalable architecture that can support API and frontend integration.
"""
import os
import sys
import shutil
import argparse
from pathlib import Path
import torch
from ultralytics import YOLO

from src.config import Config
from src.utils.logger import setup_logger

# Setup logger with centralized logging to logs/training.log
logger = setup_logger(
    __name__,
    log_file=str(Config.LOGS_DIR / os.getenv("LOG_TRAINING", "training.log")),
    level='INFO'
)


def detect_device():
    """
    Detect and return the best available device (GPU or CPU).
    
    Returns:
        str: Device identifier ('cuda', 'mps', or 'cpu')
    """
    if torch.cuda.is_available():
        device = 'cuda'
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        logger.info(f"GPU detected: {gpu_name} ({gpu_memory:.2f} GB)")
        logger.info(f"CUDA version: {torch.version.cuda}")
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        device = 'mps'
        logger.info("Apple Silicon GPU (MPS) detected")
    else:
        device = 'cpu'
        logger.warning("No GPU detected. Training will use CPU (this will be slower).")
    
    return device


def ensure_models_directory():
    """
    Ensure the models directory exists.
    
    Returns:
        Path: Path to the models directory
    """
    models_dir = Path('models')
    models_dir.mkdir(exist_ok=True)
    logger.info(f"Models directory: {models_dir.absolute()}")
    return models_dir


def get_data_yaml_path():
    """
    Get the path to data.yaml file.
    Checks both root and dataset directories.
    
    Returns:
        Path: Path to data.yaml file
        
    Raises:
        FileNotFoundError: If data.yaml is not found
    """
    possible_paths = [
        Path('dataset/data.yaml'),
        Path('data.yaml'),
    ]
    
    for path in possible_paths:
        if path.exists():
            logger.info(f"Using data configuration: {path.absolute()}")
            return path
    
    raise FileNotFoundError(
        "data.yaml not found. Please ensure it exists in 'dataset/' or root directory."
    )


def copy_best_model_to_models(source_path, models_dir):
    """
    Copy the best model from training output to models directory.
    
    Args:
        source_path (Path): Path to the best model from training
        models_dir (Path): Destination models directory
        
    Returns:
        Path: Path to the copied model in models directory
    """
    if not source_path.exists():
        raise FileNotFoundError(f"Best model not found at: {source_path}")
    
    dest_path = models_dir / 'best.pt'
    
    # Copy the model
    shutil.copy2(source_path, dest_path)
    logger.info(f"Best model copied to: {dest_path.absolute()}")
    
    return dest_path


def get_base_model_path() -> tuple[str, bool]:
    """
    Determine which model to use as starting point.
    Uses fine-tuned model (best.pt) if it exists, otherwise uses pre-trained model.
    
    Returns:
        Tuple of (model_path, is_finetuned)
    """
    best_model = Path('models/best.pt')
    
    if not best_model.exists():
        return ("models/yolo11s-seg.pt", False)
    else:
        return (str(best_model), True)


def main():
    """
    Main training function.
    Automatically uses fine-tuned model (best.pt) if available, otherwise uses pre-trained model.
    """
    parser = argparse.ArgumentParser(description='Train YOLOv11 segmentation model')
    parser.add_argument('--epochs', type=int, default=None, help='Number of training epochs')
    parser.add_argument('--batch', type=int, default=None, help='Batch size')
    parser.add_argument('--patience', type=int, default=None, help='Early stopping patience')
    
    args = parser.parse_args()
    
    try:
        # Detect device
        device = detect_device()
        
        # Ensure models directory exists
        models_dir = ensure_models_directory()
        
        # Get data configuration path
        data_yaml = get_data_yaml_path()
        
        # Determine which model to use
        model_path, is_finetuned = get_base_model_path()
        
        if is_finetuned:
            logger.info("Loading fine-tuned model (best.pt) for continued training...")
            logger.info("Using lower learning rate for fine-tuning continuation")
        else:
            logger.info("Loading pre-trained YOLOv11s-seg model...")
        
        model = YOLO(model_path)
        
        # Training configuration
        # Use lower learning rate if continuing from fine-tuned model
        base_lr = 0.001
        if is_finetuned:
            base_lr = 0.0001  # 10x lower for continued training
        
        # Use arguments if provided, otherwise use Config defaults
        epochs = args.epochs if args.epochs is not None else Config.TRAINING_EPOCHS
        batch_size = args.batch if args.batch is not None else Config.TRAINING_BATCH_SIZE
        patience = args.patience if args.patience is not None else Config.TRAINING_PATIENCE
        
        logger.info(f"Training configuration:")
        logger.info(f"  Epochs: {epochs}")
        logger.info(f"  Batch size: {batch_size}")
        logger.info(f"  Patience: {patience}")
        
        results = model.train(
            data=str(data_yaml),
            epochs=epochs,
            batch=batch_size,
            imgsz=640,
            device=device,
            optimizer='AdamW',
            lr0=base_lr,
            patience=patience,
            
            # Data augmentation
            hsv_h=0.015,
            hsv_s=0.7,
            hsv_v=0.4,
            degrees=0.0,
            translate=0.1,
            scale=0.5,
            shear=0.0,
            perspective=0.0,
            flipud=0.0,
            fliplr=0.5,
            mosaic=1.0,
            mixup=0.0,
            copy_paste=0.0,
            
            # Loss weights
            box=7.5,
            cls=0.5,
            dfl=1.5,
            
            # Other settings
            amp=(device != 'cpu'),  # Enable AMP for GPU/MPS
            workers=8 if device != 'cpu' else 4,
            project='runs/segment',
            name='train',
        )
        
        # Find and copy best model to models directory
        runs_dir = Path('runs/segment')
        training_dirs = sorted([d for d in runs_dir.iterdir() if d.is_dir() and d.name.startswith('train')], 
                            key=lambda x: x.stat().st_mtime, reverse=True)
        if training_dirs:
            best_model_source = training_dirs[0] / 'weights' / 'best.pt'
        else:
            best_model_source = Path('runs/segment/train/weights/best.pt')
        if best_model_source.exists():
            best_model_dest = copy_best_model_to_models(best_model_source, models_dir)
            
            logger.info("\n" + "="*60)
            logger.info("Training completed successfully!")
            logger.info(f"Best model saved at: {best_model_dest.absolute()}")
            logger.info("="*60)
        else:
            logger.warning("Best model not found in expected location. Training may have failed.")
            
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Training failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
