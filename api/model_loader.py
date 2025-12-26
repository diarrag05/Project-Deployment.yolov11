"""
Model loader for downloading YOLO model from Azure Blob Storage.
Downloads the model lazily when needed (not at startup) to avoid timeout issues.
"""
import os
from pathlib import Path
from backend.src.config import Config
from backend.src.utils.logger import get_logger

logger = get_logger(__name__)


def download_from_blob(blob_name: str, local_path: Path) -> bool:
    """
    Download a file from Azure Blob Storage to local path.
    
    Args:
        blob_name: Name of the blob in storage
        local_path: Local path where to save the file
    
    Returns:
        bool: True if successful, False otherwise
    """
    # If file already exists, no need to download
    if local_path.exists():
        logger.info(f"File already exists: {local_path}")
        return True
    
    # Get Azure Blob Storage credentials from environment
    storage_account = os.getenv("AZURE_STORAGE_ACCOUNT")
    storage_key = os.getenv("AZURE_STORAGE_KEY")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER", "models")
    
    if not storage_account or not storage_key:
        logger.warning(
            "Azure Blob Storage credentials not set. "
            "Set AZURE_STORAGE_ACCOUNT and AZURE_STORAGE_KEY environment variables."
        )
        return False
    
    try:
        from azure.storage.blob import BlobServiceClient
        
        logger.info(f"Downloading {blob_name} from Azure Blob Storage...")
        logger.info(f"Storage account: {storage_account}, Container: {container_name}")
        
        # Create BlobServiceClient
        account_url = f"https://{storage_account}.blob.core.windows.net"
        blob_service = BlobServiceClient(
            account_url=account_url,
            credential=storage_key
        )
        
        # Get blob client
        blob_client = blob_service.get_blob_client(
            container=container_name,
            blob=blob_name
        )
        
        # Check if blob exists
        if not blob_client.exists():
            logger.error(f"Blob not found: {container_name}/{blob_name}")
            return False
        
        # Ensure directory exists
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download file
        logger.info(f"Downloading {blob_name} to {local_path}...")
        with open(local_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        
        # Verify file was downloaded
        if local_path.exists() and local_path.stat().st_size > 0:
            file_size_mb = local_path.stat().st_size / (1024 * 1024)
            logger.info(f"File downloaded successfully: {local_path} ({file_size_mb:.2f} MB)")
            return True
        else:
            logger.error("File is empty or doesn't exist after download")
            return False
            
    except ImportError:
        logger.error(
            "azure-storage-blob package not installed. "
            "Install it with: pip install azure-storage-blob"
        )
        return False
    except Exception as e:
        logger.error(f"Failed to download {blob_name} from Blob Storage: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def download_model_from_blob():
    """
    Download YOLO model (best.pt) from Azure Blob Storage if not exists locally.
    Uses lazy loading - only downloads when needed.
    
    Returns:
        bool: True if model exists (was already there or downloaded), False otherwise
    """
    model_path = Config.DEFAULT_MODEL
    model_blob_name = os.getenv("AZURE_MODEL_BLOB_NAME", "best.pt")
    
    return download_from_blob(model_blob_name, model_path)


def download_sam_from_blob():
    """
    Download SAM checkpoint from Azure Blob Storage if not exists locally.
    
    Returns:
        bool: True if SAM checkpoint exists (was already there or downloaded), False otherwise
    """
    sam_model_type = os.getenv("SAM_MODEL_TYPE", "vit_h")
    sam_blob_name = f"sam_{sam_model_type}_4b8939.pth"
    sam_path = Config.MODELS_DIR / sam_blob_name
    
    return download_from_blob(sam_blob_name, sam_path)

