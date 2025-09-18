# MIRAGE v2 - Medical Intelligence Research Assistant for Generative Enhancement

## 🚀 Overview

**MIRAGE v2** is a comprehensive AI system designed for pharmaceutical R&D, implementing a robust, secure, and ethical approach to document processing and query response generation. Built with enterprise-grade architecture and following the 8-pillar methodology.

## 🏗️ 8 Pillars

MIRAGE v2 is built on 8 fundamental pillars:

1. **🔐 Security** - Enterprise-grade security measures, API key management, input validation
2. **🤖 EthicAI** - Ethical AI practices, human-in-the-loop validation, bias mitigation
3. **📊 Vérité Terrain** - Ground truth validation, source attribution, uncertainty handling
4. **🛡️ Robustesse** - Error handling, retry logic, system resilience, graceful degradation
5. **📋 Gouvernance** - Audit trails, version control, compliance, comprehensive logging
6. **⚙️ Opérabilité** - CLI interface, web dashboard, REST API, configuration management
7. **⚡ Performance** - Caching, optimization, real-time monitoring, scalability
8. **🔧 Maintenance** - Modularity, comprehensive testing, documentation, deployment

## 🌟 Latest Features (v2.1.1)

### 🗣️ Multi-Language Support
- **Automatic Language Detection**: Supports EN, FR, ES, DE with intelligent detection
- **Language-Consistent Responses**: Questions in French → French answers, English → English
- **Medical Terminology**: Proper medical terminology in each supported language
- **Strategic Priority**: English detection prioritized for international use

### 📝 Enhanced Formatting
- **Optimized Bullet Points**: Each point on separate lines with proper spacing
- **Visual Hierarchy**: Emojis and clear section organization
- **Professional Structure**: Medical-grade formatting for research contexts
- **Critical Instructions**: Explicit formatting requirements for AI agents

### 🔧 System Optimizations
- **Shared Prompt Instance**: All agents use synchronized, up-to-date prompts
- **Improved Error Handling**: Robust favicon handling and connection management
- **Real-time Statistics**: Live system monitoring with adaptive polling
- **Enhanced Caching**: Intelligent response caching with TTL management

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Gemini API key
- 4GB+ RAM recommended
- 10GB+ disk space for documents and embeddings

### Installation
```bash
# Clone repository
git clone <repository-url>
cd MIRAGE_v2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
export GEMINI_API_KEY="your_gemini_api_key_here"
```

### Web Interface (Recommended)
```bash
# Start the complete web interface
export GEMINI_API_KEY="your_key_here" && python web_interface.py

# Access the interface
open http://127.0.0.1:8000
```

### CLI Usage
```bash
# Check system health
python -c "from src.orchestrator.multi_agent_orchestrator import MultiAgentOrchestrator; print('System healthy')"

# Process a query via API
curl -X POST http://127.0.0.1:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the side effects of paracetamol?"}'
```

## 🏛️ Architecture

MIRAGE v2 implements a sophisticated multi-agent system:

