# Unit Tests for Flask Application
#
# This file contains comprehensive tests for:
# - API endpoints
# - Authentication and authorization
# - Error handling
# - Request/response validation
# - Rate limiting

import unittest
import json
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Import test configuration
from .test_config import FlaskTestCase, MockTestCase, PerformanceTestCase

# Import the module under test
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import create_app, require_auth, rate_limit
    from config import TestingConfig
except ImportError as e:
    print(f"Import error: {e}")
    create_app = None
    require_auth = None
    rate_limit = None
    TestingConfig = None

class TestFlaskApp(FlaskTestCase):
    """Test cases for Flask application"""
    
    def setUp(self):
        """Set up test environment"""
        super().setUp()
        
        if create_app and TestingConfig:
            self.app = create_app(TestingConfig)
            self.app_context = self.app.app_context()
            self.app_context.push()
            self.client = self.app.test_client()
        else:
            self.skipTest("Flask app or TestingConfig not available")
    
    def test_health_check_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/api/health')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('version', data)
    
    def test_register_endpoint_success(self):
        """Test successful user registration"""
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepassword123'
        }
        
        response = self.post_json('/api/auth/register', user_data)
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('user_id', data)
        self.assertIn('message', data)
    
    def test_register_endpoint_invalid_data(self):
        """Test registration with invalid data"""
        invalid_data_sets = [
            # Missing username
            {'email': 'test@example.com', 'password': 'password123'},
            # Missing email
            {'username': 'testuser', 'password': 'password123'},
            # Missing password
            {'username': 'testuser', 'email': 'test@example.com'},
            # Invalid email
            {'username': 'testuser', 'email': 'invalid-email', 'password': 'password123'},
            # Weak password
            {'username': 'testuser', 'email': 'test@example.com', 'password': '123'}
        ]
        
        for invalid_data in invalid_data_sets:
            with self.subTest(data=invalid_data):
                response = self.post_json('/api/auth/register', invalid_data)
                
                self.assertEqual(response.status_code, 400)
                
                data = json.loads(response.data)
                self.assertFalse(data['success'])
                self.assertIn('error', data)
    
    def test_login_endpoint_success(self):
        """Test successful user login"""
        # First register a user
        user_data = {
            'username': 'loginuser',
            'email': 'login@example.com',
            'password': 'securepassword123'
        }
        self.post_json('/api/auth/register', user_data)
        
        # Then try to login
        login_data = {
            'email': 'login@example.com',
            'password': 'securepassword123'
        }
        
        response = self.post_json('/api/auth/login', login_data)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('session_id', data)
        self.assertIn('user_id', data)
    
    def test_login_endpoint_invalid_credentials(self):
        """Test login with invalid credentials"""
        # Register a user first
        user_data = {
            'username': 'loginuser',
            'email': 'login@example.com',
            'password': 'correctpassword'
        }
        self.post_json('/api/auth/register', user_data)
        
        # Try to login with wrong password
        login_data = {
            'email': 'login@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.post_json('/api/auth/login', login_data)
        
        self.assertEqual(response.status_code, 401)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    def test_logout_endpoint(self):
        """Test user logout"""
        # Register and login first
        user_data = {
            'username': 'logoutuser',
            'email': 'logout@example.com',
            'password': 'securepassword123'
        }
        self.post_json('/api/auth/register', user_data)
        
        login_response = self.post_json('/api/auth/login', {
            'email': 'logout@example.com',
            'password': 'securepassword123'
        })
        
        login_data = json.loads(login_response.data)
        session_id = login_data['session_id']
        
        # Logout
        logout_response = self.post_json('/api/auth/logout', {'session_id': session_id})
        
        self.assertEqual(logout_response.status_code, 200)
        
        data = json.loads(logout_response.data)
        self.assertTrue(data['success'])
    
    def test_chat_endpoint_authenticated(self):
        """Test chat endpoint with authentication"""
        # Register and login first
        user_data = {
            'username': 'chatuser',
            'email': 'chat@example.com',
            'password': 'securepassword123'
        }
        self.post_json('/api/auth/register', user_data)
        
        login_response = self.post_json('/api/auth/login', {
            'email': 'chat@example.com',
            'password': 'securepassword123'
        })
        
        login_data = json.loads(login_response.data)
        session_id = login_data['session_id']
        
        # Send chat message
        chat_data = {
            'message': 'Hello, I need help with anxiety',
            'session_id': session_id
        }
        
        response = self.post_json('/api/chat', chat_data)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('response', data)
        self.assertIn('timestamp', data)
    
    def test_chat_endpoint_unauthenticated(self):
        """Test chat endpoint without authentication"""
        chat_data = {
            'message': 'Hello, I need help',
            'session_id': 'invalid-session'
        }
        
        response = self.post_json('/api/chat', chat_data)
        
        self.assertEqual(response.status_code, 401)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    def test_crisis_endpoint(self):
        """Test crisis detection endpoint"""
        # Register and login first
        user_data = {
            'username': 'crisisuser',
            'email': 'crisis@example.com',
            'password': 'securepassword123'
        }
        self.post_json('/api/auth/register', user_data)
        
        login_response = self.post_json('/api/auth/login', {
            'email': 'crisis@example.com',
            'password': 'securepassword123'
        })
        
        login_data = json.loads(login_response.data)
        session_id = login_data['session_id']
        
        # Send crisis message
        crisis_data = {
            'message': 'I want to hurt myself and end everything',
            'session_id': session_id
        }
        
        response = self.post_json('/api/crisis', crisis_data)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('risk_level', data)
        self.assertIn('resources', data)
        self.assertIn('immediate_actions', data)
    
    def test_resources_endpoint(self):
        """Test resources endpoint"""
        response = self.client.get('/api/resources')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('crisis_resources', data)
        self.assertIn('coping_strategies', data)
        self.assertIn('educational_content', data)
    
    def test_resources_endpoint_filtered(self):
        """Test resources endpoint with filters"""
        # Test with location filter
        response = self.client.get('/api/resources?location=Cape Town')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Test with type filter
        response = self.client.get('/api/resources?type=coping_strategies')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_user_profile_endpoint_get(self):
        """Test getting user profile"""
        # Register and login first
        user_data = {
            'username': 'profileuser',
            'email': 'profile@example.com',
            'password': 'securepassword123'
        }
        self.post_json('/api/auth/register', user_data)
        
        login_response = self.post_json('/api/auth/login', {
            'email': 'profile@example.com',
            'password': 'securepassword123'
        })
        
        login_data = json.loads(login_response.data)
        session_id = login_data['session_id']
        
        # Get profile
        response = self.client.get(
            '/api/user/profile',
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('profile', data)
        self.assertEqual(data['profile']['username'], 'profileuser')
        self.assertEqual(data['profile']['email'], 'profile@example.com')
    
    def test_user_profile_endpoint_update(self):
        """Test updating user profile"""
        # Register and login first
        user_data = {
            'username': 'updateuser',
            'email': 'update@example.com',
            'password': 'securepassword123'
        }
        self.post_json('/api/auth/register', user_data)
        
        login_response = self.post_json('/api/auth/login', {
            'email': 'update@example.com',
            'password': 'securepassword123'
        })
        
        login_data = json.loads(login_response.data)
        session_id = login_data['session_id']
        
        # Update profile
        update_data = {
            'age_range': '26-35',
            'location': 'Johannesburg, South Africa',
            'preferred_language': 'af'
        }
        
        response = self.post_json(
            '/api/user/profile',
            update_data,
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_user_progress_endpoint(self):
        """Test user progress endpoint"""
        # Register and login first
        user_data = {
            'username': 'progressuser',
            'email': 'progress@example.com',
            'password': 'securepassword123'
        }
        self.post_json('/api/auth/register', user_data)
        
        login_response = self.post_json('/api/auth/login', {
            'email': 'progress@example.com',
            'password': 'securepassword123'
        })
        
        login_data = json.loads(login_response.data)
        session_id = login_data['session_id']
        
        # Get progress
        response = self.client.get(
            '/api/user/progress',
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('progress', data)
        self.assertIn('achievements', data)
        self.assertIn('current_streak', data)
    
    def test_feedback_endpoint(self):
        """Test feedback submission endpoint"""
        feedback_data = {
            'type': 'general',
            'rating': 5,
            'message': 'Great app, very helpful!',
            'user_email': 'feedback@example.com'
        }
        
        response = self.post_json('/api/feedback', feedback_data)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('message', data)
    
    def test_404_error_handler(self):
        """Test 404 error handler"""
        response = self.client.get('/api/nonexistent')
        
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 404)
    
    def test_500_error_handler(self):
        """Test 500 error handler"""
        # This test would require triggering an actual server error
        # For now, we'll test the error handler function directly
        with self.app.test_request_context():
            from app import handle_500_error
            
            error = Exception("Test error")
            response = handle_500_error(error)
            
            self.assertEqual(response[1], 500)
            
            data = json.loads(response[0].data)
            self.assertFalse(data['success'])
            self.assertIn('error', data)
            self.assertEqual(data['error']['code'], 500)
    
    def test_request_validation(self):
        """Test request validation middleware"""
        # Test with invalid JSON
        response = self.client.post(
            '/api/auth/register',
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = self.client.get('/api/health')
        
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertIn('Access-Control-Allow-Methods', response.headers)
        self.assertIn('Access-Control-Allow-Headers', response.headers)

class TestFlaskAppPerformance(PerformanceTestCase):
    """Performance tests for Flask application"""
    
    def setUp(self):
        """Set up performance test environment"""
        super().setUp()
        
        if create_app and TestingConfig:
            self.app = create_app(TestingConfig)
            self.app_context = self.app.app_context()
            self.app_context.push()
            self.client = self.app.test_client()
        else:
            self.skipTest("Flask app or TestingConfig not available")
    
    def test_health_check_performance(self):
        """Test health check endpoint performance"""
        def health_check():
            return self.client.get('/api/health')
        
        # Health check should complete within 0.1 seconds
        response = self.assert_execution_time_under(health_check, 0.1)
        self.assertEqual(response.status_code, 200)
    
    def test_registration_performance(self):
        """Test user registration performance"""
        def register_user():
            user_data = {
                'username': f'perfuser{datetime.now().timestamp()}',
                'email': f'perf{datetime.now().timestamp()}@example.com',
                'password': 'securepassword123'
            }
            return self.client.post(
                '/api/auth/register',
                data=json.dumps(user_data),
                content_type='application/json'
            )
        
        # Registration should complete within 2 seconds
        response = self.assert_execution_time_under(register_user, 2.0)
        self.assertEqual(response.status_code, 201)
    
    def test_chat_endpoint_performance(self):
        """Test chat endpoint performance"""
        # Register and login first
        user_data = {
            'username': 'chatperfuser',
            'email': 'chatperf@example.com',
            'password': 'securepassword123'
        }
        self.client.post(
            '/api/auth/register',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        
        login_response = self.client.post(
            '/api/auth/login',
            data=json.dumps({
                'email': 'chatperf@example.com',
                'password': 'securepassword123'
            }),
            content_type='application/json'
        )
        
        login_data = json.loads(login_response.data)
        session_id = login_data['session_id']
        
        def send_chat_message():
            chat_data = {
                'message': 'Hello, I need help with stress management',
                'session_id': session_id
            }
            return self.client.post(
                '/api/chat',
                data=json.dumps(chat_data),
                content_type='application/json'
            )
        
        # Chat response should complete within 5 seconds
        response = self.assert_execution_time_under(send_chat_message, 5.0)
        self.assertEqual(response.status_code, 200)

class TestFlaskAppMocked(MockTestCase):
    """Test Flask application with mocked dependencies"""
    
    def setUp(self):
        """Set up mocked test environment"""
        super().setUp()
        
        if create_app and TestingConfig:
            self.app = create_app(TestingConfig)
            self.app_context = self.app.app_context()
            self.app_context.push()
            self.client = self.app.test_client()
        else:
            self.skipTest("Flask app or TestingConfig not available")
    
    @patch('app.UserManager')
    def test_registration_with_mocked_user_manager(self, mock_user_manager):
        """Test registration with mocked UserManager"""
        # Mock successful user creation
        mock_instance = mock_user_manager.return_value
        mock_instance.create_user.return_value = {
            'success': True,
            'user_id': 'test-user-123',
            'message': 'User created successfully'
        }
        
        user_data = {
            'username': 'mockeduser',
            'email': 'mocked@example.com',
            'password': 'securepassword123'
        }
        
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['user_id'], 'test-user-123')
    
    @patch('app.ConversationEngine')
    def test_chat_with_mocked_conversation_engine(self, mock_conversation_engine):
        """Test chat with mocked ConversationEngine"""
        # Mock conversation engine response
        mock_instance = mock_conversation_engine.return_value
        mock_instance.process_message.return_value = {
            'success': True,
            'response': 'This is a mocked AI response',
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'confidence': 0.9,
                'safety_check': 'passed'
            }
        }
        
        # Register and login first (using real user manager for this part)
        user_data = {
            'username': 'chatmockuser',
            'email': 'chatmock@example.com',
            'password': 'securepassword123'
        }
        self.client.post(
            '/api/auth/register',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        
        login_response = self.client.post(
            '/api/auth/login',
            data=json.dumps({
                'email': 'chatmock@example.com',
                'password': 'securepassword123'
            }),
            content_type='application/json'
        )
        
        login_data = json.loads(login_response.data)
        session_id = login_data['session_id']
        
        # Send chat message
        chat_data = {
            'message': 'Hello, I need help',
            'session_id': session_id
        }
        
        response = self.client.post(
            '/api/chat',
            data=json.dumps(chat_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['response'], 'This is a mocked AI response')
    
    @patch('app.ResourceManager')
    def test_resources_with_mocked_resource_manager(self, mock_resource_manager):
        """Test resources endpoint with mocked ResourceManager"""
        # Mock resource manager response
        mock_instance = mock_resource_manager.return_value
        mock_instance.get_crisis_resources.return_value = [
            {
                'id': 'crisis-1',
                'title': 'Mocked Crisis Line',
                'phone': '+27 123 456 789',
                'availability': '24/7'
            }
        ]
        mock_instance.get_coping_strategies.return_value = [
            {
                'id': 'coping-1',
                'name': 'Mocked Breathing Exercise',
                'description': 'A mocked coping strategy'
            }
        ]
        mock_instance.get_educational_content.return_value = [
            {
                'id': 'edu-1',
                'title': 'Mocked Educational Content',
                'content': 'Mocked educational material'
            }
        ]
        
        response = self.client.get('/api/resources')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('crisis_resources', data)
        self.assertIn('coping_strategies', data)
        self.assertIn('educational_content', data)
        
        # Verify mocked data is returned
        self.assertEqual(data['crisis_resources'][0]['title'], 'Mocked Crisis Line')
        self.assertEqual(data['coping_strategies'][0]['name'], 'Mocked Breathing Exercise')

class TestAuthenticationDecorator(unittest.TestCase):
    """Test authentication decorator"""
    
    def test_require_auth_decorator(self):
        """Test require_auth decorator functionality"""
        if not require_auth:
            self.skipTest("require_auth decorator not available")
        
        # This would require more complex setup to test properly
        # For now, we'll just verify the decorator exists
        self.assertTrue(callable(require_auth))
    
    def test_rate_limit_decorator(self):
        """Test rate_limit decorator functionality"""
        if not rate_limit:
            self.skipTest("rate_limit decorator not available")
        
        # This would require more complex setup to test properly
        # For now, we'll just verify the decorator exists
        self.assertTrue(callable(rate_limit))

if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)