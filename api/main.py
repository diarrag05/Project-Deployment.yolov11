"""
FastAPI application for chip-and-hole detection system.
Provides REST API for image analysis, segmentation, validation, and retraining.
"""
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.src.config import Config
from backend.src.utils.logger import get_logger
from api.routes import router
from api.storage import StorageManager
from api.training_job import TrainingJobManager

# Initialize logger
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Chip-and-Hole Detection API",
    description="API for analyzing electronic components with YOLOv11",
    version="1.0.0",
    docs_url="/docs",  # Enable Swagger UI
    redoc_url="/redoc",  # Enable ReDoc
    openapi_url="/openapi.json"  # Enable OpenAPI schema
)

# CORS middleware (FastAPI has built-in CORS support)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
storage_manager = StorageManager(Config.OUTPUT_DIR / 'validated_images')
training_job_manager = TrainingJobManager()

# Store managers and config in app state
app.state.storage_manager = storage_manager
app.state.training_job_manager = training_job_manager
app.state.upload_dir = Config.OUTPUT_DIR / 'uploads'
app.state.upload_dir.mkdir(parents=True, exist_ok=True)

# Register routes
app.include_router(router, prefix="/api", tags=["api"])

# Serve frontend
frontend_dir = Path(__file__).parent.parent / 'frontend'

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the web interface."""
    index_file = frontend_dir / 'index.html'
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>Frontend not found</h1>")

@app.get("/robots.txt")
async def robots_txt():
    """Serve robots.txt to prevent search engine indexing."""
    robots_file = frontend_dir / 'robots.txt'
    if robots_file.exists():
        return FileResponse(robots_file, media_type="text/plain")
    # Return default robots.txt if file doesn't exist
    return Response(content="User-agent: *\nDisallow: /", media_type="text/plain")

@app.get("/health")
async def health():
    """Health check endpoint - responds immediately for Azure startup probe."""
    return {"status": "healthy", "ready": True}

# Note: SAM model is loaded lazily on first use (not at startup)
# This allows the application to start quickly and pass Azure's startup probe
# The model will be loaded when the first SAM segmentation request is made

logger.info("FastAPI application initialized successfully")

