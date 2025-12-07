"""
Flask API Backend - Void Rate Detection System
Main application file
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
LABELED_FOLDER = 'labeled_data'
MODELS_FOLDER = 'models'
REPORTS_FOLDER = 'reports'

# Create folders if they don't exist
for folder in [UPLOAD_FOLDER, LABELED_FOLDER, MODELS_FOLDER, REPORTS_FOLDER]:
    Path(folder).mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Import routes
from routes.predict import predict_bp
from routes.relabel import relabel_bp
from routes.validate import validate_bp
from routes.train import train_bp
from routes.report import report_bp
from routes.feedback import feedback_bp

# Register blueprints
app.register_blueprint(predict_bp)
app.register_blueprint(relabel_bp)
app.register_blueprint(validate_bp)
app.register_blueprint(train_bp)
app.register_blueprint(report_bp)
app.register_blueprint(feedback_bp)

# ============================================================================
# HOME ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/analysis')
def analysis():
    """Analysis page"""
    image_id = request.args.get('image_id', '')
    return render_template('analysis.html', image_id=image_id)

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')

@app.route('/feedback')
def feedback():
    """Feedback & Active Learning page"""
    return render_template('feedback.html')

# ============================================================================
# UPLOADS ROUTE - Serve uploaded images
# ============================================================================

@app.route('/uploads/<filename>')
def serve_upload(filename):
    """Serve uploaded files"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path)
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f"Error serving file {filename}: {str(e)}")
        return jsonify({'error': 'Error serving file'}), 500

# ============================================================================
# STATUS ROUTES
# ============================================================================

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'uploads_available': len(os.listdir(UPLOAD_FOLDER)),
            'labeled_data_available': len(os.listdir(LABELED_FOLDER)),
            'models_available': len(os.listdir(MODELS_FOLDER)),
        })
    except Exception as e:
        logger.error(f"Status error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'API is running'}), 200

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# DEBUG
# ============================================================================

if __name__ == '__main__':
    logger.info('Starting Flask API...')
    logger.info(f'Upload folder: {UPLOAD_FOLDER}')
    logger.info(f'Labeled data folder: {LABELED_FOLDER}')
    app.run(debug=False, host='0.0.0.0', port=5000)
