"""
Route: Validate
POST /api/validate - Validate and save labeled data
"""

from flask import Blueprint, request, jsonify, current_app
import json
import os
from datetime import datetime
import logging

validate_bp = Blueprint('validate', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

from utils.storage_manager import StorageManager

storage = StorageManager()

@validate_bp.route('/validate', methods=['POST'])
def validate():
    """
    Validate masks and save labeled data
    
    Input:
    {
        "image_id": "timestamp_filename",
        "masks": [...],
        "void_rate": float,
        "stats": {...}
    }
    
    Returns:
    {
        "status": "success",
        "image_id": "timestamp_filename",
        "label_id": "uuid",
        "saved": true
    }
    """
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        masks = data.get('masks', [])
        
        # Image ID is required
        if not image_id:
            return jsonify({'error': 'image_id is required'}), 400
        
        # Masks can be empty list - that's ok, just means no specific mask data
        # The important thing is we're logging this inference result
        
        # Save labeled data
        label_id = storage.save_labels(
            image_id=image_id,
            masks=masks,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Labels saved for {image_id}: {label_id}")
        
        return jsonify({
            'status': 'success',
            'image_id': image_id,
            'label_id': label_id,
            'saved': True
        }), 200
    
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({'error': f'Validation failed: {str(e)}'}), 500

@validate_bp.route('/validate-batch', methods=['POST'])
def validate_batch():
    """
    Batch validation for multiple labeled images
    """
    try:
        data = request.get_json()
        images = data.get('images', [])
        
        if not images:
            return jsonify({'error': 'No images provided'}), 400
        
        label_ids = []
        for img_data in images:
            label_id = storage.save_labels(
                image_id=img_data.get('image_id'),
                masks=img_data.get('masks', []),
                timestamp=datetime.now().isoformat()
            )
            label_ids.append(label_id)
        
        logger.info(f"Batch validation: {len(label_ids)} images saved")
        
        return jsonify({
            'status': 'success',
            'count': len(label_ids),
            'label_ids': label_ids
        }), 200
    
    except Exception as e:
        logger.error(f"Batch validation error: {str(e)}")
        return jsonify({'error': f'Batch validation failed: {str(e)}'}), 500

@validate_bp.route('/labels', methods=['GET'])
def get_labels():
    """
    Get all labeled data
    """
    try:
        labels = storage.get_all_labels()
        return jsonify({
            'status': 'success',
            'count': len(labels),
            'labels': labels
        }), 200
    
    except Exception as e:
        logger.error(f"Get labels error: {str(e)}")
        return jsonify({'error': f'Failed to get labels: {str(e)}'}), 500

@validate_bp.route('/labels/<label_id>', methods=['GET'])
def get_label(label_id):
    """
    Get specific label by ID
    """
    try:
        label = storage.get_label(label_id)
        if not label:
            return jsonify({'error': 'Label not found'}), 404
        
        return jsonify({
            'status': 'success',
            'label': label
        }), 200
    
    except Exception as e:
        logger.error(f"Get label error: {str(e)}")
        return jsonify({'error': f'Failed to get label: {str(e)}'}), 500
