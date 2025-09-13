# ChillBuddy Mental Health Chatbot - Mental Health Resources Management
#
# This file contains:
# - Mental health resource database
# - Coping strategy recommendations
# - Educational content management
# - Professional help directory
# - Self-help tool collection
# - Resource personalization

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class ResourceType(Enum):
    COPING_STRATEGY = "coping_strategy"
    EDUCATIONAL = "educational"
    PROFESSIONAL_HELP = "professional_help"
    CRISIS_SUPPORT = "crisis_support"
    WELLNESS_TOOL = "wellness_tool"
    SELF_ASSESSMENT = "self_assessment"

class IssueType(Enum):
    ANXIETY = "anxiety"
    DEPRESSION = "depression"
    STRESS = "stress"
    TRAUMA = "trauma"
    ADDICTION = "addiction"
    RELATIONSHIPS = "relationships"
    WORKPLACE = "workplace"
    ACADEMIC = "academic"
    GENERAL = "general"

@dataclass
class MentalHealthResource:
    id: str
    title: str
    description: str
    resource_type: ResourceType
    issue_types: List[IssueType]
    content: Dict[str, Any]
    url: Optional[str] = None
    location: Optional[str] = None
    contact_info: Optional[Dict[str, str]] = None
    rating: float = 0.0
    usage_count: int = 0
    is_crisis_resource: bool = False
    is_south_african: bool = False
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class ResourceManager:
    def __init__(self):
        """Initialize ResourceManager with comprehensive mental health resources"""
        self.resources: Dict[str, MentalHealthResource] = {}
        self.resource_usage: Dict[str, Dict[str, int]] = {}  # user_id -> resource_id -> count
        self.logger = logging.getLogger(__name__)
        
        # Initialize resource database
        self._load_mental_health_resources()
        self.logger.info("ResourceManager initialized with comprehensive resource database")
    
    def _load_mental_health_resources(self):
        """Load comprehensive mental health resource database"""
        try:
            # Crisis Resources
            self._load_crisis_resources()
            
            # Coping Strategies
            self._load_coping_strategies()
            
            # Educational Content
            self._load_educational_content()
            
            # Professional Help Directory
            self._load_professional_directory()
            
            # Wellness Tools
            self._load_wellness_tools()
            
            # South African Specific Resources
            self._load_south_african_resources()
            
            self.logger.info(f"Loaded {len(self.resources)} mental health resources")
            
        except Exception as e:
            self.logger.error(f"Error loading mental health resources: {e}")
    
    def _load_crisis_resources(self):
        """Load crisis intervention resources"""
        crisis_resources = [
            {
                "id": "crisis_hotline_international",
                "title": "International Crisis Hotlines",
                "description": "24/7 crisis support hotlines worldwide",
                "content": {
                    "hotlines": {
                        "South Africa": "0800 567 567 (SADAG)",
                        "USA": "988 (Suicide & Crisis Lifeline)",
                        "UK": "116 123 (Samaritans)",
                        "Australia": "13 11 14 (Lifeline)",
                        "Canada": "1-833-456-4566"
                    },
                    "instructions": "Call immediately if you're having thoughts of self-harm or suicide"
                },
                "is_crisis_resource": True
            },
            {
                "id": "safety_planning",
                "title": "Safety Planning Guide",
                "description": "Step-by-step guide to create a personal safety plan",
                "content": {
                    "steps": [
                        "Identify warning signs of crisis",
                        "List coping strategies that work for you",
                        "Identify people who can provide support",
                        "List professional contacts",
                        "Make environment safe by removing means of harm",
                        "Create reasons for living list"
                    ],
                    "template": "Downloadable safety plan template"
                },
                "is_crisis_resource": True
            }
        ]
        
        for resource_data in crisis_resources:
            resource = MentalHealthResource(
                id=resource_data["id"],
                title=resource_data["title"],
                description=resource_data["description"],
                resource_type=ResourceType.CRISIS_SUPPORT,
                issue_types=[IssueType.GENERAL],
                content=resource_data["content"],
                is_crisis_resource=resource_data.get("is_crisis_resource", False)
            )
            self.resources[resource.id] = resource
    
    def _load_coping_strategies(self):
        """Load coping strategies and techniques"""
        coping_strategies = [
            {
                "id": "breathing_exercises",
                "title": "Breathing Exercises",
                "description": "Calming breathing techniques for anxiety and stress",
                "issue_types": [IssueType.ANXIETY, IssueType.STRESS],
                "content": {
                    "techniques": {
                        "4-7-8_breathing": {
                            "name": "4-7-8 Breathing",
                            "instructions": "Inhale for 4, hold for 7, exhale for 8",
                            "duration": "3-5 minutes",
                            "benefits": "Reduces anxiety and promotes relaxation"
                        },
                        "box_breathing": {
                            "name": "Box Breathing",
                            "instructions": "Inhale 4, hold 4, exhale 4, hold 4",
                            "duration": "5-10 minutes",
                            "benefits": "Improves focus and reduces stress"
                        },
                        "belly_breathing": {
                            "name": "Diaphragmatic Breathing",
                            "instructions": "Breathe deeply into your belly, not chest",
                            "duration": "10-15 minutes",
                            "benefits": "Activates relaxation response"
                        }
                    }
                }
            },
            {
                "id": "grounding_techniques",
                "title": "Grounding Techniques",
                "description": "Techniques to stay present and manage overwhelming emotions",
                "issue_types": [IssueType.ANXIETY, IssueType.TRAUMA],
                "content": {
                    "5_4_3_2_1_technique": {
                        "name": "5-4-3-2-1 Grounding",
                        "instructions": "5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste"
                    },
                    "progressive_muscle_relaxation": {
                        "name": "Progressive Muscle Relaxation",
                        "instructions": "Tense and release muscle groups from toes to head"
                    },
                    "mindful_observation": {
                        "name": "Mindful Observation",
                        "instructions": "Focus intently on one object for 2-3 minutes"
                    }
                }
            },
            {
                "id": "cognitive_strategies",
                "title": "Cognitive Behavioral Techniques",
                "description": "Thought challenging and cognitive restructuring techniques",
                "issue_types": [IssueType.DEPRESSION, IssueType.ANXIETY],
                "content": {
                    "thought_challenging": {
                        "questions": [
                            "Is this thought realistic?",
                            "What evidence supports/contradicts this thought?",
                            "What would I tell a friend in this situation?",
                            "What's the worst/best/most likely outcome?"
                        ]
                    },
                    "cognitive_distortions": [
                        "All-or-nothing thinking",
                        "Catastrophizing",
                        "Mind reading",
                        "Emotional reasoning",
                        "Should statements"
                    ]
                }
            }
        ]
        
        for strategy_data in coping_strategies:
            resource = MentalHealthResource(
                id=strategy_data["id"],
                title=strategy_data["title"],
                description=strategy_data["description"],
                resource_type=ResourceType.COPING_STRATEGY,
                issue_types=strategy_data["issue_types"],
                content=strategy_data["content"]
            )
            self.resources[resource.id] = resource
    
    def _load_educational_content(self):
        """Load educational mental health content"""
        educational_content = [
            {
                "id": "understanding_anxiety",
                "title": "Understanding Anxiety Disorders",
                "description": "Comprehensive guide to anxiety disorders and treatment",
                "issue_types": [IssueType.ANXIETY],
                "content": {
                    "overview": "Anxiety is a normal response to stress, but can become problematic",
                    "types": [
                        "Generalized Anxiety Disorder",
                        "Panic Disorder",
                        "Social Anxiety Disorder",
                        "Specific Phobias"
                    ],
                    "symptoms": [
                        "Excessive worry",
                        "Restlessness",
                        "Difficulty concentrating",
                        "Physical symptoms (racing heart, sweating)"
                    ],
                    "treatments": [
                        "Cognitive Behavioral Therapy",
                        "Exposure Therapy",
                        "Medication (when appropriate)",
                        "Lifestyle changes"
                    ]
                }
            },
            {
                "id": "depression_guide",
                "title": "Understanding Depression",
                "description": "Comprehensive information about depression and recovery",
                "issue_types": [IssueType.DEPRESSION],
                "content": {
                    "overview": "Depression is more than feeling sad - it's a serious mental health condition",
                    "symptoms": [
                        "Persistent sadness",
                        "Loss of interest in activities",
                        "Changes in appetite or sleep",
                        "Fatigue and low energy",
                        "Difficulty concentrating"
                    ],
                    "treatments": [
                        "Psychotherapy (CBT, IPT)",
                        "Medication",
                        "Lifestyle interventions",
                        "Support groups"
                    ],
                    "self_help": [
                        "Regular exercise",
                        "Healthy sleep habits",
                        "Social connection",
                        "Mindfulness practices"
                    ]
                }
            }
        ]
        
        for content_data in educational_content:
            resource = MentalHealthResource(
                id=content_data["id"],
                title=content_data["title"],
                description=content_data["description"],
                resource_type=ResourceType.EDUCATIONAL,
                issue_types=content_data["issue_types"],
                content=content_data["content"]
            )
            self.resources[resource.id] = resource
    
    def _load_professional_directory(self):
        """Load professional mental health services directory"""
        professional_services = [
            {
                "id": "therapy_types",
                "title": "Types of Therapy",
                "description": "Guide to different types of psychotherapy",
                "content": {
                    "therapy_types": {
                        "CBT": "Cognitive Behavioral Therapy - focuses on changing negative thought patterns",
                        "DBT": "Dialectical Behavior Therapy - teaches emotional regulation skills",
                        "EMDR": "Eye Movement Desensitization - trauma-focused therapy",
                        "Psychodynamic": "Explores unconscious thoughts and past experiences",
                        "Humanistic": "Person-centered approach focusing on self-acceptance"
                    },
                    "how_to_choose": [
                        "Consider your specific needs and goals",
                        "Research therapist credentials and specialties",
                        "Consider practical factors (location, cost, insurance)",
                        "Trust your instincts about therapeutic fit"
                    ]
                }
            }
        ]
        
        for service_data in professional_services:
            resource = MentalHealthResource(
                id=service_data["id"],
                title=service_data["title"],
                description=service_data["description"],
                resource_type=ResourceType.PROFESSIONAL_HELP,
                issue_types=[IssueType.GENERAL],
                content=service_data["content"]
            )
            self.resources[resource.id] = resource
    
    def _load_wellness_tools(self):
        """Load wellness and self-care tools"""
        wellness_tools = [
            {
                "id": "mood_tracking",
                "title": "Mood Tracking Guide",
                "description": "How to track and understand your mood patterns",
                "content": {
                    "benefits": [
                        "Identify mood patterns and triggers",
                        "Track treatment effectiveness",
                        "Improve self-awareness",
                        "Facilitate communication with healthcare providers"
                    ],
                    "tracking_methods": [
                        "Daily mood ratings (1-10 scale)",
                        "Emotion words and intensity",
                        "Trigger identification",
                        "Sleep, exercise, and medication tracking"
                    ]
                }
            },
            {
                "id": "sleep_hygiene",
                "title": "Sleep Hygiene for Mental Health",
                "description": "Improving sleep quality to support mental wellness",
                "content": {
                    "sleep_tips": [
                        "Maintain consistent sleep schedule",
                        "Create relaxing bedtime routine",
                        "Limit screen time before bed",
                        "Keep bedroom cool, dark, and quiet",
                        "Avoid caffeine and alcohol before bedtime"
                    ],
                    "sleep_mental_health_connection": "Poor sleep can worsen anxiety and depression, while good sleep supports emotional regulation"
                }
            }
        ]
        
        for tool_data in wellness_tools:
            resource = MentalHealthResource(
                id=tool_data["id"],
                title=tool_data["title"],
                description=tool_data["description"],
                resource_type=ResourceType.WELLNESS_TOOL,
                issue_types=[IssueType.GENERAL],
                content=tool_data["content"]
            )
            self.resources[resource.id] = resource
    
    def _load_south_african_resources(self):
        """Load South African specific mental health resources"""
        sa_resources = [
            {
                "id": "sadag_resources",
                "title": "South African Depression and Anxiety Group (SADAG)",
                "description": "Leading mental health organization in South Africa",
                "contact_info": {
                    "phone": "0800 567 567",
                    "sms": "31393",
                    "website": "https://www.sadag.org",
                    "email": "help@sadag.org"
                },
                "content": {
                    "services": [
                        "24/7 helpline",
                        "Support groups",
                        "Educational resources",
                        "Referral services",
                        "Online counseling"
                    ],
                    "specialties": [
                        "Depression",
                        "Anxiety",
                        "Bipolar disorder",
                        "Suicide prevention",
                        "Substance abuse"
                    ]
                },
                "location": "South Africa",
                "is_south_african": True
            },
            {
                "id": "lifeline_sa",
                "title": "Lifeline South Africa",
                "description": "Crisis counseling and suicide prevention",
                "contact_info": {
                    "phone": "0861 322 322",
                    "website": "https://www.lifeline.org.za"
                },
                "content": {
                    "services": [
                        "24/7 crisis counseling",
                        "Suicide prevention",
                        "Trauma counseling",
                        "Training programs"
                    ]
                },
                "location": "South Africa",
                "is_crisis_resource": True,
                "is_south_african": True
            },
            {
                "id": "uct_counseling",
                "title": "UCT Student Counseling Centre",
                "description": "Mental health support for UCT students",
                "contact_info": {
                    "phone": "021 650 1017",
                    "email": "student-counselling@uct.ac.za",
                    "location": "Level 4, Steve Biko Students' Union Building"
                },
                "content": {
                    "services": [
                        "Individual counseling",
                        "Group therapy",
                        "Crisis intervention",
                        "Workshops and seminars",
                        "Psychiatric services"
                    ],
                    "hours": "Monday-Friday: 8:00-16:30"
                },
                "location": "Cape Town, South Africa",
                "is_south_african": True
            }
        ]
        
        for sa_data in sa_resources:
            resource = MentalHealthResource(
                id=sa_data["id"],
                title=sa_data["title"],
                description=sa_data["description"],
                resource_type=ResourceType.PROFESSIONAL_HELP,
                issue_types=[IssueType.GENERAL],
                content=sa_data["content"],
                contact_info=sa_data.get("contact_info"),
                location=sa_data.get("location"),
                is_crisis_resource=sa_data.get("is_crisis_resource", False),
                is_south_african=sa_data.get("is_south_african", False)
            )
            self.resources[resource.id] = resource
    
    def get_resources(self, resource_type: str = "all", user_id: str = None, location: str = None) -> List[Dict[str, Any]]:
        """Get mental health resources based on filters"""
        try:
            filtered_resources = []
            
            for resource in self.resources.values():
                # Filter by resource type
                if resource_type != "all" and resource.resource_type.value != resource_type:
                    continue
                
                # Filter by location if specified
                if location and resource.location and location.lower() not in resource.location.lower():
                    continue
                
                # Convert to dict for response
                resource_dict = {
                    "id": resource.id,
                    "title": resource.title,
                    "description": resource.description,
                    "resource_type": resource.resource_type.value,
                    "issue_types": [issue.value for issue in resource.issue_types],
                    "content": resource.content,
                    "url": resource.url,
                    "location": resource.location,
                    "contact_info": resource.contact_info,
                    "rating": resource.rating,
                    "is_crisis_resource": resource.is_crisis_resource,
                    "is_south_african": resource.is_south_african
                }
                
                filtered_resources.append(resource_dict)
            
            # Sort by rating and usage
            filtered_resources.sort(key=lambda x: (x["rating"], x.get("usage_count", 0)), reverse=True)
            
            self.logger.info(f"Retrieved {len(filtered_resources)} resources for type: {resource_type}")
            return filtered_resources
            
        except Exception as e:
            self.logger.error(f"Error getting resources: {e}")
            return []
    
    def get_crisis_resources(self, crisis_type: str = "general", user_location: str = None) -> List[Dict[str, Any]]:
        """Get crisis-specific resources"""
        try:
            crisis_resources = []
            
            for resource in self.resources.values():
                if resource.is_crisis_resource:
                    # Prioritize South African resources if user is in SA
                    if user_location and "south africa" in user_location.lower():
                        if resource.is_south_african:
                            crisis_resources.insert(0, resource)
                        else:
                            crisis_resources.append(resource)
                    else:
                        crisis_resources.append(resource)
            
            # Convert to dict format
            result = []
            for resource in crisis_resources:
                resource_dict = {
                    "id": resource.id,
                    "title": resource.title,
                    "description": resource.description,
                    "content": resource.content,
                    "contact_info": resource.contact_info,
                    "location": resource.location,
                    "is_south_african": resource.is_south_african
                }
                result.append(resource_dict)
            
            self.logger.info(f"Retrieved {len(result)} crisis resources")
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting crisis resources: {e}")
            return []
    
    def get_coping_strategies(self, issue_type: str) -> List[Dict[str, Any]]:
        """Get coping strategies for specific issues"""
        try:
            strategies = []
            
            for resource in self.resources.values():
                if (resource.resource_type == ResourceType.COPING_STRATEGY and
                    (issue_type == "general" or 
                     any(issue.value == issue_type for issue in resource.issue_types))):
                    
                    strategy_dict = {
                        "id": resource.id,
                        "title": resource.title,
                        "description": resource.description,
                        "content": resource.content,
                        "issue_types": [issue.value for issue in resource.issue_types]
                    }
                    strategies.append(strategy_dict)
            
            self.logger.info(f"Retrieved {len(strategies)} coping strategies for {issue_type}")
            return strategies
            
        except Exception as e:
            self.logger.error(f"Error getting coping strategies: {e}")
            return []
    
    def search_resources(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search through resource database"""
        try:
            if not query:
                return []
            
            query_lower = query.lower()
            matching_resources = []
            
            for resource in self.resources.values():
                # Search in title, description, and content
                searchable_text = f"{resource.title} {resource.description} {str(resource.content)}".lower()
                
                if query_lower in searchable_text:
                    resource_dict = {
                        "id": resource.id,
                        "title": resource.title,
                        "description": resource.description,
                        "resource_type": resource.resource_type.value,
                        "content": resource.content,
                        "relevance_score": self._calculate_relevance(query_lower, searchable_text)
                    }
                    matching_resources.append(resource_dict)
            
            # Sort by relevance
            matching_resources.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            self.logger.info(f"Found {len(matching_resources)} resources matching query: {query}")
            return matching_resources
            
        except Exception as e:
            self.logger.error(f"Error searching resources: {e}")
            return []
    
    def track_resource_usage(self, user_id: str, resource_id: str) -> bool:
        """Track resource usage for analytics"""
        try:
            if user_id not in self.resource_usage:
                self.resource_usage[user_id] = {}
            
            if resource_id not in self.resource_usage[user_id]:
                self.resource_usage[user_id][resource_id] = 0
            
            self.resource_usage[user_id][resource_id] += 1
            
            # Update resource usage count
            if resource_id in self.resources:
                self.resources[resource_id].usage_count += 1
            
            self.logger.info(f"Tracked resource usage: user {user_id}, resource {resource_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error tracking resource usage: {e}")
            return False
    
    def recommend_resources(self, user_profile: Dict[str, Any], current_mood: str = None) -> List[Dict[str, Any]]:
        """Get personalized resource recommendations"""
        try:
            recommendations = []
            
            # Get user's primary concerns
            concerns = user_profile.get("mental_health_goals", [])
            location = user_profile.get("location")
            
            # Prioritize resources based on user needs
            for resource in self.resources.values():
                relevance_score = 0
                
                # Score based on issue type match
                for concern in concerns:
                    if any(issue.value == concern for issue in resource.issue_types):
                        relevance_score += 2
                
                # Boost South African resources for SA users
                if location and "south africa" in location.lower() and resource.is_south_african:
                    relevance_score += 1
                
                # Boost highly rated resources
                relevance_score += resource.rating / 5.0
                
                if relevance_score > 0:
                    resource_dict = {
                        "id": resource.id,
                        "title": resource.title,
                        "description": resource.description,
                        "resource_type": resource.resource_type.value,
                        "relevance_score": relevance_score,
                        "content": resource.content
                    }
                    recommendations.append(resource_dict)
            
            # Sort by relevance and limit results
            recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            self.logger.info(f"Generated {len(recommendations)} personalized recommendations")
            return recommendations[:10]  # Return top 10
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _calculate_relevance(self, query: str, text: str) -> float:
        """Calculate relevance score for search results"""
        try:
            # Simple relevance scoring based on term frequency
            query_terms = query.split()
            score = 0
            
            for term in query_terms:
                count = text.count(term)
                score += count
            
            # Normalize by text length
            return score / len(text.split()) if text else 0
            
        except Exception as e:
            self.logger.error(f"Error calculating relevance: {e}")
            return 0
    
    def get_resource_by_id(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get specific resource by ID"""
        try:
            if resource_id in self.resources:
                resource = self.resources[resource_id]
                return {
                    "id": resource.id,
                    "title": resource.title,
                    "description": resource.description,
                    "resource_type": resource.resource_type.value,
                    "issue_types": [issue.value for issue in resource.issue_types],
                    "content": resource.content,
                    "url": resource.url,
                    "location": resource.location,
                    "contact_info": resource.contact_info,
                    "rating": resource.rating,
                    "is_crisis_resource": resource.is_crisis_resource,
                    "is_south_african": resource.is_south_african
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting resource by ID: {e}")
            return None
    
    def get_resource_statistics(self) -> Dict[str, Any]:
        """Get resource database statistics"""
        try:
            stats = {
                "total_resources": len(self.resources),
                "by_type": {},
                "by_issue": {},
                "crisis_resources": sum(1 for r in self.resources.values() if r.is_crisis_resource),
                "south_african_resources": sum(1 for r in self.resources.values() if r.is_south_african),
                "total_usage": sum(r.usage_count for r in self.resources.values())
            }
            
            # Count by resource type
            for resource in self.resources.values():
                resource_type = resource.resource_type.value
                stats["by_type"][resource_type] = stats["by_type"].get(resource_type, 0) + 1
                
                # Count by issue type
                for issue in resource.issue_types:
                    issue_type = issue.value
                    stats["by_issue"][issue_type] = stats["by_issue"].get(issue_type, 0) + 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting resource statistics: {e}")
            return {}