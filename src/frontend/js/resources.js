/**
 * Resources Management System
 * Handles interactive content, help resources, search, and user engagement
 */

class ResourcesManager {
    constructor() {
        this.container = document.querySelector('.resources-div');
        this.resourcesGrid = document.getElementById('resourcesGrid');
        this.categoryFilters = document.querySelectorAll('.category-filter');
        this.searchInput = null;
        this.currentFilter = 'all';
        this.resources = [];
        this.favoriteResources = JSON.parse(localStorage.getItem('favoriteResources') || '[]');
        this.resourceHistory = JSON.parse(localStorage.getItem('resourceHistory') || '[]');
        this.init();
    }

    init() {
        this.createSearchBar();
        this.setupEventListeners();
        this.loadResources();
        this.setupInteractiveFeatures();
        this.trackResourceUsage();
    }

    createSearchBar() {
        const searchContainer = document.createElement('div');
        searchContainer.className = 'resource-search-container';
        searchContainer.innerHTML = `
            <div class="search-bar">
                <input type="text" id="resourceSearch" placeholder="Search resources, articles, tools..." class="search-input">
                <button class="search-btn" type="button">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <circle cx="11" cy="11" r="8"></circle>
                        <path d="m21 21-4.35-4.35"></path>
                    </svg>
                </button>
                <button class="clear-search-btn" type="button" style="display: none;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
            <div class="search-suggestions" style="display: none;"></div>
        `;

        const resourceCategories = this.container.querySelector('.resource-categories');
        resourceCategories.parentNode.insertBefore(searchContainer, resourceCategories);
        
        this.searchInput = document.getElementById('resourceSearch');
    }

    setupEventListeners() {
        // Category filters
        this.categoryFilters.forEach(filter => {
            filter.addEventListener('click', (e) => {
                this.handleCategoryFilter(e.target.dataset.category);
            });
        });

        // Search functionality
        if (this.searchInput) {
            this.searchInput.addEventListener('input', this.debounce(this.handleSearch.bind(this), 300));
            this.searchInput.addEventListener('focus', this.showSearchSuggestions.bind(this));
            
            const clearBtn = this.container.querySelector('.clear-search-btn');
            clearBtn.addEventListener('click', this.clearSearch.bind(this));
        }

        // Resource card interactions
        this.resourcesGrid.addEventListener('click', this.handleResourceClick.bind(this));
        
        // Keyboard navigation
        document.addEventListener('keydown', this.handleKeyboardNavigation.bind(this));
    }

    async loadResources() {
        try {
            // Load from backend API
            const response = await fetch('/api/resources', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.resources = data.resources || [];
            } else {
                // Fallback to mock data
                this.resources = this.getMockResources();
            }
        } catch (error) {
            console.warn('Failed to load resources from API, using mock data:', error);
            this.resources = this.getMockResources();
        }
        
        this.renderResources();
        this.updateResourceStats();
    }

