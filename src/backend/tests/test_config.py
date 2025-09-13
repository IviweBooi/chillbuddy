# ChillBuddy Test Configuration and Base Test Classes
#
# This file contains:
# - Test configuration setup
# - Base test classes
# - Test utilities and fixtures
# - Mock data generators

import unittest
import tempfile
import os
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Import Flask and testing utilities
try:
    from flask import Flask
    from flask.testing import FlaskClient
except ImportError:
    Flask = None
    FlaskClient = None

# Import application modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import TestingConfig, setup_logging
    from utils import generate_user_id, get_current_timestamp
except ImportError:
    TestingConfig = None
    setup_logging = None
    generate_user_id = None
    get_current_timestamp = None

class BaseTestCase(unittest.TestCase):
    """Base test case with common setup and utilities"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, 'test.db')
        
        # Setup logging for tests
        if setup_logging:
            setup_logging('testing')
        
        # Create test data
        self.test_user_id = self.generate_test_user_id()
        self.test_timestamp = self.get_test_timestamp()
        
    def tearDown(self):
        """Clean up after each test method"""
        # Clean up temporary files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def generate_test_user_id(self) -> str:
        """Generate a test user ID"""
        if generate_user_id:
            return generate_user_id()
        return "test-user-123"
    
    def get_test_timestamp(self) -> str:
        """Get a test timestamp"""
        if get_current_timestamp:
            return get_current_timestamp()
        return datetime.now().isoformat()
    
    def create_test_message(self, content: str = "Test message", user_id: str = None) -> Dict[str, Any]:
        """Create a test message"""
        return {
            "id": f"msg-{datetime.now().timestamp()}",
            "user_id": user_id or self.test_user_id,
            "content": content,
            "timestamp": self.test_timestamp,
            "type": "user"
        }
    
    def create_test_user_profile(self, user_id: str = None) -> Dict[str, Any]:
        """Create a test user profile"""
        return {
            "user_id": user_id or self.test_user_id,
            "username": "testuser",
            "email": "test@example.com",
            "age_range": "18-25",
            "location": "Cape Town, South Africa",
            "preferred_language": "en",
            "created_at": self.test_timestamp,
            "last_active": self.test_timestamp,
            "privacy_settings": {
                "data_collection": True,
                "analytics": True,
                "marketing": False
            }
        }
    
    def create_test_conversation(self, message_count: int = 3) -> List[Dict[str, Any]]:
        """Create a test conversation with multiple messages"""
        conversation = []
        
        for i in range(message_count):
            # User message
            user_msg = self.create_test_message(f"User message {i+1}")
            conversation.append(user_msg)
            
            # Assistant response
            assistant_msg = {
                "id": f"msg-assistant-{datetime.now().timestamp()}-{i}",
                "user_id": self.test_user_id,
                "content": f"Assistant response {i+1}",
                "timestamp": self.test_timestamp,
                "type": "assistant",
                "metadata": {
                    "confidence": 0.8,
                    "safety_check": "passed",
                    "response_time": 1.2
                }
            }
            conversation.append(assistant_msg)
        
        return conversation
    
    def create_test_mood_entry(self, mood_score: int = 5, notes: str = "Feeling okay") -> Dict[str, Any]:
        """Create a test mood entry"""
        return {
            "id": f"mood-{datetime.now().timestamp()}",
            "user_id": self.test_user_id,
            "mood_score": mood_score,
            "notes": notes,
            "timestamp": self.test_timestamp,
            "factors": ["work", "sleep"],
            "coping_strategies_used": ["deep_breathing", "journaling"]
        }
    
    def create_test_crisis_scenario(self, risk_level: str = "high") -> Dict[str, Any]:
        """Create a test crisis scenario"""
        crisis_messages = {
            "high": "I want to hurt myself and don't see any point in living",
            "medium": "I feel hopeless and don't know what to do",
            "low": "I'm feeling a bit down today"
        }
        
        return {
            "message": crisis_messages.get(risk_level, crisis_messages["low"]),
            "user_id": self.test_user_id,
            "timestamp": self.test_timestamp,
            "expected_risk_level": risk_level
        }
    
    def assert_valid_response_format(self, response: Dict[str, Any]):
        """Assert that a response has the expected format"""
        self.assertIn("success", response)
        self.assertIn("timestamp", response)
        self.assertIsInstance(response["success"], bool)
        self.assertIsInstance(response["timestamp"], str)
    
    def assert_error_response_format(self, response: Dict[str, Any]):
        """Assert that an error response has the expected format"""
        self.assertFalse(response["success"])
        self.assertIn("error", response)
        self.assertIn("message", response["error"])
        self.assertIn("timestamp", response["error"])
    
    def assert_conversation_response_format(self, response: Dict[str, Any]):
        """Assert that a conversation response has the expected format"""
        self.assertIn("message", response)
        self.assertIn("timestamp", response)
        self.assertIn("type", response)
        self.assertEqual(response["type"], "assistant")

class FlaskTestCase(BaseTestCase):
    """Base test case for Flask application tests"""
    
    def setUp(self):
        """Set up Flask test client"""
        super().setUp()
        
        if Flask and TestingConfig:
            self.app = Flask(__name__)
            self.app.config.from_object(TestingConfig)
            self.app_context = self.app.app_context()
            self.app_context.push()
            self.client = self.app.test_client()
        else:
            self.app = None
            self.client = None
    
    def tearDown(self):
        """Clean up Flask test environment"""
        if hasattr(self, 'app_context'):
            self.app_context.pop()
        super().tearDown()
    
    def post_json(self, url: str, data: Dict[str, Any], headers: Dict[str, str] = None):
        """Helper method to post JSON data"""
        if not self.client:
            self.skipTest("Flask not available")
        
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)
        
        return self.client.post(
            url,
            data=json.dumps(data),
            headers=default_headers
        )
    
    def get_json(self, url: str, headers: Dict[str, str] = None):
        """Helper method to get JSON data"""
        if not self.client:
            self.skipTest("Flask not available")
        
        return self.client.get(url, headers=headers or {})

class MockTestCase(BaseTestCase):
    """Base test case with common mocks"""
    
    def setUp(self):
        """Set up common mocks"""
        super().setUp()
        
        # Mock external API calls
        self.mock_openai = self.create_mock_openai()
        self.mock_database = self.create_mock_database()
        self.mock_file_system = self.create_mock_file_system()
    
    def create_mock_openai(self):
        """Create mock OpenAI API"""
        mock_openai = Mock()
        mock_openai.chat.completions.create.return_value = Mock(
            choices=[Mock(
                message=Mock(
                    content="This is a mock AI response for testing purposes."
                )
            )]
        )
        return mock_openai
    
    def create_mock_database(self):
        """Create mock database"""
        mock_db = Mock()
        mock_db.save_user_data.return_value = True
        mock_db.load_user_data.return_value = self.create_test_user_profile()
        mock_db.save_conversation.return_value = True
        mock_db.load_conversation_history.return_value = self.create_test_conversation()
        return mock_db
    
    def create_mock_file_system(self):
        """Create mock file system"""
        mock_fs = Mock()
        mock_fs.exists.return_value = True
        mock_fs.read_file.return_value = '{"test": "data"}'
        mock_fs.write_file.return_value = True
        return mock_fs

class PerformanceTestCase(BaseTestCase):
    """Base test case for performance testing"""
    
    def setUp(self):
        """Set up performance testing"""
        super().setUp()
        self.performance_data = []
    
    def measure_execution_time(self, func, *args, **kwargs):
        """Measure function execution time"""
        import time
        
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        self.performance_data.append({
            'function': func.__name__,
            'execution_time': execution_time,
            'timestamp': datetime.now().isoformat()
        })
        
        return result, execution_time
    
    def assert_execution_time_under(self, func, max_time: float, *args, **kwargs):
        """Assert that function executes under specified time"""
        result, execution_time = self.measure_execution_time(func, *args, **kwargs)
        self.assertLess(
            execution_time, 
            max_time, 
            f"{func.__name__} took {execution_time:.3f}s, expected under {max_time}s"
        )
        return result
    
    def tearDown(self):
        """Print performance summary"""
        if self.performance_data:
            print("\nPerformance Summary:")
            for data in self.performance_data:
                print(f"  {data['function']}: {data['execution_time']:.3f}s")
        super().tearDown()

# Test Data Generators
class TestDataGenerator:
    """Generate test data for various scenarios"""
    
    @staticmethod
    def generate_conversation_scenarios() -> List[Dict[str, Any]]:
        """Generate various conversation test scenarios"""
        return [
            {
                "name": "normal_conversation",
                "messages": [
                    "Hello, how are you?",
                    "I'm feeling a bit stressed about work",
                    "Can you help me with some coping strategies?"
                ],
                "expected_response_type": "supportive"
            },
            {
                "name": "crisis_conversation",
                "messages": [
                    "I don't want to live anymore",
                    "Everything feels hopeless",
                    "I'm thinking about hurting myself"
                ],
                "expected_response_type": "crisis_intervention"
            },
            {
                "name": "mood_tracking",
                "messages": [
                    "I want to log my mood",
                    "I'm feeling about a 3 out of 10 today",
                    "I didn't sleep well and had a fight with my partner"
                ],
                "expected_response_type": "mood_logging"
            },
            {
                "name": "resource_request",
                "messages": [
                    "Can you help me find a therapist?",
                    "I live in Cape Town",
                    "I prefer someone who speaks English"
                ],
                "expected_response_type": "resource_provision"
            }
        ]
    
    @staticmethod
    def generate_user_profiles() -> List[Dict[str, Any]]:
        """Generate various user profile test scenarios"""
        return [
            {
                "name": "young_adult",
                "age_range": "18-25",
                "location": "Cape Town",
                "language": "en",
                "concerns": ["anxiety", "academic_stress"]
            },
            {
                "name": "working_professional",
                "age_range": "26-35",
                "location": "Johannesburg",
                "language": "en",
                "concerns": ["work_stress", "relationships"]
            },
            {
                "name": "afrikaans_speaker",
                "age_range": "36-45",
                "location": "Stellenbosch",
                "language": "af",
                "concerns": ["depression", "family_issues"]
            }
        ]
    
    @staticmethod
    def generate_mood_data() -> List[Dict[str, Any]]:
        """Generate mood tracking test data"""
        moods = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(30):
            date = base_date + timedelta(days=i)
            mood_score = 5 + (i % 3 - 1) + (0.5 if i > 15 else -0.5)  # Slight upward trend
            
            moods.append({
                "date": date.isoformat(),
                "mood_score": max(1, min(10, mood_score)),
                "notes": f"Day {i+1} mood entry",
                "factors": ["sleep", "work"] if i % 2 == 0 else ["exercise", "social"]
            })
        
        return moods
    
    @staticmethod
    def generate_crisis_scenarios() -> List[Dict[str, Any]]:
        """Generate crisis detection test scenarios"""
        return [
            {
                "message": "I want to kill myself",
                "expected_risk": "high",
                "expected_keywords": ["kill myself"]
            },
            {
                "message": "I feel hopeless and worthless",
                "expected_risk": "medium",
                "expected_keywords": ["hopeless", "worthless"]
            },
            {
                "message": "I'm having a great day!",
                "expected_risk": "low",
                "expected_keywords": []
            },
            {
                "message": "I can't cope with this anymore, I want to end it all",
                "expected_risk": "high",
                "expected_keywords": ["can't cope", "end it all"]
            }
        ]

# Test Utilities
def run_test_suite(test_class=None, verbosity=2):
    """Run test suite with specified verbosity"""
    if test_class:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
    else:
        # Discover all tests in the tests directory
        suite = unittest.TestLoader().discover('tests', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result

def create_test_database():
    """Create a temporary test database"""
    import tempfile
    import sqlite3
    
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    # Initialize database with test schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create test tables (simplified schema)
    cursor.execute('''
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            username TEXT,
            email TEXT,
            created_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE conversations (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            message TEXT,
            response TEXT,
            timestamp TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE mood_entries (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            mood_score INTEGER,
            notes TEXT,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    
    return db_path

def cleanup_test_database(db_path):
    """Clean up test database"""
    if os.path.exists(db_path):
        os.unlink(db_path)

# Test Configuration Validation
def validate_test_environment():
    """Validate that test environment is properly set up"""
    issues = []
    
    # Check Python version
    import sys
    if sys.version_info < (3, 7):
        issues.append("Python 3.7+ required for testing")
    
    # Check required modules
    required_modules = ['unittest', 'json', 'tempfile', 'datetime']
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            issues.append(f"Required module '{module}' not available")
    
    # Check optional modules
    optional_modules = ['flask', 'requests', 'sqlite3']
    missing_optional = []
    for module in optional_modules:
        try:
            __import__(module)
        except ImportError:
            missing_optional.append(module)
    
    if missing_optional:
        issues.append(f"Optional modules not available: {', '.join(missing_optional)}")
    
    # Check file system permissions
    try:
        test_dir = tempfile.mkdtemp()
        test_file = os.path.join(test_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.unlink(test_file)
        os.rmdir(test_dir)
    except Exception as e:
        issues.append(f"File system access issue: {e}")
    
    return issues

if __name__ == '__main__':
    # Validate test environment
    issues = validate_test_environment()
    if issues:
        print("Test Environment Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Test environment is properly configured")
    
    # Run basic test
    class BasicTest(BaseTestCase):
        def test_basic_functionality(self):
            self.assertTrue(True)
            self.assertIsNotNone(self.test_user_id)
            self.assertIsNotNone(self.test_timestamp)
    
    # Run the basic test
    result = run_test_suite(BasicTest, verbosity=1)
    print(f"\nBasic test {'PASSED' if result.wasSuccessful() else 'FAILED'}")