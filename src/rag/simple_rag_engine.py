"""
Simple RAG Engine for MIRAGE v2
==============================
Version simplifiée pour éviter les erreurs de segmentation
"""

class SimpleRAGEngine:
    """Simple RAG engine"""
    
    def __init__(self):
        self.documents = []
        self.embeddings = []
    
    def get_context(self, query: str, max_results: int = 5) -> list:
        """Get context for query"""
        # Simple implementation - return empty context
        return []
    
    def add_document(self, document: dict):
        """Add document to RAG engine"""
        self.documents.append(document)
    
    def clear_documents(self):
        """Clear all documents"""
        self.documents = []
        self.embeddings = []
    
    def get_document_count(self) -> int:
        """Get document count"""
        return len(self.documents)