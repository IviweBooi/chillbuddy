// Reward Preview System
// Shows users what they can earn from completing activities in each feature

class RewardPreview {
    constructor() {
        this.rewards = {
            journal: {
                points: 3,
                badges: [
                    { name: "First Steps", icon: "🌟", description: "Complete your first journal entry", progress: "0/1" },
                    { name: "Reflection Master", icon: "📝", description: "Write 10 journal entries", progress: "0/10" },
                    { name: "Daily Writer", icon: "✍️", description: "Journal for 7 consecutive days", progress: "0/7" }
                ],
                achievements: [
                    { name: "Self-Awareness", description: "Unlock deeper insights about yourself" },
                    { name: "Emotional Intelligence", description: "Better understand your feelings" }
                ]
            },
            mood: {
                points: 2,
                badges: [
                    { name: "Mood Tracker", icon: "😊", description: "Log your first mood", progress: "0/1" },
                    { name: "Mood Master", icon: "📊", description: "Track mood for 14 consecutive days", progress: "0/14" },
                    { name: "Emotional Awareness", icon: "🎭", description: "Log 50 different moods", progress: "0/50" }
                ],
                achievements: [
                    { name: "Pattern Recognition", description: "Identify your mood patterns" },
                    { name: "Emotional Balance", description: "Maintain consistent mood tracking" }
                ]
            },
            exercise: {
                points: 5,
                badges: [
                    { name: "Wellness Warrior", icon: "🧘", description: "Complete your first exercise", progress: "0/1" },
                    { name: "Coping Champion", icon: "🛡️", description: "Use 5 different coping strategies", progress: "0/5" },
                    { name: "Mindfulness Master", icon: "🕯️", description: "Complete 20 mindfulness exercises", progress: "0/20" }
                ],
                achievements: [
                    { name: "Stress Relief", description: "Learn effective stress management" },
                    { name: "Mental Resilience", description: "Build stronger coping skills" }
                ]
            },
            progress: {
                points: 1,
                badges: [
                    { name: "Progress Tracker", icon: "📈", description: "View your progress dashboard", progress: "0/1" },
                    { name: "Goal Setter", icon: "🎯", description: "Set 3 personal goals", progress: "0/3" },
                    { name: "Achievement Hunter", icon: "🏆", description: "Earn 10 badges", progress: "0/10" }
                ],
                achievements: [
                    { name: "Self-Improvement", description: "Track your mental health journey" },
                    { name: "Goal Achievement", description: "Reach your wellness milestones" }
                ]
            },
            resources: {
                points: 1,
                badges: [
                    { name: "Resource Explorer", icon: "🔍", description: "Access 10 different resources", progress: "0/10" },
                    { name: "Knowledge Seeker", icon: "📚", description: "Read 5 articles", progress: "0/5" },
                    { name: "Help Finder", icon: "🆘", description: "Use crisis support resources", progress: "0/1" }
                ],
                achievements: [
                    { name: "Informed Wellness", description: "Access valuable mental health resources" },
                    { name: "Support Network", description: "Connect with help when needed" }
                ]
            }
        };
        
        this.init();
    }

    init() {
        this.createRewardPreviews();
        this.attachEventListeners();
        this.loadUserProgress();
        this.setupProgressTracking();
    }

    createRewardPreviews() {
        // Add reward previews to each feature section
        Object.keys(this.rewards).forEach(feature => {
            this.addRewardPreviewToFeature(feature);
        });
    }

    addRewardPreviewToFeature(feature) {
        const featureContainer = document.querySelector(`.${feature}-div`);
        if (!featureContainer) return;

        const featureBody = featureContainer.querySelector(`.${feature}-body`) || 
                           featureContainer.querySelector('.feature-body') ||
                           featureContainer;

        // Create reward preview element
        const rewardPreview = this.createRewardPreviewElement(feature);
        
        // Insert at the beginning of the feature body
        if (featureBody.firstChild) {
            featureBody.insertBefore(rewardPreview, featureBody.firstChild);
        } else {
            featureBody.appendChild(rewardPreview);
        }
    }

