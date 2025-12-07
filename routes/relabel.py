"""
Route: Relabel with YOLO (SAM fallback)
POST /api/relabel - Re-segment image
"""

from flask import Blueprint, request, jsonify, current_app
import json
import os
import base64
from pathlib import Path
import logging
import cv2
import numpy as np
from ultralytics import YOLO

relabel_bp = Blueprint('relabel', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

# Load YOLO model once
_yolo_model = None

def get_yolo_model():
    global _yolo_model
    if _yolo_model is None:
        model_path = 'models/yolov8n-seg_trained.pt'
        if not os.path.exists(model_path):
            model_path = 'yolov8n-seg.pt'
        _yolo_model = YOLO(model_path)
        logger.info(f"YOLO model loaded: {model_path}")
    return _yolo_model

@relabel_bp.route('/relabel', methods=['POST'])
def relabel():
    """
    Relabel image using YOLO (or SAM if available)
    
    Input:
    {
        "image_id": "timestamp_filename",
        "points": [[x, y], ...] (optional),
        "boxes": [[x1, y1, x2, y2], ...] (optional)
    }
    
    Returns:
    {
        "status": "success",
        "image_id": "timestamp_filename",
        "masks": [
            {
                "image": "base64_png",
                "area": 12000,
                "confidence": 0.95
            }
        ]
    }
    """
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        
        if not image_id:
            return jsonify({'error': 'image_id required'}), 400
        
        # Load original image
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_id)
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return jsonify({'error': 'Image not found'}), 404
        
        # Use YOLO for re-segmentation
        logger.info(f"Re-segmenting {image_id} with YOLO")
        model = get_yolo_model()
        
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return jsonify({'error': 'Cannot read image'}), 400
        
        # Run YOLO inference
        results = model.predict(image, conf=0.3, verbose=False)
        
        masks_list = []
        if results and len(results) > 0:
            result = results[0]
            
            if hasattr(result, 'masks') and result.masks is not None:
                masks = result.masks.data.cpu().numpy()
                boxes = result.boxes.conf.cpu().numpy()
                
                for i, (mask, conf) in enumerate(zip(masks, boxes)):
                    # Create mask visualization (white on black)
                    mask_uint8 = (mask > 0).astype(np.uint8) * 255
                    
                    # Convert to base64 PNG
                    _, buffer = cv2.imencode('.png', mask_uint8)
                    mask_b64 = base64.b64encode(buffer).decode()
                    
                    # Calculate area
                    area = int(np.sum(mask > 0))
                    
                    masks_list.append({
                        'image': mask_b64,
                        'area': area,
                        'confidence': float(conf)
                    })
        
        logger.info(f"Re-segmentation complete: {len(masks_list)} masks")
        
        return jsonify({
            'status': 'success',
            'image_id': image_id,
            'masks': masks_list,
            'count': len(masks_list)
        }), 200
    
    except Exception as e:
        logger.error(f"Relabel error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Relabel failed: {str(e)}'}), 500

@relabel_bp.route('/relabel-auto', methods=['POST'])
def relabel_auto():
    """
    Automatic relabeling using YOLO on full image
    """
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        
        if not image_id:
            return jsonify({'error': 'image_id required'}), 400
        
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_id)
        if not os.path.exists(image_path):
            return jsonify({'error': 'Image not found'}), 404
        
        # Use YOLO for full segmentation
        logger.info(f"Auto-segmenting {image_id} with YOLO")
        model = get_yolo_model()
        
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return jsonify({'error': 'Cannot read image'}), 400
        
        # Run YOLO inference with lower confidence
        results = model.predict(image, conf=0.1, verbose=False)
        
        masks_list = []
        if results and len(results) > 0:
            result = results[0]
            
            if hasattr(result, 'masks') and result.masks is not None:
                masks = result.masks.data.cpu().numpy()
                boxes = result.boxes.conf.cpu().numpy()
                
                for i, (mask, conf) in enumerate(zip(masks, boxes)):
                    # Create mask visualization (white on black)
                    mask_uint8 = (mask > 0).astype(np.uint8) * 255
                    
                    # Convert to base64 PNG
                    _, buffer = cv2.imencode('.png', mask_uint8)
                    mask_b64 = base64.b64encode(buffer).decode()
                    
                    # Calculate area
                    area = int(np.sum(mask > 0))
                    
                    masks_list.append({
                        'image': mask_b64,
                        'area': area,
                        'confidence': float(conf)
                    })
        
        logger.info(f"Auto-segmentation complete: {len(masks_list)} masks")
        return jsonify({
            'status': 'success',
            'image_id': image_id,
            'masks': masks_list,
            'count': len(masks_list)
        }), 200
    
    except Exception as e:
        logger.error(f"Auto relabel error: {str(e)}")
        return jsonify({'error': f'Auto relabel failed: {str(e)}'}), 500
