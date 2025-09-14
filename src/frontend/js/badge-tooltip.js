/**
 * Badge Tooltip System
 * Provides detailed hover information for each badge type
 */

class BadgeTooltipSystem {
    constructor() {
        this.tooltip = null;
        this.currentBadge = null;
        this.showDelay = 300;
        this.hideDelay = 100;
        this.showTimeout = null;
        this.hideTimeout = null;
        this.isVisible = false;
        
        this.init();
    }

    init() {
        this.createTooltip();
        this.attachEventListeners();
        // Removed injectStyles - using existing design system
    }

    createTooltip() {
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'badge-tooltip';
        this.tooltip.innerHTML = `
            <div class="tooltip-arrow"></div>
            <div class="tooltip-content">
                <div class="tooltip-header">
                    <div class="tooltip-badge-icon"></div>
                    <div class="tooltip-badge-info">
                        <h3 class="tooltip-badge-name"></h3>
                        <div class="tooltip-badge-meta">
                            <span class="tooltip-category"></span>
                            <span class="tooltip-difficulty"></span>
                        </div>
                    </div>
                    <div class="tooltip-status"></div>
                </div>
                <div class="tooltip-body">
                    <p class="tooltip-description"></p>
                    <div class="tooltip-requirements">
                        <h4>Requirements:</h4>
                        <ul class="requirements-list"></ul>
                    </div>
                    <div class="tooltip-progress">
                        <div class="progress-header">
                            <span class="progress-label">Progress</span>
                            <span class="progress-percentage">0%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill"></div>
                        </div>
                        <div class="progress-details"></div>
                    </div>
                    <div class="tooltip-rewards">
                        <h4>Rewards:</h4>
                        <div class="rewards-list"></div>
                    </div>
                    <div class="tooltip-stats">
                        <div class="stat-item">
                            <span class="stat-label">Earned by</span>
                            <span class="stat-value earned-count">0 users</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Rarity</span>
                            <span class="stat-value rarity">Common</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Points</span>
                            <span class="stat-value points">0</span>
                        </div>
                    </div>
                    <div class="tooltip-tips">
                        <h4>💡 Tips:</h4>
                        <ul class="tips-list"></ul>
                    </div>
                </div>
                <div class="tooltip-footer">
                    <div class="tooltip-actions">
                        <button class="btn-track" data-action="track">📊 Track Progress</button>
                        <button class="btn-share" data-action="share">🔗 Share</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(this.tooltip);
    }

    attachEventListeners() {
        // Handle badge hover events
        document.addEventListener('mouseenter', (e) => {
            const badgeElement = e.target.closest('[data-badge-id], .badge, .badge-item, .achievement-badge');
            if (badgeElement) {
                this.handleBadgeHover(badgeElement, e);
            }
        }, true);

        document.addEventListener('mouseleave', (e) => {
            const badgeElement = e.target.closest('[data-badge-id], .badge, .badge-item, .achievement-badge');
            if (badgeElement) {
                this.handleBadgeLeave(badgeElement, e);
            }
        }, true);

        // Handle tooltip hover to keep it visible
        this.tooltip.addEventListener('mouseenter', () => {
            this.clearHideTimeout();
        });

        this.tooltip.addEventListener('mouseleave', () => {
            this.hideTooltip();
        });

        // Handle tooltip actions
        this.tooltip.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            if (action && this.currentBadge) {
                this.handleTooltipAction(action, this.currentBadge);
            }
        });

        // Hide tooltip on scroll or resize
        window.addEventListener('scroll', () => this.hideTooltip(), { passive: true });
        window.addEventListener('resize', () => this.hideTooltip());
    }

    handleBadgeHover(element, event) {
        this.clearTimeouts();
        
        const badgeData = this.extractBadgeData(element);
        if (!badgeData) return;

        this.showTimeout = setTimeout(() => {
            this.showTooltip(badgeData, element, event);
        }, this.showDelay);
    }

    handleBadgeLeave(element, event) {
        this.clearShowTimeout();
        
        // Check if mouse is moving to tooltip
        const rect = this.tooltip.getBoundingClientRect();
        const mouseX = event.clientX;
        const mouseY = event.clientY;
        
        const isMovingToTooltip = (
            mouseX >= rect.left - 10 && mouseX <= rect.right + 10 &&
            mouseY >= rect.top - 10 && mouseY <= rect.bottom + 10
        );

        if (!isMovingToTooltip) {
            this.hideTimeout = setTimeout(() => {
                this.hideTooltip();
            }, this.hideDelay);
        }
    }

    extractBadgeData(element) {
        // Try to get badge ID from various attributes
        const badgeId = element.dataset.badgeId || 
                       element.dataset.badge || 
                       element.getAttribute('data-badge-type') ||
                       element.className.match(/badge-([\w-]+)/)?.[1];

        if (!badgeId) return null;

        // Get badge data from various sources
        let badgeData = this.getBadgeDataFromAPI(badgeId) || 
                       this.getBadgeDataFromElement(element) ||
                       this.getDefaultBadgeData(badgeId);

        return badgeData;
    }

    getBadgeDataFromAPI(badgeId) {
        // Try to get from global badge data if available
        if (window.badgeData && window.badgeData[badgeId]) {
            return window.badgeData[badgeId];
        }
        return null;
    }

    getBadgeDataFromElement(element) {
        // Extract data from element attributes and content
        const title = element.title || element.dataset.title || element.querySelector('.badge-name')?.textContent;
        const description = element.dataset.description || element.querySelector('.badge-description')?.textContent;
        const category = element.dataset.category || 'General';
        const difficulty = element.dataset.difficulty || 'Medium';
        const earned = element.classList.contains('earned') || element.dataset.earned === 'true';
        
        return {
            id: element.dataset.badgeId || 'unknown',
            name: title || 'Unknown Badge',
            description: description || 'No description available',
            category: category,
            difficulty: difficulty,
            earned: earned,
            progress: parseInt(element.dataset.progress) || 0,
            requirements: this.parseRequirements(element.dataset.requirements),
            rewards: this.parseRewards(element.dataset.rewards),
            tips: this.parseTips(element.dataset.tips)
        };
    }

    getDefaultBadgeData(badgeId) {
        // Fallback badge data based on common badge types
        const defaultBadges = {
            'first-message': {
                name: 'First Message',
                description: 'Send your first message in the chat',
                category: 'Getting Started',
                difficulty: 'Easy',
                requirements: ['Send 1 message'],
                rewards: ['10 points', 'Welcome badge'],
                tips: ['Just start chatting to earn this badge!'],
                rarity: 'Common',
                points: 10
            },
            'conversation-starter': {
                name: 'Conversation Starter',
                description: 'Start 10 different conversations',
                category: 'Social',
                difficulty: 'Medium',
                requirements: ['Start 10 conversations'],
                rewards: ['50 points', 'Social butterfly status'],
                tips: ['Ask questions to start engaging conversations'],
                rarity: 'Uncommon',
                points: 50
            },
            'night-owl': {
                name: 'Night Owl',
                description: 'Chat between midnight and 6 AM',
                category: 'Time-based',
                difficulty: 'Easy',
                requirements: ['Send messages between 12 AM - 6 AM'],
                rewards: ['25 points', 'Night owl title'],
                tips: ['Stay up late or wake up early to earn this!'],
                rarity: 'Common',
                points: 25
            },
            'emoji-enthusiast': {
                name: 'Emoji Enthusiast',
                description: 'Use 50 different emojis in your messages',
                category: 'Expression',
                difficulty: 'Medium',
                requirements: ['Use 50 unique emojis'],
                rewards: ['40 points', 'Emoji master badge'],
                tips: ['Express yourself with a variety of emojis!'],
                rarity: 'Uncommon',
                points: 40
            },
            'helpful-friend': {
                name: 'Helpful Friend',
                description: 'Receive 25 positive reactions to your messages',
                category: 'Community',
                difficulty: 'Hard',
                requirements: ['Get 25 positive reactions'],
                rewards: ['100 points', 'Helper status'],
                tips: ['Be helpful and supportive in conversations'],
                rarity: 'Rare',
                points: 100
            },
            'streak-master': {
                name: 'Streak Master',
                description: 'Maintain a 30-day chat streak',
                category: 'Consistency',
                difficulty: 'Expert',
                requirements: ['Chat for 30 consecutive days'],
                rewards: ['200 points', 'Dedication badge'],
                tips: ['Set daily reminders to maintain your streak'],
                rarity: 'Epic',
                points: 200
            },
            'wordsmith': {
                name: 'Wordsmith',
                description: 'Send messages totaling 10,000 words',
                category: 'Communication',
                difficulty: 'Hard',
                requirements: ['Send 10,000 total words'],
                rewards: ['150 points', 'Eloquent speaker title'],
                tips: ['Share detailed thoughts and stories'],
                rarity: 'Rare',
                points: 150
            },
            'early-bird': {
                name: 'Early Bird',
                description: 'Chat between 5 AM and 8 AM',
                category: 'Time-based',
                difficulty: 'Easy',
                requirements: ['Send messages between 5 AM - 8 AM'],
                rewards: ['25 points', 'Morning person badge'],
                tips: ['Start your day with a chat!'],
                rarity: 'Common',
                points: 25
            }
        };

        return defaultBadges[badgeId] || {
            name: badgeId.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
            description: 'A special achievement badge',
            category: 'General',
            difficulty: 'Medium',
            requirements: ['Complete specific actions'],
            rewards: ['Points and recognition'],
            tips: ['Keep engaging to unlock this badge!'],
            rarity: 'Common',
            points: 25
        };
    }

    parseRequirements(requirementsStr) {
        if (!requirementsStr) return [];
        try {
            return JSON.parse(requirementsStr);
        } catch {
            return requirementsStr.split(',').map(r => r.trim());
        }
    }

    parseRewards(rewardsStr) {
        if (!rewardsStr) return [];
        try {
            return JSON.parse(rewardsStr);
        } catch {
            return rewardsStr.split(',').map(r => r.trim());
        }
    }

    parseTips(tipsStr) {
        if (!tipsStr) return [];
        try {
            return JSON.parse(tipsStr);
        } catch {
            return tipsStr.split(',').map(t => t.trim());
        }
    }

    showTooltip(badgeData, element, event) {
        this.currentBadge = badgeData;
        this.populateTooltip(badgeData);
        this.positionTooltip(element, event);
        
        this.tooltip.classList.add('visible');
        this.isVisible = true;
        
        // Trigger entrance animation
        requestAnimationFrame(() => {
            this.tooltip.classList.add('animate-in');
        });
    }

    populateTooltip(badgeData) {
        // Header
        const badgeIcon = this.tooltip.querySelector('.tooltip-badge-icon');
        badgeIcon.innerHTML = this.getBadgeIcon(badgeData);
        
        this.tooltip.querySelector('.tooltip-badge-name').textContent = badgeData.name;
        this.tooltip.querySelector('.tooltip-category').textContent = badgeData.category;
        this.tooltip.querySelector('.tooltip-difficulty').textContent = badgeData.difficulty;
        this.tooltip.querySelector('.tooltip-difficulty').className = `tooltip-difficulty ${badgeData.difficulty.toLowerCase()}`;
        
        // Status
        const status = this.tooltip.querySelector('.tooltip-status');
        if (badgeData.earned) {
            status.innerHTML = '<span class="status-earned">✅ Earned</span>';
        } else {
            status.innerHTML = '<span class="status-locked">🔒 Locked</span>';
        }
        
        // Description
        this.tooltip.querySelector('.tooltip-description').textContent = badgeData.description;
        
        // Requirements
        const requirementsList = this.tooltip.querySelector('.requirements-list');
        requirementsList.innerHTML = '';
        (badgeData.requirements || []).forEach(req => {
            const li = document.createElement('li');
            li.textContent = req;
            requirementsList.appendChild(li);
        });
        
        // Progress
        const progress = badgeData.progress || 0;
        this.tooltip.querySelector('.progress-percentage').textContent = `${progress}%`;
        this.tooltip.querySelector('.progress-fill').style.width = `${progress}%`;
        
        const progressDetails = this.tooltip.querySelector('.progress-details');
        if (badgeData.progressDetails) {
            progressDetails.textContent = badgeData.progressDetails;
            progressDetails.style.display = 'block';
        } else {
            progressDetails.style.display = 'none';
        }
        
        // Rewards
        const rewardsList = this.tooltip.querySelector('.rewards-list');
        rewardsList.innerHTML = '';
        (badgeData.rewards || []).forEach(reward => {
            const span = document.createElement('span');
            span.className = 'reward-item';
            span.textContent = reward;
            rewardsList.appendChild(span);
        });
        
        // Stats
        this.tooltip.querySelector('.earned-count').textContent = `${badgeData.earnedBy || 0} users`;
        this.tooltip.querySelector('.rarity').textContent = badgeData.rarity || 'Common';
        this.tooltip.querySelector('.rarity').className = `stat-value rarity ${(badgeData.rarity || 'common').toLowerCase()}`;
        this.tooltip.querySelector('.points').textContent = badgeData.points || 0;
        
        // Tips
        const tipsList = this.tooltip.querySelector('.tips-list');
        tipsList.innerHTML = '';
        (badgeData.tips || []).forEach(tip => {
            const li = document.createElement('li');
            li.textContent = tip;
            tipsList.appendChild(li);
        });
        
        // Update tooltip class based on status
        this.tooltip.className = `badge-tooltip ${badgeData.earned ? 'earned' : 'locked'} ${badgeData.difficulty.toLowerCase()}`;
    }

    getBadgeIcon(badgeData) {
        // Return appropriate SVG or emoji based on badge type
        const iconMap = {
            'first-message': '💬',
            'conversation-starter': '🗣️',
            'night-owl': '🦉',
            'emoji-enthusiast': '😀',
            'helpful-friend': '🤝',
            'streak-master': '🔥',
            'wordsmith': '✍️',
            'early-bird': '🐦'
        };
        
        return iconMap[badgeData.id] || '🏆';
    }

    positionTooltip(element, event) {
        const rect = element.getBoundingClientRect();
        const tooltipRect = this.tooltip.getBoundingClientRect();
        const viewport = {
            width: window.innerWidth,
            height: window.innerHeight
        };
        
        let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
        let top = rect.top - tooltipRect.height - 10;
        
        // Adjust horizontal position if tooltip goes off screen
        if (left < 10) {
            left = 10;
        } else if (left + tooltipRect.width > viewport.width - 10) {
            left = viewport.width - tooltipRect.width - 10;
        }
        
        // Adjust vertical position if tooltip goes off screen
        if (top < 10) {
            top = rect.bottom + 10;
            this.tooltip.classList.add('below');
        } else {
            this.tooltip.classList.remove('below');
        }
        
        this.tooltip.style.left = `${left}px`;
        this.tooltip.style.top = `${top}px`;
        
        // Position arrow
        const arrow = this.tooltip.querySelector('.tooltip-arrow');
        const arrowLeft = rect.left + (rect.width / 2) - left;
        arrow.style.left = `${Math.max(20, Math.min(arrowLeft, tooltipRect.width - 20))}px`;
    }

    hideTooltip() {
        if (!this.isVisible) return;
        
        this.tooltip.classList.remove('animate-in');
        this.tooltip.classList.add('animate-out');
        
        setTimeout(() => {
            this.tooltip.classList.remove('visible', 'animate-out', 'below');
            this.isVisible = false;
            this.currentBadge = null;
        }, 200);
    }

    handleTooltipAction(action, badgeData) {
        switch (action) {
            case 'track':
                this.trackBadgeProgress(badgeData);
                break;
            case 'share':
                this.shareBadge(badgeData);
                break;
        }
    }

    trackBadgeProgress(badgeData) {
        // Add to tracked badges in localStorage
        const trackedBadges = JSON.parse(localStorage.getItem('trackedBadges') || '[]');
        if (!trackedBadges.includes(badgeData.id)) {
            trackedBadges.push(badgeData.id);
            localStorage.setItem('trackedBadges', JSON.stringify(trackedBadges));
        }
        
        // Emit event for progress tracking
        window.dispatchEvent(new CustomEvent('trackBadgeProgress', {
            detail: { badge: badgeData }
        }));
        
        // Update progress dashboard if available
        if (window.progressDashboard) {
            window.progressDashboard.trackProgress(badgeData.id);
        }
        
        // Show feedback
        this.showActionFeedback('📊 Now tracking progress for this badge!');
        this.hideTooltip();
    }

    shareBadge(badgeData) {
        // Create detailed shareable content
        const shareText = `🏆 ${badgeData.name} Badge\n\n${badgeData.description}\n\nCategory: ${badgeData.category}\nDifficulty: ${badgeData.difficulty}\nProgress: ${badgeData.progress || 0}%\n\n${badgeData.earned ? '✅ Earned!' : '🔒 In Progress'}`;
        
        if (navigator.share) {
            navigator.share({
                title: `${badgeData.name} Badge - ChillBuddy`,
                text: shareText,
                url: window.location.href
            }).then(() => {
                this.showActionFeedback('🔗 Badge shared successfully!');
            }).catch(() => {
                this.fallbackShare(shareText);
            });
        } else {
            this.fallbackShare(shareText);
        }
    }
    
    fallbackShare(shareText) {
        // Try clipboard first
        if (navigator.clipboard) {
            navigator.clipboard.writeText(shareText).then(() => {
                this.showActionFeedback('🔗 Badge info copied to clipboard!');
            }).catch(() => {
                this.showShareModal(shareText);
            });
        } else {
            this.showShareModal(shareText);
        }
    }
    
    showShareModal(shareText) {
        // Create share modal
        const modal = document.createElement('div');
        modal.className = 'share-modal-overlay';
        modal.innerHTML = `
            <div class="share-modal">
                <div class="share-modal-header">
                    <h3>Share Badge</h3>
                    <button class="close-btn" onclick="this.closest('.share-modal-overlay').remove()">&times;</button>
                </div>
                <div class="share-modal-content">
                    <textarea readonly class="share-text">${shareText}</textarea>
                    <div class="share-actions">
                        <button class="copy-btn" onclick="this.previousElementSibling.select(); document.execCommand('copy'); this.textContent='Copied!'">Copy Text</button>
                        <button class="close-btn" onclick="this.closest('.share-modal-overlay').remove()">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.querySelector('.share-text').select();
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (modal.parentNode) {
                modal.remove();
            }
        }, 10000);
    }

    showActionFeedback(message) {
        // Create temporary feedback element
        const feedback = document.createElement('div');
        feedback.className = 'tooltip-feedback';
        feedback.textContent = message;
        
        this.tooltip.appendChild(feedback);
        
        setTimeout(() => {
            feedback.remove();
        }, 2000);
    }

    clearTimeouts() {
        this.clearShowTimeout();
        this.clearHideTimeout();
    }

    clearShowTimeout() {
        if (this.showTimeout) {
            clearTimeout(this.showTimeout);
            this.showTimeout = null;
        }
    }

    clearHideTimeout() {
        if (this.hideTimeout) {
            clearTimeout(this.hideTimeout);
            this.hideTimeout = null;
        }
    }

    // Removed injectStyles method - using existing design system

    // Public API
    updateBadgeData(badgeId, data) {
        if (!window.badgeData) window.badgeData = {};
        window.badgeData[badgeId] = data;
    }

    destroy() {
        this.clearTimeouts();
        if (this.tooltip) {
            this.tooltip.remove();
        }
        
        const styles = document.getElementById('badge-tooltip-styles');
        if (styles) {
            styles.remove();
        }
    }
}

// Initialize tooltip system when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.badgeTooltipSystem = new BadgeTooltipSystem();
    });
} else {
    window.badgeTooltipSystem = new BadgeTooltipSystem();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BadgeTooltipSystem;
}

// Global helper functions
window.updateBadgeTooltipData = function(badgeId, data) {
    if (window.badgeTooltipSystem) {
        window.badgeTooltipSystem.updateBadgeData(badgeId, data);
    }
};

window.showBadgeTooltip = function(element, badgeData) {
    if (window.badgeTooltipSystem && badgeData) {
        window.badgeTooltipSystem.showTooltip(badgeData, element, { clientX: 0, clientY: 0 });
    }
};

window.hideBadgeTooltip = function() {
    if (window.badgeTooltipSystem) {
        window.badgeTooltipSystem.hideTooltip();
    }
};