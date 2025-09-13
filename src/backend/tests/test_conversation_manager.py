import unittest
import tempfile
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conversation_manager import ConversationManager
from models.database import DatabaseManager, User, Conversation, Message, ConversationStatus
from tests.test_config import BaseTestCase

class TestConversationManager(BaseTestCase):
    def setUp(self):
        """Set up test environment"""
        super().setUp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        
        # Create test database
        self.db_manager = DatabaseManager(self.db_path)
        
        # Create test user
        self.test_user = User(
            user_id="test_user_123",
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.now(),
            last_active=datetime.now()
        )
        self.db_manager.create_user(self.test_user)
        
        # Mock conversation engine
        with patch('conversation_manager.ConversationEngine') as mock_engine:
            self.mock_engine_instance = MagicMock()
            mock_engine.return_value = self.mock_engine_instance
            self.conversation_manager = ConversationManager(self.db_path)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_start_conversation(self):
        """Test starting a new conversation"""
        conversation_id = self.conversation_manager.start_conversation(
            user_id=self.test_user.user_id,
            title="Test Conversation"
        )
        
        self.assertIsNotNone(conversation_id)
        
        # Verify conversation was created by checking user conversations
        conversations = self.db_manager.get_user_conversations(self.test_user.user_id)
        self.assertEqual(len(conversations), 1)
        conversation = conversations[0]
        self.assertEqual(conversation.user_id, self.test_user.user_id)
        self.assertEqual(conversation.title, "Test Conversation")
        self.assertEqual(conversation.status, ConversationStatus.ACTIVE)
    
    def test_send_message(self):
        """Test sending a message in a conversation"""
        # Start conversation
        conversation_id = self.conversation_manager.start_conversation(
            user_id=self.test_user.user_id,
            title="Test Chat"
        )
        
        # Mock AI response
        self.mock_engine_instance.process_message.return_value = {
            'response': 'Hello! How can I help you today?',
            'confidence': 0.95,
            'safety_check': True
        }
        
        # Send message
        response = self.conversation_manager.send_message(
            conversation_id=conversation_id,
            user_message="Hello",
            user_id=self.test_user.user_id
        )
        
        self.assertIsNotNone(response)
        self.assertEqual(response['response'], 'Hello! How can I help you today?')
        
        # Verify messages were stored
        messages = self.db_manager.get_conversation_messages(conversation_id)
        self.assertEqual(len(messages), 2)  # User message + AI response
        
        user_msg = next(msg for msg in messages if msg.sender_type == 'user')
        ai_msg = next(msg for msg in messages if msg.sender_type == 'assistant')
        
        self.assertEqual(user_msg.content, "Hello")
        self.assertEqual(ai_msg.content, 'Hello! How can I help you today?')
    
    def test_get_conversation_history(self):
        """Test retrieving conversation history"""
        # Start conversation and send messages
        conversation_id = self.conversation_manager.start_conversation(
            user_id=self.test_user.user_id,
            title="History Test"
        )
        
        self.mock_engine_instance.process_message.return_value = {
            'response': 'AI response',
            'confidence': 0.9,
            'safety_check': True
        }
        
        self.conversation_manager.send_message(
            conversation_id=conversation_id,
            user_message="Test message",
            user_id=self.test_user.user_id
        )
        
        # Get history
        history = self.conversation_manager.get_conversation_history(
            conversation_id=conversation_id,
            user_id=self.test_user.user_id
        )
        
        self.assertIsNotNone(history)
        self.assertEqual(len(history['messages']), 2)
        self.assertEqual(history['conversation']['title'], "History Test")
    
    def test_get_user_conversations(self):
        """Test retrieving user's conversations"""
        # Create multiple conversations
        conv1_id = self.conversation_manager.start_conversation(
            user_id=self.test_user.user_id,
            title="Conversation 1"
        )
        conv2_id = self.conversation_manager.start_conversation(
            user_id=self.test_user.user_id,
            title="Conversation 2"
        )
        
        # Get user conversations
        conversations = self.conversation_manager.get_user_conversations(
            user_id=self.test_user.user_id
        )
        
        self.assertEqual(len(conversations), 2)
        titles = [conv['title'] for conv in conversations]
        self.assertIn("Conversation 1", titles)
        self.assertIn("Conversation 2", titles)

if __name__ == '__main__':
    unittest.main()