    getMockResources() {
        return [
            {
                id: 'crisis-hotlines',
                title: 'Crisis Hotlines',
                description: 'Immediate support when you need it most',
                category: 'crisis',
                type: 'crisis_support',
                content: {
                    hotlines: {
                        'South Africa': '0800 567 567 (SADAG)',
                        'USA': '988 (Suicide & Crisis Lifeline)',
                        'International': '116 123 (Samaritans)'
                    }
                },
                icon: '🆘',
                priority: 'high',
                tags: ['crisis', 'emergency', 'hotline', 'support']
            },
            {
                id: 'anxiety-guide',
                title: 'Understanding Anxiety',
                description: 'Learn about anxiety symptoms and coping strategies',
                category: 'articles',
                type: 'educational',
                content: {
                    overview: 'Comprehensive guide to understanding and managing anxiety',
                    sections: ['What is Anxiety?', 'Symptoms', 'Coping Strategies', 'When to Seek Help']
                },
                icon: '📚',
                readTime: '8 min read',
                tags: ['anxiety', 'mental health', 'coping', 'education']
            },
            {
                id: 'breathing-exercises',
                title: 'Breathing Techniques',
                description: 'Simple breathing exercises for stress relief',
                category: 'tools',
                type: 'wellness_tool',
                content: {
                    techniques: [
                        { name: '4-7-8 Breathing', duration: '2 minutes' },
                        { name: 'Box Breathing', duration: '3 minutes' },
                        { name: 'Belly Breathing', duration: '5 minutes' }
                    ]
                },
                icon: '🫁',
                interactive: true,
                tags: ['breathing', 'relaxation', 'stress', 'mindfulness']
            },
            {
                id: 'depression-support',
                title: 'Managing Depression',
                description: 'Practical tips for dealing with depression',
                category: 'articles',
                type: 'educational',
                content: {
                    overview: 'Evidence-based strategies for managing depression',
                    sections: ['Understanding Depression', 'Daily Strategies', 'Professional Help', 'Support Systems']
                },
                icon: '💭',
                readTime: '12 min read',
                tags: ['depression', 'mental health', 'support', 'recovery']
            },
            {
                id: 'mindfulness-tools',
                title: 'Mindfulness Toolkit',
                description: 'Collection of mindfulness exercises and meditations',
                category: 'tools',
                type: 'wellness_tool',
                content: {
                    tools: [
                        { name: 'Body Scan Meditation', duration: '10 minutes' },
                        { name: 'Mindful Walking', duration: '15 minutes' },
                        { name: 'Loving-Kindness Meditation', duration: '8 minutes' }
                    ]
                },
                icon: '🧘',
                interactive: true,
                tags: ['mindfulness', 'meditation', 'wellness', 'peace']
            },
            {
                id: 'therapy-guide',
                title: 'Finding the Right Therapist',
                description: 'Guide to different types of therapy and finding help',
                category: 'education',
                type: 'professional_help',
                content: {
                    overview: 'How to find and choose the right mental health professional',
                    sections: ['Types of Therapy', 'What to Look For', 'Questions to Ask', 'Getting Started']
                },
                icon: '🎓',
                readTime: '10 min read',
                tags: ['therapy', 'professional help', 'mental health', 'guidance']
            }
        ];
    }

    renderResources() {
        const filteredResources = this.getFilteredResources();
        
        if (filteredResources.length === 0) {
            this.resourcesGrid.innerHTML = `
                <div class="no-resources-message">
                    <div class="no-resources-icon">🔍</div>
                    <h3>No resources found</h3>
                    <p>Try adjusting your search or filter criteria</p>
                    <button class="clear-filters-btn">Clear All Filters</button>
                </div>
            `;
            return;
        }

        this.resourcesGrid.innerHTML = filteredResources.map(resource => 
            this.createResourceCard(resource)
        ).join('');
        
        this.attachResourceCardListeners();
    }

    createResourceCard(resource) {
        const isFavorite = this.favoriteResources.includes(resource.id);
        const hasBeenViewed = this.resourceHistory.some(h => h.resourceId === resource.id);
        
        return `
            <div class="resource-card ${hasBeenViewed ? 'viewed' : ''}" data-resource-id="${resource.id}" data-category="${resource.category}">
                <div class="resource-card-header">
                    <div class="resource-icon">${resource.icon}</div>
                    <button class="favorite-btn ${isFavorite ? 'active' : ''}" data-resource-id="${resource.id}">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="${isFavorite ? 'currentColor' : 'none'}" stroke="currentColor">
                            <polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"></polygon>
                        </svg>
                    </button>
                </div>
                <h3>${resource.title}</h3>
                <p>${resource.description}</p>
                ${resource.readTime ? `<div class="resource-meta"><span class="read-time">📖 ${resource.readTime}</span></div>` : ''}
                ${resource.interactive ? '<div class="interactive-badge">🎯 Interactive</div>' : ''}
                <div class="resource-actions">
                    <button class="resource-btn primary" data-action="view" data-resource-id="${resource.id}">
                        ${resource.type === 'crisis_support' ? 'Get Help' : resource.interactive ? 'Try Now' : 'Read More'}
                    </button>
                    <button class="resource-btn secondary" data-action="share" data-resource-id="${resource.id}">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
                            <polyline points="16,6 12,2 8,6"></polyline>
                            <line x1="12" y1="2" x2="12" y2="15"></line>
                        </svg>
                        Share
                    </button>
                </div>
                <div class="resource-tags">
                    ${resource.tags ? resource.tags.slice(0, 3).map(tag => `<span class="tag">${tag}</span>`).join('') : ''}
                </div>
            </div>
        `;
    }

