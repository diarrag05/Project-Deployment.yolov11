"""
Data models for results and statistics.
Uses Pydantic for validation and serialization (ready for API).
"""
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field


class MaskInfo(BaseModel):
    """Information about a detected mask."""
    class_id: int
    class_name: str
    confidence: float
    area_pixels: int
    bbox: List[float]  # [x1, y1, x2, y2]


class InferenceResult(BaseModel):
    """Result from YOLO inference."""
    image_path: str
    output_image_path: Optional[str] = None
    masks: List[MaskInfo] = []
    num_detections: int = 0
    processing_time: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class VoidRateStatistics(BaseModel):
    """Statistics for void rate calculation."""
    chip_area_pixels: int = 0
    holes_area_pixels: int = 0
    void_rate_percent: float = 0.0
    chip_holes_percentage: float = 0.0
    average_confidence: float = 0.0
    num_chips: int = 0
    num_holes: int = 0


class ChipAnalysisResult(BaseModel):
    """Complete analysis result for a chip."""
    image_path: str
    output_image_path: str
    statistics: VoidRateStatistics
    is_usable: bool
    threshold: float
    inference_result: InferenceResult
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            Path: str,
            datetime: lambda v: v.isoformat()
        }


class SegmentationResult(BaseModel):
    """Result from SAM segmentation."""
    image_path: str
    output_image_path: str
    masks_path: Optional[str] = None
    labels_path: Optional[str] = None
    num_masks: int = 0
    mode: str  # "guided" or "automatic"
    processing_time: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class TrainingResult(BaseModel):
    """Result from model training."""
    training_id: str
    status: str  # "completed", "failed", "in_progress"
    best_model_path: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    epochs_completed: int = 0
    total_epochs: int = 100
    start_time: datetime
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None

