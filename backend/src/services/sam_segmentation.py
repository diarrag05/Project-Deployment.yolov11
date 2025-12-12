"""SAM (Segment Anything Model) segmentation service for refining masks."""
import time
import urllib.request
from pathlib import Path
from typing import Optional, List, Tuple, Dict
import numpy as np
import cv2
from PIL import Image

try:
    from segment_anything import sam_model_registry, SamPredictor, SamAutomaticMaskGenerator
    SAM_AVAILABLE = True
except ImportError:
    SAM_AVAILABLE = False
    print("Warning: segment_anything not installed. SAM functionality will be limited.")

from ..config import Config
from ..schemas.result_models import SegmentationResult
from ..utils.image_utils import load_image, save_image
from ..utils.mask_utils import mask_to_yolo_format


class SAMSegmentationService:
    """Service for SAM-based segmentation refinement."""
    
    def __init__(
        self,
        model_type: str = None,
        checkpoint_path: Optional[str | Path] = None,
        device: str = "cuda"
    ):
        """
        Initialize SAM segmentation service.
        
        Args:
            model_type: SAM model type ("vit_h", "vit_l", "vit_b")
            checkpoint_path: Path to SAM checkpoint (will download if not provided)
            device: Device to use ("cuda", "cpu", "mps")
        """
        if not SAM_AVAILABLE:
            raise ImportError(
                "segment_anything package not installed. "
                "Install it with: pip install git+https://github.com/facebookresearch/segment-anything.git"
            )
        
        self.model_type = model_type or Config.SAM_MODEL_TYPE
        self.device = device
        
        # Initialize model
        self._load_model(checkpoint_path)
    
    def _load_model(self, checkpoint_path: Optional[str | Path] = None):
        """Load SAM model."""
        import torch
        
        # Determine device
        if self.device == "cuda" and not torch.cuda.is_available():
            self.device = "cpu"
        elif self.device == "mps" and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
            self.device = "cpu"
        
        
        # Get checkpoint path
        if checkpoint_path is None:
            checkpoint_path = Config.MODELS_DIR / f"sam_{self.model_type}_4b8939.pth"
            if not checkpoint_path.exists():
                print(f"SAM checkpoint not found. Downloading from {Config.SAM_CHECKPOINT_URL}...")
                print("This may take several minutes (file size: ~2.4 GB)...")
                
                Config.MODELS_DIR.mkdir(parents=True, exist_ok=True)

                try:
                    urllib.request.urlretrieve(
                        Config.SAM_CHECKPOINT_URL,
                        checkpoint_path,
                        reporthook=self._download_progress_hook
                    )
                    print(f"\nSAM checkpoint downloaded successfully to {checkpoint_path}")
                except Exception as e:
                    raise FileNotFoundError(
                        f"Failed to download SAM checkpoint: {e}\n"
                        f"Please download manually from: {Config.SAM_CHECKPOINT_URL}\n"
                        f"and place it in: {Config.MODELS_DIR}"
                    )
        
        checkpoint_path = Path(checkpoint_path)
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"SAM checkpoint not found: {checkpoint_path}")
        
        # Load model
        self.sam = sam_model_registry[self.model_type](checkpoint=str(checkpoint_path))
        self.sam.to(device=self.device)
        self.predictor = SamPredictor(self.sam)
        self.mask_generator = SamAutomaticMaskGenerator(self.sam)
    
    def _download_progress_hook(self, count, block_size, total_size):
        """Show download progress."""
        percent = int(count * block_size * 100 / total_size)
        print(f"\rDownloading: {percent}%", end='', flush=True)
    
    def segment_guided(
        self,
        image_path: str | Path,
        points: List[Tuple[int, int]],
        point_labels: List[int],
        boxes: Optional[List[List[float]]] = None,
        save_output: bool = True,
        output_dir: Optional[str | Path] = None
    ) -> SegmentationResult:
        """
        Perform guided segmentation with points and/or boxes.
        
        Args:
            image_path: Path to input image
            points: List of (x, y) point coordinates
            point_labels: List of labels (1 for foreground, 0 for background)
            boxes: Optional list of bounding boxes [x1, y1, x2, y2]
            save_output: Whether to save output
            output_dir: Output directory
        
        Returns:
            SegmentationResult object
        """
        start_time = time.time()
        image_path = Path(image_path)
        
        # Load image
        image = load_image(image_path)
        image_rgb = image if len(image.shape) == 3 else cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        # Set image in predictor
        self.predictor.set_image(image_rgb)
        
        # Prepare input
        input_points = np.array(points) if points else None
        input_labels = np.array(point_labels) if point_labels else None
        input_boxes = np.array(boxes) if boxes else None
        
        # Predict
        masks, scores, logits = self.predictor.predict(
            point_coords=input_points,
            point_labels=input_labels,
            box=input_boxes[0] if input_boxes is not None and len(input_boxes) > 0 else None,
            multimask_output=True
        )
        
        # Use best mask (highest score)
        best_mask_idx = np.argmax(scores)
        best_mask = masks[best_mask_idx]
        
        # Save output
        output_image_path = None
        if save_output:
            output_dir = Path(output_dir) if output_dir else Config.SAM_OUTPUT_DIR
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create visualization
            vis_image = self._create_mask_visualization(image_rgb, best_mask)
            
            output_filename = f"{image_path.stem}_sam_guided{image_path.suffix}"
            output_image_path = output_dir / output_filename
            save_image(vis_image, output_image_path)
        
        processing_time = time.time() - start_time
        
        return SegmentationResult(
            image_path=str(image_path),
            output_image_path=str(output_image_path) if output_image_path else "",
            num_masks=1,
            mode="guided",
            processing_time=processing_time
        )
    
    def segment_automatic(
        self,
        image_path: str | Path,
        save_output: bool = True,
        output_dir: Optional[str | Path] = None
    ) -> SegmentationResult:
        """
        Perform automatic segmentation (generates masks for entire image).
        
        Args:
            image_path: Path to input image
            save_output: Whether to save output
            output_dir: Output directory
        
        Returns:
            SegmentationResult object
        """
        start_time = time.time()
        image_path = Path(image_path)
        
        # Load image
        image = load_image(image_path)
        image_rgb = image if len(image.shape) == 3 else cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        # Generate masks
        masks = self.mask_generator.generate(image_rgb)
        
        # Save output
        output_image_path = None
        if save_output:
            output_dir = Path(output_dir) if output_dir else Config.SAM_OUTPUT_DIR
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create visualization with all masks
            vis_image = self._create_masks_visualization(image_rgb, masks)
            
            output_filename = f"{image_path.stem}_sam_automatic{image_path.suffix}"
            output_image_path = output_dir / output_filename
            save_image(vis_image, output_image_path)
        
        processing_time = time.time() - start_time
        
        return SegmentationResult(
            image_path=str(image_path),
            output_image_path=str(output_image_path) if output_image_path else "",
            num_masks=len(masks),
            mode="automatic",
            processing_time=processing_time
        )
    
    def _create_mask_visualization(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Create visualization of mask on image."""
        # Resize mask if needed
        if mask.shape[:2] != image.shape[:2]:
            mask = cv2.resize(mask.astype(np.uint8), 
                            (image.shape[1], image.shape[0]),
                            interpolation=cv2.INTER_NEAREST).astype(bool)
        
        # Create overlay
        overlay = image.copy()
        overlay[mask] = overlay[mask] * 0.7 + np.array([255, 0, 0]) * 0.3
        return overlay.astype(np.uint8)
    
    def _create_masks_visualization(self, image: np.ndarray, masks: List[Dict]) -> np.ndarray:
        """Create visualization of multiple masks on image."""
        overlay = image.copy()
        
        for mask_data in masks:
            mask = mask_data['segmentation']
            # Apply mask with transparency
            overlay[mask] = overlay[mask] * 0.7 + np.array([255, 0, 0]) * 0.3
        
        return overlay.astype(np.uint8)
    
    def get_mask_array(self, segmentation_result: SegmentationResult) -> Optional[np.ndarray]:
        """
        Get mask array from segmentation result.
        Note: This would require storing masks in SegmentationResult.
        For now, returns None - masks need to be re-extracted if needed.
        """
        # In a full implementation, we'd store masks in SegmentationResult
        return None

