"""Export utility functions for CSV and JSON formats."""
import csv
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from ..schemas.result_models import ChipAnalysisResult, VoidRateStatistics


def export_results_to_csv(
    results: List[ChipAnalysisResult],
    output_path: str | Path
) -> Path:
    """
    Export analysis results to CSV file.
    
    Args:
        results: List of ChipAnalysisResult objects
        output_path: Path to output CSV file
    
    Returns:
        Path to created CSV file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = [
        'image_path',
        'timestamp',
        'chip_area_pixels',
        'holes_area_pixels',
        'void_rate_percent',
        'chip_holes_percentage',
        'average_confidence',
        'num_chips',
        'num_holes',
        'is_usable',
        'threshold',
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            stats = result.statistics
            writer.writerow({
                'image_path': str(result.image_path),
                'timestamp': result.timestamp.isoformat(),
                'chip_area_pixels': stats.chip_area_pixels,
                'holes_area_pixels': stats.holes_area_pixels,
                'void_rate_percent': stats.void_rate_percent,
                'chip_holes_percentage': stats.chip_holes_percentage,
                'average_confidence': stats.average_confidence,
                'num_chips': stats.num_chips,
                'num_holes': stats.num_holes,
                'is_usable': result.is_usable,
                'threshold': result.threshold,
            })
    
    return output_path


def export_results_to_json(
    results: List[ChipAnalysisResult],
    output_path: str | Path,
    indent: int = 2
) -> Path:
    """
    Export analysis results to JSON file.
    
    Args:
        results: List of ChipAnalysisResult objects
        output_path: Path to output JSON file
        indent: JSON indentation
    
    Returns:
        Path to created JSON file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert results to dictionaries
    data = [result.dict() for result in results]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, default=str, ensure_ascii=False)
    
    return output_path


def export_statistics(
    statistics: VoidRateStatistics,
    output_path: str | Path,
    format: str = "json"
) -> Path:
    """
    Export single statistics object to file.
    
    Args:
        statistics: VoidRateStatistics object
        output_path: Path to output file
        format: Output format ("json" or "csv")
    
    Returns:
        Path to created file
    """
    output_path = Path(output_path)
    
    if format.lower() == "json":
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(statistics.dict(), f, indent=2, default=str, ensure_ascii=False)
    elif format.lower() == "csv":
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=statistics.dict().keys())
            writer.writeheader()
            writer.writerow(statistics.dict())
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    return output_path

