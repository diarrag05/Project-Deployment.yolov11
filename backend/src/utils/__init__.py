"""Utility functions for the chip-and-hole detection system."""

from .image_utils import (
    load_image,
    save_image,
    draw_masks_on_image,
    create_overlay_image,
)
from .mask_utils import (
    calculate_mask_area,
    filter_masks_by_class,
    combine_masks,
    mask_to_polygon,
)
from .export_utils import (
    export_results_to_csv,
    export_results_to_json,
    export_statistics,
)
from .logger import get_logger, setup_logger
from .exceptions import (
    ChipAndHoleError,
    ModelNotFoundError,
    DatasetNotFoundError,
    ImageProcessingError,
    InferenceError,
    SegmentationError,
    TrainingError,
    ValidationError,
    ConfigurationError,
)

__all__ = [
    # Image utilities
    "load_image",
    "save_image",
    "draw_masks_on_image",
    "create_overlay_image",
    # Mask utilities
    "calculate_mask_area",
    "filter_masks_by_class",
    "combine_masks",
    "mask_to_polygon",
    # Export utilities
    "export_results_to_csv",
    "export_results_to_json",
    "export_statistics",
    # Logger
    "get_logger",
    "setup_logger",
    # Exceptions
    "ChipAndHoleError",
    "ModelNotFoundError",
    "DatasetNotFoundError",
    "ImageProcessingError",
    "InferenceError",
    "SegmentationError",
    "TrainingError",
    "ValidationError",
    "ConfigurationError",
]
