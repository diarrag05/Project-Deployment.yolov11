"""
Retraining Pipeline
Handles fine-tuning YOLO with new labeled data
"""

from ultralytics import YOLO
from pathlib import Path
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RetrainingPipeline:
    def __init__(self, model_path='models/yolov8n-seg_trained.pt'):
        self.model_path = model_path
        self.training_history = []
        self.is_training = False
    
    def prepare_training_data(self):
        """Prepare data from labeled_data folder"""
        try:
            labeled_data_dir = Path('labeled_data/labels')
            training_images_dir = Path('training_data/images')
            training_labels_dir = Path('training_data/labels')
            
            # Create directories
            training_images_dir.mkdir(parents=True, exist_ok=True)
            training_labels_dir.mkdir(parents=True, exist_ok=True)
            
            # Prepare data.yaml for YOLO
            data_yaml = {
                'path': str(Path('training_data').absolute()),
                'train': 'images/train',
                'val': 'images/val',
                'nc': 2,
                'names': {0: 'chip', 1: 'hole'}
            }
            
            with open('training_data/data.yaml', 'w') as f:
                import yaml
                yaml.dump(data_yaml, f)
            
            logger.info("Training data prepared")
            return True
        
        except Exception as e:
            logger.error(f"Data preparation error: {str(e)}")
            return False
    
    def retrain(self, num_epochs=10, learning_rate=0.001, progress_callback=None):
        """
        Retrain YOLO model
        """
        try:
            self.is_training = True
            
            # Load base model
            model = YOLO(self.model_path)
            
            logger.info(f"Starting retraining: {num_epochs} epochs, lr={learning_rate}")
            
            # Fine-tune
            results = model.train(
                data='data.yaml',
                epochs=num_epochs,
                lr0=learning_rate,
                device='cpu',
                imgsz=320,
                batch=4,
                patience=5,
                save=True,
                verbose=False
            )
            
            # Update progress
            if progress_callback:
                for i in range(num_epochs):
                    progress_callback(i + 1, num_epochs)
            
            # Save new model
            new_model_path = f"models/yolov8n-seg_retrained_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
            model.save(new_model_path)
            
            # Update main model
            model.save(self.model_path)
            
            # Record in history
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'epochs': num_epochs,
                'learning_rate': learning_rate,
                'model_path': new_model_path,
                'results': str(results)
            }
            self.training_history.append(history_entry)
            
            logger.info(f"Retraining completed: {new_model_path}")
            self.is_training = False
            
            return history_entry
        
        except Exception as e:
            logger.error(f"Retraining error: {str(e)}")
            self.is_training = False
            raise
    
    def cancel(self):
        """Cancel ongoing training"""
        self.is_training = False
        logger.info("Training cancelled")
    
    def get_history(self):
        """Get training history"""
        return self.training_history
