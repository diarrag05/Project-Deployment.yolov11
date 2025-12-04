"""
Feedback Management System for Active Learning
Handles user feedback collection, storage, and analysis
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class FeedbackManager:
    """Manages user feedback for model improvements"""
    
    def __init__(self, feedback_dir: str = "feedback_data"):
        """
        Initialize FeedbackManager
        
        Args:
            feedback_dir: Directory to store feedback files
        """
        self.feedback_dir = Path(feedback_dir)
        self.feedback_dir.mkdir(exist_ok=True)
        
        # Feedback storage files
        self.feedback_file = self.feedback_dir / "feedback_log.jsonl"
        self.stats_file = self.feedback_dir / "feedback_stats.json"
        
    def add_feedback(
        self,
        image_filename: str,
        prediction: Dict,
        user_feedback: str,
        confidence: float = None,
        notes: str = None
    ) -> Dict:
        """
        Record user feedback on a prediction
        
        Args:
            image_filename: Name of the image file
            prediction: Original model prediction
            user_feedback: 'correct', 'incorrect', 'partial', 'unsure'
            confidence: User confidence in the feedback (0-1)
            notes: Additional notes from user
            
        Returns:
            Feedback record
        """
        feedback_record = {
            "timestamp": datetime.now().isoformat(),
            "image_filename": image_filename,
            "prediction": prediction,
            "user_feedback": user_feedback,
            "confidence": confidence or 1.0,
            "notes": notes,
            "status": "pending"  # pending, processed, used_for_training
        }
        
        try:
            # Append to feedback log (JSONL format)
            with open(self.feedback_file, 'a') as f:
                f.write(json.dumps(feedback_record) + '\n')
            
            logger.info(f"Feedback recorded for {image_filename}: {user_feedback}")
            
            # Update statistics
            self._update_stats()
            
            return {"success": True, "record": feedback_record}
        except Exception as e:
            logger.error(f"Error recording feedback: {e}")
            return {"success": False, "error": str(e)}
    
    def get_pending_feedback(self, limit: int = None) -> List[Dict]:
        """
        Get all pending feedback records
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of pending feedback records
        """
        if not self.feedback_file.exists():
            return []
        
        pending = []
        try:
            with open(self.feedback_file, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    if record.get('status') == 'pending':
                        pending.append(record)
                        if limit and len(pending) >= limit:
                            break
        except Exception as e:
            logger.error(f"Error reading feedback: {e}")
        
        return pending
    
    def get_incorrect_predictions(self, limit: int = None) -> List[Dict]:
        """
        Get predictions marked as incorrect (good for retraining)
        
        Args:
            limit: Maximum number of records
            
        Returns:
            List of incorrect prediction records
        """
        if not self.feedback_file.exists():
            return []
        
        incorrect = []
        try:
            with open(self.feedback_file, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    if record.get('user_feedback') in ['incorrect', 'partial']:
                        incorrect.append(record)
                        if limit and len(incorrect) >= limit:
                            break
        except Exception as e:
            logger.error(f"Error reading feedback: {e}")
        
        return incorrect
    
    def mark_as_processed(self, record_ids: List[str]) -> Dict:
        """
        Mark feedback records as processed (used for training)
        
        Args:
            record_ids: List of record IDs (timestamps)
            
        Returns:
            Status of operation
        """
        if not self.feedback_file.exists():
            return {"success": False, "error": "No feedback file"}
        
        try:
            all_records = []
            with open(self.feedback_file, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    if record['timestamp'] in record_ids:
                        record['status'] = 'processed'
                    all_records.append(record)
            
            # Rewrite file
            with open(self.feedback_file, 'w') as f:
                for record in all_records:
                    f.write(json.dumps(record) + '\n')
            
            logger.info(f"Marked {len(record_ids)} records as processed")
            self._update_stats()
            
            return {"success": True, "count": len(record_ids)}
        except Exception as e:
            logger.error(f"Error marking feedback: {e}")
            return {"success": False, "error": str(e)}
    
    def get_stats(self) -> Dict:
        """
        Get feedback statistics
        
        Returns:
            Statistics dictionary
        """
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "total_feedback": 0,
            "correct": 0,
            "incorrect": 0,
            "partial": 0,
            "unsure": 0,
            "accuracy": 0.0
        }
    
    def _update_stats(self):
        """Update feedback statistics"""
        if not self.feedback_file.exists():
            return
        
        stats = {
            "total_feedback": 0,
            "correct": 0,
            "incorrect": 0,
            "partial": 0,
            "unsure": 0,
            "pending": 0,
            "processed": 0,
            "accuracy": 0.0,
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            with open(self.feedback_file, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    stats["total_feedback"] += 1
                    
                    feedback_type = record.get('user_feedback', 'unsure')
                    stats[feedback_type] = stats.get(feedback_type, 0) + 1
                    
                    status = record.get('status', 'pending')
                    stats[status] = stats.get(status, 0) + 1
            
            # Calculate accuracy
            total_correct_incorrect = stats['correct'] + stats['incorrect'] + stats['partial']
            if total_correct_incorrect > 0:
                stats['accuracy'] = stats['correct'] / total_correct_incorrect
            
            # Save stats
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
        
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
    
    def get_training_candidates(self, min_count: int = 5) -> Dict:
        """
        Get suggestions for retraining based on feedback
        
        Args:
            min_count: Minimum number of incorrect predictions to suggest training
            
        Returns:
            Training recommendation
        """
        stats = self.get_stats()
        incorrect = stats.get('incorrect', 0) + stats.get('partial', 0)
        
        recommendation = {
            "should_retrain": incorrect >= min_count,
            "incorrect_count": incorrect,
            "total_feedback": stats.get('total_feedback', 0),
            "accuracy": stats.get('accuracy', 0),
            "next_threshold": min_count
        }
        
        return recommendation
    
    def export_feedback_for_training(self, output_path: str) -> Dict:
        """
        Export feedback data for model retraining
        
        Args:
            output_path: Path to save training data
            
        Returns:
            Export status
        """
        try:
            incorrect = self.get_incorrect_predictions()
            
            export_data = {
                "total_samples": len(incorrect),
                "feedback_samples": incorrect,
                "export_time": datetime.now().isoformat(),
                "training_notes": "High priority samples from user feedback"
            }
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported {len(incorrect)} feedback samples for training")
            return {"success": True, "count": len(incorrect)}
        
        except Exception as e:
            logger.error(f"Error exporting feedback: {e}")
            return {"success": False, "error": str(e)}
    
    def clear_feedback(self, keep_processed: bool = True) -> Dict:
        """
        Clear feedback records (optional: keep processed ones)
        
        Args:
            keep_processed: Whether to keep already processed records
            
        Returns:
            Status of operation
        """
        try:
            if keep_processed and self.feedback_file.exists():
                processed = []
                with open(self.feedback_file, 'r') as f:
                    for line in f:
                        record = json.loads(line)
                        if record.get('status') == 'processed':
                            processed.append(record)
                
                with open(self.feedback_file, 'w') as f:
                    for record in processed:
                        f.write(json.dumps(record) + '\n')
                
                return {"success": True, "kept": len(processed)}
            else:
                self.feedback_file.unlink(missing_ok=True)
                return {"success": True, "kept": 0}
        
        except Exception as e:
            logger.error(f"Error clearing feedback: {e}")
            return {"success": False, "error": str(e)}
