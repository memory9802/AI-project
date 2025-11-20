# Project Context

## Purpose
AI-powered outfit recommendation system that helps users discover personalized clothing combinations through intelligent image analysis and conversational AI interactions.

## Tech Stack
- **Backend**: Python 3.12, Flask 3.0.0
- **AI/ML**: LangChain, Google Gemini API, OpenCV 4.12.0, Pillow 12.0.0
- **Database**: MySQL 8.0
- **Frontend**: HTML, CSS, JavaScript, Bootstrap, jQuery, Axios
- **Build Tools**: Webpack, npm
- **Container**: Docker, Docker Compose
- **Chatbot**: Line Bot SDK 3.21.0
- **Development**: Node.js v25.2.1, Python venv

## Project Conventions

### Code Style
- Python: Follow PEP 8 conventions
- JavaScript: ES6+ syntax, consistent indentation (2 spaces)
- HTML: Semantic markup, accessibility considerations
- CSS: BEM naming convention where applicable

### Architecture Patterns
- **MVC Pattern**: Flask app structure with blueprints
- **Microservices Ready**: Docker containerization for scalability
- **API-First Design**: RESTful endpoints for frontend-backend communication
- **AI Service Layer**: Dedicated LangChain agents for conversation handling

### Testing Strategy
- Unit tests for Python modules
- Integration tests for API endpoints
- Manual testing for AI conversation flows
- Docker environment testing for deployment consistency

### Git Workflow
- Feature branches for new development
- `system` branch for team collaboration
- Conventional commit messages focusing on team-relevant changes
- Code reviews before merging

## Domain Context
### Fashion & Style Domain
- Outfit coordination principles (color theory, style matching)
- Seasonal clothing recommendations
- Body type considerations for styling
- Fashion trend analysis

### AI Conversation Design
- Natural language processing for fashion queries
- Context-aware conversation memory
- Multi-turn dialogue handling
- Fallback responses for unsupported queries

## Important Constraints
- **AI API Limits**: Rate limiting for Gemini API calls
- **Image Processing**: File size and format restrictions
- **Memory Management**: Conversation history storage limitations
- **Privacy**: User data protection in recommendation system
- **Team Development**: 5-person collaborative development environment

## External Dependencies
- **Google Gemini API**: For AI conversation and recommendations
- **Line Messaging API**: For chatbot functionality
- **MySQL Database**: For user data and conversation history
- **Docker Services**: MySQL, phpMyAdmin containers
- **npm Packages**: Bootstrap, jQuery, Axios, Webpack toolchain
