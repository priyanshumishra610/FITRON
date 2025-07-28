"""
FITRON Logging Utility
Consistent logging configuration across the application
"""

import logging
import sys
from typing import Optional
from datetime import datetime
import os

def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Setup logger with consistent configuration"""
    
    # Get logger
    logger = logging.getLogger(name)
    
    # Avoid adding handlers if they already exist
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = level or os.getenv("LOG_LEVEL", "INFO")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    log_file = os.getenv("LOG_FILE")
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger

def log_function_call(func_name: str, **kwargs):
    """Decorator to log function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = setup_logger(f"{func.__module__}.{func.__name__}")
            logger.info(f"Calling {func_name} with args: {args}, kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"{func_name} completed successfully")
                return result
            except Exception as e:
                logger.error(f"{func_name} failed with error: {e}")
                raise
        return wrapper
    return decorator

def log_performance(func_name: str):
    """Decorator to log function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = setup_logger(f"{func.__module__}.{func.__name__}")
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.info(f"{func_name} completed in {duration:.3f} seconds")
                return result
            except Exception as e:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.error(f"{func_name} failed after {duration:.3f} seconds with error: {e}")
                raise
        return wrapper
    return decorator

class FITRONLogger:
    """Custom logger class for FITRON-specific logging"""
    
    def __init__(self, name: str):
        self.logger = setup_logger(name)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(message, extra=kwargs)
    
    def log_user_action(self, user_id: int, action: str, details: dict = None):
        """Log user-specific actions"""
        log_data = {
            "user_id": user_id,
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        self.logger.info(f"User action: {action}", extra=log_data)
    
    def log_workout_session(self, user_id: int, session_id: str, exercise_type: str, rep_count: int):
        """Log workout session data"""
        log_data = {
            "user_id": user_id,
            "session_id": session_id,
            "exercise_type": exercise_type,
            "rep_count": rep_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info(f"Workout session: {exercise_type} - {rep_count} reps", extra=log_data)
    
    def log_pose_analysis(self, user_id: int, exercise_type: str, form_score: float, is_ego_lifting: bool):
        """Log pose analysis results"""
        log_data = {
            "user_id": user_id,
            "exercise_type": exercise_type,
            "form_score": form_score,
            "is_ego_lifting": is_ego_lifting,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info(f"Pose analysis: {exercise_type} - Form: {form_score}, Ego-lifting: {is_ego_lifting}", extra=log_data)
    
    def log_physique_goal(self, user_id: int, goal_name: str, target_celebrity: str = None):
        """Log physique goal creation"""
        log_data = {
            "user_id": user_id,
            "goal_name": goal_name,
            "target_celebrity": target_celebrity,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info(f"Physique goal created: {goal_name}", extra=log_data)
    
    def log_safety_alert(self, user_id: int, alert_type: str, severity: str, message: str):
        """Log safety alerts"""
        log_data = {
            "user_id": user_id,
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.warning(f"Safety alert: {alert_type} - {message}", extra=log_data) 