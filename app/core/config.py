"""Configuration management using environment variables."""
import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from .logger import get_logger

LOGGER = get_logger(__name__)


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""
    llm_api_key: Optional[str]  # API key for LLM (Gemini)
    llm_api_base: Optional[str]  # API base URL (optional for Gemini)
    llm_model_name: str  # name of the LLM model to use
    chroma_host: str  # ChromaDB server hostname
    chroma_port: int  # ChromaDB server port
    chroma_ssl: bool  # whether to use SSL for ChromaDB connection
    chroma_collection: str  # name of the ChromaDB collection
    chroma_api_key: Optional[str]  # API key for ChromaDB (if required)


def load_settings() -> Settings:
    """Load settings from environment variables."""
    from pathlib import Path
    
    # load environment variables from .env file
    env_path = Path(".env")
    load_dotenv()
    
    # parse CHROMA_SSL as boolean (accepts various true/false representations)
    chroma_ssl_env = os.getenv("CHROMA_SSL", "false").lower()
    chroma_ssl = chroma_ssl_env in {"1", "true", "yes", "on"}
    
    # load LLM configuration
    llm_api_key = os.getenv("LLM_API_KEY")
    llm_api_base = os.getenv("LLM_API_BASE")
    llm_model_name = os.getenv("LLM_MODEL_NAME", "gemini-2.0-flash")
    
    # create Settings object with all configuration values
    # use defaults for optional values if not provided in .env
    settings = Settings(
        llm_api_key=llm_api_key,
        llm_api_base=llm_api_base,
        llm_model_name=llm_model_name,
        chroma_host=os.getenv("CHROMA_HOST", "localhost"),
        chroma_port=int(os.getenv("CHROMA_PORT", "8000")),
        chroma_ssl=chroma_ssl,
        chroma_collection=os.getenv("CHROMA_COLLECTION", "medical_guides"),
        chroma_api_key=os.getenv("CHROMA_API_KEY"),
    )
    return settings


def get_chroma_client(settings: Optional[Settings] = None):
    """Create and return a ChromaDB HTTP client."""
    # load settings if not provided
    settings = settings or load_settings()
    
    # check if chromadb is installed
    try:
        import chromadb
    except ImportError as exc:
        raise ImportError(
            "chromadb no está instalado. Ejecutar `pip install chromadb`."
        ) from exc

    # prepare headers if API key is configured
    headers = None
    if settings.chroma_api_key:
        headers = {"Authorization": f"Bearer {settings.chroma_api_key}"}

    # create HTTP client connection to ChromaDB server
    client = chromadb.HttpClient(
        host=settings.chroma_host,
        port=settings.chroma_port,
        ssl=settings.chroma_ssl,
        headers=headers,
    )
    return client

