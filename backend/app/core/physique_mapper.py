"""
FITRON Physique Mapper Core Module
Map user goals to celebrity physiques and generate personalized plans
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass

from app.models.physique_goal import PhysiqueGoal
from app.services.clip_engine import clip_engine
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class PhysiqueBlueprint:
    """Physique blueprint data structure"""
    celebrity_name: str
    category: str
    difficulty_level: str
    target_metrics: Dict[str, float]
    estimated_time_days: int
    workout_plan: Dict[str, Any]
    nutrition_plan: Dict[str, Any]
    progress_milestones: List[Dict[str, Any]]
    recommendations: List[str]

@dataclass
class ProgressAssessment:
    """Progress assessment data structure"""
    current_similarity: float
    target_similarity: float
    progress_percentage: float
    days_remaining: int
    current_metrics: Dict[str, float]
    target_metrics: Dict[str, float]
    next_milestone: Dict[str, Any]
    recommendations: List[str]

class PhysiqueMapper:
    """Map user goals to celebrity physiques and track progress"""
    
    def __init__(self):
        """Initialize physique mapper"""
        self.logger = setup_logger(__name__)
    
    def create_physique_blueprint(self, goal: PhysiqueGoal, user_fitness_level: str) -> PhysiqueBlueprint:
        """Create a comprehensive physique blueprint"""
        try:
            # Get celebrity reference
            celebrity = self._get_celebrity_reference(goal.target_celebrity)
            if not celebrity:
                raise ValueError(f"Celebrity {goal.target_celebrity} not found")
            
            # Calculate estimated time
            estimated_time = self._estimate_time_to_goal(celebrity, goal, user_fitness_level)
            
            # Generate workout plan
            workout_plan = self._generate_workout_plan(celebrity, goal, user_fitness_level)
            
            # Generate nutrition plan
            nutrition_plan = self._generate_nutrition_plan(celebrity, goal)
            
            # Create progress milestones
            progress_milestones = self._create_progress_milestones(goal, estimated_time)
            
            # Generate recommendations
            recommendations = self._generate_blueprint_recommendations(celebrity, goal, user_fitness_level)
            
            return PhysiqueBlueprint(
                celebrity_name=celebrity.name,
                category=celebrity.category,
                difficulty_level=celebrity.difficulty_level,
                target_metrics=celebrity.target_metrics,
                estimated_time_days=estimated_time,
                workout_plan=workout_plan,
                nutrition_plan=nutrition_plan,
                progress_milestones=progress_milestones,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Error creating physique blueprint: {e}")
            raise
    
    def assess_progress(self, goal: PhysiqueGoal, current_metrics: Dict[str, float]) -> ProgressAssessment:
        """Assess progress towards physique goal"""
        try:
            # Calculate current similarity if embeddings are available
            current_similarity = goal.current_similarity_score or 0.0
            target_similarity = goal.target_similarity_score or 0.8  # Default target
            
            # Calculate progress percentage
            progress_percentage = self._calculate_progress_percentage(goal, current_metrics)
            
            # Calculate days remaining
            days_remaining = self._calculate_days_remaining(goal, progress_percentage)
            
            # Get next milestone
            next_milestone = self._get_next_milestone(goal, progress_percentage)
            
            # Generate recommendations
            recommendations = self._generate_progress_recommendations(
                progress_percentage, current_metrics, goal
            )
            
            return ProgressAssessment(
                current_similarity=current_similarity,
                target_similarity=target_similarity,
                progress_percentage=progress_percentage,
                days_remaining=days_remaining,
                current_metrics=current_metrics,
                target_metrics=goal.target_metrics or {},
                next_milestone=next_milestone,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Error assessing progress: {e}")
            raise
    
    def update_goal_progress(self, goal: PhysiqueGoal, current_image_url: str, 
                           current_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Update goal progress with current data"""
        try:
            # Analyze current physique
            analysis = clip_engine.analyze_physique_goal(current_image_url, goal.target_celebrity)
            
            if not analysis:
                raise ValueError("Could not analyze current physique")
            
            # Update goal with current data
            goal.current_weight_kg = current_metrics.get("weight_kg")
            goal.current_body_fat_percentage = current_metrics.get("body_fat_percentage")
            goal.current_muscle_mass_kg = current_metrics.get("muscle_mass_kg")
            goal.current_similarity_score = analysis.get("current_similarity")
            
            # Calculate progress
            progress_percentage = self._calculate_progress_percentage(goal, current_metrics)
            
            return {
                "goal_id": goal.id,
                "current_similarity": analysis.get("current_similarity"),
                "progress_percentage": progress_percentage,
                "current_metrics": current_metrics,
                "target_metrics": goal.target_metrics,
                "recommendations": analysis.get("recommendations", []),
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error updating goal progress: {e}")
            raise
    
    def get_similar_physiques(self, current_image_url: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Get similar physiques to current user"""
        try:
            # Encode current image
            current_embedding = clip_engine.encode_image(current_image_url)
            if not current_embedding:
                raise ValueError("Could not process current image")
            
            # Find similar physiques
            similar_physiques = clip_engine.find_similar_physiques(current_embedding, top_k)
            
            return [
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
            
        except Exception as e:
            self.logger.error(f"Error getting similar physiques: {e}")
            raise
    
    def _get_celebrity_reference(self, celebrity_name: str):
        """Get celebrity reference from database"""
        for celeb in clip_engine.celebrity_physiques:
            if celeb.name.lower() == celebrity_name.lower():
                return celeb
        return None
    
    def _estimate_time_to_goal(self, celebrity, goal: PhysiqueGoal, user_fitness_level: str) -> int:
        """Estimate time to reach goal"""
        base_time = {
            "easy": 90,
            "medium": 180,
            "hard": 365,
            "expert": 730
        }
        
        difficulty_time = base_time.get(celebrity.difficulty_level, 180)
        
        # Adjust based on user fitness level
        fitness_multipliers = {
            "beginner": 1.5,
            "intermediate": 1.0,
            "advanced": 0.7
        }
        
        multiplier = fitness_multipliers.get(user_fitness_level, 1.0)
        
        return int(difficulty_time * multiplier)
    
    def _generate_workout_plan(self, celebrity, goal: PhysiqueGoal, user_fitness_level: str) -> Dict[str, Any]:
        """Generate personalized workout plan"""
        # Get base plan from CLIP engine
        base_plan = clip_engine.generate_workout_plan(celebrity.name, user_fitness_level)
        
        if not base_plan:
            # Fallback to category-based plan
            base_plan = self._get_category_workout_plan(celebrity.category, user_fitness_level)
        
        # Customize based on goal specifics
        customized_plan = self._customize_workout_plan(base_plan, goal, user_fitness_level)
        
        return customized_plan
    
    def _generate_nutrition_plan(self, celebrity, goal: PhysiqueGoal) -> Dict[str, Any]:
        """Generate personalized nutrition plan"""
        target_metrics = celebrity.target_metrics
        
        # Calculate daily caloric needs
        current_weight = goal.current_weight_kg or 70.0
        target_weight = target_metrics.get("weight_kg", current_weight)
        
        # Simple calorie calculation (would be more sophisticated in production)
        if target_weight > current_weight:
            # Bulking phase
            daily_calories = current_weight * 20 + 500
            protein_ratio = 0.3
            carbs_ratio = 0.4
            fat_ratio = 0.3
        else:
            # Cutting phase
            daily_calories = current_weight * 18 - 300
            protein_ratio = 0.35
            carbs_ratio = 0.35
            fat_ratio = 0.3
        
        return {
            "daily_calories": round(daily_calories),
            "macronutrients": {
                "protein_g": round(daily_calories * protein_ratio / 4),
                "carbs_g": round(daily_calories * carbs_ratio / 4),
                "fat_g": round(daily_calories * fat_ratio / 9)
            },
            "meal_timing": {
                "breakfast": "7:00 AM",
                "lunch": "12:00 PM",
                "dinner": "7:00 PM",
                "pre_workout": "30 minutes before",
                "post_workout": "Within 30 minutes"
            },
            "supplements": self._get_recommended_supplements(celebrity.category),
            "hydration": "3-4 liters per day"
        }
    
    def _create_progress_milestones(self, goal: PhysiqueGoal, total_days: int) -> List[Dict[str, Any]]:
        """Create progress milestones"""
        milestones = []
        
        # Create 4 milestones (25%, 50%, 75%, 100%)
        for i, percentage in enumerate([25, 50, 75, 100]):
            days_to_milestone = int((percentage / 100) * total_days)
            milestone_date = datetime.utcnow() + timedelta(days=days_to_milestone)
            
            milestone = {
                "milestone_id": i + 1,
                "percentage": percentage,
                "days_to_reach": days_to_milestone,
                "target_date": milestone_date.isoformat(),
                "description": f"{percentage}% progress milestone",
                "metrics_target": self._calculate_milestone_metrics(goal, percentage)
            }
            
            milestones.append(milestone)
        
        return milestones
    
    def _calculate_progress_percentage(self, goal: PhysiqueGoal, current_metrics: Dict[str, float]) -> float:
        """Calculate progress percentage towards goal"""
        if not goal.target_metrics:
            return 0.0
        
        progress_factors = []
        
        # Weight progress
        if goal.target_metrics.get("weight_kg") and current_metrics.get("weight_kg"):
            target_weight = goal.target_metrics["weight_kg"]
            current_weight = current_metrics["weight_kg"]
            weight_progress = 1 - abs((current_weight - target_weight) / target_weight)
            progress_factors.append(max(0, min(1, weight_progress)))
        
        # Body fat progress
        if goal.target_metrics.get("body_fat_percentage") and current_metrics.get("body_fat_percentage"):
            target_bf = goal.target_metrics["body_fat_percentage"]
            current_bf = current_metrics["body_fat_percentage"]
            bf_progress = 1 - abs((current_bf - target_bf) / target_bf)
            progress_factors.append(max(0, min(1, bf_progress)))
        
        # Similarity progress
        if goal.current_similarity_score:
            progress_factors.append(goal.current_similarity_score)
        
        if progress_factors:
            return (sum(progress_factors) / len(progress_factors)) * 100
        else:
            return 0.0
    
    def _calculate_days_remaining(self, goal: PhysiqueGoal, progress_percentage: float) -> int:
        """Calculate days remaining to reach goal"""
        if progress_percentage >= 100:
            return 0
        
        # Simple linear calculation (would be more sophisticated in production)
        if goal.estimated_completion_date:
            remaining = goal.estimated_completion_date - datetime.utcnow()
            return max(0, remaining.days)
        else:
            # Estimate based on progress
            if progress_percentage > 0:
                days_elapsed = (datetime.utcnow() - goal.start_date).days
                total_estimated_days = int((days_elapsed / progress_percentage) * 100)
                return max(0, total_estimated_days - days_elapsed)
            else:
                return 365  # Default estimate
    
    def _get_next_milestone(self, goal: PhysiqueGoal, progress_percentage: float) -> Dict[str, Any]:
        """Get next milestone to reach"""
        milestones = [25, 50, 75, 100]
        
        for milestone in milestones:
            if progress_percentage < milestone:
                return {
                    "milestone_percentage": milestone,
                    "progress_needed": milestone - progress_percentage,
                    "description": f"Reach {milestone}% progress"
                }
        
        return {
            "milestone_percentage": 100,
            "progress_needed": 0,
            "description": "Goal achieved!"
        }
    
    def _generate_blueprint_recommendations(self, celebrity, goal: PhysiqueGoal, user_fitness_level: str) -> List[str]:
        """Generate recommendations for physique blueprint"""
        recommendations = []
        
        # Difficulty-based recommendations
        if celebrity.difficulty_level == "expert":
            recommendations.append("This is an advanced goal - consider working with a professional trainer")
        elif celebrity.difficulty_level == "hard":
            recommendations.append("This goal requires significant dedication and consistency")
        
        # Category-based recommendations
        if celebrity.category == "bodybuilder":
            recommendations.append("Focus on progressive overload and muscle isolation exercises")
        elif celebrity.category == "lean":
            recommendations.append("Emphasize cardio and maintain a caloric deficit")
        elif celebrity.category == "athletic":
            recommendations.append("Balance strength training with conditioning work")
        
        # Fitness level recommendations
        if user_fitness_level == "beginner":
            recommendations.append("Start with basic movements and gradually increase complexity")
        elif user_fitness_level == "advanced":
            recommendations.append("You can handle advanced techniques and higher intensity")
        
        return recommendations
    
    def _generate_progress_recommendations(self, progress_percentage: float, 
                                         current_metrics: Dict[str, float], 
                                         goal: PhysiqueGoal) -> List[str]:
        """Generate recommendations based on progress"""
        recommendations = []
        
        if progress_percentage < 25:
            recommendations.append("Focus on establishing consistent habits and form")
        elif progress_percentage < 50:
            recommendations.append("Great start! Now focus on progressive overload")
        elif progress_percentage < 75:
            recommendations.append("You're making excellent progress! Stay consistent")
        elif progress_percentage < 100:
            recommendations.append("You're close to your goal! Fine-tune your approach")
        else:
            recommendations.append("Congratulations! You've achieved your goal")
        
        # Specific metric recommendations
        if goal.target_metrics:
            if goal.target_metrics.get("weight_kg") and current_metrics.get("weight_kg"):
                current_weight = current_metrics["weight_kg"]
                target_weight = goal.target_metrics["weight_kg"]
                
                if current_weight < target_weight * 0.9:
                    recommendations.append("Consider increasing caloric intake for muscle growth")
                elif current_weight > target_weight * 1.1:
                    recommendations.append("Focus on fat loss through diet and cardio")
        
        return recommendations
    
    def _get_category_workout_plan(self, category: str, fitness_level: str) -> Dict[str, Any]:
        """Get category-based workout plan"""
        # Basic workout plan templates (simplified)
        plans = {
            "bodybuilder": {
                "focus": "muscle_hypertrophy",
                "frequency": "6 days per week",
                "split": "Push/Pull/Legs"
            },
            "lean": {
                "focus": "fat_loss",
                "frequency": "5 days per week",
                "split": "Full body + cardio"
            },
            "athletic": {
                "focus": "strength_power",
                "frequency": "4 days per week",
                "split": "Upper/Lower"
            }
        }
        
        return plans.get(category, {
            "focus": "general_fitness",
            "frequency": "3 days per week",
            "split": "Full body"
        })
    
    def _customize_workout_plan(self, base_plan: Dict[str, Any], goal: PhysiqueGoal, 
                               user_fitness_level: str) -> Dict[str, Any]:
        """Customize workout plan based on goal and user level"""
        # Add customization logic here
        customized_plan = base_plan.copy()
        
        # Adjust based on fitness level
        if user_fitness_level == "beginner":
            customized_plan["intensity"] = "moderate"
            customized_plan["rest_days"] = "more"
        elif user_fitness_level == "advanced":
            customized_plan["intensity"] = "high"
            customized_plan["rest_days"] = "minimal"
        
        return customized_plan
    
    def _get_recommended_supplements(self, category: str) -> List[str]:
        """Get recommended supplements based on category"""
        supplements = {
            "bodybuilder": ["Whey Protein", "Creatine", "BCAAs", "Multivitamin"],
            "lean": ["Whey Protein", "Omega-3", "Multivitamin", "Caffeine"],
            "athletic": ["Whey Protein", "Creatine", "Beta-Alanine", "Multivitamin"]
        }
        
        return supplements.get(category, ["Whey Protein", "Multivitamin"])
    
    def _calculate_milestone_metrics(self, goal: PhysiqueGoal, percentage: float) -> Dict[str, float]:
        """Calculate target metrics for a specific milestone"""
        if not goal.target_metrics:
            return {}
        
        milestone_metrics = {}
        
        for metric, target_value in goal.target_metrics.items():
            current_value = getattr(goal, f"current_{metric}", 0) or 0
            progress = percentage / 100
            milestone_value = current_value + (target_value - current_value) * progress
            milestone_metrics[metric] = round(milestone_value, 1)
        
        return milestone_metrics 