    attachResourceCardListeners() {
        // Favorite buttons
        this.resourcesGrid.querySelectorAll('.favorite-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleFavorite(btn.dataset.resourceId);
            });
        });

        // Resource action buttons
        this.resourcesGrid.querySelectorAll('.resource-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = btn.dataset.action;
                const resourceId = btn.dataset.resourceId;
                
                if (action === 'view') {
                    this.viewResource(resourceId);
                } else if (action === 'share') {
                    this.shareResource(resourceId);
                }
            });
        });

        // Clear filters button
        const clearFiltersBtn = this.resourcesGrid.querySelector('.clear-filters-btn');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', this.clearAllFilters.bind(this));
        }
    }

    getFilteredResources() {
        let filtered = this.resources;

        // Filter by category
        if (this.currentFilter !== 'all') {
            filtered = filtered.filter(resource => resource.category === this.currentFilter);
        }

        // Filter by search query
        const searchQuery = this.searchInput?.value.toLowerCase().trim();
        if (searchQuery) {
            filtered = filtered.filter(resource => {
                const searchableText = `${resource.title} ${resource.description} ${resource.tags?.join(' ') || ''}`.toLowerCase();
                return searchableText.includes(searchQuery);
            });
        }

        // Sort by priority and relevance
        return filtered.sort((a, b) => {
            if (a.priority === 'high' && b.priority !== 'high') return -1;
            if (b.priority === 'high' && a.priority !== 'high') return 1;
            return a.title.localeCompare(b.title);
        });
    }

    handleCategoryFilter(category) {
        this.currentFilter = category;
        
        // Update active filter button
        this.categoryFilters.forEach(filter => {
            filter.classList.toggle('active', filter.dataset.category === category);
        });
        
        this.renderResources();
        this.trackFilterUsage(category);
    }

    handleSearch(event) {
        const query = event.target.value.trim();
        
        // Show/hide clear button
        const clearBtn = this.container.querySelector('.clear-search-btn');
        clearBtn.style.display = query ? 'block' : 'none';
        
        this.renderResources();
        
        if (query) {
            this.trackSearchUsage(query);
            this.showSearchSuggestions();
        } else {
            this.hideSearchSuggestions();
        }
    }

    showSearchSuggestions() {
        const query = this.searchInput.value.toLowerCase().trim();
        const suggestions = this.container.querySelector('.search-suggestions');
        
        if (!query) {
            suggestions.style.display = 'none';
            return;
        }

        // Generate suggestions based on tags and titles
        const allTags = [...new Set(this.resources.flatMap(r => r.tags || []))];
        const matchingSuggestions = allTags
            .filter(tag => tag.toLowerCase().includes(query))
            .slice(0, 5);

        if (matchingSuggestions.length > 0) {
            suggestions.innerHTML = matchingSuggestions
                .map(suggestion => `<div class="suggestion-item" data-suggestion="${suggestion}">${suggestion}</div>`)
                .join('');
            suggestions.style.display = 'block';
            
            // Add click listeners to suggestions
            suggestions.querySelectorAll('.suggestion-item').forEach(item => {
                item.addEventListener('click', () => {
                    this.searchInput.value = item.dataset.suggestion;
                    this.handleSearch({ target: this.searchInput });
                    this.hideSearchSuggestions();
                });
            });
        } else {
            suggestions.style.display = 'none';
        }
    }

    hideSearchSuggestions() {
        const suggestions = this.container.querySelector('.search-suggestions');
        suggestions.style.display = 'none';
    }

    clearSearch() {
        this.searchInput.value = '';
        this.container.querySelector('.clear-search-btn').style.display = 'none';
        this.hideSearchSuggestions();
        this.renderResources();
    }

    clearAllFilters() {
        this.currentFilter = 'all';
        this.searchInput.value = '';
        this.container.querySelector('.clear-search-btn').style.display = 'none';
        
        // Reset active filter
        this.categoryFilters.forEach(filter => {
            filter.classList.toggle('active', filter.dataset.category === 'all');
        });
        
        this.renderResources();
    }

    toggleFavorite(resourceId) {
        const index = this.favoriteResources.indexOf(resourceId);
        
        if (index === -1) {
            this.favoriteResources.push(resourceId);
        } else {
            this.favoriteResources.splice(index, 1);
        }
        
        localStorage.setItem('favoriteResources', JSON.stringify(this.favoriteResources));
        this.renderResources();
        
        // Show feedback
        this.showNotification(
            index === -1 ? '⭐ Added to favorites!' : '💔 Removed from favorites',
            'success'
        );
    }

    viewResource(resourceId) {
        const resource = this.resources.find(r => r.id === resourceId);
        if (!resource) return;

        // Track resource view
        this.trackResourceView(resourceId);
        
        // Handle different resource types
        switch (resource.type) {
            case 'crisis_support':
                this.showCrisisResource(resource);
                break;
            case 'wellness_tool':
                this.showInteractiveTool(resource);
                break;
            case 'educational':
                this.showEducationalContent(resource);
                break;
            default:
                this.showResourceModal(resource);
        }
    }

    showCrisisResource(resource) {
        const modal = this.createModal('Crisis Support', `
            <div class="crisis-resource-content">
                <div class="crisis-warning">
                    <div class="warning-icon">⚠️</div>
                    <p><strong>If you're in immediate danger, please call emergency services (911, 112, etc.)</strong></p>
                </div>
                <div class="crisis-hotlines">
                    <h3>Crisis Hotlines</h3>
                    ${Object.entries(resource.content.hotlines || {}).map(([country, number]) => `
                        <div class="hotline-item">
                            <strong>${country}:</strong>
                            <a href="tel:${number.replace(/[^0-9+]/g, '')}" class="hotline-number">${number}</a>
                        </div>
                    `).join('')}
                </div>
                <div class="crisis-actions">
                    <button class="crisis-btn" onclick="window.open('tel:988')">📞 Call Crisis Line</button>
                    <button class="crisis-btn" onclick="this.closest('.modal-overlay').remove()">🆘 I'm Safe Now</button>
                </div>
            </div>
        `);
        
        document.body.appendChild(modal);
    }

    showInteractiveTool(resource) {
        if (resource.id === 'breathing-exercises') {
            this.showBreathingExercise(resource);
        } else if (resource.id === 'mindfulness-tools') {
            this.showMindfulnessTools(resource);
        } else {
            this.showResourceModal(resource);
        }
    }

    showBreathingExercise(resource) {
        const modal = this.createModal('Breathing Exercises', `
            <div class="breathing-exercise-content">
                <div class="exercise-selector">
                    <h3>Choose a breathing technique:</h3>
                    <div class="technique-options">
                        ${resource.content.techniques.map((technique, index) => `
                            <button class="technique-btn" data-technique="${index}">
                                <strong>${technique.name}</strong>
                                <span>${technique.duration}</span>
                            </button>
                        `).join('')}
                    </div>
                </div>
                <div class="breathing-guide" style="display: none;">
                    <div class="breathing-circle">
                        <div class="circle-inner"></div>
                        <div class="breathing-text">Breathe</div>
                    </div>
                    <div class="breathing-instructions"></div>
                    <div class="breathing-controls">
                        <button class="start-btn">Start</button>
                        <button class="pause-btn" style="display: none;">Pause</button>
                        <button class="reset-btn">Reset</button>
                    </div>
                </div>
            </div>
        `);
        
        this.setupBreathingExercise(modal, resource);
        document.body.appendChild(modal);
    }

    setupBreathingExercise(modal, resource) {
        const techniqueButtons = modal.querySelectorAll('.technique-btn');
        const breathingGuide = modal.querySelector('.breathing-guide');
        const exerciseSelector = modal.querySelector('.exercise-selector');
        
        techniqueButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const techniqueIndex = parseInt(btn.dataset.technique);
                const technique = resource.content.techniques[techniqueIndex];
                
                exerciseSelector.style.display = 'none';
                breathingGuide.style.display = 'block';
                
                this.initBreathingAnimation(modal, technique);
            });
        });
    }

    initBreathingAnimation(modal, technique) {
        const circle = modal.querySelector('.circle-inner');
        const text = modal.querySelector('.breathing-text');
        const instructions = modal.querySelector('.breathing-instructions');
        const startBtn = modal.querySelector('.start-btn');
        const pauseBtn = modal.querySelector('.pause-btn');
        const resetBtn = modal.querySelector('.reset-btn');
        
        let isRunning = false;
        let animationId = null;
        
        instructions.textContent = `${technique.name} - ${technique.duration}`;
        
        const breathingCycle = () => {
            if (!isRunning) return;
            
            // Inhale
            text.textContent = 'Inhale';
            circle.style.transform = 'scale(1.5)';
            circle.style.transition = 'transform 4s ease-in-out';
            
            setTimeout(() => {
                if (!isRunning) return;
                // Hold
                text.textContent = 'Hold';
                
                setTimeout(() => {
                    if (!isRunning) return;
                    // Exhale
                    text.textContent = 'Exhale';
                    circle.style.transform = 'scale(1)';
                    
                    setTimeout(() => {
                        if (isRunning) {
                            animationId = requestAnimationFrame(breathingCycle);
                        }
                    }, 4000);
                }, 2000);
            }, 4000);
        };
        
        startBtn.addEventListener('click', () => {
            isRunning = true;
            startBtn.style.display = 'none';
            pauseBtn.style.display = 'inline-block';
            breathingCycle();
        });
        
        pauseBtn.addEventListener('click', () => {
            isRunning = false;
            startBtn.style.display = 'inline-block';
            pauseBtn.style.display = 'none';
            if (animationId) {
                cancelAnimationFrame(animationId);
            }
        });
        
        resetBtn.addEventListener('click', () => {
            isRunning = false;
            startBtn.style.display = 'inline-block';
            pauseBtn.style.display = 'none';
            circle.style.transform = 'scale(1)';
            text.textContent = 'Breathe';
            if (animationId) {
                cancelAnimationFrame(animationId);
            }
        });
    }

    showEducationalContent(resource) {
        const modal = this.createModal(resource.title, `
            <div class="educational-content">
                <div class="content-overview">
                    <p>${resource.content.overview}</p>
                </div>
                <div class="content-sections">
                    <h3>What you'll learn:</h3>
                    <ul>
                        ${resource.content.sections?.map(section => `<li>${section}</li>`).join('') || ''}
                    </ul>
                </div>
                <div class="content-actions">
                    <button class="read-btn primary">Start Reading</button>
                    <button class="bookmark-btn secondary">📖 Bookmark</button>
                </div>
            </div>
        `);
        
        document.body.appendChild(modal);
    }

    showResourceModal(resource) {
        const modal = this.createModal(resource.title, `
            <div class="resource-modal-content">
                <div class="resource-header">
                    <div class="resource-icon-large">${resource.icon}</div>
                    <div class="resource-info">
                        <h2>${resource.title}</h2>
                        <p>${resource.description}</p>
                        ${resource.readTime ? `<span class="read-time">📖 ${resource.readTime}</span>` : ''}
                    </div>
                </div>
                <div class="resource-content">
                    ${this.formatResourceContent(resource.content)}
                </div>
                <div class="resource-actions">
                    <button class="action-btn primary">Get Started</button>
                    <button class="action-btn secondary" onclick="this.closest('.modal-overlay').remove()">Close</button>
                </div>
            </div>
        `);
        
        document.body.appendChild(modal);
    }

    formatResourceContent(content) {
        if (typeof content === 'string') {
            return `<p>${content}</p>`;
        }
        
        let html = '';
        
        Object.entries(content).forEach(([key, value]) => {
            if (Array.isArray(value)) {
                html += `<div class="content-section">
                    <h3>${this.formatKey(key)}</h3>
                    <ul>${value.map(item => `<li>${item}</li>`).join('')}</ul>
                </div>`;
            } else if (typeof value === 'object') {
                html += `<div class="content-section">
                    <h3>${this.formatKey(key)}</h3>
                    ${this.formatResourceContent(value)}
                </div>`;
            } else {
                html += `<div class="content-section">
                    <h3>${this.formatKey(key)}</h3>
                    <p>${value}</p>
                </div>`;
            }
        });
        
        return html;
    }

    formatKey(key) {
        return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    createModal(title, content) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay resource-modal';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h2>${title}</h2>
                    <button class="close-btn" onclick="this.closest('.modal-overlay').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;
        
        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        return modal;
    }

    shareResource(resourceId) {
        const resource = this.resources.find(r => r.id === resourceId);
        if (!resource) return;

        const shareText = `Check out this helpful resource: ${resource.title}\n\n${resource.description}\n\nFrom ChillBuddy Mental Health Resources`;
        
        if (navigator.share) {
            navigator.share({
                title: resource.title,
                text: shareText,
                url: window.location.href
            }).then(() => {
                this.showNotification('🔗 Resource shared successfully!', 'success');
            }).catch(() => {
                this.fallbackShare(shareText);
            });
        } else {
            this.fallbackShare(shareText);
        }
    }

    fallbackShare(shareText) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(shareText).then(() => {
                this.showNotification('📋 Resource info copied to clipboard!', 'success');
            });
        } else {
            this.showNotification('❌ Sharing not supported on this device', 'error');
        }
    }

    setupInteractiveFeatures() {
        // Add keyboard shortcuts
        this.setupKeyboardShortcuts();
        
        // Add accessibility features
        this.setupAccessibility();
        
        // Add analytics tracking
        this.setupAnalytics();
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'k':
                        e.preventDefault();
                        this.searchInput?.focus();
                        break;
                    case 'f':
                        e.preventDefault();
                        this.showFavorites();
                        break;
                }
            }
        });
    }

    setupAccessibility() {
        // Add ARIA labels and roles
        this.resourcesGrid.setAttribute('role', 'grid');
        this.resourcesGrid.setAttribute('aria-label', 'Mental health resources');
        
        // Add focus management
        this.resourcesGrid.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                const focusedCard = document.activeElement.closest('.resource-card');
                if (focusedCard) {
                    e.preventDefault();
                    this.viewResource(focusedCard.dataset.resourceId);
                }
            }
        });
    }

    setupAnalytics() {
        // Track resource interactions
        this.resourcesGrid.addEventListener('click', (e) => {
            const resourceCard = e.target.closest('.resource-card');
            if (resourceCard) {
                this.trackResourceInteraction(resourceCard.dataset.resourceId, 'click');
            }
        });
    }

    trackResourceView(resourceId) {
        const viewData = {
            resourceId,
            timestamp: new Date().toISOString(),
            type: 'view'
        };
        
        this.resourceHistory.push(viewData);
        
        // Keep only last 100 entries
        if (this.resourceHistory.length > 100) {
            this.resourceHistory = this.resourceHistory.slice(-100);
        }
        
        localStorage.setItem('resourceHistory', JSON.stringify(this.resourceHistory));
        
        // Emit event for progress tracking
        window.dispatchEvent(new CustomEvent('resourceViewed', {
            detail: { resourceId, timestamp: viewData.timestamp }
        }));
    }

    trackResourceInteraction(resourceId, interactionType) {
        // Track for analytics
        console.log(`Resource interaction: ${resourceId} - ${interactionType}`);
    }

    trackFilterUsage(category) {
        console.log(`Filter used: ${category}`);
    }

    trackSearchUsage(query) {
        console.log(`Search performed: ${query}`);
    }

    updateResourceStats() {
        // Update resource statistics
        const totalResources = this.resources.length;
        const favoriteCount = this.favoriteResources.length;
        const viewedCount = new Set(this.resourceHistory.map(h => h.resourceId)).size;
        
        // Emit stats for dashboard
        window.dispatchEvent(new CustomEvent('resourceStatsUpdated', {
            detail: { totalResources, favoriteCount, viewedCount }
        }));
    }

    showFavorites() {
        this.currentFilter = 'favorites';
        this.renderFavoriteResources();
    }

    renderFavoriteResources() {
        const favoriteResources = this.resources.filter(r => this.favoriteResources.includes(r.id));
        
        if (favoriteResources.length === 0) {
            this.resourcesGrid.innerHTML = `
                <div class="no-resources-message">
                    <div class="no-resources-icon">⭐</div>
                    <h3>No favorite resources yet</h3>
                    <p>Click the star icon on any resource to add it to your favorites</p>
                </div>
            `;
            return;
        }
        
        this.resourcesGrid.innerHTML = favoriteResources.map(resource => 
            this.createResourceCard(resource)
        ).join('');
        
        this.attachResourceCardListeners();
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    handleKeyboardNavigation(e) {
        if (e.key === 'Escape') {
            // Close any open modals
            const modals = document.querySelectorAll('.modal-overlay');
            modals.forEach(modal => modal.remove());
            
            // Clear search if focused
            if (document.activeElement === this.searchInput) {
                this.clearSearch();
            }
        }
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    destroy() {
        // Clean up event listeners and resources
        this.categoryFilters.forEach(filter => {
            filter.removeEventListener('click', this.handleCategoryFilter);
        });
        
        if (this.searchInput) {
            this.searchInput.removeEventListener('input', this.handleSearch);
        }
        
        document.removeEventListener('keydown', this.handleKeyboardNavigation);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.resourcesManager = new ResourcesManager();
    });
} else {
    window.resourcesManager = new ResourcesManager();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ResourcesManager;
}