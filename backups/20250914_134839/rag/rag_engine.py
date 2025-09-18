"""
Main RAG engine for MIRAGE v2.

Orchestrates document processing, embedding generation, and retrieval.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import structlog

from .document_processor import DocumentProcessor
from .embedding_manager import EmbeddingManager
from .metadata_manager import MetadataManager

logger = structlog.get_logger(__name__)


class RAGEngine:
    """Main RAG engine orchestrating all components."""
    
    def __init__(
        self,
        documents_path: str = "./data/raw_documents",
        embeddings_path: str = "./data/embeddings",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embedding_model: str = "all-MiniLM-L6-v2",
        max_results: int = 5,
        similarity_threshold: float = 0.7
    ):
        self.documents_path = Path(documents_path)
        self.embeddings_path = embeddings_path
        self.max_results = max_results
        self.similarity_threshold = similarity_threshold
        
        # Initialize components
        self.document_processor = DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        self.embedding_manager = EmbeddingManager(
            model_name=embedding_model,
            db_path=embeddings_path
        )
        
        self.metadata_manager = MetadataManager()
        
        logger.info(
            "RAGEngine initialized",
            documents_path=str(self.documents_path),
            embeddings_path=embeddings_path,
            chunk_size=chunk_size,
            embedding_model=embedding_model
        )
    
    def ingest_documents(self, force_reprocess: bool = False) -> Dict[str, Any]:
        """
        Ingest all documents from the documents directory.
        
        Args:
            force_reprocess: Whether to reprocess existing documents
            
        Returns:
            Dictionary with ingestion results
        """
        try:
            logger.info("Starting document ingestion", force_reprocess=force_reprocess)
            
            # Check if documents directory exists
            if not self.documents_path.exists():
                logger.error("Documents directory does not exist", path=str(self.documents_path))
                return {"success": False, "error": "Documents directory not found"}
            
            # Process all documents in directory
            documents, metadata_list = self.document_processor.process_directory(
                self.documents_path
            )
            
            if not documents:
                logger.warning("No documents found to process")
                return {"success": True, "documents_processed": 0, "chunks_created": 0}
            
            # Convert documents to format expected by embedding manager
            doc_dicts = []
            for doc in documents:
                doc_dict = {
                    "chunk_id": doc.metadata["chunk_id"],
                    "content": doc.page_content,
                    **doc.metadata
                }
                doc_dicts.append(doc_dict)
            
            # Generate embeddings
            texts = [doc["content"] for doc in doc_dicts]
            embeddings = self.embedding_manager.generate_embeddings(texts)
            
            # Store in vector database
            success = self.embedding_manager.store_documents(doc_dicts, embeddings)
            
            if success:
                # Store metadata
                self.metadata_manager.store_metadata(metadata_list)
                
                result = {
                    "success": True,
                    "documents_processed": len(metadata_list),
                    "chunks_created": len(documents),
                    "embeddings_generated": len(embeddings),
                    "metadata": metadata_list
                }
                
                logger.info(
                    "Document ingestion completed successfully",
                    documents=len(metadata_list),
                    chunks=len(documents)
                )
                
                return result
            else:
                logger.error("Failed to store documents in vector database")
                return {"success": False, "error": "Failed to store documents"}
                
        except Exception as e:
            logger.error("Document ingestion failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    def query_rag(self, query: str) -> Dict[str, Any]:
        """
        Query the RAG system for relevant documents.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with query results and metadata
        """
        try:
            logger.info("Processing RAG query", query=query[:100])
            
            # Search for similar documents
            similar_docs = self.embedding_manager.search_similar(
                query=query,
                n_results=self.max_results,
                similarity_threshold=self.similarity_threshold
            )
            
            if not similar_docs:
                logger.info("No similar documents found", query=query[:100])
                return {
                    "success": True,
                    "query": query,
                    "results": [],
                    "total_results": 0,
                    "message": "No relevant documents found"
                }
            
            # Format results
            formatted_results = []
            for doc in similar_docs:
                result = {
                    "chunk_id": doc["chunk_id"],
                    "content": doc["content"],
                    "similarity_score": doc["similarity_score"],
                    "metadata": doc["metadata"]
                }
                formatted_results.append(result)
            
            # Get context from results
            context = "\n\n".join([doc["content"] for doc in similar_docs])
            
            # Get unique source documents
            source_documents = list(set([
                doc["metadata"].get("filename", "unknown") 
                for doc in similar_docs
            ]))
            
            result = {
                "success": True,
                "query": query,
                "results": formatted_results,
                "total_results": len(formatted_results),
                "context": context,
                "source_documents": source_documents,
                "similarity_threshold": self.similarity_threshold,
                "max_results": self.max_results
            }
            
            logger.info(
                "RAG query completed",
                query=query[:100],
                results_found=len(formatted_results),
                sources=len(source_documents)
            )
            
            return result
            
        except Exception as e:
            logger.error("RAG query failed", query=query, error=str(e))
            return {
                "success": False,
                "query": query,
                "error": str(e)
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        try:
            # Get embedding manager stats
            embedding_stats = self.embedding_manager.get_collection_stats()
            
            # Get metadata stats
            metadata_stats = self.metadata_manager.get_stats()
            
            # Get document directory stats
            doc_files = list(self.documents_path.glob("*"))
            doc_files = [f for f in doc_files if f.is_file() and f.suffix.lower() in [".txt", ".pdf", ".md", ".docx"]]
            
            stats = {
                "rag_engine": {
                    "documents_path": str(self.documents_path),
                    "embeddings_path": self.embeddings_path,
                    "max_results": self.max_results,
                    "similarity_threshold": self.similarity_threshold
                },
                "documents": {
                    "total_files": len(doc_files),
                    "files": [f.name for f in doc_files]
                },
                "embeddings": embedding_stats,
                "metadata": metadata_stats
            }
            
            logger.info("System stats retrieved", stats=stats)
            return stats
            
        except Exception as e:
            logger.error("Failed to get system stats", error=str(e))
            return {"error": str(e)}
    
    def add_document(self, file_path: Path) -> Dict[str, Any]:
        """
        Add a single document to the RAG system.
        
        Args:
            file_path: Path to the document to add
            
        Returns:
            Dictionary with addition results
        """
        try:
            logger.info("Adding single document", file_path=str(file_path))
            
            # Process document
            documents, metadata = self.document_processor.process_document(file_path)
            
            if not documents:
                return {"success": False, "error": "Failed to process document"}
            
            # Convert to format expected by embedding manager
            doc_dicts = []
            for doc in documents:
                doc_dict = {
                    "chunk_id": doc.metadata["chunk_id"],
                    "content": doc.page_content,
                    **doc.metadata
                }
                doc_dicts.append(doc_dict)
            
            # Generate embeddings
            texts = [doc["content"] for doc in doc_dicts]
            embeddings = self.embedding_manager.generate_embeddings(texts)
            
            # Store in vector database
            success = self.embedding_manager.store_documents(doc_dicts, embeddings)
            
            if success:
                # Store metadata
                self.metadata_manager.store_metadata([metadata])
                
                result = {
                    "success": True,
                    "document_id": metadata["document_id"],
                    "chunks_created": len(documents),
                    "metadata": metadata
                }
                
                logger.info("Document added successfully", document_id=metadata["document_id"])
                return result
            else:
                return {"success": False, "error": "Failed to store document"}
                
        except Exception as e:
            logger.error("Failed to add document", file_path=str(file_path), error=str(e))
            return {"success": False, "error": str(e)}
    
    def remove_document(self, document_id: str) -> bool:
        """
        Remove a document from the RAG system.
        
        Args:
            document_id: ID of the document to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove from vector database
            success = self.embedding_manager.delete_document(document_id)
            
            if success:
                # Remove from metadata
                self.metadata_manager.remove_metadata(document_id)
                logger.info("Document removed successfully", document_id=document_id)
            
            return success
            
        except Exception as e:
            logger.error("Failed to remove document", document_id=document_id, error=str(e))
            return False
