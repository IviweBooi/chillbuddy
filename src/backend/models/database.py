#!/usr/bin/env python3
"""
ChillBuddy Mental Health Chatbot - Database Models
Handles data persistence, user management, and conversation storage

Author: ChillBuddy Team
Date: 2025
"""

import json
import sqlite3
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum


class UserStatus(Enum):
    """User account status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class ConversationStatus(Enum):
    """Conversation status enumeration"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class User:
    """User data model"""
    user_id: str
    username: str
    email: Optional[str] = None
    password_hash: Optional[str] = None
    created_at: datetime = None
    last_active: datetime = None
    status: UserStatus = UserStatus.ACTIVE
    preferences: Dict[str, Any] = None
    profile_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_active is None:
            self.last_active = datetime.now()
        if self.preferences is None:
            self.preferences = {}
        if self.profile_data is None:
            self.profile_data = {}


@dataclass
class Conversation:
    """Conversation data model"""
    conversation_id: str
    user_id: str
    title: str
    created_at: datetime = None
    updated_at: datetime = None
    status: ConversationStatus = ConversationStatus.ACTIVE
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Message:
    """Message data model"""
    message_id: str
    conversation_id: str
    user_id: str
    content: str
    message_type: str  # 'user' or 'bot'
    timestamp: datetime = None
    risk_level: RiskLevel = RiskLevel.LOW
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class UserSession:
    """User session data model"""
    session_id: str
    user_id: str
    created_at: datetime = None
    expires_at: datetime = None
    is_active: bool = True
    session_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(hours=24)
        if self.session_data is None:
            self.session_data = {}


