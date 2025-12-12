"""
Training job manager for tracking training status.
Manages asynchronous training jobs and provides status updates.
"""
import threading
import time
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import uuid

from backend.src.services import TrainingService
from backend.src.schemas.result_models import TrainingResult
from backend.src.config import Config


class TrainingJobManager:
    """Manages training jobs and their status."""
    
    def __init__(self):
        """Initialize training job manager."""
        self.jobs: Dict[str, TrainingResult] = {}
        self.job_threads: Dict[str, threading.Thread] = {}
        self.lock = threading.Lock()
    
    def start_training(
        self,
        epochs: Optional[int] = None,
        batch_size: Optional[int] = None,
        patience: Optional[int] = None
    ) -> str:
        """
        Start a training job asynchronously.
        
        Args:
            epochs: Number of epochs
            batch_size: Batch size
            patience: Early stopping patience
            
        Returns:
            Training job ID
        """
        training_id = str(uuid.uuid4())
        
        # Create initial training result
        training_result = TrainingResult(
            training_id=training_id,
            status='in_progress',
            start_time=datetime.now(),
            total_epochs=epochs or 100
        )
        
        with self.lock:
            self.jobs[training_id] = training_result
        
        # Start training in background thread
        def train_worker():
            try:
                training_service = TrainingService()
                result = training_service.retrain_model(
                    epochs=epochs,
                    batch_size=batch_size,
                    patience=patience
                )
                
                with self.lock:
                    self.jobs[training_id] = result
            except Exception as e:
                with self.lock:
                    self.jobs[training_id] = TrainingResult(
                        training_id=training_id,
                        status='failed',
                        start_time=training_result.start_time,
                        end_time=datetime.now(),
                        error_message=str(e),
                        total_epochs=epochs or 100
                    )
        
        thread = threading.Thread(target=train_worker, daemon=True)
        thread.start()
        
        with self.lock:
            self.job_threads[training_id] = thread
        
        return training_id
    
    def _update_progress_from_logs(self, training_id: str, training_result: TrainingResult):
        """
        Update training progress by reading from Ultralytics results.csv.
        
        Args:
            training_id: Training job ID
            training_result: Current training result to update
        """
        try:
            import csv
            from pathlib import Path
            import time
            
            # Find the most recent training directory
            runs_dir = Config.BASE_DIR / 'runs' / 'segment'
            if not runs_dir.exists():
                return
            
            # Get all directories that start with 'train'
            training_dirs = [
                d for d in runs_dir.iterdir() 
                if d.is_dir() and d.name.startswith('train')
            ]
            
            if not training_dirs:
                return
            
            # Sort by modification time (most recent first)
            training_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            most_recent_dir = training_dirs[0]
            
            # Check for results.csv in the most recent training run
            results_csv = most_recent_dir / 'results.csv'
            if not results_csv.exists():
                return
            
            # Try to read the CSV file (may be locked during writing)
            # Retry a few times if file is locked
            rows = []
            for attempt in range(3):
                try:
                    with open(results_csv, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        rows = list(reader)
                    break
                except (IOError, PermissionError):
                    if attempt < 2:
                        time.sleep(0.5)  # Wait before retry
                    continue
            
            if rows:
                # Get the last row (most recent epoch)
                last_row = rows[-1]
                
                # The first column is 'epoch'
                try:
                    epochs_completed = int(float(last_row['epoch'])) + 1  # +1 because epoch is 0-indexed
                except (ValueError, KeyError):
                    # Fallback: count rows
                    epochs_completed = len(rows)
                
                # Only update if we have new progress
                if epochs_completed > training_result.epochs_completed:
                    # Update the training result by creating a new dict and updating
                    result_dict = training_result.dict()
                    result_dict['epochs_completed'] = epochs_completed
                    # Create new TrainingResult with updated values
                    updated_result = TrainingResult(**result_dict)
                    # Replace in jobs dict (lock already held by caller)
                    self.jobs[training_id] = updated_result
        except Exception as e:
            # Log error for debugging but don't break status updates
            import traceback
            print(f"Error updating progress from logs: {e}")
            traceback.print_exc()
            pass
    
    def get_training_status(self, training_id: str) -> Optional[TrainingResult]:
        """
        Get status of a training job.
        Updates progress from logs if training is in progress.
        
        Args:
            training_id: Training job ID
            
        Returns:
            TrainingResult or None if not found
        """
        with self.lock:
            result = self.jobs.get(training_id)
            if result and result.status == 'in_progress':
                # Update progress from logs
                self._update_progress_from_logs(training_id, result)
            return result
    
    def get_latest_training(self) -> Optional[TrainingResult]:
        """
        Get the latest training job.
        Updates progress from logs if training is in progress.
        
        Returns:
            Latest TrainingResult or None
        """
        with self.lock:
            if not self.jobs:
                return None
            
            # Sort by start_time (newest first)
            sorted_jobs = sorted(
                self.jobs.values(),
                key=lambda x: x.start_time,
                reverse=True
            )
            latest = sorted_jobs[0]
            
            # Update progress from logs if in progress (lock is held)
            if latest and latest.status == 'in_progress':
                self._update_progress_from_logs(latest.training_id, latest)
                # Get updated result
                latest = self.jobs.get(latest.training_id)
            
            return latest
    
    def get_all_trainings(self) -> list:
        """
        Get all training jobs.
        
        Returns:
            List of TrainingResult objects
        """
        with self.lock:
            return list(self.jobs.values())
    
    def is_training_in_progress(self) -> bool:
        """
        Check if any training is currently in progress.
        
        Returns:
            True if training is in progress
        """
        with self.lock:
            for job in self.jobs.values():
                if job.status == 'in_progress':
                    return True
            return False

