/**
 * Badge Sharing Features
 * Social sharing and celebration components for achievements
 */

class BadgeSharing {
    constructor() {
        this.shareHistory = [];
        this.celebrationQueue = [];
        this.isProcessingCelebration = false;
        this.shareTemplates = this.getShareTemplates();
        this.socialPlatforms = this.getSocialPlatforms();
        
        this.init();
    }

    init() {
        // Removed injectStyles - using existing design system
        this.attachEventListeners();
        this.loadShareHistory();
        this.createSimpleShareInterface();
    }

    getShareTemplates() {
        return {
            badge: {
                default: "🏆 I just earned the '{name}' badge! {description} #Achievement #ChillBuddy",
                milestone: "🎉 Milestone achieved! I just earned '{name}' - {description} #Milestone #ChillBuddy",
                rare: "✨ Rare achievement unlocked! I earned the '{name}' badge! Only {rarity} users have this! #RareAchievement #ChillBuddy",
                streak: "🔥 {streak} day streak! I just earned '{name}' for my consistency! #Streak #ChillBuddy",
                first: "🎯 First achievement! I just earned my first badge '{name}'! Starting my journey! #FirstBadge #ChillBuddy"
            },
            milestone: {
                default: "🎯 Major milestone reached! {name} - {description} #Milestone #ChillBuddy",
                time: "📅 Time milestone! I've been active for {period}! {description} #TimeAchievement #ChillBuddy",
                usage: "💬 Usage milestone! {description} Keep the conversations going! #UsageAchievement #ChillBuddy"
            },
            custom: {
                celebration: "🎊 Celebrating my achievement! {name} - {description} #Achievement #ChillBuddy",
                progress: "📈 Making progress! Just earned '{name}' - {description} #Progress #ChillBuddy",
                community: "🤝 Community achievement! {name} - {description} Thanks to everyone! #Community #ChillBuddy"
            }
        };
    }

    getSocialPlatforms() {
        return {
            twitter: {
                name: 'Twitter',
                icon: '🐦',
                color: '#1da1f2',
                maxLength: 280,
                url: 'https://twitter.com/intent/tweet?text={text}&url={url}',
                hashtags: ['Achievement', 'ChillBuddy']
            },
            facebook: {
                name: 'Facebook',
                icon: '📘',
                color: '#4267b2',
                url: 'https://www.facebook.com/sharer/sharer.php?u={url}&quote={text}'
            },
            linkedin: {
                name: 'LinkedIn',
                icon: '💼',
                color: '#0077b5',
                url: 'https://www.linkedin.com/sharing/share-offsite/?url={url}&summary={text}'
            },
            reddit: {
                name: 'Reddit',
                icon: '🤖',
                color: '#ff4500',
                url: 'https://reddit.com/submit?url={url}&title={text}'
            },
            whatsapp: {
                name: 'WhatsApp',
                icon: '💬',
                color: '#25d366',
                url: 'https://wa.me/?text={text}%20{url}'
            },
            telegram: {
                name: 'Telegram',
                icon: '✈️',
                color: '#0088cc',
                url: 'https://t.me/share/url?url={url}&text={text}'
            }
        };
    }

    // Main sharing function
    shareAchievement(achievement, options = {}) {
        const shareData = this.prepareShareData(achievement, options);
        this.showShareModal(shareData);
    }

    prepareShareData(achievement, options) {
        const template = this.selectTemplate(achievement, options.templateType);
        const shareText = this.generateShareText(achievement, template, options);
        const shareUrl = options.url || window.location.href;
        const imageUrl = this.generateShareImage(achievement);
        
        return {
            achievement,
            text: shareText,
            url: shareUrl,
            image: imageUrl,
            template,
            options
        };
    }

    selectTemplate(achievement, templateType) {
        const type = achievement.type || 'badge';
        const category = templateType || this.detectTemplateCategory(achievement);
        
        if (this.shareTemplates[type] && this.shareTemplates[type][category]) {
            return this.shareTemplates[type][category];
        }
        
        return this.shareTemplates[type]?.default || this.shareTemplates.badge.default;
    }

    detectTemplateCategory(achievement) {
        if (achievement.isFirst) return 'first';
        if (achievement.streak) return 'streak';
        if (achievement.rarity === 'Epic' || achievement.rarity === 'Legendary') return 'rare';
        if (achievement.type === 'milestone') {
            if (achievement.category?.includes('Time')) return 'time';
            if (achievement.category?.includes('Usage')) return 'usage';
        }
        return 'default';
    }

