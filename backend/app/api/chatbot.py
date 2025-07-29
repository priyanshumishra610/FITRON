"""
FITRON AI Coach Chatbot API
FastAPI router for chat endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import logging

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import get_chat_service, ChatService
from app.services.ollama_client import get_ollama_client, OllamaClient
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Create router
router = APIRouter()

@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_with_ai_coach(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
) -> ChatResponse:
    """
    Chat with FITRON AI Coach
    
    This endpoint allows users to interact with the AI Coach for:
    - Workout advice and form guidance
    - Injury prevention and risk assessment
    - Goal progress tracking
    - Plan adjustments for travel, injuries, etc.
    - Video upload requests for form analysis
    
    **Features:**
    - Context-aware conversations (remembers last 5 messages)
    - Automatic injury risk detection and escalation
    - Goal progress tracking (e.g., "Salman Khan arms")
    - Plan adaptation for various situations
    - Anonymous and logged-in user support
    
    Args:
        request: ChatRequest with message and optional user_id
        
    Returns:
        ChatResponse with AI reply and metadata
        
    Raises:
        400: Invalid request data
        500: Internal server error
    """
    try:
        logger.info(f"Processing chat request for user: {request.user_id or 'anonymous'}")
        
        # Process the chat message
        response = await chat_service.process_chat_message(request)
        
        logger.info(f"Chat response generated successfully. Context length: {response.context_length}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message. Please try again."
        )

@router.get("/health", status_code=status.HTTP_200_OK)
async def chatbot_health_check(
    ollama_client: OllamaClient = Depends(get_ollama_client)
) -> Dict[str, Any]:
    """
    Health check for chatbot service
    
    Checks:
    - Ollama connection
    - Model availability
    - Database connectivity
    
    Returns:
        Health status and service information
    """
    try:
        # Check Ollama connection
        model_available = await ollama_client.check_model_availability()
        available_models = await ollama_client.list_available_models()
        
        health_status = {
            "status": "healthy" if model_available else "degraded",
            "service": "FITRON AI Coach Chatbot",
            "ollama_connected": model_available,
            "current_model": ollama_client.model_name,
            "available_models": available_models,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        if not model_available:
            health_status["warning"] = f"Model '{ollama_client.model_name}' not available. Available models: {available_models}"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "FITRON AI Coach Chatbot",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

@router.get("/history/{user_id}", status_code=status.HTTP_200_OK)
async def get_chat_history(
    user_id: str,
    limit: int = 50,
    chat_service: ChatService = Depends(get_chat_service)
) -> Dict[str, Any]:
    """
    Get user's chat history
    
    Args:
        user_id: User identifier
        limit: Maximum number of sessions to return (default: 50)
        
    Returns:
        User's chat history with sessions and messages
    """
    try:
        history = await chat_service.get_user_chat_history(user_id, limit)
        
        return {
            "user_id": user_id,
            "sessions_count": len(history),
            "sessions": history,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error getting chat history for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat history"
        )

@router.delete("/history/{user_id}", status_code=status.HTTP_200_OK)
async def clear_chat_history(
    user_id: str,
    chat_service: ChatService = Depends(get_chat_service)
) -> Dict[str, Any]:
    """
    Clear user's chat history
    
    Args:
        user_id: User identifier
        
    Returns:
        Confirmation of history deletion
    """
    try:
        success = await chat_service.clear_user_chat_history(user_id)
        
        if success:
            return {
                "message": "Chat history cleared successfully",
                "user_id": user_id,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No chat history found for this user"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing chat history for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear chat history"
        )

@router.get("/models", status_code=status.HTTP_200_OK)
async def list_available_models(
    ollama_client: OllamaClient = Depends(get_ollama_client)
) -> Dict[str, Any]:
    """
    List available Ollama models
    
    Returns:
        List of available models and current model
    """
    try:
        models = await ollama_client.list_available_models()
        
        return {
            "available_models": models,
            "current_model": ollama_client.model_name,
            "model_available": ollama_client.model_name in models,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve available models"
        )

@router.post("/test", status_code=status.HTTP_200_OK)
async def test_chat_endpoint() -> Dict[str, Any]:
    """
    Test endpoint for chatbot functionality
    
    Returns:
        Test response with sample data
    """
    return {
        "message": "FITRON AI Coach is ready! 🏋️‍♂️",
        "features": [
            "Real-time chat with AI Coach",
            "Injury risk detection and escalation",
            "Goal progress tracking",
            "Plan adjustments for travel/injury",
            "Video upload requests",
            "Context-aware conversations"
        ],
        "example_request": {
            "message": "I have shoulder pain during bench press",
            "user_id": "user_123"
        },
        "status": "operational"
    } 