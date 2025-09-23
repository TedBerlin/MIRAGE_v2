# MIRAGE v2 - Developer Guide RÉVOLUTIONNAIRE

## Table of Contents
1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Code Standards](#code-standards)
4. [Testing Guidelines](#testing-guidelines)
5. [🧠 RAG Avancé Development](#rag-avancé-development)
6. [🛡️ HITL Prioritaire Development](#hitl-prioritaire-development)
7. [🌍 Multilingue Development](#multilingue-development)
8. [API Enhanced Development](#api-enhanced-development)
9. [Agent Development](#agent-development)
10. [Monitoring Development](#monitoring-development)
11. [Deployment Development](#deployment-development)
12. [Contributing Guidelines](#contributing-guidelines)

## Development Setup

### 🌟 RÉVOLUTION MIRAGE v2 - DÉVELOPPEMENT
MIRAGE v2 révolutionne le développement avec **RAG AVANCÉ**, **HITL PRIORITAIRE**, et **4 LANGUES MÉDICALES**.

### Prerequisites
- Python 3.9+
- Git
- Docker (optional)
- IDE with Python support (VS Code, PyCharm, etc.)
- **API Enhanced** (port 8006)
- **RAG Avancé** capabilities
- **HITL Prioritaire** system

### Development Environment Setup

#### 1. Clone Repository
```bash
git clone <repository-url>
cd MIRAGE_v2
```

#### 2. Create Development Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

#### 3. Install Development Tools
```bash
# Install pre-commit hooks
pre-commit install

# Install development dependencies
pip install -r requirements-dev.txt
```

#### 4. Configure Development Environment
```bash
# Copy environment template
cp .env.template .env

# Set development configuration
export LOG_LEVEL=DEBUG
export ENVIRONMENT=development
export GEMINI_API_KEY=your_test_key
```

### Development Tools

#### Code Quality Tools
```bash
# Code formatting
black src/ tests/

# Linting
flake8 src/ tests/

# Type checking
mypy src/

# Security scanning
bandit -r src/
```

#### Testing Tools
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m security
pytest -m performance
```

#### Documentation Tools
```bash
# Generate API documentation
sphinx-build -b html docs/ docs/_build/

# Check documentation
doc8 docs/
```

## Project Structure

### Directory Layout
```
MIRAGE_v2/
├── src/                    # Source code
│   ├── agents/            # AI agents
│   ├── api/               # API endpoints
│   ├── cli/               # Command-line interface
│   ├── core/              # Core utilities
│   ├── monitoring/        # Monitoring system
│   ├── orchestrator/      # Orchestration logic
│   ├── rag/               # RAG system
│   └── utils/             # Utility functions
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   ├── security/          # Security tests
│   └── performance/       # Performance tests
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── data/                  # Data files
├── config/                # Configuration files
├── logs/                  # Log files
└── pyproject.toml         # Project configuration
```

### Module Organization

#### Core Modules
- **`src/core/`**: Core utilities and base classes
- **`src/utils/`**: Common utility functions
- **`src/models/`**: Data models and schemas

#### Feature Modules
- **`src/agents/`**: AI agent implementations
- **`src/rag/`**: RAG system components
- **`src/orchestrator/`**: Orchestration logic
- **`src/monitoring/`**: Monitoring and alerting

#### Interface Modules
- **`src/api/`**: REST API endpoints
- **`src/cli/`**: Command-line interface
- **`src/dashboard/`**: Web dashboard

## Code Standards

### Python Style Guide

#### PEP 8 Compliance
- **Line Length**: Maximum 88 characters (Black default)
- **Indentation**: 4 spaces
- **Imports**: Grouped and sorted
- **Naming**: snake_case for variables, PascalCase for classes

#### Code Formatting
```python
# Use Black for formatting
black src/ tests/

# Example formatted code
class ExampleClass:
    """Example class with proper formatting."""
    
    def __init__(self, param1: str, param2: int = 10):
        """Initialize with parameters.
        
        Args:
            param1: First parameter
            param2: Second parameter with default
        """
        self.param1 = param1
        self.param2 = param2
    
    def example_method(self, value: str) -> str:
        """Example method with type hints.
        
        Args:
            value: Input value
            
        Returns:
            Processed value
            
        Raises:
            ValueError: If value is invalid
        """
        if not value:
            raise ValueError("Value cannot be empty")
        
        return value.upper()
```

#### Type Hints
```python
from typing import Dict, List, Optional, Union
from datetime import datetime

def process_data(
    data: List[Dict[str, Union[str, int]]],
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """Process data with type hints."""
    # Implementation
    pass
```

#### Docstrings
```python
def complex_function(
    param1: str,
    param2: int,
    param3: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Complex function with comprehensive docstring.
    
    This function performs complex operations on the input parameters
    and returns a structured result.
    
    Args:
        param1: Primary input parameter
        param2: Secondary numeric parameter
        param3: Optional list of strings
        
    Returns:
        Dictionary containing:
            - result: The processed result
            - metadata: Additional information
            - timestamp: Processing timestamp
            
    Raises:
        ValueError: If param1 is empty
        TypeError: If param2 is not an integer
        
    Example:
        >>> result = complex_function("test", 42, ["a", "b"])
        >>> print(result["result"])
        "processed_test"
    """
    # Implementation
    pass
```

### Error Handling

#### Exception Handling
```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def robust_function(data: str) -> Optional[str]:
    """Function with proper error handling."""
    try:
        # Main logic
        result = process_data(data)
        return result
        
    except ValueError as e:
        logger.error("Invalid data provided", extra={"data": data, "error": str(e)})
        return None
        
    except Exception as e:
        logger.exception("Unexpected error in robust_function")
        raise
```

#### Custom Exceptions
```python
class MIRAGEError(Exception):
    """Base exception for MIRAGE system."""
    pass

class ConfigurationError(MIRAGEError):
    """Configuration-related errors."""
    pass

class APIError(MIRAGEError):
    """API-related errors."""
    pass

class ValidationError(MIRAGEError):
    """Validation-related errors."""
    pass
```

### Logging Standards

#### Structured Logging
```python
import structlog

logger = structlog.get_logger(__name__)

def example_function(user_id: str, action: str):
    """Function with structured logging."""
    logger.info(
        "User action started",
        user_id=user_id,
        action=action,
        timestamp=datetime.now().isoformat()
    )
    
    try:
        # Process action
        result = process_action(action)
        
        logger.info(
            "User action completed",
            user_id=user_id,
            action=action,
            result=result,
            duration=time.time() - start_time
        )
        
    except Exception as e:
        logger.error(
            "User action failed",
            user_id=user_id,
            action=action,
            error=str(e),
            duration=time.time() - start_time
        )
        raise
```

## Testing Guidelines

### Test Structure

#### Test Organization
```
tests/
├── unit/                  # Unit tests
│   ├── test_agents.py    # Agent unit tests
│   ├── test_rag.py       # RAG unit tests
│   └── test_orchestrator.py # Orchestrator tests
├── integration/          # Integration tests
│   ├── test_end_to_end.py # End-to-end tests
│   └── test_api.py       # API integration tests
├── security/             # Security tests
│   └── test_security.py  # Security test cases
└── performance/          # Performance tests
    └── test_performance.py # Performance benchmarks
```

#### Test Naming Convention
```python
# Test class naming
class TestAgentFunctionality:
    """Test agent functionality."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        pass
    
    def test_agent_response_generation(self):
        """Test agent response generation."""
        pass
    
    def test_agent_error_handling(self):
        """Test agent error handling."""
        pass
```

### Unit Testing

#### Test Structure
```python
import pytest
from unittest.mock import Mock, patch
from src.agents.generator_agent import GeneratorAgent

class TestGeneratorAgent:
    """Test GeneratorAgent functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.agent = GeneratorAgent(self.api_key)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        # Cleanup code
        pass
    
    @patch('src.agents.generator_agent.genai')
    def test_generate_response_success(self, mock_genai):
        """Test successful response generation."""
        # Arrange
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Test response"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Act
        result = self.agent.generate_response("test query", "test context")
        
        # Assert
        assert result["success"] is True
        assert result["response"] == "Test response"
        mock_genai.GenerativeModel.assert_called_once()
    
    def test_generate_response_invalid_input(self):
        """Test response generation with invalid input."""
        # Act & Assert
        with pytest.raises(ValueError):
            self.agent.generate_response("", "context")
```

#### Mocking Guidelines
```python
# Mock external dependencies
@patch('src.agents.generator_agent.genai')
def test_with_mock(self, mock_genai):
    """Test with mocked external dependency."""
    # Setup mock
    mock_genai.GenerativeModel.return_value = Mock()
    
    # Test code
    result = self.agent.generate_response("query", "context")
    
    # Verify mock usage
    mock_genai.GenerativeModel.assert_called_once()
```

### Integration Testing

#### End-to-End Tests
```python
import pytest
from src.orchestrator.orchestrator import Orchestrator

class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.orchestrator = Orchestrator(api_key=self.api_key)
    
    @patch('src.orchestrator.orchestrator.RAGEngine')
    @patch('src.orchestrator.orchestrator.GeneratorAgent')
    @patch('src.orchestrator.orchestrator.VerifierAgent')
    def test_complete_query_processing(self, mock_verifier, mock_generator, mock_rag):
        """Test complete query processing workflow."""
        # Setup mocks
        mock_rag.return_value.query_rag.return_value = {
            "success": True,
            "context": "Test context",
            "sources": ["test.pdf"]
        }
        
        # Test complete workflow
        result = self.orchestrator.process_query("test query")
        
        # Verify result
        assert result["success"] is True
        assert "answer" in result
```

### Performance Testing

#### Performance Benchmarks
```python
import pytest
import time
from src.orchestrator.orchestrator import Orchestrator

class TestPerformance:
    """Test system performance."""
    
    def test_query_processing_performance(self):
        """Test query processing performance."""
        orchestrator = Orchestrator(api_key="test_key")
        
        # Measure performance
        start_time = time.time()
        result = orchestrator.process_query("test query")
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Assert performance requirements
        assert processing_time < 5.0  # Should complete within 5 seconds
        assert result["success"] is True
```

### Security Testing

#### Security Test Cases
```python
import pytest
from src.orchestrator.orchestrator import Orchestrator

class TestSecurity:
    """Test security measures."""
    
    def test_api_key_not_exposed_in_logs(self):
        """Test that API keys are not exposed in logs."""
        api_key = "sensitive_api_key_12345"
        
        with patch('src.orchestrator.orchestrator.structlog') as mock_logger:
            orchestrator = Orchestrator(api_key=api_key)
            
            # Verify API key is not in logs
            for call in mock_logger.get_logger.return_value.info.call_args_list:
                if call[0] and api_key in str(call[0]):
                    pytest.fail("API key found in log message")
    
    def test_input_validation(self):
        """Test input validation."""
        orchestrator = Orchestrator(api_key="test_key")
        
        # Test with malicious input
        malicious_query = "test <script>alert('xss')</script>"
        result = orchestrator.process_query(malicious_query)
        
        # Verify sanitization
        assert "<script>" not in result.get("answer", "")
```

## API Development

### REST API Development

#### Endpoint Structure
```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="MIRAGE v2 API", version="1.0.0")

class QueryRequest(BaseModel):
    """Query request model."""
    query: str
    enable_human_loop: bool = False
    target_language: str = "en"

class QueryResponse(BaseModel):
    """Query response model."""
    success: bool
    answer: str
    sources: List[str]
    processing_time: float
    iteration: int
    consensus: str

@app.post("/api/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Process a query through the MIRAGE system."""
    try:
        result = orchestrator.process_query(
            query=request.query,
            enable_human_loop=request.enable_human_loop,
            target_language=request.target_language
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### Error Handling
```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid input", "detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.exception("Unhandled exception in API")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
```

### WebSocket API Development

#### WebSocket Endpoint
```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    
    try:
        while True:
            # Send real-time updates
            await send_realtime_update(websocket)
            await asyncio.sleep(5)  # Update every 5 seconds
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error("WebSocket error", error=str(e))
```

## Agent Development

### Agent Base Class

#### Base Agent Structure
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)

class BaseAgent(ABC):
    """Base class for all MIRAGE agents."""
    
    def __init__(self, api_key: str, agent_name: str):
        """Initialize base agent.
        
        Args:
            api_key: API key for external services
            agent_name: Name of the agent
        """
        self.api_key = api_key
        self.agent_name = agent_name
        self.logger = logger.bind(agent=agent_name)
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data.
        
        Args:
            input_data: Input data for processing
            
        Returns:
            Processing result
        """
        pass
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information.
        
        Returns:
            Agent information dictionary
        """
        return {
            "name": self.agent_name,
            "type": self.__class__.__name__,
            "api_key_configured": bool(self.api_key)
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation
        if not input_data:
            return False
        
        # Agent-specific validation
        return self._validate_agent_input(input_data)
    
    @abstractmethod
    def _validate_agent_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate agent-specific input.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
```

### Custom Agent Development

#### Implementing a Custom Agent
```python
from src.agents.base_agent import BaseAgent
from typing import Dict, Any

class CustomAgent(BaseAgent):
    """Custom agent implementation."""
    
    def __init__(self, api_key: str):
        """Initialize custom agent."""
        super().__init__(api_key, "CustomAgent")
        # Custom initialization
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data.
        
        Args:
            input_data: Input data containing:
                - query: User query
                - context: RAG context
                - additional_data: Any additional data
                
        Returns:
            Processing result containing:
                - success: Boolean success indicator
                - result: Processing result
                - metadata: Additional metadata
        """
        try:
            # Validate input
            if not self.validate_input(input_data):
                return {
                    "success": False,
                    "error": "Invalid input data"
                }
            
            # Process data
            result = self._process_custom_logic(input_data)
            
            return {
                "success": True,
                "result": result,
                "metadata": {
                    "agent": self.agent_name,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error("Error in custom agent", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def _validate_agent_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate custom agent input."""
        required_fields = ["query", "context"]
        return all(field in input_data for field in required_fields)
    
    def _process_custom_logic(self, input_data: Dict[str, Any]) -> Any:
        """Implement custom processing logic."""
        # Custom implementation
        pass
```

## 🧠 RAG Avancé Development

### 🌟 RÉVOLUTION RAG - DÉVELOPPEMENT
MIRAGE v2 révolutionne le RAG avec **UPLOAD TRANSPARENT**, **INDEXATION IMMÉDIATE**, et **RECHERCHE INTELLIGENTE**.

### RAG Component Development RÉVOLUTIONNAIRE

#### Document Processor
```python
from src.rag.base_processor import BaseDocumentProcessor
from typing import Dict, Any, List

class CustomDocumentProcessor(BaseDocumentProcessor):
    """Custom document processor."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize custom processor."""
        super().__init__(config)
        self.custom_config = config.get("custom", {})
    
    def process_document(self, document_path: str) -> Dict[str, Any]:
        """Process a document.
        
        Args:
            document_path: Path to the document
            
        Returns:
            Processing result
        """
        try:
            # Load document
            document = self._load_document(document_path)
            
            # Process document
            processed_document = self._process_document_content(document)
            
            # Generate metadata
            metadata = self._generate_metadata(processed_document)
            
            return {
                "success": True,
                "document": processed_document,
                "metadata": metadata
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _load_document(self, document_path: str) -> Any:
        """Load document from path."""
        # Custom document loading logic
        pass
    
    def _process_document_content(self, document: Any) -> Any:
        """Process document content."""
        # Custom content processing logic
        pass
    
    def _generate_metadata(self, document: Any) -> Dict[str, Any]:
        """Generate document metadata."""
        # Custom metadata generation logic
        pass
```

### Embedding System Development

#### Custom Embedding Manager
```python
from src.rag.base_embedding import BaseEmbeddingManager
from typing import List, Dict, Any

class CustomEmbeddingManager(BaseEmbeddingManager):
    """Custom embedding manager."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize custom embedding manager."""
        super().__init__(config)
        self.embedding_model = self._load_embedding_model()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = []
            for text in texts:
                embedding = self._generate_single_embedding(text)
                embeddings.append(embedding)
            
            return embeddings
            
        except Exception as e:
            self.logger.error("Error generating embeddings", error=str(e))
            raise
    
    def _load_embedding_model(self):
        """Load embedding model."""
        # Custom model loading logic
        pass
    
    def _generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        # Custom embedding generation logic
        pass
```

## Monitoring Development

### Custom Metrics Development

#### Custom Metrics Collector
```python
from src.monitoring.base_metrics import BaseMetricsCollector
from typing import Dict, Any

class CustomMetricsCollector(BaseMetricsCollector):
    """Custom metrics collector."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize custom metrics collector."""
        super().__init__(config)
        self.custom_metrics = {}
    
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect custom metrics.
        
        Returns:
            Dictionary of collected metrics
        """
        try:
            metrics = {}
            
            # Collect system metrics
            metrics["system"] = self._collect_system_metrics()
            
            # Collect application metrics
            metrics["application"] = self._collect_application_metrics()
            
            # Collect custom metrics
            metrics["custom"] = self._collect_custom_metrics()
            
            return metrics
            
        except Exception as e:
            self.logger.error("Error collecting metrics", error=str(e))
            return {"error": str(e)}
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics."""
        # Custom system metrics collection
        pass
    
    def _collect_application_metrics(self) -> Dict[str, Any]:
        """Collect application metrics."""
        # Custom application metrics collection
        pass
    
    def _collect_custom_metrics(self) -> Dict[str, Any]:
        """Collect custom metrics."""
        # Custom metrics collection logic
        pass
```

### Custom Alert Development

#### Custom Alert Manager
```python
from src.monitoring.base_alerts import BaseAlertManager
from typing import Dict, Any, List

class CustomAlertManager(BaseAlertManager):
    """Custom alert manager."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize custom alert manager."""
        super().__init__(config)
        self.custom_rules = config.get("custom_rules", {})
    
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for alerts based on metrics.
        
        Args:
            metrics: Current system metrics
            
        Returns:
            List of triggered alerts
        """
        alerts = []
        
        try:
            # Check standard alerts
            standard_alerts = self._check_standard_alerts(metrics)
            alerts.extend(standard_alerts)
            
            # Check custom alerts
            custom_alerts = self._check_custom_alerts(metrics)
            alerts.extend(custom_alerts)
            
            return alerts
            
        except Exception as e:
            self.logger.error("Error checking alerts", error=str(e))
            return []
    
    def _check_standard_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check standard alert rules."""
        # Standard alert checking logic
        pass
    
    def _check_custom_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check custom alert rules."""
        # Custom alert checking logic
        pass
```

## Deployment Development

### Docker Development

#### Dockerfile Development
```dockerfile
# Multi-stage build for MIRAGE v2
FROM python:3.9-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy application
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY config/ ./config/

# Create non-root user
RUN useradd -m -u 1000 mirage && chown -R mirage:mirage /app
USER mirage

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python", "-m", "src.main"]
```

#### Docker Compose Development
```yaml
version: '3.8'

services:
  mirage:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - chromadb
    restart: unless-stopped

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chromadb_data:/chroma/chroma
    restart: unless-stopped

  monitoring:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped

volumes:
  chromadb_data:
```

### CI/CD Development

#### GitHub Actions Workflow
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security scan
      run: |
        pip install bandit
        bandit -r src/
    
    - name: Run dependency check
      run: |
        pip install safety
        safety check

  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t mirage:v2 .
    
    - name: Run container tests
      run: |
        docker run --rm mirage:v2 python -m pytest tests/
```

## Contributing Guidelines

### Development Workflow

#### 1. Fork and Clone
```bash
# Fork repository on GitHub
# Clone your fork
git clone https://github.com/yourusername/MIRAGE_v2.git
cd MIRAGE_v2

# Add upstream remote
git remote add upstream https://github.com/original/MIRAGE_v2.git
```

#### 2. Create Feature Branch
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes
# Test changes
# Commit changes
git add .
git commit -m "Add your feature"
```

#### 3. Submit Pull Request
```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

### Code Review Process

#### Pull Request Requirements
- **Tests**: All new code must have tests
- **Documentation**: Update documentation as needed
- **Style**: Code must pass all style checks
- **Security**: No security vulnerabilities
- **Performance**: No performance regressions

#### Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are comprehensive
- [ ] Documentation is updated
- [ ] No security issues
- [ ] Performance is acceptable
- [ ] Error handling is proper
- [ ] Logging is appropriate

### Development Best Practices

#### Code Quality
- **Write tests first**: TDD approach
- **Keep functions small**: Single responsibility
- **Use type hints**: Better code documentation
- **Handle errors gracefully**: Proper exception handling
- **Log appropriately**: Structured logging

#### Performance
- **Profile code**: Identify bottlenecks
- **Optimize algorithms**: Efficient implementations
- **Use caching**: Reduce redundant operations
- **Monitor resources**: Track usage

#### Security
- **Validate inputs**: Sanitize all inputs
- **Protect secrets**: Never commit API keys
- **Use HTTPS**: Secure communications
- **Audit dependencies**: Regular security updates

## Conclusion

This developer guide provides comprehensive information for developing with MIRAGE v2. Follow these guidelines to ensure code quality, maintainability, and security.

For additional support or questions, refer to the system documentation or contact the development team.