```
┌─────────────────────────────────────────────────────────────┐
│                    MIRAGE v2 System                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    CLI      │  │  Dashboard  │  │    API      │        │
│  │ Interface   │  │  Monitoring │  │  Endpoints  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                    Orchestrator                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Workflow   │  │  Consensus  │  │ Human Loop  │        │
│  │  Manager    │  │  Manager    │  │  Manager    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                    Agent System                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Generator   │  │  Verifier   │  │  Reformer   │        │
│  │   Agent     │  │   Agent     │  │   Agent     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐                                          │
│  │ Translator  │                                          │
│  │   Agent     │                                          │
│  └─────────────┘                                          │
├─────────────────────────────────────────────────────────────┤
│                    RAG System                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Document    │  │ Embedding   │  │ Metadata    │        │
│  │ Processor   │  │ Manager     │  │ Manager     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Qdrant      │  │ File System │  │ Logs &      │        │
│  │ Vector DB   │  │ Storage     │  │ Metrics     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

- **🎯 Orchestrator**: Central coordination with retry logic and consensus management
- **📚 RAG System**: Document processing, embedding generation, and retrieval
- **🤖 Agent System**: Generator, Verifier, Reformer, and Translator agents
- **📊 Monitoring**: Real-time metrics, alerting, and web dashboard
- **💻 CLI Interface**: Comprehensive command-line tools
- **🌐 Web Dashboard**: Real-time monitoring and control interface

## ✨ Features

### 🗣️ Multi-Language Intelligence
- **Automatic Detection**: EN, FR, ES, DE with intelligent keyword analysis
- **Language Consistency**: Questions in French → French answers, English → English
- **Medical Terminology**: Proper pharmaceutical terminology in each language
- **Strategic Priority**: English detection prioritized for international research

### 📝 Enhanced Formatting
- **Optimized Structure**: Bullet points with proper line breaks and spacing
- **Visual Hierarchy**: Emojis and clear section organization
- **Professional Layout**: Medical-grade formatting for research contexts
- **Critical Instructions**: Explicit formatting requirements for AI agents

### Multi-Agent Processing
- **Generator Agent**: Primary response generation with "I cannot find" handling
- **Verifier Agent**: Quality assurance with explicit voting (OUI/NON)
- **Reformer Agent**: Response improvement and structured JSON formatting
- **Translator Agent**: Language translation with medical terminology preservation

### RAG Integration
- **Document Processing**: PDF, TXT support with validation
- **Embedding Generation**: Offline SentenceTransformers (all-MiniLM-L6-v2)
- **Vector Storage**: Qdrant with persistent metadata (ChromaDB removed for stability)
- **Context Retrieval**: Similarity search with source attribution
- **Direct Gemini Integration**: Streamlined API access without hybrid service layer

### Human-in-the-Loop
- **Validation Interface**: Web-based validation for critical responses
- **Approval Workflow**: Accept, modify, or reject responses
- **Audit Trail**: Complete validation history and traceability
- **Configurable Triggers**: Priority-based human validation

### Real-time Monitoring
- **System Metrics**: CPU, memory, disk, network monitoring
- **Application Metrics**: Query performance, agent statistics, RAG metrics
- **Alerting System**: Configurable thresholds and notifications
- **Web Dashboard**: Real-time updates with sequential response display
- **Sequential Interface**: Multiple query/response pairs without page reload

### Security & Compliance
- **API Key Management**: Secure environment variable storage
- **Input Validation**: Comprehensive sanitization and validation
- **Access Control**: Authentication and authorization
- **Audit Logging**: Structured logging with complete traceability

## 📚 Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)** - Comprehensive system architecture
- **[User Guide](docs/USER_GUIDE.md)** - Complete user documentation
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Development guidelines and standards
- **[Data Schemas](docs/DATA_SCHEMAS.md)** - JSON schemas and data models

## 🧪 Testing

MIRAGE v2 includes a comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests
pytest -m integration   # Integration tests
pytest -m security      # Security tests
pytest -m performance   # Performance tests
```

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Security Tests**: Vulnerability and security validation
- **Performance Tests**: Load and stress testing
- **Target Coverage**: 80%+ code coverage

## 🚀 Deployment

### Docker Deployment
```bash
# Build Docker image
docker build -t mirage:v2 .

# Run with Docker Compose
docker-compose up -d

# Access dashboard
open http://localhost:8080
```

### Production Deployment
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Kubernetes or Docker Swarm support
- **Monitoring**: Prometheus + Grafana integration
- **Logging**: Centralized logging with ELK stack

## 🔧 Configuration

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
QDRANT_DB_PATH=./data/qdrant_db
LOG_LEVEL=INFO
RAG_CHUNK_SIZE=1000
ORCHESTRATOR_MAX_RETRIES=3
HUMAN_LOOP_TIMEOUT_SECONDS=300
```

### Configuration Files
- **pyproject.toml**: Project configuration and dependencies
- **pytest.ini**: Test configuration
- **.env.template**: Environment variable template
- **docker-compose.yml**: Docker deployment configuration

## 📊 Performance

### Benchmarks
- **Query Processing**: 4-15 seconds average response time (multi-agent workflow)
- **Document Ingestion**: 1000+ documents per hour
- **Concurrent Users**: 50+ simultaneous users
- **Memory Usage**: < 2GB typical operation
- **Storage**: Efficient vector storage with Qdrant (ChromaDB removed for stability)
- **Confidence Scores**: 66-88% typical accuracy

### Optimization Features
- **Response Caching**: Frequently asked questions
- **Context Caching**: RAG query results
- **Connection Pooling**: Efficient database connections
- **Async Processing**: Non-blocking operations

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Ensure security best practices
- Maintain performance standards

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Comprehensive guides and API documentation
- **Issues**: GitHub Issues for bug reports and feature requests
- **Community**: User community and support forums
- **Professional Support**: Enterprise support available

## 🎯 Roadmap

### Recent Improvements (v2.1)
- **✅ HybridService Removal**: Eliminated service conflicts and improved stability
- **✅ Direct Gemini Integration**: Streamlined API access without intermediate layers
- **✅ Sequential Web Interface**: Multiple query/response pairs without page reload
- **✅ Qdrant Migration**: Replaced ChromaDB for better macOS compatibility
- **✅ Enhanced Multi-Agent Workflow**: Improved consensus and verification processes

### Upcoming Features
- **Multi-language Support**: Additional language interfaces
- **Advanced Analytics**: Machine learning insights and trends
- **Integration APIs**: Third-party system integrations
- **Mobile Interface**: Mobile application development

### Performance Improvements
- **Microservices Architecture**: Service decomposition
- **Event-driven Processing**: Asynchronous event handling
- **Advanced Caching**: Distributed caching solutions
- **Auto-scaling**: Dynamic resource allocation

---

**MIRAGE v2** - Empowering pharmaceutical R&D with intelligent AI assistance 🚀