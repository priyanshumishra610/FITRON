"""
FITRON Helper Utilities
Common utility functions for the application
"""

import hashlib
import uuid
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import base64
from pathlib import Path

def generate_session_id() -> str:
    """Generate a unique session ID"""
    return str(uuid.uuid4())

def generate_secure_token() -> str:
    """Generate a secure random token"""
    return hashlib.sha256(uuid.uuid4().bytes).hexdigest()

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    result = {
        "is_valid": True,
        "errors": [],
        "score": 0
    }
    
    if len(password) < 8:
        result["errors"].append("Password must be at least 8 characters long")
        result["is_valid"] = False
    
    if not re.search(r'[A-Z]', password):
        result["errors"].append("Password must contain at least one uppercase letter")
        result["is_valid"] = False
    
    if not re.search(r'[a-z]', password):
        result["errors"].append("Password must contain at least one lowercase letter")
        result["is_valid"] = False
    
    if not re.search(r'\d', password):
        result["errors"].append("Password must contain at least one number")
        result["is_valid"] = False
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        result["errors"].append("Password must contain at least one special character")
        result["is_valid"] = False
    
    # Calculate strength score
    score = 0
    if len(password) >= 8:
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'\d', password):
        score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    if len(password) >= 12:
        score += 1
    
    result["score"] = score
    
    return result

def calculate_age(birth_date: datetime) -> int:
    """Calculate age from birth date"""
    today = datetime.now()
    age = today.year - birth_date.year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    return age

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def format_weight(weight_kg: float) -> str:
    """Format weight in kg to human readable string"""
    if weight_kg < 1:
        return f"{weight_kg * 1000:.0f}g"
    else:
        return f"{weight_kg:.1f}kg"

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI from weight and height"""
    if height_cm <= 0:
        return 0
    height_m = height_cm / 100
    return weight_kg / (height_m ** 2)

def get_bmi_category(bmi: float) -> str:
    """Get BMI category"""
    if bmi < 18.5:
        return "underweight"
    elif bmi < 25:
        return "normal"
    elif bmi < 30:
        return "overweight"
    else:
        return "obese"

def calculate_rmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Calculate Resting Metabolic Rate using Mifflin-St Jeor Equation"""
    if gender.lower() == "male":
        rmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        rmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    
    return rmr

def calculate_tdee(rmr: float, activity_level: str) -> float:
    """Calculate Total Daily Energy Expenditure"""
    activity_multipliers = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725,
        "extremely_active": 1.9
    }
    
    multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
    return rmr * multiplier

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    return filename

def create_file_path(base_path: str, filename: str, user_id: int) -> str:
    """Create organized file path for user uploads"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized_filename = sanitize_filename(filename)
    return f"{base_path}/{user_id}/{timestamp}_{sanitized_filename}"

def encode_base64(data: bytes) -> str:
    """Encode bytes to base64 string"""
    return base64.b64encode(data).decode('utf-8')

def decode_base64(data: str) -> bytes:
    """Decode base64 string to bytes"""
    return base64.b64decode(data.encode('utf-8'))

def safe_json_dumps(obj: Any) -> str:
    """Safely serialize object to JSON string"""
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return json.dumps({"error": "Could not serialize object"})

def safe_json_loads(data: str) -> Any:
    """Safely deserialize JSON string to object"""
    try:
        return json.loads(data)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def flatten_list(lst: List[List[Any]]) -> List[Any]:
    """Flatten nested list"""
    return [item for sublist in lst for item in sublist]

def remove_duplicates(lst: List[Any]) -> List[Any]:
    """Remove duplicates from list while preserving order"""
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries, dict2 takes precedence"""
    result = dict1.copy()
    result.update(dict2)
    return result

def get_nested_value(data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    """Get nested dictionary value using key path"""
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

def set_nested_value(data: Dict[str, Any], keys: List[str], value: Any) -> Dict[str, Any]:
    """Set nested dictionary value using key path"""
    current = data
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value
    return data

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency"""
    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥"
    }
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol}{amount:.2f}"

def format_percentage(value: float, total: float) -> str:
    """Format value as percentage of total"""
    if total == 0:
        return "0%"
    percentage = (value / total) * 100
    return f"{percentage:.1f}%"

def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    # Basic phone number validation (can be enhanced)
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None

def mask_sensitive_data(data: str, mask_char: str = "*") -> str:
    """Mask sensitive data like email or phone number"""
    if "@" in data:  # Email
        parts = data.split("@")
        if len(parts) == 2:
            username = parts[0]
            domain = parts[1]
            if len(username) > 2:
                masked_username = username[:2] + mask_char * (len(username) - 2)
            else:
                masked_username = mask_char * len(username)
            return f"{masked_username}@{domain}"
    else:  # Phone number
        if len(data) > 4:
            return mask_char * (len(data) - 4) + data[-4:]
        else:
            return mask_char * len(data)
    
    return data

def generate_workout_id() -> str:
    """Generate unique workout session ID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = str(uuid.uuid4())[:8]
    return f"workout_{timestamp}_{random_suffix}"

def calculate_workout_duration(start_time: datetime, end_time: datetime) -> float:
    """Calculate workout duration in minutes"""
    duration = end_time - start_time
    return duration.total_seconds() / 60

def estimate_calories_burned(exercise_type: str, duration_minutes: float, weight_kg: float) -> float:
    """Estimate calories burned during exercise"""
    # MET values for different exercises (Metabolic Equivalent of Task)
    met_values = {
        "squat": 5.0,
        "deadlift": 6.0,
        "bench_press": 3.5,
        "pull_up": 8.0,
        "push_up": 3.8,
        "running": 8.0,
        "cycling": 6.0,
        "swimming": 7.0,
        "walking": 3.5
    }
    
    met = met_values.get(exercise_type.lower(), 4.0)
    calories = (met * weight_kg * duration_minutes) / 60
    return round(calories, 1) 