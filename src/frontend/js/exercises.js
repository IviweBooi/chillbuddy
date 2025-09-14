/**
 * Exercises System
 * Handles breathing exercises, mindfulness activities, and guided sessions
 */

class ExercisesSystem {
    constructor() {
        this.currentCategory = 'breathing';
        this.currentExercise = null;
        this.isActive = false;
        this.timer = null;
        this.exerciseHistory = this.loadExerciseHistory();
        this.exercises = this.initializeExercises();
        this.init();
    }

    init() {
        this.initializeCategoryCards();
        this.renderExerciseList();
        this.setupExerciseModal();
    }

    initializeExercises() {
        return {
            breathing: [
                {
                    id: 'box_breathing',
                    name: 'Box Breathing',
                    description: 'Equal counts for inhale, hold, exhale, hold',
                    duration: 300, // 5 minutes
                    difficulty: 'Beginner',
                    icon: '📦',
                    instructions: [
                        'Sit comfortably with your back straight',
                        'Inhale through your nose for 4 counts',
                        'Hold your breath for 4 counts',
                        'Exhale through your mouth for 4 counts',
                        'Hold empty for 4 counts',
                        'Repeat the cycle'
                    ],
                    benefits: ['Reduces stress', 'Improves focus', 'Calms nervous system']
                },
                {
                    id: '478_breathing',
                    name: '4-7-8 Breathing',
                    description: 'Powerful technique for relaxation and sleep',
                    duration: 240, // 4 minutes
                    difficulty: 'Intermediate',
                    icon: '🌙',
                    instructions: [
                        'Place tongue tip behind upper front teeth',
                        'Exhale completely through your mouth',
                        'Inhale through nose for 4 counts',
                        'Hold breath for 7 counts',
                        'Exhale through mouth for 8 counts',
                        'Repeat 3-4 cycles'
                    ],
                    benefits: ['Promotes sleep', 'Reduces anxiety', 'Lowers heart rate']
                },
                {
                    id: 'belly_breathing',
                    name: 'Belly Breathing',
                    description: 'Deep diaphragmatic breathing for relaxation',
                    duration: 600, // 10 minutes
                    difficulty: 'Beginner',
                    icon: '🫁',
                    instructions: [
                        'Lie down or sit comfortably',
                        'Place one hand on chest, one on belly',
                        'Breathe slowly through your nose',
                        'Feel your belly rise, chest stays still',
                        'Exhale slowly through pursed lips',
                        'Focus on the belly movement'
                    ],
                    benefits: ['Reduces stress', 'Improves oxygen flow', 'Calms mind']
                }
            ],
            mindfulness: [
                {
                    id: 'body_scan',
                    name: 'Body Scan Meditation',
                    description: 'Progressive relaxation through body awareness',
                    duration: 900, // 15 minutes
                    difficulty: 'Beginner',
                    icon: '🧘',
                    instructions: [
                        'Lie down comfortably',
                        'Close your eyes and breathe naturally',
                        'Start with your toes, notice any sensations',
                        'Slowly move attention up through your body',
                        'Spend 30 seconds on each body part',
                        'End at the top of your head'
                    ],
                    benefits: ['Reduces tension', 'Increases awareness', 'Promotes relaxation']
                },
                {
                    id: 'mindful_observation',
                    name: 'Mindful Observation',
                    description: 'Present-moment awareness through observation',
                    duration: 300, // 5 minutes
                    difficulty: 'Beginner',
                    icon: '👁️',
                    instructions: [
                        'Choose an object to focus on',
                        'Observe it as if seeing it for the first time',
                        'Notice colors, textures, shapes',
                        'When mind wanders, gently return focus',
                        'Stay curious and non-judgmental',
                        'End by taking three deep breaths'
                    ],
                    benefits: ['Improves focus', 'Reduces rumination', 'Enhances presence']
                },
                {
                    id: 'loving_kindness',
                    name: 'Loving-Kindness Meditation',
                    description: 'Cultivate compassion for self and others',
                    duration: 720, // 12 minutes
                    difficulty: 'Intermediate',
                    icon: '💝',
                    instructions: [
                        'Sit comfortably and close your eyes',
                        'Start with yourself: "May I be happy and healthy"',
                        'Extend to loved ones: "May you be happy"',
                        'Include neutral people in your life',
                        'Extend to difficult people',
                        'End with all beings everywhere'
                    ],
                    benefits: ['Increases compassion', 'Reduces negative emotions', 'Improves relationships']
                },
                {
                    id: 'mindful_walking',
                    name: 'Mindful Walking',
                    description: 'Moving meditation for grounding',
                    duration: 600, // 10 minutes
                    difficulty: 'Beginner',
                    icon: '🚶',
                    instructions: [
                        'Find a quiet path 10-20 steps long',
                        'Walk slower than normal',
                        'Feel each step: lifting, moving, placing',
                        'Notice the sensations in your feet',
                        'When you reach the end, pause and turn',
                        'Continue walking back and forth'
                    ],
                    benefits: ['Grounds energy', 'Improves balance', 'Connects mind-body']
                }
            ]
        };
    }

