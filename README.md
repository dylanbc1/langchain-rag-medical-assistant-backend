# RAG Medical Assistant Backend

A FastAPI-based backend for a medical assistant powered by Retrieval-Augmented Generation (RAG) using LangChain, ChromaDB, and Google Gemini. This system enables question-answering over medical guides (MSF and Red Cross) with conversational memory support and multiple prompt engineering techniques.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Design Decisions](#design-decisions)
  - [Document Loader](#document-loader)
  - [Text Splitter](#text-splitter)
  - [Embedding Model](#embedding-model)
  - [Vector Database](#vector-database)
  - [Retrieval Strategy](#retrieval-strategy)
  - [LLM Selection](#llm-selection)
  - [Chain Types](#chain-types)
  - [Prompt Engineering Strategy](#prompt-engineering-strategy)
  - [Memory Management](#memory-management)
- [System Flow](#system-flow)
- [Challenges and Solutions](#challenges-and-solutions)
- [Setup and Installation](#setup-and-installation)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Testing](#testing)
- [Potential Improvements](#potential-improvements)
- [Production Considerations](#production-considerations)

## Overview

This RAG system processes medical PDF documents, converts them into searchable vector embeddings, and uses semantic search to retrieve relevant context for answering medical questions. The system supports multiple prompt engineering techniques and maintains conversational context across requests.

**Key Features:**
- Document ingestion from PDF files
- Semantic search using vector embeddings
- Multiple prompt engineering strategies (default, few-shot, chain-of-thought, structured, direct)
- Conversational memory for multi-turn interactions
- RESTful API with FastAPI
- Docker support for easy deployment

### Cost-Free Implementation

This implementation is designed as a **zero-cost solution** using entirely free and open-source components. The goal was to demonstrate that a high-quality RAG system can be built without paid services while still delivering excellent results.

**Free Components Used:**
- **Embedding Model**: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` (HuggingFace, free)
- **Vector Database**: ChromaDB (open-source, self-hosted, free)
- **LLM**: Google Gemini (free tier with API key)
- **Framework**: LangChain, FastAPI (open-source, free)

**Performance and Quality:**
Despite using free components, this system delivers:
- High-quality semantic search with multilingual support
- Accurate and contextually relevant medical answers
- Consistent response formatting across different prompt types
- Reliable conversational memory for multi-turn interactions
- Fast retrieval and response times

**Trade-offs and Future Improvements:**
While this baseline implementation performs very well, there is significant room for improvement with paid services:
- **Embeddings**: OpenAI embeddings or Cohere could provide better semantic understanding
- **LLM**: GPT-4 or Claude could offer superior reasoning and answer quality
- **Vector Database**: Managed services like Pinecone could provide better scalability and performance

However, this cost-free baseline serves as an excellent starting point that demonstrates the core RAG capabilities and can be incrementally improved with paid services as needed. The architecture is designed to be modular, making it easy to swap components when budget allows.

## Architecture

The system follows a modular architecture with clear separation of concerns. This design enables easy component swapping, testing, and scaling without affecting other parts of the system.

```
┌─────────────┐
│   Client    │ (Postman, Frontend, etc.)
└──────┬──────┘
       │ HTTP Request
       ▼
┌─────────────────────────────────────────────────┐
│           FastAPI Backend                        │
│  ┌──────────────────────────────────────────┐  │
│  │  API Endpoints                           │  │
│  │  - /api/v1/ask (QA)                      │  │
│  │  - /api/v1/ingest (Document Indexing)    │  │
│  │  - /api/v1/health (Health Check)         │  │
│  └──────────────┬─────────────────────────────┘  │
│                 │                                 │
│  ┌──────────────▼─────────────────────────────┐ │
│  │  RAG Pipeline                               │ │
│  │  1. Retriever → Semantic Search             │ │
│  │  2. Prompt Engineering → Context Injection │ │
│  │  3. LLM Chain → Answer Generation           │ │
│  │  4. Memory → Conversation Context          │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────┘
                   │
                   │ HTTP/API Calls
                   ▼
┌─────────────────────────────────────────────────┐
│        ChromaDB (Vector Database)              │
│  - Vector Store                                 │
│  - Collection: "medical_guides"                │
│  - Semantic Search Index                        │
└─────────────────────────────────────────────────┘
```

**Project Structure:**
```
rag-medical-assistant-backend/
├── app/
│   ├── api/
│   │   ├── deps.py              # FastAPI dependency injection
│   │   └── v1/endpoints/
│   │       ├── qa.py            # Question-answering endpoint
│   │       ├── ingest.py        # Document ingestion endpoint
│   │       └── health.py        # Health check endpoint
│   ├── core/
│   │   ├── config.py            # Configuration management
│   │   ├── constants.py         # Global constants
│   │   └── logger.py            # Logging configuration
│   ├── rag/
│   │   ├── loader.py            # PDF document loader
│   │   ├── splitter.py          # Text chunking and cleaning
│   │   ├── embeddings.py        # Embedding model management
│   │   ├── vectorstore.py       # ChromaDB integration
│   │   ├── retriever.py         # Semantic search retriever
│   │   ├── llm_chain.py         # LLM chains and prompts
│   │   └── memory.py            # Conversational memory
│   └── main.py                  # FastAPI application entry point
├── data/
│   ├── pdfs/                    # PDF documents to index
│   └── cache/                   # Temporary cache directory
├── postman/                     # Postman collection for testing
├── docker-compose.yml           # Docker orchestration
├── Dockerfile                   # Backend container definition
└── requirements.txt             # Python dependencies
```

**Modularity and Scalability:**
The architecture is designed with modularity as a core principle, enabling:

- **Component Independence**: Each module (loader, splitter, embeddings, retriever, chain) can be modified or replaced independently
- **Interface-Based Design**: Components communicate through well-defined interfaces (LangChain abstractions)
- **Dependency Injection**: FastAPI's dependency system allows easy swapping of implementations
- **Configuration-Driven**: Behavior controlled via environment variables and parameters
- **Easy Testing**: Isolated components can be unit tested independently
- **Horizontal Scaling**: Stateless design allows multiple backend instances
- **Future-Proof**: New retrieval strategies, chain types, or LLMs can be added without refactoring existing code

## Design Decisions

### Document Loader

**Choice:** LangChain's `PyPDFLoader` from `langchain-community`

**Rationale:**
- PyPDFLoader provides reliable PDF text extraction with page-level metadata
- Integrates seamlessly with LangChain's document abstraction
- Preserves page numbers and source file information for citation
- Handles various PDF formats commonly used in medical documentation

**Implementation Details:**
- Documents are loaded with metadata including source filename and page numbers
- Each page becomes a separate document initially, allowing for precise source tracking
- The loader handles encoding issues and malformed PDFs gracefully

**Alternative Considered:** Direct PDF parsing libraries (PyPDF2, pdfplumber)
- Rejected because LangChain's abstraction provides better integration with the rest of the pipeline

### Text Splitter

**Choice:** `RecursiveCharacterTextSplitter` with custom separators and strategic chunking parameters

**Rationale:**
- RecursiveCharacterTextSplitter intelligently splits text by trying multiple separators in order of preference
- Maintains document structure by prioritizing paragraph breaks, then sentences, then words, then characters
- Handles edge cases gracefully (very long words, no separators) by falling back to character-level splitting
- Better than fixed-size splitting because it respects natural text boundaries
- Preserves semantic meaning by avoiding mid-sentence or mid-word breaks

**Why Not Other Splitters:**
- **CharacterTextSplitter**: Too simplistic, breaks sentences and words arbitrarily
- **TokenTextSplitter**: Requires tokenizer, adds complexity; character-based is sufficient for our use case
- **MarkdownHeaderTextSplitter**: Too specific, our PDFs don't have consistent markdown structure
- **Language-specific splitters**: RecursiveCharacterTextSplitter works well for multilingual content

**Chunking Strategy:**

**1. Chunk Size: 900 characters**
- **Rationale**: Medical documents often contain complete procedures, symptoms, or treatment steps that need to stay together
- **Too small (< 500 chars)**: 
  - Risk of losing context (e.g., splitting a procedure across chunks)
  - More chunks to retrieve and process
  - May break medical terminology or multi-sentence explanations
- **Too large (> 1500 chars)**:
  - Reduced retrieval precision (chunks become less focused)
  - Higher token costs when sending to LLM
  - May include irrelevant information diluting the answer
- **900 characters**: 
  - Typically contains 2-4 sentences or a complete medical instruction
  - Fits well within LLM context windows
  - Provides enough context while maintaining focus
  - Based on empirical testing with medical documents

**2. Chunk Overlap: 150 characters**
- **Rationale**: Ensures continuity when information spans chunk boundaries
- **Why overlap matters**: Medical procedures, symptoms, or treatments often span multiple sentences
- **150 characters**: 
  - Typically 1-2 sentences of overlap
  - Prevents losing critical information at boundaries
  - Example: If a procedure step ends at chunk boundary, overlap ensures the next step is included
- **Too little overlap (< 50 chars)**: Risk of losing context at boundaries
- **Too much overlap (> 300 chars)**: Redundant information, increased storage and processing costs

**3. Separator Hierarchy: `["\n\n", "\n", ".", " ", ""]`**
- **Order matters**: Splitter tries each separator in order until it finds one that works
- **`\n\n` (double newline)**: Paragraph breaks - highest priority, preserves document structure
- **`\n` (single newline)**: Line breaks - maintains list formatting and section breaks
- **`.` (period)**: Sentence boundaries - ensures complete sentences in chunks
- **` ` (space)**: Word boundaries - prevents breaking words
- **`""` (empty)**: Character-level fallback - handles edge cases (very long words, no spaces)
- **Medical document considerations**: 
  - Medical guides often use line breaks for lists and procedures
  - Preserving paragraph structure helps maintain logical flow
  - Sentence-level splitting ensures medical instructions remain complete

**4. Minimum Page Characters: 400 characters**
- **Rationale**: Prevents overly small chunks that lack context
- **Implementation**: Pages with fewer than 400 characters are combined with adjacent pages
- **Why this matters**: Short pages (headers, footers, title pages) don't provide useful context alone
- **Combining strategy**: Buffers short pages until reaching minimum threshold or encountering a long page

**Text Cleaning Pipeline:**

1. **Normalization** (`normalize_text`):
   - Converts Windows line endings (`\r\n`) to Unix (`\n`)
   - Collapses multiple spaces/tabs into single space
   - Limits consecutive newlines to maximum of 2
   - Ensures consistent formatting for splitting

2. **Header Removal** (`remove_repeated_headers`):
   - Removes repeated document headers using regex patterns
   - Patterns: `^GUÍA.*`, `^Manual.*Cruz Roja.*`, `^Referencia Rápida.*`
   - Prevents headers from appearing in every chunk
   - Case-insensitive matching

3. **Short Page Combination** (`clean_documents`):
   - Groups documents by source file
   - Sorts by page number to maintain order
   - Combines pages below minimum character threshold
   - Preserves page range metadata for citation

**Impact on System Performance:**

- **Retrieval Quality**: 
  - Well-sized chunks (900 chars) improve semantic search accuracy
  - Overlap ensures no information loss at boundaries
  - Proper splitting maintains medical terminology integrity

- **LLM Processing**:
  - Chunk size fits comfortably in context windows
  - Overlap provides redundancy that helps LLM understand context
  - Clean text reduces noise and improves answer quality

- **Storage and Costs**:
  - 900-character chunks result in manageable number of vectors
  - Overlap increases storage by ~17% (150/900) but significantly improves quality
  - Clean text reduces embedding noise and improves search precision

**Configuration:**
All chunking parameters are configurable via environment variables:
- `CHUNK_SIZE`: Default 900 characters
- `CHUNK_OVERLAP`: Default 150 characters  
- `MIN_PAGE_CHARACTERS`: Default 400 characters

**Empirical Testing:**
These values were chosen after testing with actual medical documents:
- Tested chunk sizes: 500, 700, 900, 1200, 1500 characters
- Tested overlaps: 0, 50, 100, 150, 200, 300 characters
- Evaluated based on: retrieval precision, answer quality, context preservation
- Final values (900/150) provided best balance for medical content

**Alternative Strategies Considered:**
- **Semantic chunking**: Split based on semantic similarity (requires additional processing)
- **Fixed token count**: Use token-based splitting (adds tokenizer dependency)
- **Sentence-based**: Split only at sentence boundaries (too rigid, may create very uneven chunks)
- **Paragraph-based**: Split only at paragraphs (too large for medical documents with long paragraphs)

**Current approach (RecursiveCharacterTextSplitter with 900/150) provides the best balance of simplicity, performance, and quality for medical document RAG.**

### Embedding Model

**Choice:** `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`

**Rationale:**
- Multilingual support is essential for Spanish medical documents
- MPNet architecture provides high-quality semantic representations
- Sentence-transformers library offers efficient inference
- Model size (420MB) balances quality and performance
- Strong performance on semantic similarity tasks

**Implementation:**
- Model is cached globally to avoid reloading on every request
- Uses dynamic import to support different LangChain versions
- Fallback mechanism: tries `langchain-huggingface` first, then `langchain-community`
- Embeddings are generated once during ingestion and stored in ChromaDB

**Alternative Considered:** OpenAI embeddings, Cohere embeddings
- Rejected due to cost concerns and the goal of maintaining a zero-cost implementation
- Multilingual model requirement made sentence-transformers a better fit
- OpenAI/Cohere embeddings would provide better quality but add ongoing costs
- This free baseline performs well and can be upgraded when budget allows

**Technical Details:**
- Embedding dimension: 768
- Model loaded via HuggingFace transformers
- Cached in memory for performance (reloaded only on app restart)

### Vector Database

**Choice:** ChromaDB

**Rationale:**
- Open-source and self-hostable (no vendor lock-in)
- Simple HTTP API for easy integration
- Efficient similarity search with good performance
- Supports metadata filtering for advanced queries
- Lightweight and easy to deploy with Docker
- Active development and community support

**Configuration:**
- HTTP client mode for separation of concerns
- Collection-based organization for different document sets
- Metadata storage for source tracking and filtering
- Persistent storage for production deployments

**Alternative Considered:** FAISS, Pinecone, Weaviate
- FAISS: Rejected because it's in-memory only and requires manual persistence
- Pinecone: Rejected due to cost (paid service) and vendor dependency, though it offers excellent managed infrastructure
- Weaviate: Considered but ChromaDB's simplicity and zero-cost self-hosting won out
- **Decision**: ChromaDB provides a solid free baseline that can be upgraded to managed services like Pinecone if needed

**Why Not FAISS:**
- FAISS is primarily in-memory, requiring custom persistence logic
- ChromaDB provides built-in persistence and HTTP API
- ChromaDB's metadata support is more robust for production use
- Easier to scale horizontally with ChromaDB's server mode

### Retrieval Strategy

**Choice:** Maximum Marginal Relevance (MMR) with configurable search types

**Rationale:**
- MMR balances relevance and diversity in retrieved documents
- Prevents redundant results that are too similar to each other
- Improves answer quality by providing diverse perspectives
- Better coverage of the document corpus compared to pure similarity search

**Implementation:**
- Default search type: `"mmr"` (Maximum Marginal Relevance)
- Retrieves top-k documents (default: 12) from a larger pool (fetch_k: 20)
- Lambda multiplier (0.5) balances relevance (1.0) and diversity (0.0)
- Configurable via `search_type` parameter in `get_retriever()`

**Alternative Search Types Supported:**
- `"similarity"`: Pure similarity search (fastest, may return redundant results)
- `"similarity_score_threshold"`: Similarity with minimum score threshold
- All types can be used by modifying `search_type` parameter

**Modularity:**
The retrieval strategy is isolated in `app/rag/retriever.py`, making it easy to:
- Switch between MMR, similarity, or threshold-based search
- Implement custom retrieval logic (e.g., hybrid search with BM25)
- Add ensemble retrievers combining multiple strategies
- Integrate different retriever types (e.g., WikipediaRetriever, BM25Retriever)
- Change retrieval parameters without affecting other components

**Future Improvements:**
- Hybrid search combining semantic (vector) and keyword (BM25) search
- Ensemble retriever using multiple retrieval strategies
- Re-ranking of retrieved documents using cross-encoders
- Query expansion and rewriting for better retrieval

### LLM Selection

**Choice:** Google Gemini (gemini-2.0-flash)

**Rationale:**
- Strong multilingual capabilities, especially for Spanish
- Competitive pricing compared to GPT-4
- Good balance between speed and quality
- Reliable API with good documentation
- Supports structured outputs and function calling

**Configuration:**
- Temperature: 0.2 (low for more deterministic, factual responses)
- Model name configurable via `LLM_MODEL_NAME` environment variable
- API key-based authentication

**Alternative Considered:** OpenAI GPT-4, Claude, GPT-3.5
- GPT-4: Superior reasoning and answer quality but significant cost per request
- Claude: Excellent quality but adds ongoing costs
- GPT-3.5: Lower cost than GPT-4 but still requires paid API
- **Decision**: Gemini free tier provides excellent baseline performance at zero cost
- This allows the system to be deployed without budget constraints while still delivering quality results
- Can be upgraded to GPT-4 or Claude for production if higher quality is required and budget allows

### Chain Types

**Choice:** `RetrievalQA` for stateless queries and `ConversationalRetrievalChain` for conversational queries

**Rationale:**
- `RetrievalQA`: Simple, efficient chain for one-off questions without context
- `ConversationalRetrievalChain`: Maintains conversation history for multi-turn interactions
- Both chains use the same underlying retrieval and prompt mechanisms
- Chain selection is automatic based on `use_memory` parameter

**RetrievalQA Chain:**
- **Use case**: Stateless question-answering without conversation context
- **Chain type**: `"stuff"` - all retrieved documents concatenated into prompt
- **Input key**: `"query"` (standard LangChain convention)
- **Advantages**: Fast, simple, no memory overhead
- **Best for**: Single questions, API calls without follow-ups

**ConversationalRetrievalChain:**
- **Use case**: Multi-turn conversations with context awareness
- **Chain type**: Uses `RetrievalQA` internally with memory integration
- **Input key**: `"question"` (conversational convention)
- **Advantages**: Maintains conversation context, handles follow-up questions
- **Best for**: Chat interfaces, interactive sessions, contextual queries

**Chain Type Configuration:**
- Both chains use `chain_type="stuff"` which concatenates all retrieved documents
- Alternative chain types available in LangChain:
  - `"map_reduce"`: Processes documents separately then combines (for very large contexts)
  - `"refine"`: Iteratively refines answer across documents
  - `"map_rerank"`: Ranks documents and uses top results

**Modularity and Extensibility:**
The chain architecture is highly modular, allowing easy changes:

1. **Switching Chain Types:**
   - Modify `chain_type` parameter in `build_retrieval_qa_chain()` or `build_conversational_chain()`
   - Change from `"stuff"` to `"map_reduce"` for handling larger document sets
   - No changes needed in other components

2. **Adding Custom Chains:**
   - Create new chain builder functions following the same pattern
   - Use LangChain's chain composition capabilities
   - Integrate with existing retriever and prompt infrastructure

3. **Alternative Chain Implementations:**
   - **Custom RAG Chain**: Build from scratch using LangChain primitives
   - **Agent-based RAG**: Use LangChain agents for more complex reasoning
   - **Multi-step Chains**: Chain multiple retrieval and generation steps
   - **Self-RAG**: Implement self-reflective RAG with quality checks

4. **Architecture Benefits:**
   - Clear separation: retriever → prompt → chain → LLM
   - Each component can be swapped independently
   - Dependency injection pattern allows easy testing and mocking
   - Configuration-driven approach enables runtime chain selection

**Implementation Location:**
- Chain builders: `app/rag/llm_chain.py`
- Chain selection: `app/api/v1/endpoints/qa.py` (based on `use_memory` flag)
- Retriever integration: `app/rag/retriever.py`

**Example: Switching to Map-Reduce Chain**
```python
# In llm_chain.py, change chain_type parameter:
return RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="map_reduce",  # Changed from "stuff"
    chain_type_kwargs={"prompt": prompt},
    return_source_documents=True,
)
```

### Prompt Engineering Strategy

**Choice:** Multiple prompt types with user selection

**Rationale:**
- Different questions benefit from different prompting approaches
- Allows experimentation and comparison of techniques
- Few-shot examples help guide the model's response format
- Chain-of-thought improves reasoning for complex questions
- Structured prompts ensure consistent output format

**Available Prompt Types:**

1. **Default (`default`)**: Structured prompt with sections (diagnosis, steps, warnings, recommendations)
   - Best for: General medical questions requiring comprehensive answers
   - Provides clear structure and ensures all relevant aspects are covered

2. **Few-Shot (`few_shot`)**: Includes example question-answer pairs
   - Best for: Questions where format consistency is important
   - Helps the model understand expected response style and detail level

3. **Chain-of-Thought (`chain_of_thought`)**: Step-by-step reasoning process
   - Best for: Complex questions requiring analytical thinking
   - Reduces hallucination by forcing the model to show its reasoning

4. **Structured (`structured`)**: Highly structured with strict format requirements
   - Best for: When consistent output format is critical
   - Explicitly handles missing information with "Not specified in context"

5. **Direct (`direct`)**: Concise and direct answers
   - Best for: Simple questions requiring quick answers
   - Minimizes token usage and response time

**System Prompt Design:**
- Emphasizes using ONLY information from context
- Explicitly forbids hallucination or assumptions
- Provides clear instructions for handling missing information
- Maintains medical assistant persona throughout

### Memory Management

**Choice:** Global cached `ConversationBufferMemory` for single conversation

**Rationale:**
- Simple implementation without external dependencies
- Fast access (in-memory)
- Sufficient for single-user or single-conversation scenarios
- Easy to clear and reset

**Implementation:**
- Memory is cached globally and shared across all requests
- All requests with `use_memory=true` share the same conversation history
- Memory persists until app restart or explicit clearing
- Uses LangChain's `ConversationBufferMemory` for compatibility

**Limitations:**
- Not suitable for multi-user scenarios (all users share same memory)
- Memory is lost on app restart
- No conversation isolation between different topics

**Future Improvement:** Implement per-conversation memory with session IDs

## System Flow

### Document Ingestion Flow

1. **Load PDFs** (`loader.py`)
   - Scans `data/pdfs/` directory for PDF files
   - Uses PyPDFLoader to extract text with page metadata
   - Returns list of Document objects

2. **Clean Documents** (`splitter.py`)
   - Normalizes whitespace and line endings
   - Removes repeated headers using regex patterns
   - Combines short pages to meet minimum character threshold
   - Groups documents by source file

3. **Split into Chunks** (`splitter.py`)
   - Uses RecursiveCharacterTextSplitter with configured size and overlap
   - Preserves document structure through separator hierarchy
   - Maintains metadata (source, page numbers)

4. **Generate Embeddings** (`embeddings.py`)
   - Loads multilingual embedding model
   - Converts each chunk to vector representation
   - Embeddings are 768-dimensional vectors

5. **Store in ChromaDB** (`vectorstore.py`)
   - Creates or updates collection in ChromaDB
   - Stores vectors with metadata (source, page range)
   - Indexes for fast similarity search

### Question-Answering Flow

1. **Receive Request** (`qa.py`)
   - Validates request parameters
   - Extracts question, memory preference, and prompt type

2. **Retrieve Relevant Documents** (`retriever.py`)
   - Converts question to embedding using same model
   - Performs semantic search in ChromaDB using MMR (Maximum Marginal Relevance)
   - Returns top-k most relevant chunks (default: 12)
   - MMR balances relevance and diversity to avoid redundant results
   - Search type and parameters are configurable (MMR, similarity, threshold-based)

3. **Build Prompt** (`llm_chain.py`)
   - Selects prompt template based on `prompt_type`
   - Injects retrieved context into prompt
   - Adds system instructions and formatting requirements

4. **Select and Execute Chain** (`llm_chain.py`)
   - Chooses chain type based on `use_memory` flag:
     - `RetrievalQA` for stateless queries (no memory)
     - `ConversationalRetrievalChain` for conversational queries (with memory)
   - Chain type `"stuff"` concatenates all retrieved documents
   - Sends prompt to Gemini LLM
   - LLM processes context and generates answer
   - If memory is enabled, conversation history is included in context

5. **Return Response** (`qa.py`)
   - Extracts answer from LLM response
   - Includes source documents for citation
   - Returns structured JSON response

### Memory Flow (when enabled)

1. **First Request**
   - Creates new ConversationBufferMemory instance
   - Caches globally for reuse

2. **Subsequent Requests**
   - Retrieves cached memory instance
   - Adds previous Q&A pairs to context
   - LLM can reference previous conversation

3. **Memory Structure**
   - Stores human messages (questions)
   - Stores AI messages (answers)
   - Maintains chronological order

## Challenges and Solutions

### Challenge 1: Embedding Model Compatibility

**Problem:** LangChain's embedding classes moved between packages in different versions, causing import errors.

**Solution:** Implemented dynamic import with fallback mechanism:
- Tries `langchain-huggingface` first (recommended)
- Falls back to `langchain-community.embeddings` if not available
- Provides clear error message if neither is installed

**Code Location:** `app/rag/embeddings.py`

### Challenge 2: ChromaDB Collection Not Found

**Problem:** Application would crash if ChromaDB collection didn't exist, requiring manual setup.

**Solution:** 
- Added validation in `load_vectorstore()` to check collection existence
- Provides clear error message directing user to run `/ingest` endpoint
- Handles both missing collection and empty collection cases

**Code Location:** `app/rag/vectorstore.py`

### Challenge 3: Memory Not Persisting Across Requests

**Problem:** Initial implementation created new memory instance for each request, losing conversation context.

**Solution:** 
- Implemented global cache for memory (`_cached_memory`)
- `get_memory()` returns same instance across requests
- Memory persists until app restart or explicit clearing

**Code Location:** `app/rag/memory.py`

### Challenge 4: Metadata Compatibility with ChromaDB

**Problem:** ChromaDB only supports simple metadata types (str, int, float, bool, None), but LangChain documents may have complex metadata.

**Solution:**
- Added metadata filtering before storing in ChromaDB
- Uses LangChain's `filter_complex_metadata` utility if available
- Falls back to manual filtering for compatibility

**Code Location:** `app/api/v1/endpoints/ingest.py`

### Challenge 5: Prompt Type Selection

**Problem:** Need to support multiple prompt engineering techniques without code duplication.

**Solution:**
- Created `PromptType` enum for type safety
- Implemented template mapping in `get_prompt()`
- User selects prompt type via API parameter
- Easy to add new prompt types in the future

**Code Location:** `app/rag/llm_chain.py`

### Challenge 6: Expensive Resource Loading

**Problem:** Embedding model and vectorstore loading takes 30-60 seconds, causing slow first request.

**Solution:**
- Pre-load resources on application startup
- Cache embedding model globally
- Cache vectorstore and retriever in dependency injection
- Graceful fallback: resources load on-demand if startup fails

**Code Location:** `app/main.py`, `app/api/deps.py`

## Setup and Installation

### Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose (for ChromaDB)
- Google Gemini API key

### Step 1: Clone and Navigate

```bash
cd rag-medical-assistant-backend
```

### Step 2: Environment Configuration

Create a `.env` file in the project root:

```bash
# LLM Configuration
LLM_API_KEY=your_gemini_api_key_here
LLM_MODEL_NAME=gemini-2.0-flash

# ChromaDB Configuration
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_SSL=false
CHROMA_COLLECTION=medical_guides

# Optional: Chunking Parameters
CHUNK_SIZE=900
CHUNK_OVERLAP=150
MIN_PAGE_CHARACTERS=400
```

Get your Gemini API key from: https://makersuite.google.com/app/apikey

### Step 3: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Start ChromaDB

**Option A: Using Docker (Recommended)**

```bash
docker run -d --name chroma-medical \
  -p 8000:8000 \
  -v chroma-data:/chroma/chroma \
  ghcr.io/chroma-core/chroma:latest
```

**Option B: Using Docker Compose**

```bash
docker-compose up -d chromadb
```

### Step 5: Add PDF Documents

Place your PDF files in the `data/pdfs/` directory:

```bash
mkdir -p data/pdfs
# Copy your PDF files here
cp /path/to/medical-guides/*.pdf data/pdfs/
```

### Step 6: Ingest Documents

Start the application:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

In another terminal, ingest the documents:

```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

Or use the Postman collection included in `postman/` directory.

### Step 7: Verify Installation

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Test question
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Qué hacer en caso de quemadura?",
    "use_memory": false,
    "prompt_type": "default"
  }'
```

### Docker Deployment (Full Stack)

To run both backend and ChromaDB with Docker Compose:

```bash
docker-compose up -d
```

This starts:
- ChromaDB on port 8001
- Backend API on port 8000

View logs:
```bash
docker-compose logs -f backend
```

Stop services:
```bash
docker-compose down
```

## API Endpoints

### Health Check

```http
GET /api/v1/health
```

Returns service status.

**Response:**
```json
{
  "status": "healthy",
  "service": "rag-medical-assistant-backend"
}
```

### Ingest Documents

```http
POST /api/v1/ingest
Content-Type: application/json

{
  "force": false
}
```

Indexes PDF documents from `data/pdfs/` directory.

**Parameters:**
- `force` (boolean): If `true`, deletes existing collection and re-indexes

**Response:**
```json
{
  "message": "Ingesta completada exitosamente. 2066 chunks indexados.",
  "documents_indexed": 2066,
  "collection_name": "medical_guides"
}
```

### Ask Question

```http
POST /api/v1/ask
Content-Type: application/json

{
  "question": "¿Qué hacer en caso de quemadura?",
  "use_memory": true,
  "prompt_type": "default"
}
```

Asks a medical question and returns an answer with sources.

**Parameters:**
- `question` (string, required): The medical question
- `use_memory` (boolean, default: `true`): Enable conversational memory
- `prompt_type` (string, default: `"default"`): Prompt engineering technique
  - Valid values: `"default"`, `"few_shot"`, `"chain_of_thought"`, `"structured"`, `"direct"`
- `conversation_id` (string, optional): For future session management

**Response:**
```json
{
  "answer": "**Diagnóstico o Evaluación:** Identifica el grado de la quemadura...",
  "sources": [
    {
      "source": "msf_guia_clinica.pdf",
      "page_start": 341,
      "page_end": 345
    }
  ],
  "conversation_id": null
}
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LLM_API_KEY` | Google Gemini API key | - | Yes |
| `LLM_MODEL_NAME` | Gemini model to use | `gemini-2.0-flash` | No |
| `CHROMA_HOST` | ChromaDB server hostname | `localhost` | No |
| `CHROMA_PORT` | ChromaDB server port | `8000` | No |
| `CHROMA_SSL` | Use SSL for ChromaDB | `false` | No |
| `CHROMA_COLLECTION` | Collection name | `medical_guides` | No |
| `CHROMA_API_KEY` | ChromaDB API key (if required) | - | No |
| `CHUNK_SIZE` | Document chunk size | `900` | No |
| `CHUNK_OVERLAP` | Chunk overlap | `150` | No |
| `MIN_PAGE_CHARACTERS` | Minimum characters per page | `400` | No |

### Retrieval Parameters

Edit `app/rag/retriever.py` to adjust:

- `k`: Number of documents to retrieve (default: 12)
- `fetch_k`: Pool size for MMR selection (default: 20)
- `lambda_mult`: Balance between relevance and diversity (default: 0.5)
- `search_type`: Type of search - `"mmr"` (default), `"similarity"`, or `"similarity_score_threshold"`

### Chain Configuration

The system uses two chain types that can be easily modified:

- **RetrievalQA**: Stateless chain for single questions (used when `use_memory=false`)
- **ConversationalRetrievalChain**: Conversational chain with memory (used when `use_memory=true`)

Both chains currently use `chain_type="stuff"` which concatenates all retrieved documents. To use alternative chain types:

- **Map-Reduce**: For very large document sets, modify `chain_type` to `"map_reduce"` in `llm_chain.py`
- **Refine**: For iterative answer refinement, use `chain_type="refine"`
- **Map-Rerank**: For document ranking, use `chain_type="map_rerank"`

The modular architecture allows switching chain types by changing a single parameter without affecting other components.

### Prompt Engineering

Available prompt types are defined in `app/rag/llm_chain.py`. To add a new prompt type:

1. Add new value to `PromptType` enum
2. Create new template constant (e.g., `NEW_TEMPLATE`)
3. Add mapping in `get_prompt()` function

## Testing

### Using cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Ingest documents
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{"force": false}'

# Ask question with default prompt
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Qué hacer en caso de quemadura?",
    "use_memory": false,
    "prompt_type": "default"
  }'

# Ask question with chain-of-thought prompt
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Cuáles son los signos de shock?",
    "use_memory": true,
    "prompt_type": "chain_of_thought"
  }'
```

### Using Postman

Import the collection from `postman/RAG_Medical_Assistant.postman_collection.json` into Postman. The collection includes:

- Health check and ingestion endpoints
- Examples for each prompt type (default, few-shot, chain-of-thought, structured, direct)
- Requests with and without memory
- Conversation flow tests

### Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Potential Improvements

### Short-term Improvements

1. **Per-Conversation Memory**
   - Implement session-based memory using `conversation_id`
   - Store conversations in Redis or database
   - Allow multiple concurrent conversations

2. **Enhanced Error Handling**
   - More specific error messages for different failure modes
   - Retry logic for transient failures
   - Graceful degradation when services are unavailable

3. **Response Streaming**
   - Stream LLM responses for better user experience
   - Implement Server-Sent Events (SSE) endpoint

4. **Caching Layer**
   - Cache frequent questions and answers
   - Reduce LLM API calls and costs
   - Improve response time for common queries

5. **Metadata Filtering**
   - Allow filtering by source document
   - Filter by date or document type
   - Support for document tags/categories

### Medium-term Improvements

1. **Hybrid Search**
   - Combine semantic search with keyword search (BM25)
   - Use ensemble retriever for better recall
   - Implement re-ranking of retrieved documents
   - **Implementation**: The modular retriever design makes this straightforward - add BM25Retriever and combine with existing vector retriever using LangChain's EnsembleRetriever

2. **Query Expansion**
   - Automatically expand medical queries with synonyms
   - Use medical terminology dictionaries
   - Improve retrieval for technical terms

3. **Answer Quality Metrics**
   - Implement answer relevance scoring
   - Track hallucination rates
   - A/B testing framework for prompt comparison

4. **Multi-language Support**
   - Detect query language automatically
   - Support queries in multiple languages
   - Language-specific prompt templates

5. **Document Versioning**
   - Track document updates
   - Re-index only changed documents
   - Maintain version history

### Long-term Improvements

1. **Fine-tuned Embeddings**
   - Fine-tune embedding model on medical corpus
   - Domain-specific embeddings for better retrieval
   - Specialized models for different medical specialties
   - **Cost consideration**: Current free model works well; paid embeddings (OpenAI, Cohere) would improve quality but add costs

2. **Upgrade to Paid Services (When Budget Allows)**
   - **Embeddings**: Migrate to OpenAI embeddings or Cohere for better semantic understanding
   - **LLM**: Upgrade to GPT-4 or Claude for superior reasoning and answer quality
   - **Vector DB**: Consider Pinecone or Weaviate Cloud for managed scalability
   - **Note**: Current free baseline performs excellently; upgrades should be evaluated based on specific quality requirements and budget

3. **Advanced RAG Techniques**
   - Implement parent-child document chunking
   - Use query rewriting and decomposition
   - Implement iterative retrieval refinement

4. **User Feedback Loop**
   - Collect user feedback on answer quality
   - Use feedback to improve retrieval and prompts
   - Implement learning from corrections

5. **Analytics and Monitoring**
   - Track query patterns and popular questions
   - Monitor system performance metrics
   - Alert on errors or performance degradation

6. **Integration with Medical Systems**
   - Connect to electronic health records (EHR)
   - Support for structured medical data
   - Integration with clinical decision support systems

## Production Considerations

### Security

1. **Authentication and Authorization**
   - Implement API key or OAuth2 authentication
   - Role-based access control
   - Rate limiting per user/IP

2. **Data Privacy**
   - Encrypt sensitive data at rest
   - Use HTTPS for all communications
   - Implement data retention policies
   - Comply with healthcare data regulations (HIPAA, GDPR)

3. **Input Validation**
   - Sanitize user inputs
   - Validate prompt types and parameters
   - Prevent injection attacks

### Performance

1. **Scaling**
   - Use load balancer for multiple backend instances
   - Scale ChromaDB horizontally if needed
   - Implement connection pooling

2. **Caching**
   - Cache embedding model and vectorstore connections
   - Implement response caching for common queries
   - Use CDN for static assets

3. **Monitoring**
   - Set up application performance monitoring (APM)
   - Monitor LLM API latency and costs
   - Track vector database performance

### Reliability

1. **Error Handling**
   - Implement circuit breakers for external services
   - Graceful degradation when services fail
   - Comprehensive logging and alerting

2. **Backup and Recovery**
   - Regular backups of ChromaDB collections
   - Document recovery procedures
   - Test disaster recovery scenarios

3. **Deployment**
   - Use container orchestration (Kubernetes)
   - Implement blue-green deployments
   - Automated testing in CI/CD pipeline

### Cost Optimization

**Current Implementation: Zero Cost**
This system is designed to operate at zero cost using free services. However, if upgrading to paid services:

1. **LLM Usage**
   - Monitor token usage and costs
   - Implement response length limits
   - Cache frequent queries to reduce API calls
   - Consider using cheaper models (GPT-3.5) for simple queries and GPT-4 only for complex ones

2. **Infrastructure**
   - Right-size compute resources
   - Use spot instances where possible
   - Optimize Docker image sizes
   - Current self-hosted ChromaDB has no hosting costs; managed services add costs but reduce operational overhead

3. **Baseline vs. Upgraded Costs**
   - **Current (Free)**: $0/month - Gemini free tier, self-hosted ChromaDB, free embeddings
   - **Upgraded (Paid)**: ~$50-500/month depending on usage - GPT-4 API, Pinecone, OpenAI embeddings
   - The free baseline provides excellent value and can be upgraded incrementally based on quality requirements

## Troubleshooting

### Common Issues

**Error: "No se encontró la colección"**
- Solution: Run `/api/v1/ingest` endpoint to index documents

**Error: "LLM_API_KEY no está configurada"**
- Solution: Add `LLM_API_KEY` to your `.env` file

**Error: "Could not connect to ChromaDB"**
- Solution: Ensure ChromaDB is running and accessible at `CHROMA_HOST:CHROMA_PORT`

**Slow first request**
- Solution: This is normal. The embedding model loads on first use. Pre-loading on startup helps.

**Memory not working across requests**
- Solution: Ensure `use_memory=true` in requests. Memory is global and shared across all requests.

### Getting Help

- Check application logs for detailed error messages
- Verify environment variables are set correctly
- Ensure all services (ChromaDB, backend) are running
- Review the architecture documentation for flow understanding

## Contributors

Dylan Bermudez Cardona
