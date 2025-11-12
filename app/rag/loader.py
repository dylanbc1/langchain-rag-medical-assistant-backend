"""Document loading from PDFs."""
from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from app.core.constants import PDFS_DIR
from app.core.logger import get_logger

LOGGER = get_logger(__name__)


def load_pdf_documents(pdfs_dir: Path = None) -> List[Document]:
    """Load all PDF documents from the specified directory."""
    # use default PDFs directory if not provided
    if pdfs_dir is None:
        pdfs_dir = PDFS_DIR
    
    # create directory if it doesn't exist
    pdfs_dir.mkdir(parents=True, exist_ok=True)
    
    # load all PDF files from the directory
    docs: List[Document] = []
    for pdf_path in pdfs_dir.glob("*.pdf"):
        # use PyPDFLoader to extract text from PDF
        loader = PyPDFLoader(str(pdf_path))
        pdf_docs = loader.load()
        # update metadata to include source file name
        for doc in pdf_docs:
            metadata = doc.metadata.copy()
            metadata["source"] = pdf_path.name
            doc.metadata = metadata
        docs.extend(pdf_docs)
    
    return docs

