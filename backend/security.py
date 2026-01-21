"""
Security middleware for NLP Assistant API
Provides input validation, sanitization, and API key authentication
"""
import bleach
from functools import wraps
from flask import request, jsonify
import config


def sanitize_input(text, max_length=None):
    """
    Sanitize user input by removing HTML tags and limiting length.
    """
    if not isinstance(text, str):
        return ""
    
    # Remove HTML tags and scripts
    cleaned = bleach.clean(text, tags=[], strip=True)
    
    # Limit length if specified
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    return cleaned.strip()


def validate_api_key(f):
    """
    Decorator to validate API key from request headers.
    Only applies if REQUIRE_API_KEY is True.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip API key check if not required
        if not config.REQUIRE_API_KEY:
            return f(*args, **kwargs)
        
        # Get API key from header
        api_key = request.headers.get('X-API-Key')
        
        # Validate API key
        if not api_key or api_key != config.API_KEY:
            return jsonify({
                "error": "Invalid or missing API key",
                "message": "Please provide a valid X-API-Key header"
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def validate_question(question):
    """
    Validate and sanitize question input.
    Returns (is_valid, sanitized_question, error_message)
    """
    if not question:
        return False, "", "Question is required"
    
    if not isinstance(question, str):
        return False, "", "Question must be a string"
    
    # Sanitize input
    sanitized = sanitize_input(question, max_length=config.MAX_QUESTION_LENGTH)
    
    if not sanitized:
        return False, "", "Question cannot be empty after sanitization"
    
    if len(sanitized) < 3:
        return False, "", "Question is too short (minimum 3 characters)"
    
    return True, sanitized, None


def validate_chat_title(title):
    """
    Validate and sanitize chat title.
    Returns (is_valid, sanitized_title, error_message)
    """
    if not title:
        return False, "", "Title is required"
    
    if not isinstance(title, str):
        return False, "", "Title must be a string"
    
    # Sanitize input
    sanitized = sanitize_input(title, max_length=config.MAX_TITLE_LENGTH)
    
    if not sanitized:
        return False, "", "Title cannot be empty"
    
    return True, sanitized, None
