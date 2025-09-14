// Sidebar functionality for ChillBuddy

class SidebarManager {
    constructor() {
        this.sidebar = document.querySelector('.sidebar');
        this.overlay = document.querySelector('.sidebar-overlay');
        this.toggleBtn = document.querySelector('.sidebar-toggle-btn');
        this.closeBtn = document.querySelector('.sidebar-close-btn');
        this.navItems = document.querySelectorAll('.sidebar-nav-item');
        this.newChatBtn = document.querySelector('.new-chat-btn');
        this.chatHistoryList = document.querySelector('.chat-history-list');
        
        // Chat history management
        this.currentChatId = 'current';
        this.chatHistory = this.loadChatHistory();
        
        this.init();
    }
    
    init() {
        // Bind event listeners
        this.toggleBtn?.addEventListener('click', () => this.toggleSidebar());
        this.closeBtn?.addEventListener('click', () => this.closeSidebar());
        this.overlay?.addEventListener('click', () => this.closeSidebar());
        this.newChatBtn?.addEventListener('click', () => this.createNewChat());
        
        // Handle navigation items
        this.navItems.forEach(item => {
            item.addEventListener('click', (e) => this.handleNavClick(e));
        });
        
        // Handle escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen()) {
                this.closeSidebar();
            }
        });
        
        // Initialize chat history display
        this.renderChatHistory();
    }
    
    toggleSidebar() {
        if (this.isOpen()) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    }
    
    openSidebar() {
        this.sidebar?.classList.add('open');
        this.overlay?.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }
    
    closeSidebar() {
        this.sidebar?.classList.remove('open');
        this.overlay?.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
    }
    
    isOpen() {
        return this.sidebar?.classList.contains('open') || false;
    }
    
    handleNavClick(e) {
        const clickedItem = e.currentTarget;
        const feature = clickedItem.dataset.feature;
        
        // Remove active class from all items
        this.navItems.forEach(item => item.classList.remove('active'));
        
        // Add active class to clicked item
        clickedItem.classList.add('active');
        
        // Handle feature navigation
        this.navigateToFeature(feature);
        
        // Close sidebar on mobile after selection
        if (window.innerWidth <= 768) {
            this.closeSidebar();
        }
    }
    
    navigateToFeature(feature) {
        console.log(`Navigating to feature: ${feature}`);
        
        // Hide all feature containers
        const allFeatures = document.querySelectorAll('.feature-container, .chat-div');
        allFeatures.forEach(container => {
            container.classList.add('hidden');
        });
        
        // Show the selected feature
        switch (feature) {
            case 'chat':
                document.querySelector('.chat-div')?.classList.remove('hidden');
                break;
            case 'journal':
                document.querySelector('.journal-div')?.classList.remove('hidden');
                this.initializeJournal();
                break;
            case 'mood':
                document.querySelector('.mood-tracker-div')?.classList.remove('hidden');
                this.initializeMoodTracker();
                break;
            case 'exercises':
                document.querySelector('.exercises-div')?.classList.remove('hidden');
                this.initializeExercises();
                break;
            case 'resources':
                document.querySelector('.resources-div')?.classList.remove('hidden');
                this.initializeResources();
                break;
            case 'progress':
                document.querySelector('.progress-div')?.classList.remove('hidden');
                this.initializeProgress();
                break;
            default:
                console.warn(`Unknown feature: ${feature}`);
                // Fallback to chat
                document.querySelector('.chat-div')?.classList.remove('hidden');
        }
    }
    
    // Feature initialization methods
    initializeJournal() {
        // Set current date
        const currentDateEl = document.getElementById('currentDate');
        if (currentDateEl) {
            currentDateEl.textContent = new Date().toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        }
        
        // Initialize mood selector
        const moodBtns = document.querySelectorAll('.journal-div .mood-btn');
        moodBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                moodBtns.forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
            });
        });
    }
    
    initializeMoodTracker() {
        // Initialize mood scale
        const moodItems = document.querySelectorAll('.mood-scale-item');
        moodItems.forEach(item => {
            item.addEventListener('click', () => {
                moodItems.forEach(i => i.classList.remove('selected'));
                item.classList.add('selected');
            });
        });
        
        // Initialize factor tags
        const factorTags = document.querySelectorAll('.factor-tag');
        factorTags.forEach(tag => {
            tag.addEventListener('click', () => {
                tag.classList.toggle('selected');
            });
        });
    }
    
    initializeExercises() {
        // Initialize category cards
        const categoryCards = document.querySelectorAll('.category-card');
        const exerciseSections = document.querySelectorAll('.exercise-section');
        
        categoryCards.forEach(card => {
            card.addEventListener('click', () => {
                const category = card.dataset.category;
                
                // Update active category
                categoryCards.forEach(c => c.classList.remove('active'));
                card.classList.add('active');
                
                // Show corresponding exercise section
                exerciseSections.forEach(section => section.classList.remove('active'));
                document.querySelector(`.${category}-exercises`)?.classList.add('active');
            });
        });
        
        // Initialize exercise items
        const exerciseItems = document.querySelectorAll('.exercise-item');
        exerciseItems.forEach(item => {
            item.addEventListener('click', () => {
                const exercise = item.dataset.exercise;
                console.log(`Starting exercise: ${exercise}`);
                // TODO: Implement exercise player
            });
        });
    }
    
    initializeResources() {
        // Initialize category filters
        const categoryFilters = document.querySelectorAll('.category-filter');
        const resourceCards = document.querySelectorAll('.resource-card');
        
        categoryFilters.forEach(filter => {
            filter.addEventListener('click', () => {
                const category = filter.dataset.category;
                
                // Update active filter
                categoryFilters.forEach(f => f.classList.remove('active'));
                filter.classList.add('active');
                
                // Filter resource cards
                resourceCards.forEach(card => {
                    if (category === 'all' || card.dataset.category === category) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
    }
    
    initializeProgress() {
        // Initialize progress charts and stats
        console.log('Initializing progress dashboard');
        // TODO: Implement chart rendering
    }
    
    // Chat History Management Methods
    loadChatHistory() {
        try {
            const saved = localStorage.getItem('chillbuddy_chat_history');
            return saved ? JSON.parse(saved) : [];
        } catch (error) {
            console.warn('Failed to load chat history:', error);
            return [];
        }
    }
    
    saveChatHistory() {
        try {
            localStorage.setItem('chillbuddy_chat_history', JSON.stringify(this.chatHistory));
        } catch (error) {
            console.warn('Failed to save chat history:', error);
        }
    }
    
    createNewChat() {
        // Save current chat if it has messages
        const currentMessages = document.querySelectorAll('.message');
        if (currentMessages.length > 0) {
            this.saveCurrentChat();
        }
        
        // Clear current chat
        this.clearCurrentChat();
        
        // Generate new chat ID
        this.currentChatId = 'chat_' + Date.now();
        
        // Update UI
        this.renderChatHistory();
        
        // Close sidebar on mobile
        if (window.innerWidth <= 768) {
            this.closeSidebar();
        }
        
        console.log('New chat created:', this.currentChatId);
    }
    
    saveCurrentChat() {
        const messages = document.querySelectorAll('.message');
        if (messages.length === 0) return;
        
        // Get first user message as title
        const firstUserMessage = Array.from(messages).find(msg => 
            msg.classList.contains('user-message')
        );
        const title = firstUserMessage ? 
            firstUserMessage.textContent.substring(0, 50) + '...' : 
            'Untitled Chat';
        
        // Create chat object
        const chatData = {
            id: this.currentChatId,
            title: title,
            timestamp: Date.now(),
            messages: Array.from(messages).map(msg => ({
                type: msg.classList.contains('user-message') ? 'user' : 'assistant',
                content: msg.innerHTML,
                timestamp: Date.now()
            }))
        };
        
        // Add to history (remove if already exists)
        this.chatHistory = this.chatHistory.filter(chat => chat.id !== this.currentChatId);
        this.chatHistory.unshift(chatData);
        
        // Keep only last 20 chats
        this.chatHistory = this.chatHistory.slice(0, 20);
        
        this.saveChatHistory();
    }
    
    clearCurrentChat() {
        const messagesContainer = document.querySelector('.chat-messages');
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }
        
        // Reset chat input
        const chatInput = document.querySelector('.chat-input textarea');
        if (chatInput) {
            chatInput.value = '';
        }
    }
    
    loadChat(chatId) {
        if (chatId === 'current') {
            // Already on current chat
            return;
        }
        
        // Save current chat first
        const currentMessages = document.querySelectorAll('.message');
        if (currentMessages.length > 0) {
            this.saveCurrentChat();
        }
        
        // Find and load the selected chat
        const chat = this.chatHistory.find(c => c.id === chatId);
        if (!chat) return;
        
        // Clear current messages
        this.clearCurrentChat();
        
        // Load chat messages
        const messagesContainer = document.querySelector('.chat-messages');
        if (messagesContainer && chat.messages) {
            chat.messages.forEach(msg => {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${msg.type}-message`;
                messageDiv.innerHTML = msg.content;
                messagesContainer.appendChild(messageDiv);
            });
            
            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        // Update current chat ID
        this.currentChatId = chatId;
        
        // Update UI
        this.renderChatHistory();
        
        console.log('Loaded chat:', chatId);
    }
    
    renderChatHistory() {
        if (!this.chatHistoryList) return;
        
        // Clear existing items except the current chat placeholder
        this.chatHistoryList.innerHTML = `
            <div class="chat-history-item ${this.currentChatId === 'current' ? 'active' : ''}" data-chat-id="current">
                <div class="chat-preview">
                    <span class="chat-title">Current Chat</span>
                    <span class="chat-time">Now</span>
                </div>
            </div>
        `;
        
        // Add saved chats
        this.chatHistory.forEach(chat => {
            const chatItem = document.createElement('div');
            chatItem.className = `chat-history-item ${chat.id === this.currentChatId ? 'active' : ''}`;
            chatItem.dataset.chatId = chat.id;
            
            const timeAgo = this.getTimeAgo(chat.timestamp);
            
            chatItem.innerHTML = `
                <div class="chat-preview">
                    <span class="chat-title">${chat.title}</span>
                    <span class="chat-time">${timeAgo}</span>
                </div>
            `;
            
            // Add click listener
            chatItem.addEventListener('click', () => {
                // Remove active from all items
                this.chatHistoryList.querySelectorAll('.chat-history-item').forEach(item => {
                    item.classList.remove('active');
                });
                
                // Add active to clicked item
                chatItem.classList.add('active');
                
                // Load the chat
                this.loadChat(chat.id);
                
                // Close sidebar on mobile
                if (window.innerWidth <= 768) {
                    this.closeSidebar();
                }
            });
            
            this.chatHistoryList.appendChild(chatItem);
        });
        
        // Add click listener to current chat item
        const currentChatItem = this.chatHistoryList.querySelector('[data-chat-id="current"]');
        if (currentChatItem) {
            currentChatItem.addEventListener('click', () => {
                // Remove active from all items
                this.chatHistoryList.querySelectorAll('.chat-history-item').forEach(item => {
                    item.classList.remove('active');
                });
                
                // Add active to current chat
                currentChatItem.classList.add('active');
                
                // Load current chat
                this.loadChat('current');
                
                // Close sidebar on mobile
                if (window.innerWidth <= 768) {
                    this.closeSidebar();
                }
            });
        }
    }
    
    getTimeAgo(timestamp) {
        const now = Date.now();
        const diff = now - timestamp;
        
        const minutes = Math.floor(diff / (1000 * 60));
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        
        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days < 7) return `${days}d ago`;
        
        return new Date(timestamp).toLocaleDateString();
    }
}

// Initialize sidebar when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.sidebarManager = new SidebarManager();
    });
} else {
    window.sidebarManager = new SidebarManager();
}