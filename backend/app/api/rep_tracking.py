"""
FITRON Rep Tracking API Routes
Real-time pose analysis and rep logging
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import cv2
import numpy as np
from datetime import datetime
import uuid

from app.core.config import settings
from app.core.db import get_db, get_mongo_db, Collections
from app.models.user import User
from app.models.rep_log import RepLog, RepLogCreate, RepLogResponse, RepAnalysis, SessionSummary
from app.services.pose_estimation import pose_service
from app.api.auth import get_current_active_user
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

@router.post("/analyze-video", response_model=RepAnalysis)
async def analyze_video(
    exercise_type: str,
    video_file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze video for rep counting and form analysis"""
    try:
        # Validate file type
        if not video_file.content_type.startswith('video/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a video"
            )
        
        # Read video file
        video_content = await video_file.read()
        
        # Convert to OpenCV format
        video_array = np.frombuffer(video_content, np.uint8)
        
        # Decode video frames
        frames = []
        cap = cv2.VideoCapture()
        cap.open(cv2.CAP_ANY)
        
        # This is a simplified approach - in production, you'd use proper video processing
        # For now, we'll create a mock analysis
        
        # Mock pose analysis
        analysis = pose_service.analyze_rep_sequence([], exercise_type)
        
        # Store video in MongoDB
        mongo_db = await get_mongo_db()
        video_doc = {
            "user_id": current_user.id,
            "exercise_type": exercise_type,
            "video_data": video_content,
            "analysis_result": {
                "rep_count": analysis.rep_count,
                "form_score": analysis.form_score,
                "rep_quality": analysis.rep_quality,
                "is_ego_lifting": analysis.is_ego_lifting,
                "feedback": analysis.feedback,
                "suggestions": analysis.suggestions
            },
            "created_at": datetime.utcnow()
        }
        
        await mongo_db[Collections.POSE_DATA].insert_one(video_doc)
        
        logger.info(f"Video analyzed for user {current_user.id}: {analysis.rep_count} reps")
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Video analysis failed"
        )

@router.post("/log-rep", response_model=RepLogResponse, status_code=status.HTTP_201_CREATED)
async def log_rep(
    rep_data: RepLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Log a single rep with pose data"""
    try:
        # Create rep log entry
        db_rep = RepLog(
            user_id=current_user.id,
            session_id=rep_data.session_id,
            exercise_type=rep_data.exercise_type,
            exercise_name=rep_data.exercise_name,
            set_number=rep_data.set_number,
            rep_number=rep_data.rep_number,
            weight_kg=rep_data.weight_kg,
            duration_seconds=rep_data.duration_seconds,
            velocity_mps=rep_data.velocity_mps,
            range_of_motion_degrees=rep_data.range_of_motion_degrees,
            pose_landmarks=rep_data.pose_landmarks,
            pose_angles=rep_data.pose_angles,
            pose_confidence=rep_data.pose_confidence
        )
        
        db.add(db_rep)
        await db.commit()
        await db.refresh(db_rep)
        
        logger.info(f"Rep logged for user {current_user.id}: {rep_data.exercise_name}")
        
        return RepLogResponse.from_orm(db_rep)
        
    except Exception as e:
        logger.error(f"Rep logging error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log rep"
        )

@router.get("/session/{session_id}", response_model=SessionSummary)
async def get_session_summary(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get summary of a workout session"""
    try:
        # Get all reps for the session
        result = await db.execute(
            select(RepLog).where(
                RepLog.user_id == current_user.id,
                RepLog.session_id == session_id
            )
        )
        reps = result.scalars().all()
        
        if not reps:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Calculate summary
        total_reps = len(reps)
        total_sets = len(set(rep.set_number for rep in reps))
        total_duration = sum(rep.duration_seconds or 0 for rep in reps)
        average_form_score = sum(rep.form_score or 0 for rep in reps) / total_reps if total_reps > 0 else 0
        ego_lifting_count = sum(1 for rep in reps if rep.is_ego_lifting)
        locked_reps_count = sum(1 for rep in reps if rep.is_locked)
        exercises = list(set(rep.exercise_name for rep in reps))
        
        summary = SessionSummary(
            session_id=session_id,
            total_reps=total_reps,
            total_sets=total_sets,
            total_duration=total_duration,
            average_form_score=average_form_score,
            ego_lifting_count=ego_lifting_count,
            locked_reps_count=locked_reps_count,
            exercises=exercises,
            created_at=reps[0].created_at
        )
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session summary"
        )

