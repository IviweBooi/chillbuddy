# ChillBuddy 🌟

**Your AI-Powered Mental Health Companion**

ChillBuddy is an innovative mental health support application that combines AI-driven conversations, gamification, and comprehensive resources to provide accessible mental health support. Built for the South African Intervarsity Hackathon 2025, ChillBuddy aims to make mental health care more approachable and engaging for young adults.

---

## 🚀 Features

- **🤖 AI Chat Support**: Intelligent conversational AI that provides empathetic mental health support
- **📊 Mood Tracking**: Visual mood tracking with insights and patterns
- **🏆 Gamification**: Achievement system with badges and progress tracking
- **📚 Resource Library**: Curated mental health resources and crisis support
- **🎯 Goal Setting**: Personal wellness goals with progress monitoring
- **🔒 Privacy-First**: Secure, confidential conversations with data protection
- **📱 Responsive Design**: Works seamlessly across desktop and mobile devices

## 📂 Repository Structure
```
├── assets/                 # Project assets and media
├── demo/                   # Demo videos and presentations
├── docs/                   # Project documentation
├── src/
│   ├── backend/           # Python Flask backend
│   │   ├── app.py         # Main application server
│   │   ├── conversation.py # AI conversation logic
│   │   ├── gamification.py # Achievement system
│   │   ├── resources.py   # Mental health resources
│   │   └── models/        # Data models
│   └── frontend/          # HTML/CSS/JS frontend
│       ├── index.html     # Main application interface
│       ├── css/           # Styling and themes
│       └── js/            # Client-side functionality
├── scripts/               # Utility and deployment scripts
└── vendor/                # Third-party dependencies
```
---

## 🛠️ Technology Stack

**Backend:**
- Python 3.8+
- Flask web framework
- OpenAI GPT API for conversational AI
- SQLite for data persistence
- JSON-based configuration

**Frontend:**
- Vanilla HTML5, CSS3, JavaScript
- Responsive CSS Grid and Flexbox
- Modern ES6+ JavaScript features
- CSS custom properties for theming

**Development:**
- Git version control
- Docker containerization support
- Cross-platform compatibility

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/chillbuddy.git
   cd chillbuddy
   ```

2. **Set up the backend**
   ```bash
   cd src/backend
   pip install -r requirements.txt
   python app.py
   ```

3. **Launch the frontend**
   ```bash
   cd src/frontend
   python -m http.server 8000
   ```

4. **Open your browser**
   Navigate to `http://localhost:8000`

For detailed setup instructions, see [SETUP.md](docs/SETUP.md).

## 📖 Documentation

- **[Setup Guide](docs/SETUP.md)** - Complete installation and configuration
- **[Usage Guide](docs/USAGE.md)** - How to use ChillBuddy features
- **[Team Information](docs/TEAM.md)** - Meet the development team
- **[Acknowledgements](docs/ACKNOWLEDGEMENTS.md)** - Credits and references

## 🎯 Core Components

### 🤖 AI Conversation Engine
- **Empathetic AI**: Trained responses for mental health support
- **Context Awareness**: Maintains conversation history and user preferences
- **Safety Filters**: Built-in crisis detection and appropriate responses
- **Personalization**: Adapts to individual user communication styles

### 📊 Mood & Progress Tracking
- **Daily Mood Logging**: Simple, intuitive mood entry system
- **Visual Analytics**: Charts and graphs showing mood patterns
- **Insight Generation**: AI-powered observations about mental health trends
- **Goal Progress**: Track wellness objectives and milestones

### 🏆 Gamification System
- **Achievement Badges**: Unlock rewards for consistent engagement
- **Progress Levels**: Advance through wellness journey stages
- **Sharing Features**: Celebrate achievements with community
- **Motivation Tracking**: Maintain engagement through positive reinforcement

### 📚 Resource Library
- **Curated Content**: Professional mental health resources
- **Crisis Support**: Emergency contacts and immediate help options
- **Educational Materials**: Articles, videos, and self-help guides
- **Local Resources**: South African mental health services and contacts

## 🔒 Privacy & Security

ChillBuddy prioritizes user privacy and data security:

- **Local Data Storage**: Sensitive information stored locally when possible
- **Encrypted Communications**: All API communications use HTTPS
- **Minimal Data Collection**: Only essential data is collected and processed
- **User Control**: Users can delete their data at any time
- **Compliance**: Follows best practices for mental health data handling

## 🌍 Accessibility & Inclusivity

- **Multi-language Support**: Designed for South African linguistic diversity
- **Cultural Sensitivity**: Culturally appropriate mental health approaches
- **Accessibility Features**: Screen reader compatible, keyboard navigation
- **Mobile-First Design**: Optimized for smartphones and tablets
- **Low-Bandwidth Friendly**: Efficient loading for various internet speeds

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection for AI features
- OpenAI API key (for full functionality)

### Installation

1. **Clone and navigate to the project**
   ```bash
   git clone https://github.com/yourusername/chillbuddy.git
   cd chillbuddy
   ```

2. **Install backend dependencies**
   ```bash
   cd src/backend
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp config.py.example config.py
   # Edit config.py with your API keys
   ```

4. **Start the application**
   ```bash
   # Terminal 1: Start backend
   python app.py
   
   # Terminal 2: Start frontend server
   cd ../frontend
   python -m http.server 8000
   ```

5. **Access the application**
   Open your browser to `http://localhost:8000`

### Docker Deployment (Optional)

```bash
docker build -t chillbuddy .
docker run -p 8000:8000 chillbuddy
```

## 🧪 Testing

Run the test suite to ensure everything is working correctly:

```bash
cd src/backend
python run_tests.py
```

## 📊 Project Status

- ✅ Core AI conversation system
- ✅ Mood tracking functionality
- ✅ Gamification and achievements
- ✅ Resource library
- ✅ Responsive UI design
- ✅ Crisis support integration
- 🔄 Advanced analytics (in progress)
- 🔄 Mobile app version (planned)

---

## 🤝 Contributing

We welcome contributions to ChillBuddy! Please read our contributing guidelines and feel free to submit issues and pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙌 Acknowledgments

- South African Intervarsity Hackathon 2025 organizers
- Mental health professionals who provided guidance
- Open source community for tools and libraries
- Beta testers and early users for feedback

---

**Built with ❤️ for mental health awareness and support**

*ChillBuddy - Making mental health support accessible, engaging, and effective for everyone.*
