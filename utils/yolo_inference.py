"""
YOLO Inference Module
Handles YOLO predictions and void rate calculations
"""

from ultralytics import YOLO
import cv2
import numpy as np
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class YOLOInference:
    def __init__(self, model_path):
        """Initialize YOLO model"""
        if not os.path.exists(model_path):
            logger.warning(f"Model not found at {model_path}, using default YOLOv8n-seg")
            self.model = YOLO('yolov8n-seg.pt')
        else:
            self.model = YOLO(model_path)
        
        logger.info(f"YOLO model loaded from {model_path}")
    
    def predict(self, image_path, conf=0.5):
        """
        Run YOLO inference
        
        Returns:
        {
            "image_path": str,
            "detections": [
                {
                    "class": int,
                    "class_name": str,
                    "confidence": float,
                    "box": [x1, y1, x2, y2],
                    "mask": [[x, y], ...]  # polygon points
                }
            ]
        }
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Cannot read image: {image_path}")
            
            # Run inference
            results = self.model.predict(image_path, conf=conf, verbose=False)
            result = results[0]
            
            detections = []
            if result.masks is not None:
                for i, mask in enumerate(result.masks):
                    box = result.boxes[i].xyxy[0].cpu().numpy() if result.boxes else None
                    conf = result.boxes[i].conf[0].cpu().numpy() if result.boxes else 0
                    cls = int(result.boxes[i].cls[0].cpu().numpy()) if result.boxes else 0
                    
                    # Get mask contour
                    mask_array = mask.xy[0] if len(mask.xy) > 0 else []
                    
                    detections.append({
                        'class': cls,
                        'class_name': 'hole' if cls == 1 else 'chip',
                        'confidence': float(conf),
                        'box': box.tolist() if box is not None else [],
                        'mask': mask_array.tolist() if isinstance(mask_array, np.ndarray) else mask_array
                    })
            
            logger.info(f"Inference completed: {len(detections)} detections")
            
            return {
                'image_path': image_path,
                'image_shape': image.shape,
                'detections': detections
            }
        
        except Exception as e:
            logger.error(f"Inference error: {str(e)}")
            raise
    
    def calculate_void_rate(self, inference_result):
        """
        Calculate void rate from inference results
        
        void_rate = (holes_pixels / chip_pixels) × 100
        
        Returns:
        {
            "chip_area_pixels": int,
            "holes_area_pixels": int,
            "void_rate": float,
            "chip_percentage": float,
            "holes_percentage": float
        }
        """
        try:
            detections = inference_result.get('detections', [])
            image_path = inference_result.get('image_path')
            
            # Read image
            image = cv2.imread(image_path)
            image_shape = image.shape
            total_pixels = image_shape[0] * image_shape[1]
            
            # Create masks
            chip_mask = np.zeros((image_shape[0], image_shape[1]), dtype=np.uint8)
            holes_mask = np.zeros((image_shape[0], image_shape[1]), dtype=np.uint8)
            
            # Draw masks
            for det in detections:
                mask_points = det.get('mask', [])
                if mask_points and len(mask_points) > 0:
                    # Convert to numpy array
                    points = np.array(mask_points, dtype=np.int32)
                    
                    if det['class_name'] == 'chip':
                        cv2.drawContours(chip_mask, [points], 0, 255, -1)
                    elif det['class_name'] == 'hole':
                        cv2.drawContours(holes_mask, [points], 0, 255, -1)
            
            # Calculate areas
            chip_area = np.count_nonzero(chip_mask)
            holes_area = np.count_nonzero(holes_mask)
            
            # Calculate void rate
            if chip_area > 0:
                void_rate = (holes_area / chip_area) * 100
            else:
                void_rate = 0
            
            chip_percentage = (chip_area / total_pixels) * 100
            holes_percentage = (holes_area / total_pixels) * 100
            
            logger.info(f"Void rate calculated: {void_rate:.2f}%")
            
            return {
                'chip_area_pixels': int(chip_area),
                'holes_area_pixels': int(holes_area),
                'void_rate': round(void_rate, 2),
                'chip_percentage': round(chip_percentage, 2),
                'holes_percentage': round(holes_percentage, 2),
                'total_pixels': int(total_pixels)
            }
        
        except Exception as e:
            logger.error(f"Void rate calculation error: {str(e)}")
            return {
                'chip_area_pixels': 0,
                'holes_area_pixels': 0,
                'void_rate': 0,
                'chip_percentage': 0,
                'holes_percentage': 0,
                'error': str(e)
            }
