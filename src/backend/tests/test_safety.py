# ChillBuddy Backend - Safety Manager Tests
# Comprehensive test suite for safety and crisis management functionality

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import os
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import test configuration
from .test_config import BaseTestCase, FlaskTestCase, MockTestCase

# Import the modules to test
try:
    from safety import SafetyManager, RiskLevel, SafetyAlert
except ImportError:
    import sys
    sys.path.append('..')
    from safety import SafetyManager, RiskLevel, SafetyAlert


class TestSafetyAlert(BaseTestCase):
    """Test SafetyAlert dataclass functionality"""
    
    def test_safety_alert_creation(self):
        """Test SafetyAlert object creation"""
        alert = SafetyAlert(
            risk_level=RiskLevel.HIGH,
            detected_keywords=["suicide", "hopeless"],
            confidence_score=0.85,
            timestamp=datetime.now(),
            user_id="test_user_123",
            message_content="I feel hopeless and want to end it all",
            recommended_action="immediate_intervention"
        )
        
        self.assertEqual(alert.risk_level, RiskLevel.HIGH)
        self.assertEqual(len(alert.detected_keywords), 2)
        self.assertIn("suicide", alert.detected_keywords)
        self.assertGreater(alert.confidence_score, 0.8)
        self.assertEqual(alert.user_id, "test_user_123")
        self.assertIsInstance(alert.timestamp, datetime)
    
    def test_safety_alert_serialization(self):
        """Test SafetyAlert can be converted to dict"""
        alert = SafetyAlert(
            risk_level=RiskLevel.MEDIUM,
            detected_keywords=["hurt myself"],
            confidence_score=0.65,
            timestamp=datetime.now(),
            user_id="user_456",
            message_content="Sometimes I want to hurt myself",
            recommended_action="provide_resources"
        )
        
        # Convert to dict-like structure
        alert_dict = {
            'risk_level': alert.risk_level.value,
            'detected_keywords': alert.detected_keywords,
            'confidence_score': alert.confidence_score,
            'user_id': alert.user_id,
            'message_content': alert.message_content,
            'recommended_action': alert.recommended_action
        }
        
        self.assertEqual(alert_dict['risk_level'], 'medium')
        self.assertIsInstance(alert_dict['detected_keywords'], list)


class TestRiskLevel(BaseTestCase):
    """Test RiskLevel enum functionality"""
    
    def test_risk_level_values(self):
        """Test all risk level enum values"""
        self.assertEqual(RiskLevel.LOW.value, "low")
        self.assertEqual(RiskLevel.MEDIUM.value, "medium")
        self.assertEqual(RiskLevel.HIGH.value, "high")
        self.assertEqual(RiskLevel.CRITICAL.value, "critical")
    
    def test_risk_level_comparison(self):
        """Test risk level ordering"""
        levels = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        # Test that we can iterate through levels
        for level in levels:
            self.assertIsInstance(level, RiskLevel)
            self.assertIn(level.value, ["low", "medium", "high", "critical"])


