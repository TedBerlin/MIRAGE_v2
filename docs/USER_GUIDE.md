# MIRAGE v2 - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [CLI Usage](#cli-usage)
5. [Dashboard Usage](#dashboard-usage)
6. [API Usage](#api-usage)
7. [Document Management](#document-management)
8. [Query Processing](#query-processing)
9. [Monitoring & Alerts](#monitoring--alerts)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)

## Getting Started

MIRAGE v2 is a comprehensive AI system for pharmaceutical R&D that provides intelligent document processing and query response generation. This guide will help you get started with the system.

### Prerequisites
- Python 3.9 or higher
- Gemini API key
- 4GB+ RAM recommended
- 10GB+ disk space for documents and embeddings

### Quick Start
1. Clone the repository
2. Install dependencies
3. Configure your API key
4. Start the system
5. Begin processing documents and queries

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd MIRAGE_v2
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -e .
```

### 4. Verify Installation
```bash
mirage --version
```

## Configuration

### Environment Setup
Create a `.env` file in the project root:

```bash
# Copy template
cp .env.template .env

# Edit configuration
nano .env
```

### Required Configuration
```bash
# API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

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

### Optional Configuration
```bash
# Performance Configuration
MAX_CONCURRENT_QUERIES=10
CACHE_SIZE_LIMIT=1000

# Monitoring Configuration
MONITORING_INTERVAL=30
ALERT_EMAIL=admin@company.com

# Security Configuration
API_RATE_LIMIT=100
SESSION_TIMEOUT=3600
```

## CLI Usage

MIRAGE v2 provides a comprehensive command-line interface for all operations.

### Basic Commands

#### System Status
```bash
# Check system health
mirage health

# Get system status
mirage status

# View configuration
mirage config --config
```

#### Query Processing
```bash
# Process a single query
mirage query "What are the side effects of this medication?"

# Process with human-in-the-loop
mirage query "What are the contraindications?" --human

# Process with specific language
mirage query "What is the mechanism of action?" --language fr

# Process with verbose output
mirage query "What are the drug interactions?" --verbose
```

#### Document Management
```bash
# Ingest documents
mirage rag --ingest

# Add specific document
mirage rag --add document.pdf

# View RAG statistics
mirage rag --stats

# Clear all documents
mirage rag --clear
```

#### Agent Management
```bash
# List all agents
mirage agents --list

# Test specific agent
mirage agents --test generator

# Test all agents
mirage agents --test all

# Get agent information
mirage agents --info verifier
```

#### Monitoring
```bash
# Start real-time monitoring
mirage monitor --monitor

# View recent logs
mirage monitor --logs

# Show performance metrics
mirage monitor --metrics

# Clear log files
mirage monitor --clear-logs
```

#### Validation & Testing
```bash
# Validate system configuration
mirage config --validate

# Run batch validation
mirage validate questions.txt

# Export validation results
mirage validate questions.txt --output results.json --format json

# Audit specific query
mirage audit query_id_123
```

### Advanced CLI Usage

#### Batch Processing
```bash
# Process multiple queries from file
mirage validate questions.txt --output results.csv --format csv

# Run performance tests
mirage validate questions.txt --verbose --output performance_report.json
```

#### Configuration Management
```bash
# Reset to default configuration
mirage config --reset

# Validate current configuration
mirage config --validate

# Show current configuration
mirage config --config
```

#### System Management
```bash
# Clear all metrics
mirage monitor --clear-metrics

# Export system metrics
mirage monitor --export-metrics

# Start dashboard
mirage dashboard --start
```

## Dashboard Usage

The MIRAGE v2 Dashboard provides a web-based interface for monitoring and control.

### Starting the Dashboard
```bash
# Start dashboard with default settings
python scripts/start_dashboard.py

# Start with custom host and port
python scripts/start_dashboard.py --host 0.0.0.0 --port 8080

# Start with specific API key
python scripts/start_dashboard.py --api-key your_key_here
```

### Dashboard Features

#### System Status
- **Overall Health**: System health indicator
- **CPU Usage**: Real-time CPU utilization
- **Memory Usage**: Memory consumption
- **Disk Usage**: Disk space utilization

#### Query Metrics
- **Total Queries**: Number of processed queries
- **Success Rate**: Percentage of successful queries
- **Average Duration**: Mean processing time
- **Average Iterations**: Mean iterations per query

#### Agent Metrics
- **Generator**: Generator agent statistics
- **Verifier**: Verifier agent statistics
- **Reformer**: Reformer agent statistics
- **Translator**: Translator agent statistics

#### RAG Metrics
- **Total Operations**: RAG system operations
- **Success Rate**: RAG operation success rate
- **Documents Processed**: Number of processed documents
- **Chunks Created**: Number of created chunks

#### Performance Trends
- **Real-time Charts**: Performance over time
- **Interactive Graphs**: Zoom and filter capabilities
- **Export Options**: Download chart data

#### Alert Management
- **Active Alerts**: Current system alerts
- **Alert Acknowledgment**: Mark alerts as acknowledged
- **Alert History**: Historical alert data
- **Alert Configuration**: Customize alert rules

### Dashboard Controls

#### Refresh Data
- **Manual Refresh**: Click refresh button
- **Auto Refresh**: Automatic updates every 5 seconds
- **Real-time Updates**: WebSocket-based updates

#### Export Data
- **Metrics Export**: Download metrics in JSON/CSV
- **Chart Export**: Save charts as images
- **Report Generation**: Generate comprehensive reports

#### System Control
- **Clear Metrics**: Reset all metrics data
- **Restart Services**: Restart system components
- **Configuration**: Update system settings

## API Usage

MIRAGE v2 provides a RESTful API for programmatic access.

### Authentication
All API requests require an API key in the header:
```bash
curl -H "X-API-Key: your_api_key" http://localhost:8000/api/status
```

### Core Endpoints

#### System Status
```bash
# Get system status
GET /api/status

# Health check
GET /api/health

# System metrics
GET /api/metrics
```

#### Query Processing
```bash
# Process query
POST /api/query
Content-Type: application/json

{
  "query": "What are the side effects?",
  "enable_human_loop": false,
  "target_language": "en"
}
```

#### Document Management
```bash
# Upload document
POST /api/documents/upload
Content-Type: multipart/form-data

# List documents
GET /api/documents

# Delete document
DELETE /api/documents/{document_id}
```

#### Monitoring
```bash
# Get metrics
GET /api/metrics/query
GET /api/metrics/agents
GET /api/metrics/rag
GET /api/metrics/system

# Get alerts
GET /api/alerts

# Acknowledge alert
POST /api/alerts/{alert_id}/acknowledge
```

### WebSocket API
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8080/ws');

// Listen for updates
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Update:', data);
};
```

## Document Management

### Supported Formats
- **PDF**: Pharmaceutical documents, research papers
- **TXT**: Plain text documents
- **DOCX**: Microsoft Word documents (future)

### Document Ingestion

#### Single Document
```bash
# Add single document
mirage rag --add document.pdf

# Verify ingestion
mirage rag --stats
```

#### Batch Ingestion
```bash
# Ingest all documents in directory
mirage rag --ingest

# Check ingestion status
mirage rag --stats
```

#### Document Validation
- **Size Limits**: Minimum 1KB, maximum 100MB
- **Format Validation**: File type verification
- **Content Validation**: Text extraction verification
- **Metadata Extraction**: Document information extraction

### Document Processing

#### Text Splitting
- **Chunk Size**: Configurable (default 1000 characters)
- **Overlap**: Configurable (default 200 characters)
- **Metadata**: Preserved with each chunk
- **Indexing**: Automatic vector indexing

#### Embedding Generation
- **Model**: SentenceTransformers (all-MiniLM-L6-v2)
- **Offline Processing**: No external API calls
- **Vector Storage**: ChromaDB persistent storage
- **Similarity Search**: Cosine similarity matching

### Document Management

#### Viewing Documents
```bash
# List all documents
mirage rag --stats

# View document details
mirage rag --info document_id
```

#### Document Operations
```bash
# Update document
mirage rag --update document_id

# Delete document
mirage rag --delete document_id

# Reindex document
mirage rag --reindex document_id
```

## Query Processing

### Query Types

#### Simple Queries
```bash
# Basic question
mirage query "What are the side effects?"

# Specific information
mirage query "What is the recommended dosage?"
```

#### Complex Queries
```bash
# Multi-part question
mirage query "What are the side effects and contraindications?"

# Comparative question
mirage query "How does this medication compare to alternatives?"
```

#### Language-Specific Queries
```bash
# English query
mirage query "What are the side effects?" --language en

# French query
mirage query "Quels sont les effets secondaires?" --language fr
```

### Query Processing Flow

#### 1. Input Validation
- **Query Length**: Minimum 10 characters
- **Content Validation**: Text sanitization
- **Language Detection**: Automatic language detection
- **Format Validation**: Query format verification

#### 2. Context Retrieval
- **RAG Query**: Vector similarity search
- **Context Ranking**: Relevance scoring
- **Source Attribution**: Document references
- **Context Validation**: Quality verification

#### 3. Response Generation
- **Generator Agent**: Initial response creation
- **Verifier Agent**: Quality assessment
- **Consensus Decision**: Approval/rejection
- **Reform Cycle**: Response improvement (if needed)

#### 4. Human Validation (Optional)
- **Human-in-the-Loop**: Manual validation
- **Approval Process**: Accept/reject/modify
- **Feedback Integration**: Improvement suggestions
- **Audit Trail**: Complete validation history

#### 5. Translation (Optional)
- **Language Detection**: Source language identification
- **Translation**: Target language conversion
- **Terminology Preservation**: Medical term accuracy
- **Quality Validation**: Translation verification

### Query Options

#### Human-in-the-Loop
```bash
# Enable human validation
mirage query "What are the side effects?" --human

# Human validation with timeout
mirage query "What are the contraindications?" --human --timeout 300
```

#### Verbose Mode
```bash
# Detailed output
mirage query "What is the mechanism of action?" --verbose

# Include processing details
mirage query "What are the drug interactions?" --verbose --format json
```

#### Benchmark Mode
```bash
# Performance benchmarking
mirage query "What are the side effects?" --benchmark

# Detailed performance metrics
mirage query "What are the contraindications?" --benchmark --verbose
```

## Monitoring & Alerts

### System Monitoring

#### Real-time Metrics
- **CPU Usage**: Processor utilization
- **Memory Usage**: RAM consumption
- **Disk Usage**: Storage utilization
- **Network Activity**: Network I/O

#### Application Metrics
- **Query Performance**: Processing times
- **Agent Statistics**: Agent performance
- **RAG Metrics**: Document processing
- **Error Rates**: Failure statistics

### Alert System

#### Alert Types
- **Performance Alerts**: Threshold violations
- **Error Alerts**: System errors
- **Health Alerts**: Component failures
- **Custom Alerts**: Business-specific alerts

#### Alert Severity
- **Info**: Informational messages
- **Warning**: Attention required
- **Critical**: Immediate action needed

#### Alert Management
```bash
# View active alerts
mirage monitor --alerts

# Acknowledge alert
mirage monitor --acknowledge alert_id

# View alert history
mirage monitor --alert-history
```

### Performance Monitoring

#### Key Metrics
- **Response Time**: Query processing time
- **Throughput**: Queries per minute
- **Success Rate**: Successful query percentage
- **Error Rate**: Failed query percentage

#### Performance Thresholds
- **Response Time**: < 5 seconds
- **Success Rate**: > 95%
- **Error Rate**: < 5%
- **CPU Usage**: < 80%

## Troubleshooting

### Common Issues

#### Installation Problems
```bash
# Check Python version
python --version

# Verify virtual environment
which python

# Check dependencies
pip list
```

#### Configuration Issues
```bash
# Validate configuration
mirage config --validate

# Check environment variables
env | grep MIRAGE

# Test API key
mirage health
```

#### Performance Issues
```bash
# Check system resources
mirage monitor --metrics

# View performance logs
mirage monitor --logs

# Clear cache
mirage config --clear-cache
```

#### Query Issues
```bash
# Test simple query
mirage query "test query"

# Check RAG system
mirage rag --stats

# Verify documents
mirage rag --list
```

### Error Messages

#### API Key Errors
```
Error: GEMINI_API_KEY not found
Solution: Set GEMINI_API_KEY environment variable
```

#### Configuration Errors
```
Error: Invalid configuration
Solution: Run 'mirage config --validate'
```

#### Performance Errors
```
Error: High memory usage
Solution: Check system resources and clear cache
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
mirage query "test" --verbose

# Check debug logs
mirage monitor --logs
```

### Support Resources
- **Documentation**: Complete system documentation
- **Logs**: Detailed system logs
- **Metrics**: Performance metrics
- **Community**: User community support

## Best Practices

### System Configuration

#### Performance Optimization
- **Memory**: Allocate sufficient RAM (4GB+)
- **Storage**: Use SSD for better performance
- **Network**: Ensure stable internet connection
- **CPU**: Multi-core processor recommended

#### Security Best Practices
- **API Keys**: Store securely, rotate regularly
- **Access Control**: Limit system access
- **Data Protection**: Encrypt sensitive data
- **Audit Logging**: Enable comprehensive logging

### Query Optimization

#### Effective Queries
- **Specific Questions**: Be precise and specific
- **Context**: Provide relevant context
- **Language**: Use appropriate language
- **Length**: Keep queries concise but complete

#### Query Examples
```bash
# Good: Specific and clear
mirage query "What are the common side effects of metformin?"

# Good: Contextual
mirage query "What are the contraindications for patients with diabetes?"

# Avoid: Too vague
mirage query "Tell me about drugs"
```

### Document Management

#### Document Preparation
- **Quality**: Use high-quality documents
- **Format**: Ensure proper formatting
- **Content**: Verify document content
- **Metadata**: Include relevant metadata

#### Document Organization
- **Naming**: Use descriptive filenames
- **Categorization**: Organize by type/topic
- **Versioning**: Track document versions
- **Backup**: Regular backups

### Monitoring Best Practices

#### Regular Monitoring
- **Daily Checks**: System health and performance
- **Weekly Reviews**: Performance trends
- **Monthly Analysis**: Comprehensive system analysis
- **Alert Response**: Prompt alert handling

#### Performance Optimization
- **Cache Management**: Regular cache cleanup
- **Resource Monitoring**: Track resource usage
- **Performance Tuning**: Optimize based on metrics
- **Capacity Planning**: Plan for growth

### Maintenance

#### Regular Maintenance
- **Updates**: Keep system updated
- **Backups**: Regular data backups
- **Logs**: Monitor and rotate logs
- **Performance**: Regular performance reviews

#### System Health
- **Health Checks**: Regular system health checks
- **Error Monitoring**: Monitor error rates
- **Performance Metrics**: Track key metrics
- **Alert Management**: Manage alert thresholds

## Conclusion

MIRAGE v2 provides a comprehensive solution for pharmaceutical R&D with powerful AI capabilities. This user guide covers all aspects of system usage, from basic operations to advanced features.

For additional support or questions, refer to the system documentation or contact the support team.
