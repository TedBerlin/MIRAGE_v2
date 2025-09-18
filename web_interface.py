#!/usr/bin/env python3
"""
MIRAGE v2 - Complete Web Interface
Multi-Agent System with Human-in-the-Loop Validation
"""

import os
import time
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

# FastAPI imports
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Import MIRAGE components
import sys
sys.path.append('src')

# Import du système multi-agent (VALIDÉ)
from orchestrator.multi_agent_orchestrator import MultiAgentOrchestrator

# Initialiser le système multi-agent
multi_agent_orchestrator = MultiAgentOrchestrator()

print("✅ Initializing MIRAGE v2 with Multi-Agent System")
print(f"   - Multi-Agent Orchestrator: Active")
print(f"   - Generator Agent: Active")
print(f"   - Verifier Agent: Active")
print(f"   - Reformer Agent: Active")
print(f"   - Translator Agent: Active")

# Models
class QueryRequest(BaseModel):
    query: str
    enable_human_loop: bool = False
    verbose: bool = False

class QueryResponse(BaseModel):
    success: bool = True
    query_id: str
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    processing_time: float
    human_validation_required: bool = False
    timestamp: str
    # Multi-Agent metadata
    agent_workflow: List[str] = []
    consensus: str = "N/A"
    iteration: int = 1
    verification: Dict[str, Any] = {}
    workflow: str = "multi_agent"

class DocumentInfo(BaseModel):
    filename: str
    size: int
    upload_date: datetime
    processed: bool = False
    chunks_count: int = 0
    metadata: Dict[str, Any] = {}

