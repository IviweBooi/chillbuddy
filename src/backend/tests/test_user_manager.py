# Unit Tests for UserManager Class
#
# This file contains comprehensive tests for:
# - User profile management
# - Session management
# - Authentication and security
# - Data validation and error handling

import unittest
import tempfile
import os
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Import test configuration
from .test_config import BaseTestCase, MockTestCase, PerformanceTestCase

# Import the module under test
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from user_manager import UserManager, UserProfile, UserSession, UserStatus, SessionStatus
    from utils import hash_password, verify_password, generate_user_id
except ImportError as e:
    print(f"Import error: {e}")
    UserManager = None
    UserProfile = None
    UserSession = None
    UserStatus = None
    SessionStatus = None
    hash_password = None
    verify_password = None
    generate_user_id = None

class TestUserManager(BaseTestCase):
    """Test cases for UserManager class"""
    
    def setUp(self):
        """Set up test environment"""
        super().setUp()
        
        if UserManager:
            self.user_manager = UserManager(data_dir=self.temp_dir)
        else:
            self.skipTest("UserManager not available")
    
    def test_user_manager_initialization(self):
        """Test UserManager initialization"""
        self.assertIsNotNone(self.user_manager)
        self.assertEqual(self.user_manager.data_dir, self.temp_dir)
        self.assertTrue(os.path.exists(self.user_manager.users_file))
        self.assertTrue(os.path.exists(self.user_manager.sessions_file))
    
    def test_create_user_success(self):
        """Test successful user creation"""
        username = "testuser"
        email = "test@example.com"
        password = "securepassword123"
        
        result = self.user_manager.create_user(username, email, password)
        
        self.assertTrue(result["success"])
        self.assertIn("user_id", result)
        self.assertIn("message", result)
        
        # Verify user was actually created
        user_id = result["user_id"]
        user_data = self.user_manager.load_user_data(user_id)
        self.assertIsNotNone(user_data)
        self.assertEqual(user_data["username"], username)
        self.assertEqual(user_data["email"], email)
    
    def test_create_user_duplicate_email(self):
        """Test user creation with duplicate email"""
        email = "duplicate@example.com"
        
        # Create first user
        result1 = self.user_manager.create_user("user1", email, "password1")
        self.assertTrue(result1["success"])
        
        # Try to create second user with same email
        result2 = self.user_manager.create_user("user2", email, "password2")
        self.assertFalse(result2["success"])
        self.assertIn("already exists", result2["error"]["message"].lower())
    
    def test_create_user_invalid_email(self):
        """Test user creation with invalid email"""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user..name@example.com",
            ""
        ]
        
        for email in invalid_emails:
            with self.subTest(email=email):
                result = self.user_manager.create_user("testuser", email, "password")
                self.assertFalse(result["success"])
                self.assertIn("invalid", result["error"]["message"].lower())
    
    def test_create_user_weak_password(self):
        """Test user creation with weak password"""
        weak_passwords = [
            "123",
            "password",
            "abc",
            "",
            "   "
        ]
        
        for password in weak_passwords:
            with self.subTest(password=password):
                result = self.user_manager.create_user("testuser", "test@example.com", password)
                self.assertFalse(result["success"])
                self.assertIn("password", result["error"]["message"].lower())
    
    def test_authenticate_user_success(self):
        """Test successful user authentication"""
        email = "auth@example.com"
        password = "securepassword123"
        
        # Create user first
        create_result = self.user_manager.create_user("authuser", email, password)
        self.assertTrue(create_result["success"])
        
        # Test authentication
        auth_result = self.user_manager.authenticate_user(email, password)
        self.assertTrue(auth_result["success"])
        self.assertIn("user_id", auth_result)
        self.assertEqual(auth_result["user_id"], create_result["user_id"])
    
    def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password"""
        email = "auth@example.com"
        password = "correctpassword"
        wrong_password = "wrongpassword"
        
        # Create user
        self.user_manager.create_user("authuser", email, password)
        
        # Test authentication with wrong password
        auth_result = self.user_manager.authenticate_user(email, wrong_password)
        self.assertFalse(auth_result["success"])
        self.assertIn("invalid", auth_result["error"]["message"].lower())
    
    def test_authenticate_user_nonexistent(self):
        """Test authentication with non-existent user"""
        auth_result = self.user_manager.authenticate_user("nonexistent@example.com", "password")
        self.assertFalse(auth_result["success"])
        self.assertIn("not found", auth_result["error"]["message"].lower())
    
    def test_create_session(self):
        """Test session creation"""
        # Create user first
        create_result = self.user_manager.create_user("sessionuser", "session@example.com", "password")
        user_id = create_result["user_id"]
        
        # Create session
        session_result = self.user_manager.create_session(user_id)
        self.assertTrue(session_result["success"])
        self.assertIn("session_id", session_result)
        
        # Verify session exists
        session_id = session_result["session_id"]
        session_data = self.user_manager.get_session(session_id)
        self.assertIsNotNone(session_data)
        self.assertEqual(session_data["user_id"], user_id)
        self.assertEqual(session_data["status"], SessionStatus.ACTIVE.value)
    
    def test_validate_session_active(self):
        """Test validation of active session"""
        # Create user and session
        create_result = self.user_manager.create_user("sessionuser", "session@example.com", "password")
        user_id = create_result["user_id"]
        session_result = self.user_manager.create_session(user_id)
        session_id = session_result["session_id"]
        
        # Validate session
        is_valid = self.user_manager.validate_session(session_id)
        self.assertTrue(is_valid)
    
    def test_validate_session_expired(self):
        """Test validation of expired session"""
        # Create user and session
        create_result = self.user_manager.create_user("sessionuser", "session@example.com", "password")
        user_id = create_result["user_id"]
        session_result = self.user_manager.create_session(user_id)
        session_id = session_result["session_id"]
        
        # Manually expire the session
        self.user_manager.end_session(session_id)
        
        # Validate session
        is_valid = self.user_manager.validate_session(session_id)
        self.assertFalse(is_valid)
    
    def test_update_user_profile(self):
        """Test user profile updates"""
        # Create user
        create_result = self.user_manager.create_user("updateuser", "update@example.com", "password")
        user_id = create_result["user_id"]
        
        # Update profile
        updates = {
            "age_range": "26-35",
            "location": "Johannesburg, South Africa",
            "preferred_language": "af"
        }
        
        update_result = self.user_manager.update_user_profile(user_id, updates)
        self.assertTrue(update_result["success"])
        
        # Verify updates
        user_data = self.user_manager.load_user_data(user_id)
        self.assertEqual(user_data["age_range"], "26-35")
        self.assertEqual(user_data["location"], "Johannesburg, South Africa")
        self.assertEqual(user_data["preferred_language"], "af")
    
    def test_update_user_profile_invalid_data(self):
        """Test user profile updates with invalid data"""
        # Create user
        create_result = self.user_manager.create_user("updateuser", "update@example.com", "password")
        user_id = create_result["user_id"]
        
        # Try to update with invalid data
        invalid_updates = {
            "age_range": "invalid-age",
            "email": "invalid-email",
            "preferred_language": "invalid-lang"
        }
        
        update_result = self.user_manager.update_user_profile(user_id, invalid_updates)
        self.assertFalse(update_result["success"])
    
    def test_get_user_analytics(self):
        """Test user analytics generation"""
        # Create user
        create_result = self.user_manager.create_user("analyticsuser", "analytics@example.com", "password")
        user_id = create_result["user_id"]
        
        # Get analytics
        analytics = self.user_manager.get_user_analytics(user_id)
        
        self.assertIsNotNone(analytics)
        self.assertIn("total_sessions", analytics)
        self.assertIn("total_conversations", analytics)
        self.assertIn("account_age_days", analytics)
        self.assertIn("last_active", analytics)
        self.assertIn("engagement_score", analytics)
    
    def test_delete_user_account(self):
        """Test user account deletion"""
        # Create user
        create_result = self.user_manager.create_user("deleteuser", "delete@example.com", "password")
        user_id = create_result["user_id"]
        
        # Verify user exists
        user_data = self.user_manager.load_user_data(user_id)
        self.assertIsNotNone(user_data)
        
        # Delete user
        delete_result = self.user_manager.delete_user_account(user_id)
        self.assertTrue(delete_result["success"])
        
        # Verify user is deleted
        user_data = self.user_manager.load_user_data(user_id)
        self.assertIsNone(user_data)
    
    def test_change_password(self):
        """Test password change functionality"""
        email = "changepass@example.com"
        old_password = "oldpassword123"
        new_password = "newpassword456"
        
        # Create user
        create_result = self.user_manager.create_user("changeuser", email, old_password)
        user_id = create_result["user_id"]
        
        # Change password
        change_result = self.user_manager.change_password(user_id, old_password, new_password)
        self.assertTrue(change_result["success"])
        
        # Test authentication with new password
        auth_result = self.user_manager.authenticate_user(email, new_password)
        self.assertTrue(auth_result["success"])
        
        # Test that old password no longer works
        old_auth_result = self.user_manager.authenticate_user(email, old_password)
        self.assertFalse(old_auth_result["success"])
    
    def test_change_password_wrong_current(self):
        """Test password change with wrong current password"""
        email = "changepass@example.com"
        password = "correctpassword"
        wrong_current = "wrongcurrent"
        new_password = "newpassword456"
        
        # Create user
        create_result = self.user_manager.create_user("changeuser", email, password)
        user_id = create_result["user_id"]
        
        # Try to change password with wrong current password
        change_result = self.user_manager.change_password(user_id, wrong_current, new_password)
        self.assertFalse(change_result["success"])
        self.assertIn("current password", change_result["error"]["message"].lower())

class TestUserManagerPerformance(PerformanceTestCase):
    """Performance tests for UserManager"""
    
    def setUp(self):
        """Set up performance test environment"""
        super().setUp()
        
        if UserManager:
            self.user_manager = UserManager(data_dir=self.temp_dir)
        else:
            self.skipTest("UserManager not available")
    
    def test_user_creation_performance(self):
        """Test user creation performance"""
        def create_user():
            return self.user_manager.create_user(
                f"user{datetime.now().timestamp()}",
                f"user{datetime.now().timestamp()}@example.com",
                "password123"
            )
        
        # User creation should complete within 1 second
        result = self.assert_execution_time_under(create_user, 1.0)
        self.assertTrue(result["success"])
    
    def test_authentication_performance(self):
        """Test authentication performance"""
        # Create a user first
        email = "perftest@example.com"
        password = "password123"
        self.user_manager.create_user("perfuser", email, password)
        
        def authenticate():
            return self.user_manager.authenticate_user(email, password)
        
        # Authentication should complete within 0.5 seconds
        result = self.assert_execution_time_under(authenticate, 0.5)
        self.assertTrue(result["success"])
    
    def test_bulk_user_operations(self):
        """Test performance with multiple users"""
        num_users = 10
        
        def create_multiple_users():
            results = []
            for i in range(num_users):
                result = self.user_manager.create_user(
                    f"bulkuser{i}",
                    f"bulk{i}@example.com",
                    "password123"
                )
                results.append(result)
            return results
        
        # Creating 10 users should complete within 5 seconds
        results = self.assert_execution_time_under(create_multiple_users, 5.0)
        
        # Verify all users were created successfully
        for result in results:
            self.assertTrue(result["success"])

class TestUserManagerMocked(MockTestCase):
    """Test UserManager with mocked dependencies"""
    
    def setUp(self):
        """Set up mocked test environment"""
        super().setUp()
        
        if UserManager:
            self.user_manager = UserManager(data_dir=self.temp_dir)
        else:
            self.skipTest("UserManager not available")
    
    @patch('user_manager.os.path.exists')
    @patch('user_manager.open')
    def test_load_user_data_file_not_found(self, mock_open, mock_exists):
        """Test loading user data when file doesn't exist"""
        mock_exists.return_value = False
        
        result = self.user_manager.load_user_data("nonexistent-user")
        self.assertIsNone(result)
    
    @patch('user_manager.json.load')
    @patch('user_manager.open')
    def test_load_user_data_corrupted_file(self, mock_open, mock_json_load):
        """Test loading user data from corrupted file"""
        mock_json_load.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        
        result = self.user_manager.load_user_data("test-user")
        self.assertIsNone(result)
    
    @patch('user_manager.json.dump')
    @patch('user_manager.open')
    def test_save_user_data_write_error(self, mock_open, mock_json_dump):
        """Test saving user data with write error"""
        mock_json_dump.side_effect = IOError("Write failed")
        
        user_data = self.create_test_user_profile()
        result = self.user_manager.save_user_data("test-user", user_data)
        self.assertFalse(result)

