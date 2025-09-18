# MIRAGE v2 - Architecture Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [8 Pillars Implementation](#8-pillars-implementation)
6. [Security Architecture](#security-architecture)
7. [Performance Considerations](#performance-considerations)
8. [Deployment Architecture](#deployment-architecture)

## Overview

MIRAGE v2 (Medical Intelligence Research Assistant for Generative Enhancement) is a comprehensive AI system designed for pharmaceutical R&D. It implements a robust, secure, and ethical approach to document processing and query response generation.

### Key Features
- **Multi-Agent System**: Generator, Verifier, Reformer, and Translator agents
- **RAG System**: Document ingestion, embedding, and retrieval
- **Human-in-the-Loop**: Validation and oversight for critical responses
- **Asynchronous Startup**: Optimized system initialization
- **Bilingual Interface**: French and English support
- **Real-time Monitoring**: Comprehensive metrics and alerting
- **Authentication & Security**: Enterprise-grade security measures
- **Testing Framework**: Comprehensive test coverage

## System Architecture

### High-Level Architecture

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

### Component Interaction Flow

```
Query Input → Orchestrator → RAG Engine → Context Retrieval
     ↓
Generator Agent → Response Generation
     ↓
Verifier Agent → Quality Assessment (VOTE: OUI/NON)
     ↓
Consensus Manager → Decision Making
     ↓
[If NON] → Reformer Agent → Response Improvement
     ↓
[If Human Loop] → Human Validation
     ↓
Translator Agent → Language Translation
     ↓
Final Response → Output
```

## Core Components

### 1. Orchestrator
**Purpose**: Central coordination of all system components
**Key Features**:
- Retry logic with exponential backoff
- Consensus management
- Human-in-the-loop integration
- Caching for performance
- Error handling and recovery

**Key Classes**:
- `Orchestrator`: Main orchestration logic
- `WorkflowManager`: State management
- `ConsensusManager`: Decision making
- `HumanLoopManager`: Human validation

### 2. Agent System
**Purpose**: Specialized AI agents for different tasks

#### Generator Agent
- **Role**: Primary response generation
- **Input**: Query + RAG context
- **Output**: Initial response
- **Special Feature**: "I cannot find this information" handling

#### Verifier Agent
- **Role**: Quality assurance and validation
- **Input**: Query + Context + Generated response
- **Output**: VOTE (OUI/NON) + Analysis
- **Special Feature**: Security and accuracy validation

#### Reformer Agent
- **Role**: Response improvement and formatting
- **Input**: Query + Context + Response + Verifier feedback
- **Output**: Structured JSON response
- **Special Feature**: Strict JSON formatting

#### Translator Agent
- **Role**: Language translation
- **Input**: Response + Target language
- **Output**: Translated response
- **Special Feature**: Medical terminology preservation

### 3. RAG System
**Purpose**: Document processing and retrieval

#### Document Processor
- **Function**: Document loading and splitting
- **Technologies**: LangChain, PyPDF
- **Features**: Validation, chunking, metadata extraction

#### Embedding Manager
- **Function**: Vector embedding generation
- **Technologies**: SentenceTransformers, ChromaDB
- **Features**: Offline embeddings, persistent storage

#### Metadata Manager
- **Function**: Metadata management
- **Features**: Document tracking, versioning, audit trails

### 4. Monitoring System
**Purpose**: System monitoring and alerting

#### System Monitor
- **Function**: Real-time system monitoring
- **Metrics**: CPU, memory, disk, network
- **Features**: Threshold monitoring, health checks

#### Metrics Collector
- **Function**: Detailed metrics collection
- **Metrics**: Query performance, agent statistics, RAG metrics
- **Features**: Aggregation, historical data

#### Dashboard Server
- **Function**: Web-based monitoring interface
- **Features**: Real-time updates, WebSocket, controls

#### Alert Manager
- **Function**: Alert generation and management
- **Features**: Configurable rules, notifications, suppression

## Data Flow

### 1. Document Ingestion Flow
```
PDF/TXT Document → Document Processor → Validation
     ↓
Text Splitting → Chunk Creation → Metadata Generation
     ↓
Embedding Generation → Vector Storage (ChromaDB)
     ↓
Metadata Storage → Index Update
```

### 2. Query Processing Flow
```
User Query → Input Validation → Query Hashing
     ↓
RAG Query → Context Retrieval → Similarity Search
     ↓
Generator Agent → Response Generation
     ↓
Verifier Agent → Quality Assessment
     ↓
Consensus Decision → [Reform/Approve/Human Loop]
     ↓
Translation (if needed) → Final Response
```

### 3. Monitoring Flow
```
System Metrics → Metrics Collector → Aggregation
     ↓
Threshold Check → Alert Generation → Notification
     ↓
Dashboard Update → WebSocket Broadcast → UI Update
```

## 8 Pillars Implementation

### 1. Security
- **API Key Management**: Environment variables, secure storage
- **Input Validation**: Sanitization, size limits, type checking
- **Access Control**: Authentication, authorization, audit logging
- **Data Protection**: Encryption, anonymization, retention policies

### 2. EthicAI
- **Human-in-the-Loop**: Validation for critical responses
- **Transparency**: Clear decision making, explainable AI
- **Bias Mitigation**: Diverse training data, fairness checks
- **Privacy**: Data minimization, consent management

### 3. Vérité Terrain
- **Ground Truth**: Validation against known facts
- **Source Attribution**: Document references, citations
- **Uncertainty Handling**: "I cannot find" responses
- **Quality Metrics**: Accuracy, completeness, relevance

### 4. Robustesse
- **Error Handling**: Graceful degradation, recovery
- **Retry Logic**: Exponential backoff, circuit breakers
- **Monitoring**: Health checks, performance metrics
- **Testing**: Comprehensive test coverage

### 5. Gouvernance
- **Audit Trails**: Complete operation logging
- **Version Control**: Code and data versioning
- **Compliance**: Regulatory requirements
- **Documentation**: Comprehensive documentation

### 6. Opérabilité
- **CLI Interface**: Command-line tools
- **Dashboard**: Web-based monitoring
- **API**: RESTful endpoints
- **Configuration**: Environment-based config

### 7. Performance
- **Caching**: Response and context caching
- **Optimization**: Efficient algorithms, resource management
- **Scalability**: Horizontal scaling, load balancing
- **Monitoring**: Performance metrics, alerting

### 8. Maintenance
- **Modularity**: Clean architecture, separation of concerns
- **Testing**: Unit, integration, performance tests
- **Documentation**: Code documentation, runbooks
- **Deployment**: Containerization, CI/CD

## Security Architecture

### Authentication & Authorization
```
User Request → API Key Validation → Permission Check
     ↓
Access Granted/Denied → Audit Logging → Response
```

### Data Security
- **Encryption**: AES-256 for sensitive data
- **Anonymization**: PII removal, data masking
- **Access Control**: Role-based permissions
- **Audit Logging**: Complete operation tracking

### Network Security
- **CORS**: Cross-origin resource sharing
- **HTTPS**: Encrypted communication
- **Firewall**: Network access control
- **Rate Limiting**: DDoS protection

## Performance Considerations

### Caching Strategy
- **Response Cache**: Frequently asked questions
- **Context Cache**: RAG query results
- **TTL**: Time-to-live for cache entries
- **Invalidation**: Cache invalidation strategies

### Resource Management
- **Memory**: Efficient data structures, garbage collection
- **CPU**: Optimized algorithms, parallel processing
- **Disk**: Efficient storage, cleanup policies
- **Network**: Connection pooling, compression

### Scalability
- **Horizontal Scaling**: Multiple instances
- **Load Balancing**: Request distribution
- **Database**: Connection pooling, indexing
- **Monitoring**: Performance metrics, alerting

## Deployment Architecture

### Development Environment
```
Local Machine → Python Virtual Environment → MIRAGE v2
     ↓
Local ChromaDB → Local File Storage → Local Logs
```

### Production Environment
```
Load Balancer → Multiple MIRAGE Instances → Shared ChromaDB
     ↓
Monitoring Stack → Prometheus + Grafana → Alerting
     ↓
Log Aggregation → ELK Stack → Analysis
```

### Container Architecture
```
Docker Container → MIRAGE v2 Application
     ↓
Volume Mounts → Data Persistence
     ↓
Environment Variables → Configuration
     ↓
Health Checks → Container Orchestration
```

## Technology Stack

### Core Technologies
- **Python 3.9+**: Main programming language
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Click**: CLI framework
- **Structlog**: Structured logging

### AI/ML Technologies
- **Google Gemini**: Large language model
- **SentenceTransformers**: Embedding generation
- **ChromaDB**: Vector database
- **LangChain**: Document processing

### Monitoring & Observability
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **WebSocket**: Real-time updates
- **Chart.js**: Client-side charts

### Development & Testing
- **Pytest**: Testing framework
- **Coverage**: Code coverage
- **Black**: Code formatting
- **Flake8**: Linting

## Configuration Management

### Environment Variables
```bash
# API Configuration
GEMINI_API_KEY=your_api_key_here

# Database Configuration
CHROMA_DB_PATH=./data/embeddings

# Logging Configuration
LOG_LEVEL=INFO

# RAG Configuration
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
RAG_MAX_RESULTS=5

# Orchestrator Configuration
ORCHESTRATOR_MAX_RETRIES=3
ORCHESTRATOR_RETRY_DELAY_SECONDS=1
ORCHESTRATOR_CACHE_TTL_SECONDS=3600

# Human-in-the-Loop Configuration
HUMAN_LOOP_TIMEOUT_SECONDS=300
HUMAN_LOOP_PRIORITY_THRESHOLD=0.3
```

### Configuration Files
- **pyproject.toml**: Project configuration
- **pytest.ini**: Test configuration
- **.env.template**: Environment template
- **.gitignore**: Version control exclusions

## API Documentation

### REST Endpoints
- **GET /api/status**: System status
- **GET /api/health**: Health check
- **POST /api/query**: Process query
- **GET /api/metrics**: System metrics
- **GET /api/alerts**: Active alerts

### WebSocket Endpoints
- **WS /ws**: Real-time updates

### CLI Commands
- **mirage query**: Process query
- **mirage health**: Health check
- **mirage monitor**: Start monitoring
- **mirage config**: Configuration management

## Error Handling

### Error Types
- **Validation Errors**: Input validation failures
- **API Errors**: External API failures
- **System Errors**: Internal system failures
- **Network Errors**: Connectivity issues

### Error Recovery
- **Retry Logic**: Exponential backoff
- **Circuit Breakers**: Failure isolation
- **Graceful Degradation**: Partial functionality
- **Fallback Responses**: Default responses

## Monitoring & Alerting

### Metrics
- **System Metrics**: CPU, memory, disk, network
- **Application Metrics**: Query performance, agent statistics
- **Business Metrics**: Success rates, user satisfaction
- **Error Metrics**: Error rates, failure patterns

### Alerts
- **Threshold Alerts**: Performance thresholds
- **Error Alerts**: System errors
- **Health Alerts**: Component failures
- **Custom Alerts**: Business-specific alerts

## Testing Strategy

### Test Types
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **Performance Tests**: Load and stress testing
- **Security Tests**: Security vulnerability testing

### Test Coverage
- **Code Coverage**: Minimum 80% coverage
- **Functional Coverage**: All features tested
- **Performance Coverage**: Performance benchmarks
- **Security Coverage**: Security test cases

## Deployment Strategy

### Development
- **Local Development**: Docker Compose
- **Testing**: Automated test execution
- **Code Quality**: Linting, formatting, coverage

### Production
- **Containerization**: Docker containers
- **Orchestration**: Kubernetes or Docker Swarm
- **Monitoring**: Prometheus + Grafana
- **Logging**: Centralized logging

## Maintenance & Support

### Regular Maintenance
- **Security Updates**: Regular security patches
- **Performance Optimization**: Continuous improvement
- **Documentation Updates**: Keep documentation current
- **Backup & Recovery**: Regular backups

### Support Procedures
- **Incident Response**: Emergency procedures
- **Troubleshooting**: Common issues and solutions
- **Performance Tuning**: Optimization guidelines
- **Upgrade Procedures**: Version upgrade steps

## Future Enhancements

### Planned Features
- **Multi-language Support**: Additional languages
- **Advanced Analytics**: Machine learning insights
- **Integration APIs**: Third-party integrations
- **Mobile Interface**: Mobile application

### Scalability Improvements
- **Microservices**: Service decomposition
- **Event-driven Architecture**: Asynchronous processing
- **Advanced Caching**: Distributed caching
- **Auto-scaling**: Dynamic resource allocation

## Conclusion

MIRAGE v2 represents a comprehensive, enterprise-grade solution for pharmaceutical R&D. Its architecture is designed for scalability, security, and maintainability while providing powerful AI capabilities for document processing and query response generation.

The system's modular design allows for easy extension and customization, while its robust monitoring and testing framework ensures reliability and performance in production environments.
