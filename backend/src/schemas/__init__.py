"""Data models for the chip-and-hole detection system."""

from .result_models import (
    InferenceResult,
    VoidRateStatistics,
    ChipAnalysisResult,
    SegmentationResult,
)

__all__ = [
    "InferenceResult",
    "VoidRateStatistics",
    "ChipAnalysisResult",
    "SegmentationResult",
]

