# ChillBuddy Backend

A comprehensive mental health support chatbot backend built with Flask, featuring conversation management, database persistence, and AI-powered responses.

## Features

- **Conversation Management**: Persistent chat history and context management
- **Database Layer**: SQLite-based data persistence for users, conversations, and messages
- **AI Integration**: Transformer-based conversation engine with safety filtering
- **User Management**: User authentication and session management
- **Testing Framework**: Comprehensive test suite with mocking capabilities
- **Safety Features**: Crisis detection and risk assessment

## Architecture

### Core Components

1. **ConversationManager** (`conversation_manager.py`)
   - Integrates ConversationEngine with DatabaseManager
   - Handles persistent chat history and context
   - Manages conversation lifecycle

2. **DatabaseManager** (`models/database.py`)
   - SQLite database operations
   - User, conversation, and message persistence
   - Data models with proper relationships

3. **ConversationEngine** (`conversation.py`)
   - AI-powered conversation processing
   - Safety filtering and crisis detection
   - Context-aware response generation

4. **UserManager** (`user_manager.py`)
   - User authentication and management
   - Session handling
   - User preferences and profiles

### Database Schema

#### Users Table
- `user_id` (TEXT, PRIMARY KEY)
- `username` (TEXT, UNIQUE)
- `email` (TEXT, UNIQUE)
- `password_hash` (TEXT)
- `created_at` (TIMESTAMP)
- `last_active` (TIMESTAMP)
- `status` (TEXT)
- `preferences` (TEXT, JSON)
- `profile_data` (TEXT, JSON)

#### Conversations Table
- `conversation_id` (TEXT, PRIMARY KEY)
- `user_id` (TEXT, FOREIGN KEY)
- `title` (TEXT)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)
- `status` (TEXT)
- `metadata` (TEXT, JSON)

#### Messages Table
- `message_id` (TEXT, PRIMARY KEY)
- `conversation_id` (TEXT, FOREIGN KEY)
- `user_id` (TEXT, FOREIGN KEY)
- `content` (TEXT)
- `message_type` (TEXT)
- `timestamp` (TIMESTAMP)
- `risk_level` (TEXT)
- `metadata` (TEXT, JSON)

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chillbuddy/src/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install Flask==2.3.3 Flask-CORS==4.0.0
   pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0
   pip install transformers datasets scikit-learn
   pip install pytest==7.4.2 pytest-cov==4.1.0 pytest-mock==3.11.1
   ```

4. **Initialize database**
   ```bash
   python -c "from models.database import DatabaseManager; DatabaseManager('data/chillbuddy.db')"
   ```

### Configuration

1. **Environment Variables**
   Create a `.env` file in the backend directory:
   ```
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///data/chillbuddy.db
   LOG_LEVEL=INFO
   ```

2. **Model Configuration**
   Update `models/model_config.json` with your preferred AI model settings:
   ```json
   {
     "model_name": "microsoft/DialoGPT-medium",
     "max_length": 512,
     "temperature": 0.7,
     "safety_threshold": 0.8
   }
   ```

### Running the Application

1. **Development Server**
   ```bash
   python app.py
   ```
   The server will start on `http://localhost:5000`

2. **Production Deployment**
   ```bash
   gunicorn --bind 0.0.0.0:5000 app:app
   ```

### Testing

1. **Run all tests**
   ```bash
   python -m pytest tests/ -v
   ```

2. **Run specific test file**
   ```bash
   python -m pytest tests/test_conversation_manager.py -v
   ```

3. **Run with coverage**
   ```bash
   python run_tests.py --verbose
   ```

## API Endpoints

### Conversation Management

- `POST /api/conversations` - Start new conversation
- `GET /api/conversations` - Get user conversations
- `GET /api/conversations/{id}` - Get conversation history
- `POST /api/conversations/{id}/messages` - Send message
- `DELETE /api/conversations/{id}` - Delete conversation

### User Management

- `POST /api/users/register` - Register new user
- `POST /api/users/login` - User login
- `POST /api/users/logout` - User logout
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile

### Health & Status

- `GET /api/health` - Health check
- `GET /api/status` - System status

## Usage Examples

### Starting a Conversation

```python
from conversation_manager import ConversationManager

# Initialize conversation manager
conv_manager = ConversationManager()

# Start new conversation
conversation_id = conv_manager.start_conversation(
    user_id="user123",
    title="Mental Health Check-in"
)

# Send message
response = conv_manager.send_message(
    conversation_id=conversation_id,
    user_message="I'm feeling anxious today",
    user_id="user123"
)

print(response['response'])
```

### Database Operations

```python
from models.database import DatabaseManager, User, Conversation
from datetime import datetime

# Initialize database
db = DatabaseManager()

# Create user
user = User(
    user_id="user123",
    username="john_doe",
    email="john@example.com"
)
db.create_user(user)

# Get user conversations
conversations = db.get_user_conversations("user123")
```

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write comprehensive docstrings for all classes and methods
- Maintain test coverage above 80%

### Testing

