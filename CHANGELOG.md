# Changelog

All notable changes to MIRAGE v2 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.1] - 2025-09-15

### 🎯 Phase 1 Multi-Agents - FINALISATION COMPLÈTE

#### Multi-Agent System Integration
- **COMPLETED**: Full integration of all 4 agents (Generator, Verifier, Reformer, Translator) in main workflow
- **COMPLETED**: Complete orchestration with MultiAgentOrchestrator
- **COMPLETED**: Intelligent consensus management with voting system (OUI/NON)
- **COMPLETED**: Workflow Generator → Verifier → [Reformer] → [Translator] → Final Response
- **COMPLETED**: Performance optimization with cache system and retry logic
- **COMPLETED**: Health monitoring for all agents and system components

#### Consensus & Workflow Management
- **NEW**: Intelligent voting system with confidence-based decision making
- **NEW**: Automatic reformulation when responses are rejected (confidence < 0.3)
- **NEW**: Iteration management with maximum 3 iterations per query
- **NEW**: Cache system with TTL (3600s) for responses and context
- **NEW**: Retry logic with exponential backoff for robust operation

### 🗣️ Language Intelligence & Formatting

#### Multi-Language Detection System
- **NEW**: Automatic language detection for EN, FR, ES, DE with intelligent keyword analysis
- **NEW**: Language-consistent responses (French questions → French answers)
- **NEW**: Strategic English priority for international pharmaceutical research
- **NEW**: Medical terminology support in all detected languages
- **FIXED**: UK detection now correctly responds in English (not Spanish)

#### Enhanced Response Formatting
- **NEW**: Optimized bullet point formatting with proper line breaks
- **NEW**: Visual hierarchy with emojis and clear section organization
- **NEW**: Professional medical-grade structure for research contexts
- **NEW**: Critical formatting instructions for AI agents
- **IMPROVED**: Each bullet point on separate lines with appropriate spacing

#### System Architecture Improvements
- **NEW**: Shared prompt instance system for synchronized agent prompts
- **NEW**: Enhanced error handling for favicon and connection management
- **NEW**: Real-time statistics with adaptive polling intervals
- **IMPROVED**: Intelligent response caching with TTL management
- **IMPROVED**: Robust console error handling and connection status

### 🔧 Technical Enhancements

#### Agent Prompt System
- **NEW**: `detect_language()` function with medical terminology keywords
- **NEW**: Language-specific formatting instructions in prompts
- **NEW**: Shared `AgentPrompts` instance to prevent stale prompt usage
- **IMPROVED**: Explicit formatting requirements in user prompts
- **IMPROVED**: Critical instructions for bullet point separation

#### Web Interface Optimizations
- **NEW**: Favicon route to prevent 404 errors
- **NEW**: Intelligent polling with connection retry logic
- **NEW**: Connection status indicators in frontend
- **IMPROVED**: Error handling for server disconnections
- **IMPROVED**: Adaptive polling intervals (30s online, 60s offline)

## [2.1.0] - 2025-09-14

### 🚀 Major Improvements

#### Architecture Simplification
- **BREAKING**: Removed `HybridService` completely to eliminate service conflicts
- **BREAKING**: Migrated from ChromaDB to Qdrant for better macOS compatibility
- **NEW**: Direct Gemini API integration without intermediate service layers
- **IMPROVED**: Streamlined orchestrator with direct API access

#### Web Interface Enhancements
- **NEW**: Sequential response display - multiple query/response pairs without page reload
- **NEW**: Clear History functionality with conversation reset
- **IMPROVED**: Enhanced user experience with conversation-style interface
- **IMPROVED**: Better source attribution and metadata display

#### Multi-Agent System Optimization
- **IMPROVED**: Enhanced consensus mechanism with explicit voting (OUI/NON)
- **IMPROVED**: Better response verification and reform processes
- **IMPROVED**: Optimized workflow with reduced latency
- **IMPROVED**: More accurate confidence scoring (66-88% typical)