    createRewardPreviewElement(feature) {
        const reward = this.rewards[feature];
        const div = document.createElement('div');
        div.className = 'reward-preview';
        div.innerHTML = `
            <div class="reward-preview-header">
                <h3>🎁 What You'll Earn</h3>
                <button class="reward-toggle" data-feature="${feature}">
                    <span class="toggle-icon">▼</span>
                </button>
            </div>
            <div class="reward-preview-content" data-feature="${feature}">
                <div class="reward-points">
                    <div class="points-display">
                        <span class="points-value">+${reward.points}</span>
                        <span class="points-label">Points per activity</span>
                    </div>
                </div>
                
                <div class="reward-badges">
                    <h4>🏆 Badges to Unlock</h4>
                    <div class="badge-preview-grid">
                        ${reward.badges.map(badge => `
                            <div class="badge-preview-item">
                                <div class="badge-icon">${badge.icon}</div>
                                <div class="badge-info">
                                    <div class="badge-name">${badge.name}</div>
                                    <div class="badge-description">${badge.description}</div>
                                    <div class="badge-progress">${badge.progress}</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="reward-achievements">
                    <h4>🌟 Achievements to Unlock</h4>
                    <div class="achievement-preview-list">
                        ${reward.achievements.map(achievement => `
                            <div class="achievement-preview-item">
                                <div class="achievement-name">${achievement.name}</div>
                                <div class="achievement-description">${achievement.description}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="reward-cta">
                    <button class="btn-start-earning" data-feature="${feature}">
                        Start Earning Rewards! 🚀
                    </button>
                </div>
            </div>
        `;
        
        return div;
    }

    attachEventListeners() {
        // Toggle reward preview visibility
        document.addEventListener('click', (e) => {
            if (e.target.closest('.reward-toggle')) {
                const button = e.target.closest('.reward-toggle');
                const feature = button.dataset.feature;
                this.toggleRewardPreview(feature);
            }
            
            if (e.target.closest('.btn-start-earning')) {
                const button = e.target.closest('.btn-start-earning');
                const feature = button.dataset.feature;
                this.startEarningRewards(feature);
            }
        });
    }

    toggleRewardPreview(feature) {
        const content = document.querySelector(`.reward-preview-content[data-feature="${feature}"]`);
        const toggle = document.querySelector(`.reward-toggle[data-feature="${feature}"] .toggle-icon`);
        
        if (content.style.display === 'none' || !content.style.display) {
            content.style.display = 'block';
            toggle.textContent = '▲';
            
            // Animate in
            content.style.opacity = '0';
            content.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                content.style.transition = 'all 0.3s ease';
                content.style.opacity = '1';
                content.style.transform = 'translateY(0)';
            }, 10);
        } else {
            content.style.transition = 'all 0.3s ease';
            content.style.opacity = '0';
            content.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                content.style.display = 'none';
                toggle.textContent = '▼';
            }, 300);
        }
    }

    startEarningRewards(feature) {
        // Hide the reward preview and focus on the feature content
        const rewardPreview = document.querySelector(`.${feature}-div .reward-preview`);
        if (rewardPreview) {
            rewardPreview.style.transition = 'all 0.5s ease';
            rewardPreview.style.opacity = '0';
            rewardPreview.style.transform = 'translateY(-20px)';
            
            setTimeout(() => {
                rewardPreview.style.display = 'none';
            }, 500);
        }
        
        // Show encouraging message
        this.showEncouragementMessage(feature);
        
        // Focus on the main feature content
        this.focusOnFeatureContent(feature);
        
        // Trigger feature-specific actions
        this.triggerFeatureAction(feature);
    }

    showEncouragementMessage(feature) {
        const messages = {
            journal: "Great choice! Start writing your thoughts and feelings. Every entry brings you closer to your goals! ✨",
            mood: "Excellent! Begin tracking your mood. Understanding your emotions is the first step to wellness! 😊",
            exercise: "Perfect! Try a mindfulness exercise. Each practice strengthens your mental resilience! 🧘",
            progress: "Awesome! Check your progress and set new goals. Tracking your journey keeps you motivated! 📈",
            resources: "Smart move! Explore our resources. Knowledge is power on your wellness journey! 📚"
        };
        
        // Create and show temporary encouragement message
        const messageDiv = document.createElement('div');
        messageDiv.className = 'encouragement-message';
        messageDiv.innerHTML = `
            <div class="message-content">
                <span class="message-text">${messages[feature]}</span>
                <button class="message-close">×</button>
            </div>
        `;
        
        const featureContainer = document.querySelector(`.${feature}-div`);
        featureContainer.insertBefore(messageDiv, featureContainer.firstChild);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.style.transition = 'all 0.3s ease';
                messageDiv.style.opacity = '0';
                setTimeout(() => messageDiv.remove(), 300);
            }
        }, 5000);
        
        // Manual close
        messageDiv.querySelector('.message-close').addEventListener('click', () => {
            messageDiv.style.transition = 'all 0.3s ease';
            messageDiv.style.opacity = '0';
            setTimeout(() => messageDiv.remove(), 300);
        });
    }

    focusOnFeatureContent(feature) {
        // Highlight the main content area
        const featureBody = document.querySelector(`.${feature}-div .${feature}-body`) ||
                           document.querySelector(`.${feature}-div .feature-body`);
        
        if (featureBody) {
            featureBody.style.transition = 'all 0.3s ease';
            featureBody.style.transform = 'scale(1.02)';
            featureBody.style.boxShadow = '0 8px 32px rgba(59, 130, 246, 0.15)';
            
            setTimeout(() => {
                featureBody.style.transform = 'scale(1)';
                featureBody.style.boxShadow = '';
            }, 1000);
        }
    }

    updateProgress(feature, badgeId, current, total) {
        const badgeElements = document.querySelectorAll(
            `.reward-preview-content[data-feature="${feature}"] .badge-preview-item .badge-progress`
        );
        
        badgeElements.forEach(badgeElement => {
            const badgeItem = badgeElement.closest('.badge-preview-item');
            const badgeName = badgeItem.querySelector('.badge-name').textContent;
            
            // Update progress for matching badge
            if (this.shouldUpdateBadge(badgeName, badgeId)) {
                badgeElement.textContent = `${current}/${total}`;
                
                // Add progress animation if close to completion
                const progressRatio = current / total;
                if (progressRatio >= 0.8) {
                    badgeElement.style.color = 'var(--success-color)';
                    badgeElement.style.fontWeight = 'bold';
                    
                    // Add pulsing animation for near completion
                    badgeElement.style.animation = 'pulse 2s infinite';
                }
                
                // Mark as completed if reached target
                if (progressRatio >= 1) {
                    badgeItem.style.background = 'linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(59, 130, 246, 0.1))';
                    badgeItem.style.borderColor = 'var(--success-color)';
                    badgeElement.textContent = '✅ Completed!';
                    badgeElement.style.color = 'var(--success-color)';
                }
            }
        });
    }
    
    shouldUpdateBadge(badgeName, badgeId) {
        // Map badge IDs to badge names for updates
        const badgeMapping = {
            'first_conversation': 'First Steps',
            'week_warrior': 'Daily Writer',
            'mood_tracker': 'Mood Master',
            'coping_champion': 'Coping Champion',
            'resource_explorer': 'Resource Explorer',
            'challenge_crusher': 'Wellness Warrior',
            'first_journal': 'First Steps',
            'reflection_master': 'Reflection Master',
            'daily_writer': 'Daily Writer',
            'first_mood': 'Mood Tracker',
            'mood_master': 'Mood Master',
            'emotional_awareness': 'Emotional Awareness',
            'first_exercise': 'Wellness Warrior',
            'mindfulness_master': 'Mindfulness Master'
        };
        
        return badgeMapping[badgeId] === badgeName;
    }

    hideRewardPreview(feature) {
        const rewardPreview = document.querySelector(`.${feature}-div .reward-preview`);
        if (rewardPreview) {
            rewardPreview.style.display = 'none';
        }
    }

    showRewardPreview(feature) {
        const rewardPreview = document.querySelector(`.${feature}-div .reward-preview`);
        if (rewardPreview) {
            rewardPreview.style.display = 'block';
        }
    }
}

