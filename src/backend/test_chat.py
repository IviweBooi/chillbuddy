#!/usr/bin/env python3
"""
ChillBuddy Backend Chat Test
A simple command-line interface to test the conversation system.
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conversation_manager import ConversationManager
from models.database import DatabaseManager, User, generate_id, hash_password
from user_manager import UserManager

def create_test_user(db_manager):
    """
    Create or find a test user for the chat session in the database
    
    Args:
        db_manager: DatabaseManager instance
        
    Returns:
        str: User ID if successful, None if failed
    """
    try:
        # Use a unique email with timestamp to avoid constraint errors
        import time
        timestamp = int(time.time())
        user_id = generate_id("user_")
        test_user = User(
            user_id=user_id,
            username=f"test_user_{timestamp}",
            email=f"test_{timestamp}@example.com",
            password_hash=hash_password("test_password")
        )
        
        if db_manager.create_user(test_user):
            print(f"Created new test user: {test_user.username}")
            return user_id
        else:
            print("Failed to create test user in database")
            return None
            
    except Exception as e:
        print(f"Error creating test user: {e}")
        return None

def main():
    """Main chat loop."""
    print("\n" + "="*50)
    print("🤖 Welcome to ChillBuddy Backend Chat Test!")
    print("="*50)
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("Type 'new' to start a new conversation.")
    print("Type 'history' to see conversation history.")
    print("-"*50)
    
    # Initialize components
    try:
        conv_manager = ConversationManager()
        db_manager = DatabaseManager()
        user_id = create_test_user(db_manager)
        
        if not user_id:
            print("❌ Failed to create or find test user")
            return
            
        conversation_id = None
        
        print(f"\n✅ ChillBuddy backend initialized successfully!")
        print(f"👤 User ID: {user_id}")
        
    except Exception as e:
        print(f"❌ Error initializing ChillBuddy: {e}")
        return
    
    # Main chat loop
    while True:
        try:
            # Get user input
            user_input = input("\n💬 You: ").strip()
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Thanks for testing ChillBuddy! Take care!")
                break
            
            elif user_input.lower() == 'new':
                # Start new conversation
                conversation_id = conv_manager.start_conversation(
                    user_id=user_id,
                    title=f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                print(f"\n🆕 Started new conversation: {conversation_id}")
                print("🤖 ChillBuddy: Hello! I'm ChillBuddy, your mental health support companion. How are you feeling today?")
                continue
            
            elif user_input.lower() == 'history':
                if conversation_id:
                    try:
                        # Get conversation history
                        db = DatabaseManager()
                        messages = db.get_conversation_messages(conversation_id, limit=10)
                        
                        print("\n📜 Recent conversation history:")
                        print("-"*30)
                        for msg in messages[-10:]:  # Show last 10 messages
                            sender = "You" if msg.message_type == "user" else "ChillBuddy"
                            timestamp = msg.timestamp.strftime("%H:%M")
                            print(f"[{timestamp}] {sender}: {msg.content}")
                        print("-"*30)
                    except Exception as e:
                        print(f"❌ Error getting history: {e}")
                else:
                    print("\n⚠️ No active conversation. Type 'new' to start one.")
                continue
            
            elif not user_input:
                continue
            
            # Start conversation if none exists
            if not conversation_id:
                conversation_id = conv_manager.start_conversation(
                    user_id=user_id,
                    title=f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                print(f"\n🆕 Started conversation: {conversation_id}")
            
            # Send message and get response
            print("\n🤖 ChillBuddy is thinking...")
            
            response = conv_manager.send_message(
                user_id=user_id,
                conversation_id=conversation_id,
                message_content=user_input
            )
            
            # Display response
            print(f"\n🤖 ChillBuddy: {response['message']}")
            
            # Show risk level if detected
            if response.get('risk_level') and response['risk_level'] != 'low':
                risk_emoji = "⚠️" if response['risk_level'] == 'medium' else "🚨"
                print(f"\n{risk_emoji} Risk Level: {response['risk_level'].upper()}")
            
            # Show conversation ID for reference
            print(f"\n💭 Conversation ID: {conversation_id}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    main()