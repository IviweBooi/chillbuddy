/**
 * Journal System
 * Handles journal entry creation, editing, saving, and history management
 */

class JournalSystem {
    constructor() {
        this.entries = this.loadEntries();
        this.currentEntry = null;
        this.isEditing = false;
        this.prompts = this.initializePrompts();
        this.init();
    }

    init() {
        this.setupJournalInterface();
        this.renderEntryHistory();
        this.setupEventListeners();
    }

    initializePrompts() {
        return [
            "How are you feeling today?",
            "What are you grateful for right now?",
            "What challenged you today and how did you handle it?",
            "Describe a moment that made you smile today.",
            "What would you like to let go of?",
            "What are you looking forward to?",
            "How did you take care of yourself today?",
            "What did you learn about yourself today?",
            "What emotions came up for you today?",
            "How would you describe your energy level today?",
            "What patterns do you notice in your thoughts?",
            "What would you tell a friend going through what you're experiencing?",
            "What small win can you celebrate today?",
            "How did you connect with others today?",
            "What does your inner voice sound like today?"
        ];
    }

    setupJournalInterface() {
        const journalBody = document.querySelector('.journal-body');
        if (!journalBody) return;

        const journalHTML = `
            <div class="journal-container">
                <div class="journal-main">
                    <div class="journal-header">
                        <div class="journal-stats">
                            <div class="stat">
                                <span class="stat-icon">📝</span>
                                <span class="stat-value">${this.entries.length}</span>
                                <span class="stat-label">Total Entries</span>
                            </div>
                            <div class="stat">
                                <span class="stat-icon">🔥</span>
                                <span class="stat-value">${this.getStreak()}</span>
                                <span class="stat-label">Day Streak</span>
                            </div>
                            <div class="stat">
                                <span class="stat-icon">📊</span>
                                <span class="stat-value">${this.getAverageWordsPerEntry()}</span>
                                <span class="stat-label">Avg Words</span>
                            </div>
                        </div>
                        <div class="journal-actions">
                            <button class="btn-new-entry" onclick="journalSystem.startNewEntry()">
                                <span class="icon">✏️</span> New Entry
                            </button>
                            <button class="btn-random-prompt" onclick="journalSystem.getRandomPrompt()">
                                <span class="icon">🎲</span> Random Prompt
                            </button>
                        </div>
                    </div>
                    
                    <div class="journal-editor" id="journalEditor" style="display: none;">
                        <div class="editor-header">
                            <div class="entry-date" id="entryDate"></div>
                            <div class="editor-actions">
                                <button class="btn-save" onclick="journalSystem.saveEntry()">
                                    <span class="icon">💾</span> Save
                                </button>
                                <button class="btn-cancel" onclick="journalSystem.cancelEntry()">
                                    <span class="icon">❌</span> Cancel
                                </button>
                            </div>
                        </div>
                        
                        <div class="prompt-section" id="promptSection" style="display: none;">
                            <div class="prompt-text" id="promptText"></div>
                            <button class="btn-dismiss-prompt" onclick="journalSystem.dismissPrompt()">
                                <span class="icon">✖️</span> Write freely
                            </button>
                        </div>
                        
                        <div class="editor-content">
                            <textarea 
                                id="entryTextarea" 
                                placeholder="What's on your mind today? Let your thoughts flow freely..."
                                rows="15"
                            ></textarea>
                            <div class="editor-footer">
                                <div class="word-count">
                                    <span id="wordCount">0</span> words
                                </div>
                                <div class="mood-selector">
                                    <label>How are you feeling?</label>
                                    <div class="mood-options">
                                        <button class="mood-btn" data-mood="1" title="Very Sad">😢</button>
                                        <button class="mood-btn" data-mood="2" title="Sad">😔</button>
                                        <button class="mood-btn" data-mood="3" title="Neutral">😐</button>
                                        <button class="mood-btn" data-mood="4" title="Happy">😊</button>
                                        <button class="mood-btn" data-mood="5" title="Very Happy">😄</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="journal-welcome" id="journalWelcome">
                        <div class="welcome-content">
                            <div class="welcome-icon">📖</div>
                            <h3>Welcome to Your Journal</h3>
                            <p>This is your safe space to express thoughts, feelings, and reflections. Writing regularly can help improve your mental well-being and self-awareness.</p>
                            <div class="welcome-benefits">
                                <div class="benefit">
                                    <span class="benefit-icon">🧠</span>
                                    <span>Improve mental clarity</span>
                                </div>
                                <div class="benefit">
                                    <span class="benefit-icon">💭</span>
                                    <span>Process emotions</span>
                                </div>
                                <div class="benefit">
                                    <span class="benefit-icon">📈</span>
                                    <span>Track personal growth</span>
                                </div>
                                <div class="benefit">
                                    <span class="benefit-icon">🎯</span>
                                    <span>Set and reflect on goals</span>
                                </div>
                            </div>
                            <button class="btn-start-writing" onclick="journalSystem.startNewEntry()">
                                <span class="icon">✨</span> Start Writing
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="journal-sidebar">
                    <div class="sidebar-header">
                        <h4>Recent Entries</h4>
                        <button class="btn-view-all" onclick="journalSystem.showAllEntries()">
                            View All
                        </button>
                    </div>
                    <div class="entry-history" id="entryHistory">
                        <!-- Entry history will be populated here -->
                    </div>
                </div>
            </div>
            
            <!-- Entry View Modal -->
            <div id="entryViewModal" class="modal-overlay entry-modal" style="display: none;">
                <div class="modal-container entry-modal-container">
                    <div class="modal-header">
                        <h2 id="entryViewTitle">Journal Entry</h2>
                        <div class="entry-actions">
                            <button class="btn-edit" onclick="journalSystem.editEntry()">
                                <span class="icon">✏️</span> Edit
                            </button>
                            <button class="btn-delete" onclick="journalSystem.deleteEntry()">
                                <span class="icon">🗑️</span> Delete
                            </button>
                            <button class="close-btn" onclick="journalSystem.closeEntryModal()">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                                    <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                                </svg>
                            </button>
                        </div>
                    </div>
                    <div class="modal-body entry-modal-body">
                        <div class="entry-meta" id="entryMeta"></div>
                        <div class="entry-content" id="entryContent"></div>
                    </div>
                </div>
            </div>
            
            <!-- All Entries Modal -->
            <div id="allEntriesModal" class="modal-overlay entries-modal" style="display: none;">
                <div class="modal-container entries-modal-container">
                    <div class="modal-header">
                        <h2>All Journal Entries</h2>
                        <div class="entries-filters">
                            <select id="sortFilter">
                                <option value="newest">Newest First</option>
                                <option value="oldest">Oldest First</option>
                                <option value="longest">Longest First</option>
                                <option value="shortest">Shortest First</option>
                            </select>
                            <input type="text" id="searchEntries" placeholder="Search entries...">
                        </div>
                        <button class="close-btn" onclick="journalSystem.closeAllEntriesModal()">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                                <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                            </svg>
                        </button>
                    </div>
                    <div class="modal-body entries-modal-body">
                        <div class="all-entries-list" id="allEntriesList">
                            <!-- All entries will be populated here -->
                        </div>
                    </div>
                </div>
            </div>
        `;

        journalBody.innerHTML = journalHTML;
    }

