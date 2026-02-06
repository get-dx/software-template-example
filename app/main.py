import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.endpoints.service import router
from core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Software template service for creating GitHub repositories from cookiecutter templates",
    version="1.0.0",
    openapi_url=f"{settings.API_STR}/openapi.json",
    docs_url=f"{settings.API_STR}/docs",
    redoc_url=f"{settings.API_STR}/redoc"
)

# Add CORS middleware (configure as needed for your environment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router, prefix=settings.API_STR, tags=["service"])


@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info(f"Starting {settings.PROJECT_NAME}")
    logger.info(f"API documentation available at {settings.API_STR}/docs")
    logger.info(f"Webhook endpoint: {settings.API_STR}/service")


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": f"{settings.API_STR}/docs",
        "webhook_endpoint": f"{settings.API_STR}/service"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
