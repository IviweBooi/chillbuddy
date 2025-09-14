# ChillBuddy Setup Instructions

This guide will help you set up and run ChillBuddy on your local machine. Follow these steps carefully to ensure a smooth installation process.

---

## 📦 Requirements

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher
- **Web Browser**: Chrome, Firefox, Safari, or Edge (latest versions)
- **Internet Connection**: Required for AI features and resource loading
- **Disk Space**: At least 500MB free space

### Software Dependencies
- **Python 3.8+**: Download from [python.org](https://python.org)
- **pip**: Python package installer (included with Python 3.4+)
- **Git**: Version control system for cloning the repository

### API Requirements
- **OpenAI API Key**: Required for AI chat functionality
  - Sign up at [OpenAI Platform](https://platform.openai.com)
  - Generate an API key from your dashboard
  - Note: Free tier available with usage limits

---

## ⚙️ Installation

### Step 1: Clone the Repository
```bash
# Clone the ChillBuddy repository
git clone https://github.com/IviweBooi/chillbuddy.git
cd chillbuddy
```

### Step 2: Set Up Python Environment (Recommended)
```bash
# Create a virtual environment
python -m venv chillbuddy-env

# Activate the virtual environment
# On Windows:
chillbuddy-env\Scripts\activate
# On macOS/Linux:
source chillbuddy-env/bin/activate
```

### Step 3: Install Backend Dependencies
```bash
# Navigate to backend directory
cd src/backend

# Install required Python packages
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
# Copy the example configuration file
cp config.py.example config.py

# Edit config.py with your settings
# Add your OpenAI API key and other configurations
```

**Configuration Example:**
```python
# config.py
OPENAI_API_KEY = "your-openai-api-key-here"
DEBUG = True
PORT = 5000
DATABASE_URL = "sqlite:///chillbuddy.db"
```

### Step 5: Initialize Database
```bash
# Run database initialization script
python init_db.py
```

---

## ▶️ Running the Project

### Method 1: Manual Startup (Recommended for Development)

**Terminal 1 - Start Backend Server:**
```bash
# Navigate to backend directory
cd src/backend

# Activate virtual environment (if not already active)
# Windows: chillbuddy-env\Scripts\activate
# macOS/Linux: source chillbuddy-env/bin/activate

# Start the Flask backend server
python app.py
```

**Terminal 2 - Start Frontend Server:**
```bash
# Navigate to frontend directory
cd src/frontend

# Start a simple HTTP server
python -m http.server 8000
```

**Access the Application:**
- Open your web browser
- Navigate to `http://localhost:8000`
- The application should load and be ready to use

### Method 2: Using Docker (Optional)

```bash
# Build the Docker image
docker build -t chillbuddy .

# Run the container
docker run -p 8000:8000 -p 5000:5000 chillbuddy

# Access at http://localhost:8000
```

### Method 3: Using Setup Script

```bash
# Make the setup script executable (macOS/Linux)
chmod +x scripts/setup.sh

# Run the setup script
./scripts/setup.sh

# Or on Windows:
scripts\setup.bat
```

---

## 🔧 Configuration Options

### Backend Configuration (config.py)
```python
# API Settings
OPENAI_API_KEY = "your-api-key"          # Required for AI features
OPENAI_MODEL = "gpt-3.5-turbo"           # AI model to use

# Server Settings
DEBUG = True                             # Enable debug mode
PORT = 5000                              # Backend server port
HOST = "localhost"                       # Server host

# Database Settings
DATABASE_URL = "sqlite:///chillbuddy.db" # Database connection

# Security Settings
SECRET_KEY = "your-secret-key"           # Flask secret key
SESSION_TIMEOUT = 3600                   # Session timeout in seconds

# Feature Flags
ENABLE_GAMIFICATION = True               # Enable achievement system
ENABLE_MOOD_TRACKING = True              # Enable mood tracking
ENABLE_CRISIS_DETECTION = True           # Enable crisis support
```

### Frontend Configuration
- No additional configuration required
- Automatically connects to backend on `localhost:5000`
- Responsive design adapts to screen size

---

## 🧪 Testing the Installation

### Quick Health Check
```bash
# Test backend API
curl http://localhost:5000/health

# Expected response: {"status": "healthy"}
```

### Run Test Suite
```bash
# Navigate to backend directory
cd src/backend

# Run all tests
python -m pytest tests/

# Run specific test file
python test_chat.py
```

### Manual Testing
1. Open `http://localhost:8000` in your browser
2. Try starting a conversation with the AI
3. Test mood tracking functionality
4. Check that resources load properly
5. Verify responsive design on different screen sizes

---

## 🚨 Troubleshooting

### Common Issues

**Issue: "Module not found" errors**
```bash
# Solution: Ensure virtual environment is activated and dependencies installed
pip install -r requirements.txt
```

**Issue: "OpenAI API key not found"**
```bash
# Solution: Check config.py file has correct API key
# Ensure no extra spaces or quotes in the key
```

**Issue: "Port already in use"**
```bash
# Solution: Change port in config.py or kill existing process
# Windows: netstat -ano | findstr :5000
# macOS/Linux: lsof -ti:5000 | xargs kill
```

**Issue: Frontend not loading**
```bash
# Solution: Ensure both servers are running
# Check browser console for errors
# Verify CORS settings in backend
```

### Getting Help
- Check the [Usage Guide](USAGE.md) for feature-specific help
- Review error logs in the terminal
- Ensure all requirements are met
- Contact the development team (see [TEAM.md](TEAM.md))

---

## 🔄 Development Setup

### Additional Tools for Contributors
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black src/
flake8 src/
```

### Environment Variables for Development
```bash
# Create .env file for local development
echo "OPENAI_API_KEY=your-key-here" > .env
echo "DEBUG=True" >> .env
echo "FLASK_ENV=development" >> .env
```

---

## 📱 Mobile Testing

### Local Network Access
```bash
# Find your local IP address
# Windows: ipconfig
# macOS/Linux: ifconfig

# Start frontend server with network access
python -m http.server 8000 --bind 0.0.0.0

# Access from mobile device at: http://YOUR_IP:8000
```

---

**Setup Complete!** 🎉

Your ChillBuddy installation should now be ready. If you encounter any issues, please refer to the troubleshooting section or contact our team.

Next steps:
- Read the [Usage Guide](USAGE.md) to learn how to use ChillBuddy
- Explore the codebase and contribute to development
- Share feedback and suggestions with the team
