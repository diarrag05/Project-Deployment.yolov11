"""
Evaluation script for YOLOv11 segmentation model.
Adapted for the project structure with proper path handling.
"""
import os
import sys
import argparse
from pathlib import Path
from ultralytics import YOLO

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'backend'))
from src.config import Config
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger(
    __name__,
    log_file=str(Config.LOGS_DIR / "evaluation.log"),
    level='INFO'
)


def get_model_path(model_arg: str = None) -> Path:
    """
    Get the path to the model weights file.
    
    Args:
        model_arg: Optional model path from command line
        
    Returns:
        Path to model file
    """
    if model_arg:
        model_path = Path(model_arg)
        if not model_path.exists():
            logger.error(f"Model not found at: {model_path}")
            sys.exit(1)
        return model_path
    
    # Try default locations
    possible_paths = [
        Config.DEFAULT_MODEL,  # models/best.pt
        Path('models/best.pt'),
        Path('runs/segment/train/weights/best.pt'),
    ]
    
    for path in possible_paths:
        if path.exists():
            logger.info(f"Using model: {path.absolute()}")
            return path
    
    logger.error("No model found. Please train a model first or specify --model path")
    sys.exit(1)


def get_data_yaml_path() -> Path:
    """
    Get the path to data.yaml file.
    
    Returns:
        Path to data.yaml
    """
    if Config.DATA_YAML.exists():
        return Config.DATA_YAML
    
    # Try alternative locations
    possible_paths = [
        Path('dataset/data.yaml'),
        Path('data.yaml'),
    ]
    
    for path in possible_paths:
        if path.exists():
            logger.info(f"Using data configuration: {path.absolute()}")
            return path
    
    logger.error("data.yaml not found. Please ensure it exists in 'dataset/' or root directory.")
    sys.exit(1)


def main():
    """
    Main evaluation function.
    """
    parser = argparse.ArgumentParser(description='Evaluate YOLOv11 segmentation model')
    parser.add_argument('--model', type=str, default=None,
                        help='Path to model weights (default: models/best.pt)')
    parser.add_argument('--data', type=str, default=None,
                        help='Path to data.yaml (default: dataset/data.yaml)')
    parser.add_argument('--split', type=str, default='val', choices=['val', 'test'],
                        help='Dataset split to evaluate on (default: val)')
    parser.add_argument('--batch', type=int, default=8,
                        help='Batch size for evaluation (default: 8)')
    parser.add_argument('--imgsz', type=int, default=640,
                        help='Image size for evaluation (default: 640)')
    args = parser.parse_args()
    
    try:
        # Ensure directories exist
        Config.ensure_directories()
        
        # Get model path
        model_path = get_model_path(args.model)
        
        # Get data.yaml path
        data_yaml = Path(args.data) if args.data else get_data_yaml_path()
        
        # Load model
        logger.info(f"Loading model from: {model_path.absolute()}")
        model = YOLO(str(model_path))
        
        # Run evaluation
        logger.info(f"Evaluating on {args.split} set...")
        logger.info(f"Using data configuration: {data_yaml.absolute()}")
        
        metrics = model.val(
            data=str(data_yaml),
            split=args.split,
            imgsz=args.imgsz,
            batch=args.batch,
            plots=True,
            project='runs/segment',
            name=f'eval_{args.split}',
        )
        
        # Display metrics
        logger.info("\n" + "="*60)
        logger.info("EVALUATION RESULTS")
        logger.info("="*60)
        
        # Box metrics
        logger.info("\nBounding Box Metrics:")
        logger.info(f"  mAP50: {metrics.box.map50:.3f}")
        logger.info(f"  mAP50-95: {metrics.box.map:.3f}")
        logger.info(f"  Precision: {metrics.box.mp:.3f}")
        logger.info(f"  Recall: {metrics.box.mr:.3f}")
        
        # Mask metrics
        logger.info("\nSegmentation Mask Metrics:")
        logger.info(f"  mAP50: {metrics.seg.map50:.3f}")
        logger.info(f"  mAP50-95: {metrics.seg.map:.3f}")
        logger.info(f"  Precision: {metrics.seg.mp:.3f}")
        logger.info(f"  Recall: {metrics.seg.mr:.3f}")
        
        # Per-class metrics
        logger.info("\nPer-Class Metrics:")
        class_names = Config.get_class_names()
        
        for class_id, class_name in class_names.items():
            try:
                # Get per-class results
                if hasattr(metrics.box, 'maps') and len(metrics.box.maps) > int(class_id):
                    map50 = metrics.box.maps[int(class_id)]
                else:
                    map50 = 0.0
                
                # Try to get precision and recall per class
                # Note: Ultralytics may not always provide per-class precision/recall
                logger.info(f"  {class_name} (class {class_id}):")
                logger.info(f"    mAP50: {map50:.3f}")
                
            except Exception as e:
                logger.warning(f"Could not get metrics for class {class_name}: {e}")
        
        logger.info("="*60)
        logger.info(f"\nEvaluation plots saved to: runs/segment/eval_{args.split}/")
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Evaluation failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