    generateShareText(achievement, template, options) {
        let text = template;
        
        // Replace placeholders
        text = text.replace('{name}', achievement.name);
        text = text.replace('{description}', achievement.description);
        text = text.replace('{rarity}', achievement.rarity || 'Common');
        text = text.replace('{category}', achievement.category || 'General');
        text = text.replace('{points}', achievement.points || 0);
        text = text.replace('{streak}', achievement.streak || '');
        text = text.replace('{period}', achievement.period || '');
        
        // Add custom message if provided
        if (options.customMessage) {
            text += ` ${options.customMessage}`;
        }
        
        return text;
    }

    generateShareImage(achievement) {
        // In a real implementation, this would generate a dynamic image
        // For now, return a placeholder or achievement icon
        return achievement.imageUrl || this.createAchievementCard(achievement);
    }

    createAchievementCard(achievement) {
        // Create a data URL for a simple achievement card
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        canvas.width = 400;
        canvas.height = 200;
        
        // Background gradient
        const gradient = ctx.createLinearGradient(0, 0, 400, 200);
        gradient.addColorStop(0, '#667eea');
        gradient.addColorStop(1, '#764ba2');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 400, 200);
        
        // Achievement text
        ctx.fillStyle = 'white';
        ctx.font = 'bold 24px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('🏆 Achievement Unlocked!', 200, 60);
        
        ctx.font = 'bold 18px Arial';
        ctx.fillText(achievement.name, 200, 100);
        
        ctx.font = '14px Arial';
        ctx.fillText(achievement.description, 200, 130);
        
        ctx.font = 'bold 16px Arial';
        ctx.fillText(`+${achievement.points || 0} points`, 200, 160);
        