class TestSafetyManager(BaseTestCase):
    """Test SafetyManager core functionality"""
    
    def setUp(self):
        """Set up test environment"""
        super().setUp()
        
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.config_data = {
            "crisis_keywords": [
                "suicide", "kill myself", "end it all", "want to die",
                "hurt myself", "self harm", "cutting", "overdose",
                "worthless", "hopeless", "can't go on"
            ],
            "content_filters": {
                "profanity": ["inappropriate", "offensive"],
                "spam": ["spam_pattern", "repeated_content"]
            },
            "emergency_contacts": {
                "crisis_hotline": "988 (Suicide & Crisis Lifeline)",
                "text_line": "Text HOME to 741741",
                "emergency": "911 for immediate emergency",
                "south_africa_lifeline": "0800 567 567"
            }
        }
        
        json.dump(self.config_data, self.temp_config)
        self.temp_config.close()
        
        # Initialize SafetyManager with test config
        self.safety_manager = SafetyManager(config_path=self.temp_config.name)
    
    def tearDown(self):
        """Clean up test environment"""
        super().tearDown()
        
        # Remove temporary config file
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
    
    def test_safety_manager_initialization(self):
        """Test SafetyManager initialization"""
        self.assertIsInstance(self.safety_manager, SafetyManager)
        self.assertIsInstance(self.safety_manager.crisis_keywords, list)
        self.assertIsInstance(self.safety_manager.safety_filters, dict)
        self.assertIsInstance(self.safety_manager.emergency_contacts, dict)
        self.assertIsInstance(self.safety_manager.alert_history, list)
    
    def test_load_safety_config(self):
        """Test loading safety configuration"""
        result = self.safety_manager.load_safety_config()
        
        self.assertTrue(result)
        self.assertIn("suicide", self.safety_manager.crisis_keywords)
        self.assertIn("profanity", self.safety_manager.safety_filters)
        self.assertIn("crisis_hotline", self.safety_manager.emergency_contacts)
    
    def test_load_safety_config_missing_file(self):
        """Test loading config with missing file"""
        safety_manager = SafetyManager(config_path="nonexistent_file.json")
        
        # Should fall back to defaults
        self.assertIsInstance(safety_manager.crisis_keywords, list)
        self.assertGreater(len(safety_manager.crisis_keywords), 0)
    
    def test_detect_crisis_high_risk(self):
        """Test crisis detection for high-risk messages"""
        test_messages = [
            "I want to kill myself",
            "I'm going to end it all tonight",
            "There's no point in living anymore",
            "I feel completely hopeless and worthless"
        ]
        
        for message in test_messages:
            is_crisis, keywords, confidence = self.safety_manager.detect_crisis(message)
            
            self.assertTrue(is_crisis, f"Failed to detect crisis in: {message}")
            self.assertGreater(len(keywords), 0)
            self.assertGreater(confidence, 0.5)
    
    def test_detect_crisis_low_risk(self):
        """Test crisis detection for low-risk messages"""
        test_messages = [
            "I'm having a good day today",
            "Can you help me with anxiety?",
            "I'm feeling a bit sad but okay",
            "What are some coping strategies?"
        ]
        
        for message in test_messages:
            is_crisis, keywords, confidence = self.safety_manager.detect_crisis(message)
            
            self.assertFalse(is_crisis, f"False positive crisis detection in: {message}")
            self.assertEqual(len(keywords), 0)
            self.assertEqual(confidence, 0.0)
    
    def test_assess_risk_critical(self):
        """Test risk assessment for critical messages"""
        message = "I'm going to kill myself tonight with pills"
        user_id = "test_user_critical"
        
        alert = self.safety_manager.assess_risk(message, user_id)
        
        self.assertEqual(alert.risk_level, RiskLevel.CRITICAL)
        self.assertGreater(alert.confidence_score, 0.8)
        self.assertEqual(alert.user_id, user_id)
        self.assertIn("immediate_intervention", alert.recommended_action)
    
    def test_assess_risk_high(self):
        """Test risk assessment for high-risk messages"""
        message = "I feel hopeless and want to hurt myself"
        user_id = "test_user_high"
        
        alert = self.safety_manager.assess_risk(message, user_id)
        
        self.assertEqual(alert.risk_level, RiskLevel.HIGH)
        self.assertGreater(alert.confidence_score, 0.6)
        self.assertEqual(alert.user_id, user_id)
    
    def test_assess_risk_medium(self):
        """Test risk assessment for medium-risk messages"""
        message = "I've been feeling really down lately and don't know what to do"
        user_id = "test_user_medium"
        
        alert = self.safety_manager.assess_risk(message, user_id)
        
        self.assertIn(alert.risk_level, [RiskLevel.LOW, RiskLevel.MEDIUM])
        self.assertEqual(alert.user_id, user_id)
    
    def test_assess_risk_low(self):
        """Test risk assessment for low-risk messages"""
        message = "I'm looking for some general mental health tips"
        user_id = "test_user_low"
        
        alert = self.safety_manager.assess_risk(message, user_id)
        
        self.assertEqual(alert.risk_level, RiskLevel.LOW)
        self.assertLessEqual(alert.confidence_score, 0.3)
        self.assertEqual(alert.user_id, user_id)
    
    def test_filter_content_safe(self):
        """Test content filtering for safe content"""
        safe_messages = [
            "Hello, how are you today?",
            "I'm feeling anxious about work",
            "Can you recommend some relaxation techniques?"
        ]
        
        for message in safe_messages:
            is_safe, filtered_message, flags = self.safety_manager.filter_content(message)
            
            self.assertTrue(is_safe, f"Safe message flagged as unsafe: {message}")
            self.assertEqual(filtered_message, message)
            self.assertEqual(len(flags), 0)
    
    def test_trigger_emergency_protocol(self):
        """Test emergency protocol activation"""
        alert = SafetyAlert(
            risk_level=RiskLevel.CRITICAL,
            detected_keywords=["suicide", "tonight"],
            confidence_score=0.95,
            timestamp=datetime.now(),
            user_id="emergency_user",
            message_content="I'm going to commit suicide tonight",
            recommended_action="immediate_intervention"
        )
        
        response = self.safety_manager.trigger_emergency_protocol(alert)
        
        self.assertIsInstance(response, dict)
        self.assertIn("emergency_activated", response)
        self.assertIn("crisis_resources", response)
        self.assertIn("immediate_actions", response)
        self.assertTrue(response["emergency_activated"])
    
    def test_get_crisis_resources_by_risk_level(self):
        """Test getting crisis resources based on risk level"""
        for risk_level in RiskLevel:
            resources = self.safety_manager.get_crisis_resources(risk_level)
            
            self.assertIsInstance(resources, list)
            self.assertGreater(len(resources), 0)
            
            for resource in resources:
                self.assertIsInstance(resource, dict)
                self.assertIn("name", resource)
                self.assertIn("contact", resource)
    
    def test_log_safety_event(self):
        """Test safety event logging"""
        alert = SafetyAlert(
            risk_level=RiskLevel.HIGH,
            detected_keywords=["hurt myself"],
            confidence_score=0.75,
            timestamp=datetime.now(),
            user_id="log_test_user",
            message_content="I want to hurt myself",
            recommended_action="provide_resources"
        )
        
        initial_count = len(self.safety_manager.alert_history)
        self.safety_manager.log_safety_event(alert)
        
        self.assertEqual(len(self.safety_manager.alert_history), initial_count + 1)
        self.assertEqual(self.safety_manager.alert_history[-1], alert)
    
    def test_get_safety_statistics(self):
        """Test safety statistics generation"""
        # Add some test alerts
        test_alerts = [
            SafetyAlert(RiskLevel.LOW, [], 0.2, datetime.now(), "user1", "test", "monitor"),
            SafetyAlert(RiskLevel.MEDIUM, ["sad"], 0.5, datetime.now(), "user2", "test", "support"),
            SafetyAlert(RiskLevel.HIGH, ["hopeless"], 0.8, datetime.now(), "user3", "test", "intervene")
        ]
        
        for alert in test_alerts:
            self.safety_manager.log_safety_event(alert)
        
        stats = self.safety_manager.get_safety_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn("total_alerts", stats)
        self.assertIn("risk_distribution", stats)
        self.assertIn("recent_activity", stats)
        self.assertGreaterEqual(stats["total_alerts"], len(test_alerts))
    
    def test_update_safety_filters(self):
        """Test updating safety filters"""
        new_filters = {
            "new_category": ["new_keyword1", "new_keyword2"],
            "updated_category": ["updated_keyword"]
        }
        
        result = self.safety_manager.update_safety_filters(new_filters)
        
        self.assertTrue(result)
        self.assertIn("new_category", self.safety_manager.safety_filters)
        self.assertIn("updated_category", self.safety_manager.safety_filters)