    initializeCategoryCards() {
        const categoryCards = document.querySelectorAll('.category-card');
        categoryCards.forEach(card => {
            card.addEventListener('click', () => {
                // Remove active class from all cards
                categoryCards.forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked card
                card.classList.add('active');
                
                // Update current category
                this.currentCategory = card.dataset.category;
                
                // Render exercises for this category
                this.renderExerciseList();
            });
        });
    }

    renderExerciseList() {
        const exerciseContainer = document.querySelector('.exercise-list');
        if (!exerciseContainer) {
            // Create exercise list container if it doesn't exist
            this.createExerciseContainer();
            return;
        }

        const exercises = this.exercises[this.currentCategory] || [];
        
        const exerciseHTML = exercises.map(exercise => `
            <div class="exercise-card" data-exercise-id="${exercise.id}">
                <div class="exercise-header">
                    <div class="exercise-icon">${exercise.icon}</div>
                    <div class="exercise-info">
                        <h4>${exercise.name}</h4>
                        <p>${exercise.description}</p>
                    </div>
                    <div class="exercise-meta">
                        <span class="duration">${this.formatDuration(exercise.duration)}</span>
                        <span class="difficulty ${exercise.difficulty.toLowerCase()}">${exercise.difficulty}</span>
                    </div>
                </div>
                <div class="exercise-benefits">
                    <strong>Benefits:</strong>
                    <ul>
                        ${exercise.benefits.map(benefit => `<li>${benefit}</li>`).join('')}
                    </ul>
                </div>
                <div class="exercise-actions">
                    <button class="btn-start" onclick="exercisesSystem.startExercise('${exercise.id}')">
                        <span class="icon">▶️</span> Start Exercise
                    </button>
                    <button class="btn-preview" onclick="exercisesSystem.previewExercise('${exercise.id}')">
                        <span class="icon">👁️</span> Preview
                    </button>
                </div>
            </div>
        `).join('');
        
        exerciseContainer.innerHTML = exerciseHTML;
    }

    createExerciseContainer() {
        const exercisesBody = document.querySelector('.exercises-body');
        if (!exercisesBody) return;
        
        const exerciseListHTML = `
            <div class="exercise-list-container">
                <div class="exercise-list-header">
                    <h3 id="categoryTitle">${this.currentCategory.charAt(0).toUpperCase() + this.currentCategory.slice(1)} Exercises</h3>
                    <div class="exercise-stats">
                        <span class="stat">
                            <span class="stat-icon">🏆</span>
                            <span class="stat-value">${this.getCompletedCount()}</span>
                            <span class="stat-label">Completed</span>
                        </span>
                        <span class="stat">
                            <span class="stat-icon">⏱️</span>
                            <span class="stat-value">${this.getTotalTime()}</span>
                            <span class="stat-label">Total Time</span>
                        </span>
                    </div>
                </div>
                <div class="exercise-list"></div>
            </div>
        `;
        
        exercisesBody.insertAdjacentHTML('beforeend', exerciseListHTML);
        this.renderExerciseList();
    }

