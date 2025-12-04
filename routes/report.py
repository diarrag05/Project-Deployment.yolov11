"""
Route: Report
GET /api/report - Export CSV report
"""

from flask import Blueprint, request, jsonify, send_file, current_app
import csv
import os
from datetime import datetime
from io import StringIO
import logging

report_bp = Blueprint('report', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

from utils.storage_manager import StorageManager

storage = StorageManager()

@report_bp.route('/report/csv', methods=['GET'])
def export_csv():
    """
    Export void rate report as CSV
    
    CSV columns:
    - Image Name
    - Chip Area (pixels)
    - Holes Area (pixels)
    - Void Rate (%)
    - Confidence
    - Timestamp
    """
    try:
        # Get all predictions
        predictions = storage.get_all_predictions()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Image Name',
            'Chip Area (pixels)',
            'Holes Area (pixels)',
            'Void Rate (%)',
            'Confidence',
            'Timestamp'
        ])
        
        # Write data
        for pred in predictions:
            writer.writerow([
                pred.get('image_name', ''),
                pred.get('chip_area', 0),
                pred.get('holes_area', 0),
                pred.get('void_rate', 0),
                pred.get('confidence', 0),
                pred.get('timestamp', '')
            ])
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"void_rate_report_{timestamp}.csv"
        filepath = os.path.join(current_app.config['REPORTS_FOLDER'], filename)
        
        with open(filepath, 'w') as f:
            f.write(output.getvalue())
        
        logger.info(f"CSV report exported: {filename}")
        
        return send_file(
            filepath,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        logger.error(f"CSV export error: {str(e)}")
        return jsonify({'error': f'CSV export failed: {str(e)}'}), 500

@report_bp.route('/report/summary', methods=['GET'])
def report_summary():
    """
    Get summary statistics
    """
    try:
        predictions = storage.get_all_predictions()
        
        if not predictions:
            return jsonify({
                'status': 'success',
                'summary': {
                    'total_images': 0,
                    'avg_void_rate': 0,
                    'min_void_rate': 0,
                    'max_void_rate': 0
                }
            }), 200
        
        void_rates = [p.get('void_rate', 0) for p in predictions]
        
        return jsonify({
            'status': 'success',
            'summary': {
                'total_images': len(predictions),
                'avg_void_rate': sum(void_rates) / len(void_rates),
                'min_void_rate': min(void_rates),
                'max_void_rate': max(void_rates),
                'total_chip_area': sum(p.get('chip_area', 0) for p in predictions),
                'total_holes_area': sum(p.get('holes_area', 0) for p in predictions),
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Summary error: {str(e)}")
        return jsonify({'error': f'Failed to get summary: {str(e)}'}), 500

@report_bp.route('/report/json', methods=['GET'])
def export_json():
    """
    Export report as JSON
    """
    try:
        predictions = storage.get_all_predictions()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"void_rate_report_{timestamp}.json"
        filepath = os.path.join(current_app.config['REPORTS_FOLDER'], filename)
        
        with open(filepath, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'count': len(predictions),
                'predictions': predictions
            }, f, indent=2)
        
        logger.info(f"JSON report exported: {filename}")
        
        return send_file(
            filepath,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        logger.error(f"JSON export error: {str(e)}")
        return jsonify({'error': f'JSON export failed: {str(e)}'}), 500