class TestUserProfile(BaseTestCase):
    """Test UserProfile dataclass"""
    
    def test_user_profile_creation(self):
        """Test UserProfile creation"""
        if not UserProfile:
            self.skipTest("UserProfile not available")
        
        profile = UserProfile(
            user_id="test-123",
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            age_range="18-25",
            location="Cape Town",
            preferred_language="en",
            created_at=datetime.now().isoformat(),
            last_active=datetime.now().isoformat(),
            status=UserStatus.ACTIVE,
            privacy_settings={"analytics": True}
        )
        
        self.assertEqual(profile.user_id, "test-123")
        self.assertEqual(profile.username, "testuser")
        self.assertEqual(profile.email, "test@example.com")
        self.assertEqual(profile.status, UserStatus.ACTIVE)
    
    def test_user_profile_to_dict(self):
        """Test UserProfile conversion to dictionary"""
        if not UserProfile:
            self.skipTest("UserProfile not available")
        
        profile = UserProfile(
            user_id="test-123",
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            age_range="18-25",
            location="Cape Town",
            preferred_language="en",
            created_at=datetime.now().isoformat(),
            last_active=datetime.now().isoformat(),
            status=UserStatus.ACTIVE,
            privacy_settings={"analytics": True}
        )
        
        profile_dict = profile.to_dict()
        
        self.assertIsInstance(profile_dict, dict)
        self.assertEqual(profile_dict["user_id"], "test-123")
        self.assertEqual(profile_dict["username"], "testuser")
        self.assertEqual(profile_dict["status"], UserStatus.ACTIVE.value)

