"""Label manager for saving YOLO format labels."""
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np

from ..config import Config
from ..utils.mask_utils import mask_to_yolo_format


class LabelManager:
    """Service for managing YOLO format labels."""
    
    def __init__(self):
        """Initialize label manager."""
        self.class_names = Config.get_class_names()
        self.num_classes = Config.get_num_classes()
    
    def save_labels_from_masks(
        self,
        masks: List[np.ndarray],
        class_ids: List[int],
        image_path: str | Path,
        output_labels_dir: Optional[str | Path] = None,
        image_width: Optional[int] = None,
        image_height: Optional[int] = None
    ) -> Path:
        """
        Save YOLO format labels from masks.
        
        Args:
            masks: List of binary masks
            class_ids: List of class IDs corresponding to masks
            image_path: Path to source image (used for naming)
            output_labels_dir: Directory to save labels (default: dataset/train/labels)
            image_width: Image width (if not provided, will use mask shape)
            image_height: Image height (if not provided, will use mask shape)
        
        Returns:
            Path to saved label file
        """
        image_path = Path(image_path)
        
        # Determine output directory
        if output_labels_dir is None:
            output_labels_dir = Config.TRAIN_LABELS_DIR
        else:
            output_labels_dir = Path(output_labels_dir)
        
        output_labels_dir.mkdir(parents=True, exist_ok=True)
        
        # Get image dimensions
        if image_width is None or image_height is None:
            if masks:
                image_height, image_width = masks[0].shape[:2]
            else:
                raise ValueError("Cannot determine image dimensions from empty masks")
        
        # Generate label filename
        label_filename = f"{image_path.stem}.txt"
        label_path = output_labels_dir / label_filename
        
        # Convert masks to YOLO format and write
        with open(label_path, 'w') as f:
            for mask, class_id in zip(masks, class_ids):
                # Convert mask to YOLO polygon format
                polygons = mask_to_yolo_format(mask, image_width, image_height)
                
                for polygon in polygons:
                    # Format: class_id x1 y1 x2 y2 x3 y3 ...
                    line = f"{class_id} " + " ".join(f"{coord:.6f}" for coord in polygon)
                    f.write(line + "\n")
        
        return label_path
    
    def save_labels_from_inference(
        self,
        inference_result,
        output_labels_dir: Optional[str | Path] = None
    ) -> Path:
        """
        Save labels from inference result.
        Note: This requires mask arrays which may not be stored in InferenceResult.
        For a full implementation, we'd need to store masks or re-run inference.
        
        Args:
            inference_result: InferenceResult object
            output_labels_dir: Directory to save labels
        
        Returns:
            Path to saved label file
        """
        # This is a placeholder - in practice, we'd need the actual mask arrays
        # For now, we'll create a basic implementation that would work if masks were stored
        raise NotImplementedError(
            "This method requires mask arrays. "
            "Use save_labels_from_masks() with actual mask arrays instead."
        )
    
    def load_labels(
        self,
        label_path: str | Path
    ) -> List[Tuple[int, List[List[float]]]]:
        """
        Load YOLO format labels.
        
        Args:
            label_path: Path to label file
        
        Returns:
            List of (class_id, polygon_coordinates) tuples
        """
        label_path = Path(label_path)
        if not label_path.exists():
            raise FileNotFoundError(f"Label file not found: {label_path}")
        
        labels = []
        with open(label_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split()
                class_id = int(parts[0])
                coords = [float(x) for x in parts[1:]]
                
                # Group coordinates into (x, y) pairs
                polygon = [(coords[i], coords[i+1]) for i in range(0, len(coords), 2)]
                labels.append((class_id, polygon))
        
        return labels
    
    def copy_image_and_labels_to_dataset(
        self,
        image_path: str | Path,
        labels_path: str | Path
    ) -> Tuple[Path, Path]:
        """
        Copy image and labels to dataset directory.
        
        Args:
            image_path: Path to source image
            labels_path: Path to source labels file
        
        Returns:
            Tuple of (new_image_path, new_labels_path)
        """
        image_path = Path(image_path)
        labels_path = Path(labels_path)
        
        # Validated images go to train directory
        target_images_dir = Config.TRAIN_IMAGES_DIR
        target_labels_dir = Config.TRAIN_LABELS_DIR
        
        target_images_dir.mkdir(parents=True, exist_ok=True)
        target_labels_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy files
        import shutil
        new_image_path = target_images_dir / image_path.name
        new_labels_path = target_labels_dir / labels_path.name
        
        shutil.copy2(image_path, new_image_path)
        shutil.copy2(labels_path, new_labels_path)
        
        return new_image_path, new_labels_path

