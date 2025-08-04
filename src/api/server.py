"""
Main FastAPI server application for the subscription analytics platform.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from ..core.config import get_settings
from ..database.connection import get_db_manager
from ..ai.semantic_learner import get_semantic_learner
from .routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/api_server.log')
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("🚀 Starting Subscription Analytics API Server")
    
    # Initialize components
    try:
        settings = get_settings()
        
        # Test database connection
        db_manager = get_db_manager()
        if db_manager.test_connection():
            logger.info("✅ Database connection established")
        else:
            logger.warning("⚠️ Database connection failed")
        
        # Initialize semantic learner
        semantic_learner = get_semantic_learner()
        if semantic_learner.model:
            logger.info("✅ Semantic learning model loaded")
        else:
            logger.warning("⚠️ Semantic learning model not available")
        
        logger.info("🎯 All components initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Subscription Analytics API Server")

# Create FastAPI app
app = FastAPI(
    title="Subscription Analytics API",
    description="AI-powered analytics platform for subscription and payment data",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")

# Root endpoint
@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": "Subscription Analytics API",
        "version": "2.0.0",
        "description": "AI-powered analytics platform for subscription and payment data",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

def run_server():
    """Run the server."""
    settings = get_settings()
    logger.info(f"🚀 Starting server on {settings.server.host}:{settings.server.port}")
    logger.info(f"📊 Debug mode: {settings.server.debug}")
    logger.info(f"🔗 API documentation: http://{settings.server.host}:{settings.server.port}/docs")
    
    # Configure uvicorn with better settings for stability
    uvicorn.run(
        "src.api.server:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.debug,
        log_level=settings.server.log_level.lower(),
        workers=1,  # Single worker for stability
        loop="asyncio",
        timeout_keep_alive=30,
        timeout_graceful_shutdown=30,
        access_log=True
    )

if __name__ == "__main__":
    run_server() 