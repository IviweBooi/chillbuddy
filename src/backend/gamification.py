# ChillBuddy Mental Health Chatbot - Gamification and User Engagement
#
# This file contains:
# - User progress tracking
# - Achievement and badge systems
# - Streak management
# - Challenge and goal setting
# - Reward mechanisms
# - Motivation and engagement features

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import random

logger = logging.getLogger(__name__)

class ActivityType(Enum):
    CONVERSATION = "conversation"
    MOOD_LOG = "mood_log"
    COPING_STRATEGY = "coping_strategy"
    RESOURCE_ACCESS = "resource_access"
    CHALLENGE_COMPLETE = "challenge_complete"
    DAILY_CHECKIN = "daily_checkin"
    CRISIS_SUPPORT = "crisis_support"

class AchievementType(Enum):
    MILESTONE = "milestone"
    STREAK = "streak"
    SKILL = "skill"
    ENGAGEMENT = "engagement"
    PROGRESS = "progress"

class ChallengeType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    achievement_type: AchievementType
    criteria: Dict[str, Any]
    points: int
    badge_icon: str
    unlocked_message: str
    is_hidden: bool = False
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class UserAchievement:
    achievement_id: str
    user_id: str
    unlocked_at: datetime
    progress: Dict[str, Any] = None

@dataclass
class Challenge:
    id: str
    name: str
    description: str
    challenge_type: ChallengeType
    duration_days: int
    criteria: Dict[str, Any]
    points_reward: int
    difficulty: str  # easy, medium, hard
    category: str  # mood, coping, social, etc.
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class UserChallenge:
    challenge_id: str
    user_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    progress: Dict[str, Any] = None
    is_active: bool = True

