#!/usr/bin/env python3
"""
ChillBuddy Mental Health Chatbot - Conversation Manager
Integrates conversation engine with database for persistent chat history

Author: ChillBuddy Team
Date: 2025
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import asdict

# Import our modules
from conversation import ConversationEngine
from models.database import (
    DatabaseManager, User, Conversation, Message, UserSession,
    RiskLevel, ConversationStatus, generate_id
)
from safety import SafetyManager
from user_manager import UserManager


class ConversationManager:
    """
    Manages conversations with persistent storage and context management.
    Integrates ConversationEngine with DatabaseManager for full chat functionality.
    """
    
    def __init__(self, 
                 db_path: str = "data/chillbuddy.db",
                 model_config_path: str = "models/model_config.json"):
        """
        Initialize conversation manager
        
        Args:
            db_path (str): Path to database file
            model_config_path (str): Path to model configuration
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        try:
            self.db = DatabaseManager(db_path)
            self.conversation_engine = ConversationEngine(model_config_path)
            self.safety_manager = SafetyManager()
            self.user_manager = UserManager()
            
            self.logger.info("ConversationManager initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize ConversationManager: {e}")
            raise
    
    def start_conversation(self, user_id: str, title: str = None) -> Optional[str]:
        """
        Start a new conversation for a user
        
        Args:
            user_id (str): User identifier
            title (str): Optional conversation title
            
        Returns:
            str: Conversation ID if successful, None otherwise
        """
        try:
            # Verify user exists
            user = self.db.get_user(user_id)
            if not user:
                self.logger.error(f"User not found: {user_id}")
                return None
            
            # Generate conversation ID and title
            conversation_id = generate_id("conv_")
            if not title:
                title = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Create conversation
            conversation = Conversation(
                conversation_id=conversation_id,
                user_id=user_id,
                title=title,
                metadata={
                    "created_by": "conversation_manager",
                    "initial_context": {},
                    "settings": {
                        "safety_enabled": True,
                        "context_length": 10
                    }
                }
            )
            
            if self.db.create_conversation(conversation):
                self.logger.info(f"Started conversation {conversation_id} for user {user_id}")
                return conversation_id
            else:
                self.logger.error(f"Failed to create conversation for user {user_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error starting conversation: {e}")
            return None
    
    def send_message(self, 
                    user_id: str, 
                    conversation_id: str, 
                    message_content: str,
                    context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send a message and get AI response
        
        Args:
            user_id (str): User identifier
            conversation_id (str): Conversation identifier
            message_content (str): User's message
            context (Dict): Additional context
            
        Returns:
            Dict: Response containing bot message and metadata
        """
        try:
            # Validate inputs
            if not self._validate_conversation_access(user_id, conversation_id):
                return {
                    "success": False,
                    "error": "Invalid conversation access",
                    "message": "You don't have access to this conversation."
                }
            
            # Safety check
            safety_result = self.safety_manager.assess_risk(message_content, user_id)
            risk_level = RiskLevel(safety_result.risk_level.value)
            
            # Store user message
            user_message = Message(
                message_id=generate_id("msg_"),
                conversation_id=conversation_id,
                user_id=user_id,
                content=message_content,
                message_type="user",
                risk_level=risk_level,
                metadata={
                    "safety_result": {
                        "risk_level": safety_result.risk_level.value,
                        "detected_keywords": safety_result.detected_keywords,
                        "confidence_score": safety_result.confidence_score
                    },
                    "context": context or {}
                }
            )
            
            if not self.db.add_message(user_message):
                return {
                    "success": False,
                    "error": "Failed to store message",
                    "message": "Sorry, there was an error processing your message."
                }
            
            # Handle crisis situations
            if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                crisis_response = self._handle_crisis_situation(user_id, conversation_id, safety_result)
                return crisis_response
            
            # Get conversation context
            conversation_context = self._build_conversation_context(conversation_id, context)
            
            # Generate AI response
            ai_response = self.conversation_engine.generate_response(
                user_message=message_content,
                user_id=user_id,
                context=conversation_context
            )
            
            # Store bot response
            bot_message = Message(
                message_id=generate_id("msg_"),
                conversation_id=conversation_id,
                user_id=user_id,
                content=ai_response.get("message", "I'm sorry, I couldn't generate a response."),
                message_type="bot",
                risk_level=RiskLevel.LOW,
                metadata={
                    "ai_metadata": ai_response.get("metadata", {}),
                    "generation_time": ai_response.get("generation_time", 0),
                    "model_used": ai_response.get("model_used", "unknown")
                }
            )
            
            if self.db.add_message(bot_message):
                return {
                    "success": True,
                    "message": bot_message.content,
                    "message_id": bot_message.message_id,
                    "timestamp": bot_message.timestamp.isoformat(),
                    "risk_level": risk_level.value,
                    "metadata": {
                        "safety_flags": safety_result.detected_keywords,
                        "response_type": ai_response.get("response_type", "normal"),
                        "confidence": ai_response.get("confidence", 0.5)
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to store response",
                    "message": "Sorry, there was an error saving the response."
                }
                
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return {
                "success": False,
                "error": "Internal error",
                "message": "Sorry, something went wrong. Please try again."
            }
    
    def get_conversation_history(self, 
                               user_id: str, 
                               conversation_id: str,
                               limit: int = 50) -> Dict[str, Any]:
        """
        Get conversation history
        
        Args:
            user_id (str): User identifier
            conversation_id (str): Conversation identifier
            limit (int): Maximum number of messages
            
        Returns:
            Dict: Conversation data with messages
        """
        try:
            if not self._validate_conversation_access(user_id, conversation_id):
                return {
                    "success": False,
                    "error": "Access denied",
                    "messages": []
                }
            
            messages = self.db.get_conversation_messages(conversation_id, limit)
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "message_count": len(messages),
                "messages": [
                    {
                        "message_id": msg.message_id,
                        "content": msg.content,
                        "message_type": msg.message_type,
                        "timestamp": msg.timestamp.isoformat(),
                        "risk_level": msg.risk_level.value,
                        "metadata": msg.metadata
                    }
                    for msg in messages
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting conversation history: {e}")
            return {
                "success": False,
                "error": "Failed to retrieve history",
                "messages": []
            }
    
    def get_user_conversations(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get user's conversation list
        
        Args:
            user_id (str): User identifier
            limit (int): Maximum number of conversations
            
        Returns:
            List[Dict]: List of conversation summaries
        """
        try:
            conversations = self.db.get_user_conversations(user_id, limit)
            
            return [
                {
                    "conversation_id": conv.conversation_id,
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat(),
                    "status": conv.status.value,
                    "metadata": conv.metadata
                }
                for conv in conversations
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting user conversations: {e}")
            return []
    
    def archive_conversation(self, user_id: str, conversation_id: str) -> bool:
        """
        Archive a conversation
        
        Args:
            user_id (str): User identifier
            conversation_id (str): Conversation identifier
            
        Returns:
            bool: Success status
        """
        try:
            if not self._validate_conversation_access(user_id, conversation_id):
                return False
            
            # Update conversation status
            conversations = self.db.get_user_conversations(user_id)
            for conv in conversations:
                if conv.conversation_id == conversation_id:
                    conv.status = ConversationStatus.ARCHIVED
                    conv.updated_at = datetime.now()
                    return self.db.update_conversation(conv)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error archiving conversation: {e}")
            return False
    
    def delete_conversation(self, user_id: str, conversation_id: str) -> bool:
        """
        Delete a conversation (soft delete)
        
        Args:
            user_id (str): User identifier
            conversation_id (str): Conversation identifier
            
        Returns:
            bool: Success status
        """
        try:
            if not self._validate_conversation_access(user_id, conversation_id):
                return False
            
            # Update conversation status
            conversations = self.db.get_user_conversations(user_id)
            for conv in conversations:
                if conv.conversation_id == conversation_id:
                    conv.status = ConversationStatus.DELETED
                    conv.updated_at = datetime.now()
                    return self.db.update_conversation(conv)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error deleting conversation: {e}")
            return False
    
    def get_conversation_analytics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get conversation analytics for a user
        
        Args:
            user_id (str): User identifier
            days (int): Number of days to analyze
            
        Returns:
            Dict: Analytics data
        """
        try:
            stats = self.db.get_user_stats(user_id)
            
            # Add additional analytics
            conversations = self.db.get_user_conversations(user_id, limit=100)
            recent_conversations = [
                conv for conv in conversations
                if conv.updated_at > datetime.now() - timedelta(days=days)
            ]
            
            return {
                "total_conversations": stats.get("conversation_count", 0),
                "total_messages": stats.get("message_count", 0),
                "recent_conversations": len(recent_conversations),
                "risk_distribution": stats.get("risk_distribution", {}),
                "average_messages_per_conversation": (
                    stats.get("message_count", 0) / max(stats.get("conversation_count", 1), 1)
                ),
                "period_days": days
            }
            
        except Exception as e:
            self.logger.error(f"Error getting analytics: {e}")
            return {}
    
    def _validate_conversation_access(self, user_id: str, conversation_id: str) -> bool:
        """
        Validate that user has access to conversation
        
        Args:
            user_id (str): User identifier
            conversation_id (str): Conversation identifier
            
        Returns:
            bool: Access granted
        """
        try:
            conversations = self.db.get_user_conversations(user_id)
            return any(conv.conversation_id == conversation_id for conv in conversations)
        except Exception as e:
            self.logger.error(f"Error validating conversation access: {e}")
            return False
    
    def _build_conversation_context(self, conversation_id: str, additional_context: Dict = None) -> Dict[str, Any]:
        """
        Build context for AI response generation
        
        Args:
            conversation_id (str): Conversation identifier
            additional_context (Dict): Additional context data
            
        Returns:
            Dict: Context for AI model
        """
        try:
            # Get recent messages for context
            messages = self.db.get_conversation_messages(conversation_id, limit=10)
            
            # Build conversation history
            history = []
            for msg in messages[-6:]:  # Last 6 messages for context
                history.append({
                    "role": "user" if msg.message_type == "user" else "assistant",
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "risk_level": msg.risk_level.value
                })
            
            context = {
                "conversation_id": conversation_id,
                "message_history": history,
                "conversation_length": len(messages),
                "last_interaction": messages[-1].timestamp.isoformat() if messages else None
            }
            
            # Add additional context
            if additional_context:
                context.update(additional_context)
            
            return context
            
        except Exception as e:
            self.logger.error(f"Error building context: {e}")
            return {"conversation_id": conversation_id}
    
    def _handle_crisis_situation(self, user_id: str, conversation_id: str, safety_result: Dict) -> Dict[str, Any]:
        """
        Handle crisis situations with appropriate responses
        
        Args:
            user_id (str): User identifier
            conversation_id (str): Conversation identifier
            safety_result (Dict): Safety assessment result
            
        Returns:
            Dict: Crisis response
        """
        try:
            # Trigger emergency protocol
            emergency_response = self.safety_manager.trigger_emergency_protocol(
                user_id, safety_result
            )
            
            # Store crisis response message
            crisis_message = Message(
                message_id=generate_id("msg_"),
                conversation_id=conversation_id,
                user_id=user_id,
                content=emergency_response.get("message", "I'm concerned about you. Please reach out for help."),
                message_type="bot",
                risk_level=RiskLevel.CRITICAL,
                metadata={
                    "crisis_response": True,
                    "emergency_contacts": emergency_response.get("emergency_contacts", []),
                    "resources": emergency_response.get("resources", []),
                    "safety_result": safety_result
                }
            )
            
            self.db.add_message(crisis_message)
            
            return {
                "success": True,
                "message": crisis_message.content,
                "message_id": crisis_message.message_id,
                "timestamp": crisis_message.timestamp.isoformat(),
                "risk_level": "critical",
                "crisis_response": True,
                "emergency_contacts": emergency_response.get("emergency_contacts", []),
                "resources": emergency_response.get("resources", []),
                "metadata": {
                    "safety_flags": safety_result.get("flags", []),
                    "response_type": "crisis",
                    "immediate_help_needed": True
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error handling crisis: {e}")
            return {
                "success": True,
                "message": "I'm concerned about you. Please reach out to a mental health professional or crisis hotline immediately.",
                "crisis_response": True,
                "emergency_contacts": [
                    {"name": "South African Depression and Anxiety Group", "number": "0800 567 567"},
                    {"name": "Lifeline", "number": "0861 322 322"}
                ]
            }
    
    def cleanup_old_data(self, days: int = 90) -> Dict[str, int]:
        """
        Clean up old conversation data
        
        Args:
            days (int): Days to keep data
            
        Returns:
            Dict: Cleanup statistics
        """
        try:
            # Clean up expired sessions
            expired_sessions = self.db.cleanup_expired_sessions()
            
            # Archive old conversations (implementation would depend on requirements)
            # For now, just return session cleanup count
            
            return {
                "expired_sessions_removed": expired_sessions,
                "conversations_archived": 0,  # Placeholder
                "cleanup_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return {"error": str(e)}
    
    def close(self) -> None:
        """
        Close all connections and cleanup resources
        """
        try:
            self.db.close()
            self.logger.info("ConversationManager closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing ConversationManager: {e}")


if __name__ == "__main__":
    # Test conversation manager
    import tempfile
    import os
    
    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        test_db_path = tmp_file.name
    
    try:
        # Initialize conversation manager
        conv_manager = ConversationManager(db_path=test_db_path)
        
        # Test user creation (would normally be done by user manager)
        from models.database import User, generate_id, hash_password
        
        test_user = User(
            user_id=generate_id("user_"),
            username="test_user",
            email="test@example.com",
            password_hash=hash_password("test_password")
        )
        
        conv_manager.db.create_user(test_user)
        
        # Test conversation flow
        conv_id = conv_manager.start_conversation(test_user.user_id, "Test Chat")
        print(f"Started conversation: {conv_id}")
        
        # Send test message
        response = conv_manager.send_message(
            test_user.user_id, 
            conv_id, 
            "Hello, I'm feeling a bit anxious today."
        )
        print(f"Response: {response}")
        
        # Get conversation history
        history = conv_manager.get_conversation_history(test_user.user_id, conv_id)
        print(f"History: {len(history.get('messages', []))} messages")
        
        # Get analytics
        analytics = conv_manager.get_conversation_analytics(test_user.user_id)
        print(f"Analytics: {analytics}")
        
    finally:
        # Cleanup
        try:
            conv_manager.close()
            os.unlink(test_db_path)
        except:
            pass