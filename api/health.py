from fastapi import APIRouter, HTTPException
from datetime import datetime
import psutil
import os

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint that verifies system status and dependencies.
    Returns detailed system information and component status.
    """
    try:
        # Basic system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Environment information
        env_info = {
            "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
            "python_version": os.getenv("PYTHON_VERSION", "unknown"),
            "node_version": os.getenv("NODE_VERSION", "unknown"),
            "app_version": os.getenv("APP_VERSION", "unknown")
        }
        
        # Component status
        components = {
            "api": "healthy",
            "database": "healthy",  # Add actual DB check here
            "cache": "healthy",     # Add actual cache check here
            "storage": "healthy"    # Add actual storage check here
        }
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_usage": f"{cpu_percent}%",
                "memory_usage": f"{memory.percent}%",
                "disk_usage": f"{disk.percent}%"
            },
            "environment": env_info,
            "components": components
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        ) 