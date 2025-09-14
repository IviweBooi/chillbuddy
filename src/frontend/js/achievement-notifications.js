// Achievement Notification System
class AchievementNotificationSystem {
    constructor(options = {}) {
        this.options = {
            position: 'top-right', // 'top-right', 'top-left', 'bottom-right', 'bottom-left', 'center'
            duration: 5000, // Duration in milliseconds
            maxNotifications: 3, // Maximum number of notifications to show at once
            enableSound: true,
            enableConfetti: true,
            enableVibration: true,
            ...options
        };
        
        this.notifications = [];
        this.container = null;
        this.soundEnabled = this.options.enableSound && 'Audio' in window;
        
        this.init();
    }

    init() {
        this.createContainer();
        // Removed injectStyles - using existing design system
        
        // Listen for badge earned events
        document.addEventListener('badgeEarned', (event) => {
            this.showNotification(event.detail.badge);
        });
        
        // Listen for achievement unlocked events
        document.addEventListener('achievementUnlocked', (event) => {
            this.showAchievementNotification(event.detail);
        });
    }

    createContainer() {
        this.container = document.createElement('div');
        this.container.className = `achievement-notifications-container ${this.options.position}`;
        this.container.setAttribute('aria-live', 'polite');
        this.container.setAttribute('aria-label', 'Achievement notifications');
        document.body.appendChild(this.container);
    }

    // Removed injectStyles method - using existing design system

