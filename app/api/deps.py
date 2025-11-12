"""FastAPI dependencies for dependency injection."""
from functools import lru_cache
from typing import Annotated, Any, Optional

from fastapi import Depends

from app.core.config import Settings, load_settings
from app.rag.retriever import get_retriever
from app.rag.vectorstore import load_vectorstore

# global cache for expensive objects to avoid recreating on every request
_cached_vectorstore: Optional[Any] = None
_cached_retriever: Optional[Any] = None

# cache settings to avoid reloading on every request
# lru_cache ensures settings are only loaded once
@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)."""
    return load_settings()


def get_vectorstore_dep(settings: Annotated[Settings, Depends(get_settings)]):
    """Dependency to get vectorstore (cached)."""
    global _cached_vectorstore
    # create vectorstore on first call, then reuse the cached instance
    if _cached_vectorstore is None:
        _cached_vectorstore = load_vectorstore(settings=settings)
    return _cached_vectorstore


def get_retriever_dep(
    vectorstore: Annotated[Any, Depends(get_vectorstore_dep)] = None,
    settings: Annotated[Settings, Depends(get_settings)] = None,
):
    """Dependency to get retriever (cached)."""
    global _cached_retriever
    # create retriever on first call, then reuse the cached instance
    if _cached_retriever is None:
        _cached_retriever = get_retriever(vectorstore=vectorstore)
    return _cached_retriever



