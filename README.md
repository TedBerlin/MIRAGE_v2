# MIRAGE v2 - Medical Intelligence Research Assistant for Generative Enhancement

## 🚀 Overview

**MIRAGE v2** is a comprehensive AI system designed for pharmaceutical R&D, implementing a robust, secure, and ethical approach to document processing and query response generation. Built with enterprise-grade architecture and following the 8-pillar methodology.

## 🏗️ 8 Strategic Pillars

MIRAGE v2 is built on 8 fundamental pillars:

1. **🌍 Multi-Language Support** - Automatic detection and response in EN, FR, ES, DE
2. **👥 Human-in-the-Loop** - Human validation for safety and accuracy
3. **🤖 Multi-Agent Workflow** - Generator → Verifier → Reformer → Human validation
4. **📚 RAG System** - Retrieval-Augmented Generation with vector database
5. **🎨 Enhanced Formatting** - Professional medical formatting with emojis
6. **🔗 Gemini API Integration** - Google Gemini AI for advanced language processing
7. **📄 Document Processing** - PDF, DOCX, TXT processing with chunking
8. **📊 System Monitoring** - Real-time health checks and performance metrics

## 🌟 Latest Features (v2.0-optimized)

### 🗣️ Multi-Language Support
- **Automatic Language Detection**: Supports EN, FR, ES, DE with intelligent detection
- **Language-Consistent Responses**: Questions in French → French answers, English → English
- **Medical Terminology**: Proper medical terminology in each supported language
- **Strategic Priority**: English detection prioritized for international use

### 🤖 Multi-Agent System
- **Generator Agent**: Primary response generation with pharmaceutical focus
- **Verifier Agent**: Quality assurance and validation with voting system
- **Reformer Agent**: Response refinement and JSON format output
- **Translator Agent**: Multi-language translation and localization

### 📚 RAG System
- **Vector Database**: Qdrant for efficient similarity search
- **Document Processing**: PDF, DOCX, TXT with intelligent chunking
- **Embedding Model**: Sentence-transformers for semantic understanding
- **Source Attribution**: Proper citation and confidence scoring

### 🎨 Enhanced Formatting
- **Professional Structure**: Medical-grade formatting for research contexts
- **Visual Hierarchy**: Emojis and clear section organization
- **JSON Output**: Structured responses with metadata
- **Critical Instructions**: Explicit formatting requirements for AI agents

### 🔧 System Optimizations
- **Docker Support**: Containerized deployment with Docker Compose
- **Optimized Dependencies**: 72% reduction in package count (89 → 25)
- **Reduced Image Size**: 80% reduction (2.5GB → 500MB)
- **Faster Installation**: 5x faster setup (5-10min → 1-2min)

## 🚀 Quick Start

### Prerequisites
- **Python**: 3.9+ (max 3.11.x recommended)
- **Docker**: 20.10+ (recommended for production)
- **RAM**: 4GB+ recommended
- **Disk Space**: 10GB+ for documents and embeddings
- **API Key**: Gemini API key required

### Installation

#### Option 1: Docker (Recommended)
```bash
# Clone repository
git clone https://github.com/your-org/mirage-v2.git
cd mirage-v2

# Set up environment
cp env.template .env
# Edit .env with your GEMINI_API_KEY

# Start with Docker
chmod +x mirage-minimal.sh
./mirage-minimal.sh start

# Access the application
open http://localhost:8005
```

#### Option 2: Native Python
```bash
# Clone repository
git clone https://github.com/your-org/mirage-v2.git
cd mirage-v2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-minimal.txt

# Set up environment
cp env.template .env
# Edit .env with your GEMINI_API_KEY

# Start the application
python web_interface.py
```

## 📊 Performance Metrics

### System Performance
- **Response Time**: 4.57s average (optimized)
- **Success Rate**: 100% (1.0)
- **Uptime**: 24h+ stable
- **Memory Usage**: Optimized for production

### Multi-Language Performance
- **English**: 4.8s average
- **French**: 5.2s average  
- **Spanish**: 3.9s average
- **German**: 4.2s average

### Docker Optimization
- **Dependencies**: 25 packages (vs 89 original)
- **Image Size**: 500MB (vs 2.5GB original)
- **Installation**: 1-2 minutes (vs 5-10 minutes)
- **Stability**: 100% container stability

## 🔧 Configuration

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here

# Optional
ENVIRONMENT=production
PYTHONPATH=/app
```

### API Endpoints
- **Health Check**: `GET /health`
- **System Stats**: `GET /api/stats`
- **Query Processing**: `POST /api/query`
- **Document Upload**: `POST /api/rag/ingest`
- **Human Validation**: `POST /api/validation/submit`

## 🧪 Testing

### Comprehensive Test Suite
- **50+ Questions**: Multi-language test coverage
- **Performance Testing**: Load testing and stress testing
- **Human-in-the-Loop**: Validation workflow testing
- **Multi-Agent**: Workflow and consensus testing

### Test Categories
1. **Simple Questions**: Basic functionality testing
2. **Complex Questions**: Multi-agent workflow testing
3. **Out-of-Context**: "I don't know" response testing
4. **Safety Questions**: Human validation triggering
5. **Technical Questions**: RAG and formatting testing

## 📚 Documentation

- **Architecture**: `docs/ARCHITECTURE.md`
- **Developer Guide**: `docs/DEVELOPER_GUIDE.md`
- **User Guide**: `docs/USER_GUIDE.md`
- **Test Plan**: `PLAN_TEST_COMPLET_v2.md`
- **Optimization Report**: `RAPPORT_OPTIMISATION_FINAL.md`

## 🔒 Security & Compliance

- **API Key Management**: Secure environment variable handling
- **Input Validation**: Comprehensive request validation
- **Human Validation**: Safety-critical response validation
- **Audit Trails**: Complete request/response logging
- **Data Privacy**: GDPR-compliant data handling

## 📈 Monitoring

### System Health
- **Real-time Status**: Live health monitoring
- **Performance Metrics**: Response time and success rate tracking
- **Error Handling**: Graceful degradation and recovery
- **Resource Usage**: Memory and CPU monitoring

### Human Validation
- **Validation Queue**: Pending human validations
- **Approval Rate**: Human validation statistics
- **Processing Time**: Validation workflow timing
- **Safety Triggers**: Automatic safety validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/mirage-v2/issues)
- **Documentation**: [Wiki](https://github.com/your-org/mirage-v2/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/mirage-v2/discussions)

## 🏆 Acknowledgments

- **Google Gemini**: Advanced language processing capabilities
- **Qdrant**: Vector database for semantic search
- **FastAPI**: Modern web framework for APIs
- **Docker**: Containerization and deployment
- **Open Source Community**: Various Python packages and tools

---

**MIRAGE v2** - Empowering pharmaceutical research with AI-driven intelligence and human validation.