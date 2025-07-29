"""
FITRON AI Coach Chat Service
Core service for handling chat interactions, context management, and intelligent responses
"""

import re
import uuid
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

from app.models.chat import (
    ChatRequest, ChatResponse, ChatMessage, ChatSession, 
    MessageRole, InjuryRiskLevel, GoalProgress, PlanAdjustment
)
from app.services.ollama_client import get_ollama_client
from app.core.db import get_mongo_db
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class ChatService:
    """Main chat service for FITRON AI Coach"""
    
    def __init__(self):
        """Initialize chat service"""
        # Injury keywords for risk detection
        self.injury_keywords = {
            "critical": ["tear", "rupture", "broken", "fracture", "dislocation", "severe pain", "can't move"],
            "high": ["sharp pain", "stabbing", "burning", "numbness", "tingling", "swelling", "bruising"],
            "medium": ["pain", "hurt", "sore", "ache", "stiff", "tight", "uncomfortable", "discomfort"],
            "low": ["tired", "fatigue", "weak", "slight", "minor", "mild"]
        }
        
        # Video upload triggers
        self.video_triggers = [
            "upload video", "send video", "record", "form check", "check form",
            "video analysis", "pose analysis", "form analysis"
        ]
        
        # Goal progress triggers
        self.goal_triggers = [
            "progress", "goal", "closer to", "how am i doing", "am i making progress",
            "salman khan", "celebrity", "physique", "arms", "shoulders", "chest"
        ]
        
        # Plan adjustment triggers
        self.plan_adjustment_triggers = {
            "travel": ["travel", "trip", "vacation", "hotel", "away", "business trip"],
            "injury": ["injury", "hurt", "pain", "recovery", "rest", "heal"],
            "no_gym": ["no gym", "home workout", "no equipment", "limited equipment"],
            "time_constraint": ["busy", "short time", "quick workout", "time limit"],
            "weather": ["rain", "weather", "outdoor", "indoor"]
        }

    async def process_chat_message(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat message and generate response
        
        Args:
            request: Chat request with message and optional user_id
            
        Returns:
            ChatResponse with AI reply and metadata
        """
        try:
            # Get MongoDB connection
            db = await get_mongo_db()
            
            # Get or create session
            session = await self._get_or_create_session(db, request.user_id)
            
            # Analyze message for special triggers
            analysis = self._analyze_message(request.message)
            
            # Get conversation context
            context_messages = await self._get_context_messages(session)
            
            # Generate AI response
            ollama_client = await get_ollama_client()
            ai_response = await ollama_client.generate_response(
                prompt=request.message,
                context_messages=context_messages
            )
            
            # Create response message
            response_message = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=ai_response,
                timestamp=datetime.utcnow()
            )
            
            # Update session with new messages
            await self._update_session(db, session, request.message, response_message, analysis)
            
            # Build response
            response = ChatResponse(
                reply=ai_response,
                user_id=request.user_id,
                context_length=len(session.messages) + 2,  # +2 for current exchange
                injury_risk=analysis.get("injury_risk"),
                escalation_suggested=analysis.get("escalation_suggested", False),
                video_upload_requested=analysis.get("video_upload_requested", False),
                plan_adjustment=analysis.get("plan_adjustment"),
                goal_progress=analysis.get("goal_progress"),
                timestamp=datetime.utcnow()
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            return ChatResponse(
                reply="I'm experiencing some technical difficulties. Please try again in a moment.",
                user_id=request.user_id,
                context_length=0,
                timestamp=datetime.utcnow()
            )

    def _analyze_message(self, message: str) -> Dict[str, Any]:
        """
        Analyze message for special triggers and patterns
        
        Args:
            message: User's message
            
        Returns:
            Analysis results with detected patterns
        """
        message_lower = message.lower()
        analysis = {
            "injury_risk": None,
            "escalation_suggested": False,
            "video_upload_requested": False,
            "plan_adjustment": None,
            "goal_progress": None
        }
        
        # Check for injury keywords
        for risk_level, keywords in self.injury_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                analysis["injury_risk"] = InjuryRiskLevel(risk_level)
                if risk_level in ["critical", "high"]:
                    analysis["escalation_suggested"] = True
                break
        
        # Check for video upload requests
        if any(trigger in message_lower for trigger in self.video_triggers):
            analysis["video_upload_requested"] = True
        
        # Check for goal progress requests
        if any(trigger in message_lower for trigger in self.goal_triggers):
            analysis["goal_progress"] = self._get_dummy_goal_progress()
        
        # Check for plan adjustment requests
        for adjustment_type, triggers in self.plan_adjustment_triggers.items():
            if any(trigger in message_lower for trigger in triggers):
                analysis["plan_adjustment"] = adjustment_type
                break
        
        return analysis

    def _get_dummy_goal_progress(self) -> Dict[str, Any]:
        """Get dummy goal progress data (replace with real data later)"""
        return {
            "goal_name": "Salman Khan Arms",
            "current_progress": 65.5,
            "target_date": "2024-06-01",
            "metrics": {
                "arm_circumference": {"current": 15.2, "target": 16.5, "unit": "inches"},
                "bench_press": {"current": 185, "target": 225, "unit": "lbs"},
                "workout_consistency": {"current": 85, "target": 90, "unit": "%"}
            },
            "next_milestone": "Reach 16-inch arm circumference",
            "estimated_completion": "3 months"
        }

    async def _get_or_create_session(self, db, user_id: Optional[str]) -> ChatSession:
        """Get existing session or create new one"""
        collection = db.chat_sessions
        
        if user_id:
            # Try to find existing session for user
            session_data = await collection.find_one(
                {"user_id": user_id},
                sort=[("updated_at", -1)]
            )
            
            if session_data:
                # Update existing session
                session_data["updated_at"] = datetime.utcnow()
                await collection.update_one(
                    {"_id": session_data["_id"]},
                    {"$set": {"updated_at": session_data["updated_at"]}}
                )
                return ChatSession(**session_data)
        
        # Create new session
        session = ChatSession(
            user_id=user_id,
            session_id=str(uuid.uuid4()),
            messages=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save to database
        await collection.insert_one(session.dict())
        return session

    async def _get_context_messages(self, session: ChatSession) -> List[Dict[str, str]]:
        """Get last 5 messages for context"""
        context_messages = []
        
        # Get last 5 messages (excluding system messages)
        recent_messages = [msg for msg in session.messages if msg.role != MessageRole.SYSTEM][-5:]
        
        for message in recent_messages:
            context_messages.append({
                "role": message.role.value,
                "content": message.content
            })
        
        return context_messages

    async def _update_session(
        self, 
        db, 
        session: ChatSession, 
        user_message: str, 
        assistant_message: ChatMessage,
        analysis: Dict[str, Any]
    ):
        """Update session with new messages and analysis"""
        collection = db.chat_sessions
        
        # Create user message
        user_msg = ChatMessage(
            role=MessageRole.USER,
            content=user_message,
            timestamp=datetime.utcnow()
        )
        
        # Add messages to session
        session.messages.extend([user_msg, assistant_message])
        
        # Update analysis data
        if analysis.get("injury_risk"):
            # Add injury keywords to flags
            message_lower = user_message.lower()
            for risk_level, keywords in self.injury_keywords.items():
                for keyword in keywords:
                    if keyword in message_lower and keyword not in session.injury_flags:
                        session.injury_flags.append(keyword)
        
        if analysis.get("escalation_suggested"):
            session.escalation_count += 1
        
        if analysis.get("goal_progress"):
            # Extract goal mentions
            goal_keywords = ["salman khan", "arms", "shoulders", "chest", "physique"]
            message_lower = user_message.lower()
            for keyword in goal_keywords:
                if keyword in message_lower and keyword not in session.goal_mentions:
                    session.goal_mentions.append(keyword)
        
        if analysis.get("plan_adjustment"):
            if analysis["plan_adjustment"] not in session.plan_adjustments:
                session.plan_adjustments.append(analysis["plan_adjustment"])
        
        # Update timestamp
        session.updated_at = datetime.utcnow()
        
        # Save to database
        await collection.update_one(
            {"_id": session.dict().get("_id")},
            {"$set": session.dict()}
        )

    async def get_user_chat_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's chat history"""
        try:
            db = await get_mongo_db()
            collection = db.chat_sessions
            
            # Get all sessions for user
            sessions = await collection.find(
                {"user_id": user_id},
                sort=[("updated_at", -1)]
            ).limit(limit).to_list(length=limit)
            
            return sessions
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return []

    async def clear_user_chat_history(self, user_id: str) -> bool:
        """Clear user's chat history"""
        try:
            db = await get_mongo_db()
            collection = db.chat_sessions
            
            result = await collection.delete_many({"user_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error clearing chat history: {e}")
            return False

# Global chat service instance
chat_service = ChatService()

async def get_chat_service() -> ChatService:
    """Get the global chat service instance"""
    return chat_service 