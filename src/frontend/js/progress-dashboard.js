// Progress Tracking Dashboard
class ProgressTrackingDashboard {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            showDetailedMetrics: true,
            showPredictions: true,
            showRecommendations: true,
            animateProgress: true,
            updateInterval: 30000, // 30 seconds
            ...options
        };
        
        this.progressData = [];
        this.userStats = {};
        this.updateTimer = null;
        
        this.init();
    }

    init() {
        if (!this.container) {
            console.error('Progress dashboard container not found');
            return;
        }
        
        this.loadSettings();
        this.setupEventListeners();
        this.loadProgressData();
    }

    loadSettings() {
        const savedSettings = localStorage.getItem('progressDashboardSettings');
        if (savedSettings) {
            try {
                const settings = JSON.parse(savedSettings);
                this.options = { ...this.options, ...settings };
            } catch (error) {
                console.warn('Failed to load dashboard settings:', error);
            }
        }
    }

    setupEventListeners() {
        // Listen for hash changes to update progress when navigating
        window.addEventListener('hashchange', () => {
            this.handleNavigation();
        });
        
        // Listen for custom progress events
        document.addEventListener('progressUpdate', (event) => {
            if (event.detail && event.detail.badgeId) {
                this.updateProgress(event.detail.badgeId, event.detail.progress);
            }
        });
        
        // Listen for feature activity events
        document.addEventListener('featureActivity', (event) => {
            if (event.detail) {
                this.handleFeatureActivity(event.detail);
            }
        });
    }

    handleNavigation() {
        const hash = window.location.hash.substring(1);
        
        // Update relevant progress based on navigation
        switch (hash) {
            case 'mood-tracker':
                this.simulateActivity('monthly-milestone', 'mood-log', 0);
                break;
            case 'journal':
                this.simulateActivity('monthly-milestone', 'journal-entry', 0);
                break;
            case 'exercises':
                this.simulateActivity('monthly-milestone', 'exercise', 0);
                break;
            case 'resources':
                this.simulateActivity('resource-explorer', 'resource-view', 0);
                break;
        }
    }

    handleFeatureActivity(activity) {
        // Map feature activities to badge progress
        const activityMap = {
            'mood-logged': { badgeId: 'monthly-milestone', amount: 1 },
            'journal-entry': { badgeId: 'monthly-milestone', amount: 1 },
            'exercise-completed': { badgeId: 'challenge-crusher', amount: 1 },
            'resource-explored': { badgeId: 'resource-explorer', amount: 1 }
        };
        
        const mapping = activityMap[activity.type];
        if (mapping) {
            this.simulateActivity(mapping.badgeId, activity.type, mapping.amount);
        }
    }

    async loadProgressData() {
        try {
            // Try to fetch from API first
            const [progressResponse, statsResponse] = await Promise.all([
                fetch('/api/user/progress'),
                fetch('/api/user/stats')
            ]);
            
            if (progressResponse.ok && statsResponse.ok) {
                this.progressData = await progressResponse.json();
                this.userStats = await statsResponse.json();
            } else {
                throw new Error('API not available');
            }
        } catch (error) {
            console.log('Using mock progress data:', error.message);
            this.loadMockData();
        }
    }

    loadMockData() {
        this.userStats = {
            totalSessions: 45,
            streakDays: 12,
            moodEntries: 28,
            copingStrategiesLearned: 8,
            resourcesExplored: 18,
            challengesCompleted: 2,
            activeDays: 22,
            averageMoodScore: 7.2,
            improvementRate: 15.3,
            lastActivity: '2024-01-15T10:30:00Z'
        };
        
        this.progressData = [
            {
                badgeId: 'resource-explorer',
                badgeName: 'Resource Explorer',
                category: 'learning',
                difficulty: 'medium',
                current: 18,
                target: 25,
                unit: 'resources',
                description: 'Explore mental health resources',
                estimatedCompletion: '3 days',
                dailyRate: 2.3,
                weeklyGoal: 16,
                tips: [
                    'Try exploring different categories of resources',
                    'Bookmark useful resources for later reference',
                    'Share interesting resources with friends'
                ],
                milestones: [
                    { value: 5, label: 'Getting Started', completed: true },
                    { value: 10, label: 'Explorer', completed: true },
                    { value: 15, label: 'Researcher', completed: true },
                    { value: 20, label: 'Scholar', completed: false },
                    { value: 25, label: 'Expert', completed: false }
                ],
                recentActivity: [
                    { date: '2024-01-15', count: 3, type: 'articles' },
                    { date: '2024-01-14', count: 2, type: 'videos' },
                    { date: '2024-01-13', count: 1, type: 'podcast' }
                ]
            },
            {
                badgeId: 'challenge-crusher',
                badgeName: 'Challenge Crusher',
                category: 'achievement',
                difficulty: 'hard',
                current: 2,
                target: 5,
                unit: 'challenges',
                description: 'Complete mental health challenges',
                estimatedCompletion: '2 weeks',
                dailyRate: 0.2,
                weeklyGoal: 1,
                tips: [
                    'Start with easier challenges to build confidence',
                    'Set aside dedicated time for challenge completion',
                    'Track your progress and celebrate small wins'
                ],
                milestones: [
                    { value: 1, label: 'First Challenge', completed: true },
                    { value: 2, label: 'Getting Momentum', completed: true },
                    { value: 3, label: 'Challenge Seeker', completed: false },
                    { value: 4, label: 'Almost There', completed: false },
                    { value: 5, label: 'Challenge Master', completed: false }
                ],
                recentActivity: [
                    { date: '2024-01-10', count: 1, type: 'mindfulness-challenge' },
                    { date: '2024-01-05', count: 1, type: 'gratitude-challenge' }
                ]
            },
            {
                badgeId: 'monthly-milestone',
                badgeName: 'Monthly Milestone',
                category: 'consistency',
                difficulty: 'hard',
                current: 22,
                target: 30,
                unit: 'days',
                description: 'Stay active for 30 consecutive days',
                estimatedCompletion: '8 days',
                dailyRate: 1.0,
                weeklyGoal: 7,
                tips: [
                    'Set daily reminders to check in',
                    'Even small activities count towards your streak',
                    'Focus on consistency over intensity'
                ],
                milestones: [
                    { value: 7, label: 'First Week', completed: true },
                    { value: 14, label: 'Two Weeks Strong', completed: true },
                    { value: 21, label: 'Three Week Warrior', completed: true },
                    { value: 28, label: 'Almost There', completed: false },
                    { value: 30, label: 'Monthly Master', completed: false }
                ],
                recentActivity: [
                    { date: '2024-01-15', count: 1, type: 'check-in' },
                    { date: '2024-01-14', count: 1, type: 'mood-log' },
                    { date: '2024-01-13', count: 1, type: 'chat-session' }
                ]
            },
            {
                badgeId: 'crisis-survivor',
                badgeName: 'Crisis Survivor',
                category: 'resilience',
                difficulty: 'expert',
                current: 0,
                target: 1,
                unit: 'crisis events',
                description: 'Successfully navigate a mental health crisis',
                estimatedCompletion: 'When needed',
                dailyRate: 0,
                weeklyGoal: 0,
                tips: [
                    'Familiarize yourself with crisis resources',
                    'Practice coping strategies regularly',
                    'Build a support network before you need it',
                    'Remember that seeking help is a sign of strength'
                ],
                milestones: [
                    { value: 1, label: 'Crisis Navigator', completed: false }
                ],
                recentActivity: [],
                isSpecial: true
            }
        ];
    }

    render() {
        if (!this.container) return;
        
        // Find the existing modal content and add progress section
        const modalContent = document.querySelector('.modal-content');
        if (!modalContent) {
            // Fallback to original rendering if no modal
            this.container.innerHTML = `
                <div class="progress-dashboard">
                    ${this.renderDashboardHeader()}
                    ${this.renderOverallStats()}
                    ${this.renderProgressItems()}
                    ${this.options.showRecommendations ? this.renderRecommendations() : ''}
                </div>
            `;
        } else {
            // Check if progress section already exists
            let progressSection = modalContent.querySelector('.progress-section');
            if (!progressSection) {
                progressSection = document.createElement('div');
                progressSection.className = 'progress-section';
                progressSection.innerHTML = `
                    <h3 style="margin: 24px 0 16px 0; color: var(--text-primary); display: flex; align-items: center; gap: 8px;">
                        <span>📊</span> Progress Dashboard
                    </h3>
                    <div class="progress-items" style="display: flex; flex-direction: column; gap: 16px;"></div>
                `;
                modalContent.appendChild(progressSection);
            }
            
            // Update the progress items within the modal
            const progressItemsContainer = progressSection.querySelector('.progress-items');
            if (progressItemsContainer) {
                progressItemsContainer.innerHTML = this.renderProgressItems();
            }
        }
        
        this.attachEventListeners();
        
        if (this.options.animateProgress) {
            this.animateProgressBars();
        }
    }

    renderDashboardHeader() {
        return `
            <div class="dashboard-header">
                <h2>Progress Dashboard</h2>
                <p>Track your journey towards earning badges and achieving your mental health goals.</p>
                <div class="dashboard-controls">
                    <button class="btn-refresh" onclick="progressDashboard.refresh()">
                        <span class="icon">🔄</span> Refresh
                    </button>
                    <button class="btn-settings" onclick="progressDashboard.showSettings()">
                        <span class="icon">⚙️</span> Settings
                    </button>
                </div>
            </div>
        `;
    }

    renderOverallStats() {
        const completionRate = this.calculateOverallCompletion();
        const activeGoals = this.progressData.filter(item => item.current < item.target).length;
        const nearCompletion = this.progressData.filter(item => {
            const progress = (item.current / item.target) * 100;
            return progress >= 80 && progress < 100;
        }).length;
        
        return `
            <div class="overall-stats">
                <div class="stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-content">
                        <div class="stat-value">${completionRate}%</div>
                        <div class="stat-label">Overall Progress</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">🎯</div>
                    <div class="stat-content">
                        <div class="stat-value">${activeGoals}</div>
                        <div class="stat-label">Active Goals</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">⚡</div>
                    <div class="stat-content">
                        <div class="stat-value">${nearCompletion}</div>
                        <div class="stat-label">Near Completion</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">🔥</div>
                    <div class="stat-content">
                        <div class="stat-value">${this.userStats.streakDays}</div>
                        <div class="stat-label">Day Streak</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderProgressItems() {
        return `
            <div class="progress-items">
                ${this.progressData.map(item => this.renderProgressItem(item)).join('')}
            </div>
        `;
    }

    renderProgressItem(item) {
        const progressPercentage = Math.min((item.current / item.target) * 100, 100);
        const isCompleted = item.current >= item.target;
        const isNearCompletion = progressPercentage >= 80;
        
        return `
            <div class="progress-item ${isCompleted ? 'completed' : ''} ${item.isSpecial ? 'special' : ''}" data-badge-id="${item.badgeId}">
                <div class="progress-header">
                    <div class="badge-info">
                        <h3 class="badge-name">${item.badgeName}</h3>
                        <div class="badge-meta">
                            <span class="badge-category">${this.capitalizeFirst(item.category)}</span>
                            <span class="badge-difficulty ${item.difficulty}">${this.capitalizeFirst(item.difficulty)}</span>
                        </div>
                    </div>
                    <div class="progress-summary">
                        <div class="progress-percentage ${isNearCompletion ? 'near-completion' : ''}">
                            ${Math.round(progressPercentage)}%
                        </div>
                        <div class="progress-fraction">
                            ${item.current}/${item.target} ${item.unit}
                        </div>
                    </div>
                </div>
                
                <div class="progress-bar-container">
                    <div class="progress-bar">
                        <div class="progress-fill" data-progress="${progressPercentage}" style="width: 0%;"></div>
                        ${this.renderMilestoneMarkers(item.milestones, item.target)}
                    </div>
                </div>
                
                <div class="progress-details">
                    <p class="progress-description">${item.description}</p>
                    
                    ${this.options.showDetailedMetrics ? this.renderDetailedMetrics(item) : ''}
                    
                    ${this.options.showPredictions && !isCompleted ? this.renderPredictions(item) : ''}
                    
                    ${this.renderMilestones(item.milestones)}
                    
                    ${this.renderRecentActivity(item.recentActivity)}
                    
                    ${this.renderTips(item.tips)}
                </div>
                
                <div class="progress-actions">
                    <button class="btn-track" onclick="progressDashboard.trackProgress('${item.badgeId}')">
                        ${isCompleted ? 'View Badge' : 'Track Progress'}
                    </button>
                    <button class="btn-details" onclick="progressDashboard.showDetails('${item.badgeId}')">
                        Details
                    </button>
                </div>
            </div>
        `;
    }

    renderMilestoneMarkers(milestones, target) {
        return milestones.map(milestone => {
            const position = (milestone.value / target) * 100;
            return `
                <div class="milestone-marker ${milestone.completed ? 'completed' : ''}" 
                     style="left: ${position}%" 
                     title="${milestone.label}: ${milestone.value}">
                </div>
            `;
        }).join('');
    }

    renderDetailedMetrics(item) {
        if (item.current === 0) return '';
        
        return `
            <div class="detailed-metrics">
                <div class="metric">
                    <span class="metric-label">Daily Rate:</span>
                    <span class="metric-value">${item.dailyRate.toFixed(1)} ${item.unit}/day</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Weekly Goal:</span>
                    <span class="metric-value">${item.weeklyGoal} ${item.unit}/week</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Remaining:</span>
                    <span class="metric-value">${item.target - item.current} ${item.unit}</span>
                </div>
            </div>
        `;
    }

    renderPredictions(item) {
        const daysToComplete = Math.ceil((item.target - item.current) / Math.max(item.dailyRate, 0.1));
        const completionDate = new Date();
        completionDate.setDate(completionDate.getDate() + daysToComplete);
        
        return `
            <div class="predictions">
                <div class="prediction">
                    <span class="prediction-icon">📅</span>
                    <span class="prediction-text">Estimated completion: ${item.estimatedCompletion}</span>
                </div>
                <div class="prediction">
                    <span class="prediction-icon">🎯</span>
                    <span class="prediction-text">At current rate: ${this.formatDate(completionDate)}</span>
                </div>
            </div>
        `;
    }

    renderMilestones(milestones) {
        return `
            <div class="milestones">
                <h4>Milestones</h4>
                <div class="milestone-list">
                    ${milestones.map(milestone => `
                        <div class="milestone ${milestone.completed ? 'completed' : ''}">
                            <div class="milestone-icon">${milestone.completed ? '✅' : '⭕'}</div>
                            <div class="milestone-info">
                                <span class="milestone-label">${milestone.label}</span>
                                <span class="milestone-value">${milestone.value}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderRecentActivity(activities) {
        if (!activities || activities.length === 0) {
            return `
                <div class="recent-activity">
                    <h4>Recent Activity</h4>
                    <p class="no-activity">No recent activity</p>
                </div>
            `;
        }
        
        return `
            <div class="recent-activity">
                <h4>Recent Activity</h4>
                <div class="activity-list">
                    ${activities.slice(0, 3).map(activity => `
                        <div class="activity-item">
                            <div class="activity-date">${this.formatDate(activity.date)}</div>
                            <div class="activity-details">
                                <span class="activity-count">+${activity.count}</span>
                                <span class="activity-type">${this.formatActivityType(activity.type)}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderTips(tips) {
        if (!tips || tips.length === 0) return '';
        
        return `
            <div class="progress-tips">
                <h4>💡 Tips to Progress</h4>
                <ul class="tips-list">
                    ${tips.map(tip => `<li>${tip}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    renderRecommendations() {
        const recommendations = this.generateRecommendations();
        
        if (recommendations.length === 0) return '';
        
        return `
            <div class="recommendations">
                <h3>Recommendations</h3>
                <div class="recommendation-list">
                    ${recommendations.map(rec => `
                        <div class="recommendation-item ${rec.priority}">
                            <div class="recommendation-icon">${rec.icon}</div>
                            <div class="recommendation-content">
                                <h4>${rec.title}</h4>
                                <p>${rec.description}</p>
                                ${rec.action ? `<button class="btn-action" onclick="${rec.action}">${rec.actionText}</button>` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    generateRecommendations() {
        const recommendations = [];
        
        // Find items near completion
        const nearCompletion = this.progressData.filter(item => {
            const progress = (item.current / item.target) * 100;
            return progress >= 70 && progress < 100;
        });
        
        nearCompletion.forEach(item => {
            recommendations.push({
                title: `Almost there with ${item.badgeName}!`,
                description: `You're ${item.target - item.current} ${item.unit} away from earning this badge.`,
                icon: '🎯',
                priority: 'high',
                action: `progressDashboard.trackProgress('${item.badgeId}')`,
                actionText: 'Focus on this'
            });
        });
        
        // Find stalled progress
        const stalled = this.progressData.filter(item => {
            return item.dailyRate < 0.5 && item.current > 0 && item.current < item.target;
        });
        
        if (stalled.length > 0) {
            recommendations.push({
                title: 'Boost your progress',
                description: 'Some of your goals could use more attention. Consider setting daily reminders.',
                icon: '⚡',
                priority: 'medium',
                action: 'progressDashboard.showSettings()',
                actionText: 'Set reminders'
            });
        }
        
        // Streak recommendations
        if (this.userStats.streakDays >= 7) {
            recommendations.push({
                title: 'Great streak!',
                description: `You've maintained a ${this.userStats.streakDays}-day streak. Keep it up!`,
                icon: '🔥',
                priority: 'low'
            });
        }
        
        return recommendations.slice(0, 3); // Limit to 3 recommendations
    }

    attachEventListeners() {
        // Add click handlers for expandable sections
        const progressItems = this.container.querySelectorAll('.progress-item');
        progressItems.forEach(item => {
            const header = item.querySelector('.progress-header');
            header.addEventListener('click', () => {
                item.classList.toggle('expanded');
            });
        });
    }

    animateProgressBars() {
        const progressBars = this.container.querySelectorAll('.progress-fill');
        
        progressBars.forEach((bar, index) => {
            setTimeout(() => {
                const targetWidth = bar.dataset.progress + '%';
                bar.style.transition = 'width 1.5s cubic-bezier(0.4, 0, 0.2, 1)';
                bar.style.width = targetWidth;
            }, index * 200);
        });
    }

    calculateOverallCompletion() {
        if (this.progressData.length === 0) return 0;
        
        const totalProgress = this.progressData.reduce((sum, item) => {
            return sum + Math.min((item.current / item.target) * 100, 100);
        }, 0);
        
        return Math.round(totalProgress / this.progressData.length);
    }

    startAutoUpdate() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
        }
        
        this.updateTimer = setInterval(() => {
            this.refresh();
        }, this.options.updateInterval);
    }

    stopAutoUpdate() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
    }

    // Public methods
    async refresh() {
        await this.loadProgressData();
        this.render();
    }

    trackProgress(badgeId) {
        const item = this.progressData.find(p => p.badgeId === badgeId);
        if (item) {
            this.showTrackProgressModal(item);
        }
    }

    showDetails(badgeId) {
        const item = this.progressData.find(p => p.badgeId === badgeId);
        if (item) {
            this.showDetailsModal(item);
        }
    }

    showSettings() {
        this.showSettingsModal();
    }

    showTrackProgressModal(item) {
        const isCompleted = item.current >= item.target;
        const progressPercentage = Math.min((item.current / item.target) * 100, 100);
        
        const modal = this.createModal('track-progress-modal', `
            <div class="modal-header">
                <h2>${isCompleted ? '🏆' : '📊'} ${item.badgeName}</h2>
                <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
            </div>
            <div class="modal-body">
                ${isCompleted ? `
                    <div class="badge-earned-celebration">
                        <div class="celebration-icon">🎉</div>
                        <h3>Congratulations!</h3>
                        <p>You've earned the ${item.badgeName} badge!</p>
                        <div class="badge-display">
                            <div class="badge-icon">${this.getBadgeIcon(item.category)}</div>
                            <div class="badge-info">
                                <div class="badge-name">${item.badgeName}</div>
                                <div class="badge-category">${this.capitalizeFirst(item.category)}</div>
                            </div>
                        </div>
                        <div class="share-options">
                            <button class="btn-share" onclick="progressDashboard.shareBadge('${item.badgeId}')">
                                📤 Share Achievement
                            </button>
                        </div>
                    </div>
                ` : `
                    <div class="progress-tracking">
                        <div class="current-progress">
                            <div class="progress-circle">
                                <svg width="120" height="120" viewBox="0 0 120 120">
                                    <circle cx="60" cy="60" r="50" fill="none" stroke="#e5e7eb" stroke-width="8"/>
                                    <circle cx="60" cy="60" r="50" fill="none" stroke="var(--primary-color)" 
                                            stroke-width="8" stroke-linecap="round"
                                            stroke-dasharray="${2 * Math.PI * 50}" 
                                            stroke-dashoffset="${2 * Math.PI * 50 * (1 - progressPercentage / 100)}"
                                            transform="rotate(-90 60 60)"/>
                                </svg>
                                <div class="progress-text">
                                    <div class="progress-percentage">${Math.round(progressPercentage)}%</div>
                                    <div class="progress-fraction">${item.current}/${item.target}</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="progress-actions">
                            <h3>Quick Actions</h3>
                            <div class="action-buttons">
                                ${this.getQuickActions(item).map(action => `
                                    <button class="btn-action" onclick="${action.onclick}">
                                        ${action.icon} ${action.label}
                                    </button>
                                `).join('')}
                            </div>
                        </div>
                        
                        <div class="manual-update">
                            <h3>Manual Update</h3>
                            <div class="update-controls">
                                <label for="progress-input">Current Progress:</label>
                                <input type="number" id="progress-input" min="0" max="${item.target}" 
                                       value="${item.current}" class="progress-input">
                                <button class="btn-update" onclick="progressDashboard.updateProgressFromModal('${item.badgeId}')">
                                    Update Progress
                                </button>
                            </div>
                        </div>
                    </div>
                `}
            </div>
        `);
        
        document.body.appendChild(modal);
        modal.style.display = 'flex';
    }

    showDetailsModal(item) {
        const progressPercentage = Math.min((item.current / item.target) * 100, 100);
        const isCompleted = item.current >= item.target;
        
        const modal = this.createModal('details-modal', `
            <div class="modal-header">
                <h2>📋 ${item.badgeName} Details</h2>
                <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="badge-details">
                    <div class="badge-overview">
                        <div class="badge-icon-large">${this.getBadgeIcon(item.category)}</div>
                        <div class="badge-meta">
                            <h3>${item.badgeName}</h3>
                            <div class="badge-tags">
                                <span class="tag category">${this.capitalizeFirst(item.category)}</span>
                                <span class="tag difficulty ${item.difficulty}">${this.capitalizeFirst(item.difficulty)}</span>
                                ${isCompleted ? '<span class="tag completed">Completed</span>' : ''}
                            </div>
                            <p class="badge-description">${item.description}</p>
                        </div>
                    </div>
                    
                    <div class="progress-breakdown">
                        <h4>Progress Breakdown</h4>
                        <div class="progress-stats">
                            <div class="stat">
                                <span class="stat-label">Current:</span>
                                <span class="stat-value">${item.current} ${item.unit}</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Target:</span>
                                <span class="stat-value">${item.target} ${item.unit}</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Remaining:</span>
                                <span class="stat-value">${Math.max(0, item.target - item.current)} ${item.unit}</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Progress:</span>
                                <span class="stat-value">${Math.round(progressPercentage)}%</span>
                            </div>
                        </div>
                    </div>
                    
                    ${this.renderMilestones(item.milestones)}
                    
                    ${item.recentActivity && item.recentActivity.length > 0 ? this.renderRecentActivity(item.recentActivity) : ''}
                    
                    ${this.renderTips(item.tips)}
                    
                    ${!isCompleted && this.options.showPredictions ? this.renderPredictions(item) : ''}
                </div>
            </div>
        `);
        
        document.body.appendChild(modal);
        modal.style.display = 'flex';
    }

    showSettingsModal() {
        const modal = this.createModal('settings-modal', `
            <div class="modal-header">
                <h2>⚙️ Dashboard Settings</h2>
                <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="settings-section">
                    <h3>Display Options</h3>
                    <div class="setting-item">
                        <label class="setting-label">
                            <input type="checkbox" ${this.options.showDetailedMetrics ? 'checked' : ''} 
                                   onchange="progressDashboard.updateSetting('showDetailedMetrics', this.checked)">
                            Show detailed metrics
                        </label>
                    </div>
                    <div class="setting-item">
                        <label class="setting-label">
                            <input type="checkbox" ${this.options.showPredictions ? 'checked' : ''} 
                                   onchange="progressDashboard.updateSetting('showPredictions', this.checked)">
                            Show completion predictions
                        </label>
                    </div>
                    <div class="setting-item">
                        <label class="setting-label">
                            <input type="checkbox" ${this.options.showRecommendations ? 'checked' : ''} 
                                   onchange="progressDashboard.updateSetting('showRecommendations', this.checked)">
                            Show recommendations
                        </label>
                    </div>
                    <div class="setting-item">
                        <label class="setting-label">
                            <input type="checkbox" ${this.options.animateProgress ? 'checked' : ''} 
                                   onchange="progressDashboard.updateSetting('animateProgress', this.checked)">
                            Animate progress bars
                        </label>
                    </div>
                </div>
                
                <div class="settings-section">
                    <h3>Notifications</h3>
                    <div class="setting-item">
                        <label class="setting-label">
                            Update interval (seconds):
                            <input type="number" min="10" max="300" value="${this.options.updateInterval / 1000}" 
                                   onchange="progressDashboard.updateSetting('updateInterval', this.value * 1000)">
                        </label>
                    </div>
                </div>
                
                <div class="settings-section">
                    <h3>Data Management</h3>
                    <div class="setting-actions">
                        <button class="btn-action" onclick="progressDashboard.exportProgress()">
                            📤 Export Progress Data
                        </button>
                        <button class="btn-action warning" onclick="progressDashboard.resetProgress()">
                            🔄 Reset All Progress
                        </button>
                    </div>
                </div>
            </div>
        `);
        
        document.body.appendChild(modal);
        modal.style.display = 'flex';
    }

    updateProgress(badgeId, newProgress) {
        const item = this.progressData.find(p => p.badgeId === badgeId);
        if (item) {
            item.current = Math.min(newProgress, item.target);
            this.render();
            
            // Check if badge is now earned
            if (item.current >= item.target && window.achievementNotifications) {
                window.achievementNotifications.showNotification({
                    id: item.badgeId,
                    name: item.badgeName,
                    category: item.category,
                    color: this.getCategoryColor(item.category)
                }, 'badge-earned');
            }
        }
    }

    // Utility methods
    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    formatDate(date) {
        if (typeof date === 'string') {
            date = new Date(date);
        }
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric'
        });
    }

    formatActivityType(type) {
        return type.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    getCategoryColor(category) {
        const colors = {
            'milestone': '#f59e0b',
            'consistency': '#ef4444',
            'tracking': '#3b82f6',
            'skills': '#10b981',
            'learning': '#8b5cf6',
            'achievement': '#f97316',
            'resilience': '#ef4444'
        };
        return colors[category] || '#6b7280';
    }

    getBadgeIcon(category) {
        const icons = {
            'milestone': '🏆',
            'consistency': '🔥',
            'tracking': '📊',
            'skills': '🎯',
            'learning': '📚',
            'achievement': '⭐',
            'resilience': '💪'
        };
        return icons[category] || '🏅';
    }

    createModal(id, content) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.id = id;
        modal.innerHTML = `
            <div class="modal-content">
                ${content}
            </div>
        `;
        
        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        // Close modal with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && document.getElementById(id)) {
                modal.remove();
            }
        });
        
        return modal;
    }

    getQuickActions(item) {
        const actions = [];
        
        // Category-specific quick actions
        switch (item.category) {
            case 'learning':
                actions.push(
                    { icon: '📚', label: 'Browse Resources', onclick: 'window.location.hash = "resources"' },
                    { icon: '📖', label: 'Read Article', onclick: `progressDashboard.simulateActivity('${item.badgeId}', 'article', 1)` }
                );
                break;
            case 'tracking':
                actions.push(
                    { icon: '😊', label: 'Log Mood', onclick: 'window.location.hash = "mood-tracker"' },
                    { icon: '📝', label: 'Write Journal', onclick: 'window.location.hash = "journal"' }
                );
                break;
            case 'skills':
                actions.push(
                    { icon: '🧘', label: 'Start Exercise', onclick: 'window.location.hash = "exercises"' },
                    { icon: '⏱️', label: 'Quick Breathing', onclick: `progressDashboard.simulateActivity('${item.badgeId}', 'exercise', 1)` }
                );
                break;
            case 'consistency':
                actions.push(
                    { icon: '✅', label: 'Check In', onclick: `progressDashboard.simulateActivity('${item.badgeId}', 'checkin', 1)` },
                    { icon: '📅', label: 'Set Reminder', onclick: 'progressDashboard.setReminder()' }
                );
                break;
            default:
                actions.push(
                    { icon: '🎯', label: 'Take Action', onclick: `progressDashboard.simulateActivity('${item.badgeId}', 'action', 1)` }
                );
        }
        
        return actions;
    }

    updateProgressFromModal(badgeId) {
        const input = document.getElementById('progress-input');
        if (input) {
            const newProgress = parseInt(input.value);
            this.updateProgress(badgeId, newProgress);
            
            // Close modal and refresh
            document.querySelector('.modal').remove();
            this.render();
            
            // Show success notification
            this.showNotification('Progress updated successfully!', 'success');
        }
    }

    simulateActivity(badgeId, activityType, amount) {
        const item = this.progressData.find(p => p.badgeId === badgeId);
        if (item) {
            const newProgress = Math.min(item.current + amount, item.target);
            this.updateProgress(badgeId, newProgress);
            
            // Add to recent activity
            const today = new Date().toISOString().split('T')[0];
            if (!item.recentActivity) item.recentActivity = [];
            
            const existingActivity = item.recentActivity.find(a => a.date === today);
            if (existingActivity) {
                existingActivity.count += amount;
            } else {
                item.recentActivity.unshift({
                    date: today,
                    count: amount,
                    type: activityType
                });
            }
            
            // Keep only last 7 days
            item.recentActivity = item.recentActivity.slice(0, 7);
            
            this.showNotification(`+${amount} ${item.unit} added!`, 'success');
        }
    }

    shareBadge(badgeId) {
        const item = this.progressData.find(p => p.badgeId === badgeId);
        if (item) {
            const shareText = `I just earned the ${item.badgeName} badge on ChillBuddy! 🏆 #MentalHealthJourney #ChillBuddy`;
            
            if (navigator.share) {
                navigator.share({
                    title: 'ChillBuddy Achievement',
                    text: shareText,
                    url: window.location.href
                });
            } else {
                // Fallback to clipboard
                navigator.clipboard.writeText(shareText).then(() => {
                    this.showNotification('Achievement copied to clipboard!', 'success');
                });
            }
        }
    }

    updateSetting(key, value) {
        this.options[key] = value;
        localStorage.setItem('progressDashboardSettings', JSON.stringify(this.options));
        this.render();
    }

    exportProgress() {
        const data = {
            progressData: this.progressData,
            userStats: this.userStats,
            exportDate: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chillbuddy-progress-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.showNotification('Progress data exported!', 'success');
    }

    resetProgress() {
        if (confirm('Are you sure you want to reset all progress? This action cannot be undone.')) {
            this.progressData.forEach(item => {
                item.current = 0;
                item.recentActivity = [];
                item.milestones.forEach(milestone => milestone.completed = false);
            });
            
            this.userStats = {
                totalSessions: 0,
                streakDays: 0,
                moodEntries: 0,
                copingStrategiesLearned: 0,
                resourcesExplored: 0,
                challengesCompleted: 0,
                activeDays: 0,
                averageMoodScore: 0,
                improvementRate: 0,
                lastActivity: new Date().toISOString()
            };
            
            this.render();
            document.querySelector('.modal').remove();
            this.showNotification('All progress has been reset.', 'info');
        }
    }

    setReminder() {
        this.showNotification('Reminder feature coming soon!', 'info');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            animation: slideInRight 0.3s ease;
        `;
        
        switch (type) {
            case 'success':
                notification.style.backgroundColor = '#10b981';
                break;
            case 'error':
                notification.style.backgroundColor = '#ef4444';
                break;
            case 'warning':
                notification.style.backgroundColor = '#f59e0b';
                break;
            default:
                notification.style.backgroundColor = '#3b82f6';
        }
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    destroy() {
        this.stopAutoUpdate();
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// Global instance
let progressDashboard = null;

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        const container = document.getElementById('progress-dashboard-container');
        if (container) {
            progressDashboard = new ProgressTrackingDashboard('progress-dashboard-container');
        }
    });
} else {
    const container = document.getElementById('progress-dashboard-container');
    if (container) {
        progressDashboard = new ProgressTrackingDashboard('progress-dashboard-container');
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProgressTrackingDashboard;
}

// Make available globally
window.ProgressTrackingDashboard = ProgressTrackingDashboard;
window.progressDashboard = progressDashboard;