"""Embedding model configuration."""
import importlib
from dataclasses import dataclass
from typing import Optional

from app.core.logger import get_logger

LOGGER = get_logger(__name__)

# global cache for embedding model to avoid reloading on every request
_cached_embedding_config: Optional["EmbeddingConfig"] = None


def _load_hf_embeddings():
    """Load HuggingFace embeddings class from available modules."""
    # try to import from langchain-huggingface first (recommended module)
    try:
        module = importlib.import_module("langchain_huggingface")
        return getattr(module, "HuggingFaceEmbeddings")
    except ModuleNotFoundError:
        pass
    
    # fallback to deprecated module in langchain-community
    try:
        module = importlib.import_module("langchain_community.embeddings")
        return getattr(module, "HuggingFaceEmbeddings")
    except ModuleNotFoundError as exc:
        raise ImportError(
            "langchain-huggingface o langchain-community no está instalado. "
            "Ejecuta `pip install langchain-huggingface`."
        ) from exc


@dataclass(frozen=True)
class EmbeddingConfig:
    """Embedding model configuration container."""
    embedding: object  # the actual embedding model instance
    identifier: str  # model identifier for tracking


def get_embedding_model(force_reload: bool = False) -> EmbeddingConfig:
    """Get the configured embedding model (cached for performance)."""
    global _cached_embedding_config
    
    # reload if cache is empty or force_reload is True
    if _cached_embedding_config is None or force_reload:
        # dynamically load the HuggingFaceEmbeddings class
        HuggingFaceEmbeddings = _load_hf_embeddings()
        
        # use multilingual model that works better with Spanish
        # this model supports multiple languages including Spanish
        model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        # create the embedding model instance
        # this will download the model on first use (can take 30-60 seconds)
        embedding = HuggingFaceEmbeddings(model_name=model_name)
        # cache the configuration for reuse
        _cached_embedding_config = EmbeddingConfig(embedding=embedding, identifier="paraphrase-multilingual-mpnet-base-v2")
    
    return _cached_embedding_config

