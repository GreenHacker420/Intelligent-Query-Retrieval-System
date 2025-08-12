"""Main entry point for the Intelligent Query Retrieval System."""

import uvicorn
from src.api.main import app
from src.core.config import get_settings


if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
