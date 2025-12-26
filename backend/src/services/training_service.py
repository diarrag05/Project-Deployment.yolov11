"""Training service for model retraining."""
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import uuid

from ..config import Config
from ..schemas.result_models import TrainingResult
from ..utils.logger import get_logger
from ..utils.exceptions import TrainingError, ConfigurationError


class TrainingService:
    """Service for managing model training and retraining."""
    
    def __init__(self):
        """Initialize training service."""
        self.data_yaml = Config.DATA_YAML
    
    def retrain_model(
        self,
        epochs: Optional[int] = None,
        batch_size: Optional[int] = None,
        patience: Optional[int] = None,
        device: Optional[str] = None
    ) -> TrainingResult:
        """
        Retrain the model with the current dataset.
        
        Args:
            epochs: Number of training epochs
            batch_size: Batch size for training
            patience: Early stopping patience
            device: Device to use for training
        
        Returns:
            TrainingResult object
        """
        training_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # Use optimized retraining defaults from config if not provided
        # These are optimized for speed (active learning scenario)
        epochs = epochs or Config.TRAINING_RETRAIN_EPOCHS
        batch_size = batch_size or Config.TRAINING_BATCH_SIZE
        patience = patience or Config.TRAINING_RETRAIN_PATIENCE
        
        # Run training script
        try:
            self.logger = get_logger(__name__)
            self.logger.info(f"Starting training job {training_id} with {epochs} epochs, batch_size={batch_size}, patience={patience}")
            
            # Use subprocess to run training script with parameters
            # train.py is located in backend/ directory
            train_script = Config.BASE_DIR / "backend" / "train.py"
            cmd = [
                sys.executable, 
                str(train_script),
                "--epochs", str(epochs),
                "--batch", str(batch_size),
                "--patience", str(patience)
            ]
            
            self.logger.debug(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',  # Replace invalid characters instead of raising error
                cwd=Config.BASE_DIR
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                self.logger.error(f"Training failed: {error_msg}")
                raise TrainingError(training_id, error_msg)
            
            # Check if best model was created
            best_model_path = Config.DEFAULT_MODEL
            if not best_model_path.exists():
                return TrainingResult(
                    training_id=training_id,
                    status="failed",
                    start_time=start_time,
                    end_time=datetime.now(),
                    error_message="Best model not found after training",
                    total_epochs=epochs
                )
            
            return TrainingResult(
                training_id=training_id,
                status="completed",
                best_model_path=str(best_model_path),
                start_time=start_time,
                end_time=datetime.now(),
                total_epochs=epochs,
                epochs_completed=epochs  # Would need to parse from logs
            )
            
        except Exception as e:
            return TrainingResult(
                training_id=training_id,
                status="failed",
                start_time=start_time,
                end_time=datetime.now(),
                error_message=str(e),
                total_epochs=epochs
            )
    
    def add_image_to_dataset(
        self,
        image_path: str | Path,
        labels_path: str | Path
    ) -> Tuple[Path, Path]:
        """
        Add image and labels to training dataset.
        
        Args:
            image_path: Path to image file
            labels_path: Path to labels file
        
        Returns:
            Tuple of (new_image_path, new_labels_path)
        """
        from .label_manager import LabelManager
        
        label_manager = LabelManager()
        return label_manager.copy_image_and_labels_to_dataset(
            image_path,
            labels_path
        )
    
    def get_training_status(self, training_id: str) -> Optional[TrainingResult]:
        """
        Get status of a training job.
        Note: This would require a job queue system for full implementation.
        
        Args:
            training_id: Training job ID
        
        Returns:
            TrainingResult if found, None otherwise
        """
        # In a full implementation, we'd track training jobs
        # For now, this is a placeholder
        return None

