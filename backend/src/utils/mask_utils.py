"""Mask utility functions for processing segmentation masks."""
import numpy as np
from typing import List, Tuple, Optional
import cv2


def calculate_mask_area(mask: np.ndarray) -> int:
    """
    Calculate the area of a binary mask in pixels.
    
    Args:
        mask: Binary mask (boolean or 0/1 array)
    
    Returns:
        Area in pixels
    """
    if mask.dtype != bool:
        mask = mask.astype(bool)
    return int(np.sum(mask))


def filter_masks_by_class(
    masks: List[np.ndarray],
    class_ids: List[int],
    target_class_id: int
) -> List[np.ndarray]:
    """
    Filter masks by class ID.
    
    Args:
        masks: List of masks
        class_ids: List of corresponding class IDs
        target_class_id: Target class ID to filter
    
    Returns:
        Filtered list of masks
    """
    return [mask for mask, cid in zip(masks, class_ids) if cid == target_class_id]


def combine_masks(masks: List[np.ndarray]) -> np.ndarray:
    """
    Combine multiple masks into a single mask using union.
    
    Args:
        masks: List of binary masks
    
    Returns:
        Combined mask
    """
    if not masks:
        return np.array([])
    
    # Get shape from first mask
    shape = masks[0].shape
    combined = np.zeros(shape, dtype=bool)
    
    for mask in masks:
        if mask.shape != shape:
            mask = cv2.resize(mask.astype(np.uint8), 
                            (shape[1], shape[0]),
                            interpolation=cv2.INTER_NEAREST).astype(bool)
        combined = combined | mask
    
    return combined


def mask_to_polygon(mask: np.ndarray, simplify: bool = True) -> List[List[Tuple[int, int]]]:
    """
    Convert a binary mask to polygon coordinates.
    
    Args:
        mask: Binary mask
        simplify: Whether to simplify the polygon
    
    Returns:
        List of polygons, each as a list of (x, y) coordinates
    """
    if mask.dtype != np.uint8:
        mask = (mask * 255).astype(np.uint8)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    polygons = []
    for contour in contours:
        if len(contour) < 3:
            continue
        
        # Simplify if requested
        if simplify:
            epsilon = 0.002 * cv2.arcLength(contour, True)
            contour = cv2.approxPolyDP(contour, epsilon, True)
        
        # Convert to list of tuples
        polygon = [(int(point[0][0]), int(point[0][1])) for point in contour]
        polygons.append(polygon)
    
    return polygons


def mask_to_yolo_format(
    mask: np.ndarray,
    image_width: int,
    image_height: int
) -> List[List[float]]:
    """
    Convert mask to YOLO format (normalized polygon coordinates).
    
    Args:
        mask: Binary mask
        image_width: Image width
        image_height: Image height
    
    Returns:
        List of polygons in YOLO format (normalized coordinates)
    """
    polygons = mask_to_polygon(mask)
    yolo_polygons = []
    
    for polygon in polygons:
        yolo_polygon = []
        for x, y in polygon:
            # Normalize coordinates
            x_norm = x / image_width
            y_norm = y / image_height
            yolo_polygon.extend([x_norm, y_norm])
        yolo_polygons.append(yolo_polygon)
    
    return yolo_polygons


def resize_mask(mask: np.ndarray, target_shape: Tuple[int, int]) -> np.ndarray:
    """
    Resize a mask to target shape.
    
    Args:
        mask: Binary mask
        target_shape: Target (height, width)
    
    Returns:
        Resized mask
    """
    if mask.shape[:2] == target_shape:
        return mask
    
    mask_uint8 = (mask * 255).astype(np.uint8) if mask.dtype != np.uint8 else mask
    resized = cv2.resize(mask_uint8, (target_shape[1], target_shape[0]),
                        interpolation=cv2.INTER_NEAREST)
    
    return (resized > 127).astype(bool) if mask.dtype == bool else resized