# Initialize FastAPI app
app = FastAPI(
    title="MIRAGE v2 - Multi-Agent Pharmaceutical Research System",
    description="Advanced AI system for pharmaceutical research with human validation",
    version="2.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for simulation
documents_count = 0
queries_count = 0
total_processing_time = 0.0
successful_queries = 0

def reset_statistics():
    """Reset system statistics to zero."""
    global queries_count, total_processing_time, successful_queries
    queries_count = 0
    total_processing_time = 0.0
    successful_queries = 0

# Complete HTML Interface
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIRAGE v2 - Multi-Agent Pharmaceutical Research System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.2rem; opacity: 0.9; }
        .dashboard { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
        .card { background: white; border-radius: 15px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); transition: transform 0.3s ease; }
        .card:hover { transform: translateY(-5px); }
        .stats-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .stat-item { text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px; }
        .stat-value { font-size: 2rem; font-weight: bold; color: #2c3e50; }
        .stat-label { color: #7f8c8d; font-size: 0.9rem; margin-top: 5px; }
        .query-section { background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        .query-input { width: 100%; padding: 15px; border: 2px solid #e9ecef; border-radius: 10px; font-size: 1.1rem; margin-bottom: 15px; transition: border-color 0.3s ease; }
        .query-input:focus { outline: none; border-color: #667eea; }
        .options { display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap; }
        .option-group { display: flex; align-items: center; gap: 8px; }
        .option-group label { font-weight: 500; color: #2c3e50; }
        .btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 25px; border-radius: 8px; cursor: pointer; font-size: 1rem; font-weight: 500; transition: all 0.3s ease; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .response-section { margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 10px; min-height: 200px; }
        .loading { text-align: center; padding: 40px; color: #667eea; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #667eea; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 20px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .error { background: #ffebee; color: #c62828; padding: 15px; border-radius: 10px; margin: 10px 0; }
        .success { background: #e8f5e8; color: #2e7d32; padding: 15px; border-radius: 10px; margin: 10px 0; }
        
        /* ===== CONNECTION STATUS ===== */
        .connection-status {
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
            z-index: 1000;
            transition: all 0.3s ease;
        }
        .connection-status.online {
            background: #e8f5e8;
            color: #2e7d32;
            border: 1px solid #4caf50;
        }
        .connection-status.offline {
            background: #ffebee;
            color: #c62828;
            border: 1px solid #f44336;
        }
        
        /* ===== STYLES POUR LA CONVERSATION ===== */
        .message {
            margin: 15px 0;
            padding: 12px;
            border-radius: 8px;
            animation: fadeIn 0.3s ease-in;
        }
        .user-message {
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
            margin-left: 20%;
        }
        .ai-message {
            background-color: #f1f8e9;
            border-left: 4px solid #4caf50;
            margin-right: 20%;
        }
        .error-message {
            background-color: #ffebee;
            border-left: 4px solid #f44336;
        }
        .message-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            padding-bottom: 4px;
            border-bottom: 1px solid rgba(0,0,0,0.1);
        }
        .timestamp {
            font-size: 0.8em;
            color: #666;
            font-style: italic;
        }
        .message-content {
            line-height: 1.5;
            margin-bottom: 8px;
        }
        .message-meta {
            font-size: 0.8em;
            color: #666;
            font-style: italic;
            margin-top: 8px;
            padding-top: 4px;
            border-top: 1px solid rgba(0,0,0,0.1);
        }
        .sources {
            margin-top: 10px;
            padding: 8px;
            background-color: #fff3e0;
            border-radius: 4px;
            font-size: 0.9em;
        }
        .sources ul {
            margin: 4px 0;
            padding-left: 20px;
        }
        .sources li {
            margin: 2px 0;
        }
        .agent-workflow {
            margin-top: 10px;
            padding: 8px;
            background-color: #f3e5f5;
            border-radius: 4px;
            font-size: 0.9em;
        }
        
        .verification-details {
            margin-top: 10px;
            padding: 8px;
            background-color: #e8f5e8;
            border-radius: 4px;
            font-size: 0.9em;
        }
        .message-separator {
            border: none;
            border-top: 1px dashed #ccc;
            margin: 20px 0;
        }
        .notification {
            background: #4caf50;
            color: white;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            text-align: center;
            animation: slideIn 0.3s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideIn {
            from { transform: translateY(-20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        #responseContent {
            max-height: 500px;
            overflow-y: auto;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin-bottom: 15px;
            background-color: #fafafa;
        }
        @media (max-width: 768px) { .dashboard { grid-template-columns: 1fr; } .header h1 { font-size: 2rem; } .options { flex-direction: column; } }
        
        /* ===== STYLES POUR LA VALIDATION HUMAINE ===== */
        
        .human-validation-required {
            background-color: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .validation-triggers {
            background-color: #f8f9fa;
            border-radius: 4px;
            padding: 10px;
            margin: 10px 0;
            font-size: 14px;
        }
        
        .validation-actions {
            display: flex;
            gap: 10px;
            margin: 15px 0;
            flex-wrap: wrap;
        }
        
        .validation-btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .approve-btn {
            background-color: #28a745;
            color: white;
        }
        
        .approve-btn:hover {
            background-color: #218838;
        }
        
        .reject-btn {
            background-color: #dc3545;
            color: white;
        }
        
        .reject-btn:hover {
            background-color: #c82333;
        }
        
        .modify-btn {
            background-color: #17a2b8;
            color: white;
        }
        
        .modify-btn:hover {
            background-color: #138496;
        }
        
        .validation-notes textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
            resize: vertical;
            margin-top: 10px;
        }
        
        /* ===== BOÎTE DE DIALOGUE DE MODIFICATION ===== */
        
        .modify-dialog-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        
        .modify-dialog {
            background: white;
            border-radius: 8px;
            padding: 20px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
        
        .modify-dialog h3 {
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        
        .dialog-content {
            margin: 20px 0;
        }
        
        .dialog-content label {
            display: block;
            margin: 15px 0 5px 0;
            font-weight: bold;
            color: #555;
        }
        
        .dialog-content textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
            resize: vertical;
        }
        
        .dialog-actions {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-top: 20px;
        }
        
        .btn-primary {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }
        
        .btn-primary:hover {
            background-color: #0056b3;
        }
        
        .btn-secondary {
            background-color: #6c757d;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }
        
        .btn-secondary:hover {
            background-color: #545b62;
        }
        
        /* ===== STYLES POUR LE MODE VERBOSE ===== */
        
        .verbose-details {
            margin-top: 15px;
            padding: 15px;
            background-color: #f8f9fa;
            border: 2px solid #6c757d;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.4;
        }
        
        .verbose-section {
            margin: 10px 0;
            padding: 8px;
            background-color: #ffffff;
            border-radius: 4px;
            border-left: 3px solid #007bff;
        }
        
        .verbose-info {
            color: #495057;
            font-weight: normal;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧬 MIRAGE v2</h1>
            <p>Multi-Agent Pharmaceutical Research System</p>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h3>📊 System Statistics</h3>
                <div class="stats-container">
                    <div class="stat-item">
                        <div class="stat-value" id="totalDocuments">0</div>
                        <div class="stat-label">Documents</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="totalQueries">0</div>
                        <div class="stat-label">Queries</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="avgResponseTime">0.00</div>
                        <div class="stat-label">Avg Response (s)</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="successRate">0%</div>
                        <div class="stat-label">Success Rate</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>🔧 System Health</h3>
                <div id="systemHealth">
                    <div class="stat-item">
                        <div class="stat-value" id="systemStatus">Loading...</div>
                        <div class="stat-label">Status</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card" style="margin-bottom: 30px;">
            <h3>📁 Document Management</h3>
            <div class="upload-section">
                <input type="file" id="fileInput" multiple accept=".pdf,.txt,.docx" style="display: none;">
                <button class="btn" onclick="document.getElementById('fileInput').click()" style="background: #28a745;">
                    📤 Upload Documents
                </button>
                <div id="uploadStatus" style="margin-top: 10px; font-size: 0.9em;"></div>
            </div>
            
            <div class="documents-list" id="documentsList" style="margin-top: 20px;">
                <div style="text-align: center; color: #666; padding: 20px;">
                    <p>Loading documents...</p>
                </div>
            </div>
        </div>
        
        <div class="query-section">
            <h3>💬 Query Interface</h3>
            <div class="options">
                <div class="option-group">
                    <input type="checkbox" id="humanLoop" name="humanLoop">
                    <label for="humanLoop">Human Validation</label>
                </div>
                <div class="option-group">
                    <input type="checkbox" id="verboseMode" name="verboseMode">
                    <label for="verboseMode">Verbose Mode</label>
                </div>
            </div>
            <input type="text" id="queryInput" class="query-input" placeholder="Ask about pharmaceutical research, drug interactions, side effects, etc...">
            <button class="btn" id="queryBtn" onclick="processQuery()">
                🚀 Process Query
            </button>
            
            <button class="btn" onclick="clearHistory()" id="clearBtn" style="background: #f44336; margin-left: 10px;">
                🗑️ Clear History
            </button>
            
            <div class="response-section" id="responseSection">
                <div id="responseContent">
                    <div style="text-align: center; color: #666; padding: 40px;">
                        <h4>🤖 MIRAGE v2 Ready</h4>
                        <p>Ask me anything about pharmaceutical research!</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // ===== VARIABLES GLOBALES =====
        let conversationHistory = [];
        let isProcessing = false;

        // Load system statistics with intelligent error handling
        let connectionRetries = 0;
        let isServerOnline = true;
        
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                const stats = await response.json();
                document.getElementById('totalDocuments').textContent = stats.total_documents;
                document.getElementById('totalQueries').textContent = stats.total_queries;
                document.getElementById('avgResponseTime').textContent = stats.average_response_time.toFixed(2);
                document.getElementById('successRate').textContent = (stats.success_rate * 100).toFixed(1) + '%';
                
                // Reset connection status on success
                if (!isServerOnline) {
                    isServerOnline = true;
                    connectionRetries = 0;
                    updateConnectionStatus('online');
                }
            } catch (error) {
                connectionRetries++;
                isServerOnline = false;
                updateConnectionStatus('offline');
                
                // Stop polling after 3 failed attempts
                if (connectionRetries >= 3) {
                    console.warn('Server appears to be offline. Stopping stats polling.');
                    return;
                }
                
                console.warn(`Failed to load stats (attempt ${connectionRetries}):`, error.message);
            }
        }
        
        // Update connection status indicator
        function updateConnectionStatus(status) {
            const statusElement = document.getElementById('connectionStatus') || createConnectionStatusElement();
            if (status === 'online') {
                statusElement.textContent = '🟢 Online';
                statusElement.className = 'connection-status online';
            } else {
                statusElement.textContent = '🔴 Offline';
                statusElement.className = 'connection-status offline';
            }
        }
        
        // Create connection status element if it doesn't exist
        function createConnectionStatusElement() {
            const statusElement = document.createElement('div');
            statusElement.id = 'connectionStatus';
            statusElement.className = 'connection-status';
            document.querySelector('.stats-container').appendChild(statusElement);
            return statusElement;
        }
        
        // Load documents
        async function loadDocuments() {
            try {
                const response = await fetch('/api/documents');
                const documents = await response.json();
                
                const documentsList = document.getElementById('documentsList');
                if (documents.length === 0) {
                    documentsList.innerHTML = '<div style="text-align: center; color: #666; padding: 20px;"><p>Aucun document trouvé</p></div>';
                } else {
                    let html = '';
                    documents.forEach(doc => {
                        const size = (doc.size / 1024 / 1024).toFixed(2);
                        const date = new Date(doc.upload_date).toLocaleDateString();
                        html += `
                            <div class="document-item" style="display: flex; justify-content: space-between; align-items: center; padding: 10px; border: 1px solid #ddd; border-radius: 8px; margin: 10px 0; background: #f9f9f9;">
                                <div>
                                    <strong>${doc.filename}</strong><br>
                                    <small style="color: #666;">${size} MB • ${date}</small>
                                </div>
                                <button class="btn" onclick="deleteDocument('${doc.filename}')" style="background: #dc3545; padding: 5px 10px; font-size: 0.8em;">
                                    Delete
                                </button>
                            </div>
                        `;
                    });
                    documentsList.innerHTML = html;
                }
            } catch (error) {
                console.error('Failed to load documents:', error);
                document.getElementById('documentsList').innerHTML = '<div style="text-align: center; color: #dc3545; padding: 20px;"><p>Erreur lors du chargement des documents</p></div>';
            }
        }
        
        // Upload documents
        document.getElementById('fileInput').addEventListener('change', async function(e) {
            const files = e.target.files;
            if (files.length === 0) return;
            
            const uploadStatus = document.getElementById('uploadStatus');
            uploadStatus.innerHTML = '<div style="color: #007bff;">Upload en cours...</div>';
            
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
                        uploadStatus.innerHTML += `<div style="color: #28a745;">✅ ${file.name} uploadé avec succès</div>`;
                    } else {
                        uploadStatus.innerHTML += `<div style="color: #dc3545;">❌ Erreur pour ${file.name}</div>`;
                    }
                } catch (error) {
                    uploadStatus.innerHTML += `<div style="color: #dc3545;">❌ Erreur pour ${file.name}: ${error.message}</div>`;
                }
            }
            
            // Reload documents list
            await loadDocuments();
            await loadStats();
        });
        
        // Delete document
        async function deleteDocument(filename) {
            if (!confirm(`Êtes-vous sûr de vouloir supprimer ${filename} ?`)) return;
            
            try {
                const response = await fetch(`/api/documents/${filename}`, {
                    method: 'DELETE'
                });
                
                const result = await response.json();
                if (result.success) {
                    showMessage(`Document ${filename} supprimé avec succès`, 'success');
                    await loadDocuments();
                    await loadStats();
                } else {
                    showMessage(`Erreur lors de la suppression: ${result.error}`, 'error');
                }
            } catch (error) {
                showMessage(`Erreur lors de la suppression: ${error.message}`, 'error');
            }
        }
        
        // ===== FONCTION PRINCIPALE CORRIGÉE =====
        async function processQuery() {
            if (isProcessing) return;
            
            const queryInput = document.getElementById('queryInput');
            const queryBtn = document.getElementById('queryBtn');
            const responseSection = document.getElementById('responseSection');
            const responseContent = document.getElementById('responseContent');
            
            const query = queryInput.value.trim();
            if (!query) {
                alert('Please enter a query');
                return;
            }
            
            isProcessing = true;
            queryBtn.disabled = true;
            queryBtn.textContent = '🔄 Processing...';
            responseSection.classList.add('show');
            
            try {
                // ===== AJOUTER LE MESSAGE UTILISATEUR =====
                const userMessage = {
                    type: 'user',
                    content: query,
                    timestamp: new Date().toLocaleTimeString()
                };
                conversationHistory.push(userMessage);
                
                // ===== METTRE À JOUR L'AFFICHAGE =====
                updateConversationDisplay();
                
                // ===== ENVOYER LA REQUÊTE =====
                const request = {
                    query: query,
                    enable_human_loop: document.getElementById('humanLoop').checked,
                    verbose: document.getElementById('verboseMode').checked
                };
                
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify(request)
                });

                if (!response.ok) {
                    throw new Error(`Erreur HTTP: ${response.status}`);
                }
                
                const result = await response.json();
                
                // ===== AJOUTER LA RÉPONSE DE L'IA =====
                const aiMessage = {
                    type: 'ai',
                    content: result.answer,
                    sources: result.sources || [],
                    confidence: result.confidence || 0,
                    processing_time: result.processing_time || 0,
                    query_id: result.query_id || 'unknown',
                    agent_workflow: result.agent_workflow || [],
                    consensus: result.consensus || 'N/A',
                    verification: result.verification || {},
                    human_validation_required: result.human_validation_required || result.consensus === 'pending_human_validation',
                    validation_triggers: result.human_validation?.triggers || result.human_validation?.validation_request?.triggers || result.human_validation || null,
                    timestamp: new Date().toLocaleTimeString()
                };
                conversationHistory.push(aiMessage);
                
                // ===== METTRE À JOUR L'AFFICHAGE =====
                updateConversationDisplay();
                
            } catch (error) {
                console.error('Query error:', error);
                
                // ===== AJOUTER UN MESSAGE D'ERREUR =====
                const errorMessage = {
                    type: 'error',
                    content: `❌ Erreur: ${error.message}`,
                    timestamp: new Date().toLocaleTimeString()
                };
                conversationHistory.push(errorMessage);
                updateConversationDisplay();
                
            } finally {
                isProcessing = false;
                queryBtn.disabled = false;
                queryBtn.textContent = '🚀 Process Query';
                queryInput.value = '';
                
                // Scroll vers le bas
                responseContent.scrollTop = responseContent.scrollHeight;
            }
        }
        
        // ===== FONCTION D'AFFICHAGE CORRIGÉE =====
        function updateConversationDisplay() {
            const responseContent = document.getElementById('responseContent');
            
            // ===== RECONSTRUIRE TOUTE LA CONVERSATION =====
            let htmlContent = '';
            
            conversationHistory.forEach((message, index) => {
                if (message.type === 'user') {
                    htmlContent += `
                        <div class="message user-message">
                            <div class="message-header">
                                <strong>👤 Vous</strong>
                                <span class="timestamp">${message.timestamp}</span>
                            </div>
                            <div class="message-content">${message.content.replace(/\\n/g, '<br>')}</div>
                        </div>
                    `;
                } 
                else if (message.type === 'ai') {
                    htmlContent += `
                        <div class="message ai-message">
                            <div class="message-header">
                                <strong>🤖 MIRAGE</strong>
                                <span class="timestamp">${message.timestamp}</span>
                            </div>
                            <div class="message-content">${message.content.replace(/\\n/g, '<br>')}</div>
                    `;
                    
                    // Ajouter les sources si disponibles
                    if (message.sources && message.sources.length > 0) {
                        htmlContent += `
                            <div class="sources">
                                <strong>📚 Sources:</strong>
                                <ul>
                                    ${message.sources.map(source => `
                                        <li>${source.filename || source.type || 'Unknown'} 
                                            ${source.confidence ? `(confiance: ${(source.confidence * 100).toFixed(1)}%)` : ''}
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        `;
                    }
                    
                    // Ajouter les métadonnées multi-agent
                    if (message.agent_workflow && message.agent_workflow.length > 0) {
                        htmlContent += `
                            <div class="agent-workflow">
                                <strong>🤖 Workflow:</strong> ${message.agent_workflow.map(agent => agent.charAt(0).toUpperCase() + agent.slice(1)).join(' → ')}<br>
                                <strong>Consensus:</strong> ${message.consensus}<br>
                                <strong>Temps:</strong> ${message.processing_time.toFixed(2)}s
                            </div>
                        `;
                    }
                    
                    // Verification Details
                    if (message.verification && Object.keys(message.verification).length > 0) {
                        htmlContent += `
                            <div class="verification-details">
                                <strong>🔍 Verification Details:</strong><br>
                                • Vote: ${message.verification.vote || 'N/A'}<br>
                                • Confidence: ${message.verification.confidence ? (message.verification.confidence * 100).toFixed(1) + '%' : 'N/A'}<br>
                                • Accuracy Score: ${message.verification.accuracy_score ? (message.verification.accuracy_score * 100).toFixed(1) + '%' : 'N/A'}<br>
                                • Completeness Score: ${message.verification.completeness_score ? (message.verification.completeness_score * 100).toFixed(1) + '%' : 'N/A'}
                            </div>
                        `;
                    }
                    
                    // Mode Verbose - Détails techniques
                    const verboseMode = document.getElementById('verboseMode')?.checked;
                    if (verboseMode && message.verification) {
                        htmlContent += `
                            <div class="verbose-details">
                                <strong>🔍 VERBOSE MODE - Détails Techniques:</strong><br>
                                <div class="verbose-section">
                                    <strong>┌─ Generator Agent ─────────────────────────┐</strong><br>
                                    <span class="verbose-info">Temps: ${message.processing_time ? message.processing_time.toFixed(2) + 's' : 'N/A'} | Confiance: ${(message.confidence * 100).toFixed(1)}%</span><br>
                                    <span class="verbose-info">Réponse brute: [${message.content ? message.content.length : 0} caractères]</span><br>
                                    <strong>└───────────────────────────────────────────┘</strong>
                                </div>
                                
                                <div class="verbose-section">
                                    <strong>┌─ Verifier Agent ──────────────────────────┐</strong><br>
                                    <span class="verbose-info">Temps: N/A | Vote: ${message.verification.vote || 'N/A'} | Confiance: ${message.verification.confidence ? (message.verification.confidence * 100).toFixed(1) + '%' : 'N/A'}</span><br>
                                    <span class="verbose-info">Accuracy: ${message.verification.accuracy_score ? (message.verification.accuracy_score * 100).toFixed(1) + '%' : 'N/A'} | Completeness: ${message.verification.completeness_score ? (message.verification.completeness_score * 100).toFixed(1) + '%' : 'N/A'}</span><br>
                                    <span class="verbose-info">Analyse: [${message.verification.verification_analysis ? message.verification.verification_analysis.length : 0} caractères]</span><br>
                                    <strong>└───────────────────────────────────────────┘</strong>
                                </div>
                                
                                <div class="verbose-section">
                                    <strong>┌─ Workflow Trace ──────────────────────────┐</strong><br>
                                    <span class="verbose-info">1. Generator: Response generated</span><br>
                                    <span class="verbose-info">2. Verifier: Vote = ${message.verification.vote || 'N/A'}, Confidence = ${message.verification.confidence ? (message.verification.confidence * 100).toFixed(1) + '%' : 'N/A'}</span><br>
                                    <span class="verbose-info">3. Consensus: ${message.consensus || 'N/A'}</span><br>
                                    <strong>└───────────────────────────────────────────┘</strong>
                                </div>
                                
                                <div class="verbose-section">
                                    <strong>┌─ System Metrics ──────────────────────────┐</strong><br>
                                    <span class="verbose-info">Total: ${message.processing_time ? message.processing_time.toFixed(2) + 's' : 'N/A'} | Cache: 0 hits | RAM: N/A</span><br>
                                    <strong>└───────────────────────────────────────────┘</strong>
                                </div>
                            </div>
                        `;
                    }
                    
                    // Human Validation Required
                    if (message.human_validation_required || message.consensus === 'pending_human_validation') {
                        htmlContent += `
                            <div class="human-validation-required">
                                <strong>⚠️ Human Validation Required / Validation Humaine Requise / Validación Humana Requerida / Menschliche Validierung Erforderlich</strong><br>
                                <div class="validation-triggers">
                                    <strong>Triggers detected / Déclencheurs détectés / Disparadores detectados / Auslöser erkannt:</strong><br>
                                    ${message.validation_triggers ? Object.entries(message.validation_triggers).map(([type, triggers]) => 
                                        triggers.length > 0 ? `• ${type}: ${triggers.join(', ')}<br>` : ''
                                    ).join('') : 'No specific triggers / Aucun déclencheur spécifique / Sin disparadores específicos / Keine spezifischen Auslöser'}
                                </div>
                                <div class="validation-actions">
                                    <button class="validation-btn approve-btn" onclick="submitValidation('${message.query_id}', 'approve')">
                                        ✅ Approve / Valider / Aprobar / Genehmigen
                                    </button>
                                    <button class="validation-btn reject-btn" onclick="submitValidation('${message.query_id}', 'reject')">
                                        ❌ Reject / Rejeter / Rechazar / Ablehnen
                                    </button>
                                    <button class="validation-btn modify-btn" onclick="showModifyDialog('${message.query_id}')">
                                        ✏️ Modify / Modifier / Modificar / Ändern
                                    </button>
                                </div>
                                <div class="validation-notes">
                                    <textarea id="notes_${message.query_id}" placeholder="Validation notes (optional) / Notes de validation (optionnel) / Notas de validación (opcional) / Validierungsnotizen (optional)..." rows="3"></textarea>
                                </div>
                            </div>
                        `;
                    }
                    
                    // Ajouter les métadonnées
                    htmlContent += `
                            <div class="message-meta">
                                Confiance: ${(message.confidence * 100).toFixed(1)}% | 
                                ID: ${message.query_id}
                            </div>
                        </div>
                    `;
                }
                else if (message.type === 'error') {
                    htmlContent += `
                        <div class="message error-message">
                            <div class="message-header">
                                <strong>❌ Erreur</strong>
                                <span class="timestamp">${message.timestamp}</span>
                            </div>
                            <div class="message-content">${message.content.replace(/\\n/g, '<br>')}</div>
                        </div>
                    `;
                }
                
                // Ajouter un séparateur sauf pour le dernier message
                if (index < conversationHistory.length - 1) {
                    htmlContent += `<hr class="message-separator">`;
                }
            });
            
            responseContent.innerHTML = htmlContent;
        }
        
        // ===== FONCTION POUR EFFACER L'HISTORIQUE =====
        function clearHistory() {
            conversationHistory = [];
            updateConversationDisplay();
            
            // Notification
            const responseContent = document.getElementById('responseContent');
            const notification = document.createElement('div');
            notification.className = 'notification';
            notification.textContent = 'Conversation effacée. Nouvelle session démarrée.';
            notification.style.cssText = `
                background: #4caf50;
                color: white;
                padding: 10px;
                margin: 10px 0;
                border-radius: 4px;
                text-align: center;
            `;
            
            responseContent.appendChild(notification);
            setTimeout(() => notification.remove(), 2000);
        }
        
        // ===== FONCTIONS DE VALIDATION HUMAINE =====
        
        // Soumettre une validation humaine
        async function submitValidation(queryId, decision) {
            const notes = document.getElementById(`notes_${queryId}`)?.value || '';
            
            try {
                const response = await fetch('/api/validation/submit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        response_id: queryId,
                        decision: decision,
                        notes: notes,
                        validator: 'human_user'
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`Erreur HTTP: ${response.status}`);
                }
                
                const result = await response.json();
                
                if (result.success) {
                    showMessage(`Validation ${decision} soumise avec succès`, 'success');
                    
                    // Mettre à jour l'affichage pour retirer la validation en attente
                    const messageIndex = conversationHistory.findIndex(msg => msg.query_id === queryId);
                    if (messageIndex !== -1) {
                        conversationHistory[messageIndex].human_validation_required = false;
                        conversationHistory[messageIndex].validation_status = decision;
                        updateConversationDisplay();
                    }
                    
                    // Recharger les statistiques
                    loadStats();
                } else {
                    showMessage(`Erreur lors de la validation: ${result.error}`, 'error');
                }
                
            } catch (error) {
                console.error('Validation error:', error);
                showMessage(`Erreur lors de la validation: ${error.message}`, 'error');
            }
        }
        
        // Afficher la boîte de dialogue de modification
        function showModifyDialog(queryId) {
            const message = conversationHistory.find(msg => msg.query_id === queryId);
            if (!message) return;
            
            const currentContent = message.content;
            const notes = document.getElementById(`notes_${queryId}`)?.value || '';
            
            // Créer une boîte de dialogue de modification
            const modifyDialog = document.createElement('div');
            modifyDialog.className = 'modify-dialog-overlay';
            modifyDialog.innerHTML = `
                <div class="modify-dialog">
                    <h3>✏️ Modifier la Réponse</h3>
                    <div class="dialog-content">
                        <label>Réponse actuelle:</label>
                        <textarea id="currentContent" readonly rows="8">${currentContent}</textarea>
                        
                        <label>Modifications suggérées:</label>
                        <textarea id="modifications" placeholder="Décrivez les modifications à apporter..." rows="4"></textarea>
                        
                        <label>Notes de validation:</label>
                        <textarea id="modifyNotes" placeholder="Notes supplémentaires..." rows="3">${notes}</textarea>
                    </div>
                    <div class="dialog-actions">
                        <button class="btn-secondary" onclick="closeModifyDialog()">Annuler</button>
                        <button class="btn-primary" onclick="submitModification('${queryId}')">Soumettre Modification</button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modifyDialog);
        }
        
        // Fermer la boîte de dialogue de modification
        function closeModifyDialog() {
            const dialog = document.querySelector('.modify-dialog-overlay');
            if (dialog) {
                dialog.remove();
            }
        }
        
        // Soumettre une modification
        async function submitModification(queryId) {
            const modifications = document.getElementById('modifications')?.value || '';
            const notes = document.getElementById('modifyNotes')?.value || '';
            
            if (!modifications.trim()) {
                showMessage('Veuillez décrire les modifications à apporter', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/validation/submit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        response_id: queryId,
                        decision: 'modify',
                        notes: notes,
                        modifications: modifications,
                        validator: 'human_user'
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`Erreur HTTP: ${response.status}`);
                }
                
                const result = await response.json();
                
                if (result.success) {
                    showMessage('Modification soumise avec succès', 'success');
                    closeModifyDialog();
                    
                    // Mettre à jour l'affichage
                    const messageIndex = conversationHistory.findIndex(msg => msg.query_id === queryId);
                    if (messageIndex !== -1) {
                        conversationHistory[messageIndex].human_validation_required = false;
                        conversationHistory[messageIndex].validation_status = 'modify';
                        conversationHistory[messageIndex].modifications = modifications;
                        updateConversationDisplay();
                    }
                    
                    // Recharger les statistiques
                    loadStats();
                } else {
                    showMessage(`Erreur lors de la modification: ${result.error}`, 'error');
                }
                
            } catch (error) {
                console.error('Modification error:', error);
                showMessage(`Erreur lors de la modification: ${error.message}`, 'error');
            }
        }
        
        // ===== GESTIONNAIRE D'ÉVÉNEMENTS =====
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            loadDocuments();
            
            // Intelligent polling: slower when offline, normal when online
            let pollingInterval = 30000; // 30 seconds default
            let statsInterval;
            
            function startStatsPolling() {
                if (statsInterval) clearInterval(statsInterval);
                statsInterval = setInterval(() => {
                    if (isServerOnline) {
                        loadStats();
                    } else {
                        // Try to reconnect every 60 seconds when offline
                        pollingInterval = 60000;
                        loadStats();
                    }
                }, pollingInterval);
            }
            
            startStatsPolling();
            
            // Enter key pour envoyer
            document.getElementById('queryInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    processQuery();
                }
            });
        });
        
        // Helper function to show messages
        function showMessage(message, type) {
            const responseContent = document.getElementById('responseContent');
            const messageDiv = document.createElement('div');
            messageDiv.className = type === 'error' ? 'error' : 'success';
            messageDiv.textContent = message;
            responseContent.appendChild(messageDiv);
            
            setTimeout(() => {
                messageDiv.remove();
            }, 5000);
        }
    </script>
</body>
</html>
"""

# Routes
@app.get("/")
async def root():
    """Serve the main interface."""
    return HTMLResponse(HTML_INTERFACE)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "name": "MIRAGE v2 - Complete Interface"
    }

@app.get("/api/stats")
async def get_system_stats():
    """Get system statistics including RAG data."""
    global queries_count, total_processing_time, successful_queries
    
    # Calculate actual document count from filesystem
    docs_dir = Path("data/raw_documents")
    actual_documents_count = 0
    if docs_dir.exists():
        actual_documents_count = len([f for f in docs_dir.iterdir() if f.is_file()])
    
    avg_time = total_processing_time / max(queries_count, 1)
    success_rate = (successful_queries / max(queries_count, 1)) if queries_count > 0 else 0.0
    
    # Get system statistics from multi-agent orchestrator
    try:
        orchestrator_stats = multi_agent_orchestrator.get_system_stats()
        system_health = multi_agent_orchestrator.health_check()
    except Exception as e:
        orchestrator_stats = {"error": str(e)}
        system_health = {"overall": "unhealthy"}
    
    # Get human validation statistics if available
    human_validation_stats = {}
    if hasattr(multi_agent_orchestrator, 'human_loop_manager') and multi_agent_orchestrator.human_loop_manager:
        human_validation_stats = multi_agent_orchestrator.human_loop_manager.get_validation_statistics()
    
    return {
        "total_documents": actual_documents_count,
        "total_queries": queries_count,
        "average_response_time": avg_time,
        "success_rate": success_rate,
        "system_health": system_health.get("overall", "unknown"),
        "uptime": "24h",
        "rag_documents": actual_documents_count,
        "rag_chunks": multi_agent_orchestrator.rag_engine.embedding_manager.get_collection_stats().get("total_chunks", 0),
        "rag_last_updated": datetime.now().isoformat(),
        "multi_agent_mode": "active",
        "orchestrator_status": orchestrator_stats.get("orchestrator", {}),
        "agents_status": orchestrator_stats.get("agents", {}),
        "gemini_available": True,
        "multi_agent_active": True,
        "human_validation": human_validation_stats
    }

@app.get("/api/documents", response_model=List[DocumentInfo])
async def list_documents():
    """List all uploaded documents."""
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
                    processed=True,
                    chunks_count=0,
                    metadata={"type": "pharmaceutical_document"}
                ))
    
    return documents

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document for processing and RAG integration."""
    global documents_count
    
    try:
        upload_dir = Path("data/raw_documents")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Ajouter le document à Qdrant via le système multi-agent
        try:
            qdrant_success = await multi_agent_orchestrator.rag_engine.ingest_documents(force_reprocess=True)
        except Exception as e:
            print(f"⚠️  Qdrant processing failed: {str(e)}")
            qdrant_success = False
        
        # Traitement RAG traditionnel (si disponible)
        rag_result = {"success": False, "error": "RAG engine not available"}
        if multi_agent_orchestrator.rag_engine:
            try:
                rag_result = multi_agent_orchestrator.rag_engine.ingest_documents(force_reprocess=True)
            except Exception as e:
                print(f"⚠️  RAG processing failed: {str(e)}")
                rag_result = {"success": False, "error": str(e)}
        
        # Résultat combiné
        processing_result = {
            "qdrant_success": qdrant_success,
            "rag_success": rag_result.get("success", False),
            "chunks_created": rag_result.get("chunks_created", 0)
        }
        
        documents_count += 1
        
        return {
            "success": True,
            "filename": file.filename,
            "size": len(content),
            "processed": True,
            "chunks": processing_result.get("chunks_created", 0),
            "qdrant_integrated": processing_result.get("qdrant_success", False),
            "rag_integrated": processing_result.get("rag_success", False)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Human-in-the-Loop Validation Routes
@app.get("/api/validation/queue")
@app.get("/api/human-validation/queue")
async def get_validation_queue():
    """Get current human validation queue."""
    if not hasattr(multi_agent_orchestrator, 'human_loop_manager') or not multi_agent_orchestrator.human_loop_manager:
        return {"error": "Human validation not enabled"}
    
    queue = multi_agent_orchestrator.human_loop_manager.get_validation_queue()
    return {"queue": queue, "count": len(queue)}

@app.get("/api/validation/history")
@app.get("/api/human-validation/history")
async def get_validation_history(limit: int = 100):
    """Get human validation history."""
    if not hasattr(multi_agent_orchestrator, 'human_loop_manager') or not multi_agent_orchestrator.human_loop_manager:
        return {"error": "Human validation not enabled"}
    
    history = multi_agent_orchestrator.human_loop_manager.get_validation_history(limit)
    return {"history": history, "count": len(history)}

@app.post("/api/validation/submit")
@app.post("/api/human-validation/submit")
async def submit_validation(request: Dict[str, Any]):
    """Submit human validation decision."""
    if not hasattr(multi_agent_orchestrator, 'human_loop_manager') or not multi_agent_orchestrator.human_loop_manager:
        raise HTTPException(status_code=400, detail="Human validation not enabled")
    
    response_id = request.get("response_id")
    decision = request.get("decision")  # "approve", "modify", "reject"
    notes = request.get("notes", "")
    modifications = request.get("modifications", "")
    validator = request.get("validator", "human_user")
    
    if not response_id or not decision:
        raise HTTPException(status_code=400, detail="Missing required fields: response_id, decision")
    
    success = multi_agent_orchestrator.human_loop_manager.submit_human_validation(
        response_id=response_id,
        decision=decision,
        notes=notes,
        modifications=modifications,
        validator=validator
    )
    
    if success:
        return {"success": True, "message": "Validation submitted successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to submit validation")

@app.get("/api/validation/statistics")
async def get_validation_statistics():
    """Get human validation statistics."""
    if not hasattr(multi_agent_orchestrator, 'human_loop_manager') or not multi_agent_orchestrator.human_loop_manager:
        return {"error": "Human validation not enabled"}
    
    stats = multi_agent_orchestrator.human_loop_manager.get_validation_statistics()
    return stats

@app.post("/api/rag/ingest")
async def ingest_rag_documents(force_reprocess: bool = False):
    """Ingest documents into RAG system."""
    try:
        result = multi_agent_orchestrator.rag_engine.ingest_documents(force_reprocess=force_reprocess)
        return result
    except Exception as e:
        logger.error("RAG ingestion failed", error=str(e))
        return {"success": False, "error": str(e)}

@app.delete("/api/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document."""
    global documents_count
    
    try:
        file_path = Path("data/raw_documents") / filename
        if file_path.exists():
            file_path.unlink()
            documents_count = max(0, documents_count - 1)
            return {"success": True, "message": f"Document {filename} deleted"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a query using MIRAGE v2 Multi-Agent System."""
    start_time = time.time()
    query_hash = multi_agent_orchestrator._generate_query_hash(request.query)
    
    try:
        # Use Multi-Agent Orchestrator (VALIDÉ)
        print(f"🔍 Processing query with Multi-Agent System: {request.query[:50]}...")
        
        # Appel au système multi-agent
        result = await multi_agent_orchestrator.process_query(
            query=request.query,
            enable_human_loop=request.enable_human_loop,  # Utiliser le paramètre de la requête
            target_language="en"
        )
        
        processing_time = time.time() - start_time
        global total_processing_time, queries_count, successful_queries
        total_processing_time += processing_time
        queries_count += 1
        successful_queries += 1
    
        # Formatage de la réponse du système multi-agent
        sources = []
        if result.get("rag_metadata", {}).get("source_documents"):
            for source in result["rag_metadata"]["source_documents"]:
                if isinstance(source, dict):
                    sources.append({
                        "filename": source.get("filename", source.get("type", "unknown")),
                        "content": source.get("content", "")[:200] + "..." if len(source.get("content", "")) > 200 else source.get("content", ""),
                        "confidence": source.get("confidence", 0.8)
                    })
                else:
                    sources.append({
                        "filename": str(source),
                        "content": "Source document",
                        "confidence": 0.8
                    })
        
        # Fonction pour nettoyer les objets complexes et les rendre sérialisables
        def clean_for_json(obj):
            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            elif isinstance(obj, (int, float, str, bool)) or obj is None:
                return obj
            else:
                return str(obj)
        
        # Nettoyer les objets complexes
        verification_clean = clean_for_json(result.get("verification", {}))
        human_validation_clean = clean_for_json(result.get("human_validation", {}))
        
        # Create response with multi-agent metadata (JSON-serializable)
        response_data = {
            "success": result.get("success", True),
            "query_id": result.get("query_hash", f"query_{int(time.time())}"),
            "answer": result.get("answer", "No answer generated"),
            "sources": sources,
            "confidence": float(result.get("verification", {}).get("confidence", 0.8)),
            "processing_time": float(processing_time),
            "human_validation_required": result.get("consensus") == "pending_human_validation",
            "timestamp": datetime.now().isoformat(),
            # Multi-Agent metadata
            "agent_workflow": result.get("agent_workflow", []) if isinstance(result.get("agent_workflow"), list) else [result.get("agent_workflow", "multi_agent")],
            "consensus": result.get("consensus", "N/A"),
            "iteration": int(result.get("iteration", 1)),
            "verification": verification_clean,
            "workflow": result.get("workflow", "multi_agent"),
            "human_validation": human_validation_clean
        }
        
        return QueryResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """Start the complete web interface."""
    # Reset statistics on startup
    reset_statistics()
    
    print("🚀 MIRAGE v2 - Complete Web Interface")
    print("=" * 50)
    print("✅ Complete interface initialized")
    print("🌐 Starting web interface...")
    print("   URL: http://127.0.0.1:8005")
    print("   Health: http://127.0.0.1:8005/health")
    print("   API: http://127.0.0.1:8005/api/")
    print()
    print("📋 Available features:")
    print("   • Upload pharmaceutical documents")
    print("   • AI-powered query processing")
    print("   • Human-in-the-Loop validation")
    print("   • Real-time monitoring")
    print("   • Document management")
    print("   • System statistics")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    uvicorn.run(app, host="127.0.0.1", port=8005, log_level="info")

if __name__ == "__main__":
    main()
