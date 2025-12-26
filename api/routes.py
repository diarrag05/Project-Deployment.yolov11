"""
FastAPI routes for chip-and-hole detection system.
"""
import os
import sys
import json
import uuid
import io
import csv
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Form, Request, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
import numpy as np
import cv2

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.src.services import (
    YOLOInferenceService,
    VoidRateCalculator,
    LabelManager,
    TrainingService
)
from api.sam_manager import get_sam_service
from backend.src.config import Config
from backend.src.utils.image_utils import load_image
from api.storage import StorageManager
from api.training_job import TrainingJobManager

router = APIRouter()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_managers(request: Request) -> tuple[StorageManager, TrainingJobManager, Path]:
    """Get managers from app state."""
    storage_manager: StorageManager = request.app.state.storage_manager
    training_job_manager: TrainingJobManager = request.app.state.training_job_manager
    upload_dir: Path = request.app.state.upload_dir
    return storage_manager, training_job_manager, upload_dir


@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    threshold: Optional[float] = Form(None),
    request: Request = ...
):
    """
    Analyze an image with YOLO and calculate void rate.
    
    Request:
        - file: Image file (multipart/form-data)
        - threshold: Optional void rate threshold (float)
    
    Returns:
        JSON with analysis results
    """
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    try:
        storage_manager, training_job_manager, upload_dir = get_managers(request)
        
        # Save uploaded file temporarily
        upload_dir.mkdir(parents=True, exist_ok=True)
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = upload_dir / unique_filename
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Check if model exists, if not, start initial training
        if not Config.DEFAULT_MODEL.exists():
            if training_job_manager.is_training_in_progress():
                latest = training_job_manager.get_latest_training()
                raise HTTPException(
                    status_code=503,
                    detail={
                        'error': 'No model found. Initial training is already in progress. Please wait for training to complete.',
                        'training_id': latest.training_id if latest else None
                    }
                )
            
            from backend.src.utils.logger import get_logger
            logger = get_logger(__name__)
            logger.info("No model found. Starting initial training automatically...")
            
            training_id = training_job_manager.start_training(
                epochs=Config.TRAINING_EPOCHS,
                batch_size=Config.TRAINING_BATCH_SIZE,
                patience=Config.TRAINING_PATIENCE
            )
            
            raise HTTPException(
                status_code=503,
                detail={
                    'error': 'No model found. Initial training has been started automatically.',
                    'training_id': training_id,
                    'message': 'Please wait for training to complete, then try again.'
                }
            )
        
        # Run inference
        inference_service = YOLOInferenceService()
        inference_result = inference_service.predict(str(file_path), save_output=True)
        
        # Calculate void rate
        calculator = VoidRateCalculator(threshold=threshold)
        analysis = calculator.analyze_chip(inference_result, save_annotated_image=True)
        
        # Prepare response
        return {
            'image_path': analysis.image_path,
            'output_image_path': analysis.output_image_path,
            'statistics': analysis.statistics.dict(),
            'is_usable': analysis.is_usable,
            'threshold': analysis.threshold,
            'num_detections': inference_result.num_detections,
            'processing_time': inference_result.processing_time,
            'masks_info': [mask.dict() for mask in inference_result.masks]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/batch")
async def analyze_batch(
    files: List[UploadFile] = File(...),
    threshold: Optional[float] = Form(None),
    request: Request = ...
):
    """
    Analyze multiple images.
    
    Request:
        - files: Multiple image files (multipart/form-data)
        - threshold: Optional void rate threshold (float)
    
    Returns:
        JSON with list of analysis results
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    try:
        storage_manager, training_job_manager, upload_dir = get_managers(request)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        inference_service = YOLOInferenceService()
        calculator = VoidRateCalculator(threshold=threshold)
        
        for file in files:
            if not allowed_file(file.filename):
                continue
            
            # Save file
            unique_filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = upload_dir / unique_filename
            
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
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
        
        return {'results': results, 'count': len(results)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/segment")
async def segment_image(
    file: UploadFile = File(...),
    points: str = Form(...),
    point_labels: Optional[str] = Form(None),
    class_id: Optional[int] = Form(None),
    request: Request = ...
):
    """
    Segment an image using SAM (guided mode only).
    
    Request:
        - file: Image file (multipart/form-data)
        - points: JSON array of [x, y] points (required)
        - point_labels: JSON array of labels (1=foreground, 0=background)
        - class_id: Optional class ID (0=chip, 1=hole)
    
    Returns:
        JSON with segmentation results
    """
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    try:
        storage_manager, training_job_manager, upload_dir = get_managers(request)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded file
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = upload_dir / unique_filename
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Use singleton SAM service (model loaded once, reused)
        sam_service = get_sam_service()
        
        # Parse points and labels
        points_list = json.loads(points)
        labels_list = json.loads(point_labels) if point_labels else [1] * len(points_list)
        
        result = sam_service.segment_guided(str(file_path), points_list, labels_list)
        
        return {
            'image_path': result.image_path,
            'output_image_path': result.output_image_path,
            'num_masks': result.num_masks,
            'mode': 'guided',
            'processing_time': result.processing_time,
            'points': points_list,
            'point_labels': labels_list
        }
        
    except ImportError:
        raise HTTPException(status_code=500, detail="SAM not available. Please install segment-anything.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate/from-segmentation")
async def validate_from_segmentation(
    image_path: str = Form(...),
    points: str = Form(...),
    point_labels: Optional[str] = Form(None),
    class_id: Optional[int] = Form(None),
    metadata: Optional[str] = Form("{}"),
    request: Request = ...
):
    """
    Validate an image directly from SAM segmentation results (guided mode only).
    
    Request:
        - image_path: Path to the segmented image
        - points: JSON array of [x, y] points (required)
        - point_labels: JSON array of labels (1=foreground, 0=background)
        - class_id: Optional class ID (default: chip class)
        - metadata: Optional JSON metadata
    
    Returns:
        JSON with storage ID
    """
    try:
        storage_manager, training_job_manager, upload_dir = get_managers(request)
        
        image_path_obj = Path(image_path)
        if not image_path_obj.exists():
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Load image to get dimensions
        image = load_image(str(image_path_obj))
        image_height, image_width = image.shape[:2]
        
        # Parse points and labels
        points_list = json.loads(points) if isinstance(points, str) else points
        labels_list = json.loads(point_labels) if point_labels and isinstance(point_labels, str) else (
            json.loads(point_labels) if point_labels else [1] * len(points_list)
        )
        
        # Re-run SAM segmentation (use singleton - model already loaded)
        sam_service = get_sam_service()
        result = sam_service.segment_guided(
            str(image_path_obj),
            points=points_list,
            point_labels=labels_list,
            save_output=False
        )
        
        # Get actual mask
        image_rgb = image if len(image.shape) == 3 else cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        sam_service.predictor.set_image(image_rgb)
        
        input_points = np.array(points_list)
        input_labels = np.array(labels_list)
        
        mask_results, scores, logits = sam_service.predictor.predict(
            point_coords=input_points,
            point_labels=input_labels,
            multimask_output=True
        )
        
        # Use best mask
        best_mask_idx = np.argmax(scores)
        best_mask = mask_results[best_mask_idx]
        
        # Get class ID
        class_id_final = class_id if class_id is not None else Config.CHIP_CLASS_ID
        
        masks = [best_mask.astype(bool)]
        class_ids = [class_id_final]
        
        if not masks:
            raise HTTPException(status_code=400, detail="No masks found to validate")
        
        # Save labels
        label_manager = LabelManager()
        labels_path = label_manager.save_labels_from_masks(
            masks,
            class_ids,
            image_path_obj,
            image_width=image_width,
            image_height=image_height
        )
        
        # Parse metadata
        metadata_dict = json.loads(metadata) if isinstance(metadata, str) else (metadata or {})
        metadata_dict['segmentation_mode'] = 'guided'
        
        # Save to storage
        storage_id = storage_manager.save_validated_image(
            image_path_obj,
            labels_path,
            metadata_dict
        )
        
        return {
            'storage_id': storage_id,
            'image_path': str(image_path_obj),
            'labels_path': str(labels_path),
            'message': 'Image validated and saved for retraining',
            'num_masks': len(masks)
        }
        
    except ImportError:
        raise HTTPException(status_code=500, detail="SAM not available. Please install segment-anything.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_image(
    image_path: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    labels: str = Form(...),
    metadata: Optional[str] = Form("{}"),
    request: Request = ...
):
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
        storage_manager, training_job_manager, upload_dir = get_managers(request)
        
        # Handle file upload or path
        if file:
            upload_dir.mkdir(parents=True, exist_ok=True)
            unique_filename = f"{uuid.uuid4()}_{file.filename}"
            image_path_obj = upload_dir / unique_filename
            
            with open(image_path_obj, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
        elif image_path:
            image_path_obj = Path(image_path)
            if not image_path_obj.exists():
                raise HTTPException(status_code=404, detail="Image not found")
        else:
            raise HTTPException(status_code=400, detail="Either file or image_path required")
        
        # Parse labels
        labels_data = json.loads(labels)
        
        # Convert labels to masks
        image = load_image(str(image_path_obj))
        image_height, image_width = image.shape[:2]
        
        masks = []
        class_ids = []
        
        for label_data in labels_data:
            if 'polygon' in label_data:
                polygon = label_data['polygon']
                class_id = label_data['class_id']
                
                # Convert to absolute coordinates
                abs_polygon = []
                for i in range(0, len(polygon), 2):
                    x = int(polygon[i] * image_width)
                    y = int(polygon[i+1] * image_height)
                    abs_polygon.append([x, y])
                
                # Create mask from polygon
                mask = np.zeros((image_height, image_width), dtype=np.uint8)
                cv2.fillPoly(mask, [np.array(abs_polygon, dtype=np.int32)], 255)
                masks.append(mask.astype(bool))
                class_ids.append(class_id)
        
        # Save labels
        label_manager = LabelManager()
        labels_path = label_manager.save_labels_from_masks(
            masks,
            class_ids,
            image_path_obj,
            image_width=image_width,
            image_height=image_height
        )
        
        # Parse metadata
        metadata_dict = json.loads(metadata)
        
        # Save to storage
        storage_id = storage_manager.save_validated_image(
            image_path_obj,
            labels_path,
            metadata_dict
        )
        
        return {
            'storage_id': storage_id,
            'image_path': str(image_path_obj),
            'labels_path': str(labels_path),
            'message': 'Image validated and saved for retraining'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retrain")
async def retrain(
    epochs: Optional[int] = None,
    batch_size: Optional[int] = None,
    patience: Optional[int] = None,
    move_validated: bool = True,
    request: Request = ...
):
    """
    Start model retraining with validated images.
    
    Request body (JSON):
        - epochs: Optional number of epochs (int)
        - batch_size: Optional batch size (int)
        - patience: Optional early stopping patience (int)
        - move_validated: Whether to move validated images to dataset (bool, default: True)
    
    Returns:
        JSON with training job ID
    """
    try:
        storage_manager, training_job_manager, upload_dir = get_managers(request)
        
        # Check if training is already in progress
        if training_job_manager.is_training_in_progress():
            latest = training_job_manager.get_latest_training()
            raise HTTPException(
                status_code=409,
                detail={
                    'error': 'Training already in progress',
                    'latest_training': latest.dict() if latest else None
                }
            )
        
        # Move validated images to dataset if requested
        if move_validated:
            storage_manager.move_all_to_dataset()
        
        # Start training
        training_id = training_job_manager.start_training(
            epochs=epochs,
            batch_size=batch_size,
            patience=patience
        )
        
        return {
            'training_id': training_id,
            'status': 'started',
            'message': 'Training job started'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/training/status")
async def training_status(
    training_id: Optional[str] = Query(None),
    request: Request = ...
):
    """
    Get training status.
    
    Query params:
        - training_id: Optional training job ID (if not provided, returns latest)
    
    Returns:
        JSON with training status
    """
    try:
        storage_manager, training_job_manager, upload_dir = get_managers(request)
        
        if training_id:
            result = training_job_manager.get_training_status(training_id)
            if not result:
                raise HTTPException(status_code=404, detail="Training job not found")
        else:
            result = training_job_manager.get_latest_training()
            if not result:
                return {'message': 'No training jobs found'}
        
        return result.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validated-images")
async def get_validated_images(request: Request = ...):
    """
    Get list of validated images waiting for retraining.
    
    Returns:
        JSON with list of validated images
    """
    try:
        storage_manager, training_job_manager, upload_dir = get_managers(request)
        validated_images = storage_manager.get_validated_images()
        
        return {
            'count': len(validated_images),
            'images': validated_images
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/export")
async def export_results(format: str = Query("csv", regex="^(csv|json)$")):
    """
    Export analysis results to CSV.
    
    Query params:
        - format: 'csv' or 'json' (default: 'csv')
    
    Returns:
        CSV or JSON file
    """
    try:
        results_dir = Config.RESULTS_DIR
        csv_path = results_dir / 'analysis_results.csv'
        
        if not csv_path.exists():
            raise HTTPException(status_code=404, detail="No results to export")
        
        return FileResponse(
            str(csv_path),
            media_type='text/csv',
            filename='analysis_results.csv'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/export-csv")
async def export_analyze_results_csv(
    request: Request = ...
):
    """
    Export analysis results to CSV format.
    
    Request body (JSON):
        - analysis_data: The analysis result data from /analyze endpoint
    
    Returns:
        CSV file download
    """
    try:
        # Parse JSON body
        body = await request.json()
        data = body.get('analysis_data', body)  # Support both formats
        
        # Debug: Check if data is valid
        if not data:
            raise HTTPException(status_code=400, detail="No analysis data provided")
        
        # Create CSV in memory
        output = io.StringIO()
        # Exact format as in example: Image, Component, Area, void %, Max.void %
        fieldnames = [
            'Image',
            'Component',
            'Area',
            'void %',
            'Max.void %'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        stats = data.get('statistics', {})
        if not stats:
            raise HTTPException(status_code=400, detail="No statistics found in analysis data")
        
        image_path = Path(data.get('image_path', 'unknown'))
        image_name = image_path.name if image_path.name != 'unknown' else 'unknown_image'
        
        # Get masks info
        masks_info = data.get('masks_info', [])
        
        # Per-component rows only (no Global row)
        if masks_info:
            chips = [m for m in masks_info if m.get('class_id') == 0]
            holes = [m for m in masks_info if m.get('class_id') == 1]
            
            def is_hole_in_chip(hole_bbox, chip_bbox):
                """Check if hole center is inside chip bbox."""
                if not hole_bbox or not chip_bbox or len(hole_bbox) < 4 or len(chip_bbox) < 4:
                    return False
                hole_center_x = (hole_bbox[0] + hole_bbox[2]) / 2
                hole_center_y = (hole_bbox[1] + hole_bbox[3]) / 2
                return (chip_bbox[0] <= hole_center_x <= chip_bbox[2] and
                        chip_bbox[1] <= hole_center_y <= chip_bbox[3])
            
            for idx, chip in enumerate(chips, 1):
                chip_area = chip.get('area_pixels', 0)
                chip_bbox = chip.get('bbox', [])
                
                # Find holes inside this chip
                holes_in_chip = []
                for hole in holes:
                    hole_bbox = hole.get('bbox', [])
                    if is_hole_in_chip(hole_bbox, chip_bbox):
                        holes_in_chip.append(hole)
                
                # If no holes found in chip but holes exist, consider all holes
                # (fallback for cases where bbox matching doesn't work perfectly)
                if not holes_in_chip and holes and len(chips) == 1:
                    # If only one chip, all holes belong to it
                    holes_in_chip = holes
                
                # Calculate void percentages
                total_holes_area = sum(h.get('area_pixels', 0) for h in holes_in_chip)
                max_hole_area = max([h.get('area_pixels', 0) for h in holes_in_chip], default=0)
                
                # Convert to percentage (not multiplied by 100, as in example: 0.25 = 0.25%)
                void_percent = (total_holes_area / chip_area) if chip_area > 0 else 0.0
                max_void_percent = (max_hole_area / chip_area) if chip_area > 0 else 0.0
                
                # Format with comma as decimal separator (European format) or dot
                # Using dot for now, but can be changed to comma if needed
                writer.writerow({
                    'Image': image_name if idx == 1 else '',
                    'Component': idx,
                    'Area': chip_area,
                    'void %': f"{void_percent:.2f}".replace('.', ','),  # European format
                    'Max.void %': f"{max_void_percent:.2f}".replace('.', ',')  # European format
                })
        else:
            # If no chips detected, write at least one row with zeros
            writer.writerow({
                'Image': image_name,
                'Component': 1,
                'Area': 0,
                'void %': '0,00',
                'Max.void %': '0,00'
            })
        
        # Prepare CSV response
        csv_data = output.getvalue()
        output.close()
        
        return StreamingResponse(
            io.BytesIO(csv_data.encode('utf-8')),
            media_type='text/csv; charset=utf-8',
            headers={
                'Content-Disposition': f'attachment; filename=analysis_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images/{image_path:path}")
async def get_image(image_path: str, request: Request = ...):
    """
    Serve image files.
    
    Args:
        image_path: Relative path to image (can be just filename or relative path from outputs/)
    
    Returns:
        Image file
    """
    try:
        storage_manager, training_job_manager, upload_dir = get_managers(request)
        
        # Security: prevent directory traversal
        path_obj = Path(image_path)
        
        # If it's just a filename, search in all directories
        if not path_obj.parent or path_obj.parent == Path('.'):
            filename = path_obj.name
            
            # Check in various directories
            possible_paths = [
                Config.INFERENCE_DIR / filename,
                Config.RESULTS_DIR / filename,
                Config.SAM_OUTPUT_DIR / filename,
                upload_dir / filename,
                Config.OUTPUT_DIR / 'validated_images' / 'images' / filename,
            ]
            
            for path in possible_paths:
                if path.exists() and path.is_file():
                    return FileResponse(str(path))
        else:
            # Try as relative path from outputs directory
            try:
                full_path = Config.OUTPUT_DIR / path_obj
                resolved_path = full_path.resolve()
                outputs_resolved = Config.OUTPUT_DIR.resolve()
                
                if str(resolved_path).startswith(str(outputs_resolved)) and resolved_path.exists() and resolved_path.is_file():
                    return FileResponse(str(resolved_path))
            except (ValueError, OSError):
                pass
        
        raise HTTPException(status_code=404, detail="Image not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