    setupEventListeners() {
        // Textarea word count
        const textarea = document.getElementById('entryTextarea');
        if (textarea) {
            textarea.addEventListener('input', () => {
                this.updateWordCount();
            });
        }

        // Mood selection
        const moodButtons = document.querySelectorAll('.mood-btn');
        moodButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                moodButtons.forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
            });
        });

        // Search functionality
        const searchInput = document.getElementById('searchEntries');
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                this.filterEntries();
            });
        }

        // Sort functionality
        const sortFilter = document.getElementById('sortFilter');
        if (sortFilter) {
            sortFilter.addEventListener('change', () => {
                this.filterEntries();
            });
        }

        // Auto-save functionality
        if (textarea) {
            let autoSaveTimer;
            textarea.addEventListener('input', () => {
                clearTimeout(autoSaveTimer);
                autoSaveTimer = setTimeout(() => {
                    this.autoSave();
                }, 5000); // Auto-save after 5 seconds of inactivity
            });
        }
    }

    startNewEntry() {
        this.currentEntry = {
            id: Date.now(),
            date: new Date().toISOString(),
            content: '',
            mood: null,
            prompt: null,
            wordCount: 0
        };
        this.isEditing = false;
        this.showEditor();
    }

    editEntry(entryId = null) {
        const id = entryId || this.currentEntry?.id;
        const entry = this.entries.find(e => e.id === id);
        if (!entry) return;

        this.currentEntry = { ...entry };
        this.isEditing = true;
        this.closeEntryModal();
        this.showEditor();
        
        // Populate editor with existing content
        const textarea = document.getElementById('entryTextarea');
        if (textarea) {
            textarea.value = entry.content;
            this.updateWordCount();
        }
        
        // Set mood if exists
        if (entry.mood) {
            const moodBtn = document.querySelector(`[data-mood="${entry.mood}"]`);
            if (moodBtn) {
                document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('selected'));
                moodBtn.classList.add('selected');
            }
        }
    }

    showEditor() {
        const editor = document.getElementById('journalEditor');
        const welcome = document.getElementById('journalWelcome');
        const entryDate = document.getElementById('entryDate');
        
        if (editor) editor.style.display = 'block';
        if (welcome) welcome.style.display = 'none';
        
        if (entryDate) {
            const date = new Date(this.currentEntry.date);
            entryDate.textContent = this.isEditing ? 
                `Editing entry from ${date.toLocaleDateString()}` :
                `New entry - ${date.toLocaleDateString()}`;
        }
        
        // Focus on textarea
        const textarea = document.getElementById('entryTextarea');
        if (textarea) {
            textarea.focus();
        }
    }

    hideEditor() {
        const editor = document.getElementById('journalEditor');
        const welcome = document.getElementById('journalWelcome');
        const promptSection = document.getElementById('promptSection');
        
        if (editor) editor.style.display = 'none';
        if (welcome && this.entries.length === 0) welcome.style.display = 'block';
        if (promptSection) promptSection.style.display = 'none';
        
        // Clear editor
        const textarea = document.getElementById('entryTextarea');
        if (textarea) textarea.value = '';
        
        // Clear mood selection
        document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('selected'));
        
        this.currentEntry = null;
        this.isEditing = false;
    }

    getRandomPrompt() {
        const prompt = this.prompts[Math.floor(Math.random() * this.prompts.length)];
        this.showPrompt(prompt);
    }

    showPrompt(prompt) {
        const promptSection = document.getElementById('promptSection');
        const promptText = document.getElementById('promptText');
        
        if (promptSection && promptText) {
            promptText.textContent = prompt;
            promptSection.style.display = 'block';
            
            if (this.currentEntry) {
                this.currentEntry.prompt = prompt;
            }
        }
    }

    dismissPrompt() {
        const promptSection = document.getElementById('promptSection');
        if (promptSection) {
            promptSection.style.display = 'none';
        }
        
        if (this.currentEntry) {
            this.currentEntry.prompt = null;
        }
    }

    updateWordCount() {
        const textarea = document.getElementById('entryTextarea');
        const wordCountEl = document.getElementById('wordCount');
        
        if (textarea && wordCountEl) {
            const words = textarea.value.trim().split(/\s+/).filter(word => word.length > 0);
            const count = words.length;
            wordCountEl.textContent = count;
            
            if (this.currentEntry) {
                this.currentEntry.wordCount = count;
            }
        }
    }

    saveEntry() {
        const textarea = document.getElementById('entryTextarea');
        const selectedMood = document.querySelector('.mood-btn.selected');
        
        if (!textarea || !textarea.value.trim()) {
            this.showNotification('Please write something before saving!', 'warning');
            return;
        }
        
        this.currentEntry.content = textarea.value.trim();
        this.currentEntry.mood = selectedMood ? parseInt(selectedMood.dataset.mood) : null;
        this.currentEntry.lastModified = new Date().toISOString();
        
        if (this.isEditing) {
            // Update existing entry
            const index = this.entries.findIndex(e => e.id === this.currentEntry.id);
            if (index !== -1) {
                this.entries[index] = { ...this.currentEntry };
            }
        } else {
            // Add new entry
            this.entries.unshift(this.currentEntry);
        }
        
        this.saveEntries();
        this.renderEntryHistory();
        this.updateStats();
        this.hideEditor();
        
        // Check achievements
        this.checkAchievements();
        
        // Update progress
        if (window.rewardPreview) {
            window.rewardPreview.updateProgress('journal', 'mindful_writer', this.entries.length, 1);
        }
        
        this.showNotification(
            this.isEditing ? 'Entry updated successfully!' : 'Entry saved successfully!', 
            'success'
        );
    }

    autoSave() {
        if (!this.currentEntry) return;
        
        const textarea = document.getElementById('entryTextarea');
        if (textarea && textarea.value.trim()) {
            // Save to localStorage as draft
            const draft = {
                ...this.currentEntry,
                content: textarea.value.trim(),
                isDraft: true
            };
            
            localStorage.setItem('chillbuddy_journal_draft', JSON.stringify(draft));
            this.showNotification('Draft saved automatically', 'info', 2000);
        }
    }

    cancelEntry() {
        if (this.currentEntry && this.currentEntry.content) {
            if (confirm('Are you sure you want to cancel? Any unsaved changes will be lost.')) {
                this.hideEditor();
                localStorage.removeItem('chillbuddy_journal_draft');
            }
        } else {
            this.hideEditor();
        }
    }

    deleteEntry(entryId = null) {
        const id = entryId || this.currentEntry?.id;
        const entry = this.entries.find(e => e.id === id);
        
        if (!entry) return;
        
        if (confirm('Are you sure you want to delete this entry? This action cannot be undone.')) {
            this.entries = this.entries.filter(e => e.id !== id);
            this.saveEntries();
            this.renderEntryHistory();
            this.updateStats();
            this.closeEntryModal();
            this.showNotification('Entry deleted successfully', 'success');
        }
    }

    viewEntry(entryId) {
        const entry = this.entries.find(e => e.id === entryId);
        if (!entry) return;
        
        this.currentEntry = entry;
        
        const modal = document.getElementById('entryViewModal');
        const title = document.getElementById('entryViewTitle');
        const meta = document.getElementById('entryMeta');
        const content = document.getElementById('entryContent');
        
        const date = new Date(entry.date);
        title.textContent = `Entry from ${date.toLocaleDateString()}`;
        
        const moodEmoji = entry.mood ? ['😢', '😔', '😐', '😊', '😄'][entry.mood - 1] : '';
        const moodText = entry.mood ? ['Very Sad', 'Sad', 'Neutral', 'Happy', 'Very Happy'][entry.mood - 1] : 'No mood recorded';
        
        meta.innerHTML = `
            <div class="entry-meta-grid">
                <div class="meta-item">
                    <span class="meta-label">Date:</span>
                    <span class="meta-value">${date.toLocaleDateString()} at ${date.toLocaleTimeString()}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Word Count:</span>
                    <span class="meta-value">${entry.wordCount || 0} words</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Mood:</span>
                    <span class="meta-value">${moodEmoji} ${moodText}</span>
                </div>
                ${entry.prompt ? `
                    <div class="meta-item prompt-meta">
                        <span class="meta-label">Prompt:</span>
                        <span class="meta-value">"${entry.prompt}"</span>
                    </div>
                ` : ''}
                ${entry.lastModified && entry.lastModified !== entry.date ? `
                    <div class="meta-item">
                        <span class="meta-label">Last Modified:</span>
                        <span class="meta-value">${new Date(entry.lastModified).toLocaleDateString()}</span>
                    </div>
                ` : ''}
            </div>
        `;
        
        content.innerHTML = `<div class="entry-text">${this.formatEntryContent(entry.content)}</div>`;
        
        modal.style.display = 'flex';
    }

    formatEntryContent(content) {
        // Simple formatting: convert line breaks to paragraphs
        return content
            .split('\n\n')
            .map(paragraph => `<p>${paragraph.replace(/\n/g, '<br>')}</p>`)
            .join('');
    }

    closeEntryModal() {
        const modal = document.getElementById('entryViewModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    showAllEntries() {
        const modal = document.getElementById('allEntriesModal');
        if (modal) {
            modal.style.display = 'flex';
            this.renderAllEntries();
        }
    }

    closeAllEntriesModal() {
        const modal = document.getElementById('allEntriesModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    renderAllEntries() {
        const container = document.getElementById('allEntriesList');
        if (!container) return;
        
        let entries = [...this.entries];
        
        // Apply filters
        entries = this.applySortAndFilter(entries);
        
        if (entries.length === 0) {
            container.innerHTML = `
                <div class="no-entries">
                    <div class="no-entries-icon">📝</div>
                    <p>No entries found matching your criteria.</p>
                </div>
            `;
            return;
        }
        
        const entriesHTML = entries.map(entry => {
            const date = new Date(entry.date);
            const preview = entry.content.substring(0, 150) + (entry.content.length > 150 ? '...' : '');
            const moodEmoji = entry.mood ? ['😢', '😔', '😐', '😊', '😄'][entry.mood - 1] : '😐';
            
            return `
                <div class="entry-item" onclick="journalSystem.viewEntry(${entry.id})">
                    <div class="entry-item-header">
                        <div class="entry-date">${date.toLocaleDateString()}</div>
                        <div class="entry-mood">${moodEmoji}</div>
                    </div>
                    <div class="entry-preview">${preview}</div>
                    <div class="entry-item-footer">
                        <span class="word-count">${entry.wordCount || 0} words</span>
                        ${entry.prompt ? '<span class="has-prompt">📝 Prompted</span>' : ''}
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = entriesHTML;
    }

    applySortAndFilter(entries) {
        const searchTerm = document.getElementById('searchEntries')?.value.toLowerCase() || '';
        const sortBy = document.getElementById('sortFilter')?.value || 'newest';
        
        // Filter by search term
        if (searchTerm) {
            entries = entries.filter(entry => 
                entry.content.toLowerCase().includes(searchTerm) ||
                (entry.prompt && entry.prompt.toLowerCase().includes(searchTerm))
            );
        }
        
        // Sort entries
        entries.sort((a, b) => {
            switch (sortBy) {
                case 'oldest':
                    return new Date(a.date) - new Date(b.date);
                case 'longest':
                    return (b.wordCount || 0) - (a.wordCount || 0);
                case 'shortest':
                    return (a.wordCount || 0) - (b.wordCount || 0);
                case 'newest':
                default:
                    return new Date(b.date) - new Date(a.date);
            }
        });
        
        return entries;
    }

    filterEntries() {
        this.renderAllEntries();
    }

    renderEntryHistory() {
        const container = document.getElementById('entryHistory');
        if (!container) return;
        
        const recentEntries = this.entries.slice(0, 5);
        
        if (recentEntries.length === 0) {
            container.innerHTML = `
                <div class="no-recent-entries">
                    <p>No entries yet. Start writing to see your history here!</p>
                </div>
            `;
            return;
        }
        
        const entriesHTML = recentEntries.map(entry => {
            const date = new Date(entry.date);
            const preview = entry.content.substring(0, 80) + (entry.content.length > 80 ? '...' : '');
            const moodEmoji = entry.mood ? ['😢', '😔', '😐', '😊', '😄'][entry.mood - 1] : '😐';
            
            return `
                <div class="history-item" onclick="journalSystem.viewEntry(${entry.id})">
                    <div class="history-header">
                        <span class="history-date">${date.toLocaleDateString()}</span>
                        <span class="history-mood">${moodEmoji}</span>
                    </div>
                    <div class="history-preview">${preview}</div>
                    <div class="history-meta">
                        <span class="word-count">${entry.wordCount || 0} words</span>
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = entriesHTML;
    }

    updateStats() {
        // Update stats in the header
        const statElements = {
            total: document.querySelector('.stat:nth-child(1) .stat-value'),
            streak: document.querySelector('.stat:nth-child(2) .stat-value'),
            avgWords: document.querySelector('.stat:nth-child(3) .stat-value')
        };
        
        if (statElements.total) statElements.total.textContent = this.entries.length;
        if (statElements.streak) statElements.streak.textContent = this.getStreak();
        if (statElements.avgWords) statElements.avgWords.textContent = this.getAverageWordsPerEntry();
    }

    getStreak() {
        if (this.entries.length === 0) return 0;
        
        let streak = 0;
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        for (let i = 0; i < this.entries.length; i++) {
            const entryDate = new Date(this.entries[i].date);
            entryDate.setHours(0, 0, 0, 0);
            
            const daysDiff = Math.floor((today - entryDate) / (1000 * 60 * 60 * 24));
            
            if (daysDiff === streak) {
                streak++;
            } else {
                break;
            }
        }
        
        return streak;
    }

    getAverageWordsPerEntry() {
        if (this.entries.length === 0) return 0;
        
        const totalWords = this.entries.reduce((sum, entry) => sum + (entry.wordCount || 0), 0);
        return Math.round(totalWords / this.entries.length);
    }

    checkAchievements() {
        const achievements = [];
        
        // First entry
        if (this.entries.length === 1) {
            achievements.push({
                id: 'first_journal',
                name: 'Mindful Writer',
                description: 'Wrote your first journal entry!',
                icon: '📝',
                points: 10
            });
        }
        
        // Milestone entries
        const milestones = [5, 10, 25, 50, 100];
        if (milestones.includes(this.entries.length)) {
            achievements.push({
                id: `journal_${this.entries.length}`,
                name: `Journal Master ${this.entries.length}`,
                description: `Wrote ${this.entries.length} journal entries!`,
                icon: '🏆',
                points: this.entries.length * 2
            });
        }
        
        // Streak achievements
        const streak = this.getStreak();
        if ([3, 7, 14, 30].includes(streak)) {
            achievements.push({
                id: `streak_${streak}`,
                name: `${streak} Day Streak`,
                description: `Wrote for ${streak} consecutive days!`,
                icon: '🔥',
                points: streak * 3
            });
        }
        
        // Show achievements
        achievements.forEach(achievement => {
            if (window.achievementNotifications) {
                window.achievementNotifications.showNotification(achievement, 'achievement');
            }
        });
    }

    showNotification(message, type = 'info', duration = 3000) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `journal-notification ${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '10000',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease'
        });
        
        // Set background color based on type
        const colors = {
            success: '#4CAF50',
            warning: '#FF9800',
            error: '#f44336',
            info: '#2196F3'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after duration
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, duration);
    }

    // Data persistence methods
    loadEntries() {
        try {
            const saved = localStorage.getItem('chillbuddy_journal_entries');
            return saved ? JSON.parse(saved) : [];
        } catch (error) {
            console.error('Error loading journal entries:', error);
            return [];
        }
    }

    saveEntries() {
        try {
            localStorage.setItem('chillbuddy_journal_entries', JSON.stringify(this.entries));
        } catch (error) {
            console.error('Error saving journal entries:', error);
        }
    }

    // Public methods for external access
    getEntries() {
        return this.entries;
    }

    getStats() {
        return {
            totalEntries: this.entries.length,
            streak: this.getStreak(),
            averageWords: this.getAverageWordsPerEntry(),
            totalWords: this.entries.reduce((sum, entry) => sum + (entry.wordCount || 0), 0),
            moodDistribution: this.getMoodDistribution()
        };
    }

    getMoodDistribution() {
        const distribution = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
        this.entries.forEach(entry => {
            if (entry.mood) {
                distribution[entry.mood]++;
            }
        });
        return distribution;
    }

    exportEntries() {
        const data = {
            entries: this.entries,
            exportDate: new Date().toISOString(),
            stats: this.getStats()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `chillbuddy-journal-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        URL.revokeObjectURL(url);
        
        this.showNotification('Journal entries exported successfully!', 'success');
    }
}

// Initialize journal system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.journal-div')) {
        window.journalSystem = new JournalSystem();
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = JournalSystem;
}