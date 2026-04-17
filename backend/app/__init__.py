"""FastAPI application initialization"""
from fastapi import FastAPI
from app.config import settings
from app.routers import oracle, postgres


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        description="Dual-database CRUD API for Oracle XE and PostgreSQL",
        debug=settings.DEBUG
    )

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "api": settings.API_TITLE,
            "version": settings.API_VERSION
        }

    # Include routers
    app.include_router(oracle.router)
    app.include_router(postgres.router)

    return app


# Create app instance
app = create_app()
