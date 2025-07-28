"""
FITRON Demo Server
Simple FastAPI server for demonstration purposes
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
from datetime import datetime, timedelta
import uuid

# Pydantic models
class User(BaseModel):
    id: str
    email: str
    name: str
    created_at: str
    subscription_tier: str = "free"

class RepLog(BaseModel):
    id: str
    user_id: str
    exercise_name: str
    set_number: int
    rep_number: int
    weight: float
    reps: int
    timestamp: str
    form_score: Optional[float] = None
    form_feedback: Optional[str] = None

class PhysiqueGoal(BaseModel):
    id: str
    user_id: str
    goal_name: str
    description: str
    celebrity_reference: Optional[str] = None
    target_date: str
    status: str = "active"
    progress: float = 0.0

class CelebrityAnalysisRequest(BaseModel):
    celebrity_name: str

# Initialize FastAPI app
app = FastAPI(
    title="FITRON AI Fitness OS - Demo",
    description="Demo version of the world's first AI-powered fitness OS",
    version="1.0.0-demo"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data storage
users_db = {}
rep_logs_db = []
physique_goals_db = []

# Initialize with demo data
def init_demo_data():
    # Demo user
    demo_user = User(
        id="demo-user-123",
        email="demo@fitron.ai",
        name="Demo User",
        created_at=datetime.now().isoformat(),
        subscription_tier="pro"
    )
    users_db[demo_user.id] = demo_user
    
    # Demo rep logs
    exercises = ["Bench Press", "Squat", "Deadlift", "Pull-ups"]
    for i in range(20):
        rep_log = RepLog(
            id=str(uuid.uuid4()),
            user_id=demo_user.id,
            exercise_name=exercises[i % len(exercises)],
            set_number=(i // 4) + 1,
            rep_number=(i % 4) + 1,
            weight=100.0 + (i * 5),
            reps=8 + (i % 4),
            timestamp=(datetime.now() - timedelta(days=i)).isoformat(),
            form_score=0.85 + (i * 0.01),
            form_feedback="Good form, keep it up!" if i % 3 == 0 else None
        )
        rep_logs_db.append(rep_log)
    
    # Demo physique goals
    goals = [
        PhysiqueGoal(
            id=str(uuid.uuid4()),
            user_id=demo_user.id,
            goal_name="Arnold Schwarzenegger Physique",
            description="Build massive chest and arms like Arnold",
            celebrity_reference="Arnold Schwarzenegger",
            target_date=(datetime.now() + timedelta(days=365)).isoformat(),
            progress=0.35
        ),
        PhysiqueGoal(
            id=str(uuid.uuid4()),
            user_id=demo_user.id,
            goal_name="Bruce Lee Core",
            description="Develop functional core strength like Bruce Lee",
            celebrity_reference="Bruce Lee",
            target_date=(datetime.now() + timedelta(days=180)).isoformat(),
            progress=0.65
        )
    ]
    physique_goals_db.extend(goals)

# Initialize demo data
init_demo_data()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🏋️‍♂️ Welcome to FITRON - The AI Fitness OS (Demo)",
        "version": "1.0.0-demo",
        "status": "active",
        "docs": "/docs",
        "features": [
            "Real-time rep tracking",
            "AI form analysis",
            "Celebrity physique mapping",
            "Auto-regulation system"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "FITRON AI Fitness OS - Demo",
        "timestamp": datetime.now().isoformat(),
        "users_count": len(users_db),
        "rep_logs_count": len(rep_logs_db),
        "goals_count": len(physique_goals_db)
    }

# Authentication endpoints
@app.post("/api/v1/auth/login")
async def login(email: str, password: str):
    """Demo login endpoint"""
    if email == "demo@fitron.ai" and password == "demo123":
        return {
            "access_token": "demo-token-123",
            "token_type": "bearer",
            "user": users_db["demo-user-123"].dict()
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/v1/auth/profile")
async def get_profile():
    """Get user profile"""
    return users_db["demo-user-123"]

# Rep tracking endpoints
@app.get("/api/v1/rep-tracking/logs")
async def get_rep_logs(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Get rep logs"""
    return rep_logs_db

@app.post("/api/v1/rep-tracking/log")
async def log_rep(rep_log: RepLog):
    """Log a new rep"""
    rep_logs_db.append(rep_log)
    return rep_log

