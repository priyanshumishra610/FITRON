"""
FITRON General API Routes
Basic endpoints and system information
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from datetime import datetime

from app.core.config import settings
from app.models.user import User
from app.api.auth import get_current_active_user
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

@router.get("/info")
async def get_system_info():
    """Get FITRON system information"""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "active",
        "features": [
            "real_time_pose_tracking",
            "ego_lifting_detection",
            "celebrity_physique_mapping",
            "ai_workout_planning",
            "auto_regulation",
            "pro_trainer_escalation"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/stats")
async def get_system_stats():
    """Get system statistics"""
    # In a real implementation, these would be actual database queries
    return {
        "total_users": 0,  # Would be actual count
        "total_reps_tracked": 0,  # Would be actual count
        "active_sessions": 0,  # Would be actual count
        "goals_created": 0,  # Would be actual count
        "system_uptime": "0 days",  # Would be actual uptime
        "last_updated": datetime.utcnow().isoformat()
    }

@router.get("/features")
async def get_available_features():
    """Get available features based on subscription tier"""
    return {
        "free": [
            "basic_pose_tracking",
            "rep_counting",
            "form_analysis",
            "basic_workout_plans",
            "goal_setting"
        ],
        "pro": [
            "advanced_pose_tracking",
            "ego_lifting_detection",
            "celebrity_physique_mapping",
            "ai_workout_planning",
            "auto_regulation",
            "human_trainer_escalation",
            "rep_heatmaps",
            "advanced_analytics"
        ],
        "elite": [
            "all_pro_features",
            "personal_trainer_assignment",
            "custom_workout_programs",
            "priority_support",
            "exclusive_content"
        ]
    }

@router.get("/subscription-info")
async def get_subscription_info(current_user: User = Depends(get_current_active_user)):
    """Get user's subscription information"""
    return {
        "current_tier": current_user.subscription_tier,
        "is_pro_user": current_user.is_pro_user,
        "subscription_expires": current_user.subscription_expires.isoformat() if current_user.subscription_expires else None,
        "features_available": _get_user_features(current_user.subscription_tier),
        "upgrade_options": _get_upgrade_options(current_user.subscription_tier)
    }

@router.post("/contact-support")
async def contact_support(
    message: str,
    category: str = "general",
    current_user: User = Depends(get_current_active_user)
):
    """Contact support team"""
    try:
        # In a real implementation, this would send to a support system
        support_ticket = {
            "user_id": current_user.id,
            "user_email": current_user.email,
            "category": category,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "open"
        }
        
        logger.info(f"Support ticket created by user {current_user.id}: {category}")
        
        return {
            "ticket_id": "ticket_123",  # Would be real ticket ID
            "message": "Support ticket created successfully",
            "estimated_response_time": "24 hours",
            "status": "open"
        }
        
    except Exception as e:
        logger.error(f"Contact support error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create support ticket"
        )

@router.get("/maintenance-status")
async def get_maintenance_status():
    """Get system maintenance status"""
    return {
        "is_maintenance_mode": False,
        "scheduled_maintenance": None,
        "last_maintenance": "2024-01-01T00:00:00Z",
        "system_status": "operational",
        "performance_metrics": {
            "response_time_ms": 150,
            "uptime_percentage": 99.9,
            "active_connections": 0  # Would be actual count
        }
    }

def _get_user_features(subscription_tier: str) -> list:
    """Get features available for user's subscription tier"""
    features_map = {
        "free": [
            "basic_pose_tracking",
            "rep_counting",
            "form_analysis",
            "basic_workout_plans",
            "goal_setting"
        ],
        "pro": [
            "advanced_pose_tracking",
            "ego_lifting_detection",
            "celebrity_physique_mapping",
            "ai_workout_planning",
            "auto_regulation",
            "human_trainer_escalation",
            "rep_heatmaps",
            "advanced_analytics"
        ],
        "elite": [
            "all_pro_features",
            "personal_trainer_assignment",
            "custom_workout_programs",
            "priority_support",
            "exclusive_content"
        ]
    }
    
    return features_map.get(subscription_tier, features_map["free"])

def _get_upgrade_options(current_tier: str) -> list:
    """Get available upgrade options for user"""
    if current_tier == "free":
        return [
            {
                "tier": "pro",
                "price": "$19.99/month",
                "features": [
                    "Advanced pose tracking",
                    "Ego-lifting detection",
                    "Celebrity physique mapping",
                    "AI workout planning"
                ]
            },
            {
                "tier": "elite",
                "price": "$49.99/month",
                "features": [
                    "All Pro features",
                    "Personal trainer assignment",
                    "Custom workout programs",
                    "Priority support"
                ]
            }
        ]
    elif current_tier == "pro":
        return [
            {
                "tier": "elite",
                "price": "$49.99/month",
                "features": [
                    "Personal trainer assignment",
                    "Custom workout programs",
                    "Priority support",
                    "Exclusive content"
                ]
            }
        ]
    else:
        return [] 