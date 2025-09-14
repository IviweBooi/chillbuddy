// Profile Modal JavaScript
class ProfileModal {
    constructor() {
        this.modal = null;
        this.isOpen = false;
        this.userData = null;
        this.badgeData = null;
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupModal());
        } else {
            this.setupModal();
        }
    }

    setupModal() {
        this.modal = document.getElementById('profileModal');
        if (!this.modal) {
            console.warn('Profile modal not found in DOM');
            return;
        }

        // Setup event listeners
        this.setupEventListeners();
        
        // Load initial data
        this.loadUserData();
    }

    setupEventListeners() {
        // Close modal when clicking overlay
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });

        // Close modal with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });

        // Badge hover tooltips
        this.setupBadgeTooltips();
    }

    setupBadgeTooltips() {
        const badgeItems = document.querySelectorAll('.badge-item');
        badgeItems.forEach(badge => {
            badge.addEventListener('mouseenter', (e) => this.showBadgeTooltip(e));
            badge.addEventListener('mouseleave', () => this.hideBadgeTooltip());
        });
    }

    showBadgeTooltip(e) {
        const badge = e.currentTarget;
        const badgeType = badge.dataset.badge;
        const isEarned = badge.classList.contains('earned');
        
        let tooltipText = '';
        if (isEarned) {
            tooltipText = `Click to view details about ${badge.querySelector('.badge-name').textContent}`;
        } else {
            const progressText = badge.querySelector('.progress-text');
            tooltipText = progressText ? progressText.textContent : 'Badge locked';
        }

        this.createTooltip(tooltipText, e.pageX, e.pageY);
    }

    createTooltip(text, x, y) {
        this.hideBadgeTooltip(); // Remove any existing tooltip
        
        const tooltip = document.createElement('div');
        tooltip.className = 'badge-tooltip show';
        tooltip.textContent = text;
        tooltip.style.left = x + 'px';
        tooltip.style.top = (y - 40) + 'px';
        
        document.body.appendChild(tooltip);
        this.currentTooltip = tooltip;
    }

    hideBadgeTooltip() {
        if (this.currentTooltip) {
            this.currentTooltip.remove();
            this.currentTooltip = null;
        }
    }

    async loadUserData() {
        try {
            // Simulate API call - replace with actual backend endpoint
            const response = await fetch('/api/user/profile');
            if (response.ok) {
                this.userData = await response.json();
            } else {
                // Use mock data if API not available
                this.userData = this.getMockUserData();
            }
            
            this.updateUserInterface();
        } catch (error) {
            console.log('Using mock data due to API error:', error.message);
            this.userData = this.getMockUserData();
            this.updateUserInterface();
        }
    }

    getMockUserData() {
        return {
            username: 'ChillBuddy User',
            status: 'Mental Health Champion',
            joinDate: 'January 2024',
            stats: {
                streakCount: 7,
                moodEntries: 42,
                copingStrategies: 15,
                resourcesExplored: 28
            },
            badges: {
                earned: [
                    {
                        id: 'first-steps',
                        name: 'First Steps',
                        description: 'Started your mental health journey',
                        earnedDate: '2024-01-15',
                        icon: 'first-steps.svg'
                    },
                    {
                        id: 'streak-master',
                        name: 'Streak Master',
                        description: 'Maintained a 7-day check-in streak',
                        earnedDate: '2024-01-22',
                        icon: 'streak-master.svg'
                    },
                    {
                        id: 'mood-tracker',
                        name: 'Mood Tracker',
                        description: 'Logged 30 mood entries',
                        earnedDate: '2024-02-01',
                        icon: 'mood-tracker.svg'
                    },
                    {
                        id: 'coping-champion',
                        name: 'Coping Champion',
                        description: 'Mastered 10 coping strategies',
                        earnedDate: '2024-02-08',
                        icon: 'coping-champion.svg'
                    }
                ],
                locked: [
                    {
                        id: 'resource-explorer',
                        name: 'Resource Explorer',
                        description: 'Explore 25 mental health resources',
                        progress: { current: 18, total: 25 },
                        icon: 'resource-explorer.svg'
                    },
                    {
                        id: 'challenge-crusher',
                        name: 'Challenge Crusher',
                        description: 'Complete 5 mental health challenges',
                        progress: { current: 2, total: 5 },
                        icon: 'challenge-crusher.svg'
                    },
                    {
                        id: 'monthly-milestone',
                        name: 'Monthly Milestone',
                        description: 'Maintain consistent activity for 30 days',
                        progress: { current: 22, total: 30 },
                        icon: 'monthly-milestone.svg'
                    },
                    {
                        id: 'crisis-survivor',
                        name: 'Crisis Survivor',
                        description: 'Successfully navigate a mental health crisis',
                        progress: null,
                        icon: 'crisis-survivor.svg'
                    }
                ]
            }
        };
    }

    updateUserInterface() {
        if (!this.userData) return;

        // Update user info
        this.updateElement('profileUsername', this.userData.username);
        this.updateElement('profileStatus', this.userData.status);
        this.updateElement('profileJoinDate', `Member since ${this.userData.joinDate}`);

        // Update stats
        this.updateElement('streakCount', this.userData.stats.streakCount);
        this.updateElement('moodEntries', this.userData.stats.moodEntries);
        this.updateElement('copingStrategies', this.userData.stats.copingStrategies);
        this.updateElement('resourcesExplored', this.userData.stats.resourcesExplored);

        // Update badge count
        const earnedCount = this.userData.badges.earned.length;
        const totalCount = earnedCount + this.userData.badges.locked.length;
        this.updateElement('earnedBadgeCount', earnedCount);
        document.querySelector('.total-count').textContent = `/ ${totalCount} earned`;

        // Update profile badge (show highest earned badge)
        this.updateProfileBadge();
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    updateProfileBadge() {
        const profileBadge = document.getElementById('profileAchievementBadge');
        if (!profileBadge || !this.userData.badges.earned.length) return;

        // Show the most recently earned badge
        const latestBadge = this.userData.badges.earned[this.userData.badges.earned.length - 1];
        
        // Load the SVG for the badge
        this.loadBadgeSVG(latestBadge.icon)
            .then(svgContent => {
                profileBadge.innerHTML = svgContent;
                profileBadge.title = `Latest Achievement: ${latestBadge.name}`;
            })
            .catch(error => {
                console.warn('Could not load badge SVG:', error);
                // Fallback to a simple colored circle
                profileBadge.innerHTML = '<div style="width: 100%; height: 100%; background: #10b981; border-radius: 50%;"></div>';
            });
    }

    async loadBadgeSVG(filename) {
        try {
            const response = await fetch(`assets/badges/${filename}`);
            if (response.ok) {
                return await response.text();
            }
            throw new Error('SVG not found');
        } catch (error) {
            throw error;
        }
    }

    open() {
        if (!this.modal) return;
        
        this.isOpen = true;
        this.modal.style.display = 'flex';
        
        // Trigger animation
        requestAnimationFrame(() => {
            this.modal.classList.add('show');
        });
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        // Load fresh data when opening
        this.loadUserData();
    }

    close() {
        if (!this.modal) return;
        
        this.isOpen = false;
        this.modal.classList.remove('show');
        
        // Hide modal after animation
        setTimeout(() => {
            this.modal.style.display = 'none';
        }, 300);
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Hide any tooltips
        this.hideBadgeTooltip();
    }

    // Method to show achievement notification
    showAchievementNotification(badgeData) {
        const notification = document.createElement('div');
        notification.className = 'achievement-notification';
        notification.innerHTML = `
            <div class="achievement-content">
                <div class="achievement-icon">
                    <svg width="48" height="48" viewBox="0 0 48 48">
                        <circle cx="24" cy="24" r="24" fill="#10b981"/>
                        <path d="M20 24L22 26L28 20" stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div class="achievement-text">
                    <h4>Achievement Unlocked!</h4>
                    <p>${badgeData.name}</p>
                    <span>${badgeData.description}</span>
                </div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Show notification
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
}

// Global functions for HTML onclick handlers
function openProfileModal() {
    if (window.profileModal) {
        window.profileModal.open();
    }
}

function closeProfileModal() {
    if (window.profileModal) {
        window.profileModal.close();
    }
}

function viewAchievementHistory() {
    // TODO: Implement achievement history view
    console.log('Opening achievement history...');
    alert('Achievement history feature coming soon!');
}

function shareBadges() {
    // TODO: Implement badge sharing
    console.log('Sharing badges...');
    
    if (navigator.share) {
        navigator.share({
            title: 'My ChillBuddy Achievements',
            text: 'Check out my mental health journey achievements on ChillBuddy!',
            url: window.location.href
        }).catch(console.error);
    } else {
        // Fallback for browsers without Web Share API
        const shareText = 'Check out my mental health journey achievements on ChillBuddy!';
        navigator.clipboard.writeText(shareText + ' ' + window.location.href)
            .then(() => alert('Achievement link copied to clipboard!'))
            .catch(() => alert('Sharing feature not available in this browser'));
    }
}

function signOut() {
    // Confirm sign out action
    if (confirm('Are you sure you want to sign out?')) {
        console.log('Signing out user...');
        
        // Clear user data from localStorage
        localStorage.removeItem('userProfile');
        localStorage.removeItem('chatHistory');
        localStorage.removeItem('userPreferences');
        
        // Close the profile modal
        closeProfileModal();
        
        // Redirect to login page or refresh
        window.location.href = '/login.html';
        
        // Show confirmation message
        alert('You have been signed out successfully.');
    }
}

function deleteAccount() {
    // Double confirmation for account deletion
    const firstConfirm = confirm('Are you sure you want to delete your account? This action cannot be undone.');
    
    if (firstConfirm) {
        const secondConfirm = confirm('This will permanently delete all your data, progress, and achievements. Type "DELETE" to confirm.');
        
        if (secondConfirm) {
            const userInput = prompt('Please type "DELETE" to confirm account deletion:');
            
            if (userInput === 'DELETE') {
                console.log('Deleting user account...');
                
                // Clear all user data
                localStorage.clear();
                
                // Close the profile modal
                closeProfileModal();
                
                // In a real app, you would make an API call to delete the account
                // For now, just redirect to a goodbye page or login
                alert('Your account has been deleted. We\'re sorry to see you go.');
                window.location.href = '/index.html';
            } else {
                alert('Account deletion cancelled. Please type "DELETE" exactly to confirm.');
            }
        }
    }
}

// Initialize the profile modal when the script loads
window.profileModal = new ProfileModal();

// CSS for achievement notifications (injected via JavaScript)
const achievementNotificationCSS = `
.achievement-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    border-left: 4px solid #10b981;
    padding: 16px;
    max-width: 350px;
    z-index: 3000;
    transform: translateX(400px);
    transition: transform 0.3s ease;
}

.achievement-notification.show {
    transform: translateX(0);
}

.achievement-content {
    display: flex;
    align-items: center;
    gap: 12px;
}

.achievement-icon {
    flex-shrink: 0;
}

.achievement-text h4 {
    margin: 0 0 4px 0;
    font-size: 16px;
    font-weight: 600;
    color: #1f2937;
}

.achievement-text p {
    margin: 0 0 2px 0;
    font-size: 14px;
    font-weight: 500;
    color: #10b981;
}

.achievement-text span {
    font-size: 12px;
    color: #6b7280;
}

@media (max-width: 480px) {
    .achievement-notification {
        right: 10px;
        left: 10px;
        max-width: none;
        transform: translateY(-100px);
    }
    
    .achievement-notification.show {
        transform: translateY(0);
    }
}
`;

// Inject the CSS
const style = document.createElement('style');
style.textContent = achievementNotificationCSS;
document.head.appendChild(style);

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProfileModal;
}