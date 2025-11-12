"""Conversational memory management."""
from typing import Optional

# langchain 0.3.0+ import for conversation buffer memory
from langchain.memory.buffer import ConversationBufferMemory

from app.core.logger import get_logger

LOGGER = get_logger(__name__)

# global cache for conversational memory (single conversation across all requests)
# this allows maintaining conversation context across multiple API calls
_cached_memory: Optional[ConversationBufferMemory] = None


def build_memory(
    memory_key: str = "chat_history",
    return_messages: bool = True,
    k: Optional[int] = None,
) -> ConversationBufferMemory:
    """
    Build a new conversational memory buffer.
    
    Args:
        memory_key: Key for storing chat history in the memory object
        return_messages: Whether to return messages as objects or strings
        k: Optional limit (not implemented in ConversationBufferMemory)
    
    Returns:
        Configured memory instance
    """
    # create a new conversation buffer memory instance
    # this stores the full conversation history in memory
    memory = ConversationBufferMemory(
        memory_key=memory_key,
        return_messages=return_messages,
        output_key="answer",
    )
    
    # warn if k limit is requested (not supported by ConversationBufferMemory)
    if k is not None:
        LOGGER.warning(
            "ConversationBufferMemory no implementa recortes por k=%s. "
            "Considera un buffer window si necesitas limitación.",
            k,
        )
    
    return memory


def get_memory() -> ConversationBufferMemory:
    """
    Get or create the cached conversational memory.
    
    Returns the same memory instance across all requests to maintain
    conversation continuity. This implements a single global conversation.
    
    Returns:
        Cached ConversationBufferMemory instance
    """
    global _cached_memory
    
    # create memory on first call, then reuse the same instance
    # this ensures all requests share the same conversation history
    if _cached_memory is None:
        _cached_memory = build_memory()
    
    return _cached_memory


def clear_memory() -> None:
    """
    Clear the cached conversational memory.
    
    This will reset the conversation history. Useful for starting a new conversation.
    """
    global _cached_memory
    
    # clear the memory if it exists
    if _cached_memory is not None:
        _cached_memory.clear()

