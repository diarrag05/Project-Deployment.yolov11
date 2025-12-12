"""Void rate calculation service."""
import numpy as np
from pathlib import Path
from typing import List, Tuple

from ..config import Config
from ..schemas.result_models import (
    InferenceResult,
    VoidRateStatistics,
    ChipAnalysisResult
)
from ..utils.image_utils import load_image, save_image, create_overlay_image
from ..utils.mask_utils import calculate_mask_area, filter_masks_by_class, combine_masks


class VoidRateCalculator:
    """Service for calculating void rate and determining chip usability."""
    
    def __init__(self, threshold: float = None):
        """
        Initialize void rate calculator.
        
        Args:
            threshold: Void rate threshold percentage (default: Config.VOID_RATE_THRESHOLD)
        """
        self.threshold = threshold or Config.VOID_RATE_THRESHOLD
        self.chip_class_id = Config.CHIP_CLASS_ID
        self.hole_class_id = Config.HOLE_CLASS_ID
    
    def calculate_statistics(
        self,
        inference_result: InferenceResult,
        masks: List[np.ndarray] = None,
        class_ids: List[int] = None
    ) -> VoidRateStatistics:
        """
        Calculate void rate statistics from inference result.
        
        Args:
            inference_result: InferenceResult from YOLO
            masks: Optional list of mask arrays (if not provided, will use area from MaskInfo)
            class_ids: Optional list of class IDs corresponding to masks
        
        Returns:
            VoidRateStatistics object
        """
        # Extract chip and hole masks
        chip_masks = []
        hole_masks = []
        confidences = []
        
        for mask_info in inference_result.masks:
            confidences.append(mask_info.confidence)
            
            if mask_info.class_id == self.chip_class_id:
                chip_masks.append(mask_info)
            elif mask_info.class_id == self.hole_class_id:
                hole_masks.append(mask_info)
        
        # Calculate areas
        chip_area = sum(m.area_pixels for m in chip_masks)
        holes_area = sum(m.area_pixels for m in hole_masks)
        
        # Calculate void rate
        if chip_area > 0:
            void_rate = (holes_area / chip_area) * 100.0
            chip_holes_percentage = (holes_area / chip_area) * 100.0
        else:
            void_rate = 0.0
            chip_holes_percentage = 0.0
        
        # Average confidence
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        return VoidRateStatistics(
            chip_area_pixels=chip_area,
            holes_area_pixels=holes_area,
            void_rate_percent=void_rate,
            chip_holes_percentage=chip_holes_percentage,
            average_confidence=float(avg_confidence),
            num_chips=len(chip_masks),
            num_holes=len(hole_masks)
        )
    
    def is_usable(self, statistics: VoidRateStatistics) -> bool:
        """
        Determine if chip is usable based on void rate threshold.
        
        Args:
            statistics: VoidRateStatistics object
        
        Returns:
            True if usable (void rate < threshold), False otherwise
        """
        # Si aucune chip n'est détectée, l'image est automatiquement non utilisable
        if statistics.num_chips == 0:
            return False
        
        # Sinon, vérifier le void rate
        return statistics.void_rate_percent < self.threshold
    
    def analyze_chip(
        self,
        inference_result: InferenceResult,
        save_annotated_image: bool = True,
        output_dir: Path = None
    ) -> ChipAnalysisResult:
        """
        Complete chip analysis: calculate statistics and determine usability.
        
        Args:
            inference_result: InferenceResult from YOLO
            save_annotated_image: Whether to save annotated image with statistics
            output_dir: Directory to save output (default: Config.RESULTS_DIR)
        
        Returns:
            ChipAnalysisResult object
        """
        # Calculate statistics
        statistics = self.calculate_statistics(inference_result)
        
        # Determine usability
        is_usable = self.is_usable(statistics)
        
        # Save annotated image if requested
        output_image_path = None
        if save_annotated_image:
            try:
                image = load_image(inference_result.image_path)
                
                # Re-extract masks for visualization
                # Note: In a full implementation, we'd store masks in InferenceResult
                # For now, we'll create a simple visualization
                annotated_image = create_overlay_image(
                    image,
                    [],  # Masks would go here
                    statistics.dict(),
                    is_usable,
                    self.threshold
                )
                
                output_dir = output_dir or Config.RESULTS_DIR
                output_dir.mkdir(parents=True, exist_ok=True)
                
                image_path = Path(inference_result.image_path)
                output_filename = f"{image_path.stem}_analysis{image_path.suffix}"
                output_image_path = output_dir / output_filename
                save_image(annotated_image, output_image_path)
            except Exception as e:
                print(f"Warning: Could not create annotated image: {e}")
                output_image_path = inference_result.output_image_path
        
        return ChipAnalysisResult(
            image_path=inference_result.image_path,
            output_image_path=str(output_image_path) if output_image_path else inference_result.output_image_path or "",
            statistics=statistics,
            is_usable=is_usable,
            threshold=self.threshold,
            inference_result=inference_result
        )

