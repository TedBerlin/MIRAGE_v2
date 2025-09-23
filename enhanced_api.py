#!/usr/bin/env python3
"""
API MIRAGE v2 avec RAG Avancé
Gestion transparente des documents avec prise en compte immédiate
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from simple_orchestrator import orchestrator
from advanced_rag_manager import rag_manager
import uvicorn
import logging
from typing import List, Dict, Any, Optional

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MIRAGE v2 Enhanced API", 
    version="2.0",
    description="API avec RAG avancé et HITL prioritaire"
)

class QueryRequest(BaseModel):
    query: str
    target_language: str = None
    enable_human_loop: bool = True

class DocumentUploadResponse(BaseModel):
    success: bool
    document_id: str
    chunks_count: int
    status: str
    timestamp: str

class RAGSearchResponse(BaseModel):
    success: bool
    results: List[Dict[str, Any]]
    total_found: int
    query: str

@app.get("/")
async def root():
    return {
        "message": "MIRAGE v2 Enhanced API - RAG Avancé + HITL Prioritaire", 
        "version": "2.0",
        "status": "active",
        "features": ["HITL Priority", "Advanced RAG", "Document Management", "Multilingual"]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "version": "2.0",
        "hitl_enabled": True,
        "rag_enabled": True,
        "priority": "HITL → Fallback Éthique"
    }

@app.post("/query", response_model=Dict[str, Any])
async def handle_query(request: QueryRequest):
    """
    Endpoint avec RAG avancé et HITL prioritaire
    """
    try:
        logger.info(f"🔍 Processing query: {request.query[:50]}...")
        
        # Recherche RAG si disponible
        rag_results = []
        if rag_manager.get_document_stats()["total_documents"] > 0:
            rag_results = rag_manager.search_similar(request.query, top_k=3)
            logger.info(f"📚 RAG results: {len(rag_results)} documents trouvés")
        
        # Traitement avec l'orchestrateur
        result = orchestrator.process_query(request.query, request.target_language)
        
        # Enrichissement avec RAG si disponible
        if rag_results and result.get("workflow") != "human_validation":
            # Ajouter les sources RAG
            result["sources"] = [
                {
                    "content": r["content"],
                    "similarity": r["similarity"],
                    "document_id": r["document_id"]
                }
                for r in rag_results
            ]
            result["rag_enabled"] = True
            result["rag_results_count"] = len(rag_results)
        else:
            result["rag_enabled"] = False
            result["rag_results_count"] = 0
        
        logger.info(f"✅ Response: {result['workflow']} | HITL: {result['human_validation_required']} | RAG: {len(rag_results)}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur de traitement: {str(e)}")

@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    metadata: str = Form("{}")
):
    """
    Upload de document avec traitement immédiat
    """
    try:
        # Lecture du contenu
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Traitement immédiat
        result = rag_manager.add_document(
            document_path=file.filename,
            content=content_str,
            metadata={"filename": file.filename, "size": len(content)}
        )
        
        logger.info(f"📄 Document uploadé: {file.filename} ({result['chunks_count']} chunks)")
        return DocumentUploadResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Erreur upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur upload: {str(e)}")

@app.get("/documents/search")
async def search_documents(query: str, top_k: int = 5):
    """
    Recherche dans les documents
    """
    try:
        results = rag_manager.search_similar(query, top_k)
        
        return RAGSearchResponse(
            success=True,
            results=results,
            total_found=len(results),
            query=query
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur recherche: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur recherche: {str(e)}")

@app.get("/documents/stats")
async def get_document_stats():
    """
    Statistiques des documents
    """
    try:
        stats = rag_manager.get_document_stats()
        return {
            "success": True,
            "stats": stats,
            "timestamp": "2025-09-21T12:00:00"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur stats: {str(e)}")

@app.delete("/documents/clear")
async def clear_documents():
    """
    Nettoyage des documents
    """
    try:
        rag_manager.clear_all()
        return {
            "success": True,
            "message": "Documents nettoyés",
            "timestamp": "2025-09-21T12:00:00"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur nettoyage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur nettoyage: {str(e)}")

if __name__ == "__main__":
    print("🚀 Démarrage de l'API MIRAGE v2 Enhanced...")
    print("🎯 Features: HITL Prioritaire + RAG Avancé")
    print("📚 Gestion de documents: Transparente et immédiate")
    print("🌍 Port: 8006")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8006,
        reload=False,
        workers=1,
        log_level="info"
    )
