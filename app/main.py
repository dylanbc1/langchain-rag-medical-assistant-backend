"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import health, ingest, qa
from app.core.config import load_settings
from app.core.logger import get_logger
from app.rag.embeddings import get_embedding_model
from app.rag.vectorstore import load_vectorstore

LOGGER = get_logger(__name__)

# create the main FastAPI application instance
# this is the entry point for all API requests
app = FastAPI(
    title="RAG Medical Assistant API",
    description="API para asistente médico basado en RAG con LangChain y Gemini",
    version="1.0.0",
)

# configure CORS middleware to allow cross-origin requests
# in production, restrict allow_origins to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register all API routers with the /api/v1 prefix
# each router handles a specific set of endpoints
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(qa.router, prefix="/api/v1", tags=["qa"])
app.include_router(ingest.router, prefix="/api/v1", tags=["ingest"])


@app.on_event("startup")
async def startup_event():
    """Pre-load expensive resources on startup to avoid delays on first request."""
    LOGGER.info("RAG Medical Assistant Backend starting up")
    
    try:
        # pre-load the embedding model which can take 30-60 seconds on first run
        # this gets cached so subsequent requests are fast
        embedding_config = get_embedding_model()
        LOGGER.info("Embedding model loaded: %s", embedding_config.identifier)
        
        # pre-load the vectorstore connection to ChromaDB
        # this also caches the connection for reuse
        settings = load_settings()
        vectorstore = load_vectorstore(settings=settings)
        LOGGER.info("Vectorstore loaded and ready")
        
    except Exception as e:
        # if pre-loading fails, resources will be loaded on-demand
        # this allows the app to start even if ChromaDB is temporarily unavailable
        import traceback
        LOGGER.error("Error pre-loading resources (will load on-demand): %s", str(e))
        LOGGER.debug("Traceback: %s", traceback.format_exc())


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup tasks when the application shuts down."""
    LOGGER.info("RAG Medical Assistant Backend shutting down")


@app.get("/")
async def root():
    """Root endpoint that returns basic API information."""
    return {
        "message": "RAG Medical Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }

