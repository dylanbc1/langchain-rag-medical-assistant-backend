"""Vector store management with ChromaDB."""
from typing import Any, Optional

# try to import from langchain_chroma first (recommended), fallback to langchain_community
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

from app.core.config import Settings, get_chroma_client, load_settings
from app.rag.embeddings import get_embedding_model
from app.core.logger import get_logger

LOGGER = get_logger(__name__)


def load_vectorstore(settings: Optional[Settings] = None) -> Any:
    """Load the vector store from ChromaDB and create LangChain wrapper."""
    # load settings if not provided
    settings = settings or load_settings()
    # get ChromaDB HTTP client connection
    client = get_chroma_client(settings)

    # handle NotFoundError import for different ChromaDB versions
    try:
        from chromadb.errors import NotFoundError
    except ImportError:
        NotFoundError = Exception  # type: ignore

    # check if collection exists in ChromaDB
    try:
        collection = client.get_collection(settings.chroma_collection)
    except NotFoundError as exc:
        raise FileNotFoundError(
            f"No se encontró la colección '{settings.chroma_collection}' en Chroma. "
            "Ejecuta el endpoint /ingest para indexar documentos."
        ) from exc

    # verify collection has documents
    doc_count = collection.count()
    if doc_count == 0:
        raise RuntimeError(
            f"La colección '{settings.chroma_collection}' existe pero no contiene vectores. "
            "Ejecuta el endpoint /ingest para indexar documentos."
        )

    # get embedding model identifier from collection metadata
    # this ensures we use the same embedding model that was used for indexing
    metadata = collection.metadata or {}
    identifier = metadata.get("embedding_model", "paraphrase-multilingual-mpnet-base-v2")

    # get the embedding model (must match the one used during indexing)
    embedding_config = get_embedding_model()
    embeddings = embedding_config.embedding

    # create LangChain Chroma wrapper that connects to the existing collection
    # this wrapper provides the interface for semantic search
    vectorstore = Chroma(
        client=client,
        collection_name=settings.chroma_collection,
        embedding_function=embeddings,
    )
    return vectorstore

