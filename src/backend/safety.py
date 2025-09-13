# ChillBuddy Mental Health Chatbot - Safety and Crisis Management
#
# This file contains:
# - Crisis keyword detection
# - Risk assessment algorithms
# - Emergency response protocols
# - Safety resource management
# - Professional referral systems
# - Incident logging and reporting

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
import os
import re
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    """Risk assessment levels for user messages"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SafetyAlert:
    """Data structure for safety alerts"""
    risk_level: RiskLevel
    detected_keywords: List[str]
    confidence_score: float
    timestamp: datetime
    user_id: str
    message_content: str
    recommended_action: str

class SafetyManager:
    """
    Comprehensive safety management system for ChillBuddy.
    
    This class handles:
    - Crisis detection and intervention
    - Content filtering and moderation
    - Emergency protocol activation
    - Safety alert generation and logging
    - Integration with mental health resources
    
    The safety system is designed to be the first line of defense
    in protecting users and ensuring responsible AI interactions.
    """
    
    def __init__(self, config_path: str = "models/safety_filters.json"):
        """
        Initialize the SafetyManager with configuration and filters.
        
        Args:
            config_path: Path to safety configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self.safety_filters = {}
        self.crisis_keywords = []
        self.emergency_contacts = {}
        self.alert_history = []
        
        # Default crisis keywords if config fails to load
        self.default_crisis_keywords = [
            "suicide", "kill myself", "end it all", "want to die", "hurt myself",
            "self harm", "cutting", "overdose", "jump off", "hang myself",
            "worthless", "hopeless", "can't go on", "better off dead", "no point"
        ]
        
        # Default emergency resources
        self.default_resources = {
            "crisis_hotline": "988 (Suicide & Crisis Lifeline)",
            "text_line": "Text HOME to 741741",
            "emergency": "911 for immediate emergency"
        }
        
        self.load_safety_config()
        
    def load_safety_config(self) -> bool:
        """
        Load safety configuration from JSON file.
        
        Returns:
            bool: True if configuration loaded successfully
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                self.crisis_keywords = config.get('crisis_keywords', self.default_crisis_keywords)
                self.safety_filters = config.get('content_filters', {})
                self.emergency_contacts = config.get('emergency_contacts', self.default_resources)
                
                self.logger.info(f"Safety configuration loaded from {self.config_path}")
                return True
            else:
                self.logger.warning(f"Safety config file not found: {self.config_path}. Using defaults.")
                self.crisis_keywords = self.default_crisis_keywords
                self.emergency_contacts = self.default_resources
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading safety configuration: {e}")
            self.crisis_keywords = self.default_crisis_keywords
            self.emergency_contacts = self.default_resources
            return False
    
    def assess_risk(self, message: str, user_id: str, context: Dict[str, Any] = None) -> SafetyAlert:
        """
        Assess the risk level of a user message.
        
        Args:
            message: User's message content
            user_id: Unique identifier for the user
            context: Additional context information
            
        Returns:
            SafetyAlert: Comprehensive risk assessment
        """
        try:
            # Detect crisis indicators
            is_crisis, detected_keywords, confidence = self.detect_crisis(message)
            
            # Determine risk level based on detection results
            if confidence >= 0.8:
                risk_level = RiskLevel.CRITICAL
                action = "Immediate intervention required - provide crisis resources"
            elif confidence >= 0.6:
                risk_level = RiskLevel.HIGH
                action = "High concern - offer support and monitor closely"
            elif confidence >= 0.3:
                risk_level = RiskLevel.MEDIUM
                action = "Moderate concern - provide supportive response"
            else:
                risk_level = RiskLevel.LOW
                action = "Continue normal conversation with empathy"
            
            # Create safety alert
            alert = SafetyAlert(
                risk_level=risk_level,
                detected_keywords=detected_keywords,
                confidence_score=confidence,
                timestamp=datetime.now(),
                user_id=user_id,
                message_content=message[:200] + "..." if len(message) > 200 else message,
                recommended_action=action
            )
            
            # Log the alert
            self.log_safety_event(alert)
            
            return alert
            
        except Exception as e:
            self.logger.error(f"Error in risk assessment: {e}")
            # Return safe default
            return SafetyAlert(
                risk_level=RiskLevel.LOW,
                detected_keywords=[],
                confidence_score=0.0,
                timestamp=datetime.now(),
                user_id=user_id,
                message_content="Error in assessment",
                recommended_action="Continue with caution"
            )
    
    def detect_crisis(self, message: str) -> Tuple[bool, List[str], float]:
        """
        Detect potential crisis situations in user messages.
        
        Args:
            message: User's message to analyze
            
        Returns:
            Tuple containing:
            - bool: Whether crisis indicators were detected
            - List[str]: Detected crisis keywords/patterns
            - float: Confidence score (0.0 to 1.0)
        """
        try:
            message_lower = message.lower()
            detected_keywords = []
            total_score = 0.0
            
            # Check for direct crisis keywords
            for keyword in self.crisis_keywords:
                if keyword.lower() in message_lower:
                    detected_keywords.append(keyword)
                    # Weight keywords by severity
                    if keyword in ["suicide", "kill myself", "want to die"]:
                        total_score += 0.4
                    elif keyword in ["hurt myself", "self harm", "overdose"]:
                        total_score += 0.3
                    else:
                        total_score += 0.2
            
            # Check for crisis patterns using regex
            crisis_patterns = [
                r"\b(want to|going to|plan to)\s+(die|kill|hurt)\b",
                r"\b(can't|cannot)\s+(take|handle|deal with)\s+(this|it|anymore)\b",
                r"\b(no one|nobody)\s+(cares|loves|understands)\b",
                r"\b(life is|everything is)\s+(pointless|meaningless|hopeless)\b"
            ]
            
            for pattern in crisis_patterns:
                if re.search(pattern, message_lower):
                    detected_keywords.append(f"Pattern: {pattern}")
                    total_score += 0.25
            
            # Cap the confidence score at 1.0
            confidence_score = min(total_score, 1.0)
            
            # Crisis detected if confidence > 0.2 or any keywords found
            is_crisis = confidence_score > 0.2 or len(detected_keywords) > 0
            
            return is_crisis, detected_keywords, confidence_score
            
        except Exception as e:
            self.logger.error(f"Error in crisis detection: {e}")
            return False, [], 0.0
    
    def filter_content(self, message: str) -> Tuple[bool, str, List[str]]:
        """
        Filter and moderate message content.
        
        Args:
            message: Message content to filter
            
        Returns:
            Tuple containing:
            - bool: Whether content is safe
            - str: Filtered/cleaned message
            - List[str]: List of issues found
        """
        try:
            issues = []
            cleaned_message = message.strip()
            
            # Check message length
            if len(cleaned_message) > 5000:
                issues.append("Message too long")
                cleaned_message = cleaned_message[:5000] + "..."
            
            if len(cleaned_message) == 0:
                issues.append("Empty message")
                return False, "", issues
            
            # Check for spam patterns
            spam_patterns = [
                r'(.)\1{10,}',  # Repeated characters
                r'[A-Z]{20,}',  # Excessive caps
                r'(http|www)\S+',  # URLs (for safety)
            ]
            
            for pattern in spam_patterns:
                if re.search(pattern, cleaned_message):
                    issues.append(f"Spam pattern detected: {pattern}")
            
            # Basic profanity filter (simple implementation)
            profanity_words = ['spam', 'scam', 'fake']  # Minimal list for demo
            for word in profanity_words:
                if word.lower() in cleaned_message.lower():
                    issues.append(f"Inappropriate content: {word}")
                    cleaned_message = re.sub(re.escape(word), '*' * len(word), cleaned_message, flags=re.IGNORECASE)
            
            # Content is safe if no critical issues found
            is_safe = len([issue for issue in issues if 'spam' not in issue.lower()]) == 0
            
            return is_safe, cleaned_message, issues
            
        except Exception as e:
            self.logger.error(f"Error in content filtering: {e}")
            return True, message, ["Error in content filtering"]
    
    def trigger_emergency_protocol(self, alert: SafetyAlert) -> Dict[str, Any]:
        """
        Trigger emergency response protocols for critical situations.
        
        Args:
            alert: SafetyAlert containing crisis information
            
        Returns:
            Dict containing emergency response details
        """
        try:
            response = {
                "alert_id": f"alert_{alert.timestamp.strftime('%Y%m%d_%H%M%S')}_{alert.user_id[:8]}",
                "timestamp": alert.timestamp.isoformat(),
                "risk_level": alert.risk_level.value,
                "actions_taken": [],
                "resources_provided": [],
                "follow_up_required": False
            }
            
            # Log critical alert
            if alert.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                self.logger.critical(f"CRISIS ALERT - User: {alert.user_id}, Risk: {alert.risk_level.value}, Keywords: {alert.detected_keywords}")
                response["actions_taken"].append("Critical alert logged")
            
            # Get appropriate crisis resources
            resources = self.get_crisis_resources(alert.risk_level)
            response["resources_provided"] = resources
            
            # Determine follow-up requirements
            if alert.risk_level == RiskLevel.CRITICAL:
                response["follow_up_required"] = True
                response["actions_taken"].append("Follow-up scheduled")
            
            # Add emergency contacts for critical situations
            if alert.risk_level == RiskLevel.CRITICAL:
                response["emergency_contacts"] = self.emergency_contacts
                response["actions_taken"].append("Emergency contacts provided")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in emergency protocol: {e}")
            return {"error": "Emergency protocol failed", "timestamp": datetime.now().isoformat()}
    
    def get_crisis_resources(self, risk_level: RiskLevel) -> List[Dict[str, str]]:
        """
        Get appropriate crisis resources based on risk level.
        
        Args:
            risk_level: Assessed risk level
            
        Returns:
            List of crisis resources with contact information
        """
        try:
            resources = []
            
            if risk_level == RiskLevel.CRITICAL:
                resources.extend([
                    {
                        "name": "National Suicide Prevention Lifeline",
                        "contact": "988",
                        "description": "24/7 crisis support and suicide prevention",
                        "type": "phone"
                    },
                    {
                        "name": "Crisis Text Line",
                        "contact": "Text HOME to 741741",
                        "description": "24/7 text-based crisis support",
                        "type": "text"
                    },
                    {
                        "name": "Emergency Services",
                        "contact": "911",
                        "description": "Immediate emergency assistance",
                        "type": "emergency"
                    }
                ])
            
            elif risk_level == RiskLevel.HIGH:
                resources.extend([
                    {
                        "name": "National Suicide Prevention Lifeline",
                        "contact": "988",
                        "description": "24/7 crisis support and suicide prevention",
                        "type": "phone"
                    },
                    {
                        "name": "SAMHSA National Helpline",
                        "contact": "1-800-662-4357",
                        "description": "Mental health and substance abuse support",
                        "type": "phone"
                    }
                ])
            
            elif risk_level == RiskLevel.MEDIUM:
                resources.extend([
                    {
                        "name": "NAMI Support",
                        "contact": "1-800-950-6264",
                        "description": "Mental health information and support",
                        "type": "phone"
                    },
                    {
                        "name": "Psychology Today",
                        "contact": "https://www.psychologytoday.com",
                        "description": "Find mental health professionals",
                        "type": "website"
                    }
                ])
            
            # Always include general support resources
            resources.append({
                "name": "ChillBuddy Support",
                "contact": "Available 24/7 through this app",
                "description": "Continue talking with ChillBuddy for ongoing support",
                "type": "app"
            })
            
            return resources
            
        except Exception as e:
            self.logger.error(f"Error getting crisis resources: {e}")
            return [{
                "name": "Emergency",
                "contact": "911",
                "description": "Call for immediate help",
                "type": "emergency"
            }]
    
    def log_safety_event(self, alert: SafetyAlert) -> None:
        """
        Log safety events for monitoring and analysis.
        
        Args:
            alert: SafetyAlert to log
        """
        try:
            # Add to in-memory history
            self.alert_history.append(alert)
            
            # Keep only last 1000 alerts in memory
            if len(self.alert_history) > 1000:
                self.alert_history = self.alert_history[-1000:]
            
            # Log to file (anonymized)
            log_entry = {
                "timestamp": alert.timestamp.isoformat(),
                "risk_level": alert.risk_level.value,
                "confidence_score": alert.confidence_score,
                "user_id_hash": hash(alert.user_id) % 10000,  # Anonymized user ID
                "keywords_count": len(alert.detected_keywords),
                "message_length": len(alert.message_content)
            }
            
            # Log based on severity
            if alert.risk_level == RiskLevel.CRITICAL:
                self.logger.critical(f"Safety Event: {log_entry}")
            elif alert.risk_level == RiskLevel.HIGH:
                self.logger.warning(f"Safety Event: {log_entry}")
            else:
                self.logger.info(f"Safety Event: {log_entry}")
                
        except Exception as e:
            self.logger.error(f"Error logging safety event: {e}")
    
    def get_safety_statistics(self, timeframe: timedelta = None) -> Dict[str, Any]:
        """
        Get safety statistics and metrics.
        
        Args:
            timeframe: Time period for statistics (default: last 24 hours)
            
        Returns:
            Dictionary containing safety metrics
        """
        try:
            if timeframe is None:
                timeframe = timedelta(hours=24)
            
            cutoff_time = datetime.now() - timeframe
            recent_alerts = [alert for alert in self.alert_history if alert.timestamp >= cutoff_time]
            
            stats = {
                "total_alerts": len(recent_alerts),
                "timeframe_hours": timeframe.total_seconds() / 3600,
                "risk_level_counts": {
                    "low": len([a for a in recent_alerts if a.risk_level == RiskLevel.LOW]),
                    "medium": len([a for a in recent_alerts if a.risk_level == RiskLevel.MEDIUM]),
                    "high": len([a for a in recent_alerts if a.risk_level == RiskLevel.HIGH]),
                    "critical": len([a for a in recent_alerts if a.risk_level == RiskLevel.CRITICAL])
                },
                "average_confidence": sum(a.confidence_score for a in recent_alerts) / len(recent_alerts) if recent_alerts else 0.0,
                "unique_users": len(set(a.user_id for a in recent_alerts))
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting safety statistics: {e}")
            return {"error": "Failed to generate statistics"}
    
    def update_safety_filters(self, new_filters: Dict[str, Any]) -> bool:
        """
        Update safety filters and configuration.
        
        Args:
            new_filters: Updated filter configuration
            
        Returns:
            bool: True if update was successful
        """
        try:
            # Validate new filters
            if "crisis_keywords" in new_filters:
                if isinstance(new_filters["crisis_keywords"], list):
                    self.crisis_keywords = new_filters["crisis_keywords"]
                else:
                    self.logger.error("Invalid crisis_keywords format")
                    return False
            
            if "content_filters" in new_filters:
                if isinstance(new_filters["content_filters"], dict):
                    self.safety_filters.update(new_filters["content_filters"])
                else:
                    self.logger.error("Invalid content_filters format")
                    return False
            
            if "emergency_contacts" in new_filters:
                if isinstance(new_filters["emergency_contacts"], dict):
                    self.emergency_contacts.update(new_filters["emergency_contacts"])
                else:
                    self.logger.error("Invalid emergency_contacts format")
                    return False
            
            # Save updated configuration
            try:
                config = {
                    "crisis_keywords": self.crisis_keywords,
                    "content_filters": self.safety_filters,
                    "emergency_contacts": self.emergency_contacts
                }
                
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                self.logger.info("Safety configuration updated successfully")
                return True
                
            except Exception as e:
                self.logger.error(f"Error saving updated configuration: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating safety filters: {e}")
            return False

# Crisis Response Templates:
# TODO: SUICIDE_RESPONSE_TEMPLATE - Immediate suicide crisis response
# TODO: SELF_HARM_RESPONSE_TEMPLATE - Self-harm crisis response
# TODO: ANXIETY_CRISIS_TEMPLATE - Severe anxiety crisis response
# TODO: DEPRESSION_CRISIS_TEMPLATE - Severe depression crisis response

# Emergency Contacts Database:
# TODO: SOUTH_AFRICA_CRISIS_LINES - Local crisis hotlines
# TODO: INTERNATIONAL_CRISIS_LINES - International crisis support
# TODO: PROFESSIONAL_REFERRAL_NETWORK - Mental health professional network
# TODO: EMERGENCY_SERVICES - Police, ambulance, hospital contacts

# Helper Functions:
# TODO: validate_emergency_contact(contact_info) - Verify contact information
# TODO: format_crisis_message(template, user_data) - Personalize crisis responses
# TODO: encrypt_sensitive_data(data) - Protect sensitive crisis data
# TODO: audit_safety_actions(action_log) - Review safety intervention effectiveness