"""Text splitting and cleaning utilities."""
import re
from typing import List, Optional

# try to import from langchain_text_splitters first (newer versions), fallback to langchain
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.core.constants import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    HEADER_PATTERNS,
    MIN_PAGE_CHARACTERS,
)
from app.core.logger import get_logger

LOGGER = get_logger(__name__)


def normalize_text(text: str) -> str:
    """Normalize whitespace and remove excessive newlines."""
    # convert Windows line endings to Unix
    text = re.sub(r"\r\n?", "\n", text)
    # collapse multiple spaces/tabs into single space
    text = re.sub(r"[ \t]+", " ", text)
    # limit consecutive newlines to maximum of 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def remove_repeated_headers(text: str, header_patterns: Optional[List[str]] = None) -> str:
    """Remove repeated headers based on provided regex patterns."""
    if not header_patterns:
        return text

    # filter out lines that match any of the header patterns
    cleaned_lines = []
    for line in text.splitlines():
        # check if line matches any header pattern (case-insensitive)
        if any(re.fullmatch(pattern, line.strip(), flags=re.IGNORECASE) for pattern in header_patterns):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def _build_metadata(source: str, pages: Optional[List[int]]) -> dict:
    """Build metadata dictionary with page range."""
    metadata: dict[str, object] = {"source": source}
    # add page range if pages are provided
    if pages:
        metadata["page_start"] = min(pages)
        metadata["page_end"] = max(pages)
    return metadata


def clean_documents(
    documents: List[Document],
    min_characters: int = MIN_PAGE_CHARACTERS,
    header_patterns: Optional[List[str]] = None,
) -> List[Document]:
    """Clean and combine short documents."""
    # use default header patterns if not provided
    if header_patterns is None:
        header_patterns = HEADER_PATTERNS
    
    # group documents by source file
    grouped: dict[str, List[Document]] = {}
    for doc in documents:
        source = doc.metadata.get("source", "unknown")
        grouped.setdefault(source, []).append(doc)

    cleaned_docs: List[Document] = []
    # process each source file separately
    for source, docs in grouped.items():
        # sort documents by page number to maintain order
        docs.sort(key=lambda d: d.metadata.get("page", 0))
        # buffer for accumulating short pages
        buffer_text = ""
        buffer_pages: List[int] = []

        for doc in docs:
            # normalize text and remove repeated headers
            text = normalize_text(doc.page_content)
            text = remove_repeated_headers(text, header_patterns)
            if not text:
                continue

            page_number = doc.metadata.get("page")

            # if page is too short, add to buffer to combine with next page
            if len(text) < min_characters:
                buffer_text = f"{buffer_text}\n\n{text}".strip() if buffer_text else text
                if isinstance(page_number, int):
                    buffer_pages.append(page_number)
                continue

            # if we have buffered text, flush it before processing current page
            if buffer_text:
                cleaned_docs.append(
                    Document(
                        page_content=buffer_text,
                        metadata=_build_metadata(source, buffer_pages),
                    )
                )
                buffer_text = ""
                buffer_pages = []

            # add the current page as a document
            cleaned_docs.append(
                Document(
                    page_content=text,
                    metadata=_build_metadata(source, [page_number] if isinstance(page_number, int) else None),
                )
            )

        # flush any remaining buffered text
        if buffer_text:
            cleaned_docs.append(
                Document(
                    page_content=buffer_text,
                    metadata=_build_metadata(source, buffer_pages),
                )
            )

    return cleaned_docs


def split_documents(
    documents: List[Document],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Document]:
    """Split documents into chunks using RecursiveCharacterTextSplitter."""
    # create splitter with specified chunk size and overlap
    # separators are tried in order: paragraphs, lines, sentences, words, characters
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    # split all documents into chunks
    split_docs = splitter.split_documents(documents)
    return split_docs

