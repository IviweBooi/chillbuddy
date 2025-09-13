# ChillBuddy Mental Health Chatbot - Main Flask Application
#
# This file contains:
# - Flask app initialization and configuration
# - API route definitions
# - Request/response handling
# - Error handling and logging
# - CORS configuration
# - Session management

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from functools import wraps
import logging
import os
from datetime import datetime, timedelta
import traceback
from typing import Dict, Any, Optional, Tuple

# Import custom modules
from conversation import ConversationEngine
from safety import SafetyManager
from user_manager import UserManager
from resources import ResourceManager
from gamification import GamificationManager
from utils import validate_input, sanitize_text, rate_limit_check

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Configure CORS
CORS(app, origins=['http://localhost:3000', 'http://localhost:5173'], supports_credentials=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chillbuddy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize components
conversation_engine = None
safety_manager = None
user_manager = None
resource_manager = None
gamification_manager = None

def init_app_components():
    """Initialize all application components"""
    global conversation_engine, safety_manager, user_manager, resource_manager, gamification_manager
    
    try:
        logger.info("Initializing ChillBuddy components...")
        
        # Initialize managers
        conversation_engine = ConversationEngine()
        safety_manager = SafetyManager()
        user_manager = UserManager()
        resource_manager = ResourceManager()
        gamification_manager = GamificationManager()
        
        logger.info("All components initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        return False

# Authentication decorator
def require_auth(f):
    """Decorator to require authentication for protected endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = request.headers.get('Authorization')
        if not session_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Validate session
        is_valid, user_session = user_manager.validate_session(session_id)
        if not is_valid:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        # Add user info to request context
        request.user_id = user_session.user_id
        request.session_id = session_id
        
        return f(*args, **kwargs)
    return decorated_function

# Rate limiting decorator
def rate_limit(max_requests: int = 60, window_minutes: int = 1):
    """Decorator for rate limiting endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            if not rate_limit_check(client_ip, max_requests, window_minutes):
                return jsonify({'error': 'Rate limit exceeded'}), 429
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Request logging middleware
@app.before_request
def log_request_info():
    """Log incoming requests"""
    logger.info(f"{request.method} {request.url} - IP: {request.remote_addr}")

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'conversation_engine': conversation_engine is not None,
                'safety_manager': safety_manager is not None,
                'user_manager': user_manager is not None,
                'resource_manager': resource_manager is not None,
                'gamification_manager': gamification_manager is not None
            }
        }
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# User registration endpoint
@app.route('/api/auth/register', methods=['POST'])
@rate_limit(max_requests=5, window_minutes=15)
def register_user():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['username', 'email', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Sanitize input
        username = sanitize_text(data['username'])
        email = sanitize_text(data['email'])
        password = data['password']
        
        # Validate input format
        if not validate_input(username, 'username') or not validate_input(email, 'email'):
            return jsonify({'error': 'Invalid input format'}), 400
        
        # Create user
        success, message, user_profile = user_manager.create_user(
            username=username,
            email=email,
            password=password,
            preferences=data.get('preferences', {})
        )
        
        if success:
            # Create session
            session_success, session_message, user_session = user_manager.create_session(
                user_id=user_profile.user_id,
                device_info=data.get('device_info', {}),
                ip_address=request.remote_addr
            )
            
            if session_success:
                return jsonify({
                    'message': 'User registered successfully',
                    'user_id': user_profile.user_id,
                    'session_id': user_session.session_id
                }), 201
            else:
                return jsonify({'error': 'User created but session failed'}), 500
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

# User login endpoint
@app.route('/api/auth/login', methods=['POST'])
@rate_limit(max_requests=10, window_minutes=15)
def login_user():
    """Authenticate user and create session"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password required'}), 400
        
        username = sanitize_text(data['username'])
        password = data['password']
        
        # Authenticate user
        success, message, user_profile = user_manager.authenticate_user(username, password)
        
        if success:
            # Create session
            session_success, session_message, user_session = user_manager.create_session(
                user_id=user_profile.user_id,
                device_info=data.get('device_info', {}),
                ip_address=request.remote_addr
            )
            
            if session_success:
                return jsonify({
                    'message': 'Login successful',
                    'user_id': user_profile.user_id,
                    'session_id': user_session.session_id,
                    'username': user_profile.username
                }), 200
            else:
                return jsonify({'error': 'Authentication succeeded but session failed'}), 500
        else:
            return jsonify({'error': message}), 401
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

# User logout endpoint
@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout_user():
    """Terminate user session"""
    try:
        success = user_manager.terminate_session(request.session_id)
        
        if success:
            return jsonify({'message': 'Logout successful'}), 200
        else:
            return jsonify({'error': 'Logout failed'}), 500
            
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': 'Logout failed'}), 500

# Chat endpoint
@app.route('/api/chat', methods=['POST'])
@require_auth
@rate_limit(max_requests=30, window_minutes=1)
def chat():
    """Handle chat messages and generate responses"""
    try:
        data = request.get_json()
        
        if not data.get('message'):
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = sanitize_text(data['message'])
        user_id = request.user_id
        
        # Get conversation context
        conversation_history = data.get('conversation_history', [])
        
        # Generate response
        response_data = conversation_engine.generate_response(
            user_message=user_message,
            user_id=user_id,
            conversation_history=conversation_history
        )
        
        # Check for crisis situations
        if response_data.get('crisis_detected'):
            # Log crisis event
            safety_manager.log_safety_event(
                user_id=user_id,
                event_type='crisis_detected',
                severity='high',
                details={'message': user_message, 'response': response_data}
            )
        
        # Update user engagement
        gamification_manager.update_user_engagement(
            user_id=user_id,
            action='chat_message',
            metadata={'message_length': len(user_message)}
        )
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'error': 'Failed to process message'}), 500

# Crisis endpoint
@app.route('/api/crisis', methods=['POST'])
@require_auth
def handle_crisis():
    """Handle crisis situations"""
    try:
        data = request.get_json()
        user_id = request.user_id
        
        crisis_type = data.get('crisis_type', 'general')
        severity = data.get('severity', 'medium')
        details = data.get('details', {})
        
        # Handle crisis
        crisis_response = safety_manager.handle_crisis(
            user_id=user_id,
            crisis_type=crisis_type,
            severity=severity,
            user_message=details.get('message', ''),
            context=details
        )
        
        # Get crisis resources
        resources = resource_manager.get_crisis_resources(
            crisis_type=crisis_type,
            user_location=details.get('location')
        )
        
        response = {
            'crisis_response': crisis_response,
            'resources': resources,
            'emergency_contacts': safety_manager.get_emergency_contacts(),
            'follow_up_scheduled': True
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Crisis handling error: {e}")
        return jsonify({'error': 'Failed to handle crisis'}), 500

# Resources endpoint
@app.route('/api/resources', methods=['GET'])
@require_auth
def get_resources():
    """Get mental health resources"""
    try:
        user_id = request.user_id
        resource_type = request.args.get('type', 'all')
        location = request.args.get('location')
        
        resources = resource_manager.get_resources(
            resource_type=resource_type,
            user_id=user_id,
            location=location
        )
        
        return jsonify({'resources': resources}), 200
        
    except Exception as e:
        logger.error(f"Resources error: {e}")
        return jsonify({'error': 'Failed to get resources'}), 500

# User profile endpoint
@app.route('/api/user/profile', methods=['GET'])
@require_auth
def get_user_profile():
    """Get user profile and progress"""
    try:
        user_id = request.user_id
        
        # Get user profile
        user_profile = user_manager.get_user_profile(user_id)
        if not user_profile:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user analytics
        analytics = user_manager.get_user_analytics(user_id)
        
        # Get user achievements
        achievements = gamification_manager.get_user_achievements(user_id)
        
        # Prepare response (exclude sensitive data)
        profile_data = {
            'user_id': user_profile.user_id,
            'username': user_profile.username,
            'email': user_profile.email,
            'created_at': user_profile.created_at.isoformat(),
            'last_login': user_profile.last_login.isoformat() if user_profile.last_login else None,
            'preferences': user_profile.preferences,
            'mental_health_goals': user_profile.mental_health_goals,
            'privacy_settings': user_profile.privacy_settings,
            'analytics': analytics,
            'achievements': achievements
        }
        
        return jsonify(profile_data), 200
        
    except Exception as e:
        logger.error(f"Profile error: {e}")
        return jsonify({'error': 'Failed to get profile'}), 500

# Update user progress endpoint
@app.route('/api/user/progress', methods=['POST'])
@require_auth
def update_user_progress():
    """Update user progress and achievements"""
    try:
        data = request.get_json()
        user_id = request.user_id
        
        progress_type = data.get('type')
        progress_data = data.get('data', {})
        
        # Update progress
        success = gamification_manager.update_user_progress(
            user_id=user_id,
            progress_type=progress_type,
            progress_data=progress_data
        )
        
        if success:
            # Check for new achievements
            new_achievements = gamification_manager.check_achievements(user_id)
            
            return jsonify({
                'message': 'Progress updated successfully',
                'new_achievements': new_achievements
            }), 200
        else:
            return jsonify({'error': 'Failed to update progress'}), 500
            
    except Exception as e:
        logger.error(f"Progress update error: {e}")
        return jsonify({'error': 'Failed to update progress'}), 500

# User badges endpoint
@app.route('/api/user/badges', methods=['GET'])
@require_auth
def get_user_badges():
    """Get user achievements and badges"""
    try:
        user_id = request.user_id
        
        badges = gamification_manager.get_user_badges(user_id)
        achievements = gamification_manager.get_user_achievements(user_id)
        
        return jsonify({
            'badges': badges,
            'achievements': achievements
        }), 200
        
    except Exception as e:
        logger.error(f"Badges error: {e}")
        return jsonify({'error': 'Failed to get badges'}), 500

# Feedback endpoint
@app.route('/api/feedback', methods=['POST'])
@require_auth
@rate_limit(max_requests=5, window_minutes=60)
def submit_feedback():
    """Submit user feedback"""
    try:
        data = request.get_json()
        user_id = request.user_id
        
        feedback_type = data.get('type', 'general')
        feedback_text = sanitize_text(data.get('feedback', ''))
        rating = data.get('rating')
        
        if not feedback_text:
            return jsonify({'error': 'Feedback text is required'}), 400
        
        # Store feedback
        feedback_data = {
            'user_id': user_id,
            'type': feedback_type,
            'feedback': feedback_text,
            'rating': rating,
            'timestamp': datetime.now().isoformat(),
            'ip_address': request.remote_addr
        }
        
        # Log feedback
        logger.info(f"Feedback received from user {user_id}: {feedback_type}")
        
        return jsonify({'message': 'Feedback submitted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        return jsonify({'error': 'Failed to submit feedback'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(429)
def rate_limit_exceeded(error):
    """Handle rate limit errors"""
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {e}\n{traceback.format_exc()}")
    return jsonify({'error': 'An unexpected error occurred'}), 500

# Application startup
if __name__ == '__main__':
    # Initialize components
    if not init_app_components():
        logger.error("Failed to initialize application components")
        exit(1)
    
    # Get configuration
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    logger.info(f"Starting ChillBuddy server on {host}:{port} (debug={debug_mode})")
    
    # Run the application
    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        threaded=True
    )