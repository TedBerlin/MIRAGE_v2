"""
Embedding management module for MIRAGE v2.

Handles vector embeddings generation and storage using sentence-transformers.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import structlog
import numpy as np

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

logger = structlog.get_logger(__name__)


class EmbeddingManager:
    """Manages vector embeddings with ChromaDB storage."""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        db_path: str = "./data/embeddings",
        collection_name: str = "mirage_documents"
    ):
        self.model_name = model_name
        self.db_path = db_path
        self.collection_name = collection_name
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(model_name)
        
        # Initialize ChromaDB
        self._init_chromadb()
        
        logger.info(
            "EmbeddingManager initialized",
            model=model_name,
            db_path=db_path,
            collection=collection_name
        )
    
    def _init_chromadb(self):
        """Initialize ChromaDB client and collection."""
        try:
            # Ensure directory exists
            Path(self.db_path).mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            try:
                self.collection = self.chroma_client.get_collection(
                    name=self.collection_name
                )
                logger.info("Existing collection loaded", collection=self.collection_name)
            except Exception:
                self.collection = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "MIRAGE v2 document embeddings"}
                )
                logger.info("New collection created", collection=self.collection_name)
                
        except Exception as e:
            logger.error("ChromaDB initialization failed", error=str(e))
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
            logger.info("Embeddings generated", count=len(texts), dimension=len(embeddings[0]))
            return embeddings.tolist()
            
        except Exception as e:
            logger.error("Embedding generation failed", error=str(e))
            raise
    
    def store_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> bool:
        """
        Store documents and embeddings in ChromaDB.
        
        Args:
            documents: List of document dictionaries with metadata
            embeddings: List of embedding vectors
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if len(documents) != len(embeddings):
                raise ValueError("Documents and embeddings count mismatch")
            
            # Prepare data for ChromaDB
            ids = [doc["chunk_id"] for doc in documents]
            texts = [doc["content"] for doc in documents]
            metadatas = [
                {
                    k: v for k, v in doc.items() 
                    if k not in ["chunk_id", "content"] and isinstance(v, (str, int, float, bool))
                }
                for doc in documents
            ]
            
            # Store in ChromaDB
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info("Documents stored in ChromaDB", count=len(documents))
            return True
            
        except Exception as e:
            logger.error("Document storage failed", error=str(e))
            return False
    
    def search_similar(
        self,
        query: str,
        n_results: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query: Search query
            n_results: Number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar documents with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embeddings([query])[0]
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Process results
            similar_docs = []
            for i in range(len(results["ids"][0])):
                # Convert distance to similarity score (ChromaDB uses distance, we want similarity)
                distance = results["distances"][0][i]
                similarity = 1 - distance  # Convert distance to similarity
                
                if similarity >= similarity_threshold:
                    doc = {
                        "chunk_id": results["ids"][0][i],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity_score": similarity,
                        "distance": distance
                    }
                    similar_docs.append(doc)
            
            logger.info(
                "Similarity search completed",
                query=query[:100],
                results_found=len(similar_docs),
                threshold=similarity_threshold
            )
            
            return similar_docs
            
        except Exception as e:
            logger.error("Similarity search failed", query=query, error=str(e))
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        try:
            count = self.collection.count()
            
            # Get sample metadata to understand structure
            sample = self.collection.get(limit=1, include=["metadatas"])
            metadata_keys = set()
            if sample["metadatas"]:
                metadata_keys = set(sample["metadatas"][0].keys())
            
            stats = {
                "total_documents": count,
                "collection_name": self.collection_name,
                "embedding_model": self.model_name,
                "metadata_fields": list(metadata_keys),
                "db_path": self.db_path
            }
            
            logger.info("Collection stats retrieved", stats=stats)
            return stats
            
        except Exception as e:
            logger.error("Failed to get collection stats", error=str(e))
            return {}
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the collection.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.collection.delete(ids=[document_id])
            logger.info("Document deleted", document_id=document_id)
            return True
            
        except Exception as e:
            logger.error("Document deletion failed", document_id=document_id, error=str(e))
            return False
    
    def reset_collection(self) -> bool:
        """Reset the entire collection (use with caution)."""
        try:
            self.chroma_client.delete_collection(name=self.collection_name)
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "MIRAGE v2 document embeddings"}
            )
            logger.warning("Collection reset completed", collection=self.collection_name)
            return True
            
        except Exception as e:
            logger.error("Collection reset failed", error=str(e))
            return False
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding model."""
        try:
            # Generate a test embedding to get dimension
            test_embedding = self.generate_embeddings(["test"])[0]
            return len(test_embedding)
        except Exception as e:
            logger.error("Failed to get embedding dimension", error=str(e))
            return 0