- Write unit tests for all new features
- Use mocking for external dependencies
- Test both success and error scenarios
- Include integration tests for API endpoints

### Security

- Never commit secrets or API keys
- Use environment variables for configuration
- Implement proper input validation
- Follow OWASP security guidelines

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure virtual environment is activated
   - Check Python path configuration
   - Verify all dependencies are installed

2. **Database Issues**
   - Check database file permissions
   - Ensure data directory exists
   - Verify SQLite installation

3. **Model Loading Errors**
   - Check internet connection for model downloads
   - Verify sufficient disk space
   - Ensure compatible PyTorch version

### Logging

Logs are written to `logs/chillbuddy.log` with the following levels:
- ERROR: Critical errors requiring attention
- WARNING: Potential issues or deprecated usage
- INFO: General application flow
- DEBUG: Detailed debugging information

## Project Structure

```
src/backend/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── user_manager.py       # User management and authentication
├── resources.py          # Mental health resources management
├── gamification.py       # User engagement and progress tracking
├── utils.py              # Utility functions and helpers
├── requirements.txt      # Python dependencies
├── tests/                # Test suite
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_user_manager.py
│   ├── test_resources.py
│   └── test_app.py
└── README.md            # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Setup

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd chillbuddy/src/backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   Create a `.env` file in the backend directory:
   ```env
   FLASK_ENV=development
   FLASK_DEBUG=True
   SECRET_KEY=your-secret-key-here
   OPENAI_API_KEY=your-openai-api-key
   DATABASE_URL=sqlite:///chillbuddy.db
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   RATE_LIMIT_STORAGE_URL=memory://
   LOG_LEVEL=INFO
   ```

## Running the Application

### Development Mode

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Production Mode

Using Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

### Health Check
- `GET /health` - Application health status

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `POST /api/logout` - User logout

### Chat
- `POST /api/chat` - Send message to AI chatbot

### Crisis Support
- `POST /api/crisis` - Get crisis support resources

### Resources
- `GET /api/resources` - Get mental health resources
- `GET /api/resources/search` - Search resources

### User Management
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile
- `GET /api/user/progress` - Get user progress
- `GET /api/user/badges` - Get user achievements

### Feedback
- `POST /api/feedback` - Submit user feedback

## Testing

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pytest --cov=. --cov-report=html
```

### Run Specific Test Files
```bash
pytest tests/test_app.py
pytest tests/test_user_manager.py
pytest tests/test_resources.py
```

### Run Tests with Verbose Output
```bash
pytest -v
```

## Configuration

The application supports multiple environments:

- **Development**: Debug mode enabled, detailed logging
- **Testing**: Isolated test database, mocked external services
- **Production**: Optimized settings, security hardened

Configuration is managed through the `config.py` file and environment variables.

## Security Features

- **Rate Limiting**: Prevents API abuse
- **Input Validation**: Sanitizes and validates all inputs
- **Authentication**: Secure JWT-based authentication
- **CORS Protection**: Configurable cross-origin resource sharing
- **Error Handling**: Secure error responses without sensitive information
- **Logging**: Comprehensive request and error logging

## Mental Health Resources

The application includes:

- **Crisis Resources**: Emergency contacts and immediate help
- **Coping Strategies**: Evidence-based mental health techniques
- **Educational Content**: Mental health awareness and information
- **Professional Help**: Directory of mental health professionals
- **Wellness Tools**: Self-care and mindfulness resources
- **South African Resources**: Localized support and services

## Gamification Features

- **Progress Tracking**: Monitor user engagement and improvement
- **Achievement System**: Badges and milestones for motivation
- **Daily Challenges**: Personalized mental health activities
- **Streak Tracking**: Consistency rewards and motivation
- **Personalized Recommendations**: Adaptive content suggestions

## Development

### Code Quality

The project uses several tools for code quality:

```bash
# Format code
black .
isort .

# Lint code
flake8 .

# Type checking
mypy .
```

### Adding New Features

1. Create feature branch
2. Implement functionality
3. Add comprehensive tests
4. Update documentation
5. Run quality checks
6. Submit pull request

### Database Management

Currently using SQLite for simplicity. For production, consider:
- PostgreSQL for better performance
- Redis for caching and session storage
- Database migrations for schema changes

## Monitoring and Logging

- **Application Logs**: Structured logging with configurable levels
- **Request Logging**: All API requests and responses
- **Error Tracking**: Detailed error information and stack traces
- **Performance Monitoring**: Response times and resource usage

## Deployment

### Docker (Recommended)

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Environment Variables for Production

```env
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
OPENAI_API_KEY=your-openai-api-key
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/0
CORS_ORIGINS=https://yourdomain.com
RATE_LIMIT_STORAGE_URL=redis://host:port/1
LOG_LEVEL=WARNING
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## Acknowledgments

- Mental health professionals who provided guidance
- South African mental health organizations
- Open source libraries and frameworks used
- Contributors and testers

---

**Note**: This is a mental health application. Always prioritize user safety and follow best practices for handling sensitive mental health data.