// Initialize when DOM is loaded

document.addEventListener('DOMContentLoaded', () => {
    rewardPreview = new RewardPreview();
});

    loadUserProgress() {
        // Load progress from localStorage and update displays
        const journalEntries = JSON.parse(localStorage.getItem('journalEntries') || '[]');
        const moodEntries = JSON.parse(localStorage.getItem('moodHistory') || '[]');
        const exerciseProgress = JSON.parse(localStorage.getItem('exerciseProgress') || '{}');
        
        // Update journal progress
        if (journalEntries.length > 0) {
            this.updateBadgeProgress('journal', 'First Steps', 1, 1);
            this.updateBadgeProgress('journal', 'Reflection Master', Math.min(journalEntries.length, 10), 10);
            
            // Check for consecutive days
            const consecutiveDays = this.calculateConsecutiveDays(journalEntries);
            this.updateBadgeProgress('journal', 'Daily Writer', Math.min(consecutiveDays, 7), 7);
        }
        
        // Update mood progress
        if (moodEntries.length > 0) {
            this.updateBadgeProgress('mood', 'Mood Tracker', 1, 1);
            
            const consecutiveMoodDays = this.calculateConsecutiveDays(moodEntries);
            this.updateBadgeProgress('mood', 'Mood Master', Math.min(consecutiveMoodDays, 14), 14);
            this.updateBadgeProgress('mood', 'Emotional Awareness', Math.min(moodEntries.length, 50), 50);
        }
        
        // Update exercise progress
        const completedExercises = exerciseProgress.completed || [];
        if (completedExercises.length > 0) {
            this.updateBadgeProgress('exercise', 'Wellness Warrior', 1, 1);
            
            const uniqueTypes = new Set(completedExercises.map(ex => ex.type)).size;
            this.updateBadgeProgress('exercise', 'Coping Champion', Math.min(uniqueTypes, 5), 5);
            
            const mindfulnessCount = completedExercises.filter(ex => ex.category === 'mindfulness').length;
            this.updateBadgeProgress('exercise', 'Mindfulness Master', Math.min(mindfulnessCount, 20), 20);
        }
    }
    
    calculateConsecutiveDays(entries) {
        if (entries.length === 0) return 0;
        
        const dates = entries.map(entry => {
            const date = new Date(entry.date || entry.timestamp);
            return date.toDateString();
        }).sort();
        
        const uniqueDates = [...new Set(dates)];
        let consecutive = 1;
        let maxConsecutive = 1;
        
        for (let i = 1; i < uniqueDates.length; i++) {
            const prevDate = new Date(uniqueDates[i - 1]);
            const currDate = new Date(uniqueDates[i]);
            const diffTime = currDate - prevDate;
            const diffDays = diffTime / (1000 * 60 * 60 * 24);
            
            if (diffDays === 1) {
                consecutive++;
                maxConsecutive = Math.max(maxConsecutive, consecutive);
            } else {
                consecutive = 1;
            }
        }
        
        return maxConsecutive;
    }
    
    updateBadgeProgress(feature, badgeName, current, total) {
        const badgeElements = document.querySelectorAll(
            `.reward-preview-content[data-feature="${feature}"] .badge-preview-item`
        );
        
        badgeElements.forEach(badgeItem => {
            const nameElement = badgeItem.querySelector('.badge-name');
            const progressElement = badgeItem.querySelector('.badge-progress');
            
            if (nameElement && nameElement.textContent === badgeName) {
                progressElement.textContent = `${current}/${total}`;
                
                // Add progress animation if close to completion
                const progressRatio = current / total;
                if (progressRatio >= 0.8) {
                    progressElement.style.color = '#4CAF50';
                    progressElement.style.fontWeight = 'bold';
                }
                
                // Mark as completed if reached target
                if (progressRatio >= 1) {
                    badgeItem.style.background = 'linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(33, 150, 243, 0.1))';
                    badgeItem.style.borderColor = '#4CAF50';
                    progressElement.textContent = '✅ Completed!';
                    progressElement.style.color = '#4CAF50';
                    
                    // Add celebration animation
                    badgeItem.style.animation = 'celebration 0.6s ease';
                }
            }
        });
    }
    
    setupProgressTracking() {
        // Listen for custom events from other systems
        document.addEventListener('journalEntryAdded', () => {
            this.loadUserProgress();
            this.showProgressNotification('journal', 'Great job! You\'ve added a new journal entry! 📝');
        });
        
        document.addEventListener('moodLogged', () => {
            this.loadUserProgress();
            this.showProgressNotification('mood', 'Mood logged successfully! Keep tracking your emotions! 😊');
        });
        
        document.addEventListener('exerciseCompleted', (e) => {
            this.loadUserProgress();
            this.showProgressNotification('exercise', `Exercise completed! You\'re building mental resilience! 🧘`);
        });
    }
    
    showProgressNotification(feature, message) {
        const notification = document.createElement('div');
        notification.className = 'progress-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">🎉</span>
                <span class="notification-message">${message}</span>
                <button class="notification-close">×</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-hide after 4 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.opacity = '0';
                setTimeout(() => notification.remove(), 300);
            }
        }, 4000);
        
        // Manual close
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        });
    }
    
    triggerFeatureAction(feature) {
        switch (feature) {
            case 'journal':
                // Trigger journal new entry if system exists
                if (window.journalSystem) {
                    window.journalSystem.startNewEntry();
                }
                break;
            case 'mood':
                // Focus on mood tracker if system exists
                if (window.moodTracker) {
                    const moodScale = document.querySelector('.mood-scale');
                    if (moodScale) {
                        moodScale.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }
                break;
            case 'exercise':
                // Open exercises modal if system exists
                if (window.exercisesSystem) {
                    const firstCategory = document.querySelector('.exercise-category');
                    if (firstCategory) {
                        firstCategory.click();
                    }
                }
                break;
            case 'progress':
                // Scroll to progress dashboard
                const progressDashboard = document.querySelector('.progress-dashboard');
                if (progressDashboard) {
                    progressDashboard.scrollIntoView({ behavior: 'smooth' });
                }
                break;
            case 'resources':
                // Scroll to resources section
                const resourcesSection = document.querySelector('.resources-div');
                if (resourcesSection) {
                    resourcesSection.scrollIntoView({ behavior: 'smooth' });
                }
                break;
        }
    }
}

// Initialize when DOM is loaded
let rewardPreview;
document.addEventListener('DOMContentLoaded', () => {
    rewardPreview = new RewardPreview();
});

// Make it globally accessible
window.rewardPreview = rewardPreview;