"""
FITRON Ollama Client
Async client for local LLM inference using Ollama
"""

import httpx
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class OllamaClient:
    """Async client for Ollama API"""
    
    def __init__(self, base_url: str = None, model_name: str = None):
        """Initialize Ollama client"""
        self.base_url = base_url or getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model_name = model_name or getattr(settings, 'MODEL_NAME', 'gemma')
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Default system prompt for FITRON AI Coach
        self.system_prompt = """You are FITRON, an AI-powered fitness coach and personal trainer. You are:

1. **Expert Fitness Coach**: Provide safe, effective workout advice and form guidance
2. **Injury Prevention Specialist**: Identify potential injury risks and suggest modifications
3. **Motivational Trainer**: Keep users motivated and on track with their fitness goals
4. **Adaptive Planner**: Adjust workouts for travel, injuries, equipment limitations, etc.
5. **Goal-Oriented**: Help users track progress toward their dream physique goals

**Key Guidelines:**
- Always prioritize safety and proper form
- If injury keywords are detected (pain, hurt, tear, etc.), flag as risky and suggest escalation
- Be encouraging but realistic about progress
- Provide specific, actionable advice
- Ask clarifying questions when needed
- Suggest video uploads for form analysis when appropriate

**Response Style:**
- Friendly, professional, and motivating
- Use emojis sparingly but effectively
- Keep responses concise but comprehensive
- Always end with a clear next step or question

Remember: You're not just an AI - you're their personal trainer, coach, and fitness partner!"""

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def generate_response(
        self, 
        prompt: str, 
        context_messages: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Generate response from Ollama
        
        Args:
            prompt: User's message
            context_messages: Previous conversation context
            temperature: Response creativity (0.0-1.0)
            max_tokens: Maximum response length
            
        Returns:
            Generated response text
        """
        try:
            # Build conversation context
            messages = []
            
            # Add system prompt
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })
            
            # Add context messages if provided
            if context_messages:
                messages.extend(context_messages)
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Prepare request payload
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_k": 40,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            }
            
            # Make request to Ollama
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "I apologize, but I couldn't generate a response.")
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return "I'm having trouble connecting to my training systems. Please try again in a moment."
                
        except httpx.TimeoutException:
            logger.error("Ollama request timed out")
            return "I'm taking a bit longer than usual to respond. Please try again."
        except httpx.RequestError as e:
            logger.error(f"Ollama request error: {e}")
            return "I'm experiencing technical difficulties. Please try again later."
        except Exception as e:
            logger.error(f"Unexpected error in Ollama client: {e}")
            return "I encountered an unexpected error. Please try again."

    async def check_model_availability(self) -> bool:
        """Check if the specified model is available"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(model.get("name") == self.model_name for model in models)
            return False
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False

    async def list_available_models(self) -> List[str]:
        """List available models"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model.get("name") for model in models]
            return []
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

# Global Ollama client instance
ollama_client = OllamaClient()

async def get_ollama_client() -> OllamaClient:
    """Get the global Ollama client instance"""
    return ollama_client 