### 🔧 Technical Changes

#### Removed Components
- `HybridService` class and all related code
- ChromaDB integration (replaced with Qdrant)
- Complex service abstraction layers
- Redundant API wrapper functions

#### Added Components
- Direct Gemini API integration in orchestrator
- Sequential web interface JavaScript logic
- Enhanced conversation management
- Improved error handling and logging

#### Modified Components
- `MultiAgentOrchestrator`: Direct Gemini integration
- `web_interface.py`: Sequential display and conversation management
- All agent classes: Updated to use `gemini-1.5-flash` model
- API endpoints: Enhanced response formatting

### 🐛 Bug Fixes

- **FIXED**: Qdrant access conflicts resolved
- **FIXED**: macOS ChromaDB segmentation faults eliminated
- **FIXED**: Service initialization race conditions
- **FIXED**: Memory leaks in hybrid service layer
- **FIXED**: Port binding conflicts on system restart

### 📊 Performance Improvements

- **IMPROVED**: Reduced response time variability
- **IMPROVED**: Better memory management
- **IMPROVED**: More stable system operation
- **IMPROVED**: Enhanced error recovery mechanisms

### 🔒 Security & Stability

- **IMPROVED**: Simplified attack surface with fewer service layers
- **IMPROVED**: Better error isolation and handling
- **IMPROVED**: Enhanced logging and monitoring
- **IMPROVED**: More predictable system behavior

### 📚 Documentation Updates

- **UPDATED**: README.md with new installation and usage instructions
- **UPDATED**: Architecture diagrams reflecting new structure
- **UPDATED**: Performance benchmarks with current metrics
- **UPDATED**: Configuration examples with new environment variables

### 🧪 Testing & Validation

- **VERIFIED**: All multi-agent workflows functional
- **VERIFIED**: Web interface sequential display working
- **VERIFIED**: API endpoints responding correctly
- **VERIFIED**: Document management operations stable
- **VERIFIED**: No regressions in core functionality

## [2.0.0] - 2025-09-13

### 🚀 Initial Release

#### Core Features
- Multi-agent system with Generator, Verifier, Reformer, and Translator agents
- RAG integration with document processing and vector storage
- Human-in-the-loop validation system
- Web-based monitoring dashboard
- REST API with comprehensive endpoints
- CLI interface for system management

#### Architecture
- Orchestrator-based workflow management
- ChromaDB vector storage (later replaced with Qdrant)
- Hybrid service layer for API management (later removed)
- Comprehensive logging and monitoring
- 8-pillar methodology implementation

#### Security & Compliance
- API key management
- Input validation and sanitization
- Audit trails and compliance logging
- Enterprise-grade security measures

---

## Migration Guide

### From v2.0 to v2.1

#### Breaking Changes
1. **HybridService Removal**: All code referencing `HybridService` must be updated
2. **ChromaDB to Qdrant**: Update vector database configuration
3. **Direct API Integration**: Update orchestrator initialization code

#### Required Updates
1. Update environment variables:
   ```bash
   # Remove
   CHROMA_DB_PATH=./data/embeddings
   
   # Add
   QDRANT_DB_PATH=./data/qdrant_db
   ```

2. Update import statements:
   ```python
   # Remove
   from hybrid_service import HybridService
   
   # Update orchestrator usage
   from src.orchestrator.multi_agent_orchestrator import MultiAgentOrchestrator
   ```

3. Update web interface usage:
   - Sequential display is now default behavior
   - Clear History functionality available
   - Enhanced conversation management

#### Compatibility
- All existing document data is compatible
- API endpoints remain the same
- Configuration files need minor updates
- No data migration required

---

## Support

For migration assistance or questions about these changes, please refer to:
- Updated README.md documentation
- System health checks via web interface
- API endpoint testing
- Backup and restore procedures
