#!/usr/bin/env python3
"""
Gestionnaire RAG Avancé pour MIRAGE v2
Gestion transparente avec prise en compte immédiate
"""

import os
import time
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class AdvancedRAGManager:
    """
    Gestionnaire RAG avancé avec prise en compte immédiate
    """
    
    def __init__(self):
        self.documents = {}
        self.chunks = {}
        self.embeddings = {}
        self.metadata = {}
        self.vector_index = {}
        self.last_update = None
        
        logger.info("✅ AdvancedRAGManager initialized")
    
    def add_document(self, document_path: str, content: str, metadata: Dict = None) -> Dict[str, Any]:
        """
        Ajout de document avec traitement immédiat
        """
        try:
            # Génération ID unique
            doc_id = hashlib.md5(f"{document_path}_{time.time()}".encode()).hexdigest()
            
            # Traitement immédiat
            chunks = self._process_document(content)
            embeddings = self._generate_embeddings(chunks)
            
            # Stockage
            self.documents[doc_id] = {
                "path": document_path,
                "content": content,
                "chunks": chunks,
                "embeddings": embeddings,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
                "status": "processed"
            }
            
            # Indexation immédiate
            self._index_document(doc_id, chunks, embeddings)
            
            logger.info(f"✅ Document ajouté: {document_path} ({len(chunks)} chunks)")
            
            return {
                "success": True,
                "document_id": doc_id,
                "chunks_count": len(chunks),
                "status": "processed",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur ajout document: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _process_document(self, content: str) -> List[str]:
        """
        Traitement de document en chunks
        """
        # Chunking intelligent
        sentences = content.split('. ')
        chunks = []
        
        for sentence in sentences:
            if len(sentence.strip()) > 10:  # Chunks significatifs
                chunks.append(sentence.strip())
        
        # Chunking par paragraphe si nécessaire
        if len(chunks) < 3:
            paragraphs = content.split('\n\n')
            chunks = [p.strip() for p in paragraphs if len(p.strip()) > 20]
        
        return chunks
    
    def _generate_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """
        Génération d'embeddings simplifiés
        """
        embeddings = []
        
        for chunk in chunks:
            # Embedding simplifié basé sur les mots-clés
            embedding = self._simple_embedding(chunk)
            embeddings.append(embedding)
        
        return embeddings
    
    def _simple_embedding(self, text: str) -> List[float]:
        """
        Embedding simplifié basé sur les mots-clés médicaux
        """
        text_lower = text.lower()
        
        # Mots-clés médicaux avec poids
        medical_keywords = {
            'safety': 0.9, 'approved': 0.8, 'fda': 0.9, 'side effects': 0.9,
            'pregnancy': 0.8, 'children': 0.7, 'dosage': 0.6, 'contraindications': 0.9,
            'interactions': 0.8, 'allergies': 0.8, 'elderly': 0.7, 'insufficiency': 0.8,
            'renal': 0.7, 'hepatic': 0.7, 'cardiac': 0.7, 'respiratory': 0.6,
            'digestive': 0.6, 'neurological': 0.7, 'psychiatric': 0.7,
            'dermatological': 0.6, 'ophthalmological': 0.6, 'urological': 0.6,
            'gynecological': 0.6, 'pediatric': 0.7, 'geriatric': 0.7,
            'emergency': 0.8, 'intensive care': 0.8, 'resuscitation': 0.8,
            'surgery': 0.7, 'anesthesia': 0.7, 'radiology': 0.6, 'laboratory': 0.6,
            'analyses': 0.6, 'examinations': 0.6, 'balance': 0.5, 'follow-up': 0.6,
            'monitoring': 0.7, 'evaluation': 0.6, 'efficacy': 0.7, 'tolerance': 0.7,
            'safety': 0.9, 'quality': 0.6, 'cost': 0.4, 'reimbursement': 0.5,
            'insurance': 0.5, 'mutual': 0.4, 'social security': 0.4
        }
        
        # Génération embedding basé sur les mots-clés
        embedding = [0.0] * 50  # Embedding de 50 dimensions
        
        for i, (keyword, weight) in enumerate(medical_keywords.items()):
            if keyword in text_lower:
                embedding[i % 50] += weight
        
        # Normalisation
        norm = sum(x**2 for x in embedding)**0.5
        if norm > 0:
            embedding = [x/norm for x in embedding]
        
        return embedding
    
    def _index_document(self, doc_id: str, chunks: List[str], embeddings: List[List[float]]):
        """
        Indexation immédiate du document
        """
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{doc_id}_chunk_{i}"
            
            self.chunks[chunk_id] = {
                "document_id": doc_id,
                "content": chunk,
                "embedding": embedding,
                "index": i,
                "timestamp": datetime.now().isoformat()
            }
            
            # Index vectoriel simplifié
            self.vector_index[chunk_id] = embedding
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Recherche de similarité avec prise en compte immédiate
        """
        try:
            # Embedding de la requête
            query_embedding = self._simple_embedding(query)
            
            # Calcul de similarité
            similarities = []
            
            for chunk_id, chunk_embedding in self.vector_index.items():
                similarity = self._cosine_similarity(query_embedding, chunk_embedding)
                similarities.append({
                    "chunk_id": chunk_id,
                    "similarity": similarity,
                    "content": self.chunks[chunk_id]["content"],
                    "document_id": self.chunks[chunk_id]["document_id"]
                })
            
            # Tri par similarité
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche: {str(e)}")
            return []
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """
        Calcul de similarité cosinus
        """
        if len(a) != len(b):
            return 0.0
        
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x**2 for x in a)**0.5
        norm_b = sum(x**2 for x in b)**0.5
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def get_document_stats(self) -> Dict[str, Any]:
        """
        Statistiques des documents
        """
        total_documents = len(self.documents)
        total_chunks = len(self.chunks)
        total_embeddings = len(self.vector_index)
        
        return {
            "total_documents": total_documents,
            "total_chunks": total_chunks,
            "total_embeddings": total_embeddings,
            "last_update": self.last_update,
            "status": "active"
        }
    
    def clear_all(self):
        """
        Nettoyage complet
        """
        self.documents.clear()
        self.chunks.clear()
        self.embeddings.clear()
        self.vector_index.clear()
        self.last_update = None
        
        logger.info("✅ RAG Manager nettoyé")

# Instance globale
rag_manager = AdvancedRAGManager()

# Test immédiat
if __name__ == "__main__":
    print("🧪 TEST DU GESTIONNAIRE RAG AVANCÉ")
    print("=" * 50)
    
    # Test d'ajout de document
    test_content = """
    Ce médicament est approuvé par la FDA pour le traitement de l'hypertension.
    Les effets secondaires incluent des maux de tête et des nausées.
    Contre-indications: grossesse et allaitement.
    Surveillance requise chez les patients âgés.
    """
    
    result = rag_manager.add_document("test_doc.pdf", test_content)
    print(f"✅ Document ajouté: {result}")
    
    # Test de recherche
    search_results = rag_manager.search_similar("effets secondaires", top_k=3)
    print(f"✅ Recherche: {len(search_results)} résultats")
    
    for result in search_results:
        print(f"   - {result['content'][:50]}... (similarité: {result['similarity']:.3f})")
    
    # Statistiques
    stats = rag_manager.get_document_stats()
    print(f"✅ Stats: {stats}")
