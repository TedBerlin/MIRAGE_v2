"""
Document processing module for MIRAGE v2.

Handles document ingestion, validation, and chunking with comprehensive metadata.
"""

import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import structlog

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_core.documents import Document

logger = structlog.get_logger(__name__)


class DocumentProcessor:
    """Processes documents with validation and comprehensive metadata."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_file_size: int = 100,  # bytes
        max_file_size: int = 50 * 1024 * 1024,  # 50MB
        allowed_extensions: List[str] = [".txt", ".pdf", ".md", ".docx"]
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_file_size = min_file_size
        self.max_file_size = max_file_size
        self.allowed_extensions = allowed_extensions
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        logger.info(
            "DocumentProcessor initialized",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_file_size=max_file_size
        )
    
    def validate_document(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Validate document before processing.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if file exists
            if not file_path.exists():
                return False, f"File does not exist: {file_path}"
            
            # Check file extension
            if file_path.suffix.lower() not in self.allowed_extensions:
                return False, f"Unsupported file type: {file_path.suffix}"
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size < self.min_file_size:
                return False, f"File too small: {file_size} bytes (min: {self.min_file_size})"
            
            if file_size > self.max_file_size:
                return False, f"File too large: {file_size} bytes (max: {self.max_file_size})"
            
            return True, None
            
        except Exception as e:
            logger.error("Document validation failed", file_path=str(file_path), error=str(e))
            return False, f"Validation error: {str(e)}"
    
    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from document.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Dictionary with metadata
        """
        try:
            stat = file_path.stat()
            
            # Calculate file hash for deduplication
            file_hash = self._calculate_file_hash(file_path)
            
            metadata = {
                "document_id": file_hash,
                "filename": file_path.name,
                "file_path": str(file_path),
                "file_size": stat.st_size,
                "file_type": file_path.suffix.lower(),
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "processed_time": datetime.now().isoformat(),
                "version": "1.0",
                "author": "MIRAGE System",
                "document_type": self._infer_document_type(file_path),
                "language": "en",  # Default to English, scalable for future
                "source": "pharmaceutical_research",
                "confidentiality": "internal",
                "tags": self._extract_tags(file_path),
                "checksum": file_hash
            }
            
            logger.info("Metadata extracted", document_id=file_hash, filename=file_path.name)
            return metadata
            
        except Exception as e:
            logger.error("Metadata extraction failed", file_path=str(file_path), error=str(e))
            return {}
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _infer_document_type(self, file_path: Path) -> str:
        """Infer document type from filename and content."""
        filename_lower = file_path.name.lower()
        
        if "clinical" in filename_lower or "trial" in filename_lower:
            return "clinical_trial"
        elif "pharmaceutical" in filename_lower or "drug" in filename_lower:
            return "pharmaceutical_guide"
        elif "interaction" in filename_lower:
            return "drug_interaction"
        elif "cancer" in filename_lower or "oncology" in filename_lower:
            return "oncology_research"
        else:
            return "research_document"
    
    def _extract_tags(self, file_path: Path) -> List[str]:
        """Extract relevant tags from filename."""
        filename_lower = file_path.name.lower()
        tags = []
        
        # Medical domain tags
        if any(word in filename_lower for word in ["cancer", "oncology", "tumor"]):
            tags.append("oncology")
        if any(word in filename_lower for word in ["clinical", "trial", "study"]):
            tags.append("clinical_research")
        if any(word in filename_lower for word in ["drug", "pharmaceutical", "medication"]):
            tags.append("pharmaceutical")
        if any(word in filename_lower for word in ["interaction", "combination"]):
            tags.append("drug_interactions")
        
        # Document type tags
        if file_path.suffix.lower() == ".pdf":
            tags.append("pdf")
        elif file_path.suffix.lower() == ".txt":
            tags.append("text")
        
        return tags
    
    def load_document(self, file_path: Path) -> List[Document]:
        """
        Load document using appropriate loader.
        
        Args:
            file_path: Path to the document
            
        Returns:
            List of Document objects
        """
        try:
            if file_path.suffix.lower() == ".pdf":
                loader = PyPDFLoader(str(file_path))
            elif file_path.suffix.lower() in [".txt", ".md"]:
                loader = TextLoader(str(file_path), encoding="utf-8")
            else:
                raise ValueError(f"Unsupported file type: {file_path.suffix}")
            
            documents = loader.load()
            logger.info("Document loaded", file_path=str(file_path), pages=len(documents))
            return documents
            
        except Exception as e:
            logger.error("Document loading failed", file_path=str(file_path), error=str(e))
            return []
    
    def process_document(self, file_path: Path) -> Tuple[List[Document], Dict[str, Any]]:
        """
        Process document with validation, metadata extraction, and chunking.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Tuple of (chunked_documents, metadata)
        """
        # Validate document
        is_valid, error_msg = self.validate_document(file_path)
        if not is_valid:
            logger.error("Document validation failed", file_path=str(file_path), error=error_msg)
            return [], {}
        
        # Extract metadata
        metadata = self.extract_metadata(file_path)
        if not metadata:
            logger.error("Metadata extraction failed", file_path=str(file_path))
            return [], {}
        
        # Load document
        documents = self.load_document(file_path)
        if not documents:
            logger.error("Document loading failed", file_path=str(file_path))
            return [], {}
        
        # Add metadata to each document
        for doc in documents:
            doc.metadata.update(metadata)
            doc.metadata["chunk_id"] = abs(hash(f"{metadata['document_id']}_{doc.page_content}")) % 1000000000
        
        # Split into chunks
        chunked_documents = self.text_splitter.split_documents(documents)
        
        # Add chunk-specific metadata
        for i, chunk in enumerate(chunked_documents):
            chunk.metadata.update({
                "chunk_index": i,
                "total_chunks": len(chunked_documents),
                "chunk_size": len(chunk.page_content)
            })
        
        logger.info(
            "Document processed successfully",
            file_path=str(file_path),
            chunks=len(chunked_documents),
            document_id=metadata["document_id"]
        )
        
        return chunked_documents, metadata
    
    def process_directory(self, directory_path: Path) -> Tuple[List[Document], List[Dict[str, Any]]]:
        """
        Process all valid documents in a directory.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            Tuple of (all_chunked_documents, all_metadata)
        """
        all_documents = []
        all_metadata = []
        
        if not directory_path.exists() or not directory_path.is_dir():
            logger.error("Directory does not exist", directory_path=str(directory_path))
            return all_documents, all_metadata
        
        # Find all valid files
        valid_files = []
        for file_path in directory_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.allowed_extensions:
                is_valid, _ = self.validate_document(file_path)
                if is_valid:
                    valid_files.append(file_path)
        
        logger.info("Found valid files", directory=str(directory_path), count=len(valid_files))
        
        # Process each file
        for file_path in valid_files:
            try:
                documents, metadata = self.process_document(file_path)
                all_documents.extend(documents)
                all_metadata.append(metadata)
            except Exception as e:
                logger.error("Failed to process file", file_path=str(file_path), error=str(e))
                continue
        
        logger.info(
            "Directory processing completed",
            directory=str(directory_path),
            files_processed=len(all_metadata),
            total_chunks=len(all_documents)
        )
        
        return all_documents, all_metadata
    
    def process_documents(self, directory_path: str) -> Tuple[List[Document], List[Dict[str, Any]]]:
        """
        Process all documents in a directory.
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            Tuple of (documents, metadata_list)
        """
        return self.process_directory(Path(directory_path))
