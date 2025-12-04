"""
Feedback API Routes for Active Learning
POST /api/feedback - Submit feedback
GET /api/feedback - Get feedback statistics
"""

from flask import Blueprint, request, jsonify
import logging
from utils.feedback_manager import FeedbackManager

logger = logging.getLogger(__name__)

feedback_bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')
feedback_manager = FeedbackManager()


@feedback_bp.route('', methods=['POST'])
def submit_feedback():
    """
    Submit feedback on a prediction
    
    Expected JSON:
    {
        "image_filename": "image.jpg",
        "prediction": {...},
        "user_feedback": "correct|incorrect|partial|unsure",
        "confidence": 0.8,
        "notes": "optional notes"
    }
    """
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['image_filename', 'user_feedback', 'prediction']):
            return jsonify({"error": "Missing required fields"}), 400
        
        result = feedback_manager.add_feedback(
            image_filename=data['image_filename'],
            prediction=data['prediction'],
            user_feedback=data['user_feedback'],
            confidence=data.get('confidence', 1.0),
            notes=data.get('notes')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        return jsonify({"error": str(e)}), 500


@feedback_bp.route('', methods=['GET'])
def get_feedback_stats():
    """Get feedback statistics and recommendations"""
    try:
        stats = feedback_manager.get_stats()
        recommendation = feedback_manager.get_training_candidates()
        
        return jsonify({
            "stats": stats,
            "recommendation": recommendation
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting feedback stats: {e}")
        return jsonify({"error": str(e)}), 500


@feedback_bp.route('/pending', methods=['GET'])
def get_pending_feedback():
    """Get all pending feedback records"""
    try:
        limit = request.args.get('limit', default=None, type=int)
        pending = feedback_manager.get_pending_feedback(limit=limit)
        
        return jsonify({
            "count": len(pending),
            "feedback": pending
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting pending feedback: {e}")
        return jsonify({"error": str(e)}), 500


@feedback_bp.route('/incorrect', methods=['GET'])
def get_incorrect_predictions():
    """Get predictions marked as incorrect (for retraining)"""
    try:
        limit = request.args.get('limit', default=50, type=int)
        incorrect = feedback_manager.get_incorrect_predictions(limit=limit)
        
        return jsonify({
            "count": len(incorrect),
            "predictions": incorrect
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting incorrect predictions: {e}")
        return jsonify({"error": str(e)}), 500


@feedback_bp.route('/mark-processed', methods=['POST'])
def mark_processed():
    """Mark feedback records as processed (used for training)"""
    try:
        data = request.get_json()
        record_ids = data.get('record_ids', [])
        
        if not record_ids:
            return jsonify({"error": "No record IDs provided"}), 400
        
        result = feedback_manager.mark_as_processed(record_ids)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logger.error(f"Error marking feedback: {e}")
        return jsonify({"error": str(e)}), 500


@feedback_bp.route('/export', methods=['POST'])
def export_feedback():
    """Export feedback data for model retraining"""
    try:
        output_path = request.json.get('output_path', 'feedback_export.json')
        
        result = feedback_manager.export_feedback_for_training(output_path)
        
        if result['success']:
            return jsonify({
                "success": True,
                "count": result['count'],
                "file": output_path
            }), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logger.error(f"Error exporting feedback: {e}")
        return jsonify({"error": str(e)}), 500


@feedback_bp.route('/clear', methods=['POST'])
def clear_feedback():
    """Clear feedback records"""
    try:
        keep_processed = request.json.get('keep_processed', True)
        
        result = feedback_manager.clear_feedback(keep_processed=keep_processed)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logger.error(f"Error clearing feedback: {e}")
        return jsonify({"error": str(e)}), 500
