/**
 * Mood Tracker System
 * Handles mood logging, history tracking, and insights generation
 */

class MoodTracker {
    constructor() {
        this.currentMood = null;
        this.selectedFactors = [];
        this.moodHistory = this.loadMoodHistory();
        this.init();
    }

    init() {
        this.initializeMoodScale();
        this.initializeFactorTags();
        this.initializeLogButton();
        this.renderMoodHistory();
        this.generateInsights();
    }

    initializeMoodScale() {
        const moodItems = document.querySelectorAll('.mood-scale-item');
        moodItems.forEach(item => {
            item.addEventListener('click', () => {
                // Remove previous selection
                moodItems.forEach(i => i.classList.remove('selected'));
                
                // Add selection to clicked item
                item.classList.add('selected');
                this.currentMood = {
                    value: parseInt(item.dataset.value),
                    emoji: item.querySelector('.mood-emoji').textContent,
                    label: item.querySelector('span').textContent
                };
                
                // Add visual feedback
                item.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    item.style.transform = 'scale(1)';
                }, 200);
                
                this.updateLogButton();
            });
        });
    }

    initializeFactorTags() {
        const factorTags = document.querySelectorAll('.factor-tag');
        factorTags.forEach(tag => {
            tag.addEventListener('click', () => {
                tag.classList.toggle('selected');
                const factor = tag.dataset.factor;
                
                if (tag.classList.contains('selected')) {
                    if (!this.selectedFactors.includes(factor)) {
                        this.selectedFactors.push(factor);
                    }
                } else {
                    this.selectedFactors = this.selectedFactors.filter(f => f !== factor);
                }
                
                this.updateLogButton();
            });
        });
    }

    initializeLogButton() {
        const logButton = document.getElementById('logMoodBtn');
        if (logButton) {
            logButton.addEventListener('click', () => {
                this.logMood();
            });
        }
    }

    updateLogButton() {
        const logButton = document.getElementById('logMoodBtn');
        if (logButton) {
            if (this.currentMood) {
                logButton.disabled = false;
                logButton.textContent = `Log ${this.currentMood.label} Mood`;
                logButton.style.background = 'var(--primary-color)';
            } else {
                logButton.disabled = true;
                logButton.textContent = 'Select a mood first';
                logButton.style.background = 'var(--text-secondary)';
            }
        }
    }

    logMood() {
        if (!this.currentMood) {
            this.showNotification('Please select a mood first!', 'warning');
            return;
        }

        const moodEntry = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            mood: this.currentMood,
            factors: [...this.selectedFactors],
            date: new Date().toLocaleDateString()
        };

        // Add to history
        this.moodHistory.unshift(moodEntry);
        
        // Keep only last 30 entries
        if (this.moodHistory.length > 30) {
            this.moodHistory = this.moodHistory.slice(0, 30);
        }
        
        // Save to localStorage
        this.saveMoodHistory();
        
        // Update UI
        this.renderMoodHistory();
        this.generateInsights();
        this.resetForm();
        
        // Show success message
        this.showNotification(`Mood logged successfully! ${this.currentMood.emoji}`, 'success');
        
        // Update progress if reward preview exists
        if (window.rewardPreview) {
            window.rewardPreview.updateProgress('mood', 'mood_tracker', this.moodHistory.length, 14);
        }
        
        // Trigger achievement check
        this.checkAchievements(moodEntry);
    }

    resetForm() {
        // Clear mood selection
        document.querySelectorAll('.mood-scale-item').forEach(item => {
            item.classList.remove('selected');
        });
        
        // Clear factor selection
        document.querySelectorAll('.factor-tag').forEach(tag => {
            tag.classList.remove('selected');
        });
        
        this.currentMood = null;
        this.selectedFactors = [];
        this.updateLogButton();
    }

    renderMoodHistory() {
        const chartContainer = document.getElementById('moodChart');
        if (!chartContainer) return;

        if (this.moodHistory.length === 0) {
            chartContainer.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📊</div>
                    <p>No mood data yet</p>
                    <small>Start logging your moods to see patterns!</small>
                </div>
            `;
            return;
        }

        // Create simple chart visualization
        const recentEntries = this.moodHistory.slice(0, 7).reverse();
        const chartHTML = `
            <div class="mood-chart-container">
                <div class="chart-header">
                    <h4>Last 7 Days</h4>
                    <span class="average-mood">Avg: ${this.calculateAverageMood().toFixed(1)}/5</span>
                </div>
                <div class="mood-bars">
                    ${recentEntries.map((entry, index) => `
                        <div class="mood-bar-item">
                            <div class="mood-bar" style="height: ${(entry.mood.value / 5) * 100}%" title="${entry.mood.label}">
                                <span class="mood-emoji">${entry.mood.emoji}</span>
                            </div>
                            <span class="mood-date">${new Date(entry.timestamp).toLocaleDateString('en-US', { weekday: 'short' })}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="mood-legend">
                    <div class="legend-item"><span class="legend-color" style="background: #ef4444;"></span>1-2: Low</div>
                    <div class="legend-item"><span class="legend-color" style="background: #f59e0b;"></span>3: Neutral</div>
                    <div class="legend-item"><span class="legend-color" style="background: #10b981;"></span>4-5: High</div>
                </div>
            </div>
        `;
        
        chartContainer.innerHTML = chartHTML;
    }

    generateInsights() {
        const insightContainer = document.getElementById('insightCards');
        if (!insightContainer) return;

        if (this.moodHistory.length < 3) {
            insightContainer.innerHTML = `
                <div class="insight-card">
                    <div class="insight-icon">💡</div>
                    <div class="insight-content">
                        <h5>Getting Started</h5>
                        <p>Log a few more moods to unlock personalized insights!</p>
                    </div>
                </div>
            `;
            return;
        }

        const insights = this.analyzePatterns();
        const insightsHTML = insights.map(insight => `
            <div class="insight-card ${insight.type}">
                <div class="insight-icon">${insight.icon}</div>
                <div class="insight-content">
                    <h5>${insight.title}</h5>
                    <p>${insight.description}</p>
                    ${insight.suggestion ? `<small class="insight-suggestion">${insight.suggestion}</small>` : ''}
                </div>
            </div>
        `).join('');
        
        insightContainer.innerHTML = insightsHTML;
    }

    analyzePatterns() {
        const insights = [];
        const recentEntries = this.moodHistory.slice(0, 7);
        
        // Mood trend analysis
        if (recentEntries.length >= 3) {
            const recent = recentEntries.slice(0, 3).map(e => e.mood.value);
            const older = recentEntries.slice(3, 6).map(e => e.mood.value);
            
            const recentAvg = recent.reduce((a, b) => a + b, 0) / recent.length;
            const olderAvg = older.length > 0 ? older.reduce((a, b) => a + b, 0) / older.length : recentAvg;
            
            if (recentAvg > olderAvg + 0.5) {
                insights.push({
                    type: 'positive',
                    icon: '📈',
                    title: 'Improving Trend',
                    description: 'Your mood has been trending upward recently!',
                    suggestion: 'Keep doing what you\'re doing - you\'re on the right track.'
                });
            } else if (recentAvg < olderAvg - 0.5) {
                insights.push({
                    type: 'warning',
                    icon: '📉',
                    title: 'Declining Trend',
                    description: 'Your mood has been lower lately.',
                    suggestion: 'Consider talking to someone or trying some coping strategies.'
                });
            } else {
                insights.push({
                    type: 'neutral',
                    icon: '📊',
                    title: 'Stable Pattern',
                    description: 'Your mood has been relatively stable.',
                    suggestion: 'Consistency is good! Keep monitoring your patterns.'
                });
            }
        }
        
        // Factor analysis
        const factorCounts = {};
        this.moodHistory.forEach(entry => {
            entry.factors.forEach(factor => {
                factorCounts[factor] = (factorCounts[factor] || 0) + 1;
            });
        });
        
        const topFactor = Object.keys(factorCounts).reduce((a, b) => 
            factorCounts[a] > factorCounts[b] ? a : b, null
        );
        
        if (topFactor && factorCounts[topFactor] >= 3) {
            insights.push({
                type: 'info',
                icon: '🔍',
                title: 'Common Factor',
                description: `"${topFactor}" appears frequently in your mood logs.`,
                suggestion: 'Consider how this factor affects your wellbeing.'
            });
        }
        
        // Streak analysis
        const streak = this.calculateStreak();
        if (streak >= 3) {
            insights.push({
                type: 'positive',
                icon: '🔥',
                title: 'Great Streak!',
                description: `You've logged your mood ${streak} days in a row!`,
                suggestion: 'Consistency helps identify patterns. Keep it up!'
            });
        }
        
        return insights;
    }

    calculateAverageMood() {
        if (this.moodHistory.length === 0) return 0;
        const sum = this.moodHistory.reduce((total, entry) => total + entry.mood.value, 0);
        return sum / this.moodHistory.length;
    }

    calculateStreak() {
        if (this.moodHistory.length === 0) return 0;
        
        let streak = 0;
        const today = new Date().toDateString();
        let currentDate = new Date();
        
        for (const entry of this.moodHistory) {
            const entryDate = new Date(entry.timestamp).toDateString();
            const expectedDate = currentDate.toDateString();
            
            if (entryDate === expectedDate) {
                streak++;
                currentDate.setDate(currentDate.getDate() - 1);
            } else {
                break;
            }
        }
        
        return streak;
    }

    checkAchievements(entry) {
        const achievements = [];
        
        // First mood log
        if (this.moodHistory.length === 1) {
            achievements.push({
                id: 'first_mood',
                name: 'Mood Tracker',
                description: 'Logged your first mood!',
                icon: '😊',
                points: 10
            });
        }
        
        // Streak achievements
        const streak = this.calculateStreak();
        if (streak === 7) {
            achievements.push({
                id: 'mood_week',
                name: 'Week Warrior',
                description: '7-day mood tracking streak!',
                icon: '🔥',
                points: 25
            });
        }
        
        // Show achievements
        achievements.forEach(achievement => {
            if (window.achievementNotifications) {
                window.achievementNotifications.showNotification(achievement, 'achievement');
            }
        });
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `mood-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${type === 'success' ? '✅' : type === 'warning' ? '⚠️' : 'ℹ️'}</span>
                <span class="notification-message">${message}</span>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    loadMoodHistory() {
        try {
            const saved = localStorage.getItem('chillbuddy_mood_history');
            return saved ? JSON.parse(saved) : [];
        } catch (error) {
            console.error('Error loading mood history:', error);
            return [];
        }
    }

    saveMoodHistory() {
        try {
            localStorage.setItem('chillbuddy_mood_history', JSON.stringify(this.moodHistory));
        } catch (error) {
            console.error('Error saving mood history:', error);
        }
    }

    // Public methods for external access
    getMoodHistory() {
        return this.moodHistory;
    }

    getAverageMood() {
        return this.calculateAverageMood();
    }

    getCurrentStreak() {
        return this.calculateStreak();
    }
}

// Initialize mood tracker when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.mood-tracker-div')) {
        window.moodTracker = new MoodTracker();
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MoodTracker;
}