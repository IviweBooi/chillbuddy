# ChillBuddy Mental Health Chatbot - Backend Utility Functions
#
# This file contains:
# - Common helper functions
# - Data validation utilities
# - Text processing helpers
# - Date/time utilities
# - Security and encryption helpers
# - API response formatting
# - Error handling utilities

import json
import re
import hashlib
import secrets
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Union, Tuple
from functools import wraps
from urllib.parse import urlparse
import bleach
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify, request
import uuid

logger = logging.getLogger(__name__)

# Text Processing Utilities

def clean_text(text: str) -> str:
    """Clean and sanitize user input"""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove potentially harmful characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Limit length to prevent abuse
    max_length = 5000
    if len(text) > max_length:
        text = text[:max_length]
    
    return text

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract important keywords from text"""
    if not text:
        return []
    
    # Simple keyword extraction (can be enhanced with NLP libraries)
    text = clean_text(text.lower())
    
    # Remove common stop words
    stop_words = {
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
        'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
        'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
        'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
        'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
        'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after',
        'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
        'further', 'then', 'once'
    }
    
    # Extract words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
    keywords = [word for word in words if word not in stop_words]
    
    # Count frequency and return most common
    word_freq = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_keywords[:max_keywords]]

def calculate_sentiment(text: str) -> Dict[str, Any]:
    """Basic sentiment analysis"""
    if not text:
        return {"sentiment": "neutral", "confidence": 0.0, "score": 0.0}
    
    # Simple sentiment analysis using keyword matching
    positive_words = {
        'happy', 'joy', 'excited', 'good', 'great', 'amazing', 'wonderful', 'fantastic',
        'excellent', 'positive', 'love', 'like', 'enjoy', 'pleased', 'satisfied',
        'grateful', 'thankful', 'hopeful', 'optimistic', 'confident', 'proud', 'calm',
        'peaceful', 'relaxed', 'content', 'cheerful', 'delighted', 'thrilled'
    }
    
    negative_words = {
        'sad', 'angry', 'upset', 'depressed', 'anxious', 'worried', 'stressed', 'frustrated',
        'disappointed', 'hurt', 'pain', 'suffering', 'terrible', 'awful', 'horrible',
        'hate', 'dislike', 'fear', 'scared', 'nervous', 'overwhelmed', 'hopeless',
        'lonely', 'isolated', 'tired', 'exhausted', 'confused', 'lost', 'helpless'
    }
    
    text_lower = text.lower()
    words = re.findall(r'\b[a-zA-Z]+\b', text_lower)
    
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    total_sentiment_words = positive_count + negative_count
    
    if total_sentiment_words == 0:
        return {"sentiment": "neutral", "confidence": 0.0, "score": 0.0}
    
    score = (positive_count - negative_count) / len(words) if words else 0
    confidence = total_sentiment_words / len(words) if words else 0
    
    if score > 0.1:
        sentiment = "positive"
    elif score < -0.1:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    return {
        "sentiment": sentiment,
        "confidence": min(confidence, 1.0),
        "score": max(-1.0, min(1.0, score * 10))  # Scale to -1 to 1
    }

def detect_language(text: str) -> str:
    """Detect text language (basic implementation)"""
    if not text:
        return "unknown"
    
    # Simple language detection based on common words
    english_indicators = ['the', 'and', 'is', 'are', 'was', 'were', 'have', 'has', 'will', 'would']
    afrikaans_indicators = ['die', 'en', 'is', 'was', 'het', 'van', 'in', 'op', 'met', 'vir']
    
    text_lower = text.lower()
    words = re.findall(r'\b[a-zA-Z]+\b', text_lower)
    
    english_count = sum(1 for word in words if word in english_indicators)
    afrikaans_count = sum(1 for word in words if word in afrikaans_indicators)
    
    if english_count > afrikaans_count:
        return "en"
    elif afrikaans_count > 0:
        return "af"
    else:
        return "en"  # Default to English

def normalize_text(text: str) -> str:
    """Normalize text for processing"""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove punctuation except sentence endings
    text = re.sub(r'[^\w\s\.\!\?]', '', text)
    
    return text

# Validation Utilities

def validate_user_input(input_data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate user input against schema"""
    errors = []
    
    if not isinstance(input_data, dict):
        return False, ["Input must be a dictionary"]
    
    # Check required fields
    required_fields = schema.get('required', [])
    for field in required_fields:
        if field not in input_data:
            errors.append(f"Missing required field: {field}")
    
    # Check field types and constraints
    properties = schema.get('properties', {})
    for field, constraints in properties.items():
        if field not in input_data:
            continue
        
        value = input_data[field]
        field_type = constraints.get('type')
        
        # Type validation
        if field_type == 'string' and not isinstance(value, str):
            errors.append(f"Field {field} must be a string")
        elif field_type == 'integer' and not isinstance(value, int):
            errors.append(f"Field {field} must be an integer")
        elif field_type == 'number' and not isinstance(value, (int, float)):
            errors.append(f"Field {field} must be a number")
        elif field_type == 'boolean' and not isinstance(value, bool):
            errors.append(f"Field {field} must be a boolean")
        
        # Length validation for strings
        if isinstance(value, str):
            min_length = constraints.get('minLength', 0)
            max_length = constraints.get('maxLength', float('inf'))
            if len(value) < min_length:
                errors.append(f"Field {field} must be at least {min_length} characters")
            if len(value) > max_length:
                errors.append(f"Field {field} must be at most {max_length} characters")
        
        # Range validation for numbers
        if isinstance(value, (int, float)):
            minimum = constraints.get('minimum')
            maximum = constraints.get('maximum')
            if minimum is not None and value < minimum:
                errors.append(f"Field {field} must be at least {minimum}")
            if maximum is not None and value > maximum:
                errors.append(f"Field {field} must be at most {maximum}")
    
    return len(errors) == 0, errors

