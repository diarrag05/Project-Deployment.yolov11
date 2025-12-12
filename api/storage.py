"""
Storage manager for validated images waiting for retraining.
Manages the storage and retrieval of validated images and their labels.
"""
import shutil
import uuid
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json


class StorageManager:
    """Manages storage of validated images for active learning."""
    
    def __init__(self, storage_dir: Path):
        """
        Initialize storage manager.
        
        Args:
            storage_dir: Directory to store validated images
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories
        self.images_dir = self.storage_dir / 'images'
        self.labels_dir = self.storage_dir / 'labels'
        self.metadata_dir = self.storage_dir / 'metadata'
        
        # Ensure directories exist
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.labels_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
    
    def save_validated_image(
        self,
        image_path: Path,
        labels_path: Path,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Save a validated image and its labels to storage.
        
        Args:
            image_path: Path to the validated image
            labels_path: Path to the labels file
            metadata: Optional metadata dictionary
            
        Returns:
            Storage ID (unique identifier for this validated image)
        """
        storage_id = str(uuid.uuid4())
        
        # Copy files
        image_dest = self.images_dir / f"{storage_id}{image_path.suffix}"
        labels_dest = self.labels_dir / f"{storage_id}.txt"
        
        shutil.copy2(image_path, image_dest)
        shutil.copy2(labels_path, labels_dest)
        
        # Save metadata
        metadata_dict = {
            'storage_id': storage_id,
            'original_image_path': str(image_path),
            'original_labels_path': str(labels_path),
            'saved_at': datetime.now().isoformat(),
            'image_path': str(image_dest),
            'labels_path': str(labels_dest),
            **(metadata or {})
        }
        
        metadata_file = self.metadata_dir / f"{storage_id}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata_dict, f, indent=2)
        
        return storage_id
    
    def get_validated_images(self) -> List[Dict]:
        """
        Get list of all validated images.
        
        Returns:
            List of metadata dictionaries
        """
        validated_images = []
        
        for metadata_file in self.metadata_dir.glob('*.json'):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                validated_images.append(metadata)
        
        # Sort by saved_at (newest first)
        validated_images.sort(key=lambda x: x.get('saved_at', ''), reverse=True)
        
        return validated_images
    
    def get_validated_image(self, storage_id: str) -> Optional[Dict]:
        """
        Get metadata for a specific validated image.
        
        Args:
            storage_id: Storage ID
            
        Returns:
            Metadata dictionary or None if not found
        """
        metadata_file = self.metadata_dir / f"{storage_id}.json"
        
        if not metadata_file.exists():
            return None
        
        with open(metadata_file, 'r') as f:
            return json.load(f)
    
    def move_to_dataset(
        self,
        storage_id: str
    ) -> Tuple[Path, Path]:
        """
        Move validated image to dataset directory for training.
        
        Args:
            storage_id: Storage ID
            
        Returns:
            Tuple of (new_image_path, new_labels_path)
        """
        metadata = self.get_validated_image(storage_id)
        if not metadata:
            raise ValueError(f"Validated image not found: {storage_id}")
        
        image_path = Path(metadata['image_path'])
        labels_path = Path(metadata['labels_path'])
        
        # Import here to avoid circular imports
        from backend.src.services import TrainingService
        
        training_service = TrainingService()
        new_image_path, new_labels_path = training_service.add_image_to_dataset(
            image_path,
            labels_path
        )
        
        return new_image_path, new_labels_path
    
    def move_all_to_dataset(self) -> List[Tuple[Path, Path]]:
        """
        Move all validated images to training dataset directory.
        
        Returns:
            List of tuples (new_image_path, new_labels_path)
        """
        validated_images = self.get_validated_images()
        moved = []
        
        for metadata in validated_images:
            storage_id = metadata['storage_id']
            try:
                result = self.move_to_dataset(storage_id)
                moved.append(result)
            except Exception as e:
                print(f"Error moving {storage_id}: {e}")
        
        return moved
    
    def delete_validated_image(self, storage_id: str) -> bool:
        """
        Delete a validated image from storage.
        
        Args:
            storage_id: Storage ID
            
        Returns:
            True if deleted, False if not found
        """
        metadata = self.get_validated_image(storage_id)
        if not metadata:
            return False
        
        # Delete files
        image_path = Path(metadata['image_path'])
        labels_path = Path(metadata['labels_path'])
        metadata_file = self.metadata_dir / f"{storage_id}.json"
        
        if image_path.exists():
            image_path.unlink()
        if labels_path.exists():
            labels_path.unlink()
        if metadata_file.exists():
            metadata_file.unlink()
        
        return True
    
    def count_validated_images(self) -> int:
        """Get count of validated images."""
        return len(list(self.metadata_dir.glob('*.json')))