@app.post("/api/v1/rep-tracking/analyze-pose")
async def analyze_pose():
    """Demo pose analysis"""
    return {
        "form_score": 0.92,
        "feedback": "Excellent form! Keep your chest up and maintain depth.",
        "pose_data": {
            "knee_angle": 85.2,
            "hip_angle": 45.1,
            "back_angle": 15.3
        },
        "is_ego_lifting": False,
        "fatigue_indicators": {
            "velocity_decrease": 0.05,
            "form_deterioration": 0.02
        }
    }

# Auto-regulation endpoints
@app.get("/api/v1/auto-regulation/status")
async def get_auto_regulation_status():
    """Get auto-regulation status"""
    return {
        "is_locked": False,
        "reason": None,
        "recommendations": [
            "Your form is excellent, keep it up!",
            "Consider increasing weight by 5-10 lbs",
            "Focus on controlled eccentric movements"
        ],
        "risk_score": 0.15
    }

@app.post("/api/v1/auto-regulation/override")
async def override_auto_regulation(reason: str):
    """Override auto-regulation"""
    return {
        "override_granted": True,
        "reason": reason,
        "timestamp": datetime.now().isoformat(),
        "warning": "Proceed with caution and maintain proper form"
    }

# Physique goals endpoints
@app.get("/api/v1/physique-goals/list")
async def get_physique_goals():
    """Get physique goals"""
    return physique_goals_db

@app.post("/api/v1/physique-goals/create")
async def create_physique_goal(goal: PhysiqueGoal):
    """Create a new physique goal"""
    physique_goals_db.append(goal)
    return goal

@app.post("/api/v1/physique-goals/analyze-celebrity")
async def analyze_celebrity_physique(request: CelebrityAnalysisRequest):
    """Analyze celebrity physique"""
    celebrities = {
        "arnold schwarzenegger": {
            "name": "Arnold Schwarzenegger",
            "physique_type": "bodybuilder",
            "muscle_groups": ["chest", "arms", "shoulders", "back"],
            "body_fat_percentage": 8,
            "training_style": "bodybuilding",
            "difficulty": "expert",
            "time_to_achieve": "3-5 years",
            "similarity_score": 0.85
        },
        "bruce lee": {
            "name": "Bruce Lee",
            "physique_type": "functional",
            "muscle_groups": ["core", "shoulders", "forearms"],
            "body_fat_percentage": 6,
            "training_style": "functional_fitness",
            "difficulty": "intermediate",
            "time_to_achieve": "1-2 years",
            "similarity_score": 0.78
        },
        "chris hemsworth": {
            "name": "Chris Hemsworth",
            "physique_type": "superhero",
            "muscle_groups": ["chest", "arms", "shoulders", "back", "core"],
            "body_fat_percentage": 10,
            "training_style": "functional_strength",
            "difficulty": "advanced",
            "time_to_achieve": "2-4 years",
            "similarity_score": 0.82
        }
    }
    
    celebrity_lower = request.celebrity_name.lower()
    if celebrity_lower in celebrities:
        return celebrities[celebrity_lower]
    else:
        return {
            "error": "Celebrity not found in database",
            "available_celebrities": list(celebrities.keys())
        }

# Analytics endpoints
@app.get("/api/v1/analytics/workout-stats")
async def get_workout_stats():
    """Get workout statistics"""
    return {
        "total_workouts": 15,
        "total_reps": 1200,
        "total_weight_lifted": 45000,
        "average_form_score": 0.87,
        "strength_progress": {
            "bench_press": "+25 lbs",
            "squat": "+40 lbs",
            "deadlift": "+35 lbs"
        },
        "weekly_progress": [
            {"week": 1, "reps": 80, "form_score": 0.82},
            {"week": 2, "reps": 85, "form_score": 0.84},
            {"week": 3, "reps": 90, "form_score": 0.86},
            {"week": 4, "reps": 95, "form_score": 0.88}
        ]
    }

@app.get("/api/v1/analytics/form-analysis")
async def get_form_analysis():
    """Get form analysis"""
    return {
        "overall_form_score": 0.87,
        "exercise_breakdown": {
            "bench_press": {"score": 0.89, "common_issues": ["Shoulder instability"]},
            "squat": {"score": 0.85, "common_issues": ["Knee tracking"]},
            "deadlift": {"score": 0.88, "common_issues": ["Back rounding"]},
            "pull_ups": {"score": 0.84, "common_issues": ["Incomplete range of motion"]}
        },
        "improvement_areas": [
            "Focus on full range of motion in pull-ups",
            "Maintain neutral spine in deadlifts",
            "Keep chest up in squats"
        ],
        "strengths": [
            "Excellent bench press form",
            "Good deadlift technique",
            "Consistent workout frequency"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 