def validate_email(email: str) -> bool:
    """Email format validation"""
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone_number(phone: str, country_code: str = "ZA") -> bool:
    """Phone number validation"""
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # South African phone number validation
    if country_code == "ZA":
        # Should be 10 digits (without country code) or 12 digits (with +27)
        if len(digits) == 10 and digits.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
            return True
        elif len(digits) == 11 and digits.startswith('27'):
            return True
    
    return False

def validate_json_structure(data: Any, required_fields: List[str]) -> Tuple[bool, List[str]]:
    """JSON structure validation"""
    errors = []
    
    if not isinstance(data, dict):
        return False, ["Data must be a JSON object"]
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    return len(errors) == 0, errors

def sanitize_html(html_content: str) -> str:
    """Remove potentially harmful HTML"""
    if not html_content:
        return ""
    
    # Allow only safe HTML tags
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li']
    allowed_attributes = {}
    
    return bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attributes, strip=True)

# Security Utilities

def generate_secure_token(length: int = 32) -> str:
    """Generate secure random tokens"""
    return secrets.token_urlsafe(length)

def hash_password(password: str) -> str:
    """Hash passwords securely"""
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return check_password_hash(hashed, password)

def encrypt_data(data: str, key: str) -> str:
    """Encrypt sensitive data (simple implementation)"""
    # This is a basic implementation - use proper encryption libraries in production
    import base64
    
    if not data or not key:
        return ""
    
    # Simple XOR encryption (use proper encryption in production)
    key_bytes = key.encode('utf-8')
    data_bytes = data.encode('utf-8')
    
    encrypted = bytearray()
    for i, byte in enumerate(data_bytes):
        encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
    
    return base64.b64encode(encrypted).decode('utf-8')

def decrypt_data(encrypted_data: str, key: str) -> str:
    """Decrypt sensitive data"""
    import base64
    
    if not encrypted_data or not key:
        return ""
    
    try:
        key_bytes = key.encode('utf-8')
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        
        decrypted = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        
        return decrypted.decode('utf-8')
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        return ""

def generate_user_id() -> str:
    """Generate anonymous user identifiers"""
    return str(uuid.uuid4())

# Date and Time Utilities

def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now(timezone.utc).isoformat()

