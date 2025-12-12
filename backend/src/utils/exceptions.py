"""
Custom exceptions for the chip-and-hole detection system.
Provides specific exception types for better error handling.
"""


class ChipAndHoleError(Exception):
    """Base exception for all chip-and-hole detection errors."""
    pass


class ModelNotFoundError(ChipAndHoleError):
    """Raised when a model file is not found."""
    def __init__(self, model_path: str, message: str = None):
        self.model_path = model_path
        if message is None:
            message = f"Model not found: {model_path}"
        super().__init__(message)


class DatasetNotFoundError(ChipAndHoleError):
    """Raised when dataset files are not found."""
    def __init__(self, dataset_path: str, message: str = None):
        self.dataset_path = dataset_path
        if message is None:
            message = f"Dataset not found: {dataset_path}"
        super().__init__(message)


class ImageProcessingError(ChipAndHoleError):
    """Raised when image processing fails."""
    def __init__(self, image_path: str, reason: str = None, message: str = None):
        self.image_path = image_path
        self.reason = reason
        if message is None:
            message = f"Image processing failed for {image_path}"
            if reason:
                message += f": {reason}"
        super().__init__(message)


class InferenceError(ChipAndHoleError):
    """Raised when YOLO inference fails."""
    def __init__(self, image_path: str, reason: str = None, message: str = None):
        self.image_path = image_path
        self.reason = reason
        if message is None:
            message = f"Inference failed for {image_path}"
            if reason:
                message += f": {reason}"
        super().__init__(message)


class SegmentationError(ChipAndHoleError):
    """Raised when SAM segmentation fails."""
    def __init__(self, image_path: str, reason: str = None, message: str = None):
        self.image_path = image_path
        self.reason = reason
        if message is None:
            message = f"Segmentation failed for {image_path}"
            if reason:
                message += f": {reason}"
        super().__init__(message)


class TrainingError(ChipAndHoleError):
    """Raised when model training fails."""
    def __init__(self, training_id: str = None, reason: str = None, message: str = None):
        self.training_id = training_id
        self.reason = reason
        if message is None:
            message = "Model training failed"
            if training_id:
                message += f" (training_id: {training_id})"
            if reason:
                message += f": {reason}"
        super().__init__(message)


class ValidationError(ChipAndHoleError):
    """Raised when data validation fails."""
    def __init__(self, field: str = None, value: any = None, message: str = None):
        self.field = field
        self.value = value
        if message is None:
            message = "Validation failed"
            if field:
                message += f" for field '{field}'"
            if value is not None:
                message += f" (value: {value})"
        super().__init__(message)


class ConfigurationError(ChipAndHoleError):
    """Raised when configuration is invalid or missing."""
    def __init__(self, config_key: str = None, message: str = None):
        self.config_key = config_key
        if message is None:
            message = "Configuration error"
            if config_key:
                message += f": missing or invalid '{config_key}'"
        super().__init__(message)

