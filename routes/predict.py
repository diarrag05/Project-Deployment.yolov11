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

# Setup
predict_bp = Blueprint('predict', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

# Import YOLO inference
from utils.yolo_inference import YOLOInference

# Initialize YOLO
yolo_model = YOLOInference('models/yolov8n-seg_trained.pt')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        # Check if file exists
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
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
        
        # Run YOLO inference
        results = yolo_model.predict(upload_path)
        
        # Calculate void rate
        void_rate_result = yolo_model.calculate_void_rate(results)
        
        # Prepare response
        response = {
            'status': 'success',
            'image_id': image_id,
            'timestamp': timestamp,
            'predictions': results['detections'],
            'statistics': void_rate_result,
            'image_url': f'/uploads/{image_id}'
        }
        
        # Save prediction results
        results_file = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{image_id}_results.json")
        with open(results_file, 'w') as f:
            json.dump(response, f, indent=2)
        
        logger.info(f"Prediction successful for {image_id}")
        return jsonify(response), 200
    
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
                pred_results = yolo_model.predict(upload_path)
                void_rate_result = yolo_model.calculate_void_rate(pred_results)
                
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