def parse_date(date_string: str) -> Optional[datetime]:
    """Parse date strings safely"""
    if not date_string:
        return None
    
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%S.%f%z'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    return None

def calculate_time_difference(start_time: datetime, end_time: datetime) -> timedelta:
    """Calculate time differences"""
    return end_time - start_time

def is_same_day(date1: datetime, date2: datetime) -> bool:
    """Check if two dates are the same day"""
    return date1.date() == date2.date()

def get_week_start(date: datetime) -> datetime:
    """Get the start of the week for a date"""
    days_since_monday = date.weekday()
    return date - timedelta(days=days_since_monday)

def format_relative_time(timestamp: datetime) -> str:
    """Format time as '2 hours ago'"""
    now = datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

# API Response Utilities

def create_success_response(data: Any = None, message: str = None) -> Dict[str, Any]:
    """Standard success response"""
    response = {
        "success": True,
        "timestamp": get_current_timestamp()
    }
    
    if data is not None:
        response["data"] = data
    
    if message:
        response["message"] = message
    
    return response

def create_error_response(error_message: str, error_code: str = None, status_code: int = 400) -> Tuple[Dict[str, Any], int]:
    """Standard error response"""
    response = {
        "success": False,
        "error": {
            "message": error_message,
            "timestamp": get_current_timestamp()
        }
    }
    
    if error_code:
        response["error"]["code"] = error_code
    
    return response, status_code

def create_paginated_response(data: List[Any], page: int, per_page: int, total: int) -> Dict[str, Any]:
    """Paginated responses"""
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "success": True,
        "data": data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "timestamp": get_current_timestamp()
    }

