"""
SAM Model Manager - Singleton to load SAM model once and reuse it.
This prevents reloading the heavy SAM model on every request.
"""
from typing import Optional
from backend.src.services.sam_segmentation import SAMSegmentationService

# Global SAM service instance (singleton)
_sam_service: Optional[SAMSegmentationService] = None


def get_sam_service() -> SAMSegmentationService:
    """
    Get or create the global SAM service instance.
    The model is loaded only once on first call.
    
    Returns:
        SAMSegmentationService instance
    """
    global _sam_service
    
    if _sam_service is None:
        # Load SAM model (this happens only once)
        _sam_service = SAMSegmentationService()
    
    return _sam_service


def reset_sam_service():
    """
    Reset the global SAM service (useful for testing or reloading).
    """
    global _sam_service
    _sam_service = None