        return canvas.toDataURL();
    }

    showShareModal(shareData) {
        // Use simple interface if complex modal creation fails
        if (this.simpleShareModal) {
            this.showSimpleShareModal(shareData);
            return;
        }
        
        const modal = this.createShareModal(shareData);
        document.body.appendChild(modal);
        
        // Animate in
        requestAnimationFrame(() => {
            modal.classList.add('active');
        });
        
        // Auto-remove after timeout if not interacted with
        setTimeout(() => {
            if (modal.parentNode && !modal.classList.contains('interacted')) {
                this.closeShareModal(modal);
            }
        }, 30000);
    }

    showSimpleShareModal(shareData) {
        if (!this.simpleShareModal) return;
        
        // Update preview
        const preview = this.simpleShareModal.querySelector('.simple-badge-preview');
        preview.innerHTML = `
            <div style="font-size: 2rem; margin-bottom: 8px;">${shareData.achievement.icon || '🏆'}</div>
            <h5 style="margin: 0 0 4px 0; color: #374151;">${shareData.achievement.name}</h5>
            <p style="margin: 0; font-size: 0.9rem; color: #6b7280;">${shareData.achievement.description}</p>
        `;
        
        // Store current badge for sharing
        this.currentBadge = shareData;
        
        // Show modal
        this.simpleShareModal.style.display = 'block';
    }

    createShareModal(shareData) {
        const modal = document.createElement('div');
        modal.className = 'share-modal-overlay';
        
        modal.innerHTML = `
            <div class="share-modal">
                <div class="share-modal-header">
                    <div class="share-achievement-preview">
                        <div class="share-achievement-icon">${shareData.achievement.icon || '🏆'}</div>
                        <div class="share-achievement-info">
                            <h3>${shareData.achievement.name}</h3>
                            <p>${shareData.achievement.description}</p>
                            <div class="share-achievement-meta">
                                <span class="share-points">+${shareData.achievement.points || 0} points</span>
                                <span class="share-rarity ${(shareData.achievement.rarity || 'common').toLowerCase()}">
                                    ${shareData.achievement.rarity || 'Common'}
                                </span>
                            </div>
                        </div>
                    </div>
                    <button class="share-modal-close" aria-label="Close">
                        <span>✕</span>
                    </button>
                </div>
                
                <div class="share-modal-content">
                    <div class="share-text-section">
                        <label for="share-text">Share Message:</label>
                        <textarea id="share-text" class="share-text-input" rows="3" maxlength="500">${shareData.text}</textarea>
                        <div class="share-text-controls">
                            <div class="character-count">
                                <span class="current">${shareData.text.length}</span>/<span class="max">500</span>
                            </div>
                            <div class="share-templates">
                                <button class="template-btn" data-template="celebration">🎊 Celebration</button>
                                <button class="template-btn" data-template="progress">📈 Progress</button>
                                <button class="template-btn" data-template="community">🤝 Community</button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="share-platforms-section">
                        <h4>Share on:</h4>
                        <div class="share-platforms">
                            ${Object.entries(this.socialPlatforms).map(([key, platform]) => `
                                <button class="share-platform-btn" data-platform="${key}" style="--platform-color: ${platform.color}">
                                    <span class="platform-icon">${platform.icon}</span>
                                    <span class="platform-name">${platform.name}</span>
                                </button>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="share-options-section">
                        <h4>Additional Options:</h4>
                        <div class="share-options">
                            <button class="share-option-btn" data-action="copy">
                                <span class="icon">📋</span>
                                <span>Copy to Clipboard</span>
                            </button>
                            <button class="share-option-btn" data-action="download">
                                <span class="icon">💾</span>
                                <span>Download Image</span>
                            </button>
                            <button class="share-option-btn" data-action="email">
                                <span class="icon">📧</span>
                                <span>Send via Email</span>
                            </button>
                            <button class="share-option-btn" data-action="qr">
                                <span class="icon">📱</span>
                                <span>Generate QR Code</span>
                            </button>
                        </div>
                    </div>
                    
                    <div class="share-celebration-section">
                        <button class="celebration-btn" data-celebration="confetti">
                            🎊 Celebrate with Confetti
                        </button>
                        <button class="celebration-btn" data-celebration="fireworks">
                            🎆 Fireworks Celebration
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        this.attachModalEventListeners(modal, shareData);
        return modal;
    }

    attachModalEventListeners(modal, shareData) {
        // Mark as interacted when user does anything
        modal.addEventListener('click', () => {
            modal.classList.add('interacted');
        });
        
        // Close button
        modal.querySelector('.share-modal-close').addEventListener('click', () => {
            this.closeShareModal(modal);
        });
        
        // Click outside to close
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeShareModal(modal);
            }
        });
        
        // Text input character count
        const textInput = modal.querySelector('.share-text-input');
        const currentCount = modal.querySelector('.character-count .current');
        
        textInput.addEventListener('input', () => {
            currentCount.textContent = textInput.value.length;
            shareData.text = textInput.value;
        });
        
        // Template buttons
        modal.querySelectorAll('.template-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const templateType = btn.dataset.template;
                const newTemplate = this.shareTemplates.custom[templateType];
                const newText = this.generateShareText(shareData.achievement, newTemplate, shareData.options);
                textInput.value = newText;
                shareData.text = newText;
                currentCount.textContent = newText.length;
            });
        });
        
        // Platform sharing buttons
        modal.querySelectorAll('.share-platform-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const platform = btn.dataset.platform;
                this.shareOnPlatform(platform, shareData);
            });
        });
        
        // Additional options
        modal.querySelectorAll('.share-option-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                this.handleShareOption(action, shareData);
            });
        });
        
        // Celebration buttons
        modal.querySelectorAll('.celebration-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const celebration = btn.dataset.celebration;
                this.triggerCelebration(celebration);
            });
        });
    }

    shareOnPlatform(platform, shareData) {
        const platformConfig = this.socialPlatforms[platform];
        if (!platformConfig) return;
        
        let shareUrl = platformConfig.url;
        let shareText = shareData.text;
        
        // Truncate text if platform has length limits
        if (platformConfig.maxLength && shareText.length > platformConfig.maxLength) {
            shareText = shareText.substring(0, platformConfig.maxLength - 3) + '...';
        }
        
        // Replace URL placeholders
        shareUrl = shareUrl.replace('{text}', encodeURIComponent(shareText));
        shareUrl = shareUrl.replace('{url}', encodeURIComponent(shareData.url));
        
        // Open sharing window
        const width = 600;
        const height = 400;
        const left = (window.innerWidth - width) / 2;
        const top = (window.innerHeight - height) / 2;
        
        window.open(
            shareUrl,
            'share',
            `width=${width},height=${height},left=${left},top=${top},scrollbars=yes,resizable=yes`
        );
        
        // Track share
        this.trackShare(platform, shareData.achievement);
        
        // Show success feedback
        this.showShareFeedback(`Shared on ${platformConfig.name}!`);
    }

    handleShareOption(action, shareData) {
        switch (action) {
            case 'copy':
                this.copyToClipboard(shareData.text);
                break;
            case 'download':
                this.downloadShareImage(shareData);
                break;
            case 'email':
                this.shareViaEmail(shareData);
                break;
            case 'qr':
                this.generateQRCode(shareData);
                break;
        }
    }

    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showShareFeedback('Copied to clipboard!');
        }).catch(() => {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            textArea.remove();
            this.showShareFeedback('Copied to clipboard!');
        });
    }

    downloadShareImage(shareData) {
        const imageUrl = shareData.image;
        const link = document.createElement('a');
        link.href = imageUrl;
        link.download = `${shareData.achievement.name.replace(/\s+/g, '_')}_achievement.png`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        
        this.showShareFeedback('Image downloaded!');
    }

    shareViaEmail(shareData) {
        const subject = encodeURIComponent(`Check out my achievement: ${shareData.achievement.name}`);
        const body = encodeURIComponent(`${shareData.text}\n\n${shareData.url}`);
        const emailUrl = `mailto:?subject=${subject}&body=${body}`;
        
        window.location.href = emailUrl;
        this.showShareFeedback('Email client opened!');
    }

    generateQRCode(shareData) {
        // Simple QR code generation (in real app, use a proper QR library)
        const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(shareData.url)}`;
        
        const qrModal = document.createElement('div');
        qrModal.className = 'qr-modal-overlay';
        qrModal.innerHTML = `
            <div class="qr-modal">
                <div class="qr-header">
                    <h3>QR Code for Sharing</h3>
                    <button class="qr-close">✕</button>
                </div>
                <div class="qr-content">
                    <img src="${qrUrl}" alt="QR Code" class="qr-image">
                    <p>Scan this QR code to view the achievement</p>
                    <button class="qr-download">Download QR Code</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(qrModal);
        
        // Event listeners for QR modal
        qrModal.querySelector('.qr-close').addEventListener('click', () => {
            qrModal.remove();
        });
        
        qrModal.querySelector('.qr-download').addEventListener('click', () => {
            const link = document.createElement('a');
            link.href = qrUrl;
            link.download = `${shareData.achievement.name}_qr.png`;
            link.click();
        });
        
        qrModal.addEventListener('click', (e) => {
            if (e.target === qrModal) {
                qrModal.remove();
            }
        });
    }

    triggerCelebration(type) {
        switch (type) {
            case 'confetti':
                this.showConfetti();
                break;
            case 'fireworks':
                this.showFireworks();
                break;
        }
    }

    showConfetti() {
        // Create confetti animation
        const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#dda0dd'];
        const confettiCount = 50;
        
        for (let i = 0; i < confettiCount; i++) {
            setTimeout(() => {
                this.createConfettiPiece(colors[Math.floor(Math.random() * colors.length)]);
            }, i * 50);
        }
    }

    createConfettiPiece(color) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti-piece';
        confetti.style.cssText = `
            position: fixed;
            width: 10px;
            height: 10px;
            background: ${color};
            left: ${Math.random() * 100}vw;
            top: -10px;
            z-index: 10000;
            pointer-events: none;
            animation: confetti-fall 3s linear forwards;
        `;
        
        document.body.appendChild(confetti);
        
        setTimeout(() => {
            confetti.remove();
        }, 3000);
    }

    showFireworks() {
        // Create fireworks animation
        const fireworksCount = 5;
        
        for (let i = 0; i < fireworksCount; i++) {
            setTimeout(() => {
                this.createFirework();
            }, i * 500);
        }
    }

    createFirework() {
        const firework = document.createElement('div');
        firework.className = 'firework';
        firework.style.cssText = `
            position: fixed;
            width: 4px;
            height: 4px;
            background: #fff;
            border-radius: 50%;
            left: ${Math.random() * 100}vw;
            top: ${Math.random() * 50 + 25}vh;
            z-index: 10000;
            pointer-events: none;
            animation: firework-explode 1s ease-out forwards;
        `;
        
        document.body.appendChild(firework);
        
        setTimeout(() => {
            firework.remove();
        }, 1000);
    }

    closeShareModal(modal) {
        modal.classList.add('closing');
        setTimeout(() => {
            modal.remove();
        }, 300);
    }

    showShareFeedback(message) {
        const feedback = document.createElement('div');
        feedback.className = 'share-feedback';
        feedback.textContent = message;
        
        document.body.appendChild(feedback);
        
        setTimeout(() => {
            feedback.remove();
        }, 3000);
    }

    trackShare(platform, achievement) {
        const shareRecord = {
            platform,
            achievement: achievement.id,
            timestamp: new Date(),
            achievementName: achievement.name
        };
        
        this.shareHistory.push(shareRecord);
        this.saveShareHistory();
        
        // Emit event for analytics
        window.dispatchEvent(new CustomEvent('achievementShared', {
            detail: shareRecord
        }));
    }

    loadShareHistory() {
        try {
            const saved = localStorage.getItem('chillbuddy_share_history');
            if (saved) {
                this.shareHistory = JSON.parse(saved);
            }
        } catch (error) {
            console.warn('Failed to load share history:', error);
        }
    }

    saveShareHistory() {
        try {
            localStorage.setItem('chillbuddy_share_history', JSON.stringify(this.shareHistory));
        } catch (error) {
            console.warn('Failed to save share history:', error);
        }
    }

    attachEventListeners() {
        // Listen for achievement events
        window.addEventListener('badgeEarned', (e) => {
            if (e.detail.autoShare) {
                this.shareAchievement(e.detail.badge, { templateType: 'celebration' });
            }
        });
        
        window.addEventListener('milestoneReached', (e) => {
            if (e.detail.autoShare) {
                this.shareAchievement(e.detail.milestone, { templateType: 'milestone' });
            }
        });
        
        // Listen for manual share requests
        window.addEventListener('shareAchievement', (e) => {
            this.shareAchievement(e.detail.achievement, e.detail.options);
        });
    }

    // Removed injectStyles - using existing design system

    createSimpleShareInterface() {
        // Create a simple share interface that integrates with existing UI elements
        if (document.querySelector('.simple-share-interface')) return;
        
        const shareInterface = document.createElement('div');
        shareInterface.className = 'simple-share-interface';
        shareInterface.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
            z-index: 1000;
            display: none;
            max-width: 400px;
            width: 90%;
        `;
        
        shareInterface.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h4 style="margin: 0; color: #374151;">Share Achievement</h4>
                <button class="close-simple-share" style="background: none; border: none; font-size: 20px; cursor: pointer; color: #6b7280;">×</button>
            </div>
            <div class="simple-badge-preview" style="text-align: center; margin-bottom: 16px; padding: 16px; background: #f9fafb; border-radius: 8px;"></div>
            <div class="simple-share-options" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">
                <button class="simple-share-btn" data-platform="twitter" style="padding: 8px; border: 1px solid #d1d5db; background: white; border-radius: 6px; cursor: pointer;">🐦 Twitter</button>
                <button class="simple-share-btn" data-platform="facebook" style="padding: 8px; border: 1px solid #d1d5db; background: white; border-radius: 6px; cursor: pointer;">📘 Facebook</button>
                <button class="simple-share-btn" data-platform="linkedin" style="padding: 8px; border: 1px solid #d1d5db; background: white; border-radius: 6px; cursor: pointer;">💼 LinkedIn</button>
                <button class="simple-share-btn" data-platform="copy" style="padding: 8px; border: 1px solid #d1d5db; background: white; border-radius: 6px; cursor: pointer;">📋 Copy</button>
            </div>
        `;
        
        document.body.appendChild(shareInterface);
        this.simpleShareModal = shareInterface;
        
        // Add event listeners
        shareInterface.querySelector('.close-simple-share').addEventListener('click', () => {
            shareInterface.style.display = 'none';
        });
        
        shareInterface.querySelectorAll('.simple-share-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const platform = e.target.dataset.platform;
                this.shareOnPlatform(platform, this.currentBadge);
            });
        });
    }

    // Public API
    share(achievement, options = {}) {
        this.shareAchievement(achievement, options);
    }

    getShareHistory() {
        return this.shareHistory;
    }

    clearShareHistory() {
        this.shareHistory = [];
        this.saveShareHistory();
    }

    destroy() {
        const styles = document.getElementById('badge-sharing-styles');
        if (styles) {
            styles.remove();
        }
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BadgeSharing;
}

// Global instance
window.badgeSharing = new BadgeSharing();

// Global helper functions
window.shareAchievement = function(achievement, options = {}) {
    return window.badgeSharing.share(achievement, options);
};

window.celebrateAchievement = function(type = 'confetti') {
    return window.badgeSharing.triggerCelebration(type);
};