class TestUserSession(BaseTestCase):
    """Test UserSession dataclass"""
    
    def test_user_session_creation(self):
        """Test UserSession creation"""
        if not UserSession:
            self.skipTest("UserSession not available")
        
        session = UserSession(
            session_id="session-123",
            user_id="user-123",
            created_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
            expires_at=(datetime.now() + timedelta(hours=24)).isoformat(),
            status=SessionStatus.ACTIVE,
            ip_address="127.0.0.1",
            user_agent="Test Browser"
        )
        
        self.assertEqual(session.session_id, "session-123")
        self.assertEqual(session.user_id, "user-123")
        self.assertEqual(session.status, SessionStatus.ACTIVE)
    
    def test_user_session_is_expired(self):
        """Test UserSession expiration check"""
        if not UserSession:
            self.skipTest("UserSession not available")
        
        # Create expired session
        expired_session = UserSession(
            session_id="session-123",
            user_id="user-123",
            created_at=(datetime.now() - timedelta(hours=25)).isoformat(),
            last_activity=(datetime.now() - timedelta(hours=25)).isoformat(),
            expires_at=(datetime.now() - timedelta(hours=1)).isoformat(),
            status=SessionStatus.ACTIVE,
            ip_address="127.0.0.1",
            user_agent="Test Browser"
        )
        
        self.assertTrue(expired_session.is_expired())
        
        # Create active session
        active_session = UserSession(
            session_id="session-456",
            user_id="user-123",
            created_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
            expires_at=(datetime.now() + timedelta(hours=1)).isoformat(),
            status=SessionStatus.ACTIVE,
            ip_address="127.0.0.1",
            user_agent="Test Browser"
        )
        
        self.assertFalse(active_session.is_expired())

if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)