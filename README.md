# 🤖 Customer Support AI Platform

A full-stack customer support platform powered by AI. Built with FastAPI, React TypeScript, and Google Gemini API with a bit MCP (Model Context Protocol) integration.

![Platform Demo](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Tech Stack](https://img.shields.io/badge/Stack-FastAPI%20%2B%20React%20%2B%20TypeScript-blue)
![AI Powered](https://img.shields.io/badge/AI-Google%20Gemini-orange)

## ✨ Features

### 🎯 **Core Capabilities**
- **AI-Powered Customer Support**: Automated Tier-1 support using Google Gemini API
- **Real-time Chat Interface**: Instant customer messaging with AI responses
- **Admin Dashboard**: Comprehensive analytics and conversation management
- **System Prompt Management**: Customizable AI behavior for different departments
- **Live Analytics**: Real-time metrics and conversation tracking
- **Confidence Scoring**: AI response confidence indicators

### 🚀 **Production Features**
- **WebSocket Support**: Real-time communication
- **Database Persistence**: SQLAlchemy with SQLite/PostgreSQL support
- **Type Safety**: Full TypeScript implementation
- **Professional UI**: Material-UI components
- **API Documentation**: Auto-generated FastAPI docs
- **Error Handling**: Comprehensive error management
- **Scalable Architecture**: Modular, maintainable codebase

## 🛠 Tech Stack

### Backend
- **FastAPI**: Modern Python web framework with auto-docs
- **SQLAlchemy**: Database ORM with migration support
- **Google Generative AI**: AI responses via Gemini API
- **Some parts MCP (Model Context Protocol)**: Anthropic's protocol for AI interactions
- **WebSockets**: Real-time communication
- **Pydantic**: Data validation and serialization

### Frontend
- **React 18**: Modern React with hooks and concurrent features
- **TypeScript**: Type-safe JavaScript development
- **Material-UI (MUI)**: Professional, accessible UI components
- **Axios**: HTTP client with interceptors
- **React Router**: Client-side routing

### Database & Infrastructure
- **SQLite**: Development database (easily switchable to PostgreSQL)
- **SQLAlchemy Models**: Customer, Conversation, Message, SystemPrompt
- **Database Migrations**: Alembic support ready
- **Environment Configuration**: Flexible deployment options

## 📁 Project Structure

```
customer-support-ai/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── customer.py
│   │   │   ├── conversation.py
│   │   │   ├── message.py
│   │   │   └── system_prompt.py
│   │   ├── services/          # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── chat_service.py
│   │   │   ├── admin_service.py
│   │   │   └── ai_service.py
│   │   └── api/              # API routes
│   │       ├── __init__.py
│   │       ├── chat.py
│   │       └── admin.py
│   ├── main.py               # FastAPI application
│   ├── requirements.txt      # Python dependencies
│   ├── init_data.py         # Database initialization
│   └── customer_support.db  # SQLite database
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── ChatInterface.tsx
│   │   │   └── AdminDashboard.tsx
│   │   ├── services/        # API services
│   │   │   └── api.ts
│   │   ├── types/          # TypeScript types
│   │   │   └── index.ts
│   │   ├── App.tsx         # Main app component
│   │   └── index.tsx       # React entry point
│   ├── package.json        # Node.js dependencies
│   └── tsconfig.json       # TypeScript configuration
└── shared/                 # Shared types and utilities
    └── types/
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))

### 1. Clone & Setup
```bash
git clone <repository-url>
cd customer-support-ai
```

### 2. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export GEMINI_API_KEY="your_gemini_api_key_here"

# Initialize database with sample data
python init_data.py

# Start the server
python main.py
```
🌐 Backend available at: `http://localhost:8000`
📚 API docs at: `http://localhost:8000/docs`

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```
🌐 Frontend available at: `http://localhost:3000`

## 📡 API Reference

### Chat Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/chat/start` | Start new chat session |
| `POST` | `/api/v1/chat/message` | Send message & get AI response |
| `GET` | `/api/v1/chat/history/{session_id}` | Get conversation history |

### Admin Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/admin/analytics` | Dashboard analytics |
| `GET` | `/api/v1/admin/prompts` | List system prompts |
| `POST` | `/api/v1/admin/prompts` | Create system prompt |
| `PUT` | `/api/v1/admin/prompts/{id}` | Update system prompt |

### Health Check
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health status |

## 🎯 Key Features Breakdown

### 💬 Customer Chat Interface
- **Real-time Messaging**: Instant message delivery
- **AI Responses**: Powered by Google Gemini with confidence scores
- **Message History**: Persistent conversation tracking
- **Professional UI**: Clean, intuitive Material-UI design
- **Responsive Design**: Works on desktop and mobile

### 📊 Admin Dashboard
- **Live Analytics**: 
  - Total & Active Conversations
  - Message Count
  - Support Actions
- **Conversation Management**: Recent conversations table
- **System Prompt CRUD**: Create, read, update system prompts
- **Real-time Updates**: Live data refresh

### 🧠 AI Integration
- **Google Gemini API**: Advanced language model
- **Custom System Prompts**: Department-specific AI behavior
- **Confidence Scoring**: Response quality indicators
- **Fallback Handling**: Graceful error management
- **MCP Protocol**: Anthropic's Model Context Protocol

## 🔧 Configuration

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
DATABASE_URL=sqlite:///./customer_support.db  # Default
PORT=8000                                      # Default
HOST=0.0.0.0                                  # Default
```

### Database Configuration
The application uses SQLite by default but can be easily configured for PostgreSQL:

```python
# For PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/customer_support
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Testing
```bash
cd frontend
npm test
npm run test:coverage
```

### End-to-End Testing
```bash
# Start both servers
npm run test:e2e
```

## 🚀 Production Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Manual Deployment
```bash
# Frontend build
cd frontend
npm run build

# Backend production server
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Environment Setup
```bash
# Production environment variables
export GEMINI_API_KEY="your_production_api_key"
export DATABASE_URL="postgresql://user:pass@host:5432/db"
export ENVIRONMENT="production"
```

## 🔒 Security Features

- **Input Validation**: Pydantic models for all API inputs
- **SQL Injection Protection**: SQLAlchemy ORM
- **CORS Configuration**: Configurable cross-origin requests
- **Rate Limiting**: API rate limiting (configurable)
- **Environment Variables**: Secure credential management

## 📈 Performance

- **Async/Await**: Non-blocking I/O operations
- **Connection Pooling**: Database connection optimization
- **Caching**: Response caching for static data
- **Lazy Loading**: Efficient data loading strategies
- **WebSocket Optimization**: Real-time communication

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow TypeScript/Python type hints
- Add tests for new features
- Update documentation
- Follow existing code style
- Add meaningful commit messages

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.



## 📞 Support

For support, email iradukundavierra4@gmail.com or create an issue in this repository.

---
N.B: This is a proof of concept/for demonstration, it is not ready now for usage!
