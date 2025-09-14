/**
 * Main JavaScript file for ChillBuddy UI interactions.
 */

const DAILY_API_LIMIT = 25; // Set the daily message limit per user

/**
 * A simple markdown-to-HTML parser.
 * Handles paragraphs, bold text, and numbered lists.
 * @param {string} text The raw text from the bot.
 * @returns {string} The formatted HTML string.
 */
function parseMarkdown(text) {
    // Process block-level elements first (lists), then inline elements.
    const lines = text.split('\n');
    let html = '';
    let inList = false;

    for (const line of lines) {
        if (/^\d+\.\s/.test(line)) { // Handle numbered lists
            if (!inList) {
                html += '<ol>';
                inList = true;
            }
            html += `<li>${line.replace(/^\d+\.\s/, '')}</li>`;
        } else { // Handle paragraphs
            if (inList) {
                html += '</ol>';
                inList = false;
            }
            if (line.trim()) {
                html += `<p>${line}</p>`;
            }
        }
    }

    if (inList) { // Close any open list at the end
        html += '</ol>';
    }

    // Process inline elements like bold
    return html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
}

/**
 * Gets the current API call count from localStorage for the current day.
 * Resets the count if it's a new day.
 * @returns {{count: number, date: string}}
 */
function getApiCallCount() {
    const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD format
    const usageData = localStorage.getItem('apiUsage');
    let usage = usageData ? JSON.parse(usageData) : { count: 0, date: '' };

    if (usage.date !== today) {
        usage = { count: 0, date: today };
        localStorage.setItem('apiUsage', JSON.stringify(usage));
    }
    return usage;
}

/**
 * Increments the API call count in localStorage.
 */
function incrementApiCallCount() {
    let usage = getApiCallCount(); // Ensures date is current before incrementing
    usage.count++;
    localStorage.setItem('apiUsage', JSON.stringify(usage));
}

