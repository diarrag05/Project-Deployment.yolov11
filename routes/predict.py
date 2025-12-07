"""
Route: Prediction
POST /api/predict - Upload image and get YOLO predictions
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import json
from pathlib import Path
from datetime import datetime
import logging
import cv2
import numpy as np

# Imports pour inference
from void_rate_calculator import VoidRateCalculator

# Configuration
MODEL_PATH = "models/yolov8n-seg_trained.pt"

# Setup
predict_bp = Blueprint('predict', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

# Import YOLO inference
from utils.yolo_inference import YOLOInference

# Lazy load YOLO - only load when needed
yolo_model = None

def get_yolo_model():
    """Lazy load YOLO model"""
    global yolo_model
    if yolo_model is None:
        logger.info("Loading YOLO model...")
        yolo_model = YOLOInference('models/yolov8n-seg_trained.pt')
    return yolo_model

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_segmentation_image(image_path, void_rate_result):
    """
    Génère une image avec les contours des masks dessinés
    Utilise les résultats du void_rate_result qui contient déjà le modèle et les masks
    """
    try:
        # Charger l'image
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Cannot read image: {image_path}")
            return None
        
        logger.info(f"Image shape: {image.shape}")
        
        # Récupérer les résultats YOLO depuis void_rate_result
        if 'yolo_results' not in void_rate_result:
            logger.warning("No YOLO results found in void_rate_result")
            return None
            
        results = void_rate_result.get('yolo_results')
        if not results or len(results) == 0:
            logger.warning("No results from YOLO")
            return None
            
        result = results[0]
        
        if not hasattr(result, 'masks') or result.masks is None:
            logger.warning("No masks in results")
            return None
        
        num_masks = len(result.masks) if result.masks is not None else 0
        logger.info(f"Found {num_masks} masks")
        
        if num_masks == 0:
            logger.warning("No masks found")
            return None
        
        # Créer une copie pour dessiner
        output = image.copy()
        
        # Couleurs pour chips (vert) et holes (rouge) - BGR format
        colors = {
            0: (0, 255, 0),    # chip - vert
            1: (0, 0, 255)     # hole - rouge
        }
        
        # Dessiner chaque mask
        masks = result.masks.data
        cls_ids = result.boxes.cls if hasattr(result.boxes, 'cls') else None
        
        logger.info(f"Processing {len(masks)} masks")
        
        for idx, mask_tensor in enumerate(masks):
            # Get class ID
            if cls_ids is not None and idx < len(cls_ids):
                cls = int(cls_ids[idx].item())
            else:
                cls = 0  # Default to chip
            
            color = colors.get(cls, (255, 0, 0))
            
            # Convertir le mask en numpy array
            if hasattr(mask_tensor, 'cpu'):
                mask_np = mask_tensor.cpu().numpy()
            elif hasattr(mask_tensor, 'numpy'):
                mask_np = mask_tensor.numpy()
            else:
                mask_np = np.array(mask_tensor)
            
            # Redimensionner si nécessaire
            if mask_np.ndim == 3:
                mask_np = mask_np[0]  # Remove channel dimension if present
                
            if mask_np.shape != image.shape[:2]:
                mask_np = cv2.resize(mask_np, (image.shape[1], image.shape[0]))
            
            # Convertir en uint8 (0-255)
            mask_np = (mask_np * 255).astype(np.uint8)
            
            # Trouver les contours
            contours, _ = cv2.findContours(mask_np, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            logger.info(f"Processing mask {idx} (class {cls}): {len(contours)} contours found")
            
            # Dessiner les contours
            if len(contours) > 0:
                cv2.drawContours(output, contours, -1, color, 2)  # Épaisseur: 2
        
        # Sauvegarder l'image avec contours
        mask_filename = os.path.basename(image_path).rsplit('.', 1)[0] + '_mask.png'
        mask_path = os.path.join(current_app.config['UPLOAD_FOLDER'], mask_filename)
        success = cv2.imwrite(mask_path, output)
        
        if success:
            logger.info(f"✓ Generated segmentation mask: {mask_path}")
            return mask_path
        else:
            logger.error(f"Failed to write mask image: {mask_path}")
            return None
        
    except Exception as e:
        logger.error(f"Error generating segmentation image: {e}", exc_info=True)
        return None

@predict_bp.route('/predict', methods=['POST'])
def predict():
    """
    Predict on uploaded image
    
    Returns:
    {
        "status": "success",
        "image_id": "uuid",
        "predictions": [
            {
                "class": "hole",
                "confidence": 0.95,
                "box": [x1, y1, x2, y2],
                "mask": [...polygon...]
            }
        ],
        "statistics": {
            "chip_area_pixels": 45000,
            "holes_area_pixels": 6800,
            "void_rate": 15.1,
            "chip_percentage": 84.9,
            "holes_percentage": 15.1
        }
    }
    """
    try:
        # Check if file exists (check both 'file' and 'image' keys for compatibility)
        if 'image' not in request.files and 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files.get('image') or request.files.get('file')
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_id = f"{timestamp}_{filename}"
        
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_id)
        file.save(upload_path)
        
        logger.info(f"Processing image: {image_id}")
        
        try:
            # Run YOLO inference and calculate void rate
            void_rate_calc = VoidRateCalculator(MODEL_PATH)
            void_rate_result = void_rate_calc.calculate_void_rate(upload_path, verbose=False)
            
            logger.info(f"Void rate result type: {type(void_rate_result)}")
            logger.info(f"Void rate result: {void_rate_result}")
            
            if void_rate_result is None:
                logger.error("void_rate_result is None!")
                return jsonify({'status': 'error', 'message': 'Void rate calculation returned None'}), 500
            
            # Try to generate segmentation image with contours
            mask_image_path = None
            if void_rate_result.get('num_chips', 0) > 0 or void_rate_result.get('num_holes', 0) > 0:
                # Only generate mask image if there are detections
                mask_image_path = generate_segmentation_image(upload_path, void_rate_result)
            
            # Set mask_url: only different if mask was actually generated
            # If no detections, mask_url is None to signal frontend to use original image
            mask_image_url = f'/uploads/{os.path.basename(mask_image_path)}' if mask_image_path else None
            
            # Calculate percentages
            chip_area = void_rate_result.get('chip_area_pixels', 1)  # Avoid division by 0
            holes_area = void_rate_result.get('hole_area_pixels', 0)
            total_area = chip_area + holes_area if (chip_area + holes_area) > 0 else 1
            
            chip_percentage = (chip_area / total_area) * 100 if total_area > 0 else 0
            holes_percentage = (holes_area / total_area) * 100 if total_area > 0 else 0
            
            # Prepare response - matching frontend expectations
            response = {
                'status': 'success',
                'result': {
                    'void_rate': float(void_rate_result.get('void_rate', 0)),
                    'chip_area': int(chip_area),
                    'holes_area': int(holes_area),
                    'chip_percentage': float(chip_percentage),
                    'holes_percentage': float(holes_percentage),
                    'confidence': 0.85,  # Default confidence
                    'num_chips': int(void_rate_result.get('num_chips', 0)),
                    'num_holes': int(void_rate_result.get('num_holes', 0))
                },
                'image_id': image_id,
                'timestamp': timestamp,
                'image_url': f'/uploads/{image_id}',
                'mask_url': mask_image_url
            }
            
            # Save prediction results
            results_file = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{image_id}_results.json")
            with open(results_file, 'w') as f:
                json.dump(response, f, indent=2)
            
            logger.info(f"Prediction successful for {image_id}")
            return jsonify(response), 200
            
        except Exception as e:
            logger.error(f"Error in predict: {str(e)}", exc_info=True)
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@predict_bp.route('/predict-batch', methods=['POST'])
def predict_batch():
    """
    Batch prediction on multiple images
    """
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        results = []
        
        for file in files:
            if file and allowed_file(file.filename):
                # Save and predict
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S%f')
                image_id = f"{timestamp}_{filename}"
                
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_id)
                file.save(upload_path)
                
                # Predict
                model = get_yolo_model()
                pred_results = model.predict(upload_path)
                void_rate_result = model.calculate_void_rate(pred_results)
                
                results.append({
                    'image_id': image_id,
                    'predictions': pred_results['detections'],
                    'statistics': void_rate_result
                })
        
        logger.info(f"Batch prediction: {len(results)} images processed")
        return jsonify({
            'status': 'success',
            'count': len(results),
            'results': results
        }), 200
    
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        return jsonify({'error': f'Batch prediction failed: {str(e)}'}), 500
