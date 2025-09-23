#!/usr/bin/env python3
"""
API minimaliste évitant tous les imports problématiques
Priorité HITL → Fallback Éthique
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from simple_orchestrator import orchestrator
import uvicorn
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MIRAGE Simple API", 
    version="1.0",
    description="API simplifiée avec priorité HITL → Fallback Éthique"
)

class QueryRequest(BaseModel):
    query: str
    target_language: str = None
    enable_human_loop: bool = True

class QueryResponse(BaseModel):
    success: bool
    query_id: str
    answer: str
    sources: list
    confidence: float
    processing_time: float
    human_validation_required: bool
    timestamp: str
    agent_workflow: list
    consensus: str
    iteration: int
    verification: dict
    workflow: str
    detected_language: str
    target_language: str

@app.get("/")
async def root():
    return {
        "message": "MIRAGE Simple API - HITL Prioritaire", 
        "version": "1.0",
        "status": "active",
        "hitl_priority": "HITL → Fallback Éthique"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "version": "simple_1.0",
        "hitl_enabled": True,
        "priority": "HITL → Fallback Éthique"
    }

@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """
    Endpoint simplifié avec priorité HITL
    """
    try:
        logger.info(f"🔍 Processing query: {request.query[:50]}...")
        logger.info(f"🎯 HITL enabled: {request.enable_human_loop}")
        
        # Traitement avec l'orchestrateur simplifié
        result = orchestrator.process_query(request.query, request.target_language)
        
        # Adapter la réponse au format API
        response = QueryResponse(
            success=result["success"],
            query_id=result["query_id"],
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"],
            processing_time=result["processing_time"],
            human_validation_required=result["human_validation_required"],
            timestamp=result["timestamp"],
            agent_workflow=result["agent_workflow"],
            consensus=result["consensus"],
            iteration=result["iteration"],
            verification=result["verification"],
            workflow=result["workflow"],
            detected_language=result["detected_language"],
            target_language=result["target_language"]
        )
        
        logger.info(f"✅ Response: {result['workflow']} | HITL: {result['human_validation_required']}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur de traitement: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    return {
        "total_queries": 0,
        "successful_queries": 0,
        "hitl_triggered": 0,
        "ethical_fallback": 0,
        "average_response_time": 0.0,
        "success_rate": 1.0
    }

if __name__ == "__main__":
    print("🚀 Démarrage de l'API simplifiée MIRAGE...")
    print("🎯 Priorité HITL → Fallback Éthique")
    print("🌍 Port: 8005")
    print("📝 Logs: server_simple.log")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8005,
        reload=False,  # Désactivé pour éviter les problèmes
        workers=1,
        log_level="info"
    )
