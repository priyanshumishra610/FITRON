"""
FITRON Rep Analyzer Core Module
Analyze workout data and generate insights
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass

from app.models.rep_log import RepLog
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class WorkoutInsights:
    """Workout insights data structure"""
    total_reps: int
    total_sets: int
    total_duration: float
    average_form_score: float
    form_trend: str  # improving, declining, stable
    ego_lifting_percentage: float
    most_common_exercise: str
    strength_progress: Dict[str, float]
    recommendations: List[str]

@dataclass
class ExerciseAnalysis:
    """Exercise-specific analysis"""
    exercise_name: str
    total_reps: int
    average_weight: float
    average_form_score: float
    form_trend: str
    max_weight: float
    volume_progression: List[float]
    recommendations: List[str]

class RepAnalyzer:
    """Analyze rep data and generate insights"""
    
    def __init__(self):
        """Initialize rep analyzer"""
        self.logger = setup_logger(__name__)
    
    def analyze_workout_session(self, reps: List[RepLog]) -> WorkoutInsights:
        """Analyze a complete workout session"""
        if not reps:
            return WorkoutInsights(
                total_reps=0,
                total_sets=0,
                total_duration=0.0,
                average_form_score=0.0,
                form_trend="no_data",
                ego_lifting_percentage=0.0,
                most_common_exercise="none",
                strength_progress={},
                recommendations=["Start tracking your workouts to get insights"]
            )
        
        # Basic metrics
        total_reps = len(reps)
        total_sets = len(set(rep.set_number for rep in reps))
        total_duration = sum(rep.duration_seconds or 0 for rep in reps)
        
        # Form analysis
        form_scores = [rep.form_score for rep in reps if rep.form_score is not None]
        average_form_score = np.mean(form_scores) if form_scores else 0.0
        
        # Ego lifting analysis
        ego_lifting_reps = [rep for rep in reps if rep.is_ego_lifting]
        ego_lifting_percentage = len(ego_lifting_reps) / total_reps if total_reps > 0 else 0.0
        
        # Most common exercise
        exercise_counts = {}
        for rep in reps:
            exercise_counts[rep.exercise_name] = exercise_counts.get(rep.exercise_name, 0) + 1
        most_common_exercise = max(exercise_counts.items(), key=lambda x: x[1])[0] if exercise_counts else "none"
        
        # Form trend analysis
        form_trend = self._analyze_form_trend(reps)
        
        # Strength progress analysis
        strength_progress = self._analyze_strength_progress(reps)
        
        # Generate recommendations
        recommendations = self._generate_workout_recommendations(
            average_form_score, ego_lifting_percentage, form_trend
        )
        
        return WorkoutInsights(
            total_reps=total_reps,
            total_sets=total_sets,
            total_duration=total_duration,
            average_form_score=average_form_score,
            form_trend=form_trend,
            ego_lifting_percentage=ego_lifting_percentage,
            most_common_exercise=most_common_exercise,
            strength_progress=strength_progress,
            recommendations=recommendations
        )
    
    def analyze_exercise(self, reps: List[RepLog], exercise_name: str) -> ExerciseAnalysis:
        """Analyze a specific exercise"""
        exercise_reps = [rep for rep in reps if rep.exercise_name == exercise_name]
        
        if not exercise_reps:
            return ExerciseAnalysis(
                exercise_name=exercise_name,
                total_reps=0,
                average_weight=0.0,
                average_form_score=0.0,
                form_trend="no_data",
                max_weight=0.0,
                volume_progression=[],
                recommendations=["No data available for this exercise"]
            )
        
        # Basic metrics
        total_reps = len(exercise_reps)
        weights = [rep.weight_kg for rep in exercise_reps if rep.weight_kg is not None]
        average_weight = np.mean(weights) if weights else 0.0
        max_weight = max(weights) if weights else 0.0
        
        # Form analysis
        form_scores = [rep.form_score for rep in exercise_reps if rep.form_score is not None]
        average_form_score = np.mean(form_scores) if form_scores else 0.0
        
        # Form trend
        form_trend = self._analyze_form_trend(exercise_reps)
        
        # Volume progression
        volume_progression = self._calculate_volume_progression(exercise_reps)
        
        # Generate recommendations
        recommendations = self._generate_exercise_recommendations(
            exercise_name, average_form_score, average_weight, form_trend
        )
        
        return ExerciseAnalysis(
            exercise_name=exercise_name,
            total_reps=total_reps,
            average_weight=average_weight,
            average_form_score=average_form_score,
            form_trend=form_trend,
            max_weight=max_weight,
            volume_progression=volume_progression,
            recommendations=recommendations
        )
    
    def analyze_long_term_progress(self, all_reps: List[RepLog], days: int = 30) -> Dict[str, Any]:
        """Analyze long-term progress over specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_reps = [rep for rep in all_reps if rep.created_at >= cutoff_date]
        
        if not recent_reps:
            return {
                "period_days": days,
                "total_workouts": 0,
                "total_reps": 0,
                "form_improvement": 0.0,
                "strength_improvement": 0.0,
                "consistency_score": 0.0,
                "recommendations": ["Start tracking your workouts to see progress"]
            }
        
        # Group by exercise and analyze progress
        exercise_progress = {}
        for rep in recent_reps:
            if rep.exercise_name not in exercise_progress:
                exercise_progress[rep.exercise_name] = []
            exercise_progress[rep.exercise_name].append(rep)
        
        # Calculate improvements
        form_improvement = self._calculate_form_improvement(recent_reps)
        strength_improvement = self._calculate_strength_improvement(recent_reps)
        consistency_score = self._calculate_consistency_score(recent_reps)
        
        # Generate recommendations
        recommendations = self._generate_progress_recommendations(
            form_improvement, strength_improvement, consistency_score
        )
        
        return {
            "period_days": days,
            "total_workouts": len(set(rep.session_id for rep in recent_reps)),
            "total_reps": len(recent_reps),
            "form_improvement": form_improvement,
            "strength_improvement": strength_improvement,
            "consistency_score": consistency_score,
            "exercise_breakdown": {
                exercise: len(reps) for exercise, reps in exercise_progress.items()
            },
            "recommendations": recommendations
        }
    
    def _analyze_form_trend(self, reps: List[RepLog]) -> str:
        """Analyze form trend over time"""
        if len(reps) < 5:
            return "insufficient_data"
        
        # Sort by creation time
        sorted_reps = sorted(reps, key=lambda x: x.created_at)
        
        # Split into early and late periods
        mid_point = len(sorted_reps) // 2
        early_reps = sorted_reps[:mid_point]
        late_reps = sorted_reps[mid_point:]
        
        # Calculate average form scores
        early_scores = [rep.form_score for rep in early_reps if rep.form_score is not None]
        late_scores = [rep.form_score for rep in late_reps if rep.form_score is not None]
        
        if not early_scores or not late_scores:
            return "insufficient_data"
        
        early_avg = np.mean(early_scores)
        late_avg = np.mean(late_scores)
        
        # Determine trend
        if late_avg > early_avg + 0.1:
            return "improving"
        elif late_avg < early_avg - 0.1:
            return "declining"
        else:
            return "stable"
    
    def _analyze_strength_progress(self, reps: List[RepLog]) -> Dict[str, float]:
        """Analyze strength progress by exercise"""
        strength_progress = {}
        
        # Group by exercise
        exercise_groups = {}
        for rep in reps:
            if rep.exercise_name not in exercise_groups:
                exercise_groups[rep.exercise_name] = []
            exercise_groups[rep.exercise_name].append(rep)
        
        # Calculate progress for each exercise
        for exercise, exercise_reps in exercise_groups.items():
            weights = [rep.weight_kg for rep in exercise_reps if rep.weight_kg is not None]
            if len(weights) >= 2:
                # Calculate percentage increase from first to last workout
                sorted_weights = sorted(weights)
                first_weight = sorted_weights[0]
                last_weight = sorted_weights[-1]
                
                if first_weight > 0:
                    progress = ((last_weight - first_weight) / first_weight) * 100
                    strength_progress[exercise] = round(progress, 1)
        
        return strength_progress
    
    def _calculate_volume_progression(self, reps: List[RepLog]) -> List[float]:
        """Calculate volume progression over time"""
        if len(reps) < 2:
            return []
        
        # Sort by creation time
        sorted_reps = sorted(reps, key=lambda x: x.created_at)
        
        # Calculate volume for each set (weight * reps)
        volumes = []
        for rep in sorted_reps:
            if rep.weight_kg and rep.rep_number:
                volume = rep.weight_kg * rep.rep_number
                volumes.append(volume)
        
        return volumes
    
    def _calculate_form_improvement(self, reps: List[RepLog]) -> float:
        """Calculate form improvement percentage"""
        if len(reps) < 10:
            return 0.0
        
        # Sort by time and split into quarters
        sorted_reps = sorted(reps, key=lambda x: x.created_at)
        quarter_size = len(sorted_reps) // 4
        
        if quarter_size < 2:
            return 0.0
        
        # Calculate average form scores for first and last quarters
        first_quarter = sorted_reps[:quarter_size]
        last_quarter = sorted_reps[-quarter_size:]
        
        first_scores = [rep.form_score for rep in first_quarter if rep.form_score is not None]
        last_scores = [rep.form_score for rep in last_quarter if rep.form_score is not None]
        
        if not first_scores or not last_scores:
            return 0.0
        
        first_avg = np.mean(first_scores)
        last_avg = np.mean(last_scores)
        
        if first_avg > 0:
            improvement = ((last_avg - first_avg) / first_avg) * 100
            return round(improvement, 1)
        
        return 0.0
    
    def _calculate_strength_improvement(self, reps: List[RepLog]) -> float:
        """Calculate strength improvement percentage"""
        if len(reps) < 10:
            return 0.0
        
        # Group by exercise and calculate max weight improvements
        exercise_max_weights = {}
        for rep in reps:
            if rep.weight_kg is not None:
                if rep.exercise_name not in exercise_max_weights:
                    exercise_max_weights[rep.exercise_name] = []
                exercise_max_weights[rep.exercise_name].append(rep.weight_kg)
        
        total_improvement = 0.0
        exercise_count = 0
        
        for exercise, weights in exercise_max_weights.items():
            if len(weights) >= 2:
                sorted_weights = sorted(weights)
                first_weight = sorted_weights[0]
                last_weight = sorted_weights[-1]
                
                if first_weight > 0:
                    improvement = ((last_weight - first_weight) / first_weight) * 100
                    total_improvement += improvement
                    exercise_count += 1
        
        if exercise_count > 0:
            return round(total_improvement / exercise_count, 1)
        
        return 0.0
    
    def _calculate_consistency_score(self, reps: List[RepLog]) -> float:
        """Calculate workout consistency score"""
        if not reps:
            return 0.0
        
        # Group by date
        dates = set(rep.created_at.date() for rep in reps)
        total_days = len(dates)
        
        # Calculate average reps per workout day
        avg_reps_per_day = len(reps) / total_days if total_days > 0 else 0
        
        # Simple consistency score (can be enhanced)
        if avg_reps_per_day >= 20:
            return 100.0
        elif avg_reps_per_day >= 15:
            return 80.0
        elif avg_reps_per_day >= 10:
            return 60.0
        elif avg_reps_per_day >= 5:
            return 40.0
        else:
            return 20.0
    
    def _generate_workout_recommendations(self, form_score: float, ego_percentage: float, form_trend: str) -> List[str]:
        """Generate workout recommendations"""
        recommendations = []
        
        if form_score < 0.6:
            recommendations.append("Focus on improving form before increasing weight")
        
        if ego_percentage > 0.2:
            recommendations.append("Reduce ego-lifting - prioritize form over weight")
        
        if form_trend == "declining":
            recommendations.append("Form is declining - consider reducing intensity")
        elif form_trend == "improving":
            recommendations.append("Great form improvement! Consider progressive overload")
        
        if form_score > 0.8 and ego_percentage < 0.1:
            recommendations.append("Excellent form! Ready to increase weight safely")
        
        return recommendations
    
    def _generate_exercise_recommendations(self, exercise: str, form_score: float, avg_weight: float, form_trend: str) -> List[str]:
        """Generate exercise-specific recommendations"""
        recommendations = []
        
        if form_score < 0.6:
            recommendations.append(f"Focus on {exercise} form - consider reducing weight")
        
        if form_trend == "declining":
            recommendations.append(f"{exercise} form is declining - review technique")
        
        if form_score > 0.8:
            recommendations.append(f"Great {exercise} form! Consider increasing weight")
        
        # Exercise-specific recommendations
        if "squat" in exercise.lower():
            recommendations.append("Keep chest up and knees in line with toes")
        elif "deadlift" in exercise.lower():
            recommendations.append("Maintain neutral spine throughout the movement")
        elif "bench" in exercise.lower():
            recommendations.append("Keep shoulder blades retracted and feet flat")
        
        return recommendations
    
    def _generate_progress_recommendations(self, form_improvement: float, strength_improvement: float, consistency: float) -> List[str]:
        """Generate progress-based recommendations"""
        recommendations = []
        
        if consistency < 50:
            recommendations.append("Increase workout consistency for better results")
        
        if form_improvement < 0:
            recommendations.append("Focus on form improvement - consider working with a trainer")
        
        if strength_improvement < 5:
            recommendations.append("Consider progressive overload to improve strength")
        
        if form_improvement > 10 and strength_improvement > 10:
            recommendations.append("Excellent progress! Keep up the great work")
        
        return recommendations 