    setupExerciseModal() {
        // Create modal if it doesn't exist
        if (!document.getElementById('exerciseModal')) {
            this.createExerciseModal();
        }
    }

    createExerciseModal() {
        const modalHTML = `
            <div id="exerciseModal" class="modal-overlay exercise-modal" style="display: none;">
                <div class="modal-container exercise-modal-container">
                    <div class="modal-header">
                        <h2 id="exerciseModalTitle">Exercise</h2>
                        <button class="close-btn" onclick="exercisesSystem.closeExerciseModal()">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                                <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                            </svg>
                        </button>
                    </div>
                    <div class="modal-body exercise-modal-body">
                        <div class="exercise-content">
                            <div class="exercise-instructions" id="exerciseInstructions"></div>
                            <div class="exercise-timer" id="exerciseTimer">
                                <div class="timer-display">
                                    <span class="time-remaining">00:00</span>
                                    <div class="timer-progress">
                                        <div class="progress-bar"></div>
                                    </div>
                                </div>
                                <div class="timer-controls">
                                    <button class="btn-timer" id="startPauseBtn" onclick="exercisesSystem.toggleTimer()">
                                        <span class="icon">▶️</span> Start
                                    </button>
                                    <button class="btn-timer" id="resetBtn" onclick="exercisesSystem.resetTimer()">
                                        <span class="icon">🔄</span> Reset
                                    </button>
                                    <button class="btn-timer" id="completeBtn" onclick="exercisesSystem.completeExercise()" style="display: none;">
                                        <span class="icon">✅</span> Complete
                                    </button>
                                </div>
                            </div>
                            <div class="breathing-guide" id="breathingGuide" style="display: none;">
                                <div class="breathing-circle">
                                    <div class="circle-inner"></div>
                                    <div class="breathing-text">Breathe</div>
                                </div>
                                <div class="breathing-instructions">
                                    <span id="breathingPhase">Prepare to begin</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    previewExercise(exerciseId) {
        const exercise = this.findExercise(exerciseId);
        if (!exercise) return;
        
        const modal = document.getElementById('exerciseModal');
        const title = document.getElementById('exerciseModalTitle');
        const instructions = document.getElementById('exerciseInstructions');
        const timer = document.getElementById('exerciseTimer');
        const breathingGuide = document.getElementById('breathingGuide');
        
        title.textContent = `${exercise.icon} ${exercise.name}`;
        
        const instructionsHTML = `
            <div class="exercise-preview">
                <div class="exercise-description">
                    <p>${exercise.description}</p>
                    <div class="exercise-details">
                        <span class="detail"><strong>Duration:</strong> ${this.formatDuration(exercise.duration)}</span>
                        <span class="detail"><strong>Difficulty:</strong> ${exercise.difficulty}</span>
                    </div>
                </div>
                <div class="exercise-steps">
                    <h4>Instructions:</h4>
                    <ol>
                        ${exercise.instructions.map(step => `<li>${step}</li>`).join('')}
                    </ol>
                </div>
                <div class="exercise-benefits-preview">
                    <h4>Benefits:</h4>
                    <ul>
                        ${exercise.benefits.map(benefit => `<li>${benefit}</li>`).join('')}
                    </ul>
                </div>
                <div class="preview-actions">
                    <button class="btn-primary" onclick="exercisesSystem.startExercise('${exercise.id}')">
                        <span class="icon">▶️</span> Start Exercise
                    </button>
                </div>
            </div>
        `;
        
        instructions.innerHTML = instructionsHTML;
        timer.style.display = 'none';
        breathingGuide.style.display = 'none';
        
        modal.style.display = 'flex';
    }

    startExercise(exerciseId) {
        const exercise = this.findExercise(exerciseId);
        if (!exercise) return;
        
        this.currentExercise = exercise;
        this.isActive = false;
        
        const modal = document.getElementById('exerciseModal');
        const title = document.getElementById('exerciseModalTitle');
        const instructions = document.getElementById('exerciseInstructions');
        const timer = document.getElementById('exerciseTimer');
        const breathingGuide = document.getElementById('breathingGuide');
        
        title.textContent = `${exercise.icon} ${exercise.name}`;
        
        // Show quick instructions
        instructions.innerHTML = `
            <div class="exercise-active-instructions">
                <p><strong>Remember:</strong> ${exercise.description}</p>
                <div class="key-points">
                    ${exercise.instructions.slice(0, 3).map(step => `<div class="key-point">• ${step}</div>`).join('')}
                </div>
            </div>
        `;
        
        // Setup timer
        this.setupTimer(exercise.duration);
        timer.style.display = 'block';
        
        // Show breathing guide for breathing exercises
        if (this.currentCategory === 'breathing') {
            breathingGuide.style.display = 'block';
            this.setupBreathingGuide(exercise);
        } else {
            breathingGuide.style.display = 'none';
        }
        
        modal.style.display = 'flex';
    }

    setupTimer(duration) {
        this.timeRemaining = duration;
        this.totalDuration = duration;
        this.updateTimerDisplay();
        
        const startPauseBtn = document.getElementById('startPauseBtn');
        const completeBtn = document.getElementById('completeBtn');
        
        startPauseBtn.innerHTML = '<span class="icon">▶️</span> Start';
        completeBtn.style.display = 'none';
    }

    setupBreathingGuide(exercise) {
        const breathingText = document.querySelector('.breathing-text');
        const breathingPhase = document.getElementById('breathingPhase');
        
        breathingText.textContent = 'Ready';
        breathingPhase.textContent = 'Click Start when ready';
    }

    toggleTimer() {
        if (this.isActive) {
            this.pauseTimer();
        } else {
            this.startTimer();
        }
    }

    startTimer() {
        this.isActive = true;
        const startPauseBtn = document.getElementById('startPauseBtn');
        startPauseBtn.innerHTML = '<span class="icon">⏸️</span> Pause';
        
        if (this.currentCategory === 'breathing') {
            this.startBreathingGuide();
        }
        
        this.timer = setInterval(() => {
            this.timeRemaining--;
            this.updateTimerDisplay();
            
            if (this.timeRemaining <= 0) {
                this.completeExercise();
            }
        }, 1000);
    }

    pauseTimer() {
        this.isActive = false;
        clearInterval(this.timer);
        
        const startPauseBtn = document.getElementById('startPauseBtn');
        startPauseBtn.innerHTML = '<span class="icon">▶️</span> Resume';
        
        if (this.currentCategory === 'breathing') {
            this.pauseBreathingGuide();
        }
    }

    resetTimer() {
        this.isActive = false;
        clearInterval(this.timer);
        
        this.timeRemaining = this.totalDuration;
        this.updateTimerDisplay();
        
        const startPauseBtn = document.getElementById('startPauseBtn');
        const completeBtn = document.getElementById('completeBtn');
        
        startPauseBtn.innerHTML = '<span class="icon">▶️</span> Start';
        completeBtn.style.display = 'none';
        
        if (this.currentCategory === 'breathing') {
            this.resetBreathingGuide();
        }
    }

    updateTimerDisplay() {
        const timeDisplay = document.querySelector('.time-remaining');
        const progressBar = document.querySelector('.progress-bar');
        
        if (timeDisplay) {
            const minutes = Math.floor(this.timeRemaining / 60);
            const seconds = this.timeRemaining % 60;
            timeDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
        
        if (progressBar) {
            const progress = ((this.totalDuration - this.timeRemaining) / this.totalDuration) * 100;
            progressBar.style.width = `${progress}%`;
        }
        
        // Show complete button when 30 seconds or less remaining
        const completeBtn = document.getElementById('completeBtn');
        if (completeBtn && this.timeRemaining <= 30 && this.isActive) {
            completeBtn.style.display = 'inline-block';
        }
    }

    startBreathingGuide() {
        const circle = document.querySelector('.breathing-circle');
        const breathingText = document.querySelector('.breathing-text');
        const breathingPhase = document.getElementById('breathingPhase');
        
        if (!this.currentExercise) return;
        
        // Different breathing patterns
        let pattern;
        if (this.currentExercise.id === 'box_breathing') {
            pattern = { inhale: 4, hold1: 4, exhale: 4, hold2: 4 };
        } else if (this.currentExercise.id === '478_breathing') {
            pattern = { inhale: 4, hold1: 7, exhale: 8, hold2: 0 };
        } else {
            pattern = { inhale: 4, hold1: 0, exhale: 6, hold2: 0 };
        }
        
        this.breathingCycle(pattern, circle, breathingText, breathingPhase);
    }

    breathingCycle(pattern, circle, breathingText, breathingPhase) {
        if (!this.isActive) return;
        
        const phases = [
            { name: 'Inhale', duration: pattern.inhale, text: 'Breathe In', scale: 1.5 },
            { name: 'Hold', duration: pattern.hold1, text: 'Hold', scale: 1.5 },
            { name: 'Exhale', duration: pattern.exhale, text: 'Breathe Out', scale: 1 },
            { name: 'Hold', duration: pattern.hold2, text: 'Hold', scale: 1 }
        ].filter(phase => phase.duration > 0);
        
        let currentPhaseIndex = 0;
        
        const runPhase = () => {
            if (!this.isActive) return;
            
            const phase = phases[currentPhaseIndex];
            breathingText.textContent = phase.text;
            breathingPhase.textContent = `${phase.name} for ${phase.duration} seconds`;
            
            // Animate circle
            circle.style.transform = `scale(${phase.scale})`;
            circle.style.transition = `transform ${phase.duration}s ease-in-out`;
            
            setTimeout(() => {
                currentPhaseIndex = (currentPhaseIndex + 1) % phases.length;
                runPhase();
            }, phase.duration * 1000);
        };
        
        runPhase();
    }

    pauseBreathingGuide() {
        const breathingPhase = document.getElementById('breathingPhase');
        breathingPhase.textContent = 'Paused - Click Resume to continue';
    }

    resetBreathingGuide() {
        const circle = document.querySelector('.breathing-circle');
        const breathingText = document.querySelector('.breathing-text');
        const breathingPhase = document.getElementById('breathingPhase');
        
        circle.style.transform = 'scale(1)';
        circle.style.transition = 'transform 0.3s ease';
        breathingText.textContent = 'Ready';
        breathingPhase.textContent = 'Click Start when ready';
    }

    completeExercise() {
        this.isActive = false;
        clearInterval(this.timer);
        
        if (!this.currentExercise) return;
        
        // Record completion
        const completion = {
            id: Date.now(),
            exerciseId: this.currentExercise.id,
            exerciseName: this.currentExercise.name,
            category: this.currentCategory,
            duration: this.totalDuration - this.timeRemaining,
            completedAt: new Date().toISOString(),
            date: new Date().toLocaleDateString()
        };
        
        this.exerciseHistory.unshift(completion);
        
        // Keep only last 50 completions
        if (this.exerciseHistory.length > 50) {
            this.exerciseHistory = this.exerciseHistory.slice(0, 50);
        }
        
        this.saveExerciseHistory();
        
        // Update progress
        if (window.rewardPreview) {
            window.rewardPreview.updateProgress('exercise', 'wellness_warrior', this.exerciseHistory.length, 1);
        }
        
        // Show completion message
        this.showCompletionMessage();
        
        // Check achievements
        this.checkAchievements(completion);
        
        // Close modal after a delay
        setTimeout(() => {
            this.closeExerciseModal();
        }, 3000);
    }

    showCompletionMessage() {
        const modal = document.querySelector('.exercise-modal-body');
        const completionHTML = `
            <div class="exercise-completion">
                <div class="completion-icon">🎉</div>
                <h3>Exercise Complete!</h3>
                <p>Great job completing the ${this.currentExercise.name}!</p>
                <div class="completion-stats">
                    <div class="stat">
                        <span class="stat-value">${this.formatDuration(this.totalDuration - this.timeRemaining)}</span>
                        <span class="stat-label">Time Practiced</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">+${this.currentCategory === 'breathing' ? 5 : 10}</span>
                        <span class="stat-label">Points Earned</span>
                    </div>
                </div>
                <div class="completion-benefits">
                    <h4>Benefits you just gained:</h4>
                    <ul>
                        ${this.currentExercise.benefits.map(benefit => `<li>✅ ${benefit}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
        
        modal.innerHTML = completionHTML;
    }

    checkAchievements(completion) {
        const achievements = [];
        
        // First exercise
        if (this.exerciseHistory.length === 1) {
            achievements.push({
                id: 'first_exercise',
                name: 'Wellness Warrior',
                description: 'Completed your first exercise!',
                icon: '🧘',
                points: 15
            });
        }
        
        // Category-specific achievements
        const categoryCount = this.exerciseHistory.filter(h => h.category === this.currentCategory).length;
        if (categoryCount === 5) {
            achievements.push({
                id: `${this.currentCategory}_master`,
                name: `${this.currentCategory.charAt(0).toUpperCase() + this.currentCategory.slice(1)} Master`,
                description: `Completed 5 ${this.currentCategory} exercises!`,
                icon: this.currentCategory === 'breathing' ? '🫁' : '🧘',
                points: 25
            });
        }
        
        // Show achievements
        achievements.forEach(achievement => {
            if (window.achievementNotifications) {
                window.achievementNotifications.showNotification(achievement, 'achievement');
            }
        });
    }

    closeExerciseModal() {
        const modal = document.getElementById('exerciseModal');
        if (modal) {
            modal.style.display = 'none';
        }
        
        // Clean up timer
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
        
        this.isActive = false;
        this.currentExercise = null;
        
        // Update exercise list to reflect new completions
        this.renderExerciseList();
    }

    // Utility methods
    findExercise(exerciseId) {
        for (const category in this.exercises) {
            const exercise = this.exercises[category].find(ex => ex.id === exerciseId);
            if (exercise) return exercise;
        }
        return null;
    }

    formatDuration(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        
        if (minutes === 0) {
            return `${remainingSeconds}s`;
        } else if (remainingSeconds === 0) {
            return `${minutes}m`;
        } else {
            return `${minutes}m ${remainingSeconds}s`;
        }
    }

    getCompletedCount() {
        return this.exerciseHistory.length;
    }

    getTotalTime() {
        const totalSeconds = this.exerciseHistory.reduce((total, completion) => total + completion.duration, 0);
        return this.formatDuration(totalSeconds);
    }

    loadExerciseHistory() {
        try {
            const saved = localStorage.getItem('chillbuddy_exercise_history');
            return saved ? JSON.parse(saved) : [];
        } catch (error) {
            console.error('Error loading exercise history:', error);
            return [];
        }
    }

    saveExerciseHistory() {
        try {
            localStorage.setItem('chillbuddy_exercise_history', JSON.stringify(this.exerciseHistory));
        } catch (error) {
            console.error('Error saving exercise history:', error);
        }
    }

    // Public methods
    getExerciseHistory() {
        return this.exerciseHistory;
    }

    getCompletionStats() {
        const stats = {
            total: this.exerciseHistory.length,
            breathing: this.exerciseHistory.filter(h => h.category === 'breathing').length,
            mindfulness: this.exerciseHistory.filter(h => h.category === 'mindfulness').length,
            totalTime: this.exerciseHistory.reduce((total, h) => total + h.duration, 0)
        };
        
        return stats;
    }
}

// Initialize exercises system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.exercises-div')) {
        window.exercisesSystem = new ExercisesSystem();
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ExercisesSystem;
}