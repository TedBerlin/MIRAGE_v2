#!/usr/bin/env python3
"""
MIRAGE v2 - Web API for User Interface

FastAPI endpoints for the web dashboard and user interface.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

import structlog

# Import MIRAGE components
from orchestrator.orchestrator import Orchestrator
from rag.rag_engine import RAGEngine
from monitoring.metrics import MetricsCollector

logger = structlog.get_logger(__name__)

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    enable_human_loop: bool = False
    verbose: bool = False

class QueryResponse(BaseModel):
    query_id: str
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    processing_time: float
    human_validation_required: bool = False
    timestamp: datetime

class DocumentInfo(BaseModel):
    filename: str
    size: int
    upload_date: datetime
    processed: bool
    chunks_count: int
    metadata: Dict[str, Any]

class SystemStats(BaseModel):
    total_documents: int
    total_queries: int
    average_response_time: float
    success_rate: float
    system_health: str
    uptime: str

class MIRAGEWebAPI:
    """Web API for MIRAGE v2 user interface."""
    
    def __init__(self, api_key: str):
        """Initialize the web API."""
        self.app = FastAPI(
            title="MIRAGE v2 API",
            description="AI-powered pharmaceutical research assistant",
            version="2.0.0"
        )
        
        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize components
        self.orchestrator = Orchestrator(api_key=api_key)
        self.rag_engine = RAGEngine()
        self.metrics_collector = MetricsCollector()
        
        # WebSocket connections
        self.active_connections: List[WebSocket] = []
        
        # Setup routes
        self._setup_routes()
        
        logger.info("MIRAGE v2 Web API initialized")
    
    def _setup_routes(self):
        """Setup API routes."""
        
        # Static files
        self.app.mount("/static", StaticFiles(directory="static"), name="static")
        
        # Root endpoint
        @self.app.get("/", response_class=HTMLResponse)
        async def root():
            """Serve the main dashboard."""
            return HTMLResponse(content=self._get_dashboard_html(), status_code=200)
        
        # Health check
        @self.app.get("/health")
        async def health():
            """Health check endpoint."""
            try:
                stats = self.orchestrator.get_system_stats()
                return {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "version": "2.0.0",
                    "components": {
                        "orchestrator": "healthy",
                        "rag_engine": "healthy",
                        "metrics": "healthy"
                    }
                }
            except Exception as e:
                logger.error("Health check failed", error=str(e))
                raise HTTPException(status_code=500, detail="System unhealthy")
        
        # Query endpoint
        @self.app.post("/api/query", response_model=QueryResponse)
        async def query_documents(request: QueryRequest):
            """Process a query using MIRAGE v2."""
            try:
                start_time = datetime.now()
                
                # Process query through orchestrator
                result = self.orchestrator.process_query(
                    query=request.query,
                    enable_human_loop=request.enable_human_loop
                )
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                # Collect metrics
                self.metrics_collector.record_query(
                    query_id=result.get("query_id", "unknown"),
                    processing_time=processing_time,
                    success=result.get("success", False)
                )
                
                # Broadcast to WebSocket connections
                await self._broadcast_query_result(result)
                
                return QueryResponse(
                    query_id=result.get("query_id", "unknown"),
                    answer=result.get("answer", "No answer generated"),
                    sources=result.get("sources", []),
                    confidence=result.get("confidence", 0.0),
                    processing_time=processing_time,
                    human_validation_required=result.get("human_validation_required", False),
                    timestamp=datetime.now()
                )
                
            except Exception as e:
                logger.error("Query processing failed", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        # Document management
        @self.app.post("/api/documents/upload")
        async def upload_document(file: UploadFile = File(...)):
            """Upload a document for processing."""
            try:
                # Save uploaded file
                upload_dir = Path("data/raw_documents")
                upload_dir.mkdir(parents=True, exist_ok=True)
                
                file_path = upload_dir / file.filename
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                
                # Process document through RAG engine
                result = self.rag_engine.ingest_document(str(file_path))
                
                # Broadcast document update
                await self._broadcast_document_update({
                    "action": "document_uploaded",
                    "filename": file.filename,
                    "size": len(content),
                    "processed": result.get("success", False)
                })
                
                return {
                    "success": True,
                    "filename": file.filename,
                    "size": len(content),
                    "processed": result.get("success", False),
                    "chunks": result.get("chunks_count", 0)
                }
                
            except Exception as e:
                logger.error("Document upload failed", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/documents", response_model=List[DocumentInfo])
        async def list_documents():
            """List all uploaded documents."""
            try:
                documents = []
                docs_dir = Path("data/raw_documents")
                
                if docs_dir.exists():
                    for file_path in docs_dir.iterdir():
                        if file_path.is_file():
                            stat = file_path.stat()
                            documents.append(DocumentInfo(
                                filename=file_path.name,
                                size=stat.st_size,
                                upload_date=datetime.fromtimestamp(stat.st_mtime),
                                processed=True,  # Assume processed if in directory
                                chunks_count=0,  # Would need to query RAG engine
                                metadata={"type": "pharmaceutical_document"}
                            ))
                
                return documents
                
            except Exception as e:
                logger.error("Failed to list documents", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.delete("/api/documents/{filename}")
        async def delete_document(filename: str):
            """Delete a document."""
            try:
                file_path = Path("data/raw_documents") / filename
                if file_path.exists():
                    file_path.unlink()
                    
                    # Broadcast document deletion
                    await self._broadcast_document_update({
                        "action": "document_deleted",
                        "filename": filename
                    })
                    
                    return {"success": True, "message": f"Document {filename} deleted"}
                else:
                    raise HTTPException(status_code=404, detail="Document not found")
                    
            except Exception as e:
                logger.error("Failed to delete document", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        # System statistics
        @self.app.get("/api/stats", response_model=SystemStats)
        async def get_system_stats():
            """Get system statistics."""
            try:
                # Get orchestrator stats
                orchestrator_stats = self.orchestrator.get_system_stats()
                
                # Get document count
                docs_dir = Path("data/raw_documents")
                total_documents = len(list(docs_dir.glob("*"))) if docs_dir.exists() else 0
                
                # Get metrics
                metrics = self.metrics_collector.get_metrics()
                
                return SystemStats(
                    total_documents=total_documents,
                    total_queries=metrics.get("total_queries", 0),
                    average_response_time=metrics.get("average_response_time", 0.0),
                    success_rate=metrics.get("success_rate", 0.0),
                    system_health="healthy",
                    uptime="24h"  # Would calculate actual uptime
                )
                
            except Exception as e:
                logger.error("Failed to get system stats", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        # WebSocket endpoint for real-time updates
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates."""
            await websocket.accept()
            self.active_connections.append(websocket)
            
            try:
                while True:
                    # Keep connection alive
                    await websocket.receive_text()
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
    
    async def _broadcast_query_result(self, result: Dict[str, Any]):
        """Broadcast query result to all WebSocket connections."""
        message = {
            "type": "query_result",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(json.dumps(message))
            except:
                self.active_connections.remove(connection)
    
    async def _broadcast_document_update(self, update: Dict[str, Any]):
        """Broadcast document update to all WebSocket connections."""
        message = {
            "type": "document_update",
            "data": update,
            "timestamp": datetime.now().isoformat()
        }
        
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(json.dumps(message))
            except:
                self.active_connections.remove(connection)
    
    def _get_dashboard_html(self) -> str:
        """Get the main dashboard HTML."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIRAGE v2 - AI Pharmaceutical Research Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }
        
        .query-section {
            grid-column: 1 / -1;
        }
        
        .query-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 1rem;
            margin-bottom: 15px;
            transition: border-color 0.3s ease;
        }
        
        .query-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .options {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .option {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .option input[type="checkbox"] {
            width: 18px;
            height: 18px;
            accent-color: #667eea;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .upload-section {
            margin-bottom: 20px;
        }
        
        .file-input {
            width: 100%;
            padding: 10px;
            border: 2px dashed #e1e5e9;
            border-radius: 10px;
            text-align: center;
            cursor: pointer;
            transition: border-color 0.3s ease;
        }
        
        .file-input:hover {
            border-color: #667eea;
        }
        
        .documents-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .document-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            border-bottom: 1px solid #e1e5e9;
        }
        
        .document-item:last-child {
            border-bottom: none;
        }
        
        .document-info {
            flex: 1;
        }
        
        .document-name {
            font-weight: 600;
            color: #333;
        }
        
        .document-size {
            font-size: 0.9rem;
            color: #666;
        }
        
        .delete-btn {
            background: #ff4757;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.8rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #666;
            margin-top: 5px;
        }
        
        .response-section {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            display: none;
        }
        
        .response-section.show {
            display: block;
        }
        
        .response-content {
            margin-bottom: 15px;
        }
        
        .response-answer {
            font-size: 1.1rem;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        
        .response-sources {
            margin-top: 15px;
        }
        
        .source-item {
            background: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #667eea;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        
        .success {
            background: #e8f5e8;
            color: #2e7d32;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        
        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .options {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧬 MIRAGE v2</h1>
            <p>AI-Powered Pharmaceutical Research Assistant</p>
        </div>
        
        <div class="dashboard">
            <!-- System Statistics -->
            <div class="card">
                <h2>📊 System Statistics</h2>
                <div class="stats-grid" id="statsGrid">
                    <div class="stat-item">
                        <div class="stat-value" id="totalDocuments">-</div>
                        <div class="stat-label">Documents</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="totalQueries">-</div>
                        <div class="stat-label">Queries</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="avgResponseTime">-</div>
                        <div class="stat-label">Avg Response (s)</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="successRate">-</div>
                        <div class="stat-label">Success Rate</div>
                    </div>
                </div>
            </div>
            
            <!-- Document Management -->
            <div class="card">
                <h2>📁 Document Management</h2>
                <div class="upload-section">
                    <input type="file" id="fileInput" class="file-input" accept=".pdf,.txt,.docx" multiple>
                    <button class="btn" onclick="uploadDocuments()" style="margin-top: 10px; width: 100%;">
                        📤 Upload Documents
                    </button>
                </div>
                <div class="documents-list" id="documentsList">
                    <div class="loading">Loading documents...</div>
                </div>
            </div>
            
            <!-- Query Interface -->
            <div class="card query-section">
                <h2>🔍 AI Query Interface</h2>
                <textarea 
                    id="queryInput" 
                    class="query-input" 
                    placeholder="Ask a question about your pharmaceutical documents..."
                    rows="3"
                ></textarea>
                
                <div class="options">
                    <div class="option">
                        <input type="checkbox" id="humanLoop">
                        <label for="humanLoop">Enable Human-in-the-Loop</label>
                    </div>
                    <div class="option">
                        <input type="checkbox" id="verboseMode">
                        <label for="verboseMode">Verbose Mode</label>
                    </div>
                </div>
                
                <button class="btn" onclick="processQuery()" id="queryBtn">
                    🚀 Process Query
                </button>
                
                <div class="response-section" id="responseSection">
                    <div class="response-content" id="responseContent"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        
        // Initialize WebSocket connection
        function initWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onmessage = function(event) {
                const message = JSON.parse(event.data);
                handleWebSocketMessage(message);
            };
            
            ws.onclose = function() {
                console.log('WebSocket connection closed');
                setTimeout(initWebSocket, 5000); // Reconnect after 5 seconds
            };
        }
        
        // Handle WebSocket messages
        function handleWebSocketMessage(message) {
            if (message.type === 'query_result') {
                displayQueryResult(message.data);
            } else if (message.type === 'document_update') {
                loadDocuments();
                loadStats();
            }
        }
        
        // Load system statistics
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('totalDocuments').textContent = stats.total_documents;
                document.getElementById('totalQueries').textContent = stats.total_queries;
                document.getElementById('avgResponseTime').textContent = stats.average_response_time.toFixed(2);
                document.getElementById('successRate').textContent = (stats.success_rate * 100).toFixed(1) + '%';
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        }
        
        // Load documents
        async function loadDocuments() {
            try {
                const response = await fetch('/api/documents');
                const documents = await response.json();
                
                const documentsList = document.getElementById('documentsList');
                
                if (documents.length === 0) {
                    documentsList.innerHTML = '<div class="loading">No documents uploaded yet</div>';
                    return;
                }
                
                documentsList.innerHTML = documents.map(doc => `
                    <div class="document-item">
                        <div class="document-info">
                            <div class="document-name">${doc.filename}</div>
                            <div class="document-size">${formatFileSize(doc.size)} • ${new Date(doc.upload_date).toLocaleDateString()}</div>
                        </div>
                        <button class="delete-btn" onclick="deleteDocument('${doc.filename}')">Delete</button>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Failed to load documents:', error);
                document.getElementById('documentsList').innerHTML = '<div class="error">Failed to load documents</div>';
            }
        }
        
        // Upload documents
        async function uploadDocuments() {
            const fileInput = document.getElementById('fileInput');
            const files = fileInput.files;
            
            if (files.length === 0) {
                alert('Please select files to upload');
                return;
            }
            
            for (let file of files) {
                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    const response = await fetch('/api/documents/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        showMessage(`Document ${file.name} uploaded successfully`, 'success');
                    } else {
                        showMessage(`Failed to upload ${file.name}`, 'error');
                    }
                } catch (error) {
                    console.error('Upload error:', error);
                    showMessage(`Failed to upload ${file.name}`, 'error');
                }
            }
            
            // Clear file input
            fileInput.value = '';
            loadDocuments();
            loadStats();
        }
        
        // Delete document
        async function deleteDocument(filename) {
            if (!confirm(`Are you sure you want to delete ${filename}?`)) {
                return;
            }
            
            try {
                const response = await fetch(`/api/documents/${filename}`, {
                    method: 'DELETE'
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showMessage(`Document ${filename} deleted successfully`, 'success');
                    loadDocuments();
                    loadStats();
                } else {
                    showMessage(`Failed to delete ${filename}`, 'error');
                }
            } catch (error) {
                console.error('Delete error:', error);
                showMessage(`Failed to delete ${filename}`, 'error');
            }
        }
        
        // Process query
        async function processQuery() {
            const queryInput = document.getElementById('queryInput');
            const queryBtn = document.getElementById('queryBtn');
            const responseSection = document.getElementById('responseSection');
            const responseContent = document.getElementById('responseContent');
            
            const query = queryInput.value.trim();
            if (!query) {
                alert('Please enter a query');
                return;
            }
            
            // Show loading state
            queryBtn.disabled = true;
            queryBtn.textContent = '🔄 Processing...';
            responseSection.classList.add('show');
            responseContent.innerHTML = '<div class="loading"><div class="spinner"></div>Processing your query...</div>';
            
            try {
                const request = {
                    query: query,
                    enable_human_loop: document.getElementById('humanLoop').checked,
                    verbose: document.getElementById('verboseMode').checked
                };
                
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(request)
                });
                
                const result = await response.json();
                displayQueryResult(result);
                
            } catch (error) {
                console.error('Query error:', error);
                responseContent.innerHTML = '<div class="error">Failed to process query. Please try again.</div>';
            } finally {
                queryBtn.disabled = false;
                queryBtn.textContent = '🚀 Process Query';
            }
        }
        
        // Display query result
        function displayQueryResult(result) {
            const responseContent = document.getElementById('responseContent');
            
            let html = `
                <div class="response-answer">
                    <strong>Answer:</strong><br>
                    ${result.answer}
                </div>
                
                <div style="margin: 15px 0; padding: 10px; background: #e3f2fd; border-radius: 5px;">
                    <strong>Query ID:</strong> ${result.query_id}<br>
                    <strong>Processing Time:</strong> ${result.processing_time.toFixed(2)}s<br>
                    <strong>Confidence:</strong> ${(result.confidence * 100).toFixed(1)}%<br>
                    <strong>Timestamp:</strong> ${new Date(result.timestamp).toLocaleString()}
                </div>
            `;
            
            if (result.human_validation_required) {
                html += '<div class="success">✅ Human validation required - response pending approval</div>';
            }
            
            if (result.sources && result.sources.length > 0) {
                html += '<div class="response-sources"><strong>Sources:</strong>';
                result.sources.forEach((source, index) => {
                    html += `
                        <div class="source-item">
                            <strong>Source ${index + 1}:</strong> ${source.filename || 'Unknown'}<br>
                            <em>${source.content || source.text || 'No content available'}</em>
                        </div>
                    `;
                });
                html += '</div>';
            }
            
            responseContent.innerHTML = html;
        }
        
        // Show message
        function showMessage(message, type) {
            const messageDiv = document.createElement('div');
            messageDiv.className = type;
            messageDiv.textContent = message;
            messageDiv.style.position = 'fixed';
            messageDiv.style.top = '20px';
            messageDiv.style.right = '20px';
            messageDiv.style.zIndex = '1000';
            messageDiv.style.maxWidth = '300px';
            
            document.body.appendChild(messageDiv);
            
            setTimeout(() => {
                document.body.removeChild(messageDiv);
            }, 5000);
        }
        
        // Format file size
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            initWebSocket();
            loadStats();
            loadDocuments();
            
            // Auto-refresh stats every 30 seconds
            setInterval(loadStats, 30000);
        });
    </script>
</body>
</html>
        """
    
    def start(self, host: str = "127.0.0.1", port: int = 8000):
        """Start the web API server."""
        import uvicorn
        
        logger.info("Starting MIRAGE v2 Web API", host=host, port=port)
        uvicorn.run(self.app, host=host, port=port, log_level="info")


def create_web_api(api_key: str) -> MIRAGEWebAPI:
    """Create and return a MIRAGE Web API instance."""
    return MIRAGEWebAPI(api_key)
