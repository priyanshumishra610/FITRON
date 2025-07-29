"""
FITRON - AI Fitness OS
Main FastAPI Application Entry Point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.db import init_db
from app.api import routes, auth, rep_tracking, auto_regulation, physique_goal, chatbot
from app.utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting FITRON AI Fitness OS...")
    await init_db()
    logger.info("✅ Database initialized")
    logger.info("✅ FITRON is ready to track your gains!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down FITRON...")

# Initialize FastAPI app
app = FastAPI(
    title="FITRON AI Fitness OS",
    description="The world's first AI-powered fitness OS - Track every rep, detect bad form, map your goal physique",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(rep_tracking.router, prefix="/api/v1/rep-tracking", tags=["Rep Tracking"])
app.include_router(auto_regulation.router, prefix="/api/v1/auto-regulation", tags=["Auto Regulation"])
app.include_router(physique_goal.router, prefix="/api/v1/physique-goal", tags=["Physique Goal"])
app.include_router(chatbot.router, prefix="/api/v1/chatbot", tags=["AI Coach Chatbot"])
app.include_router(routes.router, prefix="/api/v1", tags=["General"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🏋️‍♂️ Welcome to FITRON - The AI Fitness OS",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "FITRON AI Fitness OS",
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    ) 