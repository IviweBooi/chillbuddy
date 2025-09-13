# Unit Tests for ResourceManager Class
#
# This file contains comprehensive tests for:
# - Mental health resources database
# - Crisis resource management
# - Coping strategies
# - Professional help directory
# - South African specific resources

import unittest
import tempfile
import os
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Import test configuration
from .test_config import BaseTestCase, MockTestCase, PerformanceTestCase

# Import the module under test
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from resources import ResourceManager, MentalHealthResource, ResourceType, IssueType
except ImportError as e:
    print(f"Import error: {e}")
    ResourceManager = None
    MentalHealthResource = None
    ResourceType = None
    IssueType = None

class TestResourceManager(BaseTestCase):
    """Test cases for ResourceManager class"""
    
    def setUp(self):
        """Set up test environment"""
        super().setUp()
        
        if ResourceManager:
            self.resource_manager = ResourceManager(data_dir=self.temp_dir)
        else:
            self.skipTest("ResourceManager not available")
    
    def test_resource_manager_initialization(self):
        """Test ResourceManager initialization"""
        self.assertIsNotNone(self.resource_manager)
        self.assertEqual(self.resource_manager.data_dir, self.temp_dir)
        
        # Check that resource files are created
        expected_files = [
            'crisis_resources.json',
            'coping_strategies.json',
            'educational_content.json',
            'professional_directory.json',
            'wellness_tools.json'
        ]
        
        for filename in expected_files:
            file_path = os.path.join(self.temp_dir, filename)
            self.assertTrue(os.path.exists(file_path), f"{filename} should exist")
    
    def test_get_crisis_resources(self):
        """Test getting crisis resources"""
        crisis_resources = self.resource_manager.get_crisis_resources()
        
        self.assertIsInstance(crisis_resources, list)
        self.assertGreater(len(crisis_resources), 0)
        
        # Check that each resource has required fields
        for resource in crisis_resources:
            self.assertIn('id', resource)
            self.assertIn('title', resource)
            self.assertIn('description', resource)
            self.assertIn('contact_info', resource)
            self.assertIn('availability', resource)
            self.assertIn('type', resource)
    
    def test_get_crisis_resources_by_location(self):
        """Test getting crisis resources filtered by location"""
        # Test South African resources
        sa_resources = self.resource_manager.get_crisis_resources(location="South Africa")
        self.assertIsInstance(sa_resources, list)
        
        # Test Cape Town specific resources
        ct_resources = self.resource_manager.get_crisis_resources(location="Cape Town")
        self.assertIsInstance(ct_resources, list)
        
        # Verify location filtering works
        for resource in sa_resources:
            location = resource.get('location', '').lower()
            self.assertTrue(
                'south africa' in location or 'national' in location,
                f"Resource {resource['title']} should be available in South Africa"
            )
    
    def test_get_coping_strategies(self):
        """Test getting coping strategies"""
        strategies = self.resource_manager.get_coping_strategies()
        
        self.assertIsInstance(strategies, list)
        self.assertGreater(len(strategies), 0)
        
        # Check strategy structure
        for strategy in strategies:
            self.assertIn('id', strategy)
            self.assertIn('name', strategy)
            self.assertIn('description', strategy)
            self.assertIn('instructions', strategy)
            self.assertIn('category', strategy)
            self.assertIn('difficulty_level', strategy)
    
    def test_get_coping_strategies_by_issue(self):
        """Test getting coping strategies filtered by issue type"""
        if not IssueType:
            self.skipTest("IssueType not available")
        
        # Test anxiety strategies
        anxiety_strategies = self.resource_manager.get_coping_strategies(issue_type=IssueType.ANXIETY)
        self.assertIsInstance(anxiety_strategies, list)
        
        # Test depression strategies
        depression_strategies = self.resource_manager.get_coping_strategies(issue_type=IssueType.DEPRESSION)
        self.assertIsInstance(depression_strategies, list)
        
        # Verify filtering works
        for strategy in anxiety_strategies:
            applicable_issues = strategy.get('applicable_issues', [])
            self.assertTrue(
                IssueType.ANXIETY.value in applicable_issues or 'general' in applicable_issues,
                f"Strategy {strategy['name']} should be applicable to anxiety"
            )
    
    def test_get_educational_content(self):
        """Test getting educational content"""
        content = self.resource_manager.get_educational_content()
        
        self.assertIsInstance(content, list)
        self.assertGreater(len(content), 0)
        
        # Check content structure
        for item in content:
            self.assertIn('id', item)
            self.assertIn('title', item)
            self.assertIn('content', item)
            self.assertIn('category', item)
            self.assertIn('reading_time', item)
            self.assertIn('difficulty_level', item)
    
    def test_get_educational_content_by_topic(self):
        """Test getting educational content filtered by topic"""
        # Test specific topics
        topics = ['anxiety', 'depression', 'stress', 'mindfulness']
        
        for topic in topics:
            with self.subTest(topic=topic):
                content = self.resource_manager.get_educational_content(topic=topic)
                self.assertIsInstance(content, list)
                
                # Verify topic filtering
                for item in content:
                    item_topics = item.get('topics', [])
                    item_category = item.get('category', '').lower()
                    self.assertTrue(
                        topic in item_topics or topic in item_category,
                        f"Content {item['title']} should be related to {topic}"
                    )
    
    def test_find_professional_help(self):
        """Test finding professional help"""
        professionals = self.resource_manager.find_professional_help()
        
        self.assertIsInstance(professionals, list)
        self.assertGreater(len(professionals), 0)
        
        # Check professional structure
        for professional in professionals:
            self.assertIn('id', professional)
            self.assertIn('name', professional)
            self.assertIn('specialization', professional)
            self.assertIn('location', professional)
            self.assertIn('contact_info', professional)
            self.assertIn('languages', professional)
    
    def test_find_professional_help_by_location(self):
        """Test finding professional help filtered by location"""
        # Test Cape Town professionals
        ct_professionals = self.resource_manager.find_professional_help(location="Cape Town")
        self.assertIsInstance(ct_professionals, list)
        
        # Test Johannesburg professionals
        jhb_professionals = self.resource_manager.find_professional_help(location="Johannesburg")
        self.assertIsInstance(jhb_professionals, list)
        
        # Verify location filtering
        for professional in ct_professionals:
            location = professional.get('location', '').lower()
            self.assertTrue(
                'cape town' in location or 'western cape' in location,
                f"Professional {professional['name']} should be in Cape Town area"
            )
    
    def test_find_professional_help_by_specialization(self):
        """Test finding professional help filtered by specialization"""
        specializations = ['anxiety', 'depression', 'trauma', 'addiction']
        
        for specialization in specializations:
            with self.subTest(specialization=specialization):
                professionals = self.resource_manager.find_professional_help(specialization=specialization)
                self.assertIsInstance(professionals, list)
                
                # Verify specialization filtering
                for professional in professionals:
                    prof_specializations = professional.get('specialization', [])
                    if isinstance(prof_specializations, str):
                        prof_specializations = [prof_specializations]
                    
                    self.assertTrue(
                        any(specialization.lower() in spec.lower() for spec in prof_specializations),
                        f"Professional {professional['name']} should specialize in {specialization}"
                    )
    
    def test_get_wellness_tools(self):
        """Test getting wellness tools"""
        tools = self.resource_manager.get_wellness_tools()
        
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
        
        # Check tool structure
        for tool in tools:
            self.assertIn('id', tool)
            self.assertIn('name', tool)
            self.assertIn('description', tool)
            self.assertIn('type', tool)
            self.assertIn('instructions', tool)
    
    def test_search_resources(self):
        """Test resource search functionality"""
        # Test search with various queries
        search_queries = [
            'anxiety',
            'depression',
            'breathing',
            'therapist',
            'crisis'
        ]
        
        for query in search_queries:
            with self.subTest(query=query):
                results = self.resource_manager.search_resources(query)
                self.assertIsInstance(results, list)
                
                # Verify search results contain the query term
                for result in results:
                    result_text = (
                        result.get('title', '') + ' ' +
                        result.get('description', '') + ' ' +
                        ' '.join(result.get('tags', []))
                    ).lower()
                    
                    self.assertTrue(
                        query.lower() in result_text,
                        f"Search result should contain '{query}'"
                    )
    
    def test_get_personalized_recommendations(self):
        """Test personalized resource recommendations"""
        # Create test user profile
        user_profile = {
            'concerns': ['anxiety', 'stress'],
            'location': 'Cape Town',
            'preferred_language': 'en',
            'experience_level': 'beginner'
        }
        
        recommendations = self.resource_manager.get_personalized_recommendations(user_profile)
        
        self.assertIsInstance(recommendations, dict)
        self.assertIn('coping_strategies', recommendations)
        self.assertIn('educational_content', recommendations)
        self.assertIn('professional_help', recommendations)
        
        # Verify recommendations are relevant
        strategies = recommendations['coping_strategies']
        for strategy in strategies:
            applicable_issues = strategy.get('applicable_issues', [])
            self.assertTrue(
                any(concern in applicable_issues for concern in user_profile['concerns']) or
                'general' in applicable_issues,
                f"Strategy {strategy['name']} should be relevant to user concerns"
            )
    
    def test_track_resource_usage(self):
        """Test resource usage tracking"""
        user_id = self.test_user_id
        resource_id = "test-resource-123"
        resource_type = "coping_strategy"
        
        # Track resource usage
        result = self.resource_manager.track_resource_usage(user_id, resource_id, resource_type)
        self.assertTrue(result)
        
        # Get usage statistics
        stats = self.resource_manager.get_usage_statistics(user_id)
        self.assertIsInstance(stats, dict)
        self.assertIn('total_resources_accessed', stats)
        self.assertIn('most_used_categories', stats)
        self.assertIn('recent_activity', stats)
    
    def test_get_south_african_resources(self):
        """Test getting South African specific resources"""
        sa_resources = self.resource_manager.get_south_african_resources()
        
        self.assertIsInstance(sa_resources, dict)
        self.assertIn('crisis_lines', sa_resources)
        self.assertIn('mental_health_organizations', sa_resources)
        self.assertIn('government_services', sa_resources)
        self.assertIn('support_groups', sa_resources)
        
        # Check crisis lines
        crisis_lines = sa_resources['crisis_lines']
        self.assertIsInstance(crisis_lines, list)
        self.assertGreater(len(crisis_lines), 0)
        
        # Verify South African contact numbers
        for crisis_line in crisis_lines:
            contact = crisis_line.get('phone', '')
            # South African numbers should start with +27 or 0
            self.assertTrue(
                contact.startswith('+27') or contact.startswith('0') or 'toll-free' in contact.lower(),
                f"Crisis line {crisis_line['name']} should have SA contact number"
            )

