"""
FITRON Physique Goal API Routes
Celebrity physique mapping and goal tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.config import settings
from app.core.db import get_db
from app.models.user import User
from app.models.physique_goal import PhysiqueGoal, PhysiqueGoalCreate, PhysiqueGoalResponse, PhysiqueGoalUpdate
from app.services.clip_engine import clip_engine
from app.api.auth import get_current_active_user
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

@router.post("/analyze-physique", response_model=Dict[str, Any])
async def analyze_physique(
    current_image: UploadFile = File(...),
    target_celebrity: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Analyze current physique and compare with target celebrity"""
    try:
        # Validate file type
        if not current_image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Save image temporarily and get path
        # In production, you'd upload to S3 or similar
        image_path = f"temp/{current_user.id}_{datetime.utcnow().timestamp()}.jpg"
        
        # Analyze physique
        if target_celebrity:
            analysis = clip_engine.analyze_physique_goal(image_path, target_celebrity)
            if not analysis:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not analyze physique against target celebrity"
                )
        else:
            # Get current physique embedding
            current_embedding = clip_engine.encode_image(image_path)
            if not current_embedding:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not process image"
                )
            
            # Find similar physiques
            similar_physiques = clip_engine.find_similar_physiques(current_embedding)
            
            analysis = {
                "current_embedding": current_embedding,
                "similar_physiques": [
                    {
                        "celebrity_name": p.celebrity_name,
                        "similarity_score": p.similarity_score,
                        "category": p.category,
                        "difficulty_level": p.difficulty_level,
                        "recommendations": p.recommendations,
                        "estimated_time": p.estimated_time
                    }
                    for p in similar_physiques
                ]
            }
        
        logger.info(f"Physique analyzed for user {current_user.id}")
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Physique analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze physique"
        )

