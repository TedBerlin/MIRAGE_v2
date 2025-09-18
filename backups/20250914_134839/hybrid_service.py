#!/usr/bin/env python3
"""
MIRAGE v2 - Service Hybride
Intégration Qdrant + ChromaDB avec fallback vers Gemini direct
"""

import os
import logging
from typing import List, Dict, Any, Optional
import asyncio
import numpy as np
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Gemini
import google.generativeai as genai

# Import Qdrant
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logger.warning("⚠️  qdrant-client non disponible")

class HybridService:
    def __init__(self):
        """Initialisation du service hybride avec Qdrant"""
        self.gemini_model = None
        self.qdrant_client = None
        self.is_chromadb_available = False
        self.is_qdrant_available = False
        self.is_gemini_available = False
        
        # Configuration Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                self.is_gemini_available = True
                logger.info("✅ Gemini configuré avec succès")
            except Exception as e:
                logger.error(f"❌ Erreur configuration Gemini: {e}")
                self.is_gemini_available = False
        else:
            logger.warning("⚠️  GEMINI_API_KEY non trouvée")
            self.is_gemini_available = False
        
        # Vérification Qdrant (priorité)
        self._check_qdrant_availability()
        
        # Vérification ChromaDB (fallback)
        self._check_chromadb_availability()
        
        logger.info(f"🔧 Service hybride initialisé - Qdrant: {self.is_qdrant_available}, ChromaDB: {self.is_chromadb_available}, Gemini: {self.is_gemini_available}")
    
    def _check_qdrant_availability(self):
        """Vérifie si Qdrant est disponible et l'initialise"""
        if not QDRANT_AVAILABLE:
            logger.warning("⚠️  qdrant-client non installé")
            self.is_qdrant_available = False
            return
        
        try:
            # Initialisation Qdrant local
            self.qdrant_client = QdrantClient(path="./data/qdrant_db")
            
            # Test de connexion
            collections = self.qdrant_client.get_collections()
            self.is_qdrant_available = True
            logger.info("✅ Qdrant initialisé avec succès")
            
            # Créer la collection si elle n'existe pas
            self._ensure_collection_exists()
            
        except Exception as e:
            logger.warning(f"⚠️  Qdrant non disponible: {e}")
            self.is_qdrant_available = False
    
    def _ensure_collection_exists(self):
        """S'assure que la collection MIRAGE existe"""
        try:
            collection_name = "mirage_documents"
            collections = self.qdrant_client.get_collections()
            
            if collection_name not in [col.name for col in collections.collections]:
                # Créer la collection avec les paramètres appropriés
                # Utiliser 192 dimensions pour la compatibilité macOS
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=192, distance=Distance.COSINE)  # Compatible macOS
                )
                logger.info(f"✅ Collection '{collection_name}' créée")
            else:
                logger.info(f"✅ Collection '{collection_name}' existe déjà")
                
        except Exception as e:
            logger.error(f"❌ Erreur création collection: {e}")
    
    def _check_chromadb_availability(self):
        """Vérifie si ChromaDB est disponible sans causer de segmentation fault"""
        try:
            # Tentative de vérification sécurisée
            import chromadb
            # Test d'initialisation minimal
            client = chromadb.Client()
            self.is_chromadb_available = True
            logger.info("✅ ChromaDB est disponible")
        except Exception as e:
            logger.warning(f"⚠️  ChromaDB non disponible: {e}. Utilisation du mode Gemini direct.")
            self.is_chromadb_available = False
        
        # Désactiver ChromaDB sur macOS pour éviter les segmentation faults
        import platform
        if platform.system() == "Darwin":  # macOS
            logger.warning("🍎 macOS détecté - ChromaDB désactivé pour éviter les segmentation faults")
            self.is_chromadb_available = False
    
    async def query_with_fallback(self, query: str, context: str = None) -> Dict[str, Any]:
        """
        Query hybride: utilise Qdrant en priorité, puis ChromaDB, puis Gemini direct
        """
        logger.info(f"🔍 Traitement de la requête: {query[:50]}...")
        
        # Priorité 1: Qdrant
        if self.is_qdrant_available:
            try:
                logger.info("🗄️ Tentative avec Qdrant...")
                return await self._query_with_qdrant(query)
            except Exception as e:
                logger.error(f"❌ Erreur Qdrant: {e}. Fallback vers ChromaDB.")
                self.is_qdrant_available = False
        
        # Priorité 2: ChromaDB
        if self.is_chromadb_available:
            try:
                logger.info("📚 Tentative avec ChromaDB...")
                return await self._query_with_chromadb(query)
            except Exception as e:
                logger.error(f"❌ Erreur ChromaDB: {e}. Fallback vers Gemini.")
                self.is_chromadb_available = False
        
        # Priorité 3: Gemini direct
        if self.is_gemini_available:
            logger.info("🤖 Utilisation de Gemini direct...")
            return await self._query_with_gemini(query, context)
        else:
            logger.error("❌ Aucun service disponible")
            return await self._query_with_simulation(query)
    
    async def _query_with_qdrant(self, query: str) -> Dict[str, Any]:
        """Requête avec Qdrant + Gemini"""
        try:
            # Générer l'embedding de la requête
            query_embedding = await self._generate_embedding(query)
            
            # Recherche dans Qdrant
            collection_name = "mirage_documents"
            search_results = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=5
            )
            
            # Préparer le contexte avec filtrage par score
            context_docs = []
            for result in search_results:
                # Filtrer les résultats avec un score trop faible (moins de 0.6 pour macOS)
                if result.score >= 0.6:
                    context_docs.append({
                        "content": result.payload.get("content", ""),
                        "filename": result.payload.get("filename", "unknown"),
                        "score": result.score
                    })
            
            # Générer la réponse avec Gemini
            if self.is_gemini_available and context_docs:
                context = "\n\n".join([f"Document {doc['filename']}:\n{doc['content']}" for doc in context_docs])
                gemini_result = await self._query_with_gemini(query, context)
                # Préserver les sources de Qdrant
                gemini_result["sources"] = context_docs
                gemini_result["mode"] = "qdrant_gemini"
                return gemini_result
            else:
                # Fallback si pas de documents ou Gemini indisponible
                return {
                    "answer": f"Recherche effectuée dans {len(context_docs)} documents. Aucune réponse générée.",
                    "sources": context_docs,
                    "confidence": 0.7,
                    "mode": "qdrant_search_only"
                }
                
        except Exception as e:
            logger.error(f"❌ Erreur dans _query_with_qdrant: {e}")
            raise Exception(f"Qdrant error: {str(e)}")
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Génère un embedding pour le texte (version compatible macOS)"""
        try:
            # Vérifier si on est sur macOS
            import platform
            if platform.system() == "Darwin":  # macOS
                logger.warning("🍎 macOS détecté - utilisation d'embeddings simplifiés")
                # Embedding basé sur le hash du texte (compatible macOS)
                import hashlib
                text_hash = hashlib.md5(text.encode()).hexdigest()
                # Convertir le hash en vecteur de 192 dimensions
                embedding = []
                # MD5 hash = 32 caractères hex = 16 bytes
                for i in range(0, len(text_hash), 2):
                    val = int(text_hash[i:i+2], 16) / 255.0
                    embedding.append(val)
                
                # Étendre à 192 dimensions en répétant le pattern
                while len(embedding) < 192:
                    embedding.extend(embedding[:min(16, 192-len(embedding))])
                
                return embedding[:192]  # S'assurer d'avoir exactement 192 dimensions
            
            # Pour les autres OS, utiliser SentenceTransformers
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embedding = model.encode(text)
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"❌ Erreur génération embedding: {e}")
            # Fallback: embedding basé sur le hash
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()
            embedding = []
            for i in range(0, len(text_hash), 2):
                val = int(text_hash[i:i+2], 16) / 255.0
                embedding.append(val)
            
            # Étendre à 192 dimensions en répétant le pattern
            while len(embedding) < 192:
                embedding.extend(embedding[:min(16, 192-len(embedding))])
            
            return embedding[:192]
    
    async def _query_with_chromadb(self, query: str) -> Dict[str, Any]:
        """Version originale avec ChromaDB (isolée pour éviter les crashes)"""
        try:
            # Import sécurisé des composants RAG
            import sys
            sys.path.append('src')
            
            from rag.rag_engine import RAGEngine
            from orchestrator.orchestrator import Orchestrator
            
            # Initialisation sécurisée
            rag_engine = RAGEngine()
            orchestrator = Orchestrator(api_key=os.getenv("GEMINI_API_KEY"))
            
            result = orchestrator.process_query(query)
            
            return {
                "answer": result.get("answer", "Réponse non disponible"),
                "sources": result.get("sources", []),
                "confidence": result.get("confidence", 0.8),
                "mode": "chromadb_rag"
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur dans _query_with_chromadb: {e}")
            # Ne pas re-raise l'exception, laisser le fallback se déclencher
            raise Exception(f"ChromaDB error: {str(e)}")
    
    async def _query_with_gemini(self, query: str, context: str = None) -> Dict[str, Any]:
        """Version de secours avec Gemini direct"""
        try:
            # Prompt optimisé pour les réponses médicales
            if context:
                medical_prompt = f"""En tant qu'expert médical, réponds de manière précise et concise à la question suivante.

