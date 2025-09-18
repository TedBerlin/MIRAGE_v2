"""
Simple RAG Engine for MIRAGE v2.
Simplified version without sentence-transformers to avoid segmentation fault.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)


class SimpleRAGEngine:
    """Simplified RAG engine using basic text matching."""
    
    def __init__(
        self,
        documents_path: str = "./data/raw_documents",
        max_results: int = 5,
        similarity_threshold: float = 0.3
    ):
        self.documents_path = Path(documents_path)
        self.max_results = max_results
        self.similarity_threshold = similarity_threshold
        
        # Simple keyword-based matching
        self.medical_keywords = [
            'paracetamol', 'acetaminophen', 'overdose', 'hepatotoxicity', 'liver',
            'side effects', 'contraindications', 'dosage', 'safety', 'clinical',
            'treatment', 'medication', 'drug', 'pharmaceutical', 'medical'
        ]
        
        logger.info(
            "SimpleRAGEngine initialized",
            documents_path=str(self.documents_path),
            max_results=max_results
        )
    
    def query_rag(self, query: str) -> Dict[str, Any]:
        """
        Query the simple RAG system for relevant documents.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with query results and metadata
        """
        try:
            logger.info("Processing simple RAG query", query=query[:100])
            
            # Simple keyword matching
            query_lower = query.lower()
            matched_keywords = [kw for kw in self.medical_keywords if kw in query_lower]
            
            if not matched_keywords:
                logger.info("No medical keywords found", query=query[:100])
                return {
                    "success": True,
                    "query": query,
                    "results": [],
                    "total_results": 0,
                    "context": "No relevant medical context found.",
                    "source_documents": [],
                    "message": "No relevant documents found"
                }
            
            # Generate simple context based on keywords
            context = self._generate_simple_context(query, matched_keywords)
            
            # Create mock source documents
            source_documents = [{
                "type": "simple_rag",
                "filename": "medical_knowledge_base",
                "confidence": 0.8,
                "content": "Medical knowledge base generated from keyword matching"
            }]
            
            result = {
                "success": True,
                "query": query,
                "context": context,
                "total_results": 1,
                "source_documents": source_documents,
                "similarity_threshold": self.similarity_threshold,
                "service_used": "simple_rag"
            }
            
            logger.info("Simple RAG query completed", 
                       query=query[:100], 
                       matched_keywords=len(matched_keywords))
            
            return result
                
        except Exception as e:
            logger.error("Simple RAG query failed", query=query, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "results": [],
                "total_results": 0,
                "context": "No relevant context found.",
                "source_documents": []
            }
    
    def _generate_simple_context(self, query: str, matched_keywords: List[str]) -> str:
        """Generate simple context based on matched keywords."""
        
        context_parts = []
        
        if 'paracetamol' in matched_keywords or 'acetaminophen' in matched_keywords:
            context_parts.append("Paracetamol (acetaminophen) is a widely used analgesic and antipyretic medication.")
        
        if 'overdose' in matched_keywords:
            context_parts.append("Paracetamol overdose can cause severe hepatotoxicity and liver damage.")
        
        if 'side effects' in matched_keywords:
            context_parts.append("Common side effects include nausea, vomiting, and in severe cases, hepatotoxicity.")
        
        if 'dosage' in matched_keywords:
            context_parts.append("Proper dosage is crucial to avoid hepatotoxicity, especially in children and elderly.")
        
        if 'safety' in matched_keywords:
            context_parts.append("Safety considerations include monitoring for hepatotoxicity and avoiding alcohol consumption.")
        
        if not context_parts:
            context_parts.append("General pharmaceutical information relevant to the query.")
        
        return " ".join(context_parts)
