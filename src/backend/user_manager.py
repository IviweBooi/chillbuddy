# ChillBuddy Mental Health Chatbot - User Data Management
#
# This file contains:
# - User profile management
# - Data storage and retrieval
# - Privacy and consent handling
# - Session management
# - User preferences
# - Data anonymization and security

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import os
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import hashlib
import secrets

class UserStatus(Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class SessionStatus(Enum):
    """User session status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"

@dataclass
class UserProfile:
    """User profile data structure"""
    user_id: str
    username: str
    email: str
    created_at: datetime
    last_login: Optional[datetime]
    status: UserStatus
    preferences: Dict[str, Any]
    mental_health_goals: List[str]
    privacy_settings: Dict[str, bool]
    emergency_contacts: List[Dict[str, str]]
    password_hash: str = ""

@dataclass
class UserSession:
    """User session data structure"""
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    status: SessionStatus
    device_info: Dict[str, str]
    ip_address: str

class UserManager:
    """
    Comprehensive user management system for ChillBuddy.
    
    This class handles:
    - User registration and authentication
    - Profile management and preferences
    - Session management and security
    - Privacy and data protection
    - User analytics and insights
    
    The user management system ensures secure, privacy-focused
    handling of user data while providing personalized experiences.
    """
    
    def __init__(self, data_file: str = "user_data.json"):
        """
        Initialize the UserManager with data storage.
        
        Args:
            data_file: Path to user data storage file
        """
        self.logger = logging.getLogger(__name__)
        self.data_file = data_file
        self.users = {}
        self.sessions = {}
        self.session_timeout = timedelta(hours=24)
        
        # Default user preferences
        self.default_preferences = {
            "theme": "light",
            "notifications": True,
            "crisis_alerts": True,
            "data_sharing": False,
            "conversation_history": True,
            "ai_personality": "supportive"
        }
        
        # Default privacy settings
        self.default_privacy = {
            "profile_visible": False,
            "share_analytics": False,
            "emergency_contact_access": True,
            "data_retention": True
        }
        
        self.load_user_data()
        
    def load_user_data(self) -> bool:
        """
        Load user data from storage.
        
        Returns:
            bool: True if data loaded successfully
        """
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load users
                for user_data in data.get('users', []):
                    # Convert datetime strings back to datetime objects
                    user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
                    if user_data.get('last_login'):
                        user_data['last_login'] = datetime.fromisoformat(user_data['last_login'])
                    
                    user_data['status'] = UserStatus(user_data['status'])
                    user_profile = UserProfile(**user_data)
                    self.users[user_profile.user_id] = user_profile
                
                # Load sessions
                for session_data in data.get('sessions', []):
                    session_data['created_at'] = datetime.fromisoformat(session_data['created_at'])
                    session_data['last_activity'] = datetime.fromisoformat(session_data['last_activity'])
                    session_data['expires_at'] = datetime.fromisoformat(session_data['expires_at'])
                    session_data['status'] = SessionStatus(session_data['status'])
                    
                    session = UserSession(**session_data)
                    self.sessions[session.session_id] = session
                
                self.logger.info(f"Loaded {len(self.users)} users and {len(self.sessions)} sessions")
                return True
            else:
                self.logger.info("No existing user data file found. Starting fresh.")
                return True
                
        except Exception as e:
            self.logger.error(f"Error loading user data: {e}")
            return False
    
    def save_user_data(self) -> bool:
        """
        Save user data to storage.
        
        Returns:
            bool: True if data saved successfully
        """
        try:
            # Prepare data for serialization
            users_data = []
            for user in self.users.values():
                user_dict = asdict(user)
                user_dict['created_at'] = user.created_at.isoformat()
                user_dict['last_login'] = user.last_login.isoformat() if user.last_login else None
                user_dict['status'] = user.status.value
                users_data.append(user_dict)
            
            sessions_data = []
            for session in self.sessions.values():
                session_dict = asdict(session)
                session_dict['created_at'] = session.created_at.isoformat()
                session_dict['last_activity'] = session.last_activity.isoformat()
                session_dict['expires_at'] = session.expires_at.isoformat()
                session_dict['status'] = session.status.value
                sessions_data.append(session_dict)
            
            data = {
                'users': users_data,
                'sessions': sessions_data,
                'last_updated': datetime.now().isoformat()
            }
            
            # Create backup if file exists
            if os.path.exists(self.data_file):
                backup_file = f"{self.data_file}.backup"
                os.rename(self.data_file, backup_file)
            
            # Save new data
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info("User data saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving user data: {e}")
            return False
    
    def _hash_password(self, password: str) -> str:
        """
        Hash password using SHA-256 with salt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """
        Verify password against stored hash.
        
        Args:
            password: Plain text password
            stored_hash: Stored password hash
            
        Returns:
            bool: True if password matches
        """
        try:
            salt, hash_value = stored_hash.split(':')
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return password_hash == hash_value
        except:
            return False
    
    def create_user(self, username: str, email: str, password: str, 
                   preferences: Dict[str, Any] = None) -> Tuple[bool, str, Optional[UserProfile]]:
        """
        Create a new user account.
        
        Args:
            username: Unique username
            email: User's email address
            password: User's password (will be hashed)
            preferences: Initial user preferences
            
        Returns:
            Tuple containing:
            - bool: Success status
            - str: Result message
            - Optional[UserProfile]: Created user profile
        """
        try:
            # Validate input
            if not username or not email or not password:
                return False, "Username, email, and password are required", None
            
            if len(password) < 8:
                return False, "Password must be at least 8 characters long", None
            
            # Check for existing users
            for user in self.users.values():
                if user.username.lower() == username.lower():
                    return False, "Username already exists", None
                if user.email.lower() == email.lower():
                    return False, "Email already registered", None
            
            # Create user profile
            user_id = str(uuid.uuid4())
            password_hash = self._hash_password(password)
            
            user_preferences = self.default_preferences.copy()
            if preferences:
                user_preferences.update(preferences)
            
            user_profile = UserProfile(
                user_id=user_id,
                username=username,
                email=email,
                created_at=datetime.now(),
                last_login=None,
                status=UserStatus.ACTIVE,
                preferences=user_preferences,
                mental_health_goals=[],
                privacy_settings=self.default_privacy.copy(),
                emergency_contacts=[],
                password_hash=password_hash
            )
            
            # Save user
            self.users[user_id] = user_profile
            self.save_user_data()
            
            self.logger.info(f"Created new user: {username} ({user_id})")
            return True, "User created successfully", user_profile
            
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            return False, "Failed to create user account", None
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str, Optional[UserProfile]]:
        """
        Authenticate user credentials.
        
        Args:
            username: Username or email
            password: User's password
            
        Returns:
            Tuple containing:
            - bool: Authentication success
            - str: Result message
            - Optional[UserProfile]: User profile if authenticated
        """
        try:
            # Find user by username or email
            user_profile = None
            for user in self.users.values():
                if (user.username.lower() == username.lower() or 
                    user.email.lower() == username.lower()):
                    user_profile = user
                    break
            
            if not user_profile:
                return False, "User not found", None
            
            if user_profile.status != UserStatus.ACTIVE:
                return False, "Account is not active", None
            
            # Verify password
            if not self._verify_password(password, user_profile.password_hash):
                return False, "Invalid password", None
            
            # Update last login
            user_profile.last_login = datetime.now()
            self.save_user_data()
            
            self.logger.info(f"User authenticated: {user_profile.username}")
            return True, "Authentication successful", user_profile
            
        except Exception as e:
            self.logger.error(f"Error authenticating user: {e}")
            return False, "Authentication failed", None
    
    def create_session(self, user_id: str, device_info: Dict[str, str] = None, 
                      ip_address: str = None) -> Tuple[bool, str, Optional[UserSession]]:
        """
        Create a new user session.
        
        Args:
            user_id: User's unique identifier
            device_info: Device information
            ip_address: User's IP address
            
        Returns:
            Tuple containing:
            - bool: Success status
            - str: Result message
            - Optional[UserSession]: Created session
        """
        try:
            if user_id not in self.users:
                return False, "User not found", None
            
            # Generate secure session ID
            session_id = secrets.token_urlsafe(32)
            now = datetime.now()
            
            session = UserSession(
                session_id=session_id,
                user_id=user_id,
                created_at=now,
                last_activity=now,
                expires_at=now + self.session_timeout,
                status=SessionStatus.ACTIVE,
                device_info=device_info or {},
                ip_address=ip_address or "unknown"
            )
            
            self.sessions[session_id] = session
            
            # Clean up expired sessions
            self.cleanup_expired_sessions()
            
            self.save_user_data()
            
            self.logger.info(f"Created session for user {user_id}: {session_id}")
            return True, "Session created successfully", session
            
        except Exception as e:
            self.logger.error(f"Error creating session: {e}")
            return False, "Failed to create session", None
    
    def validate_session(self, session_id: str) -> Tuple[bool, Optional[UserSession]]:
        """
        Validate and refresh user session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Tuple containing:
            - bool: Session validity
            - Optional[UserSession]: Session object if valid
        """
        try:
            session = self.sessions.get(session_id)
            
            if not session:
                return False, None
            
            if session.status != SessionStatus.ACTIVE:
                return False, None
            
            # Check expiration
            if datetime.now() > session.expires_at:
                session.status = SessionStatus.EXPIRED
                self.save_user_data()
                return False, None
            
            # Update last activity
            session.last_activity = datetime.now()
            self.save_user_data()
            
            return True, session
            
        except Exception as e:
            self.logger.error(f"Error validating session: {e}")
            return False, None
    
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Update user profile information.
        
        Args:
            user_id: User's unique identifier
            updates: Dictionary of fields to update
            
        Returns:
            Tuple containing:
            - bool: Update success
            - str: Result message
        """
        try:
            if user_id not in self.users:
                return False, "User not found"
            
            user = self.users[user_id]
            
            # Validate and apply updates
            allowed_fields = ['username', 'email', 'mental_health_goals', 'emergency_contacts']
            
            for field, value in updates.items():
                if field in allowed_fields:
                    setattr(user, field, value)
                else:
                    self.logger.warning(f"Attempted to update restricted field: {field}")
            
            self.save_user_data()
            
            self.logger.info(f"Updated profile for user {user_id}")
            return True, "Profile updated successfully"
            
        except Exception as e:
            self.logger.error(f"Error updating user profile: {e}")
            return False, "Failed to update profile"
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Retrieve user profile by ID.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            UserProfile object or None if not found
        """
        return self.users.get(user_id)
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences and settings.
        
        Args:
            user_id: User's unique identifier
            preferences: New preference settings
            
        Returns:
            bool: Update success status
        """
        try:
            if user_id not in self.users:
                return False
            
            user = self.users[user_id]
            user.preferences.update(preferences)
            
            self.save_user_data()
            
            self.logger.info(f"Updated preferences for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating preferences: {e}")
            return False
    
    def set_mental_health_goals(self, user_id: str, goals: List[str]) -> bool:
        """
        Set user's mental health goals.
        
        Args:
            user_id: User's unique identifier
            goals: List of mental health goals
            
        Returns:
            bool: Success status
        """
        try:
            if user_id not in self.users:
                return False
            
            user = self.users[user_id]
            user.mental_health_goals = goals
            
            self.save_user_data()
            
            self.logger.info(f"Set mental health goals for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting mental health goals: {e}")
            return False
    
    def get_user_analytics(self, user_id: str, timeframe: timedelta = None) -> Dict[str, Any]:
        """
        Get user analytics and insights.
        
        Args:
            user_id: User's unique identifier
            timeframe: Time period for analytics
            
        Returns:
            Dictionary containing user analytics
        """
        try:
            if user_id not in self.users:
                return {}
            
            user = self.users[user_id]
            
            # Calculate basic analytics
            user_sessions = [s for s in self.sessions.values() if s.user_id == user_id]
            
            analytics = {
                "user_id": user_id,
                "account_age_days": (datetime.now() - user.created_at).days,
                "total_sessions": len(user_sessions),
                "active_sessions": len([s for s in user_sessions if s.status == SessionStatus.ACTIVE]),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "mental_health_goals_count": len(user.mental_health_goals),
                "preferences": user.preferences.copy()
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error generating user analytics: {e}")
            return {}
    
    def terminate_session(self, session_id: str) -> bool:
        """
        Terminate a user session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: Termination success
        """
        try:
            session = self.sessions.get(session_id)
            
            if session:
                session.status = SessionStatus.TERMINATED
                self.save_user_data()
                
                self.logger.info(f"Terminated session: {session_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error terminating session: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired user sessions.
        
        Returns:
            int: Number of sessions cleaned up
        """
        try:
            now = datetime.now()
            expired_sessions = []
            
            for session_id, session in self.sessions.items():
                if (session.status == SessionStatus.ACTIVE and 
                    now > session.expires_at):
                    session.status = SessionStatus.EXPIRED
                    expired_sessions.append(session_id)
            
            if expired_sessions:
                self.save_user_data()
                self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            
            return len(expired_sessions)
            
        except Exception as e:
            self.logger.error(f"Error cleaning up sessions: {e}")
            return 0
    
    def delete_user_account(self, user_id: str, confirmation: str) -> Tuple[bool, str]:
        """
        Delete user account and associated data.
        
        Args:
            user_id: User's unique identifier
            confirmation: Confirmation string
            
        Returns:
            Tuple containing:
            - bool: Deletion success
            - str: Result message
        """
        try:
            if user_id not in self.users:
                return False, "User not found"
            
            if confirmation != "DELETE_ACCOUNT":
                return False, "Invalid confirmation"
            
            user = self.users[user_id]
            
            # Mark user as deleted
            user.status = UserStatus.DELETED
            
            # Terminate all user sessions
            user_sessions = [s for s in self.sessions.values() if s.user_id == user_id]
            for session in user_sessions:
                session.status = SessionStatus.TERMINATED
            
            self.save_user_data()
            
            self.logger.info(f"Deleted user account: {user_id}")
            return True, "Account deleted successfully"
            
        except Exception as e:
            self.logger.error(f"Error deleting user account: {e}")
            return False, "Failed to delete account"