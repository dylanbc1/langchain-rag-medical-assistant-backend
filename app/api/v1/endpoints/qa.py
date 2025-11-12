"""Question-answering endpoint."""
from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_retriever_dep, get_settings
from app.core.config import Settings
from app.rag.llm_chain import PromptType

router = APIRouter()


class QuestionRequest(BaseModel):
    """Request model for QA."""
    question: str  # the user's question
    use_memory: bool = True  # whether to use conversational memory
    prompt_type: str = PromptType.DEFAULT.value  # prompt engineering technique to use
    conversation_id: Optional[str] = None  # for future session management


class SourceDocument(BaseModel):
    """Source document metadata."""
    source: str  # source file name
    page_start: Optional[int] = None  # starting page number
    page_end: Optional[int] = None  # ending page number


class QuestionResponse(BaseModel):
    """Response model for QA."""
    answer: str  # the generated answer
    sources: list[SourceDocument]  # list of source documents used
    conversation_id: Optional[str] = None  # conversation identifier


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    retriever: Annotated[Any, Depends(get_retriever_dep)],
    settings: Annotated[Settings, Depends(get_settings)] = None,
):
    """
    Ask a question to the medical assistant.
    
    Args:
        request: Question request with question text and optional memory flag
        retriever: Retriever dependency (injected by FastAPI)
        settings: Application settings
    
    Returns:
        Answer with source documents
    """
    try:
        # validate and convert prompt_type string to PromptType enum
        try:
            prompt_type = PromptType(request.prompt_type)
        except ValueError:
            # if invalid prompt type, default to DEFAULT
            prompt_type = PromptType.DEFAULT
        
        # build the appropriate QA chain based on memory preference
        # if use_memory is true, use conversational chain that maintains context
        if request.use_memory:
            from app.rag.llm_chain import build_conversational_chain
            qa_chain = build_conversational_chain(
                retriever=retriever,
                settings=settings,
                verbose=False,
                prompt_type=prompt_type,
            )
            # ConversationalRetrievalChain expects "question" as input key
            chain_input = {"question": request.question}
        else:
            # if use_memory is false, use simple retrieval chain without memory
            from app.rag.llm_chain import build_retrieval_qa_chain
            qa_chain = build_retrieval_qa_chain(
                retriever=retriever,
                settings=settings,
                prompt_type=prompt_type,
            )
            # RetrievalQA expects "query" as input key
            chain_input = {"query": request.question}
        
        # invoke the chain with the question
        # this triggers: retrieval -> prompt construction -> LLM generation
        response = qa_chain.invoke(chain_input)
        
        # extract the answer from the chain response
        # different chain types may use different output keys
        answer = None
        if isinstance(response, dict):
            # try to get the output_key from the chain if available
            output_key = getattr(qa_chain, "output_key", None)
            if output_key and output_key in response:
                answer = response[output_key]
            
            # fallback to common keys if output_key not found
            if not answer:
                answer = response.get("answer") or response.get("result") or response.get("output")
        
        # default message if no answer was found
        if not answer:
            answer = "No se obtuvo respuesta."
        
        # extract source documents from the response
        # these are the documents that were retrieved and used to generate the answer
        source_documents = response.get("source_documents", []) if isinstance(response, dict) else []
        sources = []
        for doc in source_documents:
            metadata = doc.metadata or {}
            sources.append(
                SourceDocument(
                    source=metadata.get("source", "desconocido"),
                    page_start=metadata.get("page_start"),
                    page_end=metadata.get("page_end"),
                )
            )
        
        return QuestionResponse(
            answer=answer,
            sources=sources,
            conversation_id=request.conversation_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

