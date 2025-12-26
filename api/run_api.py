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
    
    # Azure uses PORT environment variable - read it directly
    port_env = os.getenv("PORT")
    if port_env:
        port = int(port_env)
    else:
        port = int(os.getenv("FASTAPI_PORT", "8000"))
    
    # Host: Azure needs 0.0.0.0, local uses localhost
    host_env = os.getenv("HOST")
    if host_env:
        host = host_env
    elif os.getenv("WEBSITE_HOSTNAME") or os.getenv("PORT"):
        # Azure deployment
        host = "0.0.0.0"
    else:
        host = "localhost"
    
    print("="*60)
    print("Chip-and-Hole Detection API (FastAPI)")
    print("="*60)
    print(f"Environment: {Config.FASTAPI_ENV}")
    print(f"Debug: {Config.FASTAPI_DEBUG}")
    print(f"PORT env var: {os.getenv('PORT', 'not set')}")
    print(f"Host: {host}, Port: {port}")
    print(f"API available at: http://{host}:{port}")
    print(f"Documentation: http://{host}:{port}/docs")
    print(f"Health check: http://{host}:{port}/health")
    print("="*60)
    
    # Configure workers based on environment
    # Production: 1 worker (can be scaled horizontally on Azure)
    # Development: 1 worker with reload enabled
    workers = 1 if not Config.FASTAPI_DEBUG else None
    
    try:
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
    except Exception as e:
        print(f"ERROR starting server: {e}")
        import traceback
        traceback.print_exc()
        raise
