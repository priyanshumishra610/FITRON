"""
FITRON Configuration Settings
Environment variables and app configuration
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """FITRON application settings"""
    
    # App Configuration
    APP_NAME: str = "FITRON AI Fitness OS"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "fitron-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS & Security
    ALLOWED_HOSTS: List[str] = ["*"]
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8000"
    ]
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://fitron:fitron@localhost:5432/fitron"
    MONGODB_URL: str = "mongodb://localhost:27017/fitron"
    
    # Redis for caching and real-time features
    REDIS_URL: str = "redis://localhost:6379"
    
    # External APIs
    OPENAI_API_KEY: Optional[str] = None
    CLIP_MODEL_PATH: str = "models/clip-vit-base-patch32"
    
    # Computer Vision Models
    YOLO_MODEL_PATH: str = "models/yolov8n-pose.pt"
    MEDIAPIPE_MODEL_PATH: str = "models/mediapipe_pose"
    SAM_MODEL_PATH: str = "models/sam_vit_h_4b8939.pth"
    
    # File Storage
    S3_BUCKET_NAME: str = "fitron-assets"
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_REGION: str = "us-east-1"
    
    # ZenML Configuration
    ZENML_STACK_NAME: str = "fitron-stack"
    ZENML_PIPELINE_NAME: str = "fitron-adaptive-pipeline"
    
    # Analytics
    POSTHOG_API_KEY: Optional[str] = None
    POSTHOG_HOST: str = "https://app.posthog.com"
    
    # Firebase (for mobile push notifications)
    FIREBASE_CREDENTIALS_PATH: str = "config/firebase-credentials.json"
    
    # Socket.io
    SOCKET_CORS_ORIGINS: List[str] = ["*"]
    
    # Rep Tracking Configuration
    MIN_REP_CONFIDENCE: float = 0.7
    MAX_REP_DURATION: float = 10.0  # seconds
    EGO_LIFTING_THRESHOLD: float = 0.8
    
    # Physique Goal Configuration
    CLIP_SIMILARITY_THRESHOLD: float = 0.75
    MAX_GOAL_PHYSIQUES: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings() 