document.addEventListener('DOMContentLoaded', () => {
    // Mobile tooltip functionality
    const handleMobileTooltip = (event) => {
        if (window.innerWidth > 768) return; // Only for mobile
        
        const element = event.currentTarget;
        element.classList.add('show-tooltip');
        
        // Remove any existing timeout to prevent multiple timeouts
        if (element.tooltipTimeout) {
            clearTimeout(element.tooltipTimeout);
        }
        
        // Hide tooltip after 3 seconds
        element.tooltipTimeout = setTimeout(() => {
            element.classList.remove('show-tooltip');
        }, 3000);
    };
    
    // Add touch event listeners to all elements with data-tooltip on mobile
    const addMobileTooltipListeners = () => {
        if (window.innerWidth <= 768) {
            document.querySelectorAll('[data-tooltip]').forEach(element => {
                element.addEventListener('touchstart', handleMobileTooltip);
            });
        }
    };
    
    // Initialize mobile tooltips
    addMobileTooltipListeners();
    
    // Re-initialize on window resize
    window.addEventListener('resize', addMobileTooltipListeners);

    let startAnimation = () => {};
    let stopAnimation = () => {};

    // --- Theme Dropdown Functionality ---
    const settingsBtn = document.querySelector('.settings-btn');
    const rightHeaderDiv = document.querySelector('.right-header-div');

    if (settingsBtn && rightHeaderDiv) {
        settingsBtn.addEventListener('click', (event) => {
            // Toggles the dropdown visibility
            rightHeaderDiv.classList.toggle('show-themes');
            // Prevents the window click listener from immediately closing the dropdown
            event.stopPropagation();
        });
    }

    // Add a listener to the whole window to close the dropdown when clicking anywhere else
    window.addEventListener('click', (event) => {
        // Close theme dropdown
        if (rightHeaderDiv.classList.contains('show-themes')) {
            rightHeaderDiv.classList.remove('show-themes');
        }

        // Close emoji picker
        if (emojiPicker && !emojiPicker.classList.contains('hidden')) {
            emojiPicker.classList.add('hidden');
        }
    });

    // --- Theme Switching Functionality ---
    const lightModeBtn = document.querySelector('.light-mode-btn');
    const darkModeBtn = document.querySelector('.dark-mode-btn');
    const systemModeBtn = document.querySelector('.system-mode-btn');

    const applyTheme = (theme) => {
        if (theme === 'dark') {
            document.documentElement.classList.remove('dark-theme-preload');
            document.body.classList.add('dark-theme');
            if (canvas) {
                canvas.classList.add('active');
                startAnimation();
            }
        } else {
            document.body.classList.remove('dark-theme');
            document.documentElement.classList.remove('dark-theme-preload');
            if (canvas) {
                canvas.classList.remove('active');
                stopAnimation();
            }
        }
    };

    const handleSystemTheme = () => {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            applyTheme('dark');
        } else {
            applyTheme('light');
        }
    };

    const loadTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            applyTheme(savedTheme);
        } else {
            // Default to system theme if nothing is saved
            handleSystemTheme();
        }
    };

    lightModeBtn.addEventListener('click', () => {
        localStorage.setItem('theme', 'light');
        applyTheme('light');
    });
    darkModeBtn.addEventListener('click', () => {
        localStorage.setItem('theme', 'dark');
        applyTheme('dark');
    });
    systemModeBtn.addEventListener('click', () => {
        localStorage.removeItem('theme');
        handleSystemTheme();
    });

    // Listen for changes in OS theme preference
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        // Only update if user has not set a specific preference (i.e., is on 'system')
        if (!localStorage.getItem('theme')) {
            handleSystemTheme();
        }
    });

    // --- Chat Input Button Toggle ---
    const chatInput = document.querySelector('.chat-input input[type="text"]');
    const micBtn = document.querySelector('.mic-btn');
    const sendBtn = document.querySelector('.send-btn');

    if (chatInput && micBtn && sendBtn) {
        chatInput.addEventListener('input', () => {
            if (chatInput.value.trim() !== '') {
                // User is typing, show send button
                micBtn.classList.add('hidden');
                sendBtn.classList.remove('hidden');
            } else {
                // Input is empty, show mic button
                micBtn.classList.remove('hidden');
                sendBtn.classList.add('hidden');
            }
        });
    }

    // --- Emoji Picker Functionality ---
    const emojiBtn = document.querySelector('.emoji-btn');
    const emojiPicker = document.querySelector('emoji-picker');

    if (emojiBtn && emojiPicker && chatInput) {
        emojiBtn.addEventListener('click', (event) => {
            event.stopPropagation(); // Prevent window listener from closing it immediately
            emojiPicker.classList.toggle('hidden');

            // If we are showing the picker, calculate its position
            if (!emojiPicker.classList.contains('hidden')) {
                const btnRect = emojiBtn.getBoundingClientRect();
                
                // Position the bottom of the picker 10px above the top of the button
                emojiPicker.style.left = `${btnRect.left}px`;
                emojiPicker.style.bottom = `${window.innerHeight - btnRect.top + 10}px`;
                
                emojiPicker.style.top = ''; // Clear top property to avoid conflicts
            }
        });

        emojiPicker.addEventListener('emoji-click', event => {
            chatInput.value += event.detail.unicode;
            // Manually trigger the input event to update the send/mic button visibility
            chatInput.dispatchEvent(new Event('input'));
            // Focus the input after adding an emoji
            chatInput.focus();
        });

        // Prevent clicks inside the picker from closing it
        emojiPicker.addEventListener('click', event => {
            event.stopPropagation();
        });
    }

    // --- Speech Recognition (Microphone) Functionality ---
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition;

    // Web Audio API for visualization
    let audioContext;
    let analyser;
    let microphoneStream;
    let animationFrameId;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = 'en-US';
        recognition.interimResults = false;

        const visualize = () => {
            if (!analyser) return;
            const bufferLength = analyser.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);
            analyser.getByteFrequencyData(dataArray);

            let sum = 0;
            for (let i = 0; i < bufferLength; i++) {
                sum += dataArray[i];
            }
            const average = sum / bufferLength;

            // Scale the animation based on the average volume.
            const scale = 1 + (average / 256) * 0.1; // Scale up to 1.1
            const shadowOpacity = Math.min(average / 100, 0.7);
            
            micBtn.style.transform = `scale(${scale})`;
            micBtn.style.boxShadow = `0 0 10px rgba(220, 38, 38, ${shadowOpacity})`;

            animationFrameId = requestAnimationFrame(visualize);
        };

        micBtn.addEventListener('click', () => {
            if (micBtn.classList.contains('is-listening')) {
                recognition.stop();
                return;
            }
            
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    microphoneStream = stream;
                    audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    analyser = audioContext.createAnalyser();
                    const source = audioContext.createMediaStreamSource(stream);
                    source.connect(analyser);
                    analyser.fftSize = 512;
                    recognition.start();
                })
                .catch(err => {
                    console.error("Error accessing microphone for visualization:", err);
                    recognition.start(); // Fallback to start without visualization
                });
        });

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            chatInput.value = transcript;
            // Manually trigger the input event to show the send button
            chatInput.dispatchEvent(new Event('input'));
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
        };

        recognition.onstart = () => {
            micBtn.classList.add('is-listening');
            visualize();
        };

        recognition.onend = () => {
            micBtn.classList.remove('is-listening');
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
                animationFrameId = null;
            }
            if (microphoneStream) {
                microphoneStream.getTracks().forEach(track => track.stop());
                microphoneStream = null;
            }
            if (audioContext) {
                audioContext.close();
                audioContext = null;
            }
            // Reset inline styles
            micBtn.style.transform = '';
            micBtn.style.boxShadow = '';
        };
    } else {
        // Hide the mic button if the browser doesn't support the API
        if (micBtn) micBtn.classList.add('hidden');
    }

    // --- Suggested Prompts Functionality ---
    const suggestedPromptButtons = document.querySelectorAll('.suggested-prompts button');

    if (suggestedPromptButtons.length > 0 && chatInput) {
        suggestedPromptButtons.forEach(button => {
            button.addEventListener('click', () => {
                const promptText = button.textContent;
                chatInput.value = promptText;

                // Manually trigger the input event to update the send/mic button visibility
                chatInput.dispatchEvent(new Event('input'));

                // Set focus to the input field for a better user experience
                chatInput.focus();
            });
        });
    }

    // --- Dynamic Suggested Prompts ---
    // These prompts match exactly with the hardcoded responses for instant replies
    const allPrompts = [
        'How can I reduce stress?',
        'Give me a motivational quote',
        'Suggest a 5-minute meditation',
        'Tell me a fun fact',
        'What are some good breathing exercises?',
        'Write a short, calming story',
        'How can I improve my focus?',
        'Give me a positive affirmation',
        'Suggest a relaxing activity',
        'What is a simple mindfulness exercise?',
        'Tell me a joke'
    ];

    const updateSuggestedPrompts = () => {
        if (suggestedPromptButtons.length === 0) {
            return;
        }

        // 1. Add a class to trigger the fade-out animation
        suggestedPromptButtons.forEach(button => {
            button.classList.add('prompt-fade-out');
        });

        // 2. Wait for the animation to finish before changing the text
        setTimeout(() => {
            const shuffledPrompts = [...allPrompts].sort(() => 0.5 - Math.random());

            suggestedPromptButtons.forEach((button, index) => {
                button.textContent = shuffledPrompts[index];
            });

            // 3. Remove the class to trigger the fade-in animation
            suggestedPromptButtons.forEach(button => {
                button.classList.remove('prompt-fade-out');
            });
        }, 200); // This duration should match the CSS transition
    };

    // --- Send Message Functionality ---
    const chatMessagesContainer = document.querySelector('.chat-messages');

    const mainElement = document.querySelector('main');
    const chatHeader = document.querySelector('.chat-header');
    const headerTitle = document.querySelector('.header-title');
    const newChatBtn = document.querySelector('.new-chat-btn');

    const handleSendMessage = () => {
        const messageText = chatInput.value.trim();

        if (messageText === '') {
            return; // Don't send empty messages
        }

        // Check API call limit before sending
        const usage = getApiCallCount();
        if (usage.count >= DAILY_API_LIMIT) {
            const limitMessageElement = document.createElement('div');
            limitMessageElement.classList.add('message', 'bot-message');
            limitMessageElement.textContent = `You have reached your daily message limit of ${DAILY_API_LIMIT}. Please come back tomorrow!`;
            chatMessagesContainer.appendChild(limitMessageElement);
            limitMessageElement.scrollIntoView({ behavior: 'smooth' });
            // Clear the input field after showing the limit message
            chatInput.value = '';
            return;
        }

        // On first message, hide header and show "New Chat" button
        if (chatHeader && !chatHeader.classList.contains('hidden')) {
            chatHeader.classList.add('hidden');
            if (headerTitle) headerTitle.classList.add('hidden');
            if (newChatBtn) newChatBtn.classList.remove('hidden');
            if (mainElement) mainElement.classList.add('is-chatting');
        }

        // 1. Create and display the user's message bubble
        const userMessageElement = document.createElement('div');
        userMessageElement.classList.add('message', 'user-message');
        userMessageElement.textContent = messageText;
        chatMessagesContainer.appendChild(userMessageElement);

        // Increment the count now that a valid message has been sent
        incrementApiCallCount();

        // 2. Clear the input field
        chatInput.value = '';

        // 3. Reset the input buttons (show mic, hide send)
        chatInput.dispatchEvent(new Event('input'));

        // 4. Scroll to the new message
        userMessageElement.scrollIntoView({ behavior: 'smooth' });

        // 5. Show typing indicator and get bot response
        showBotResponse(messageText);

        // 6. Update suggested prompts for the next interaction
        updateSuggestedPrompts();
    };

    // --- Hardcoded Responses for Suggested Prompts ---
    const hardcodedResponses = {
        'How can I reduce stress?': [
            "Here are some effective stress reduction techniques:\n\n• **Deep breathing**: Try the 4-7-8 technique - inhale for 4, hold for 7, exhale for 8\n• **Progressive muscle relaxation**: Tense and release each muscle group\n• **Mindfulness**: Focus on the present moment without judgment\n• **Physical activity**: Even a 10-minute walk can help\n• **Time management**: Break tasks into smaller, manageable steps\n\nWhich of these resonates with you? I'd be happy to guide you through any of these techniques.",
            "Stress is your body's natural response to challenges, and there are many ways to manage it effectively:\n\n🌱 **Quick relief**: Try box breathing (4 counts in, 4 hold, 4 out, 4 hold)\n🌱 **Medium-term**: Establish a daily routine that includes relaxation time\n🌱 **Long-term**: Regular exercise, good sleep, and healthy boundaries\n\nRemember, it's okay to feel stressed sometimes. What's causing you the most stress right now?"
        ],
        'Give me a motivational quote': [
            "Here's a beautiful quote for you:\n\n*\"You are braver than you believe, stronger than you seem, and smarter than you think.\"* - A.A. Milne\n\nThis reminds us that we often underestimate our own capabilities. You have overcome challenges before, and you have the strength to face whatever comes next. 💪✨",
            "*\"The only way to do great work is to love what you do.\"* - Steve Jobs\n\nSometimes we need reminding that passion and purpose can transform even the most difficult tasks. What brings you joy and energy in your life? 🌟",
            "*\"Progress, not perfection.\"*\n\nEvery small step forward matters. You don't have to be perfect - you just need to keep moving in the direction of your goals. Celebrate the small wins along the way! 🎯"
        ],
        'Suggest a 5-minute meditation': [
            "Here's a simple 5-minute mindfulness meditation:\n\n**Minute 1-2**: Sit comfortably and focus on your breath. Notice the sensation of air entering and leaving your nostrils.\n\n**Minute 3**: Expand awareness to your whole body. Notice any tension or sensations without trying to change them.\n\n**Minute 4**: If your mind wanders (and it will!), gently bring attention back to your breath. This is normal and part of the practice.\n\n**Minute 5**: Take three deep breaths and slowly open your eyes.\n\nRemember: there's no 'perfect' meditation. Just showing up is enough. 🧘‍♀️",
            "Let's try a **5-minute gratitude meditation**:\n\n🌅 **Minutes 1-2**: Close your eyes and take slow, deep breaths\n🌅 **Minute 3**: Think of three things you're grateful for today, no matter how small\n🌅 **Minute 4**: Feel the warmth of appreciation in your heart and body\n🌅 **Minute 5**: Send that gratitude out to someone who has helped you\n\nGratitude meditation can shift your perspective and boost mood. How do you feel after trying this?"
        ],
        'Tell me a fun fact': [
            "🐙 Did you know that octopuses have three hearts and blue blood? Two hearts pump blood to their gills, while the third pumps blood to the rest of their body!\n\nEven more amazing - the main heart stops beating when they swim, which is why they prefer crawling. Nature is full of incredible adaptations! What's your favorite animal?",
            "🌈 Here's a delightful fact: Honey never spoils! Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible.\n\nBees are incredible chemists - they create this natural preservative through their unique process. Sometimes the simplest things in nature are the most extraordinary! 🍯",
            "🎵 Music can literally change your brain structure! Learning to play an instrument increases gray matter in various brain regions and strengthens connections between brain hemispheres.\n\nIt's never too late to start - even listening to music actively can boost cognitive function. Do you play any instruments or have a favorite type of music? 🎶"
        ],
        'What are some good breathing exercises?': [
            "Here are three powerful breathing exercises:\n\n**🌊 4-7-8 Breathing (for relaxation)**\n• Inhale through nose for 4 counts\n• Hold breath for 7 counts\n• Exhale through mouth for 8 counts\n• Repeat 3-4 times\n\n**📦 Box Breathing (for focus)**\n• Inhale for 4, hold for 4, exhale for 4, hold for 4\n• Visualize drawing a square with your breath\n\n**⚡ Energizing Breath**\n• Quick, shallow breaths for 30 seconds\n• Then one long, slow exhale\n\nWhich one would you like to try first?",
            "Breathing is one of the most accessible tools for managing stress and emotions:\n\n🫁 **Belly Breathing**: Place one hand on chest, one on belly. Breathe so only the bottom hand moves\n🫁 **Alternate Nostril**: Use thumb to close right nostril, inhale left. Switch and exhale right\n🫁 **Coherent Breathing**: 5 seconds in, 5 seconds out, for 5 minutes\n\nThe beauty of breathwork is you can do it anywhere, anytime. Your breath is always with you as an anchor to the present moment."
        ],
        'Write a short, calming story': [
            "**The Garden of Quiet Moments**\n\nThere was once a small garden hidden behind an old wooden gate. No one knew who tended it, but somehow it was always perfectly kept. Soft moss covered the stepping stones, and gentle wind chimes sang in the breeze.\n\nA weary traveler discovered this garden one evening. As they sat on the weathered bench, surrounded by lavender and jasmine, their breathing naturally slowed. The weight they'd been carrying seemed to dissolve into the earth.\n\nThe garden asked for nothing - no payment, no explanation. It simply offered peace to anyone who needed it.\n\nSometimes, we all need to find our own quiet garden. 🌿✨",
            "**The Lighthouse Keeper's Evening**\n\nEvery night, the lighthouse keeper climbed the spiral stairs to light the beacon. Tonight, as golden hour painted the ocean, she paused at the window.\n\nBelow, waves rolled in their eternal rhythm - the same rhythm that had soothed countless souls before her. She realized that like the lighthouse, she too was a beacon - not just for ships, but for her own inner peace.\n\nThe light she tended wasn't just for others; it was a reminder that even in darkness, there's always a way home to yourself.\n\nShe smiled, lit the lamp, and felt the gentle pulse of her own steady heart. 🌊💫"
        ],
        'How can I improve my focus?': [
            "Here are proven strategies to enhance your focus:\n\n🎯 **Environment**: Clear your workspace, use noise-canceling headphones, or try background nature sounds\n\n🎯 **Time blocks**: Try the Pomodoro Technique - 25 minutes focused work, 5-minute break\n\n🎯 **Single-tasking**: Our brains aren't built for multitasking. Do one thing at a time\n\n🎯 **Mindfulness**: Even 5 minutes of daily meditation can improve attention span\n\n🎯 **Physical care**: Stay hydrated, eat brain-healthy foods, and get enough sleep\n\nWhat's your biggest focus challenge? I can help you create a personalized strategy.",
            "Focus is like a muscle - it gets stronger with practice! Here's how to train it:\n\n💪 **Start small**: Begin with 10-15 minute focused sessions\n💪 **Remove distractions**: Phone in another room, close unnecessary tabs\n💪 **Use visual cues**: A clean desk signals your brain it's time to focus\n💪 **Take breaks**: Your brain needs rest to maintain concentration\n💪 **Practice mindfulness**: Notice when your mind wanders and gently redirect\n\nRemember, everyone's attention span varies. Be patient with yourself as you build this skill!"
        ],
        'Give me a positive affirmation': [
            "Here's a powerful affirmation for you:\n\n✨ **\"I am capable of handling whatever comes my way. I have overcome challenges before, and I have the strength and wisdom to navigate what lies ahead. I trust in my ability to grow and adapt.\"** ✨\n\nTake a deep breath and let these words settle in your heart. You are more resilient than you know. 💙",
            "✨ **\"I choose to focus on what I can control and release what I cannot. My peace comes from within, and I am worthy of love, respect, and happiness - especially from myself.\"** ✨\n\nSay this to yourself with kindness, as you would speak to a dear friend. You deserve the same compassion you give others. 🌟",
            "✨ **\"Every day, I am growing stronger and wiser. My challenges are opportunities for growth, and my setbacks are setups for comebacks. I believe in my potential.\"** ✨\n\nCarry this energy with you today. You have everything within you to create positive change. 🌱"
        ],
        'Suggest a relaxing activity': [
            "Here are some wonderfully relaxing activities to try:\n\n🌿 **Nature connection**: Take a slow walk outside, even if it's just around the block\n🌿 **Creative expression**: Try doodling, coloring, or writing in a journal\n🌿 **Gentle movement**: Stretch, do yoga, or dance to your favorite song\n🌿 **Sensory comfort**: Take a warm bath, listen to calming music, or make herbal tea\n🌿 **Mindful activities**: Organize a small space, tend to plants, or practice gratitude\n\nWhat sounds most appealing to you right now? Sometimes our intuition knows exactly what we need.",
            "Let's find the perfect relaxing activity for your current mood:\n\n🛁 **If you need comfort**: Warm bath with essential oils, cozy blanket with a good book\n🎨 **If you need creativity**: Adult coloring books, sketching, or crafting\n🌱 **If you need grounding**: Gardening, cooking something simple, organizing\n🎵 **If you need escape**: Listen to a podcast, watch nature documentaries, or create a playlist\n\nThe key is choosing something that feels nurturing rather than demanding. What calls to you?"
        ],
        'What is a simple mindfulness exercise?': [
            "Here's a simple **5-4-3-2-1 grounding exercise** you can do anywhere:\n\n👀 **5 things you can see** (a pen, the ceiling, your hands...)\n✋ **4 things you can touch** (your chair, your clothes, a smooth surface...)\n👂 **3 things you can hear** (traffic, your breathing, a clock ticking...)\n👃 **2 things you can smell** (coffee, fresh air, soap...)\n👅 **1 thing you can taste** (gum, coffee, or just the taste in your mouth)\n\nThis exercise brings you into the present moment and can help with anxiety or overwhelm. Try it now if you'd like! 🌟",
            "Let's try **mindful breathing with counting**:\n\n🌬️ Sit comfortably and close your eyes\n🌬️ Breathe naturally and count each exhale: 1... 2... 3...\n🌬️ When you reach 10, start over at 1\n🌬️ If you lose count, simply start again at 1\n🌬️ Continue for 2-3 minutes\n\nThis simple practice trains your attention and creates a sense of calm. There's no 'perfect' way to do it - just showing up is enough. How did that feel?"
        ],
        'Tell me a joke': [
            "Why don't scientists trust atoms?\n\nBecause they make up everything! 😄\n\nI hope that brought a little smile to your day. Laughter really is great medicine - it releases endorphins and can instantly shift our mood. Do you have a favorite type of humor?",
            "What do you call a bear with no teeth?\n\nA gummy bear! 🐻😁\n\nSometimes the silliest jokes are exactly what we need. Humor helps us step back from our worries and remember that joy can be found in the simplest moments. Thanks for letting me share a laugh with you!",
            "Why did the meditation teacher refuse Novocaine at the dentist?\n\nThey wanted to transcend dental medication! 🧘‍♀️😂\n\nOkay, that was pretty cheesy, but I hope it made you smile! Sometimes a little silliness is the perfect antidote to a serious day."
        ]
    };

    const getHardcodedResponse = (userMessage) => {
        const responses = hardcodedResponses[userMessage];
        if (responses && responses.length > 0) {
            // Return a random response from the available options
            return responses[Math.floor(Math.random() * responses.length)];
        }
        return null;
    };

    const showBotResponse = async (userMessage) => {
        // 1. Show typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.classList.add('typing-indicator');
        typingIndicator.innerHTML = '<span></span><span></span><span></span>';
        chatMessagesContainer.appendChild(typingIndicator);
        typingIndicator.scrollIntoView({ behavior: 'smooth' });
        
        try {
            let botResponseText;
            
            // 2. Check if this is a suggested prompt with hardcoded response
            const hardcodedResponse = getHardcodedResponse(userMessage);
            
            if (hardcodedResponse) {
                // Simulate API delay for better UX (1-3 seconds)
                const delay = Math.random() * 2000 + 1000; // 1-3 seconds
                await new Promise(resolve => setTimeout(resolve, delay));
                botResponseText = hardcodedResponse;
            } else {
                // 3. Use the actual ChillBuddy API for non-suggested prompts
                botResponseText = await getChillBuddyResponse(userMessage);
            }

            // 3. Remove the typing indicator once the response is received
            typingIndicator.remove();

            // 4. Create and display the bot's message bubble
            const botMessageElement = document.createElement('div');
            botMessageElement.classList.add('message', 'bot-message');

            // Message text
            const contentElement = document.createElement('div');
            contentElement.innerHTML = parseMarkdown(botResponseText);

            // Action buttons
            const actionsContainer = document.createElement('div');
            actionsContainer.classList.add('message-actions');

            const actions = [
                { icon: 'regenerate', tooltip: 'Regenerate' },
                { icon: 'copy', tooltip: 'Copy' },
                { icon: 'share', tooltip: 'Share' },
                { icon: 'like', tooltip: 'Like' },
                { icon: 'dislike', tooltip: 'Dislike' }
            ];

            actions.forEach(action => {
                const button = document.createElement('button');
                button.dataset.tooltip = action.tooltip;
                const img = document.createElement('img');
                img.src = `assets/icons/${action.icon}.svg`;
                img.alt = action.tooltip;
                button.appendChild(img);

                if (action.icon === 'copy') {
                    button.addEventListener('click', () => {
                        const originalTooltip = button.dataset.tooltip;
                        // Use the raw text from the bot to preserve original formatting
                        navigator.clipboard.writeText(botResponseText).then(() => {
                            button.dataset.tooltip = 'Copied!';
                            setTimeout(() => {
                                button.dataset.tooltip = originalTooltip;
                            }, 2000);
                        }).catch(err => {
                            console.error('Failed to copy text: ', err);
                        });
                    });
                }

                if (action.icon === 'regenerate') {
                    button.addEventListener('click', () => {
                        botMessageElement.remove();
                        showBotResponse(userMessage);
                    });
                }

                if (action.icon === 'like' || action.icon === 'dislike') {
                    button.addEventListener('click', () => {
                        const isAlreadyActive = button.classList.contains('active');

                        // Find sibling like/dislike buttons within the same actions container
                        const likeButton = button.parentElement.querySelector('[data-tooltip="Like"]');
                        const dislikeButton = button.parentElement.querySelector('[data-tooltip="Dislike"]');

                        // Deactivate both to ensure only one can be active
                        if (likeButton) likeButton.classList.remove('active');
                        if (dislikeButton) dislikeButton.classList.remove('active');

                        // If the button was not already active, activate it.
                        if (!isAlreadyActive) {
                            button.classList.add('active');
                        }
                    });
                }

                if (action.icon === 'share') {
                    button.addEventListener('click', async () => {
                        const shareData = {
                            title: 'ChillBuddy Response',
                            text: botResponseText,
                            url: window.location.href
                        };

                        if (navigator.share) {
                            try {
                                await navigator.share(shareData);
                            } catch (err) {
                                console.error('Share API failed:', err);
                            }
                        } else {
                            // Fallback for browsers that don't support Web Share API
                            const originalTooltip = button.dataset.tooltip;
                            navigator.clipboard.writeText(botResponseText).then(() => {
                                button.dataset.tooltip = 'Copied!';
                                setTimeout(() => {
                                    button.dataset.tooltip = originalTooltip;
                                }, 2000);
                            }).catch(err => console.error('Fallback copy failed:', err));
                        }
                    });
                }

                actionsContainer.appendChild(button);
            });

            botMessageElement.appendChild(contentElement);
            botMessageElement.appendChild(actionsContainer);
            chatMessagesContainer.appendChild(botMessageElement);

            // 5. Scroll to the new message
            botMessageElement.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            // If there's an error, remove the indicator and show an error message
            typingIndicator.remove();
            console.error("Failed to show bot response:", error);
        }
    };

    // --- New Chat Functionality ---
    if (newChatBtn) {
        newChatBtn.addEventListener('click', () => {
            // Clear messages
            chatMessagesContainer.innerHTML = '';
            
            // Reset UI state
            if (chatHeader) chatHeader.classList.remove('hidden');
            if (headerTitle) headerTitle.classList.remove('hidden');
            newChatBtn.classList.add('hidden');
            if (mainElement) mainElement.classList.remove('is-chatting');
            
            // Update suggested prompts
            updateSuggestedPrompts();
            
            // Trigger sidebar new chat if sidebar manager exists
            if (window.sidebarManager && typeof window.sidebarManager.createNewChat === 'function') {
                window.sidebarManager.createNewChat();
            }
            
            console.log('New chat started from header button');
        });
    }
    
    // --- Starry Night Effect ---
    const canvas = document.getElementById('stars-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let animationFrameId = null;
        let stars = [];
        let shootingStars = [];

        const STAR_COUNT = 200;
        const SHOOTING_STAR_COUNT = 2;

        class Star {
            constructor() {
                this.x = Math.random() * window.innerWidth;
                this.y = Math.random() * window.innerHeight;
                this.radius = Math.random() * 1.2;
                this.alpha = Math.random() * 0.5 + 0.5; // Start with random opacity for twinkling
                this.vx = (Math.random() - 0.5) * 0.1; // Slow horizontal velocity
                this.vy = (Math.random() - 0.5) * 0.1; // Slow vertical velocity
                this.alphaVelocity = (Math.random() - 0.5) * 0.02;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255, 255, 255, ${this.alpha})`;
                ctx.fill();
            }

            update() {
                // Twinkling effect
                if (this.alpha <= 0.2 || this.alpha >= 1) {
                    this.alphaVelocity = -this.alphaVelocity;
                }
                this.alpha += this.alphaVelocity;

                // Movement
                this.x += this.vx;
                this.y += this.vy;

                // Wrap around screen edges
                if (this.x < 0) this.x = window.innerWidth;
                if (this.x > window.innerWidth) this.x = 0;
                if (this.y < 0) this.y = window.innerHeight;
                if (this.y > window.innerHeight) this.y = 0;

                this.draw();
            }
        }

        /* Shooting Star Class */
        class ShootingStar {
            constructor() {
                this.reset();
            }

            reset() {
                this.x = Math.random() * window.innerWidth;
                this.y = 0;
                this.len = (Math.random() * 80) + 10;
                this.speed = (Math.random() * 10) + 6;
                this.size = (Math.random() * 1) + 0.1;
                this.waitTime = new Date().getTime() + (Math.random() * 3000) + 500;
                this.active = false;
            }

            update() {
                if (this.active) {
                    this.x -= this.speed;
                    this.y += this.speed;
                    if (this.x < 0 || this.y >= window.innerHeight) {
                        this.reset();
                    }
                } else {
                    if (this.waitTime < new Date().getTime()) {
                        this.active = true;
                    }
                }
            }
            /* drawing shooting stars */
            draw() {
                if (this.active) {
                    const gradient = ctx.createLinearGradient(this.x, this.y, this.x + this.len, this.y - this.len);
                    gradient.addColorStop(0, `rgba(255, 255, 255, ${this.size})`);
                    gradient.addColorStop(1, "rgba(255, 255, 255, 0)");
                    ctx.strokeStyle = gradient;
                    ctx.lineWidth = this.size;
                    ctx.beginPath();
                    ctx.moveTo(this.x, this.y);
                    ctx.lineTo(this.x + this.len, this.y - this.len);
                    ctx.stroke();
                }
            }
        }

        function setupCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            stars = Array.from({ length: STAR_COUNT }, () => new Star());
            shootingStars = Array.from({ length: SHOOTING_STAR_COUNT }, () => new ShootingStar());
        }

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            stars.forEach(star => star.update());
            shootingStars.forEach(star => {
                star.update();
                star.draw();
            });
            animationFrameId = requestAnimationFrame(animate);
        }

        startAnimation = function() {
            if (!animationFrameId) {
                setupCanvas();
                animate();
            }
        }

        stopAnimation = function() {
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
                animationFrameId = null;
                setTimeout(() => {
                    if (!canvas.classList.contains('active')) {
                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                    }
                }, 1500); // Clear after fade out (matches CSS transition)
            }
        }

        window.addEventListener('resize', () => {
            if (canvas.classList.contains('active')) setupCanvas();
        });
    }

    if (sendBtn && chatInput && chatMessagesContainer) {
        sendBtn.addEventListener('click', handleSendMessage);

        chatInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault(); // Prevent new line on Enter
                handleSendMessage();
            }
        });
    }

    // --- Initial Setup ---

    loadTheme(); // Set theme on page load
    updateSuggestedPrompts(); // Set initial random prompts

    // Set an interval to change prompts periodically
    setInterval(updateSuggestedPrompts, 7000); // Change prompts every 7 seconds
});