    showNotification(badge, type = 'badge-earned') {
        // Remove oldest notification if we've reached the limit
        if (this.notifications.length >= this.options.maxNotifications) {
            this.removeNotification(this.notifications[0]);
        }

        const notification = this.createNotification(badge, type);
        this.notifications.push(notification);
        this.container.appendChild(notification);

        // Trigger entrance animation
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });

        // Play sound effect
        if (this.soundEnabled) {
            this.playNotificationSound(type);
        }

        // Trigger haptic feedback
        if (this.options.enableVibration && 'vibrate' in navigator) {
            navigator.vibrate([100, 50, 100]);
        }

        // Show confetti for special achievements
        if (this.options.enableConfetti && (type === 'special' || badge.difficulty === 'expert')) {
            this.showConfetti();
        }

        // Auto-remove after duration
        setTimeout(() => {
            this.removeNotification(notification);
        }, this.options.duration);

        // Dispatch custom event
        document.dispatchEvent(new CustomEvent('achievementNotificationShown', {
            detail: { badge, type, notification }
        }));

        return notification;
    }

    createNotification(badge, type) {
        const notification = document.createElement('div');
        notification.className = `achievement-notification ${type}`;
        notification.setAttribute('role', 'alert');
        notification.setAttribute('aria-live', 'assertive');

        const icon = this.getNotificationIcon(badge, type);
        const title = this.getNotificationTitle(badge, type);
        const subtitle = this.getNotificationSubtitle(badge, type);

        notification.innerHTML = `
            <button class="notification-close" aria-label="Close notification">&times;</button>
            <div class="notification-header">
                <div class="notification-icon">${icon}</div>
                <div class="notification-content">
                    <h4 class="notification-title">${title}</h4>
                    <p class="notification-subtitle">${subtitle}</p>
                </div>
            </div>
            ${badge ? this.createBadgePreview(badge) : ''}
            <div class="notification-progress" style="animation-duration: ${this.options.duration}ms;"></div>
        `;

        // Add click handler to close
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.removeNotification(notification);
        });

        // Add click handler to view badge details
        notification.addEventListener('click', () => {
            if (badge && window.profileModal) {
                window.profileModal.showBadgeDetails(badge.id);
            }
            this.removeNotification(notification);
        });

        return notification;
    }

    createBadgePreview(badge) {
        return `
            <div class="notification-badge-preview">
                <div class="badge-mini-icon" style="background-color: ${badge.color || '#3b82f6'}">
                    ${badge.name ? badge.name.charAt(0) : '🏆'}
                </div>
                <div class="badge-mini-info">
                    <p class="badge-mini-name">${badge.name}</p>
                    <p class="badge-mini-category">${badge.category || 'achievement'}</p>
                </div>
            </div>
        `;
    }

    getNotificationIcon(badge, type) {
        const icons = {
            'badge-earned': '🏆',
            'milestone': '🎯',
            'special': '⭐',
            'streak': '🔥',
            'level-up': '📈',
            'first-time': '🎉'
        };
        
        return icons[type] || '🏆';
    }

    getNotificationTitle(badge, type) {
        const titles = {
            'badge-earned': 'Badge Earned!',
            'milestone': 'Milestone Reached!',
            'special': 'Special Achievement!',
            'streak': 'Streak Achievement!',
            'level-up': 'Level Up!',
            'first-time': 'First Time Achievement!'
        };
        
        return titles[type] || 'Achievement Unlocked!';
    }

    getNotificationSubtitle(badge, type) {
        if (badge) {
            return `You've earned the "${badge.name}" badge!`;
        }
        
        const subtitles = {
            'milestone': 'You\'ve reached an important milestone!',
            'special': 'You\'ve unlocked something special!',
            'streak': 'Keep up the great work!',
            'level-up': 'You\'ve advanced to the next level!',
            'first-time': 'Welcome to your journey!'
        };
        
        return subtitles[type] || 'Congratulations on your achievement!';
    }

    removeNotification(notification) {
        if (!notification || !notification.parentNode) return;
        
        notification.classList.add('hide');
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
            
            const index = this.notifications.indexOf(notification);
            if (index > -1) {
                this.notifications.splice(index, 1);
            }
        }, 400);
    }

    playNotificationSound(type) {
        try {
            // Create audio context for Web Audio API
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // Different frequencies for different types
            const frequencies = {
                'badge-earned': [523.25, 659.25, 783.99], // C5, E5, G5
                'milestone': [440, 554.37, 659.25], // A4, C#5, E5
                'special': [523.25, 698.46, 880], // C5, F5, A5
                'streak': [659.25, 783.99, 987.77], // E5, G5, B5
                'level-up': [523.25, 659.25, 783.99, 1046.5] // C5, E5, G5, C6
            };
            
            const notes = frequencies[type] || frequencies['badge-earned'];
            
            notes.forEach((frequency, index) => {
                setTimeout(() => {
                    const oscillator = audioContext.createOscillator();
                    const gainNode = audioContext.createGain();
                    
                    oscillator.connect(gainNode);
                    gainNode.connect(audioContext.destination);
                    
                    oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);
                    oscillator.type = 'sine';
                    
                    gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
                    
                    oscillator.start(audioContext.currentTime);
                    oscillator.stop(audioContext.currentTime + 0.3);
                }, index * 100);
            });
        } catch (error) {
            console.log('Could not play notification sound:', error);
        }
    }

    showConfetti() {
        const confettiContainer = document.createElement('div');
        confettiContainer.className = 'confetti-container';
        document.body.appendChild(confettiContainer);

        const colors = ['#f59e0b', '#10b981', '#3b82f6', '#ef4444', '#8b5cf6', '#f97316'];
        const pieces = 50;

        for (let i = 0; i < pieces; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti-piece';
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.animationDelay = Math.random() * 2 + 's';
            confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
            
            confettiContainer.appendChild(confetti);
        }

        // Remove confetti after animation
        setTimeout(() => {
            if (confettiContainer.parentNode) {
                confettiContainer.parentNode.removeChild(confettiContainer);
            }
        }, 4000);
    }

    // Public methods
    showAchievementNotification(achievement) {
        return this.showNotification(achievement.badge, achievement.type || 'badge-earned');
    }

    showMilestoneNotification(milestone) {
        return this.showNotification(milestone, 'milestone');
    }

    showStreakNotification(streak) {
        return this.showNotification(streak, 'streak');
    }

    showSpecialNotification(special) {
        return this.showNotification(special, 'special');
    }

    clearAllNotifications() {
        this.notifications.forEach(notification => {
            this.removeNotification(notification);
        });
    }

    updateSettings(newOptions) {
        this.options = { ...this.options, ...newOptions };
        
        // Update container position if changed
        if (newOptions.position) {
            this.container.className = `achievement-notifications-container ${newOptions.position}`;
        }
    }

    destroy() {
        this.clearAllNotifications();
        
        if (this.container && this.container.parentNode) {
            this.container.remove();
        }
        
        const styles = document.getElementById('achievement-notification-styles');
        if (styles && styles.parentNode) {
            styles.remove();
        }
    }
}

// Global instance
let achievementNotifications = null;

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        achievementNotifications = new AchievementNotificationSystem();
    });
} else {
    achievementNotifications = new AchievementNotificationSystem();
}

// Global helper functions
function showBadgeEarned(badge) {
    if (achievementNotifications) {
        return achievementNotifications.showNotification(badge, 'badge-earned');
    }
}

function showMilestone(milestone) {
    if (achievementNotifications) {
        return achievementNotifications.showMilestoneNotification(milestone);
    }
}

function showStreak(streak) {
    if (achievementNotifications) {
        return achievementNotifications.showStreakNotification(streak);
    }
}

function showSpecialAchievement(achievement) {
    if (achievementNotifications) {
        return achievementNotifications.showSpecialNotification(achievement);
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AchievementNotificationSystem;
}

// Make available globally
window.AchievementNotificationSystem = AchievementNotificationSystem;
window.achievementNotifications = achievementNotifications;