@dataclass
class UserProgress:
    user_id: str
    total_points: int = 0
    level: int = 1
    conversations_count: int = 0
    mood_logs_count: int = 0
    coping_strategies_used: int = 0
    resources_accessed: int = 0
    current_streaks: Dict[str, int] = None
    longest_streaks: Dict[str, int] = None
    last_activity: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.current_streaks is None:
            self.current_streaks = {"daily": 0, "mood": 0, "challenge": 0}
        if self.longest_streaks is None:
            self.longest_streaks = {"daily": 0, "mood": 0, "challenge": 0}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class GamificationManager:
    def __init__(self):
        """Initialize GamificationManager with achievement and challenge systems"""
        self.achievements: Dict[str, Achievement] = {}
        self.challenges: Dict[str, Challenge] = {}
        self.user_progress: Dict[str, UserProgress] = {}
        self.user_achievements: Dict[str, List[UserAchievement]] = {}
        self.user_challenges: Dict[str, List[UserChallenge]] = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize achievement and challenge definitions
        self._load_achievements()
        self._load_challenges()
        self.logger.info("GamificationManager initialized with engagement systems")
    
    def _load_achievements(self):
        """Load achievement definitions"""
        try:
            achievement_definitions = [
                {
                    "id": "first_conversation",
                    "name": "First Steps",
                    "description": "Had your first conversation with ChillBuddy",
                    "achievement_type": AchievementType.MILESTONE,
                    "criteria": {"conversations": 1},
                    "points": 10,
                    "badge_icon": "🌟",
                    "unlocked_message": "Welcome to ChillBuddy! You've taken the first step on your mental health journey."
                },
                {
                    "id": "week_warrior",
                    "name": "Week Warrior",
                    "description": "Maintained a 7-day conversation streak",
                    "achievement_type": AchievementType.STREAK,
                    "criteria": {"daily_streak": 7},
                    "points": 50,
                    "badge_icon": "🔥",
                    "unlocked_message": "Amazing! You've built a strong habit of daily check-ins."
                },
                {
                    "id": "mood_tracker",
                    "name": "Mood Master",
                    "description": "Logged your mood for 14 consecutive days",
                    "achievement_type": AchievementType.STREAK,
                    "criteria": {"mood_streak": 14},
                    "points": 75,
                    "badge_icon": "📊",
                    "unlocked_message": "Excellent self-awareness! Tracking your mood helps identify patterns."
                },
                {
                    "id": "coping_champion",
                    "name": "Coping Champion",
                    "description": "Used 5 different coping strategies",
                    "achievement_type": AchievementType.SKILL,
                    "criteria": {"unique_coping_strategies": 5},
                    "points": 100,
                    "badge_icon": "🛡️",
                    "unlocked_message": "You're building a strong toolkit for managing difficult emotions!"
                },
                {
                    "id": "resource_explorer",
                    "name": "Resource Explorer",
                    "description": "Accessed 10 different mental health resources",
                    "achievement_type": AchievementType.ENGAGEMENT,
                    "criteria": {"resources_accessed": 10},
                    "points": 60,
                    "badge_icon": "🔍",
                    "unlocked_message": "Great job exploring resources to support your mental health!"
                },
                {
                    "id": "challenge_crusher",
                    "name": "Challenge Crusher",
                    "description": "Completed 5 daily challenges",
                    "achievement_type": AchievementType.PROGRESS,
                    "criteria": {"challenges_completed": 5},
                    "points": 80,
                    "badge_icon": "💪",
                    "unlocked_message": "You're crushing your goals! Keep up the momentum."
                },
                {
                    "id": "month_milestone",
                    "name": "Monthly Milestone",
                    "description": "Active for 30 consecutive days",
                    "achievement_type": AchievementType.STREAK,
                    "criteria": {"daily_streak": 30},
                    "points": 200,
                    "badge_icon": "🏆",
                    "unlocked_message": "Incredible dedication! A month of consistent self-care is amazing."
                },
                {
                    "id": "crisis_survivor",
                    "name": "Crisis Survivor",
                    "description": "Reached out for crisis support when needed",
                    "achievement_type": AchievementType.MILESTONE,
                    "criteria": {"crisis_support_used": 1},
                    "points": 150,
                    "badge_icon": "🆘",
                    "unlocked_message": "Reaching out for help shows incredible strength and courage.",
                    "is_hidden": True
                }
            ]
            
            for achievement_data in achievement_definitions:
                achievement = Achievement(
                    id=achievement_data["id"],
                    name=achievement_data["name"],
                    description=achievement_data["description"],
                    achievement_type=achievement_data["achievement_type"],
                    criteria=achievement_data["criteria"],
                    points=achievement_data["points"],
                    badge_icon=achievement_data["badge_icon"],
                    unlocked_message=achievement_data["unlocked_message"],
                    is_hidden=achievement_data.get("is_hidden", False)
                )
                self.achievements[achievement.id] = achievement
            
            self.logger.info(f"Loaded {len(self.achievements)} achievements")
            
        except Exception as e:
            self.logger.error(f"Error loading achievements: {e}")
    
    def _load_challenges(self):
        """Load challenge definitions"""
        try:
            challenge_definitions = [
                {
                    "id": "daily_mood_check",
                    "name": "Daily Mood Check",
                    "description": "Log your mood once today",
                    "challenge_type": ChallengeType.DAILY,
                    "duration_days": 1,
                    "criteria": {"mood_logs": 1},
                    "points_reward": 5,
                    "difficulty": "easy",
                    "category": "mood"
                },
                {
                    "id": "gratitude_practice",
                    "name": "Gratitude Practice",
                    "description": "Share three things you're grateful for",
                    "challenge_type": ChallengeType.DAILY,
                    "duration_days": 1,
                    "criteria": {"gratitude_entries": 3},
                    "points_reward": 10,
                    "difficulty": "easy",
                    "category": "mindfulness"
                },
                {
                    "id": "breathing_exercise",
                    "name": "Breathing Exercise",
                    "description": "Complete a 5-minute breathing exercise",
                    "challenge_type": ChallengeType.DAILY,
                    "duration_days": 1,
                    "criteria": {"breathing_exercise_completed": 1},
                    "points_reward": 8,
                    "difficulty": "easy",
                    "category": "coping"
                },
                {
                    "id": "positive_affirmation",
                    "name": "Positive Affirmation",
                    "description": "Practice positive self-talk for 2 minutes",
                    "challenge_type": ChallengeType.DAILY,
                    "duration_days": 1,
                    "criteria": {"affirmation_practice": 1},
                    "points_reward": 6,
                    "difficulty": "easy",
                    "category": "mindfulness"
                },
                {
                    "id": "social_connection",
                    "name": "Social Connection",
                    "description": "Reach out to someone you care about",
                    "challenge_type": ChallengeType.DAILY,
                    "duration_days": 1,
                    "criteria": {"social_interaction": 1},
                    "points_reward": 12,
                    "difficulty": "medium",
                    "category": "social"
                },
                {
                    "id": "week_consistency",
                    "name": "Week of Consistency",
                    "description": "Check in with ChillBuddy every day for a week",
                    "challenge_type": ChallengeType.WEEKLY,
                    "duration_days": 7,
                    "criteria": {"daily_checkins": 7},
                    "points_reward": 50,
                    "difficulty": "medium",
                    "category": "engagement"
                },
                {
                    "id": "coping_mastery",
                    "name": "Coping Strategy Mastery",
                    "description": "Try 3 different coping strategies this week",
                    "challenge_type": ChallengeType.WEEKLY,
                    "duration_days": 7,
                    "criteria": {"unique_coping_strategies": 3},
                    "points_reward": 40,
                    "difficulty": "medium",
                    "category": "coping"
                }
            ]
            
            for challenge_data in challenge_definitions:
                challenge = Challenge(
                    id=challenge_data["id"],
                    name=challenge_data["name"],
                    description=challenge_data["description"],
                    challenge_type=challenge_data["challenge_type"],
                    duration_days=challenge_data["duration_days"],
                    criteria=challenge_data["criteria"],
                    points_reward=challenge_data["points_reward"],
                    difficulty=challenge_data["difficulty"],
                    category=challenge_data["category"]
                )
                self.challenges[challenge.id] = challenge
            
            self.logger.info(f"Loaded {len(self.challenges)} challenges")
            
        except Exception as e:
            self.logger.error(f"Error loading challenges: {e}")
    
    def track_activity(self, user_id: str, activity_type: ActivityType, activity_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Track user activity and update progress"""
        try:
            if user_id not in self.user_progress:
                self.user_progress[user_id] = UserProgress(user_id=user_id)
            
            progress = self.user_progress[user_id]
            progress.last_activity = datetime.now()
            progress.updated_at = datetime.now()
            
            # Update activity counters
            if activity_type == ActivityType.CONVERSATION:
                progress.conversations_count += 1
                self._update_daily_streak(user_id)
            elif activity_type == ActivityType.MOOD_LOG:
                progress.mood_logs_count += 1
                self._update_mood_streak(user_id)
            elif activity_type == ActivityType.COPING_STRATEGY:
                progress.coping_strategies_used += 1
            elif activity_type == ActivityType.RESOURCE_ACCESS:
                progress.resources_accessed += 1
            elif activity_type == ActivityType.DAILY_CHECKIN:
                self._update_daily_streak(user_id)
            
            # Award points based on activity
            points_earned = self._calculate_activity_points(activity_type, activity_data)
            progress.total_points += points_earned
            
            # Update level based on points
            new_level = self._calculate_level(progress.total_points)
            level_up = new_level > progress.level
            progress.level = new_level
            
            # Check for new achievements
            new_achievements = self._check_achievements(user_id)
            
            # Update active challenges
            challenge_updates = self._update_challenges(user_id, activity_type, activity_data)
            
            result = {
                "points_earned": points_earned,
                "total_points": progress.total_points,
                "level": progress.level,
                "level_up": level_up,
                "new_achievements": new_achievements,
                "challenge_updates": challenge_updates,
                "current_streaks": progress.current_streaks.copy()
            }
            
            self.logger.info(f"Tracked activity for user {user_id}: {activity_type.value}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error tracking activity: {e}")
            return {}
    
    def _calculate_activity_points(self, activity_type: ActivityType, activity_data: Dict[str, Any] = None) -> int:
        """Calculate points for different activities"""
        point_values = {
            ActivityType.CONVERSATION: 2,
            ActivityType.MOOD_LOG: 3,
            ActivityType.COPING_STRATEGY: 5,
            ActivityType.RESOURCE_ACCESS: 1,
            ActivityType.CHALLENGE_COMPLETE: 10,
            ActivityType.DAILY_CHECKIN: 2,
            ActivityType.CRISIS_SUPPORT: 20
        }
        
        base_points = point_values.get(activity_type, 1)
        
        # Bonus points for certain conditions
        if activity_data:
            if activity_data.get("first_time", False):
                base_points *= 2
            if activity_data.get("streak_bonus", False):
                base_points += 1
        
        return base_points
    
    def _calculate_level(self, total_points: int) -> int:
        """Calculate user level based on total points"""
        # Level progression: 100 points for level 2, then +50 points per level
        if total_points < 100:
            return 1
        return min(50, 2 + (total_points - 100) // 50)  # Cap at level 50
    
    def _update_daily_streak(self, user_id: str):
        """Update daily conversation streak"""
        try:
            progress = self.user_progress[user_id]
            today = datetime.now().date()
            
            if progress.last_activity:
                last_date = progress.last_activity.date()
                if last_date == today:
                    return  # Already counted today
                elif last_date == today - timedelta(days=1):
                    progress.current_streaks["daily"] += 1
                else:
                    progress.current_streaks["daily"] = 1
            else:
                progress.current_streaks["daily"] = 1
            
            # Update longest streak
            if progress.current_streaks["daily"] > progress.longest_streaks["daily"]:
                progress.longest_streaks["daily"] = progress.current_streaks["daily"]
            
        except Exception as e:
            self.logger.error(f"Error updating daily streak: {e}")
    
    def _update_mood_streak(self, user_id: str):
        """Update mood logging streak"""
        try:
            progress = self.user_progress[user_id]
            progress.current_streaks["mood"] += 1
            
            if progress.current_streaks["mood"] > progress.longest_streaks["mood"]:
                progress.longest_streaks["mood"] = progress.current_streaks["mood"]
            
        except Exception as e:
            self.logger.error(f"Error updating mood streak: {e}")
    
    def _check_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Check and unlock new achievements"""
        try:
            if user_id not in self.user_achievements:
                self.user_achievements[user_id] = []
            
            progress = self.user_progress[user_id]
            unlocked_achievement_ids = {ua.achievement_id for ua in self.user_achievements[user_id]}
            new_achievements = []
            
            for achievement in self.achievements.values():
                if achievement.id in unlocked_achievement_ids:
                    continue
                
                if self._meets_achievement_criteria(progress, achievement):
                    user_achievement = UserAchievement(
                        achievement_id=achievement.id,
                        user_id=user_id,
                        unlocked_at=datetime.now()
                    )
                    self.user_achievements[user_id].append(user_achievement)
                    
                    # Award achievement points
                    progress.total_points += achievement.points
                    
                    new_achievement_data = {
                        "id": achievement.id,
                        "name": achievement.name,
                        "description": achievement.description,
                        "points": achievement.points,
                        "badge_icon": achievement.badge_icon,
                        "unlocked_message": achievement.unlocked_message
                    }
                    new_achievements.append(new_achievement_data)
            
            return new_achievements
            
        except Exception as e:
            self.logger.error(f"Error checking achievements: {e}")
            return []
    
    def _meets_achievement_criteria(self, progress: UserProgress, achievement: Achievement) -> bool:
        """Check if user meets achievement criteria"""
        try:
            criteria = achievement.criteria
            
            for criterion, required_value in criteria.items():
                if criterion == "conversations":
                    if progress.conversations_count < required_value:
                        return False
                elif criterion == "daily_streak":
                    if progress.current_streaks["daily"] < required_value:
                        return False
                elif criterion == "mood_streak":
                    if progress.current_streaks["mood"] < required_value:
                        return False
                elif criterion == "unique_coping_strategies":
                    if progress.coping_strategies_used < required_value:
                        return False
                elif criterion == "resources_accessed":
                    if progress.resources_accessed < required_value:
                        return False
                elif criterion == "challenges_completed":
                    completed_challenges = len([uc for uc in self.user_challenges.get(progress.user_id, []) if uc.completed_at])
                    if completed_challenges < required_value:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking achievement criteria: {e}")
            return False
    
    def _update_challenges(self, user_id: str, activity_type: ActivityType, activity_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Update progress on active challenges"""
        try:
            if user_id not in self.user_challenges:
                self.user_challenges[user_id] = []
            
            challenge_updates = []
            
            for user_challenge in self.user_challenges[user_id]:
                if not user_challenge.is_active or user_challenge.completed_at:
                    continue
                
                challenge = self.challenges.get(user_challenge.challenge_id)
                if not challenge:
                    continue
                
                # Check if activity contributes to challenge
                progress_made = self._update_challenge_progress(user_challenge, challenge, activity_type, activity_data)
                
                if progress_made:
                    # Check if challenge is completed
                    if self._is_challenge_completed(user_challenge, challenge):
                        user_challenge.completed_at = datetime.now()
                        user_challenge.is_active = False
                        
                        # Award challenge points
                        self.user_progress[user_id].total_points += challenge.points_reward
                        
                        challenge_updates.append({
                            "challenge_id": challenge.id,
                            "name": challenge.name,
                            "completed": True,
                            "points_earned": challenge.points_reward
                        })
                    else:
                        challenge_updates.append({
                            "challenge_id": challenge.id,
                            "name": challenge.name,
                            "completed": False,
                            "progress": user_challenge.progress
                        })
            
            return challenge_updates
            
        except Exception as e:
            self.logger.error(f"Error updating challenges: {e}")
            return []
    
    def _update_challenge_progress(self, user_challenge: UserChallenge, challenge: Challenge, activity_type: ActivityType, activity_data: Dict[str, Any] = None) -> bool:
        """Update progress on a specific challenge"""
        try:
            if user_challenge.progress is None:
                user_challenge.progress = {}
            
            progress_made = False
            
            # Map activity types to challenge criteria
            if activity_type == ActivityType.MOOD_LOG and "mood_logs" in challenge.criteria:
                user_challenge.progress["mood_logs"] = user_challenge.progress.get("mood_logs", 0) + 1
                progress_made = True
            elif activity_type == ActivityType.DAILY_CHECKIN and "daily_checkins" in challenge.criteria:
                user_challenge.progress["daily_checkins"] = user_challenge.progress.get("daily_checkins", 0) + 1
                progress_made = True
            elif activity_type == ActivityType.COPING_STRATEGY and "unique_coping_strategies" in challenge.criteria:
                strategies = user_challenge.progress.get("coping_strategies", set())
                if activity_data and "strategy_type" in activity_data:
                    strategies.add(activity_data["strategy_type"])
                    user_challenge.progress["coping_strategies"] = strategies
                    user_challenge.progress["unique_coping_strategies"] = len(strategies)
                    progress_made = True
            
            return progress_made
            
        except Exception as e:
            self.logger.error(f"Error updating challenge progress: {e}")
            return False
    
    def _is_challenge_completed(self, user_challenge: UserChallenge, challenge: Challenge) -> bool:
        """Check if challenge is completed"""
        try:
            if not user_challenge.progress:
                return False
            
            for criterion, required_value in challenge.criteria.items():
                current_value = user_challenge.progress.get(criterion, 0)
                if isinstance(current_value, set):
                    current_value = len(current_value)
                
                if current_value < required_value:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking challenge completion: {e}")
            return False
    
    def assign_daily_challenges(self, user_id: str, num_challenges: int = 3) -> List[Dict[str, Any]]:
        """Assign daily challenges to user"""
        try:
            if user_id not in self.user_challenges:
                self.user_challenges[user_id] = []
            
            # Get daily challenges
            daily_challenges = [c for c in self.challenges.values() if c.challenge_type == ChallengeType.DAILY]
            
            # Remove already active challenges
            active_challenge_ids = {uc.challenge_id for uc in self.user_challenges[user_id] if uc.is_active}
            available_challenges = [c for c in daily_challenges if c.id not in active_challenge_ids]
            
            # Randomly select challenges
            selected_challenges = random.sample(available_challenges, min(num_challenges, len(available_challenges)))
            
            assigned_challenges = []
            for challenge in selected_challenges:
                user_challenge = UserChallenge(
                    challenge_id=challenge.id,
                    user_id=user_id,
                    started_at=datetime.now()
                )
                self.user_challenges[user_id].append(user_challenge)
                
                assigned_challenges.append({
                    "id": challenge.id,
                    "name": challenge.name,
                    "description": challenge.description,
                    "points_reward": challenge.points_reward,
                    "difficulty": challenge.difficulty,
                    "category": challenge.category
                })
            
            self.logger.info(f"Assigned {len(assigned_challenges)} daily challenges to user {user_id}")
            return assigned_challenges
            
        except Exception as e:
            self.logger.error(f"Error assigning daily challenges: {e}")
            return []
    
    def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user progress data"""
        try:
            if user_id not in self.user_progress:
                return {}
            
            progress = self.user_progress[user_id]
            achievements = self.user_achievements.get(user_id, [])
            active_challenges = [uc for uc in self.user_challenges.get(user_id, []) if uc.is_active]
            
            return {
                "user_id": user_id,
                "level": progress.level,
                "total_points": progress.total_points,
                "points_to_next_level": self._points_to_next_level(progress.total_points),
                "current_streaks": progress.current_streaks,
                "longest_streaks": progress.longest_streaks,
                "activity_counts": {
                    "conversations": progress.conversations_count,
                    "mood_logs": progress.mood_logs_count,
                    "coping_strategies": progress.coping_strategies_used,
                    "resources_accessed": progress.resources_accessed
                },
                "achievements_count": len(achievements),
                "active_challenges_count": len(active_challenges),
                "last_activity": progress.last_activity.isoformat() if progress.last_activity else None
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user progress: {e}")
            return {}
    
    def _points_to_next_level(self, current_points: int) -> int:
        """Calculate points needed for next level"""
        current_level = self._calculate_level(current_points)
        if current_level == 1:
            return 100 - current_points
        else:
            next_level_points = 100 + (current_level - 1) * 50
            return next_level_points - current_points
    
    def get_user_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's unlocked achievements"""
        try:
            user_achievements = self.user_achievements.get(user_id, [])
            result = []
            
            for user_achievement in user_achievements:
                achievement = self.achievements.get(user_achievement.achievement_id)
                if achievement:
                    result.append({
                        "id": achievement.id,
                        "name": achievement.name,
                        "description": achievement.description,
                        "badge_icon": achievement.badge_icon,
                        "points": achievement.points,
                        "unlocked_at": user_achievement.unlocked_at.isoformat()
                    })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting user achievements: {e}")
            return []
    
    def get_available_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get achievements user can still unlock"""
        try:
            unlocked_ids = {ua.achievement_id for ua in self.user_achievements.get(user_id, [])}
            available = []
            
            for achievement in self.achievements.values():
                if achievement.id not in unlocked_ids and not achievement.is_hidden:
                    available.append({
                        "id": achievement.id,
                        "name": achievement.name,
                        "description": achievement.description,
                        "badge_icon": achievement.badge_icon,
                        "points": achievement.points,
                        "criteria": achievement.criteria
                    })
            
            return available
            
        except Exception as e:
            self.logger.error(f"Error getting available achievements: {e}")
            return []
    
    def generate_motivational_message(self, user_id: str) -> str:
        """Generate personalized motivational message"""
        try:
            if user_id not in self.user_progress:
                return "Welcome to ChillBuddy! Every step you take towards better mental health matters."
            
            progress = self.user_progress[user_id]
            messages = []
            
            # Streak-based messages
            if progress.current_streaks["daily"] >= 7:
                messages.append(f"Amazing! You've maintained a {progress.current_streaks['daily']}-day streak. Your consistency is inspiring!")
            elif progress.current_streaks["daily"] >= 3:
                messages.append(f"Great job on your {progress.current_streaks['daily']}-day streak! Keep building this healthy habit.")
            
            # Level-based messages
            if progress.level >= 10:
                messages.append(f"Wow! You've reached level {progress.level}. Your dedication to mental health is remarkable.")
            elif progress.level >= 5:
                messages.append(f"Level {progress.level} achieved! You're making excellent progress on your mental health journey.")
            
            # Activity-based messages
            if progress.conversations_count >= 50:
                messages.append("You've had so many meaningful conversations with ChillBuddy. Your commitment to self-care shines through.")
            elif progress.mood_logs_count >= 20:
                messages.append("Your consistent mood tracking shows great self-awareness. This insight will help you grow.")
            
            # Default encouraging messages
            default_messages = [
                "Every conversation is a step forward in your mental health journey.",
                "You're building valuable skills for managing life's challenges.",
                "Your willingness to engage with mental health support shows real strength.",
                "Remember, progress isn't always linear, but you're moving in the right direction.",
                "Taking care of your mental health is one of the best investments you can make."
            ]
            
            if not messages:
                messages = default_messages
            
            return random.choice(messages)
            
        except Exception as e:
            self.logger.error(f"Error generating motivational message: {e}")
            return "Keep going! Every step matters in your mental health journey."
    
    def get_gamification_stats(self) -> Dict[str, Any]:
        """Get overall gamification system statistics"""
        try:
            total_users = len(self.user_progress)
            total_achievements_unlocked = sum(len(achievements) for achievements in self.user_achievements.values())
            total_challenges_completed = sum(
                len([uc for uc in challenges if uc.completed_at])
                for challenges in self.user_challenges.values()
            )
            
            return {
                "total_users": total_users,
                "total_achievements": len(self.achievements),
                "total_challenges": len(self.challenges),
                "achievements_unlocked": total_achievements_unlocked,
                "challenges_completed": total_challenges_completed,
                "average_level": sum(p.level for p in self.user_progress.values()) / total_users if total_users > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting gamification stats: {e}")
            return {}