@router.post("/create-goal", response_model=PhysiqueGoalResponse, status_code=status.HTTP_201_CREATED)
async def create_physique_goal(
    goal_data: PhysiqueGoalCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new physique goal"""
    try:
        # If target celebrity is specified, get their embedding
        target_embedding = None
        if goal_data.target_celebrity:
            # In a real implementation, you'd get this from the celebrity database
            # For now, we'll create a placeholder
            target_embedding = [0.0] * 512  # CLIP embedding size
        
        # Create physique goal
        db_goal = PhysiqueGoal(
            user_id=current_user.id,
            goal_name=goal_data.goal_name,
            physique_category=goal_data.physique_category,
            target_celebrity=goal_data.target_celebrity,
            target_image_url=goal_data.target_image_url,
            target_embedding=target_embedding,
            target_weight_kg=goal_data.target_weight_kg,
            target_body_fat_percentage=goal_data.target_body_fat_percentage,
            target_muscle_mass_kg=goal_data.target_muscle_mass_kg,
            target_date=goal_data.target_date,
            priority=goal_data.priority,
            is_primary_goal=goal_data.is_primary_goal
        )
        
        db.add(db_goal)
        await db.commit()
        await db.refresh(db_goal)
        
        logger.info(f"Physique goal created for user {current_user.id}: {goal_data.goal_name}")
        
        return PhysiqueGoalResponse.from_orm(db_goal)
        
    except Exception as e:
        logger.error(f"Create physique goal error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create physique goal"
        )

@router.get("/goals", response_model=List[PhysiqueGoalResponse])
async def get_user_goals(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's physique goals"""
    try:
        result = await db.execute(
            select(PhysiqueGoal).where(PhysiqueGoal.user_id == current_user.id)
            .order_by(PhysiqueGoal.priority.desc(), PhysiqueGoal.created_at.desc())
        )
        goals = result.scalars().all()
        
        return [PhysiqueGoalResponse.from_orm(goal) for goal in goals]
        
    except Exception as e:
        logger.error(f"Get user goals error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get physique goals"
        )

@router.get("/goals/{goal_id}", response_model=PhysiqueGoalResponse)
async def get_goal_detail(
    goal_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed information about a specific goal"""
    try:
        result = await db.execute(
            select(PhysiqueGoal).where(
                PhysiqueGoal.id == goal_id,
                PhysiqueGoal.user_id == current_user.id
            )
        )
        goal = result.scalar_one_or_none()
        
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        
        return PhysiqueGoalResponse.from_orm(goal)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get goal detail error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get goal details"
        )

@router.put("/goals/{goal_id}", response_model=PhysiqueGoalResponse)
async def update_goal(
    goal_id: int,
    goal_update: PhysiqueGoalUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update physique goal"""
    try:
        result = await db.execute(
            select(PhysiqueGoal).where(
                PhysiqueGoal.id == goal_id,
                PhysiqueGoal.user_id == current_user.id
            )
        )
        goal = result.scalar_one_or_none()
        
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        
        # Update goal fields
        update_data = goal_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(goal, field):
                setattr(goal, field, value)
        
        await db.commit()
        await db.refresh(goal)
        
        logger.info(f"Goal updated: {goal_id}")
        
        return PhysiqueGoalResponse.from_orm(goal)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update goal error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update goal"
        )

@router.delete("/goals/{goal_id}")
async def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete physique goal"""
    try:
        result = await db.execute(
            select(PhysiqueGoal).where(
                PhysiqueGoal.id == goal_id,
                PhysiqueGoal.user_id == current_user.id
            )
        )
        goal = result.scalar_one_or_none()
        
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        
        await db.delete(goal)
        await db.commit()
        
        logger.info(f"Goal deleted: {goal_id}")
        
        return {"message": "Goal deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete goal error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete goal"
        )

@router.get("/celebrities", response_model=List[Dict[str, Any]])
async def get_available_celebrities():
    """Get list of available celebrity physiques"""
    try:
        celebrities = []
        for celeb in clip_engine.celebrity_physiques:
            celebrities.append({
                "name": celeb.name,
                "category": celeb.category,
                "description": celeb.description,
                "difficulty_level": celeb.difficulty_level,
                "target_metrics": celeb.target_metrics
            })
        
        return celebrities
        
    except Exception as e:
        logger.error(f"Get celebrities error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get celebrities"
        )

@router.post("/goals/{goal_id}/progress", response_model=Dict[str, Any])
async def update_goal_progress(
    goal_id: int,
    current_metrics: Dict[str, float],
    current_image: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update goal progress with current physique and metrics"""
    try:
        # Get goal
        result = await db.execute(
            select(PhysiqueGoal).where(
                PhysiqueGoal.id == goal_id,
                PhysiqueGoal.user_id == current_user.id
            )
        )
        goal = result.scalar_one_or_none()
        
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        
        # Analyze current physique
        image_path = f"temp/{current_user.id}_{datetime.utcnow().timestamp()}.jpg"
        current_embedding = clip_engine.encode_image(image_path)
        
        if not current_embedding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not process current physique image"
            )
        
        # Calculate similarity if target embedding exists
        similarity_score = None
        if goal.target_embedding:
            similarity_score = clip_engine.calculate_similarity(
                current_embedding, goal.target_embedding
            )
        
        # Update goal with current data
        goal.current_weight_kg = current_metrics.get("weight_kg")
        goal.current_body_fat_percentage = current_metrics.get("body_fat_percentage")
        goal.current_muscle_mass_kg = current_metrics.get("muscle_mass_kg")
        goal.user_current_embedding = current_embedding
        goal.current_similarity_score = similarity_score
        
        await db.commit()
        await db.refresh(goal)
        
        # Calculate progress
        progress_percentage = _calculate_progress_percentage(goal, current_metrics)
        
        logger.info(f"Goal progress updated for user {current_user.id}: {progress_percentage}%")
        
        return {
            "goal_id": goal_id,
            "current_similarity": similarity_score,
            "progress_percentage": progress_percentage,
            "current_metrics": current_metrics,
            "target_metrics": {
                "weight_kg": goal.target_weight_kg,
                "body_fat_percentage": goal.target_body_fat_percentage,
                "muscle_mass_kg": goal.target_muscle_mass_kg
            },
            "updated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update goal progress error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update goal progress"
        )

