"""
Route: Train
POST /api/train - Trigger retraining with new labeled data
"""

from flask import Blueprint, request, jsonify, current_app
import json
import os
from datetime import datetime
import logging
import threading

train_bp = Blueprint('train', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

from utils.retrain_pipeline import RetrainingPipeline

# Initialize retraining pipeline
retrain_pipeline = RetrainingPipeline()

# Track training status
training_status = {
    'is_training': False,
    'progress': 0,
    'status': 'idle',
    'started_at': None,
    'current_epoch': 0,
    'total_epochs': 0
}

def retrain_worker(num_epochs, learning_rate):
    """Background worker for retraining"""
    global training_status
    try:
        training_status['is_training'] = True
        training_status['status'] = 'training'
        training_status['started_at'] = datetime.now().isoformat()
        
        # Run retraining
        results = retrain_pipeline.retrain(
            num_epochs=num_epochs,
            learning_rate=learning_rate,
            progress_callback=lambda e, total: update_progress(e, total)
        )
        
        training_status['status'] = 'completed'
        training_status['is_training'] = False
        training_status['progress'] = 100
        
        logger.info(f"Retraining completed: {results}")
    
    except Exception as e:
        logger.error(f"Retraining error: {str(e)}")
        training_status['status'] = 'error'
        training_status['is_training'] = False

def update_progress(epoch, total_epochs):
    """Update training progress"""
    global training_status
    training_status['current_epoch'] = epoch
    training_status['total_epochs'] = total_epochs
    training_status['progress'] = int((epoch / total_epochs) * 100)
    logger.info(f"Training progress: {epoch}/{total_epochs}")

@train_bp.route('/train', methods=['POST'])
def train():
    """
    Trigger retraining with new labeled data
    
    Input:
    {
        "num_epochs": 10,
        "learning_rate": 0.001,
        "batch_size": 4
    }
    
    Returns:
    {
        "status": "success",
        "message": "Training started",
        "training_id": "uuid"
    }
    """
    try:
        global training_status
        
        if training_status['is_training']:
            return jsonify({'error': 'Training already in progress'}), 400
        
        data = request.get_json() or {}
        num_epochs = data.get('num_epochs', 10)
        learning_rate = data.get('learning_rate', 0.001)
        batch_size = data.get('batch_size', 4)
        
        # Start retraining in background
        training_thread = threading.Thread(
            target=retrain_worker,
            args=(num_epochs, learning_rate)
        )
        training_thread.daemon = True
        training_thread.start()
        
        logger.info(f"Training started: {num_epochs} epochs, lr={learning_rate}")
        
        return jsonify({
            'status': 'success',
            'message': 'Training started',
            'training_id': datetime.now().isoformat(),
            'epochs': num_epochs,
            'learning_rate': learning_rate
        }), 202
    
    except Exception as e:
        logger.error(f"Train start error: {str(e)}")
        return jsonify({'error': f'Training failed: {str(e)}'}), 500

@train_bp.route('/train/status', methods=['GET'])
def train_status():
    """
    Get training status
    """
    try:
        return jsonify({
            'status': 'success',
            'training': training_status
        }), 200
    
    except Exception as e:
        logger.error(f"Status error: {str(e)}")
        return jsonify({'error': f'Failed to get status: {str(e)}'}), 500

@train_bp.route('/train/cancel', methods=['POST'])
def train_cancel():
    """
    Cancel ongoing training
    """
    try:
        global training_status
        if training_status['is_training']:
            retrain_pipeline.cancel()
            training_status['is_training'] = False
            training_status['status'] = 'cancelled'
            return jsonify({'status': 'success', 'message': 'Training cancelled'}), 200
        else:
            return jsonify({'error': 'No training in progress'}), 400
    
    except Exception as e:
        logger.error(f"Cancel error: {str(e)}")
        return jsonify({'error': f'Failed to cancel: {str(e)}'}), 500

@train_bp.route('/train/history', methods=['GET'])
def train_history():
    """
    Get training history
    """
    try:
        history = retrain_pipeline.get_history()
        return jsonify({
            'status': 'success',
            'history': history
        }), 200
    
    except Exception as e:
        logger.error(f"History error: {str(e)}")
        return jsonify({'error': f'Failed to get history: {str(e)}'}), 500
