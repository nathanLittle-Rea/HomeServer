"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.files import router as files_router
from src.api.monitoring import router as monitoring_router
from src.config import settings

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-purpose home server with media, files, automation, and AI",
)

# Include routers
app.include_router(files_router)
app.include_router(monitoring_router)

# Mount static files for dashboard
app.mount("/static", StaticFiles(directory="src/static"), name="static")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - basic info about the server."""
    return {
        "message": "Welcome to HomeServer",
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint for monitoring."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version,
        },
    )


@app.get("/api/v1/info")
async def api_info() -> dict[str, str | dict[str, str]]:
    """API information endpoint."""
    return {
        "api_version": "v1",
        "services": {
            "media": "planned",
            "files": "active",
            "automation": "planned",
            "ai": "planned",
            "monitoring": "active",
            "web": "planned",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
