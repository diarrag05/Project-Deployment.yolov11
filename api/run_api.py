"""
Startup script for FastAPI API with Uvicorn.
Uses environment variables for configuration.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn
from api.main import app
from backend.src.config import Config

if __name__ == '__main__':
    import os
    
    # Azure uses PORT environment variable
    port = int(os.getenv("PORT", Config.FASTAPI_PORT))
    host = os.getenv("HOST", Config.FASTAPI_HOST)
    
    print("="*60)
    print("Chip-and-Hole Detection API (FastAPI)")
    print("="*60)
    print(f"Environment: {Config.FASTAPI_ENV}")
    print(f"Debug: {Config.FASTAPI_DEBUG}")
    print(f"API available at: http://{host}:{port}")
    print(f"Documentation: http://{host}:{port}/docs")
    print(f"Health check: http://{host}:{port}/health")
    print("="*60)
    
    # Configure workers based on environment
    # Production: 1 worker (can be scaled horizontally on Azure)
    # Development: 1 worker with reload enabled
    workers = 1 if not Config.FASTAPI_DEBUG else None
    
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        workers=workers,
        reload=Config.FASTAPI_DEBUG,
        log_level="info" if Config.FASTAPI_DEBUG else "warning",
        access_log=True,
        timeout_keep_alive=30  # Keep connections alive for 30 seconds
    )