def format_conversation_response(message: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Format chat responses"""
    response = {
        "message": message,
        "timestamp": get_current_timestamp(),
        "type": "assistant"
    }
    
    if metadata:
        response["metadata"] = metadata
    
    return response

def format_user_progress_response(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format progress data"""
    return {
        "user_progress": user_data,
        "timestamp": get_current_timestamp()
    }

# Data Processing Utilities

def merge_user_data(existing_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
    """Safely merge user data"""
    merged = existing_data.copy()
    
    for key, value in new_data.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            merged[key] = merge_user_data(merged[key], value)
        else:
            merged[key] = value
    
    return merged

def calculate_engagement_score(user_activity: Dict[str, Any]) -> float:
    """Calculate user engagement"""
    score = 0.0
    
    # Weight different activities
    weights = {
        'conversations': 2.0,
        'mood_logs': 1.5,
        'coping_strategies': 3.0,
        'resources_accessed': 1.0,
        'daily_streak': 5.0
    }
    
    for activity, weight in weights.items():
        if activity in user_activity:
            score += user_activity[activity] * weight
    
    # Normalize to 0-100 scale
    return min(100.0, score / 10.0)

def aggregate_mood_data(mood_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process mood tracking data"""
    if not mood_entries:
        return {"average_mood": 0, "mood_trend": "stable", "total_entries": 0}
    
    moods = [entry.get('mood_score', 0) for entry in mood_entries]
    average_mood = sum(moods) / len(moods)
    
    # Calculate trend (simple linear regression)
    if len(moods) >= 2:
        recent_avg = sum(moods[-3:]) / min(3, len(moods))
        older_avg = sum(moods[:-3]) / max(1, len(moods) - 3) if len(moods) > 3 else average_mood
        
        if recent_avg > older_avg + 0.5:
            trend = "improving"
        elif recent_avg < older_avg - 0.5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
    
    return {
        "average_mood": round(average_mood, 2),
        "mood_trend": trend,
        "total_entries": len(mood_entries),
        "latest_mood": moods[-1] if moods else 0
    }

def calculate_streak(activity_dates: List[datetime]) -> int:
    """Calculate activity streaks"""
    if not activity_dates:
        return 0
    
    # Sort dates in descending order
    sorted_dates = sorted([date.date() for date in activity_dates], reverse=True)
    
    streak = 0
    current_date = datetime.now().date()
    
    for date in sorted_dates:
        if date == current_date or date == current_date - timedelta(days=streak):
            streak += 1
            current_date = date
        else:
            break
    
    return streak

def anonymize_conversation_data(conversation: Dict[str, Any]) -> Dict[str, Any]:
    """Remove PII from conversations"""
    anonymized = conversation.copy()
    
    # Remove or hash sensitive fields
    sensitive_fields = ['user_id', 'ip_address', 'location']
    
    for field in sensitive_fields:
        if field in anonymized:
            if field == 'user_id':
                # Hash user ID for analytics while maintaining uniqueness
                anonymized[field] = hashlib.sha256(str(anonymized[field]).encode()).hexdigest()[:16]
            else:
                del anonymized[field]
    
    # Remove personal information from message content
    if 'message' in anonymized:
        message = anonymized['message']
        # Remove email addresses
        message = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', message)
        # Remove phone numbers
        message = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', message)
        # Remove potential names (simple heuristic)
        message = re.sub(r'\bmy name is \w+\b', 'my name is [NAME]', message, flags=re.IGNORECASE)
        anonymized['message'] = message
    
    return anonymized

# File and Storage Utilities

def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Safely load JSON files"""
    try:
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        return None

def save_json_file(data: Any, file_path: str) -> bool:
    """Safely save JSON files"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False, default=str)
        
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {e}")
        return False

def validate_file_path(file_path: str) -> bool:
    """Validate file paths for security"""
    if not file_path:
        return False
    
    # Prevent directory traversal attacks
    if '..' in file_path or file_path.startswith('/'):
        return False
    
    # Check for valid file extensions
    allowed_extensions = {'.json', '.txt', '.log', '.csv'}
    _, ext = os.path.splitext(file_path)
    
    return ext.lower() in allowed_extensions

# Mental Health Specific Utilities

def assess_message_risk(message: str) -> Dict[str, Any]:
    """Quick risk assessment of messages"""
    if not message:
        return {"risk_level": "low", "confidence": 0.0, "keywords": []}
    
    # Crisis keywords (this should be more sophisticated in production)
    high_risk_keywords = {
        'suicide', 'kill myself', 'end it all', 'want to die', 'no point living',
        'self harm', 'hurt myself', 'cut myself', 'overdose', 'jump off'
    }
    
    medium_risk_keywords = {
        'depressed', 'hopeless', 'worthless', 'alone', 'trapped', 'burden',
        'can\'t cope', 'overwhelmed', 'desperate', 'empty', 'numb'
    }
    
    message_lower = message.lower()
    found_high_risk = [kw for kw in high_risk_keywords if kw in message_lower]
    found_medium_risk = [kw for kw in medium_risk_keywords if kw in message_lower]
    
    if found_high_risk:
        return {
            "risk_level": "high",
            "confidence": 0.8,
            "keywords": found_high_risk,
            "requires_immediate_attention": True
        }
    elif found_medium_risk:
        return {
            "risk_level": "medium",
            "confidence": 0.6,
            "keywords": found_medium_risk,
            "requires_immediate_attention": False
        }
    else:
        return {
            "risk_level": "low",
            "confidence": 0.3,
            "keywords": [],
            "requires_immediate_attention": False
        }

def extract_mood_indicators(text: str) -> Dict[str, List[str]]:
    """Extract mood-related keywords"""
    if not text:
        return {"positive": [], "negative": [], "neutral": []}
    
    positive_indicators = {
        'happy', 'joy', 'excited', 'good', 'great', 'amazing', 'wonderful',
        'grateful', 'thankful', 'hopeful', 'optimistic', 'confident', 'proud',
        'calm', 'peaceful', 'relaxed', 'content', 'cheerful', 'delighted'
    }
    
    negative_indicators = {
        'sad', 'angry', 'upset', 'depressed', 'anxious', 'worried', 'stressed',
        'frustrated', 'disappointed', 'hurt', 'pain', 'terrible', 'awful',
        'hate', 'fear', 'scared', 'nervous', 'overwhelmed', 'hopeless',
        'lonely', 'tired', 'exhausted', 'confused', 'lost'
    }
    
    neutral_indicators = {
        'okay', 'fine', 'normal', 'average', 'usual', 'same', 'nothing',
        'regular', 'typical', 'ordinary'
    }
    
    text_lower = text.lower()
    words = re.findall(r'\b[a-zA-Z]+\b', text_lower)
    
    found_positive = [word for word in words if word in positive_indicators]
    found_negative = [word for word in words if word in negative_indicators]
    found_neutral = [word for word in words if word in neutral_indicators]
    
    return {
        "positive": list(set(found_positive)),
        "negative": list(set(found_negative)),
        "neutral": list(set(found_neutral))
    }

def suggest_coping_strategy(mood: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Suggest appropriate coping strategies"""
    strategies = {
        "anxious": [
            {"name": "Deep Breathing", "description": "Take slow, deep breaths for 5 minutes", "duration": 5},
            {"name": "Progressive Muscle Relaxation", "description": "Tense and relax muscle groups", "duration": 10},
            {"name": "Grounding Exercise", "description": "Name 5 things you can see, 4 you can hear, 3 you can touch", "duration": 3}
        ],
        "sad": [
            {"name": "Journaling", "description": "Write down your thoughts and feelings", "duration": 15},
            {"name": "Gentle Movement", "description": "Take a short walk or do light stretching", "duration": 10},
            {"name": "Connect with Others", "description": "Reach out to a friend or family member", "duration": 20}
        ],
        "angry": [
            {"name": "Counting Exercise", "description": "Count slowly from 1 to 10 or backwards from 100", "duration": 2},
            {"name": "Physical Release", "description": "Do jumping jacks or punch a pillow", "duration": 5},
            {"name": "Cool Down", "description": "Splash cold water on your face or step outside", "duration": 3}
        ],
        "stressed": [
            {"name": "Time Management", "description": "Make a priority list of tasks", "duration": 10},
            {"name": "Mindfulness", "description": "Focus on the present moment", "duration": 5},
            {"name": "Break Tasks", "description": "Break large tasks into smaller steps", "duration": 15}
        ]
    }
    
    mood_lower = mood.lower()
    suggested_strategies = strategies.get(mood_lower, strategies["anxious"])  # Default to anxiety strategies
    
    return {
        "mood": mood,
        "strategies": suggested_strategies,
        "recommendation": "Try one of these strategies that feels right for you right now"
    }

def calculate_wellness_score(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall wellness score"""
    score = 50  # Base score
    factors = []
    
    # Mood trend factor
    if 'mood_data' in user_data:
        mood_trend = user_data['mood_data'].get('mood_trend', 'stable')
        if mood_trend == 'improving':
            score += 15
            factors.append("Improving mood trend (+15)")
        elif mood_trend == 'declining':
            score -= 10
            factors.append("Declining mood trend (-10)")
    
    # Activity engagement factor
    if 'activity_counts' in user_data:
        activity = user_data['activity_counts']
        total_activities = sum(activity.values())
        if total_activities > 20:
            score += 10
            factors.append("High engagement (+10)")
        elif total_activities > 10:
            score += 5
            factors.append("Moderate engagement (+5)")
    
    # Streak factor
    if 'current_streaks' in user_data:
        daily_streak = user_data['current_streaks'].get('daily', 0)
        if daily_streak >= 7:
            score += 10
            factors.append(f"Strong daily streak: {daily_streak} days (+10)")
        elif daily_streak >= 3:
            score += 5
            factors.append(f"Good daily streak: {daily_streak} days (+5)")
    
    # Coping strategies factor
    if 'coping_strategies_used' in user_data:
        strategies = user_data['coping_strategies_used']
        if strategies >= 5:
            score += 8
            factors.append("Diverse coping strategies (+8)")
        elif strategies >= 2:
            score += 4
            factors.append("Some coping strategies (+4)")
    
    # Ensure score is within bounds
    score = max(0, min(100, score))
    
    # Determine wellness level
    if score >= 80:
        level = "Excellent"
    elif score >= 65:
        level = "Good"
    elif score >= 50:
        level = "Fair"
    elif score >= 35:
        level = "Needs Attention"
    else:
        level = "Concerning"
    
    return {
        "score": score,
        "level": level,
        "factors": factors,
        "calculated_at": get_current_timestamp()
    }

# Logging and Monitoring Utilities

def log_user_activity(user_id: str, activity_type: str, details: Dict[str, Any] = None):
    """Log user activities"""
    log_data = {
        "user_id": hashlib.sha256(user_id.encode()).hexdigest()[:16],  # Anonymized
        "activity_type": activity_type,
        "timestamp": get_current_timestamp(),
        "details": details or {}
    }
    
    logger.info(f"User activity: {json.dumps(log_data)}")

def log_error(error: Exception, context: str, user_id: str = None):
    """Structured error logging"""
    error_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "timestamp": get_current_timestamp()
    }
    
    if user_id:
        error_data["user_id"] = hashlib.sha256(user_id.encode()).hexdigest()[:16]
    
    logger.error(f"Application error: {json.dumps(error_data)}")

def log_security_event(event_type: str, details: Dict[str, Any]):
    """Log security-related events"""
    security_data = {
        "event_type": event_type,
        "details": details,
        "timestamp": get_current_timestamp(),
        "ip_address": request.remote_addr if request else "unknown"
    }
    
    logger.warning(f"Security event: {json.dumps(security_data)}")

# Configuration Utilities

def load_environment_config() -> Dict[str, Any]:
    """Load environment-specific configuration"""
    config = {
        "debug": os.getenv("DEBUG", "False").lower() == "true",
        "secret_key": os.getenv("SECRET_KEY", generate_secure_token()),
        "database_url": os.getenv("DATABASE_URL", "sqlite:///chillbuddy.db"),
        "max_message_length": int(os.getenv("MAX_MESSAGE_LENGTH", "5000")),
        "rate_limit_per_minute": int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
        "session_timeout_hours": int(os.getenv("SESSION_TIMEOUT_HOURS", "24"))
    }
    
    return config

def get_config_value(key: str, default: Any = None) -> Any:
    """Get configuration values safely"""
    return os.getenv(key, default)

def validate_environment() -> Tuple[bool, List[str]]:
    """Validate required environment variables"""
    required_vars = ["SECRET_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars

def is_development_mode() -> bool:
    """Check if running in development mode"""
    return os.getenv("FLASK_ENV", "production").lower() == "development"

# Rate Limiting Utilities (simple in-memory implementation)
_rate_limit_store = {}

def check_rate_limit(user_id: str, endpoint: str, limit_per_minute: int = 60) -> Tuple[bool, int]:
    """Check if user has exceeded rate limits"""
    key = f"{user_id}:{endpoint}"
    now = datetime.now()
    minute_key = now.strftime("%Y-%m-%d:%H:%M")
    
    if key not in _rate_limit_store:
        _rate_limit_store[key] = {}
    
    current_count = _rate_limit_store[key].get(minute_key, 0)
    
    if current_count >= limit_per_minute:
        return False, limit_per_minute - current_count
    
    return True, limit_per_minute - current_count - 1

def update_rate_limit_counter(user_id: str, endpoint: str):
    """Update rate limit counters"""
    key = f"{user_id}:{endpoint}"
    now = datetime.now()
    minute_key = now.strftime("%Y-%m-%d:%H:%M")
    
    if key not in _rate_limit_store:
        _rate_limit_store[key] = {}
    
    _rate_limit_store[key][minute_key] = _rate_limit_store[key].get(minute_key, 0) + 1
    
    # Clean up old entries (keep only last 5 minutes)
    cutoff_time = now - timedelta(minutes=5)
    keys_to_remove = []
    
    for stored_key in _rate_limit_store[key]:
        try:
            stored_time = datetime.strptime(stored_key, "%Y-%m-%d:%H:%M")
            if stored_time < cutoff_time:
                keys_to_remove.append(stored_key)
        except ValueError:
            keys_to_remove.append(stored_key)
    
    for old_key in keys_to_remove:
        del _rate_limit_store[key][old_key]