class TestResourceManagerPerformance(PerformanceTestCase):
    """Performance tests for ResourceManager"""
    
    def setUp(self):
        """Set up performance test environment"""
        super().setUp()
        
        if ResourceManager:
            self.resource_manager = ResourceManager(data_dir=self.temp_dir)
        else:
            self.skipTest("ResourceManager not available")
    
    def test_resource_loading_performance(self):
        """Test resource loading performance"""
        def load_all_resources():
            crisis = self.resource_manager.get_crisis_resources()
            coping = self.resource_manager.get_coping_strategies()
            education = self.resource_manager.get_educational_content()
            professionals = self.resource_manager.find_professional_help()
            tools = self.resource_manager.get_wellness_tools()
            return len(crisis) + len(coping) + len(education) + len(professionals) + len(tools)
        
        # Loading all resources should complete within 2 seconds
        total_resources = self.assert_execution_time_under(load_all_resources, 2.0)
        self.assertGreater(total_resources, 0)
    
    def test_search_performance(self):
        """Test search performance"""
        def search_resources():
            return self.resource_manager.search_resources("anxiety depression stress")
        
        # Search should complete within 1 second
        results = self.assert_execution_time_under(search_resources, 1.0)
        self.assertIsInstance(results, list)
    
    def test_personalized_recommendations_performance(self):
        """Test personalized recommendations performance"""
        user_profile = {
            'concerns': ['anxiety', 'depression', 'stress'],
            'location': 'Cape Town',
            'preferred_language': 'en',
            'experience_level': 'intermediate'
        }
        
        def get_recommendations():
            return self.resource_manager.get_personalized_recommendations(user_profile)
        
        # Recommendations should complete within 1.5 seconds
        recommendations = self.assert_execution_time_under(get_recommendations, 1.5)
        self.assertIsInstance(recommendations, dict)

