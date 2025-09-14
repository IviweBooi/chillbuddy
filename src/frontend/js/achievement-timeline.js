/**
 * Achievement History Timeline
 * Chronological view of earned badges and milestones
 */

class AchievementTimeline {
    constructor(container) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        this.achievements = [];
        this.milestones = [];
        this.filteredData = [];
        this.currentFilter = 'all';
        this.currentSort = 'newest';
        this.isLoading = false;
        
        this.init();
    }

    init() {
        this.createTimelineStructure();
        this.loadData();
        this.attachEventListeners();
        // Removed injectStyles - using existing design system
    }

    createTimelineStructure() {
        // Check if we're inside a modal and adapt accordingly
        const isInModal = this.container.closest('.modal-content');
        
        if (isInModal) {
            // Simplified structure for modal integration
            this.container.innerHTML = `
                <div class="timeline-container modal-timeline">
                    <div class="timeline-header">
                        <h3 style="margin: 0 0 16px 0; display: flex; align-items: center; gap: 8px;">
                            📅 Achievement Timeline
                        </h3>
                        <div class="timeline-filters">
                            <button class="filter-btn active" data-filter="all">All</button>
                            <button class="filter-btn" data-filter="badges">Badges</button>
                            <button class="filter-btn" data-filter="milestones">Milestones</button>
                            <button class="filter-btn" data-filter="recent">Recent</button>
                        </div>
                    </div>
                    
                    <div class="timeline-content">
                        <div class="timeline-loading" style="display: none;">
                            <div class="loading-spinner"></div>
                            <p>Loading achievements...</p>
                        </div>
                        
                        <div class="timeline-empty" style="display: none;">
                            <div class="empty-icon">🎯</div>
                            <h4>No Achievements Yet</h4>
                            <p>Start chatting to earn badges!</p>
                        </div>
                        
                        <div class="timeline-list"></div>
                    </div>
                </div>
            `;
        } else {
            // Full structure for standalone use
            this.container.innerHTML = `
                <div class="timeline-container">
                    <div class="timeline-header">
                        <div class="timeline-title">
                            <h2>🏆 Achievement History</h2>
                            <p>Your journey through badges and milestones</p>
                        </div>
                        <div class="timeline-controls">
                            <div class="timeline-filters">
                                <button class="filter-btn active" data-filter="all">All</button>
                                <button class="filter-btn" data-filter="badges">Badges</button>
                                <button class="filter-btn" data-filter="milestones">Milestones</button>
                                <button class="filter-btn" data-filter="recent">Recent</button>
                            </div>
                            <div class="timeline-sort">
                                <select class="sort-select">
                                    <option value="newest">Newest First</option>
                                    <option value="oldest">Oldest First</option>
                                    <option value="category">By Category</option>
                                    <option value="importance">By Importance</option>
                                </select>
                            </div>
                            <button class="timeline-refresh" title="Refresh Timeline">
                                <span class="icon">🔄</span>
                            </button>
                        </div>
                    </div>
                    
                    <div class="timeline-stats">
                        <div class="stat-card">
                            <div class="stat-icon">🏅</div>
                            <div class="stat-content">
                                <div class="stat-value" id="total-badges">0</div>
                                <div class="stat-label">Total Badges</div>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon">🎯</div>
                            <div class="stat-content">
                                <div class="stat-value" id="total-milestones">0</div>
                                <div class="stat-label">Milestones</div>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon">📅</div>
                            <div class="stat-content">
                                <div class="stat-value" id="active-days">0</div>
                                <div class="stat-label">Active Days</div>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon">🔥</div>
                            <div class="stat-content">
                                <div class="stat-value" id="current-streak">0</div>
                                <div class="stat-label">Current Streak</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="timeline-content">
                        <div class="timeline-loading" style="display: none;">
                            <div class="loading-spinner"></div>
                            <p>Loading your achievement history...</p>
                        </div>
                        
                        <div class="timeline-empty" style="display: none;">
                            <div class="empty-icon">🎯</div>
                            <h3>No Achievements Yet</h3>
                            <p>Start chatting and engaging to earn your first badges!</p>
                            <button class="btn-start-earning">Start Earning Badges</button>
                        </div>
                        
                        <div class="timeline-list"></div>
                    </div>
                    
                    <div class="timeline-footer">
                        <div class="timeline-pagination">
                            <button class="btn-load-more" style="display: none;">Load More</button>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    async loadData() {
        this.showLoading(true);
        
        try {
            // Try to load from API first
            const data = await this.fetchTimelineData();
            if (data) {
                this.achievements = data.achievements || [];
                this.milestones = data.milestones || [];
            } else {
                // Fallback to mock data
                this.loadMockData();
            }
            
            this.updateStats();
            this.filterAndRenderTimeline();
        } catch (error) {
            console.warn('Failed to load timeline data, using mock data:', error);
            this.loadMockData();
            this.updateStats();
            this.filterAndRenderTimeline();
        } finally {
            this.showLoading(false);
        }
    }

    async fetchTimelineData() {
        try {
            const response = await fetch('/api/achievements/timeline');
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.warn('API not available:', error);
        }
        return null;
    }

    loadMockData() {
        const now = new Date();
        const dayMs = 24 * 60 * 60 * 1000;
        
        this.achievements = [
            {
                id: 'first-message',
                type: 'badge',
                name: 'First Message',
                description: 'Sent your first message in the chat',
                category: 'Getting Started',
                difficulty: 'Easy',
                icon: '💬',
                earnedAt: new Date(now - 30 * dayMs),
                points: 10,
                rarity: 'Common'
            },
            {
                id: 'early-bird',
                type: 'badge',
                name: 'Early Bird',
                description: 'Chatted between 5 AM and 8 AM',
                category: 'Time-based',
                difficulty: 'Easy',
                icon: '🐦',
                earnedAt: new Date(now - 25 * dayMs),
                points: 25,
                rarity: 'Common'
            },
            {
                id: 'week-milestone',
                type: 'milestone',
                name: 'One Week Active',
                description: 'Completed your first week of activity',
                category: 'Consistency',
                icon: '📅',
                earnedAt: new Date(now - 23 * dayMs),
                points: 50,
                significance: 'major'
            },
            {
                id: 'emoji-enthusiast',
                type: 'badge',
                name: 'Emoji Enthusiast',
                description: 'Used 50 different emojis in messages',
                category: 'Expression',
                difficulty: 'Medium',
                icon: '😀',
                earnedAt: new Date(now - 20 * dayMs),
                points: 40,
                rarity: 'Uncommon'
            },
            {
                id: 'conversation-starter',
                type: 'badge',
                name: 'Conversation Starter',
                description: 'Started 10 different conversations',
                category: 'Social',
                difficulty: 'Medium',
                icon: '🗣️',
                earnedAt: new Date(now - 15 * dayMs),
                points: 50,
                rarity: 'Uncommon'
            },
            {
                id: 'night-owl',
                type: 'badge',
                name: 'Night Owl',
                description: 'Chatted between midnight and 6 AM',
                category: 'Time-based',
                difficulty: 'Easy',
                icon: '🦉',
                earnedAt: new Date(now - 12 * dayMs),
                points: 25,
                rarity: 'Common'
            },
            {
                id: 'month-milestone',
                type: 'milestone',
                name: 'One Month Journey',
                description: 'Completed your first month of engagement',
                category: 'Consistency',
                icon: '🎉',
                earnedAt: new Date(now - 7 * dayMs),
                points: 100,
                significance: 'major'
            },
            {
                id: 'helpful-friend',
                type: 'badge',
                name: 'Helpful Friend',
                description: 'Received 25 positive reactions',
                category: 'Community',
                difficulty: 'Hard',
                icon: '🤝',
                earnedAt: new Date(now - 5 * dayMs),
                points: 100,
                rarity: 'Rare'
            },
            {
                id: 'wordsmith',
                type: 'badge',
                name: 'Wordsmith',
                description: 'Sent messages totaling 10,000 words',
                category: 'Communication',
                difficulty: 'Hard',
                icon: '✍️',
                earnedAt: new Date(now - 2 * dayMs),
                points: 150,
                rarity: 'Rare'
            },
            {
                id: 'streak-master',
                type: 'badge',
                name: 'Streak Master',
                description: 'Maintained a 30-day chat streak',
                category: 'Consistency',
                difficulty: 'Expert',
                icon: '🔥',
                earnedAt: new Date(now - 1 * dayMs),
                points: 200,
                rarity: 'Epic'
            }
        ];
        
        // Add some milestones
        this.milestones = this.achievements.filter(item => item.type === 'milestone');
        this.achievements = this.achievements.filter(item => item.type === 'badge');
    }

    updateStats() {
        const totalBadges = this.achievements.length;
        const totalMilestones = this.milestones.length;
        
        // Calculate active days (unique days with achievements)
        const achievementDates = [...this.achievements, ...this.milestones]
            .map(item => item.earnedAt.toDateString());
        const activeDays = new Set(achievementDates).size;
        
        // Calculate current streak (mock calculation)
        const currentStreak = this.calculateCurrentStreak();
        
        document.getElementById('total-badges').textContent = totalBadges;
        document.getElementById('total-milestones').textContent = totalMilestones;
        document.getElementById('active-days').textContent = activeDays;
        document.getElementById('current-streak').textContent = currentStreak;
    }

    calculateCurrentStreak() {
        // Mock streak calculation - in real app, this would come from API
        const streakBadge = this.achievements.find(badge => badge.id === 'streak-master');
        return streakBadge ? 30 : Math.floor(Math.random() * 15) + 1;
    }

    filterAndRenderTimeline() {
        // Combine achievements and milestones
        let allItems = [...this.achievements, ...this.milestones];
        
        // Apply filters
        switch (this.currentFilter) {
            case 'badges':
                allItems = this.achievements;
                break;
            case 'milestones':
                allItems = this.milestones;
                break;
            case 'recent':
                const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
                allItems = allItems.filter(item => item.earnedAt >= weekAgo);
                break;
        }
        
        // Apply sorting
        switch (this.currentSort) {
            case 'newest':
                allItems.sort((a, b) => b.earnedAt - a.earnedAt);
                break;
            case 'oldest':
                allItems.sort((a, b) => a.earnedAt - b.earnedAt);
                break;
            case 'category':
                allItems.sort((a, b) => a.category.localeCompare(b.category));
                break;
            case 'importance':
                allItems.sort((a, b) => (b.points || 0) - (a.points || 0));
                break;
        }
        
        this.filteredData = allItems;
        this.renderTimeline();
    }

    renderTimeline() {
        const timelineList = this.container.querySelector('.timeline-list');
        const emptyState = this.container.querySelector('.timeline-empty');
        
        if (this.filteredData.length === 0) {
            timelineList.style.display = 'none';
            emptyState.style.display = 'block';
            return;
        }
        
        timelineList.style.display = 'block';
        emptyState.style.display = 'none';
        
        // Group items by date for better organization
        const groupedItems = this.groupItemsByDate(this.filteredData);
        
        timelineList.innerHTML = '';
        
        Object.entries(groupedItems).forEach(([dateKey, items]) => {
            const dateGroup = this.createDateGroup(dateKey, items);
            timelineList.appendChild(dateGroup);
        });
    }

    groupItemsByDate(items) {
        const groups = {};
        
        items.forEach(item => {
            const dateKey = this.formatDateKey(item.earnedAt);
            if (!groups[dateKey]) {
                groups[dateKey] = [];
            }
            groups[dateKey].push(item);
        });
        
        return groups;
    }

    formatDateKey(date) {
        const now = new Date();
        const diffTime = now - date;
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) {
            return 'Today';
        } else if (diffDays === 1) {
            return 'Yesterday';
        } else if (diffDays < 7) {
            return `${diffDays} days ago`;
        } else if (diffDays < 30) {
            const weeks = Math.floor(diffDays / 7);
            return `${weeks} week${weeks > 1 ? 's' : ''} ago`;
        } else {
            return date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            });
        }
    }

    createDateGroup(dateKey, items) {
        const group = document.createElement('div');
        group.className = 'timeline-date-group';
        
        const dateHeader = document.createElement('div');
        dateHeader.className = 'timeline-date-header';
        dateHeader.innerHTML = `
            <div class="timeline-date-line"></div>
            <div class="timeline-date-label">${dateKey}</div>
            <div class="timeline-date-count">${items.length} achievement${items.length > 1 ? 's' : ''}</div>
        `;
        
        group.appendChild(dateHeader);
        
        items.forEach(item => {
            const timelineItem = this.createTimelineItem(item);
            group.appendChild(timelineItem);
        });
        
        return group;
    }

    createTimelineItem(item) {
        const timelineItem = document.createElement('div');
        timelineItem.className = `timeline-item ${item.type} ${item.rarity?.toLowerCase() || ''} ${item.significance || ''}`;
        timelineItem.dataset.itemId = item.id;
        
        const timeString = item.earnedAt.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        timelineItem.innerHTML = `
            <div class="timeline-marker">
                <div class="timeline-icon">${item.icon}</div>
                <div class="timeline-connector"></div>
            </div>
            <div class="timeline-content">
                <div class="timeline-item-header">
                    <div class="timeline-item-info">
                        <h3 class="timeline-item-title">${item.name}</h3>
                        <div class="timeline-item-meta">
                            <span class="timeline-category">${item.category}</span>
                            ${item.difficulty ? `<span class="timeline-difficulty ${item.difficulty.toLowerCase()}">${item.difficulty}</span>` : ''}
                            ${item.rarity ? `<span class="timeline-rarity ${item.rarity.toLowerCase()}">${item.rarity}</span>` : ''}
                            <span class="timeline-time">${timeString}</span>
                        </div>
                    </div>
                    <div class="timeline-points">+${item.points || 0}</div>
                </div>
                <p class="timeline-description">${item.description}</p>
                <div class="timeline-actions">
                    <button class="btn-view-details" data-action="details" data-item-id="${item.id}">
                        <span class="icon">👁️</span> View Details
                    </button>
                    <button class="btn-share-achievement" data-action="share" data-item-id="${item.id}">
                        <span class="icon">🔗</span> Share
                    </button>
                    ${item.type === 'badge' ? `
                        <button class="btn-view-progress" data-action="progress" data-item-id="${item.id}">
                            <span class="icon">📊</span> Progress
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
        
        return timelineItem;
    }

    attachEventListeners() {
        // Filter buttons
        this.container.addEventListener('click', (e) => {
            if (e.target.classList.contains('filter-btn')) {
                this.handleFilterChange(e.target);
            }
        });
        
        // Sort dropdown
        const sortSelect = this.container.querySelector('.sort-select');
        sortSelect.addEventListener('change', (e) => {
            this.currentSort = e.target.value;
            this.filterAndRenderTimeline();
        });
        
        // Refresh button
        const refreshBtn = this.container.querySelector('.timeline-refresh');
        refreshBtn.addEventListener('click', () => {
            this.refreshTimeline();
        });
        
        // Timeline item actions
        this.container.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            const itemId = e.target.dataset.itemId;
            
            if (action && itemId) {
                this.handleTimelineAction(action, itemId);
            }
        });
        
        // Start earning button
        this.container.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-start-earning')) {
                this.handleStartEarning();
            }
        });
    }

    handleFilterChange(button) {
        // Update active filter button
        this.container.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');
        
        // Update filter and re-render
        this.currentFilter = button.dataset.filter;
        this.filterAndRenderTimeline();
    }

    handleTimelineAction(action, itemId) {
        const item = [...this.achievements, ...this.milestones].find(i => i.id === itemId);
        if (!item) return;
        
        switch (action) {
            case 'details':
                this.showItemDetails(item);
                break;
            case 'share':
                this.shareAchievement(item);
                break;
            case 'progress':
                this.viewProgress(item);
                break;
        }
    }

    showItemDetails(item) {
        // Emit event for modal or detailed view
        window.dispatchEvent(new CustomEvent('showAchievementDetails', {
            detail: { achievement: item }
        }));
    }

    shareAchievement(item) {
        const shareText = `🏆 I just earned the "${item.name}" ${item.type}! ${item.description}`;
        
        if (navigator.share) {
            navigator.share({
                title: `${item.name} Achievement`,
                text: shareText,
                url: window.location.href
            });
        } else {
            navigator.clipboard.writeText(shareText).then(() => {
                this.showFeedback('Achievement shared to clipboard!');
            });
        }
    }

    viewProgress(item) {
        // Emit event for progress tracking
        window.dispatchEvent(new CustomEvent('viewBadgeProgress', {
            detail: { badge: item }
        }));
    }

    handleStartEarning() {
        // Emit event to guide user to earning badges
        window.dispatchEvent(new CustomEvent('startEarningBadges'));
    }

    async refreshTimeline() {
        const refreshBtn = this.container.querySelector('.timeline-refresh');
        const icon = refreshBtn.querySelector('.icon');
        
        // Add spinning animation
        icon.style.animation = 'spin 1s linear infinite';
        
        try {
            await this.loadData();
            this.showFeedback('Timeline refreshed!');
        } catch (error) {
            this.showFeedback('Failed to refresh timeline', 'error');
        } finally {
            icon.style.animation = '';
        }
    }

    showLoading(show) {
        const loading = this.container.querySelector('.timeline-loading');
        const content = this.container.querySelector('.timeline-list');
        
        if (show) {
            loading.style.display = 'flex';
            content.style.display = 'none';
        } else {
            loading.style.display = 'none';
            content.style.display = 'block';
        }
    }

    showFeedback(message, type = 'success') {
        // Create temporary feedback element
        const feedback = document.createElement('div');
        feedback.className = `timeline-feedback ${type}`;
        feedback.textContent = message;
        
        this.container.appendChild(feedback);
        
        setTimeout(() => {
            feedback.remove();
        }, 3000);
    }

    // Removed injectStyles - using existing design system

    // Public API
    addAchievement(achievement) {
        if (achievement.type === 'milestone') {
            this.milestones.push(achievement);
        } else {
            this.achievements.push(achievement);
        }
        this.updateStats();
        this.filterAndRenderTimeline();
    }

    refresh() {
        this.loadData();
    }

    setFilter(filter) {
        this.currentFilter = filter;
        this.filterAndRenderTimeline();
        
        // Update UI
        this.container.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === filter);
        });
    }

    destroy() {
        const styles = document.getElementById('achievement-timeline-styles');
        if (styles) {
            styles.remove();
        }
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AchievementTimeline;
}

// Global helper function
window.createAchievementTimeline = function(container) {
    return new AchievementTimeline(container);
};