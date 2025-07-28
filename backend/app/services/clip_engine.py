"""
FITRON CLIP Engine Service
Physique analysis and comparison using CLIP embeddings
"""

import torch
import clip
import numpy as np
from PIL import Image
import requests
from io import BytesIO
from typing import List, Dict, Tuple, Optional, Any
import json
import os
from dataclasses import dataclass
import logging

from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class CelebrityPhysique:
    """Celebrity physique reference"""
    name: str
    category: str
    image_url: str
    embedding: List[float]
    description: str
    difficulty_level: str
    target_metrics: Dict[str, float]

@dataclass
class PhysiqueComparison:
    """Physique comparison result"""
    similarity_score: float
    celebrity_name: str
    category: str
    difficulty_level: str
    recommendations: List[str]
    estimated_time: int  # days

class CLIPEngine:
    """CLIP engine for physique analysis and comparison"""
    
    def __init__(self):
        """Initialize CLIP model"""
        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)
            logger.info(f"✅ CLIP model loaded successfully on {self.device}")
            
            # Load celebrity physique database
            self.celebrity_physiques = self._load_celebrity_database()
            
        except Exception as e:
            logger.error(f"❌ CLIP model initialization failed: {e}")
            raise
    
    def _load_celebrity_database(self) -> List[CelebrityPhysique]:
        """Load celebrity physique database"""
        # This would typically be loaded from a database or JSON file
        # For now, creating a sample database
        celebrities = [
            CelebrityPhysique(
                name="Arnold Schwarzenegger",
                category="bodybuilder",
                image_url="https://example.com/arnold.jpg",
                embedding=[],  # Would be pre-computed
                description="Classic bodybuilding physique with massive muscle mass",
                difficulty_level="expert",
                target_metrics={
                    "body_fat_percentage": 8.0,
                    "muscle_mass_kg": 85.0,
                    "weight_kg": 105.0
                }
            ),
            CelebrityPhysique(
                name="Bruce Lee",
                category="lean",
                image_url="https://example.com/bruce.jpg",
                embedding=[],
                description="Lean, functional physique with low body fat",
                difficulty_level="hard",
                target_metrics={
                    "body_fat_percentage": 6.0,
                    "muscle_mass_kg": 65.0,
                    "weight_kg": 68.0
                }
            ),
            CelebrityPhysique(
                name="Dwayne Johnson",
                category="athletic",
                image_url="https://example.com/rock.jpg",
                embedding=[],
                description="Athletic build with balanced muscle mass",
                difficulty_level="hard",
                target_metrics={
                    "body_fat_percentage": 12.0,
                    "muscle_mass_kg": 75.0,
                    "weight_kg": 118.0
                }
            ),
            CelebrityPhysique(
                name="Salman Khan",
                category="athletic",
                image_url="https://example.com/salman.jpg",
                embedding=[],
                description="Bollywood athletic physique",
                difficulty_level="medium",
                target_metrics={
                    "body_fat_percentage": 10.0,
                    "muscle_mass_kg": 70.0,
                    "weight_kg": 80.0
                }
            )
        ]
        
        return celebrities
    
    def encode_image(self, image_path: str) -> Optional[List[float]]:
        """Encode image to CLIP embedding"""
        try:
            # Load and preprocess image
            if image_path.startswith('http'):
                response = requests.get(image_path)
                image = Image.open(BytesIO(response.content))
            else:
                image = Image.open(image_path)
            
            # Preprocess image
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            
            # Encode image
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                embedding = image_features.cpu().numpy().flatten().tolist()
            
            return embedding
            
        except Exception as e:
            logger.error(f"Image encoding error: {e}")
            return None
    
    def encode_text(self, text: str) -> Optional[List[float]]:
        """Encode text to CLIP embedding"""
        try:
            # Tokenize text
            text_input = clip.tokenize([text]).to(self.device)
            
            # Encode text
            with torch.no_grad():
                text_features = self.model.encode_text(text_input)
                embedding = text_features.cpu().numpy().flatten().tolist()
            
            return embedding
            
        except Exception as e:
            logger.error(f"Text encoding error: {e}")
            return None
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Normalize vectors
            vec1_norm = vec1 / np.linalg.norm(vec1)
            vec2_norm = vec2 / np.linalg.norm(vec2)
            
            # Calculate cosine similarity
            similarity = np.dot(vec1_norm, vec2_norm)
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Similarity calculation error: {e}")
            return 0.0
    
    def find_similar_physiques(self, user_embedding: List[float], 
                             top_k: int = 5) -> List[PhysiqueComparison]:
        """Find similar physiques from celebrity database"""
        try:
            similarities = []
            
            for celebrity in self.celebrity_physiques:
                if celebrity.embedding:  # Skip if embedding not available
                    similarity = self.calculate_similarity(user_embedding, celebrity.embedding)
                    similarities.append((similarity, celebrity))
            
            # Sort by similarity score
            similarities.sort(key=lambda x: x[0], reverse=True)
            
            # Return top k results
            results = []
            for similarity, celebrity in similarities[:top_k]:
                comparison = PhysiqueComparison(
                    similarity_score=similarity,
                    celebrity_name=celebrity.name,
                    category=celebrity.category,
                    difficulty_level=celebrity.difficulty_level,
                    recommendations=self._generate_recommendations(celebrity, similarity),
                    estimated_time=self._estimate_time_to_goal(celebrity, similarity)
                )
                results.append(comparison)
            
            return results
            
        except Exception as e:
            logger.error(f"Physique comparison error: {e}")
            return []
    
    def analyze_physique_goal(self, current_image_url: str, 
                            target_celebrity: str) -> Optional[Dict[str, Any]]:
        """Analyze user's current physique against target celebrity"""
        try:
            # Encode current physique
            current_embedding = self.encode_image(current_image_url)
            if not current_embedding:
                return None
            
            # Find target celebrity
            target_celeb = None
            for celeb in self.celebrity_physiques:
                if celeb.name.lower() == target_celebrity.lower():
                    target_celeb = celeb
                    break
            
            if not target_celeb or not target_celeb.embedding:
                return None
            
            # Calculate similarity
            similarity = self.calculate_similarity(current_embedding, target_celeb.embedding)
            
            # Generate analysis
            analysis = {
                "current_similarity": similarity,
                "target_celebrity": target_celeb.name,
                "category": target_celeb.category,
                "difficulty_level": target_celeb.difficulty_level,
                "target_metrics": target_celeb.target_metrics,
                "estimated_time_days": self._estimate_time_to_goal(target_celeb, similarity),
                "recommendations": self._generate_recommendations(target_celeb, similarity),
                "progress_percentage": self._calculate_progress_percentage(similarity),
                "confidence": self._calculate_confidence(similarity)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Physique goal analysis error: {e}")
            return None
    
    def generate_workout_plan(self, target_celebrity: str, 
                            user_fitness_level: str) -> Optional[Dict[str, Any]]:
        """Generate workout plan based on target celebrity"""
        try:
            # Find target celebrity
            target_celeb = None
            for celeb in self.celebrity_physiques:
                if celeb.name.lower() == target_celebrity.lower():
                    target_celeb = celeb
                    break
            
            if not target_celeb:
                return None
            
            # Generate workout plan based on category and difficulty
            workout_plan = self._create_workout_plan(target_celeb, user_fitness_level)
            
            return workout_plan
            
        except Exception as e:
            logger.error(f"Workout plan generation error: {e}")
            return None
    
    def _generate_recommendations(self, celebrity: CelebrityPhysique, 
                                similarity: float) -> List[str]:
        """Generate recommendations based on celebrity and similarity"""
        recommendations = []
        
        if similarity < 0.3:
            recommendations.extend([
                "Focus on building foundational strength",
                "Start with compound movements",
                "Establish consistent training routine",
                "Work on nutrition fundamentals"
            ])
        elif similarity < 0.6:
            recommendations.extend([
                "Increase training intensity",
                "Focus on muscle hypertrophy",
                "Optimize nutrition for muscle growth",
                "Add progressive overload"
            ])
        else:
            recommendations.extend([
                "Fine-tune specific muscle groups",
                "Optimize body composition",
                "Advanced training techniques",
                "Precision nutrition planning"
            ])
        
        # Add category-specific recommendations
        if celebrity.category == "bodybuilder":
            recommendations.append("Focus on muscle isolation exercises")
        elif celebrity.category == "lean":
            recommendations.append("Emphasize cardio and fat loss")
        elif celebrity.category == "athletic":
            recommendations.append("Balance strength and conditioning")
        
        return recommendations
    
    def _estimate_time_to_goal(self, celebrity: CelebrityPhysique, 
                              similarity: float) -> int:
        """Estimate time to reach goal physique (in days)"""
        base_time = {
            "easy": 90,
            "medium": 180,
            "hard": 365,
            "expert": 730
        }
        
        difficulty_time = base_time.get(celebrity.difficulty_level, 180)
        
        # Adjust based on current similarity
        if similarity > 0.8:
            return max(30, int(difficulty_time * 0.2))
        elif similarity > 0.6:
            return max(60, int(difficulty_time * 0.4))
        elif similarity > 0.4:
            return max(120, int(difficulty_time * 0.6))
        else:
            return difficulty_time
    
    def _calculate_progress_percentage(self, similarity: float) -> float:
        """Calculate progress percentage based on similarity"""
        # Assuming 0.8+ similarity is considered "goal achieved"
        return min(100.0, (similarity / 0.8) * 100)
    
    def _calculate_confidence(self, similarity: float) -> float:
        """Calculate confidence in analysis"""
        # Higher similarity = higher confidence
        return min(1.0, similarity * 1.25)
    
    def _create_workout_plan(self, celebrity: CelebrityPhysique, 
                           user_fitness_level: str) -> Dict[str, Any]:
        """Create workout plan based on celebrity and user level"""
        # This would be a more sophisticated implementation
        # For now, returning a basic template
        
        workout_plan = {
            "celebrity": celebrity.name,
            "category": celebrity.category,
            "difficulty_level": celebrity.difficulty_level,
            "user_fitness_level": user_fitness_level,
            "weekly_schedule": {
                "monday": ["compound_lifts", "strength_training"],
                "tuesday": ["cardio", "conditioning"],
                "wednesday": ["muscle_isolation", "hypertrophy"],
                "thursday": ["rest", "recovery"],
                "friday": ["compound_lifts", "strength_training"],
                "saturday": ["cardio", "conditioning"],
                "sunday": ["rest", "recovery"]
            },
            "focus_areas": self._get_focus_areas(celebrity.category),
            "nutrition_guidelines": self._get_nutrition_guidelines(celebrity.category),
            "estimated_duration_weeks": self._get_estimated_duration(celebrity.difficulty_level)
        }
        
        return workout_plan
    
    def _get_focus_areas(self, category: str) -> List[str]:
        """Get focus areas based on physique category"""
        focus_areas = {
            "bodybuilder": ["muscle_hypertrophy", "symmetry", "definition"],
            "lean": ["fat_loss", "muscle_definition", "endurance"],
            "athletic": ["strength", "power", "conditioning"],
            "functional": ["mobility", "stability", "movement_patterns"]
        }
        return focus_areas.get(category, ["general_fitness"])
    
    def _get_nutrition_guidelines(self, category: str) -> Dict[str, Any]:
        """Get nutrition guidelines based on category"""
        guidelines = {
            "bodybuilder": {
                "protein_ratio": 0.3,
                "carbs_ratio": 0.4,
                "fat_ratio": 0.3,
                "calorie_surplus": True
            },
            "lean": {
                "protein_ratio": 0.35,
                "carbs_ratio": 0.35,
                "fat_ratio": 0.3,
                "calorie_deficit": True
            },
            "athletic": {
                "protein_ratio": 0.25,
                "carbs_ratio": 0.5,
                "fat_ratio": 0.25,
                "calorie_maintenance": True
            }
        }
        return guidelines.get(category, {"protein_ratio": 0.3, "carbs_ratio": 0.4, "fat_ratio": 0.3})
    
    def _get_estimated_duration(self, difficulty_level: str) -> int:
        """Get estimated duration in weeks"""
        durations = {
            "easy": 12,
            "medium": 24,
            "hard": 48,
            "expert": 96
        }
        return durations.get(difficulty_level, 24)

# Global instance
clip_engine = CLIPEngine() 