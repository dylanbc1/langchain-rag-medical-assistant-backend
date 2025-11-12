"""Retriever configuration for semantic search."""
from typing import Any, Dict, Optional

from app.rag.vectorstore import load_vectorstore
from app.core.logger import get_logger

LOGGER = get_logger(__name__)


def get_retriever(
    search_kwargs: Optional[Dict[str, Any]] = None,
    search_type: str = "mmr",
    vectorstore: Optional[Any] = None,
) -> Any:
    """
    Create a retriever with MMR (Maximum Marginal Relevance) for diversity.
    
    Args:
        search_kwargs: Custom search parameters to override defaults
        search_type: Type of search ("mmr", "similarity", "similarity_score_threshold")
        vectorstore: Optional vectorstore instance (loads if not provided)
    
    Returns:
        Configured retriever instance
    """
    # load vectorstore if not provided
    vectorstore = vectorstore or load_vectorstore()
    
    # MMR parameters for better diversity and coverage
    # MMR balances relevance with diversity to avoid redundant results
    kwargs = {
        "k": 12,  # number of documents to retrieve
        "fetch_k": 20,  # larger pool for MMR selection (must be >= k)
        "lambda_mult": 0.5  # balance between relevance (1.0) and diversity (0.0)
    }
    # override with custom parameters if provided
    if search_kwargs:
        kwargs.update(search_kwargs)
    
    # convert vectorstore to retriever with specified search type and parameters
    return vectorstore.as_retriever(search_type=search_type, search_kwargs=kwargs)