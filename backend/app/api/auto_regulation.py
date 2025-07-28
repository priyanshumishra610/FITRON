"""
FITRON Auto-Regulation API Routes
Ego-lifting detection and safety features
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.db import get_db
from app.models.user import User
from app.models.rep_log import RepLog
from app.api.auth import get_current_active_user
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

@router.get("/ego-lifting-status")
async def get_ego_lifting_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's ego-lifting status and risk assessment"""
    try:
        # Get recent reps (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        result = await db.execute(
            select(RepLog).where(
                RepLog.user_id == current_user.id,
                RepLog.created_at >= thirty_days_ago
            ).order_by(RepLog.created_at.desc())
        )
        recent_reps = result.scalars().all()
        
        if not recent_reps:
            return {
                "ego_lifting_risk": "low",
                "risk_score": 0.0,
                "locked_reps_count": 0,
                "recommendations": ["Start tracking your workouts to get personalized safety insights"],
                "is_plan_locked": False
            }
        
        # Calculate ego-lifting metrics
        total_reps = len(recent_reps)
        ego_lifting_reps = [rep for rep in recent_reps if rep.is_ego_lifting]
        locked_reps = [rep for rep in recent_reps if rep.is_locked]
        
        ego_lifting_percentage = len(ego_lifting_reps) / total_reps if total_reps > 0 else 0
        locked_percentage = len(locked_reps) / total_reps if total_reeps > 0 else 0
        
        # Calculate risk score
        risk_score = (ego_lifting_percentage * 0.6) + (locked_percentage * 0.4)
        
        # Determine risk level
        if risk_score > 0.3:
            risk_level = "high"
            is_plan_locked = True
        elif risk_score > 0.15:
            risk_level = "medium"
            is_plan_locked = False
        else:
            risk_level = "low"
            is_plan_locked = False
        
        # Generate recommendations
        recommendations = _generate_safety_recommendations(risk_score, ego_lifting_percentage)
        
        return {
            "ego_lifting_risk": risk_level,
            "risk_score": round(risk_score, 3),
            "ego_lifting_percentage": round(ego_lifting_percentage * 100, 1),
            "locked_reps_count": len(locked_reps),
            "total_recent_reps": total_reps,
            "recommendations": recommendations,
            "is_plan_locked": is_plan_locked,
            "last_assessment": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ego-lifting status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get ego-lifting status"
        )

