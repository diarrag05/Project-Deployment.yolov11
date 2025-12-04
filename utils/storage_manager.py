"""
Storage Manager
Handles labeled data and predictions storage
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class StorageManager:
    def __init__(self, base_path='labeled_data'):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.predictions_file = self.base_path / 'predictions.jsonl'
        self.labels_dir = self.base_path / 'labels'
        self.labels_dir.mkdir(exist_ok=True)
    
    def save_labels(self, image_id, masks, timestamp):
        """Save labeled data"""
        try:
            label_id = str(uuid.uuid4())
            
            label_data = {
                'label_id': label_id,
                'image_id': image_id,
                'masks': masks,
                'timestamp': timestamp
            }
            
            # Save to file
            label_file = self.labels_dir / f"{label_id}.json"
            with open(label_file, 'w') as f:
                json.dump(label_data, f, indent=2)
            
            logger.info(f"Labels saved: {label_id}")
            return label_id
        
        except Exception as e:
            logger.error(f"Save labels error: {str(e)}")
            raise
    
    def get_all_labels(self):
        """Get all labeled data"""
        try:
            labels = []
            for label_file in self.labels_dir.glob('*.json'):
                with open(label_file, 'r') as f:
                    labels.append(json.load(f))
            return labels
        
        except Exception as e:
            logger.error(f"Get labels error: {str(e)}")
            return []
    
    def get_label(self, label_id):
        """Get specific label"""
        try:
            label_file = self.labels_dir / f"{label_id}.json"
            if label_file.exists():
                with open(label_file, 'r') as f:
                    return json.load(f)
            return None
        
        except Exception as e:
            logger.error(f"Get label error: {str(e)}")
            return None
    
    def save_prediction(self, image_id, void_rate, chip_area, holes_area, confidence):
        """Save prediction result"""
        try:
            prediction = {
                'image_id': image_id,
                'void_rate': void_rate,
                'chip_area': chip_area,
                'holes_area': holes_area,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat()
            }
            
            # Append to JSONL file
            with open(self.predictions_file, 'a') as f:
                f.write(json.dumps(prediction) + '\n')
            
            logger.info(f"Prediction saved: {image_id}")
        
        except Exception as e:
            logger.error(f"Save prediction error: {str(e)}")
    
    def get_all_predictions(self):
        """Get all predictions"""
        try:
            predictions = []
            if self.predictions_file.exists():
                with open(self.predictions_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            predictions.append(json.loads(line))
            return predictions
        
        except Exception as e:
            logger.error(f"Get predictions error: {str(e)}")
            return []