@router.get("/goals/{goal_id}/workout-plan", response_model=Dict[str, Any])
async def get_goal_workout_plan(
    goal_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get personalized workout plan for the goal"""
    try:
        # Get goal
        result = await db.execute(
            select(PhysiqueGoal).where(
                PhysiqueGoal.id == goal_id,
                PhysiqueGoal.user_id == current_user.id
            )
        )
        goal = result.scalar_one_or_none()
        
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        
        # Generate workout plan
        if goal.target_celebrity:
            workout_plan = clip_engine.generate_workout_plan(
                goal.target_celebrity, current_user.fitness_level
            )
        else:
            # Generate plan based on physique category
            workout_plan = _generate_category_workout_plan(
                goal.physique_category, current_user.fitness_level
            )
        
        if not workout_plan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not generate workout plan"
            )
        
        return workout_plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workout plan error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workout plan"
        )

def _calculate_progress_percentage(goal: PhysiqueGoal, current_metrics: Dict[str, float]) -> float:
    """Calculate progress percentage towards goal"""
    try:
        # Simple progress calculation based on metrics
        # In a real implementation, this would be more sophisticated
        
        progress_factors = []
        
        if goal.target_weight_kg and current_metrics.get("weight_kg"):
            weight_progress = 1 - abs(
                (current_metrics["weight_kg"] - goal.target_weight_kg) / goal.target_weight_kg
            )
            progress_factors.append(max(0, min(1, weight_progress)))
        
        if goal.target_body_fat_percentage and current_metrics.get("body_fat_percentage"):
            bf_progress = 1 - abs(
                (current_metrics["body_fat_percentage"] - goal.target_body_fat_percentage) / goal.target_body_fat_percentage
            )
            progress_factors.append(max(0, min(1, bf_progress)))
        
        if goal.current_similarity_score:
            progress_factors.append(goal.current_similarity_score)
        
        if progress_factors:
            return sum(progress_factors) / len(progress_factors) * 100
        else:
            return 0.0
            
    except Exception as e:
        logger.error(f"Progress calculation error: {e}")
        return 0.0

def _generate_category_workout_plan(category: str, fitness_level: str) -> Dict[str, Any]:
    """Generate workout plan based on physique category"""
    # Basic workout plan templates
    plans = {
        "bodybuilder": {
            "focus": "muscle_hypertrophy",
            "weekly_schedule": {
                "monday": ["chest", "triceps"],
                "tuesday": ["back", "biceps"],
                "wednesday": ["legs"],
                "thursday": ["shoulders", "abs"],
                "friday": ["arms"],
                "saturday": ["legs"],
                "sunday": ["rest"]
            },
            "sets_per_exercise": 4,
            "reps_range": "8-12",
            "rest_time": "60-90 seconds"
        },
        "lean": {
            "focus": "fat_loss",
            "weekly_schedule": {
                "monday": ["cardio", "strength"],
                "tuesday": ["hiit"],
                "wednesday": ["strength", "cardio"],
                "thursday": ["rest"],
                "friday": ["strength", "cardio"],
                "saturday": ["hiit"],
                "sunday": ["rest"]
            },
            "sets_per_exercise": 3,
            "reps_range": "12-15",
            "rest_time": "30-45 seconds"
        },
        "athletic": {
            "focus": "strength_power",
            "weekly_schedule": {
                "monday": ["compound_lifts"],
                "tuesday": ["conditioning"],
                "wednesday": ["compound_lifts"],
                "thursday": ["rest"],
                "friday": ["compound_lifts"],
                "saturday": ["conditioning"],
                "sunday": ["rest"]
            },
            "sets_per_exercise": 5,
            "reps_range": "3-6",
            "rest_time": "2-3 minutes"
        }
    }
    
    return plans.get(category, {
        "focus": "general_fitness",
        "weekly_schedule": {
            "monday": ["full_body"],
            "tuesday": ["cardio"],
            "wednesday": ["full_body"],
            "thursday": ["rest"],
            "friday": ["full_body"],
            "saturday": ["cardio"],
            "sunday": ["rest"]
        },
        "sets_per_exercise": 3,
        "reps_range": "10-12",
        "rest_time": "60 seconds"
    }) 