@router.post("/override-lock")
async def override_safety_lock(
    reason: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Override safety lock (requires trainer approval for Pro users)"""
    try:
        # Check if user is Pro
        if not current_user.is_pro_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Pro subscription required for safety overrides"
            )
        
        # Log override request
        override_log = {
            "user_id": current_user.id,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending_approval"
        }
        
        # In a real implementation, this would be stored in a database
        # and trigger a notification to the user's trainer
        
        logger.info(f"Safety override requested by user {current_user.id}: {reason}")
        
        return {
            "message": "Override request submitted for trainer approval",
            "override_id": "override_123",  # Would be a real ID
            "status": "pending_approval",
            "estimated_response_time": "24 hours"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Override lock error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit override request"
        )

@router.get("/safety-alerts")
async def get_safety_alerts(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get active safety alerts for the user"""
    try:
        # Get recent dangerous reps
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        result = await db.execute(
            select(RepLog).where(
                RepLog.user_id == current_user.id,
                RepLog.rep_quality == "dangerous",
                RepLog.created_at >= seven_days_ago
            ).order_by(RepLog.created_at.desc())
        )
        dangerous_reps = result.scalars().all()
        
        alerts = []
        
        # Check for dangerous form patterns
        if dangerous_reps:
            alerts.append({
                "type": "dangerous_form",
                "severity": "high",
                "message": f"Detected {len(dangerous_reps)} reps with dangerous form in the last 7 days",
                "recommendation": "Consider reducing weight and focusing on form",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Check for rapid weight progression
        weight_progression_alerts = _check_weight_progression(current_user.id, db)
        alerts.extend(weight_progression_alerts)
        
        # Check for overtraining
        overtraining_alerts = _check_overtraining(current_user.id, db)
        alerts.extend(overtraining_alerts)
        
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "high_severity_count": len([a for a in alerts if a["severity"] == "high"]),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Safety alerts error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get safety alerts"
        )

@router.post("/safety-settings")
async def update_safety_settings(
    settings: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """Update user's safety settings"""
    try:
        # Validate settings
        allowed_settings = {
            "ego_lifting_threshold": float,
            "auto_lock_enabled": bool,
            "safety_notifications": bool,
            "trainer_escalation": bool
        }
        
        for key, value in settings.items():
            if key not in allowed_settings:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid setting: {key}"
                )
            
            if not isinstance(value, allowed_settings[key]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid type for {key}"
                )
        
        # In a real implementation, these would be stored in user preferences
        logger.info(f"Safety settings updated for user {current_user.id}: {settings}")
        
        return {
            "message": "Safety settings updated successfully",
            "updated_settings": settings,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update safety settings error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update safety settings"
        )

@router.get("/form-trends")
async def get_form_trends(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get form quality trends over time"""
    try:
        # Get reps from the specified period
        start_date = datetime.utcnow() - timedelta(days=days)
        
        result = await db.execute(
            select(RepLog).where(
                RepLog.user_id == current_user.id,
                RepLog.created_at >= start_date
            ).order_by(RepLog.created_at)
        )
        reps = result.scalars().all()
        
        if not reps:
            return {
                "trend": "no_data",
                "message": "No workout data available for trend analysis",
                "period_days": days
            }
        
        # Group reps by day and calculate average form scores
        daily_scores = {}
        for rep in reps:
            date_key = rep.created_at.date().isoformat()
            if date_key not in daily_scores:
                daily_scores[date_key] = []
            if rep.form_score:
                daily_scores[date_key].append(rep.form_score)
        
        # Calculate daily averages
        trend_data = []
        for date, scores in sorted(daily_scores.items()):
            avg_score = sum(scores) / len(scores) if scores else 0
            trend_data.append({
                "date": date,
                "average_form_score": round(avg_score, 3),
                "rep_count": len(scores)
            })
        
        # Calculate overall trend
        if len(trend_data) >= 2:
            first_week_avg = sum(d["average_form_score"] for d in trend_data[:7]) / min(7, len(trend_data))
            last_week_avg = sum(d["average_form_score"] for d in trend_data[-7:]) / min(7, len(trend_data))
            
            if last_week_avg > first_week_avg + 0.1:
                trend = "improving"
            elif last_week_avg < first_week_avg - 0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "trend": trend,
            "trend_data": trend_data,
            "period_days": days,
            "total_reps": len(reps),
            "average_form_score": round(sum(rep.form_score or 0 for rep in reps) / len(reps), 3)
        }
        
    except Exception as e:
        logger.error(f"Form trends error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get form trends"
        )

def _generate_safety_recommendations(risk_score: float, ego_lifting_percentage: float) -> List[str]:
    """Generate safety recommendations based on risk assessment"""
    recommendations = []
    
    if risk_score > 0.3:
        recommendations.extend([
            "Immediate action required: Reduce training intensity",
            "Focus on perfect form over weight",
            "Consider working with a trainer",
            "Take additional rest days between sessions"
        ])
    elif risk_score > 0.15:
        recommendations.extend([
            "Monitor your form more closely",
            "Consider reducing weight on compound movements",
            "Increase warm-up time before heavy sets",
            "Focus on controlled movements"
        ])
    else:
        recommendations.extend([
            "Continue with current training approach",
            "Maintain focus on form",
            "Gradually increase intensity as form allows"
        ])
    
    if ego_lifting_percentage > 0.2:
        recommendations.append("High ego-lifting detected - prioritize form over weight")
    
    return recommendations

async def _check_weight_progression(user_id: int, db: AsyncSession) -> List[Dict[str, Any]]:
    """Check for unsafe weight progression patterns"""
    # This would implement logic to detect rapid weight increases
    # For now, returning empty list
    return []

async def _check_overtraining(user_id: int, db: AsyncSession) -> List[Dict[str, Any]]:
    """Check for overtraining patterns"""
    # This would implement logic to detect overtraining
    # For now, returning empty list
    return [] 