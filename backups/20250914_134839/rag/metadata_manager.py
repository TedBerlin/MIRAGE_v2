"""
Metadata management module for MIRAGE v2.

Handles storage and retrieval of document metadata with comprehensive tracking.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


class MetadataManager:
    """Manages document metadata storage and retrieval."""
    
    def __init__(self, metadata_path: str = "./data/processed/metadata.json"):
        self.metadata_path = Path(metadata_path)
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing metadata
        self.metadata = self._load_metadata()
        
        logger.info("MetadataManager initialized", metadata_path=str(self.metadata_path))
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata from file."""
        try:
            if self.metadata_path.exists():
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                logger.info("Metadata loaded from file", count=len(metadata.get("documents", {})))
                return metadata
            else:
                # Initialize empty metadata structure
                return {
                    "version": "1.0",
                    "created_time": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "documents": {},
                    "statistics": {
                        "total_documents": 0,
                        "total_chunks": 0,
                        "total_size_bytes": 0,
                        "document_types": {},
                        "languages": {},
                        "sources": {}
                    }
                }
        except Exception as e:
            logger.error("Failed to load metadata", error=str(e))
            return {
                "version": "1.0",
                "created_time": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "documents": {},
                "statistics": {
                    "total_documents": 0,
                    "total_chunks": 0,
                    "total_size_bytes": 0,
                    "document_types": {},
                    "languages": {},
                    "sources": {}
                }
            }
    
    def _save_metadata(self) -> bool:
        """Save metadata to file."""
        try:
            self.metadata["last_updated"] = datetime.now().isoformat()
            
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            
            logger.info("Metadata saved to file", path=str(self.metadata_path))
            return True
            
        except Exception as e:
            logger.error("Failed to save metadata", error=str(e))
            return False
    
    def store_metadata(self, metadata_list: List[Dict[str, Any]]) -> bool:
        """
        Store metadata for multiple documents.
        
        Args:
            metadata_list: List of metadata dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for metadata in metadata_list:
                document_id = metadata.get("document_id")
                if not document_id:
                    logger.warning("Metadata missing document_id", metadata=metadata)
                    continue
                
                # Store document metadata
                self.metadata["documents"][document_id] = metadata
                
                # Update statistics
                self._update_statistics(metadata)
            
            # Save to file
            success = self._save_metadata()
            
            if success:
                logger.info("Metadata stored successfully", count=len(metadata_list))
            
            return success
            
        except Exception as e:
            logger.error("Failed to store metadata", error=str(e))
            return False
    
    def _update_statistics(self, metadata: Dict[str, Any]):
        """Update statistics based on new metadata."""
        try:
            stats = self.metadata["statistics"]
            
            # Update total documents
            stats["total_documents"] = len(self.metadata["documents"])
            
            # Update total size
            file_size = metadata.get("file_size", 0)
            stats["total_size_bytes"] = sum(
                doc.get("file_size", 0) 
                for doc in self.metadata["documents"].values()
            )
            
            # Update document types
            doc_type = metadata.get("document_type", "unknown")
            stats["document_types"][doc_type] = stats["document_types"].get(doc_type, 0) + 1
            
            # Update languages
            language = metadata.get("language", "unknown")
            stats["languages"][language] = stats["languages"].get(language, 0) + 1
            
            # Update sources
            source = metadata.get("source", "unknown")
            stats["sources"][source] = stats["sources"].get(source, 0) + 1
            
        except Exception as e:
            logger.error("Failed to update statistics", error=str(e))
    
    def get_metadata(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Metadata dictionary or None if not found
        """
        try:
            metadata = self.metadata["documents"].get(document_id)
            if metadata:
                logger.info("Metadata retrieved", document_id=document_id)
            else:
                logger.warning("Metadata not found", document_id=document_id)
            return metadata
            
        except Exception as e:
            logger.error("Failed to get metadata", document_id=document_id, error=str(e))
            return None
    
    def get_all_metadata(self) -> Dict[str, Any]:
        """Get all stored metadata."""
        try:
            return self.metadata.copy()
        except Exception as e:
            logger.error("Failed to get all metadata", error=str(e))
            return {}
    
    def remove_metadata(self, document_id: str) -> bool:
        """
        Remove metadata for a specific document.
        
        Args:
            document_id: ID of the document to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if document_id in self.metadata["documents"]:
                # Get metadata for statistics update
                metadata = self.metadata["documents"][document_id]
                
                # Remove from documents
                del self.metadata["documents"][document_id]
                
                # Update statistics
                self._recalculate_statistics()
                
                # Save to file
                success = self._save_metadata()
                
                if success:
                    logger.info("Metadata removed successfully", document_id=document_id)
                
                return success
            else:
                logger.warning("Document not found in metadata", document_id=document_id)
                return False
                
        except Exception as e:
            logger.error("Failed to remove metadata", document_id=document_id, error=str(e))
            return False
    
    def _recalculate_statistics(self):
        """Recalculate all statistics from stored documents."""
        try:
            stats = {
                "total_documents": 0,
                "total_chunks": 0,
                "total_size_bytes": 0,
                "document_types": {},
                "languages": {},
                "sources": {}
            }
            
            for doc_metadata in self.metadata["documents"].values():
                stats["total_documents"] += 1
                stats["total_size_bytes"] += doc_metadata.get("file_size", 0)
                
                # Document types
                doc_type = doc_metadata.get("document_type", "unknown")
                stats["document_types"][doc_type] = stats["document_types"].get(doc_type, 0) + 1
                
                # Languages
                language = doc_metadata.get("language", "unknown")
                stats["languages"][language] = stats["languages"].get(language, 0) + 1
                
                # Sources
                source = doc_metadata.get("source", "unknown")
                stats["sources"][source] = stats["sources"].get(source, 0) + 1
            
            self.metadata["statistics"] = stats
            
        except Exception as e:
            logger.error("Failed to recalculate statistics", error=str(e))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        try:
            return self.metadata.get("statistics", {}).copy()
        except Exception as e:
            logger.error("Failed to get stats", error=str(e))
            return {}
    
    def search_metadata(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search metadata with filters.
        
        Args:
            filters: Dictionary of filters to apply
            
        Returns:
            List of matching metadata
        """
        try:
            results = []
            
            for doc_id, metadata in self.metadata["documents"].items():
                if self._matches_filters(metadata, filters):
                    results.append(metadata)
            
            logger.info("Metadata search completed", filters=filters, results=len(results))
            return results
            
        except Exception as e:
            logger.error("Metadata search failed", filters=filters, error=str(e))
            return []
    
    def _matches_filters(self, metadata: Dict[str, Any], filters: Optional[Dict[str, Any]]) -> bool:
        """Check if metadata matches the given filters."""
        if not filters:
            return True
        
        try:
            for key, value in filters.items():
                if key not in metadata:
                    return False
                
                if isinstance(value, list):
                    if metadata[key] not in value:
                        return False
                else:
                    if metadata[key] != value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error("Filter matching failed", error=str(e))
            return False
    
    def get_documents_by_type(self, document_type: str) -> List[Dict[str, Any]]:
        """Get all documents of a specific type."""
        return self.search_metadata({"document_type": document_type})
    
    def get_documents_by_language(self, language: str) -> List[Dict[str, Any]]:
        """Get all documents in a specific language."""
        return self.search_metadata({"language": language})
    
    def get_documents_by_source(self, source: str) -> List[Dict[str, Any]]:
        """Get all documents from a specific source."""
        return self.search_metadata({"source": source})
    
    def export_metadata(self, export_path: str) -> bool:
        """
        Export metadata to a file.
        
        Args:
            export_path: Path to export file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            
            logger.info("Metadata exported successfully", export_path=str(export_path))
            return True
            
        except Exception as e:
            logger.error("Failed to export metadata", export_path=export_path, error=str(e))
            return False
