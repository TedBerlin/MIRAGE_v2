"""
Embedding management module for MIRAGE v2.

Handles vector embeddings generation and storage using sentence-transformers with QDrant.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import structlog
import numpy as np

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

logger = structlog.get_logger(__name__)


class EmbeddingManager:
    """Manages vector embeddings with QDrant storage."""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        db_path: str = "./data/qdrant_db",
        collection_name: str = "mirage_documents"
    ):
        self.model_name = model_name
        self.db_path = db_path
        self.collection_name = collection_name
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(model_name)
        
        # Initialize QDrant
        self._init_qdrant()
        
        logger.info(
            "EmbeddingManager initialized",
            model=model_name,
            db_path=db_path,
            collection=collection_name
        )
    
    def _init_qdrant(self):
        """Initialize QDrant client and collection."""
        try:
            # Ensure directory exists
            Path(self.db_path).mkdir(parents=True, exist_ok=True)
            
            # Initialize QDrant client with unique path to avoid conflicts
            import time
            unique_path = f"{self.db_path}_{int(time.time())}"
            self.qdrant_client = QdrantClient(path=unique_path)
            
            # Get or create collection
            try:
                # Check if collection exists
                collections = self.qdrant_client.get_collections()
                collection_exists = any(col.name == self.collection_name for col in collections.collections)
                
                if collection_exists:
                    logger.info("Existing collection loaded", collection=self.collection_name)
                else:
                    # Create collection with vector size from embedding model
                    vector_size = self.embedding_model.get_sentence_embedding_dimension()
                    self.qdrant_client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
                    )
                    logger.info("New collection created", collection=self.collection_name, vector_size=vector_size)
            except Exception as e:
                logger.error("Collection creation/loading failed", error=str(e))
                raise
        except Exception as e:
            logger.error("QDrant initialization failed", error=str(e))
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
        Store documents and embeddings in QDrant.
        
        Args:
            documents: List of document dictionaries with metadata
            embeddings: List of embedding vectors
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if len(documents) != len(embeddings):
                raise ValueError("Documents and embeddings count mismatch")
            
            # Prepare data for QDrant
            points = []
            for i, doc in enumerate(documents):
                point = PointStruct(
                    id=doc["chunk_id"],
                    vector=embeddings[i],
                    payload={
                        "content": doc["content"],
                        **{k: v for k, v in doc.items() 
                           if k not in ["chunk_id", "content"] and isinstance(v, (str, int, float, bool))}
                    }
                )
                points.append(point)
            
            # Store in QDrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info("Documents stored in QDrant", count=len(documents))
            return True
            
        except Exception as e:
            logger.error("Document storage failed", error=str(e))
            return False
    
    def search_similar(
        self,
        query: str,
        n_results: int = 5,
        similarity_threshold: float = 0.3
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
            
            # Search in QDrant
            results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=n_results,
                score_threshold=similarity_threshold
            )
            
            # Process results
            similar_docs = []
            for result in results:
                doc = {
                    "chunk_id": result.id,
                    "content": result.payload.get("content", ""),
                    "metadata": {k: v for k, v in result.payload.items() if k != "content"},
                    "similarity_score": result.score,
                    "distance": 1 - result.score  # Convert similarity to distance
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
        """Get REAL statistics about the collection."""
        try:
            # Get collection info
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            total_chunks = collection_info.points_count
            
            # Count unique documents by scanning document_id in payload
            document_ids = set()
            try:
                # Scroll through all points to count unique documents
                offset = None
                while True:
                    result = self.qdrant_client.scroll(
                        collection_name=self.collection_name,
                        limit=1000,
                        offset=offset,
                        with_payload=True
                    )
                    
                    points, next_offset = result
                    if not points:
                        break
                    
                    for point in points:
                        if point.payload and 'document_id' in point.payload:
                            document_ids.add(point.payload['document_id'])
                    
                    if next_offset is None:
                        break
                    offset = next_offset
                    
            except Exception as e:
                logger.warning("Could not count unique documents", error=str(e))
                # Fallback: estimate documents from chunks
                document_ids = set()
            
            total_documents = len(document_ids) if document_ids else 0
            
            # Get sample points to understand structure
            sample_points = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=1,
                with_payload=True
            )[0]
            
            metadata_keys = set()
            if sample_points:
                payload = sample_points[0].payload
                metadata_keys = set(payload.keys())
            
            stats = {
                "total_documents": total_documents,  # Real document count
                "total_chunks": total_chunks,        # Real chunk count
                "collection_name": self.collection_name,
                "embedding_model": self.model_name,
                "metadata_fields": list(metadata_keys),
                "db_path": self.db_path,
                "vector_size": collection_info.config.params.vectors.size
            }
            
            logger.info("Collection stats retrieved", stats=stats)
            return stats
            
        except Exception as e:
            logger.error("Failed to get collection stats", error=str(e))
            return {"total_documents": 0, "total_chunks": 0}
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the collection.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=[document_id]
            )
            logger.info("Document deleted", document_id=document_id)
            return True
            
        except Exception as e:
            logger.error("Document deletion failed", document_id=document_id, error=str(e))
            return False
    
    def reset_collection(self) -> bool:
        """Reset the entire collection (use with caution)."""
        try:
            self.qdrant_client.delete_collection(collection_name=self.collection_name)
            
            # Recreate collection
            vector_size = self.embedding_model.get_sentence_embedding_dimension()
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
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
