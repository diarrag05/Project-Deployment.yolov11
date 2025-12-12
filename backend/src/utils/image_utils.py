"""Image utility functions."""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def load_image(image_path: str | Path) -> np.ndarray:
    """Load an image from file path."""
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    # Convert BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


def save_image(image: np.ndarray, output_path: str | Path, format: str = "PNG") -> Path:
    """Save an image to file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert RGB to BGR for OpenCV
    if len(image.shape) == 3:
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    else:
        image_bgr = image
    
    cv2.imwrite(str(output_path), image_bgr)
    return output_path


def draw_masks_on_image(
    image: np.ndarray,
    masks: List[np.ndarray],
    boxes: List[List[float]],
    class_ids: List[int],
    confidences: List[float],
    class_names: dict,
    alpha: float = 0.5
) -> np.ndarray:
    """
    Draw segmentation masks on image.
    
    Args:
        image: Input image (RGB)
        masks: List of binary masks
        boxes: List of bounding boxes [x1, y1, x2, y2]
        class_ids: List of class IDs
        confidences: List of confidence scores
        class_names: Dictionary mapping class_id to class_name
        alpha: Transparency for mask overlay
    
    Returns:
        Image with masks drawn
    """
    result_image = image.copy()
    
    # Color map for different classes
    colors = {
        0: (0, 255, 0),    # Green for chip
        1: (255, 0, 0),    # Red for hole
    }
    
    for mask, box, class_id, conf in zip(masks, boxes, class_ids, confidences):
        color = colors.get(class_id, (128, 128, 128))
        class_name = class_names.get(class_id, f"class_{class_id}")
        
        # Resize mask to image size if needed
        if mask.shape[:2] != image.shape[:2]:
            mask = cv2.resize(mask.astype(np.uint8), 
                            (image.shape[1], image.shape[0]),
                            interpolation=cv2.INTER_NEAREST).astype(bool)
        
        # Create colored mask
        colored_mask = np.zeros_like(result_image)
        colored_mask[mask] = color
        
        # Overlay mask
        result_image = cv2.addWeighted(result_image, 1 - alpha, colored_mask, alpha, 0)
        
        # Draw bounding box
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(result_image, (x1, y1), (x2, y2), color, 2)
        
        # Draw label
        label = f"{class_name}: {conf:.2f}"
        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(result_image, (x1, y1 - label_size[1] - 10), 
                     (x1 + label_size[0], y1), color, -1)
        cv2.putText(result_image, label, (x1, y1 - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return result_image


def create_overlay_image(
    image: np.ndarray,
    masks: List[np.ndarray],
    statistics: dict,
    is_usable: bool,
    threshold: float
) -> np.ndarray:
    """
    Create an annotated image with masks and statistics overlay.
    
    Args:
        image: Input image (RGB)
        masks: List of binary masks
        statistics: Dictionary with statistics
        is_usable: Whether chip is usable
        threshold: Void rate threshold
    
    Returns:
        Annotated image
    """
    # Create figure with matplotlib for better text rendering
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.imshow(image)
    ax.axis('off')
    
    # Draw masks
    for mask in masks:
        if mask.shape[:2] != image.shape[:2]:
            mask = cv2.resize(mask.astype(np.uint8),
                            (image.shape[1], image.shape[0]),
                            interpolation=cv2.INTER_NEAREST).astype(bool)
        
        # Create overlay
        overlay = np.zeros((*image.shape[:2], 4))
        overlay[mask, :] = [1, 0, 0, 0.3]  # Red with transparency
        ax.imshow(overlay)
    
    # Add statistics text box
    stats_text = f"""
    Chip Analysis Results
    {'=' * 30}
    Chip Area: {statistics.get('chip_area_pixels', 0):,} pixels
    Holes Area: {statistics.get('holes_area_pixels', 0):,} pixels
    Void Rate: {statistics.get('void_rate_percent', 0.0):.2f}%
    Chip/Holes %: {statistics.get('chip_holes_percentage', 0.0):.2f}%
    Average Confidence: {statistics.get('average_confidence', 0.0):.2f}
    Threshold: {threshold:.2f}%
    
    Status: {'✓ USABLE' if is_usable else '✗ NOT USABLE'}
    """
    
    # Add text box
    props = dict(boxstyle='round', facecolor='white', alpha=0.8)
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top', bbox=props,
           family='monospace')
    
    # Convert matplotlib figure to numpy array
    fig.canvas.draw()
    buf = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    buf = buf.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    plt.close(fig)
    
    return buf

