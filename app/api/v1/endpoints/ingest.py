"""Document ingestion endpoint."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.config import Settings, get_chroma_client, load_settings
from app.core.constants import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE
from app.core.logger import get_logger
from app.rag.embeddings import get_embedding_model
from app.rag.loader import load_pdf_documents
from app.rag.splitter import clean_documents, split_documents
from app.api.deps import get_settings

# try to import from langchain_chroma first (recommended), fallback to langchain_community
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

router = APIRouter()
LOGGER = get_logger(__name__)


class IngestRequest(BaseModel):
    """Request model for ingestion."""
    force: bool = False  # force re-indexing even if collection exists


class IngestResponse(BaseModel):
    """Response model for ingestion."""
    message: str  # status message
    documents_indexed: int  # number of documents indexed
    collection_name: str  # name of the ChromaDB collection


@router.post("/ingest", response_model=IngestResponse)
async def ingest_documents(
    request: IngestRequest,
    settings: Annotated[Settings, Depends(get_settings)] = None,
):
    """
    Ingest PDF documents from the data/pdfs directory.
    
    This endpoint processes PDFs, splits them into chunks, generates embeddings,
    and stores them in ChromaDB for semantic search.
    
    Args:
        request: Ingest request with optional force flag
        settings: Application settings
    
    Returns:
        Ingestion result with document count
    """
    try:
        # load settings if not provided
        settings = settings or load_settings()
        # get ChromaDB HTTP client connection
        client = get_chroma_client(settings)
        
        # load all PDF documents from the data/pdfs directory
        docs = load_pdf_documents()
        
        if not docs:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron archivos PDF en el directorio data/pdfs"
            )
        
        # clean documents: normalize text, remove headers, combine short pages
        cleaned_docs = clean_documents(docs)
        
        # split documents into chunks using RecursiveCharacterTextSplitter
        # chunks are sized according to DEFAULT_CHUNK_SIZE with DEFAULT_CHUNK_OVERLAP
        split_docs = split_documents(
            cleaned_docs,
            chunk_size=DEFAULT_CHUNK_SIZE,
            chunk_overlap=DEFAULT_CHUNK_OVERLAP,
        )
        
        # get the embedding model that will convert text chunks to vectors
        embedding_config = get_embedding_model()
        embeddings = embedding_config.embedding
        
        # store metadata about the ingestion process in the collection
        # this helps track which embedding model and chunking params were used
        collection_metadata = {
            "embedding_model": embedding_config.identifier,
            "chunk_size": DEFAULT_CHUNK_SIZE,
            "chunk_overlap": DEFAULT_CHUNK_OVERLAP,
        }
        
        # check if collection already exists in ChromaDB
        collection = client.get_or_create_collection(
            name=settings.chroma_collection,
            metadata=collection_metadata,
        )
        existing_count = collection.count()
        
        # if collection has documents and force is false, return early
        if existing_count > 0 and not request.force:
            return IngestResponse(
                message=f"La colección '{settings.chroma_collection}' ya contiene {existing_count} vectores. "
                       "Usa force=true para regenerarla.",
                documents_indexed=existing_count,
                collection_name=settings.chroma_collection,
            )
        
        # if force is true, delete existing collection and create a new one
        if existing_count > 0 and request.force:
            client.delete_collection(settings.chroma_collection)
            collection = client.create_collection(
                name=settings.chroma_collection,
                metadata=collection_metadata,
            )
        
        # filter metadata to ensure ChromaDB compatibility
        # ChromaDB only supports simple types (str, int, float, bool, None)
        try:
            from langchain_community.vectorstores.utils import filter_complex_metadata
            filtered_docs = filter_complex_metadata(split_docs)
        except ImportError:
            # manual filtering if utility not available
            filtered_docs = []
            for doc in split_docs:
                clean_meta = {}
                for k, v in (doc.metadata or {}).items():
                    if isinstance(v, (str, int, float, bool)) or v is None:
                        clean_meta[k] = v
                filtered_docs.append(
                    type(doc)(page_content=doc.page_content, metadata=clean_meta)
                )
        
        # create LangChain Chroma wrapper and add documents
        # this will generate embeddings and store them in ChromaDB
        vectorstore = Chroma(
            client=client,
            collection_name=settings.chroma_collection,
            embedding_function=embeddings,
            collection_metadata=collection_metadata,
        )
        
        # add all documents to the vectorstore
        # this triggers embedding generation and indexing
        vectorstore.add_documents(filtered_docs)
        
        # verify the final count of indexed documents
        collection = client.get_collection(settings.chroma_collection)
        indexed_count = collection.count()
        
        return IngestResponse(
            message=f"Ingesta completada exitosamente. {indexed_count} chunks indexados.",
            documents_indexed=indexed_count,
            collection_name=settings.chroma_collection,
        )
    except Exception as e:
        LOGGER.error("Error durante la ingesta: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error durante la ingesta: {str(e)}")