class TestSafetyManagerIntegration(FlaskTestCase):
    """Integration tests for SafetyManager with Flask app"""
    
    def setUp(self):
        """Set up Flask test environment"""
        super().setUp()
        self.safety_manager = SafetyManager()
    
    def test_safety_integration_with_chat_endpoint(self):
        """Test safety integration with chat endpoint"""
        # This would test integration with the actual Flask app
        # For now, we'll test the safety manager independently
        
        crisis_message = "I want to end my life"
        alert = self.safety_manager.assess_risk(crisis_message, "test_user")
        
        self.assertIn(alert.risk_level, [RiskLevel.HIGH, RiskLevel.CRITICAL])
        
        # Test that emergency protocol would be triggered
        if alert.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            response = self.safety_manager.trigger_emergency_protocol(alert)
            self.assertTrue(response["emergency_activated"])


class TestSafetyManagerPerformance(BaseTestCase):
    """Performance tests for SafetyManager"""
    
    def setUp(self):
        """Set up performance test environment"""
        super().setUp()
        self.safety_manager = SafetyManager()
    
    def test_crisis_detection_performance(self):
        """Test crisis detection performance with multiple messages"""
        import time
        
        test_messages = [
            "I'm feeling okay today",
            "I want to hurt myself",
            "How can I manage stress?",
            "I feel hopeless and worthless",
            "What are some coping strategies?"
        ] * 100  # 500 messages total
        
        start_time = time.time()
        
        for message in test_messages:
            self.safety_manager.detect_crisis(message)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process 500 messages in under 5 seconds
        self.assertLess(processing_time, 5.0)
        
        # Average processing time per message should be reasonable
        avg_time_per_message = processing_time / len(test_messages)
        self.assertLess(avg_time_per_message, 0.01)  # Less than 10ms per message
    
    def test_risk_assessment_performance(self):
        """Test risk assessment performance"""
        import time
        
        test_message = "I'm feeling really down and don't know what to do"
        
        start_time = time.time()
        
        for i in range(100):
            self.safety_manager.assess_risk(test_message, f"user_{i}")
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process 100 assessments in under 2 seconds
        self.assertLess(processing_time, 2.0)


class TestSafetyManagerMocked(MockTestCase):
    """Tests with mocked dependencies"""
    
    def setUp(self):
        """Set up mocked test environment"""
        super().setUp()
        
        # Mock file operations
        self.mock_file_exists = self.create_mock('os.path.exists')
        self.mock_open = self.create_mock('builtins.open')
        
        self.safety_manager = SafetyManager()
    
    @patch('os.path.exists')
    @patch('builtins.open')
    def test_load_config_with_mocked_file(self, mock_open, mock_exists):
        """Test loading config with mocked file operations"""
        mock_exists.return_value = True
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.read.return_value = json.dumps({
            "crisis_keywords": ["test_keyword"],
            "content_filters": {},
            "emergency_contacts": {}
        })
        mock_open.return_value = mock_file
        
        result = self.safety_manager.load_safety_config()
        
        self.assertTrue(result)
        mock_exists.assert_called_once()
        mock_open.assert_called_once()


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)