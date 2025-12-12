"""
Flask application for chip-and-hole detection system.
Provides REST API for image analysis, segmentation, validation, and retraining.
"""
from flask import Flask, render_template
from flask_cors import CORS
import sys
from pathlib import Path

# Add parent directory to path so 'api' module can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))
# Add backend directory to path
# sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from backend.src.config import Config
from backend.src.utils.logger import get_logger
from routes import api_bp
from storage import StorageManager
from training_job import TrainingJobManager

# Initialize logger
logger = get_logger(__name__)


def create_app():
    """Create and configure Flask application."""
    logger.info("Initializing Flask application...")
    app = Flask(__name__, 
            template_folder=str(Path(__file__).parent.parent / 'frontend'))
    
    # Configuration from environment variables
    max_upload_size = Config.FLASK_MAX_UPLOAD_SIZE * 1024 * 1024
    app.config['MAX_CONTENT_LENGTH'] = max_upload_size
    app.config['UPLOAD_FOLDER'] = Config.OUTPUT_DIR / 'uploads'
    app.config['VALIDATED_IMAGES_DIR'] = Config.OUTPUT_DIR / 'validated_images'
    app.config['ENV'] = Config.FLASK_ENV
    app.config['DEBUG'] = Config.FLASK_DEBUG
    
    # Ensure upload directories exist
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
    Path(app.config['VALIDATED_IMAGES_DIR']).mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    logger.info(f"Validated images dir: {app.config['VALIDATED_IMAGES_DIR']}")
    
    # Enable CORS for frontend integration
    CORS(app)
    
    # Initialize managers
    app.storage_manager = StorageManager(app.config['VALIDATED_IMAGES_DIR'])
    app.training_job_manager = TrainingJobManager()
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        """Serve the web interface."""
        return render_template('index.html')
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return {'status': 'healthy'}
    
    logger.info("Flask application initialized successfully")
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        debug=Config.FLASK_DEBUG,
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT
    )

