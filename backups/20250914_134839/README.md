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
pip install -e .

# Configure environment
cp .env.template .env
# Edit .env with your API key: GEMINI_API_KEY=your_key_here
```

### Basic Usage
```bash
# Check system health
mirage health

# Process a query
mirage query "What are the side effects of this medication?"

# Process with human-in-the-loop
mirage query "What are the contraindications?" --human

# Start monitoring dashboard
python scripts/start_dashboard.py
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
│  │ ChromaDB    │  │ File System │  │ Logs &      │        │
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

### Multi-Agent Processing
- **Generator Agent**: Primary response generation with "I cannot find" handling
- **Verifier Agent**: Quality assurance with explicit voting (OUI/NON)
- **Reformer Agent**: Response improvement and structured JSON formatting
- **Translator Agent**: Language translation with medical terminology preservation

### RAG Integration
- **Document Processing**: PDF, TXT support with validation
- **Embedding Generation**: Offline SentenceTransformers (all-MiniLM-L6-v2)
- **Vector Storage**: ChromaDB with persistent metadata
- **Context Retrieval**: Similarity search with source attribution

### Human-in-the-Loop
- **Validation Interface**: Web-based validation for critical responses
- **Approval Workflow**: Accept, modify, or reject responses
- **Audit Trail**: Complete validation history and traceability
- **Configurable Triggers**: Priority-based human validation

### Real-time Monitoring
- **System Metrics**: CPU, memory, disk, network monitoring
- **Application Metrics**: Query performance, agent statistics, RAG metrics
- **Alerting System**: Configurable thresholds and notifications
- **Web Dashboard**: Real-time updates with WebSocket integration

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
CHROMA_DB_PATH=./data/embeddings
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
- **Query Processing**: < 5 seconds average response time
- **Document Ingestion**: 1000+ documents per hour
- **Concurrent Users**: 50+ simultaneous users
- **Memory Usage**: < 2GB typical operation
- **Storage**: Efficient vector storage with ChromaDB

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