"""
API routes for chip-and-hole detection system.
"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
import uuid

from backend.src.services import (
    YOLOInferenceService,
    VoidRateCalculator,
    SAMSegmentationService,
    LabelManager,
    TrainingService
)
from backend.src.config import Config
from backend.src.utils.export_utils import export_results_to_csv
from storage import StorageManager
from training_job import TrainingJobManager


api_bp = Blueprint('api', __name__)


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@api_bp.route('/analyze', methods=['POST'])
def analyze_image():
    """
    Analyze an image with YOLO and calculate void rate.
    
    Request:
        - file: Image file (multipart/form-data)
        - threshold: Optional void rate threshold (float)
    
    Returns:
        JSON with analysis results
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # Save uploaded file temporarily
        upload_dir = Path(current_app.config['UPLOAD_FOLDER'])
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = upload_dir / unique_filename
        file.save(str(file_path))
        
        # Get threshold if provided
        threshold = request.form.get('threshold', type=float)
        
        # Check if model exists, if not, start initial training
        if not Config.DEFAULT_MODEL.exists():
            # Check if training is already in progress
            job_manager: TrainingJobManager = current_app.training_job_manager
            if job_manager.is_training_in_progress():
                return jsonify({
                    'error': 'No model found. Initial training is already in progress. Please wait for training to complete.',
                    'training_id': job_manager.get_latest_training().training_id if job_manager.get_latest_training() else None
                }), 503
            
            # Start initial training automatically
            from backend.src.utils.logger import get_logger
            logger = get_logger(__name__)
            logger.info("No model found. Starting initial training automatically...")
            
            training_id = job_manager.start_training(
                epochs=Config.TRAINING_EPOCHS,
                batch_size=Config.TRAINING_BATCH_SIZE,
                patience=Config.TRAINING_PATIENCE
            )
            
            return jsonify({
                'error': 'No model found. Initial training has been started automatically.',
                'training_id': training_id,
                'message': 'Please wait for training to complete, then try again.'
            }), 503
        
        # Run inference
        inference_service = YOLOInferenceService()
        inference_result = inference_service.predict(str(file_path), save_output=True)
        
        # Calculate void rate
        calculator = VoidRateCalculator(threshold=threshold)
        analysis = calculator.analyze_chip(inference_result, save_annotated_image=True)
        
        # Prepare response with mask info for validation
        response = {
            'image_path': analysis.image_path,
            'output_image_path': analysis.output_image_path,
            'statistics': analysis.statistics.dict(),
            'is_usable': analysis.is_usable,
            'threshold': analysis.threshold,
            'num_detections': inference_result.num_detections,
            'processing_time': inference_result.processing_time,
            'masks_info': [mask.dict() for mask in inference_result.masks]
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/analyze/batch', methods=['POST'])
def analyze_batch():
    """
    Analyze multiple images.
    
    Request:
        - files: Multiple image files (multipart/form-data)
        - threshold: Optional void rate threshold (float)
    
    Returns:
        JSON with list of analysis results
    """
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400
    
    try:
        threshold = request.form.get('threshold', type=float)
        upload_dir = Path(current_app.config['UPLOAD_FOLDER'])
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        inference_service = YOLOInferenceService()
        calculator = VoidRateCalculator(threshold=threshold)
        
        for file in files:
            if not allowed_file(file.filename):
                continue
            
            # Save file
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = upload_dir / unique_filename
            file.save(str(file_path))
            
            # Analyze
            inference_result = inference_service.predict(str(file_path), save_output=True)
            analysis = calculator.analyze_chip(inference_result, save_annotated_image=True)
            
            results.append({
                'image_path': analysis.image_path,
                'output_image_path': analysis.output_image_path,
                'statistics': analysis.statistics.dict(),
                'is_usable': analysis.is_usable,
                'threshold': analysis.threshold
            })
        
        return jsonify({'results': results, 'count': len(results)}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/segment', methods=['POST'])
def segment_image():
    """
    Segment an image using SAM (guided mode only).
    
    Request:
        - file: Image file (multipart/form-data)
        - points: JSON array of [x, y] points (required)
        - point_labels: JSON array of labels (1=foreground, 0=background)
    
    Returns:
        JSON with segmentation results
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # Save uploaded file
        upload_dir = Path(current_app.config['UPLOAD_FOLDER'])
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = upload_dir / unique_filename
        file.save(str(file_path))
        
        sam_service = SAMSegmentationService()
        
        # Guided mode only - require points
        points_json = request.form.get('points')
        labels_json = request.form.get('point_labels')
        
        if not points_json:
            return jsonify({'error': 'Points required for segmentation'}), 400
        
        import json
        points = json.loads(points_json)
        point_labels = json.loads(labels_json) if labels_json else [1] * len(points)
        
        result = sam_service.segment_guided(str(file_path), points, point_labels)
        
        response = {
            'image_path': result.image_path,
            'output_image_path': result.output_image_path,
            'num_masks': result.num_masks,
            'mode': 'guided',
            'processing_time': result.processing_time,
            'points': points,
            'point_labels': point_labels
        }
        
        return jsonify(response), 200
        
    except ImportError:
        return jsonify({'error': 'SAM not available. Please install segment-anything.'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/validate/from-segmentation', methods=['POST'])
def validate_from_segmentation():
    """
    Validate an image directly from SAM segmentation results (guided mode only).
    
    Request:
        - image_path: Path to the segmented image
        - points: JSON array of [x, y] points (required)
        - point_labels: JSON array of labels (1=foreground, 0=background)
        - class_id: Optional class ID (default: chip class)
    
    Returns:
        JSON with storage ID
    """
    try:
        import json
        import numpy as np
        from backend.src.utils.image_utils import load_image
        
        image_path = request.json.get('image_path') if request.is_json else request.form.get('image_path')
        if not image_path:
            return jsonify({'error': 'image_path required'}), 400
        
        image_path = Path(image_path)
        if not image_path.exists():
            return jsonify({'error': 'Image not found'}), 404
        
        # Load image to get dimensions
        image = load_image(str(image_path))
        image_height, image_width = image.shape[:2]
        
        # Re-run SAM segmentation to get masks (guided mode only)
        sam_service = SAMSegmentationService()
        masks = []
        class_ids = []
        
        # Guided mode only - require points
        points_json = request.json.get('points') if request.is_json else request.form.get('points')
        labels_json = request.json.get('point_labels') if request.is_json else request.form.get('point_labels')
        
        if not points_json:
            return jsonify({'error': 'Points required for segmentation'}), 400
        
        points = json.loads(points_json) if isinstance(points_json, str) else points_json
        point_labels = json.loads(labels_json) if labels_json and isinstance(labels_json, str) else (labels_json if labels_json else [1] * len(points))
        
        # Re-run guided segmentation
        result = sam_service.segment_guided(
            str(image_path),
            points=points,
            point_labels=point_labels,
            save_output=False
        )
        
        # Re-run to get actual mask
        import cv2
        image_rgb = image if len(image.shape) == 3 else cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        sam_service.predictor.set_image(image_rgb)
        
        input_points = np.array(points)
        input_labels = np.array(point_labels)
        
        mask_results, scores, logits = sam_service.predictor.predict(
            point_coords=input_points,
            point_labels=input_labels,
            multimask_output=True
        )
        
        # Use best mask
        best_mask_idx = np.argmax(scores)
        best_mask = mask_results[best_mask_idx]
        
        # Get class ID (default to chip)
        provided_class_id = request.json.get('class_id') if request.is_json else request.form.get('class_id')
        class_id = int(provided_class_id) if provided_class_id else Config.CHIP_CLASS_ID
        
        masks.append(best_mask.astype(bool))
        class_ids.append(class_id)
        
        if not masks:
            return jsonify({'error': 'No masks found to validate'}), 400
        
        # Save labels
        label_manager = LabelManager()
        labels_path = label_manager.save_labels_from_masks(
            masks,
            class_ids,
            image_path,
            image_width=image_width,
            image_height=image_height
        )
        
        # Get metadata
        metadata_json = request.json.get('metadata', '{}') if request.is_json else request.form.get('metadata', '{}')
        metadata = json.loads(metadata_json) if isinstance(metadata_json, str) else (metadata_json or {})
        metadata['segmentation_mode'] = 'guided'
        
        # Save to storage
        storage_manager: StorageManager = current_app.storage_manager
        storage_id = storage_manager.save_validated_image(
            image_path,
            labels_path,
            metadata
        )
        
        return jsonify({
            'storage_id': storage_id,
            'image_path': str(image_path),
            'labels_path': str(labels_path),
            'message': 'Image validated and saved for retraining',
            'num_masks': len(masks)
        }), 200
        
    except ImportError:
        return jsonify({'error': 'SAM not available. Please install segment-anything.'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/validate', methods=['POST'])
def validate_image():
    """
    Validate and save an image with corrected labels for retraining.
    
    Request:
        - image_path: Path to the image (or file upload)
        - labels: JSON array of label objects with masks and class_ids
        - metadata: Optional JSON metadata
    
    Returns:
        JSON with storage ID
    """
    try:
        import json
        import numpy as np
        from src.utils.image_utils import load_image
        
        # Handle file upload or path
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            upload_dir = Path(current_app.config['UPLOAD_FOLDER'])
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            image_path = upload_dir / unique_filename
            file.save(str(image_path))
        else:
            image_path = Path(request.form.get('image_path'))
            if not image_path.exists():
                return jsonify({'error': 'Image not found'}), 404
        
        # Get labels
        labels_json = request.form.get('labels')
        if not labels_json:
            return jsonify({'error': 'Labels required'}), 400
        
        labels_data = json.loads(labels_json)
        
        # Convert labels to masks
        image = load_image(str(image_path))
        image_height, image_width = image.shape[:2]
        
        masks = []
        class_ids = []
        
        for label_data in labels_data:
            # Expect polygon points in normalized YOLO format
            if 'polygon' in label_data:
                # Convert normalized polygon to mask
                polygon = label_data['polygon']
                class_id = label_data['class_id']
                
                # Convert to absolute coordinates
                abs_polygon = []
                for i in range(0, len(polygon), 2):
                    x = int(polygon[i] * image_width)
                    y = int(polygon[i+1] * image_height)
                    abs_polygon.append([x, y])
                
                # Create mask from polygon
                import cv2
                mask = np.zeros((image_height, image_width), dtype=np.uint8)
                cv2.fillPoly(mask, [np.array(abs_polygon, dtype=np.int32)], 255)
                masks.append(mask.astype(bool))
                class_ids.append(class_id)
        
        # Save labels
        label_manager = LabelManager()
        labels_path = label_manager.save_labels_from_masks(
            masks,
            class_ids,
            image_path,
            image_width=image_width,
            image_height=image_height
        )
        
        # Get metadata
        metadata_json = request.form.get('metadata', '{}')
        metadata = json.loads(metadata_json)
        
        # Save to storage
        storage_manager: StorageManager = current_app.storage_manager
        storage_id = storage_manager.save_validated_image(
            image_path,
            labels_path,
            metadata
        )
        
        return jsonify({
            'storage_id': storage_id,
            'image_path': str(image_path),
            'labels_path': str(labels_path),
            'message': 'Image validated and saved for retraining'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/retrain', methods=['POST'])
def retrain():
    """
    Start model retraining with validated images.
    
    Request:
        - epochs: Optional number of epochs (int)
        - batch_size: Optional batch size (int)
        - patience: Optional early stopping patience (int)
        - move_validated: Whether to move validated images to dataset (bool, default: True)
    
    Returns:
        JSON with training job ID
    """
    try:
        # Check if training is already in progress
        job_manager: TrainingJobManager = current_app.training_job_manager
        if job_manager.is_training_in_progress():
            return jsonify({
                'error': 'Training already in progress',
                'latest_training': job_manager.get_latest_training().dict() if job_manager.get_latest_training() else None
            }), 409
        
        # Move validated images to dataset if requested
        move_validated = request.json.get('move_validated', True) if request.is_json else True
        
        if move_validated:
            storage_manager: StorageManager = current_app.storage_manager
            storage_manager.move_all_to_dataset()
        
        # Get training parameters
        epochs = request.json.get('epochs') if request.is_json else None
        batch_size = request.json.get('batch_size') if request.is_json else None
        patience = request.json.get('patience') if request.is_json else None
        
        # Start training
        training_id = job_manager.start_training(
            epochs=epochs,
            batch_size=batch_size,
            patience=patience
        )
        
        return jsonify({
            'training_id': training_id,
            'status': 'started',
            'message': 'Training job started'
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/training/status', methods=['GET'])
def training_status():
    """
    Get training status.
    
    Query params:
        - training_id: Optional training job ID (if not provided, returns latest)
    
    Returns:
        JSON with training status
    """
    try:
        job_manager: TrainingJobManager = current_app.training_job_manager
        
        training_id = request.args.get('training_id')
        
        if training_id:
            result = job_manager.get_training_status(training_id)
            if not result:
                return jsonify({'error': 'Training job not found'}), 404
        else:
            result = job_manager.get_latest_training()
            if not result:
                return jsonify({'message': 'No training jobs found'}), 200
        
        return jsonify(result.dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/validated-images', methods=['GET'])
def get_validated_images():
    """
    Get list of validated images waiting for retraining.
    
    Returns:
        JSON with list of validated images
    """
    try:
        storage_manager: StorageManager = current_app.storage_manager
        validated_images = storage_manager.get_validated_images()
        
        return jsonify({
            'count': len(validated_images),
            'images': validated_images
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/results/export', methods=['GET'])
def export_results():
    """
    Export analysis results to CSV.
    
    Query params:
        - format: 'csv' or 'json' (default: 'csv')
    
    Returns:
        CSV or JSON file
    """
    try:
        # This would typically fetch results from a database
        # For now, we'll export from the results directory
        results_dir = Config.RESULTS_DIR
        csv_path = results_dir / 'analysis_results.csv'
        
        if not csv_path.exists():
            return jsonify({'error': 'No results to export'}), 404
        
        return send_file(
            str(csv_path),
            mimetype='text/csv',
            as_attachment=True,
            download_name='analysis_results.csv'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/analyze/export-csv', methods=['POST'])
def export_analyze_results_csv():
    """
    Export analysis results to CSV format.
    
    Request body (JSON):
        - analysis_data: The analysis result data from /analyze endpoint
    
    Returns:
        CSV file download
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'JSON data required'}), 400
        
        data = request.json.get('analysis_data')
        if not data:
            return jsonify({'error': 'analysis_data required'}), 400
        
        import io
        import csv
        from datetime import datetime
        
        # Create CSV in memory
        output = io.StringIO()
        fieldnames = [
            'Image',
            'Component',
            'Area',
            'void %',
            'Max.void %',
            'Chips détectées',
            'Trous détectés',
            'Confiance moyenne'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        stats = data.get('statistics', {})
        image_path = Path(data.get('image_path', 'unknown'))
        image_name = image_path.name
        
        # Calculate max void % from all holes
        masks_info = data.get('masks_info', [])
        holes = [m for m in masks_info if m.get('class_id') == 1] if masks_info else []
        chip_area = stats.get('chip_area_pixels', 0)
        max_hole_area = max([h.get('area_pixels', 0) for h in holes], default=0)
        max_void_percent = (max_hole_area / chip_area * 100) if chip_area > 0 else 0.0
        
        # Write main row with global statistics
        writer.writerow({
            'Image': image_name,
            'Component': 'Global',
            'Area': chip_area,
            'void %': f"{stats.get('void_rate_percent', 0.0):.2f}",
            'Max.void %': f"{max_void_percent:.2f}",
            'Chips détectées': stats.get('num_chips', 0),
            'Trous détectés': stats.get('num_holes', 0),
            'Confiance moyenne': f"{(stats.get('average_confidence', 0.0) * 100):.1f}"
        })
        
        # If we have masks info, try to create per-component rows
        # masks_info already defined above
        if masks_info:
            # Group chips and holes
            chips = [m for m in masks_info if m.get('class_id') == 0]  # Assuming 0 is chip class
            holes = [m for m in masks_info if m.get('class_id') == 1]  # Assuming 1 is hole class
            
            # Helper function to check if a hole is inside a chip bbox
            def is_hole_in_chip(hole_bbox, chip_bbox):
                """Check if hole center is inside chip bbox."""
                if not hole_bbox or not chip_bbox or len(hole_bbox) < 4 or len(chip_bbox) < 4:
                    return False
                hole_center_x = (hole_bbox[0] + hole_bbox[2]) / 2
                hole_center_y = (hole_bbox[1] + hole_bbox[3]) / 2
                return (chip_bbox[0] <= hole_center_x <= chip_bbox[2] and
                        chip_bbox[1] <= hole_center_y <= chip_bbox[3])
            
            # For each chip, calculate void rate
            for idx, chip in enumerate(chips, 1):
                chip_area = chip.get('area_pixels', 0)
                chip_bbox = chip.get('bbox', [])
                
                # Find holes that belong to this chip using bbox intersection
                holes_in_chip = []
                for hole in holes:
                    hole_bbox = hole.get('bbox', [])
                    if is_hole_in_chip(hole_bbox, chip_bbox):
                        holes_in_chip.append(hole)
                
                # If no holes found with bbox method, use all holes as fallback
                if not holes_in_chip and holes:
                    holes_in_chip = holes
                
                total_holes_area = sum(h.get('area_pixels', 0) for h in holes_in_chip)
                max_hole_area = max([h.get('area_pixels', 0) for h in holes_in_chip], default=0)
                
                void_percent = (total_holes_area / chip_area * 100) if chip_area > 0 else 0.0
                max_void_percent = (max_hole_area / chip_area * 100) if chip_area > 0 else 0.0
                
                writer.writerow({
                    'Image': image_name if idx == 1 else '',  # Only show image name on first component
                    'Component': idx,
                    'Area': chip_area,
                    'void %': f"{void_percent:.2f}",
                    'Max.void %': f"{max_void_percent:.2f}",
                    'Chips détectées': '',
                    'Trous détectés': len(holes_in_chip),
                    'Confiance moyenne': f"{(chip.get('confidence', 0.0) * 100):.1f}"
                })
        
        # Prepare CSV response
        csv_data = output.getvalue()
        output.close()
        
        # Create response with CSV
        response = current_app.response_class(
            csv_data,
            mimetype='text/csv; charset=utf-8',
            headers={
                'Content-Disposition': f'attachment; filename=analysis_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        )
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/images/<path:image_path>', methods=['GET'])
def get_image(image_path: str):
    """
    Serve image files.
    
    Args:
        image_path: Relative path to image (can be just filename or relative path from outputs/)
    
    Returns:
        Image file
    """
    try:
        # Security: prevent directory traversal
        # Normalize path and get only the filename if it's a relative path
        path_obj = Path(image_path)
        
        # If it's just a filename, search in all directories
        if not path_obj.parent or path_obj.parent == Path('.'):
            filename = path_obj.name
            
            # Check in various directories
            possible_paths = [
                Config.INFERENCE_DIR / filename,
                Config.RESULTS_DIR / filename,
                Config.SAM_OUTPUT_DIR / filename,
                Path(current_app.config['UPLOAD_FOLDER']) / filename,
                Config.OUTPUT_DIR / 'validated_images' / 'images' / filename,
            ]
            
            for path in possible_paths:
                if path.exists() and path.is_file():
                    return send_file(str(path))
        else:
            # Try as relative path from outputs directory
            # Security: ensure path is within outputs directory
            try:
                full_path = Config.OUTPUT_DIR / path_obj
                # Resolve to ensure no directory traversal
                resolved_path = full_path.resolve()
                outputs_resolved = Config.OUTPUT_DIR.resolve()
                
                # Check if resolved path is within outputs directory
                if str(resolved_path).startswith(str(outputs_resolved)) and resolved_path.exists() and resolved_path.is_file():
                    return send_file(str(resolved_path))
            except (ValueError, OSError):
                pass
        
        return jsonify({'error': 'Image not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

