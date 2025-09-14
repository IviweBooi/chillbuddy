// Configuration for ChillBuddy frontend
const CONFIG = {
    // Backend API base URL
    API_BASE_URL: 'http://127.0.0.1:5000',
    
    // API endpoints
    ENDPOINTS: {
        CHAT: '/api/chat',
        REGISTER: '/api/register',
        HEALTH: '/api/health'
    },
    
    // App settings
    DAILY_MESSAGE_LIMIT: 25,
    
    // Request timeout in milliseconds
    REQUEST_TIMEOUT: 30000
};

// Make config globally available
window.CONFIG = CONFIG;