"""FastAPI application initialization"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import oracle, postgres, jposee


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        description="Dual-database CRUD API for Oracle XE and PostgreSQL with jPOS EE integration",
        debug=settings.DEBUG
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
    app.include_router(jposee.router)

    return app


# Create app instance
app = create_app()
