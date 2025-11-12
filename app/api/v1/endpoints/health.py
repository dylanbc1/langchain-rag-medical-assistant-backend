"""Health check endpoint."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring service availability."""
    # simple health check that returns service status
    return {"status": "healthy", "service": "rag-medical-assistant-backend"}