Contexte disponible: {context}

Question: {query}

IMPORTANT: Si le contexte fourni ne contient pas d'informations pertinentes pour répondre à la question, commence ta réponse par: "Je ne trouve pas cette information précise dans nos bases documentaires."

Réponds en français avec:
- Une réponse factuelle et vérifiée basée UNIQUEMENT sur le contexte fourni
- Si le contexte n'est pas pertinent, reconnais explicitement cette limitation
- Des informations structurées
- Des précisions sur les limites de la connaissance
- Un ton professionnel et adapté au domaine médical
- Mentionne toujours l'importance de consulter un professionnel de santé

Réponse:"""
            else:
                medical_prompt = f"""En tant qu'expert médical, réponds de manière précise et concise à la question suivante.

Question: {query}

IMPORTANT: Aucun contexte documentaire n'est disponible. Commence ta réponse par: "Je ne trouve pas cette information dans nos bases documentaires."

Réponds en français avec:
- Une reconnaissance explicite de l'absence d'information dans la base
- Des informations générales si tu en as connaissance
- Des précisions sur les limites de la connaissance
- Un ton professionnel et adapté au domaine médical
- Mentionne toujours l'importance de consulter un professionnel de santé

Réponse:"""

            response = self.gemini_model.generate_content(medical_prompt)
            
            return {
                "answer": response.text,
                "sources": [{"type": "gemini_direct", "confidence": 0.85}],
                "confidence": 0.85,
                "mode": "gemini_fallback"
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur Gemini: {e}")
            return await self._query_with_simulation(query)
    
    async def _query_with_simulation(self, query: str) -> Dict[str, Any]:
        """Mode simulation en dernier recours"""
        return {
            "answer": f"Mode simulation - Question: {query}\n\nRéponse simulée: Cette fonctionnalité nécessite la configuration de l'API Gemini ou la disponibilité de ChromaDB.",
            "sources": [],
            "confidence": 0.3,
            "mode": "simulation"
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut du service hybride"""
        return {
            "qdrant_available": self.is_qdrant_available,
            "chromadb_available": self.is_chromadb_available,
            "gemini_available": self.is_gemini_available,
            "mode": "hybrid",
            "fallback_active": not (self.is_qdrant_available or self.is_chromadb_available)
        }
    
    async def check_and_recover_chromadb(self):
        """Tentative périodique de récupération de ChromaDB"""
        if not self.is_chromadb_available:
            try:
                logger.info("🔄 Tentative de récupération de ChromaDB...")
                import chromadb
                client = chromadb.Client()
                self.is_chromadb_available = True
                logger.info("✅ ChromaDB récupéré avec succès!")
            except Exception as e:
                logger.debug(f"ChromaDB toujours indisponible: {e}")
    
    async def add_document_to_qdrant(self, filename: str, content: str, chunks: List[str] = None) -> bool:
        """Ajoute un document à Qdrant"""
        if not self.is_qdrant_available:
            logger.warning("⚠️  Qdrant non disponible pour l'ajout de document")
            return False
        
        try:
            import uuid
            collection_name = "mirage_documents"
            points = []
            
            if chunks:
                # Ajouter chaque chunk
                for i, chunk in enumerate(chunks):
                    embedding = await self._generate_embedding(chunk)
                    point = PointStruct(
                        id=str(uuid.uuid4()),  # Utiliser UUID au lieu du nom de fichier
                        vector=embedding,
                        payload={
                            "filename": filename,
                            "content": chunk,
                            "chunk_id": i,
                            "total_chunks": len(chunks)
                        }
                    )
                    points.append(point)
            else:
                # Ajouter le document entier
                embedding = await self._generate_embedding(content)
                point = PointStruct(
                    id=str(uuid.uuid4()),  # Utiliser UUID au lieu du nom de fichier
                    vector=embedding,
                    payload={
                        "filename": filename,
                        "content": content
                    }
                )
                points.append(point)
            
            # Insérer dans Qdrant
            self.qdrant_client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            logger.info(f"✅ Document '{filename}' ajouté à Qdrant ({len(points)} points)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur ajout document à Qdrant: {e}")
            return False

# Instance globale du service hybride
hybrid_service = HybridService()
