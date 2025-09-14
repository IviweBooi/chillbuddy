// Badge Gallery Component
class BadgeGallery {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            showProgress: true,
            showEarnedDate: true,
            showDescription: true,
            allowFiltering: true,
            showStats: true,
            ...options
        };
        
        this.badges = [];
        this.filteredBadges = [];
        this.currentFilter = 'all'; // 'all', 'earned', 'locked'
        this.currentSort = 'recent'; // 'recent', 'alphabetical', 'progress'
        
        this.init();
    }

    init() {
        if (!this.container) {
            console.error('Badge gallery container not found');
            return;
        }
        
        this.setupEventListeners();
        this.loadBadgeData();
    }

    async loadBadgeData() {
        try {
            // Try to fetch from API first
            const response = await fetch('/api/user/badges');
            if (response.ok) {
                const data = await response.json();
                this.badges = [...data.earned, ...data.locked];
            } else {
                throw new Error('API not available');
            }
        } catch (error) {
            console.log('Using mock badge data:', error.message);
            this.badges = this.getMockBadgeData();
        }
        
        this.filteredBadges = [...this.badges];
    }

    getMockBadgeData() {
        return [
            {
                id: 'first-steps',
                name: 'First Steps',
                description: 'Started your mental health journey with ChillBuddy',
                category: 'milestone',
                difficulty: 'easy',
                earned: true,
                earnedDate: '2024-01-15',
                icon: 'first-steps.svg',
                color: '#3B82F6',
                criteria: 'Complete your first conversation',
                tips: 'Welcome to ChillBuddy! This badge marks the beginning of your mental health journey.'
            },
            {
                id: 'streak-master',
                name: 'Streak Master',
                description: 'Maintained a 7-day check-in streak',
                category: 'consistency',
                difficulty: 'medium',
                earned: true,
                earnedDate: '2024-01-22',
                icon: 'streak-master.svg',
                color: '#EF4444',
                criteria: 'Check in for 7 consecutive days',
                tips: 'Consistency is key to mental wellness. Keep up the great work!'
            },
            {
                id: 'mood-tracker',
                name: 'Mood Tracker',
                description: 'Logged 30 mood entries',
                category: 'tracking',
                difficulty: 'medium',
                earned: true,
                earnedDate: '2024-02-01',
                icon: 'mood-tracker.svg',
                color: '#3B82F6',
                criteria: 'Log 30 mood entries',
                tips: 'Understanding your mood patterns is a powerful tool for mental health.'
            },
            {
                id: 'coping-champion',
                name: 'Coping Champion',
                description: 'Mastered 10 coping strategies',
                category: 'skills',
                difficulty: 'hard',
                earned: true,
                earnedDate: '2024-02-08',
                icon: 'coping-champion.svg',
                color: '#10B981',
                criteria: 'Learn and practice 10 different coping strategies',
                tips: 'Having multiple coping strategies gives you flexibility in managing stress.'
            },
            {
                id: 'resource-explorer',
                name: 'Resource Explorer',
                description: 'Explore 25 mental health resources',
                category: 'learning',
                difficulty: 'medium',
                earned: false,
                progress: { current: 18, total: 25 },
                icon: 'resource-explorer.svg',
                color: '#8B5CF6',
                criteria: 'Explore 25 different mental health resources',
                tips: 'Knowledge is power. The more you learn, the better equipped you\'ll be.'
            },
            {
                id: 'challenge-crusher',
                name: 'Challenge Crusher',
                description: 'Complete 5 mental health challenges',
                category: 'achievement',
                difficulty: 'hard',
                earned: false,
                progress: { current: 2, total: 5 },
                icon: 'challenge-crusher.svg',
                color: '#EF4444',
                criteria: 'Complete 5 different mental health challenges',
                tips: 'Challenges help you grow stronger and more resilient.'
            },
            {
                id: 'monthly-milestone',
                name: 'Monthly Milestone',
                description: 'Maintain consistent activity for 30 days',
                category: 'consistency',
                difficulty: 'hard',
                earned: false,
                progress: { current: 22, total: 30 },
                icon: 'monthly-milestone.svg',
                color: '#F59E0B',
                criteria: 'Stay active on ChillBuddy for 30 consecutive days',
                tips: 'Building lasting habits takes time. You\'re almost there!'
            },
            {
                id: 'crisis-survivor',
                name: 'Crisis Survivor',
                description: 'Successfully navigate a mental health crisis',
                category: 'resilience',
                difficulty: 'expert',
                earned: false,
                progress: null,
                icon: 'crisis-survivor.svg',
                color: '#EF4444',
                criteria: 'Use ChillBuddy resources during a mental health crisis',
                tips: 'This badge represents incredible strength and resilience.'
            }
        ];
    }

    render() {
        if (!this.container) return;
        
        this.container.innerHTML = `
            ${this.options.showStats ? this.renderStats() : ''}
            ${this.options.allowFiltering ? this.renderFilters() : ''}
            <div class="badge-gallery-grid">
                ${this.renderBadges()}
            </div>
        `;
        
        this.attachEventListeners();
    }

    renderStats() {
        const earnedCount = this.badges.filter(b => b.earned).length;
        const totalCount = this.badges.length;
        const progressPercentage = Math.round((earnedCount / totalCount) * 100);
        
        return `
            <div class="badge-stats">
                <div class="stats-overview">
                    <h3>Badge Collection</h3>
                    <div class="progress-summary">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${progressPercentage}%"></div>
                        </div>
                        <span class="progress-text">${earnedCount} of ${totalCount} badges earned (${progressPercentage}%)</span>
                    </div>
                </div>
                <div class="category-breakdown">
                    ${this.renderCategoryStats()}
                </div>
            </div>
        `;
    }

    renderCategoryStats() {
        const categories = {};
        this.badges.forEach(badge => {
            if (!categories[badge.category]) {
                categories[badge.category] = { total: 0, earned: 0 };
            }
            categories[badge.category].total++;
            if (badge.earned) {
                categories[badge.category].earned++;
            }
        });

        return Object.entries(categories).map(([category, stats]) => `
            <div class="category-stat">
                <span class="category-name">${this.capitalizeFirst(category)}</span>
                <span class="category-progress">${stats.earned}/${stats.total}</span>
            </div>
        `).join('');
    }

    renderFilters() {
        return `
            <div class="badge-filters">
                <div class="filter-group">
                    <label>Show:</label>
                    <select class="filter-select" data-filter="status">
                        <option value="all">All Badges</option>
                        <option value="earned">Earned Only</option>
                        <option value="locked">Locked Only</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Sort by:</label>
                    <select class="filter-select" data-filter="sort">
                        <option value="recent">Most Recent</option>
                        <option value="alphabetical">Alphabetical</option>
                        <option value="progress">Progress</option>
                        <option value="difficulty">Difficulty</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Category:</label>
                    <select class="filter-select" data-filter="category">
                        <option value="all">All Categories</option>
                        <option value="milestone">Milestones</option>
                        <option value="consistency">Consistency</option>
                        <option value="tracking">Tracking</option>
                        <option value="skills">Skills</option>
                        <option value="learning">Learning</option>
                        <option value="achievement">Achievement</option>
                        <option value="resilience">Resilience</option>
                    </select>
                </div>
            </div>
        `;
    }

    renderBadges() {
        return this.filteredBadges.map(badge => this.renderBadge(badge)).join('');
    }

    renderBadge(badge) {
        const earnedClass = badge.earned ? 'earned' : 'locked';
        const progressText = this.getProgressText(badge);
        
        return `
            <div class="badge-gallery-item ${earnedClass}" data-badge-id="${badge.id}">
                <div class="badge-visual">
                    <div class="badge-icon-container">
                        ${this.renderBadgeIcon(badge)}
                        ${badge.earned ? '<div class="earned-indicator">✓</div>' : ''}
                    </div>
                    <div class="badge-difficulty ${badge.difficulty}">${this.capitalizeFirst(badge.difficulty)}</div>
                </div>
                
                <div class="badge-content">
                    <div class="badge-header">
                        <h4 class="badge-title">${badge.name}</h4>
                        <span class="badge-category">${this.capitalizeFirst(badge.category)}</span>
                    </div>
                    
                    ${this.options.showDescription ? `<p class="badge-description">${badge.description}</p>` : ''}
                    
                    <div class="badge-criteria">
                        <strong>How to earn:</strong> ${badge.criteria}
                    </div>
                    
                    ${this.options.showProgress && !badge.earned ? `
                        <div class="badge-progress-section">
                            ${progressText}
                            ${badge.progress ? this.renderProgressBar(badge.progress) : ''}
                        </div>
                    ` : ''}
                    
                    ${this.options.showEarnedDate && badge.earned ? `
                        <div class="badge-earned-date">
                            <span>Earned on ${this.formatDate(badge.earnedDate)}</span>
                        </div>
                    ` : ''}
                    
                    <div class="badge-tips">
                        <strong>💡 Tip:</strong> ${badge.tips}
                    </div>
                </div>
                
                <div class="badge-actions">
                    ${badge.earned ? `
                        <button class="btn-share" onclick="shareBadge('${badge.id}')">Share</button>
                    ` : `
                        <button class="btn-track" onclick="trackBadgeProgress('${badge.id}')">Track Progress</button>
                    `}
                    <button class="btn-details" onclick="showBadgeDetails('${badge.id}')">Details</button>
                </div>
            </div>
        `;
    }

    renderBadgeIcon(badge) {
        // For now, return a placeholder. In a real implementation, you'd load the actual SVG
        return `
            <div class="badge-icon" style="background-color: ${badge.color}">
                <svg width="48" height="48" viewBox="0 0 48 48">
                    <circle cx="24" cy="24" r="20" fill="white" opacity="0.9"/>
                    <text x="24" y="28" text-anchor="middle" font-size="16" fill="${badge.color}">
                        ${badge.name.charAt(0)}
                    </text>
                </svg>
            </div>
        `;
    }

    renderProgressBar(progress) {
        const percentage = Math.round((progress.current / progress.total) * 100);
        return `
            <div class="progress-bar-container">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${percentage}%"></div>
                </div>
                <span class="progress-percentage">${percentage}%</span>
            </div>
        `;
    }

    getProgressText(badge) {
        if (badge.earned) {
            return '<span class="earned-text">✅ Earned!</span>';
        }
        
        if (badge.progress) {
            return `<span class="progress-text">Progress: ${badge.progress.current}/${badge.progress.total}</span>`;
        }
        
        return '<span class="locked-text">🔒 Locked</span>';
    }

    attachEventListeners() {
        // Filter change handlers
        const filterSelects = this.container.querySelectorAll('.filter-select');
        filterSelects.forEach(select => {
            select.addEventListener('change', (e) => {
                this.handleFilterChange(e.target.dataset.filter, e.target.value);
            });
        });

        // Badge click handlers
        const badgeItems = this.container.querySelectorAll('.badge-gallery-item');
        badgeItems.forEach(item => {
            item.addEventListener('click', (e) => {
                if (!e.target.closest('.badge-actions')) {
                    this.showBadgeModal(item.dataset.badgeId);
                }
            });
        });
    }

    handleFilterChange(filterType, value) {
        switch (filterType) {
            case 'status':
                this.currentFilter = value;
                break;
            case 'sort':
                this.currentSort = value;
                break;
            case 'category':
                this.currentCategory = value;
                break;
        }
        
        this.applyFilters();
        this.render();
    }

    applyFilters() {
        let filtered = [...this.badges];
        
        // Filter by status
        if (this.currentFilter === 'earned') {
            filtered = filtered.filter(badge => badge.earned);
        } else if (this.currentFilter === 'locked') {
            filtered = filtered.filter(badge => !badge.earned);
        }
        
        // Filter by category
        if (this.currentCategory && this.currentCategory !== 'all') {
            filtered = filtered.filter(badge => badge.category === this.currentCategory);
        }
        
        // Sort
        switch (this.currentSort) {
            case 'alphabetical':
                filtered.sort((a, b) => a.name.localeCompare(b.name));
                break;
            case 'progress':
                filtered.sort((a, b) => {
                    if (a.earned && !b.earned) return -1;
                    if (!a.earned && b.earned) return 1;
                    if (a.progress && b.progress) {
                        const aProgress = a.progress.current / a.progress.total;
                        const bProgress = b.progress.current / b.progress.total;
                        return bProgress - aProgress;
                    }
                    return 0;
                });
                break;
            case 'difficulty':
                const difficultyOrder = { 'easy': 1, 'medium': 2, 'hard': 3, 'expert': 4 };
                filtered.sort((a, b) => difficultyOrder[a.difficulty] - difficultyOrder[b.difficulty]);
                break;
            case 'recent':
            default:
                filtered.sort((a, b) => {
                    if (a.earned && b.earned) {
                        return new Date(b.earnedDate) - new Date(a.earnedDate);
                    }
                    if (a.earned && !b.earned) return -1;
                    if (!a.earned && b.earned) return 1;
                    return 0;
                });
                break;
        }
        
        this.filteredBadges = filtered;
    }

    showBadgeModal(badgeId) {
        const badge = this.badges.find(b => b.id === badgeId);
        if (!badge) return;
        
        // Create and show detailed badge modal
        console.log('Showing badge details for:', badge.name);
        // TODO: Implement detailed badge modal
    }

    // Utility methods
    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    // Public methods for external use
    refresh() {
        this.loadBadgeData().then(() => {
            this.applyFilters();
            this.render();
        });
    }

    addBadge(badgeData) {
        this.badges.push(badgeData);
        this.applyFilters();
        this.render();
    }

    updateBadgeProgress(badgeId, progress) {
        const badge = this.badges.find(b => b.id === badgeId);
        if (badge) {
            badge.progress = progress;
            this.applyFilters();
            this.render();
        }
    }

    earnBadge(badgeId) {
        const badge = this.badges.find(b => b.id === badgeId);
        if (badge && !badge.earned) {
            badge.earned = true;
            badge.earnedDate = new Date().toISOString().split('T')[0];
            delete badge.progress;
            
            // Show achievement notification
            if (window.profileModal) {
                window.profileModal.showAchievementNotification(badge);
            }
            
            this.applyFilters();
            this.render();
        }
    }
}

// Global functions for button handlers
function shareBadge(badgeId) {
    console.log('Sharing badge:', badgeId);
    // TODO: Implement badge sharing
}

function trackBadgeProgress(badgeId) {
    console.log('Tracking progress for badge:', badgeId);
    // TODO: Implement progress tracking
}

function showBadgeDetails(badgeId) {
    console.log('Showing details for badge:', badgeId);
    // TODO: Implement detailed badge view
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BadgeGallery;
}