class DatabaseManager:
    """Database manager for ChillBuddy application"""
    
    def __init__(self, db_path: str = "data/chillbuddy.db"):
        """
        Initialize database manager
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._init_database()
        
    def _init_database(self) -> None:
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE,
                        password_hash TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'active',
                        preferences TEXT DEFAULT '{}',
                        profile_data TEXT DEFAULT '{}'
                    )
                """)
                
                # Conversations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        conversation_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'active',
                        metadata TEXT DEFAULT '{}',
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                """)
                
                # Messages table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        message_id TEXT PRIMARY KEY,
                        conversation_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        content TEXT NOT NULL,
                        message_type TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        risk_level TEXT DEFAULT 'low',
                        metadata TEXT DEFAULT '{}',
                        FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id),
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                """)
                
                # User sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        session_data TEXT DEFAULT '{}',
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations (user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages (conversation_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages (user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions (user_id)")
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def create_user(self, user: User) -> bool:
        """Create a new user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (user_id, username, email, password_hash, 
                                     created_at, last_active, status, preferences, profile_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user.user_id, user.username, user.email, user.password_hash,
                    user.created_at, user.last_active, user.status.value,
                    json.dumps(user.preferences), json.dumps(user.profile_data)
                ))
                conn.commit()
                self.logger.info(f"User created: {user.user_id}")
                return True
        except Exception as e:
            self.logger.error(f"Failed to create user: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                
                if row:
                    return User(
                        user_id=row[0],
                        username=row[1],
                        email=row[2],
                        password_hash=row[3],
                        created_at=datetime.fromisoformat(row[4]) if row[4] else None,
                        last_active=datetime.fromisoformat(row[5]) if row[5] else None,
                        status=UserStatus(row[6]),
                        preferences=json.loads(row[7]) if row[7] else {},
                        profile_data=json.loads(row[8]) if row[8] else {}
                    )
                return None
        except Exception as e:
            self.logger.error(f"Failed to get user: {e}")
            return None
    
    def update_user(self, user: User) -> bool:
        """Update user information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users SET username = ?, email = ?, password_hash = ?,
                                   last_active = ?, status = ?, preferences = ?, profile_data = ?
                    WHERE user_id = ?
                """, (
                    user.username, user.email, user.password_hash,
                    user.last_active, user.status.value,
                    json.dumps(user.preferences), json.dumps(user.profile_data),
                    user.user_id
                ))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Failed to update user: {e}")
            return False
    
    def create_conversation(self, conversation: Conversation) -> bool:
        """Create a new conversation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversations (conversation_id, user_id, title,
                                             created_at, updated_at, status, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    conversation.conversation_id, conversation.user_id, conversation.title,
                    conversation.created_at, conversation.updated_at,
                    conversation.status.value, json.dumps(conversation.metadata)
                ))
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to create conversation: {e}")
            return False
    
    def update_conversation(self, conversation: Conversation) -> bool:
        """Update conversation information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE conversations SET title = ?, updated_at = ?, status = ?, metadata = ?
                    WHERE conversation_id = ?
                """, (
                    conversation.title, conversation.updated_at,
                    conversation.status.value, json.dumps(conversation.metadata),
                    conversation.conversation_id
                ))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Failed to update conversation: {e}")
            return False
    
    def get_user_conversations(self, user_id: str, limit: int = 50) -> List[Conversation]:
        """Get user's conversations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM conversations 
                    WHERE user_id = ? AND status != 'deleted'
                    ORDER BY updated_at DESC LIMIT ?
                """, (user_id, limit))
                
                conversations = []
                for row in cursor.fetchall():
                    conversations.append(Conversation(
                        conversation_id=row[0],
                        user_id=row[1],
                        title=row[2],
                        created_at=datetime.fromisoformat(row[3]) if row[3] else None,
                        updated_at=datetime.fromisoformat(row[4]) if row[4] else None,
                        status=ConversationStatus(row[5]),
                        metadata=json.loads(row[6]) if row[6] else {}
                    ))
                return conversations
        except Exception as e:
            self.logger.error(f"Failed to get conversations: {e}")
            return []
    
    def add_message(self, message: Message) -> bool:
        """Add a message to conversation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO messages (message_id, conversation_id, user_id, content,
                                        message_type, timestamp, risk_level, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message.message_id, message.conversation_id, message.user_id,
                    message.content, message.message_type, message.timestamp,
                    message.risk_level.value, json.dumps(message.metadata)
                ))
                
                # Update conversation timestamp
                cursor.execute("""
                    UPDATE conversations SET updated_at = ? WHERE conversation_id = ?
                """, (datetime.now(), message.conversation_id))
                
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to add message: {e}")
            return False
    
    def get_conversation_messages(self, conversation_id: str, limit: int = 100) -> List[Message]:
        """Get messages from a conversation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM messages 
                    WHERE conversation_id = ?
                    ORDER BY timestamp ASC LIMIT ?
                """, (conversation_id, limit))
                
                messages = []
                for row in cursor.fetchall():
                    messages.append(Message(
                        message_id=row[0],
                        conversation_id=row[1],
                        user_id=row[2],
                        content=row[3],
                        message_type=row[4],
                        timestamp=datetime.fromisoformat(row[5]) if row[5] else None,
                        risk_level=RiskLevel(row[6]),
                        metadata=json.loads(row[7]) if row[7] else {}
                    ))
                return messages
        except Exception as e:
            self.logger.error(f"Failed to get messages: {e}")
            return []
    
    def create_session(self, session: UserSession) -> bool:
        """Create a user session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_sessions (session_id, user_id, created_at,
                                             expires_at, is_active, session_data)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id, session.user_id, session.created_at,
                    session.expires_at, session.is_active, json.dumps(session.session_data)
                ))
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user_sessions WHERE session_id = ?", (session_id,))
                row = cursor.fetchone()
                
                if row:
                    return UserSession(
                        session_id=row[0],
                        user_id=row[1],
                        created_at=datetime.fromisoformat(row[2]) if row[2] else None,
                        expires_at=datetime.fromisoformat(row[3]) if row[3] else None,
                        is_active=bool(row[4]),
                        session_data=json.loads(row[5]) if row[5] else {}
                    )
                return None
        except Exception as e:
            self.logger.error(f"Failed to get session: {e}")
            return None
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM user_sessions 
                    WHERE expires_at < ? OR is_active = 0
                """, (datetime.now(),))
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            self.logger.error(f"Failed to cleanup sessions: {e}")
            return 0
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get conversation count
                cursor.execute("""
                    SELECT COUNT(*) FROM conversations 
                    WHERE user_id = ? AND status = 'active'
                """, (user_id,))
                conversation_count = cursor.fetchone()[0]
                
                # Get message count
                cursor.execute("""
                    SELECT COUNT(*) FROM messages WHERE user_id = ?
                """, (user_id,))
                message_count = cursor.fetchone()[0]
                
                # Get risk level distribution
                cursor.execute("""
                    SELECT risk_level, COUNT(*) FROM messages 
                    WHERE user_id = ? GROUP BY risk_level
                """, (user_id,))
                risk_distribution = dict(cursor.fetchall())
                
                return {
                    "conversation_count": conversation_count,
                    "message_count": message_count,
                    "risk_distribution": risk_distribution
                }
        except Exception as e:
            self.logger.error(f"Failed to get user stats: {e}")
            return {}
    
    def close(self) -> None:
        """Close database connection"""
        # SQLite connections are automatically closed when using context managers
        pass


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID"""
    import uuid
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == password_hash


if __name__ == "__main__":
    # Test database functionality
    db = DatabaseManager("test_chillbuddy.db")
    
    # Create test user
    test_user = User(
        user_id=generate_id("user_"),
        username="test_user",
        email="test@example.com",
        password_hash=hash_password("test_password")
    )
    
    print(f"Creating user: {db.create_user(test_user)}")
    print(f"User stats: {db.get_user_stats(test_user.user_id)}")