@router.get("/reps", response_model=List[RepLogResponse])
async def get_user_reps(
    skip: int = 0,
    limit: int = 100,
    exercise_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's rep logs with optional filtering"""
    try:
        query = select(RepLog).where(RepLog.user_id == current_user.id)
        
        if exercise_type:
            query = query.where(RepLog.exercise_type == exercise_type)
        
        query = query.order_by(RepLog.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        reps = result.scalars().all()
        
        return [RepLogResponse.from_orm(rep) for rep in reps]
        
    except Exception as e:
        logger.error(f"Get reps error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get rep logs"
        )

@router.get("/reps/{rep_id}", response_model=RepLogResponse)
async def get_rep_detail(
    rep_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed information about a specific rep"""
    try:
        result = await db.execute(
            select(RepLog).where(
                RepLog.id == rep_id,
                RepLog.user_id == current_user.id
            )
        )
        rep = result.scalar_one_or_none()
        
        if not rep:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rep not found"
            )
        
        return RepLogResponse.from_orm(rep)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get rep detail error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get rep details"
        )

@router.put("/reps/{rep_id}", response_model=RepLogResponse)
async def update_rep(
    rep_id: int,
    rep_update: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update rep log entry"""
    try:
        result = await db.execute(
            select(RepLog).where(
                RepLog.id == rep_id,
                RepLog.user_id == current_user.id
            )
        )
        rep = result.scalar_one_or_none()
        
        if not rep:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rep not found"
            )
        
        # Update rep fields
        for field, value in rep_update.items():
            if hasattr(rep, field) and value is not None:
                setattr(rep, field, value)
        
        await db.commit()
        await db.refresh(rep)
        
        logger.info(f"Rep updated: {rep_id}")
        
        return RepLogResponse.from_orm(rep)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update rep error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update rep"
        )

@router.delete("/reps/{rep_id}")
async def delete_rep(
    rep_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete rep log entry"""
    try:
        result = await db.execute(
            select(RepLog).where(
                RepLog.id == rep_id,
                RepLog.user_id == current_user.id
            )
        )
        rep = result.scalar_one_or_none()
        
        if not rep:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rep not found"
            )
        
        await db.delete(rep)
        await db.commit()
        
        logger.info(f"Rep deleted: {rep_id}")
        
        return {"message": "Rep deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete rep error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete rep"
        )

@router.post("/start-session")
async def start_workout_session(
    current_user: User = Depends(get_current_active_user)
):
    """Start a new workout session"""
    try:
        session_id = str(uuid.uuid4())
        
        logger.info(f"Workout session started for user {current_user.id}: {session_id}")
        
        return {
            "session_id": session_id,
            "message": "Workout session started",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Start session error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start session"
        )

@router.get("/analytics/summary")
async def get_analytics_summary(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's workout analytics summary"""
    try:
        # Get total reps
        total_reps_result = await db.execute(
            select(func.count(RepLog.id)).where(RepLog.user_id == current_user.id)
        )
        total_reps = total_reps_result.scalar()
        
        # Get average form score
        avg_form_result = await db.execute(
            select(func.avg(RepLog.form_score)).where(RepLog.user_id == current_user.id)
        )
        avg_form_score = avg_form_result.scalar() or 0
        
        # Get ego lifting count
        ego_lifting_result = await db.execute(
            select(func.count(RepLog.id)).where(
                RepLog.user_id == current_user.id,
                RepLog.is_ego_lifting == True
            )
        )
        ego_lifting_count = ego_lifting_result.scalar()
        
        # Get most common exercise
        exercise_result = await db.execute(
            select(RepLog.exercise_name, func.count(RepLog.id)).where(
                RepLog.user_id == current_user.id
            ).group_by(RepLog.exercise_name).order_by(func.count(RepLog.id).desc()).limit(1)
        )
        most_common_exercise = exercise_result.first()
        
        analytics = {
            "total_reps": total_reps,
            "average_form_score": round(avg_form_score, 2),
            "ego_lifting_count": ego_lifting_count,
            "ego_lifting_percentage": round((ego_lifting_count / total_reps * 100) if total_reps > 0 else 0, 2),
            "most_common_exercise": most_common_exercise[0] if most_common_exercise else None,
            "total_workouts": total_reps // 20 if total_reps > 0 else 0  # Rough estimate
        }
        
        return analytics
        
    except Exception as e:
        logger.error(f"Analytics summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analytics summary"
        ) 