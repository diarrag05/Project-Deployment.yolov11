"""YOLO inference service for chip and hole detection."""
import time
from pathlib import Path
from typing import Optional, List
import numpy as np
from ultralytics import YOLO

from ..config import Config
from ..schemas.result_models import InferenceResult, MaskInfo
from ..utils.logger import get_logger
from ..utils.exceptions import ModelNotFoundError, InferenceError, ImageProcessingError
from ..utils.image_utils import load_image, save_image, draw_masks_on_image


class YOLOInferenceService:
    """Service for running YOLO inference on images."""
    
    def __init__(
        self,
        model_path: Optional[str | Path] = None,
        conf_threshold: float = None,
        iou_threshold: float = None
    ):
        """
        Initialize YOLO inference service.
        
        Args:
            model_path: Path to YOLO model weights
            conf_threshold: Confidence threshold for detection
            iou_threshold: IoU threshold for NMS
        """
        self.model_path = Path(model_path) if model_path else Config.DEFAULT_MODEL
        self.conf_threshold = conf_threshold or Config.YOLO_CONF_THRESHOLD
        self.iou_threshold = iou_threshold or Config.YOLO_IOU_THRESHOLD
        self.logger = get_logger(__name__)
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        self.model = YOLO(str(self.model_path))
        self.class_names = Config.get_class_names()
    
    def predict(
        self,
        image_path: str | Path,
        save_output: bool = True,
        output_dir: Optional[str | Path] = None
    ) -> InferenceResult:
        """
        Run YOLO inference on an image.
        
        Args:
            image_path: Path to input image
            save_output: Whether to save output image
            output_dir: Directory to save output (defaults to Config.INFERENCE_DIR)
        
        Returns:
            InferenceResult object
        
        Raises:
            ImageProcessingError: If image cannot be loaded or processed
            InferenceError: If inference fails
        """
        """
        Run inference on a single image.
        
        Args:
            image_path: Path to input image
            save_output: Whether to save the output image
            output_dir: Directory to save output (default: Config.INFERENCE_DIR)
        
        Returns:
            InferenceResult object
        """
        image_path = Path(image_path)
        if not image_path.exists():
            self.logger.error(f"Image not found: {image_path}")
            raise ImageProcessingError(str(image_path), "File not found")
        
        start_time = time.time()
        
        # Run inference
        results = self.model.predict(
            source=str(image_path),
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            imgsz=Config.YOLO_IMG_SIZE,
            save=False,  # We'll handle saving ourselves
            verbose=False
        )
        
        result = results[0]  # Single image inference
        
        # Extract masks and boxes
        masks_info = []
        output_image_path = None
        
        if result.masks is not None and len(result.masks) > 0:
            # Extract mask data
            masks = []
            boxes = []
            class_ids = []
            confidences = []
            
            # Load original image for area calculation
            image = load_image(image_path)
            
            for i, box in enumerate(result.boxes):
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                bbox = box.xyxy[0].cpu().numpy().tolist()
                
                # Get corresponding mask
                if i < len(result.masks.data):
                    mask = result.masks.data[i].cpu().numpy()
                    # Resize mask to original image size
                    mask_resized = self._resize_mask(mask, image.shape[:2])
                    masks.append(mask_resized)
                    
                    # Calculate mask area
                    area = int(np.sum(mask_resized))
                    
                    masks_info.append(MaskInfo(
                        class_id=class_id,
                        class_name=self.class_names.get(class_id, f"class_{class_id}"),
                        confidence=confidence,
                        area_pixels=area,
                        bbox=bbox
                    ))
                    
                    boxes.append(bbox)
                    class_ids.append(class_id)
                    confidences.append(confidence)
            
            # Use YOLO's native plot() method to get annotated image with original visible
            # This ensures the original image is properly displayed with annotations
            if save_output:
                annotated_image = result.plot()  # YOLO's native method - returns RGB numpy array
                
                output_dir = Path(output_dir) if output_dir else Config.INFERENCE_DIR
                output_dir.mkdir(parents=True, exist_ok=True)
                
                output_filename = f"{image_path.stem}_inference{image_path.suffix}"
                output_image_path = output_dir / output_filename
                save_image(annotated_image, output_image_path)
        
        processing_time = time.time() - start_time
        
        return InferenceResult(
            image_path=str(image_path),
            output_image_path=str(output_image_path) if output_image_path else None,
            masks=masks_info,
            num_detections=len(masks_info),
            processing_time=processing_time
        )
    
    def _resize_mask(self, mask: np.ndarray, target_shape: tuple) -> np.ndarray:
        """Resize mask to target shape."""
        import cv2
        if mask.shape[:2] == target_shape:
            return mask > 0.5
        
        mask_uint8 = (mask * 255).astype(np.uint8)
        resized = cv2.resize(mask_uint8, (target_shape[1], target_shape[0]),
                           interpolation=cv2.INTER_NEAREST)
        return (resized > 127).astype(bool)
    
    def get_masks_data(self, inference_result: InferenceResult) -> tuple:
        """
        Extract masks data from inference result for further processing.
        
        Returns:
            Tuple of (masks, class_ids, confidences) as numpy arrays
        """
        # This would require storing the actual mask arrays
        # For now, return empty - masks need to be re-extracted if needed
        # In a full implementation, we'd store masks in InferenceResult
        return [], [], []

