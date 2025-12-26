"""
Inference script for YOLOv11 segmentation model.
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
    log_file=str(Config.LOGS_DIR / "inference.log"),
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
    logger.info("You can train a model using: python backend/train.py")
    sys.exit(1)


def main():
    """
    Main inference function.
    """
    parser = argparse.ArgumentParser(description='Run inference with YOLOv11 segmentation model')
    parser.add_argument('--model', type=str, default=None,
                        help='Path to model weights (default: models/best.pt)')
    parser.add_argument('--source', type=str, required=True,
                        help='Path to image, video, or directory')
    parser.add_argument('--conf', type=float, default=None,
                        help=f'Confidence threshold (default: {Config.YOLO_CONF_THRESHOLD})')
    parser.add_argument('--iou', type=float, default=None,
                        help=f'IoU threshold for NMS (default: {Config.YOLO_IOU_THRESHOLD})')
    parser.add_argument('--save', action='store_true', default=True,
                        help='Save results (default: True)')
    parser.add_argument('--save-txt', action='store_true',
                        help='Save results as txt labels')
    parser.add_argument('--imgsz', type=int, default=None,
                        help=f'Image size (default: {Config.YOLO_IMG_SIZE})')
    parser.add_argument('--project', type=str, default='runs/segment',
                        help='Project directory for results (default: runs/segment)')
    parser.add_argument('--name', type=str, default='predict',
                        help='Experiment name (default: predict)')
    args = parser.parse_args()
    
    try:
        # Ensure directories exist
        Config.ensure_directories()
        
        # Get model path
        model_path = get_model_path(args.model)
        
        # Use config defaults if not specified
        conf_threshold = args.conf if args.conf is not None else Config.YOLO_CONF_THRESHOLD
        iou_threshold = args.iou if args.iou is not None else Config.YOLO_IOU_THRESHOLD
        imgsz = args.imgsz if args.imgsz is not None else Config.YOLO_IMG_SIZE
        
        # Check source path
        source_path = Path(args.source)
        if not source_path.exists():
            logger.error(f"Source not found: {source_path}")
            sys.exit(1)
        
        # Load model
        logger.info(f"Loading model from: {model_path.absolute()}")
        model = YOLO(str(model_path))
        
        # Get class names
        class_names = Config.get_class_names()
        logger.info(f"Classes: {class_names}")
        
        # Run inference
        logger.info(f"Running inference on: {source_path.absolute()}")
        logger.info(f"Confidence threshold: {conf_threshold}")
        logger.info(f"IoU threshold: {iou_threshold}")
        logger.info(f"Image size: {imgsz}")
        
        results = model.predict(
            source=str(source_path),
            conf=conf_threshold,
            iou=iou_threshold,
            save=args.save,
            save_txt=args.save_txt,
            imgsz=imgsz,
            project=args.project,
            name=args.name,
        )
        
        # Display results
        logger.info("\n" + "="*60)
        logger.info("INFERENCE COMPLETED")
        logger.info("="*60)
        logger.info(f"Results saved to: {args.project}/{args.name}/")
        
        for i, result in enumerate(results):
            logger.info(f"\nImage {i+1}: {result.path if hasattr(result, 'path') else 'Unknown'}")
            
            if result.masks is not None and len(result.masks) > 0:
                logger.info(f"  Detected {len(result.masks)} objects")
                
                for j, box in enumerate(result.boxes):
                    class_id = int(box.cls[0]) if hasattr(box.cls, '__len__') else int(box.cls)
                    confidence = float(box.conf[0]) if hasattr(box.conf, '__len__') else float(box.conf)
                    class_name = class_names.get(class_id, f"class_{class_id}")
                    
                    logger.info(f"    Object {j+1}: {class_name} (confidence: {confidence:.2f})")
            else:
                logger.info("  No objects detected")
        
        logger.info("="*60 + "\n")
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Inference failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()