class TestResourceManagerMocked(MockTestCase):
    """Test ResourceManager with mocked dependencies"""
    
    def setUp(self):
        """Set up mocked test environment"""
        super().setUp()
        
        if ResourceManager:
            self.resource_manager = ResourceManager(data_dir=self.temp_dir)
        else:
            self.skipTest("ResourceManager not available")
    
    @patch('resources.os.path.exists')
    @patch('resources.open')
    def test_load_resources_file_not_found(self, mock_open, mock_exists):
        """Test loading resources when file doesn't exist"""
        mock_exists.return_value = False
        
        # Should return empty list when file doesn't exist
        result = self.resource_manager._load_resource_file('nonexistent.json')
        self.assertEqual(result, [])
    
    @patch('resources.json.load')
    @patch('resources.open')
    def test_load_resources_corrupted_file(self, mock_open, mock_json_load):
        """Test loading resources from corrupted file"""
        mock_json_load.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        
        # Should return empty list when file is corrupted
        result = self.resource_manager._load_resource_file('corrupted.json')
        self.assertEqual(result, [])
    
    @patch('resources.requests.get')
    def test_external_api_failure(self, mock_get):
        """Test handling of external API failures"""
        # Mock API failure
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response
        
        # Should handle API failures gracefully
        result = self.resource_manager._fetch_external_resources()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)  # Should return empty list on failure

