"""
SAM (Segment Anything Model) Handler
For user-guided re-segmentation
"""

import logging
import cv2
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

class SAMHandler:
    def __init__(self):
        """Initialize SAM"""
        try:
            from segment_anything import sam_model_registry, SamPredictor
            
            # Load SAM model (base model)
            model_type = "vit_b"
            sam_checkpoint = "sam_vit_b_01ec64.pth"
            
            # Download if not exists
            if not Path(sam_checkpoint).exists():
                logger.warning(f"SAM model not found, downloading...")
                # In production, download from Facebook research
                # For now, we'll handle gracefully
            
            device = "cpu"  # Can be "cuda" if GPU available
            sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
            sam.to(device=device)
            
            self.predictor = SamPredictor(sam)
            logger.info("SAM model loaded successfully")
        
        except ImportError:
            logger.warning("SAM not installed. Install with: pip install git+https://github.com/facebookresearch/segment-anything.git")
            self.predictor = None
    
    def segment(self, image_path, points=None, boxes=None):
        """
        Segment image with optional user guidance
        
        Args:
            image_path: Path to image
            points: List of [[x, y], ...] for point prompts
            boxes: List of [[x1, y1, x2, y2], ...] for box prompts
        
        Returns:
            List of masks with confidence
        """
        if self.predictor is None:
            logger.error("SAM not available")
            return []
        
        try:
            # Load image
            image = cv2.imread(image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Set image for predictor
            self.predictor.set_image(image_rgb)
            
            masks = []
            
            # Process point prompts
            if points:
                points_array = np.array(points, dtype=np.float32)
                labels = np.ones(len(points), dtype=np.int32)  # 1 for positive, 0 for negative
                
                masks_pred, scores, logits = self.predictor.predict(
                    point_coords=points_array,
                    point_labels=labels,
                    multimask_output=True
                )
                
                for i, (mask, score) in enumerate(zip(masks_pred, scores)):
                    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    for contour in contours:
                        polygon = contour.squeeze().tolist()
                        if len(polygon) >= 3:
                            masks.append({
                                'mask': polygon,
                                'confidence': float(score),
                                'area': int(cv2.contourArea(contour))
                            })
            
            # Process box prompts
            if boxes:
                boxes_array = np.array(boxes, dtype=np.float32)
                
                masks_pred, scores, logits = self.predictor.predict(
                    box=boxes_array,
                    multimask_output=True
                )
                
                for i, (mask, score) in enumerate(zip(masks_pred, scores)):
                    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    for contour in contours:
                        polygon = contour.squeeze().tolist()
                        if len(polygon) >= 3:
                            masks.append({
                                'mask': polygon,
                                'confidence': float(score),
                                'area': int(cv2.contourArea(contour))
                            })
            
            logger.info(f"SAM segmentation: {len(masks)} masks found")
            return masks
        
        except Exception as e:
            logger.error(f"SAM segmentation error: {str(e)}")
            return []
    
    def segment_all(self, image_path):
        """
        Automatic segmentation of entire image
        """
        if self.predictor is None:
            logger.error("SAM not available")
            return []
        
        try:
            image = cv2.imread(image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            self.predictor.set_image(image_rgb)
            
            # Segment everything
            masks, scores, logits = self.predictor.predict(
                point_coords=None,
                point_labels=None,
                box=None,
                mask_input=None,
                multimask_output=True,
                return_logits=False,
            )
            
            masks_list = []
            for mask, score in zip(masks, scores):
                contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    polygon = contour.squeeze().tolist()
                    if len(polygon) >= 3:
                        masks_list.append({
                            'mask': polygon,
                            'confidence': float(score),
                            'area': int(cv2.contourArea(contour))
                        })
            
            logger.info(f"Full segmentation: {len(masks_list)} masks found")
            return masks_list
        
        except Exception as e:
            logger.error(f"Full segmentation error: {str(e)}")
            return []
