"""
Route: Relabel with SAM
POST /api/relabel - Launch SAM for re-segmentation
"""

from flask import Blueprint, request, jsonify, current_app
import json
import os
from pathlib import Path
import logging

relabel_bp = Blueprint('relabel', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

from utils.sam_handler import SAMHandler

# Initialize SAM
sam_handler = SAMHandler()

@relabel_bp.route('/relabel', methods=['POST'])
def relabel():
    """
    Relabel image using SAM
    
    Input:
    {
        "image_id": "timestamp_filename",
        "points": [[x, y], ...] (optional - for guided segmentation),
        "boxes": [[x1, y1, x2, y2], ...] (optional)
    }
    
    Returns:
    {
        "status": "success",
        "image_id": "timestamp_filename",
        "masks": [
            {
                "mask": [polygon_points],
                "confidence": 0.95,
                "area": 12000
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
            return jsonify({'error': 'Image not found'}), 404
        
        # Get SAM masks
        points = data.get('points', None)
        boxes = data.get('boxes', None)
        
        masks = sam_handler.segment(
            image_path,
            points=points,
            boxes=boxes
        )
        
        logger.info(f"SAM segmentation for {image_id}: {len(masks)} masks")
        
        return jsonify({
            'status': 'success',
            'image_id': image_id,
            'masks': masks,
            'count': len(masks)
        }), 200
    
    except Exception as e:
        logger.error(f"Relabel error: {str(e)}")
        return jsonify({'error': f'Relabel failed: {str(e)}'}), 500

@relabel_bp.route('/relabel-auto', methods=['POST'])
def relabel_auto():
    """
    Automatic relabeling using SAM on full image
    """
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        
        if not image_id:
            return jsonify({'error': 'image_id required'}), 400
        
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_id)
        if not os.path.exists(image_path):
            return jsonify({'error': 'Image not found'}), 404
        
        # Get all masks from SAM
        masks = sam_handler.segment_all(image_path)
        
        logger.info(f"Auto relabel for {image_id}: {len(masks)} masks found")
        
        return jsonify({
            'status': 'success',
            'image_id': image_id,
            'masks': masks,
            'count': len(masks)
        }), 200
    
    except Exception as e:
        logger.error(f"Auto relabel error: {str(e)}")
        return jsonify({'error': f'Auto relabel failed: {str(e)}'}), 500