class TestMentalHealthResource(BaseTestCase):
    """Test MentalHealthResource dataclass"""
    
    def test_mental_health_resource_creation(self):
        """Test MentalHealthResource creation"""
        if not MentalHealthResource or not ResourceType:
            self.skipTest("MentalHealthResource or ResourceType not available")
        
        resource = MentalHealthResource(
            id="test-123",
            title="Test Resource",
            description="A test mental health resource",
            type=ResourceType.COPING_STRATEGY,
            content="Test content",
            tags=["anxiety", "breathing"],
            difficulty_level="beginner",
            estimated_time=10,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.assertEqual(resource.id, "test-123")
        self.assertEqual(resource.title, "Test Resource")
        self.assertEqual(resource.type, ResourceType.COPING_STRATEGY)
        self.assertIn("anxiety", resource.tags)
    
    def test_mental_health_resource_to_dict(self):
        """Test MentalHealthResource conversion to dictionary"""
        if not MentalHealthResource or not ResourceType:
            self.skipTest("MentalHealthResource or ResourceType not available")
        
        resource = MentalHealthResource(
            id="test-123",
            title="Test Resource",
            description="A test mental health resource",
            type=ResourceType.EDUCATIONAL,
            content="Test content",
            tags=["depression", "cbt"],
            difficulty_level="intermediate",
            estimated_time=15,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        resource_dict = resource.to_dict()
        
        self.assertIsInstance(resource_dict, dict)
        self.assertEqual(resource_dict["id"], "test-123")
        self.assertEqual(resource_dict["title"], "Test Resource")
        self.assertEqual(resource_dict["type"], ResourceType.EDUCATIONAL.value)
        self.assertIn("depression", resource_dict["tags"])

class TestResourceTypes(BaseTestCase):
    """Test ResourceType and IssueType enums"""
    
    def test_resource_type_enum(self):
        """Test ResourceType enum values"""
        if not ResourceType:
            self.skipTest("ResourceType not available")
        
        expected_types = [
            'CRISIS_RESOURCE',
            'COPING_STRATEGY',
            'EDUCATIONAL',
            'PROFESSIONAL_HELP',
            'WELLNESS_TOOL'
        ]
        
        for expected_type in expected_types:
            self.assertTrue(
                hasattr(ResourceType, expected_type),
                f"ResourceType should have {expected_type}"
            )
    
    def test_issue_type_enum(self):
        """Test IssueType enum values"""
        if not IssueType:
            self.skipTest("IssueType not available")
        
        expected_issues = [
            'ANXIETY',
            'DEPRESSION',
            'STRESS',
            'TRAUMA',
            'ADDICTION',
            'RELATIONSHIPS',
            'GRIEF',
            'GENERAL'
        ]
        
        for expected_issue in expected_issues:
            self.assertTrue(
                hasattr(IssueType, expected_issue),
                f"IssueType should have {expected_issue}"
            )

if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)