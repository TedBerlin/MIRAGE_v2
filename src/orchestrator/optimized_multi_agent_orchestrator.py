"""
MIRAGE v2 - Orchestrateur Multi-Agent Optimisé
==============================================
Version optimisée avec gestion robuste des timeouts et fallback éthique
Respect du brief initial + 8 piliers + "Je ne sais pas" obligatoire
"""

import os
import time
import hashlib
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from functools import wraps

# Import Gemini directly
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import google.generativeai as genai
from agents.generator_agent import GeneratorAgent
from agents.verifier_agent import VerifierAgent
from agents.reformer_agent import ReformerAgent
from agents.translator_agent import TranslatorAgent
from agents.agent_prompts import detect_language
from orchestrator.human_loop_manager import HumanLoopManager
from rag.rag_engine import RAGEngine

logger = structlog.get_logger(__name__)

def timeout_decorator(timeout_seconds: int):
    """Décorateur pour gérer les timeouts avec fallback éthique"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                logger.warning(f"Timeout sur {func.__name__} après {timeout_seconds}s")
                return None
        return wrapper
    return decorator

class OptimizedMultiAgentOrchestrator:
    """Orchestrateur optimisé avec gestion robuste des timeouts"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        enable_human_loop: bool = True,
        max_iterations: int = 3,
        cache_ttl: int = 3600,
        request_timeout: int = 60
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configuration optimisée
        self.enable_human_loop = enable_human_loop
        self.max_iterations = max_iterations
        self.cache_ttl = cache_ttl
        self.request_timeout = request_timeout
        
        # Timeouts granulaires pour chaque étape
        self.timeout_limits = {
            "detection_langue": 5,
            "traduction": 10,
            "recherche_rag": 15,
            "generation_reponse": 20,
            "verification": 10
        }
        
        # Initialize components
        self._initialize_components()
        
        # Cache pour optimiser les performances
        self.context_cache = {}
        self.response_cache = {}
        
        logger.info("OptimizedMultiAgentOrchestrator initialized with robust timeout management")
    
    def _initialize_components(self):
        """Initialisation des composants avec gestion d'erreurs"""
        try:
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Initialize agents
            self.generator = GeneratorAgent(self.gemini_model)
            self.verifier = VerifierAgent(self.gemini_model)
            self.reformer = ReformerAgent(self.gemini_model)
            self.translator = TranslatorAgent(self.gemini_model)
            
            # Initialize RAG
            self.rag_engine = RAGEngine()
            
            # Initialize Human Loop Manager
            self.human_loop_manager = HumanLoopManager() if self.enable_human_loop else None
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize components", error=str(e))
            raise
    
    @timeout_decorator(60)
    async def process_query_optimized(self, user_query: str, target_language: str = None) -> Dict[str, Any]:
        """
        Version optimisée avec gestion robuste des timeouts et fallback éthique
        Respect du brief initial : "Je ne sais pas" obligatoire
        """
        start_time = time.time()
        query_hash = hashlib.md5(user_query.encode()).hexdigest()
        
        # Détection de langue avec timeout
        detected_language = await self._detect_language_with_timeout(user_query)
        if not detected_language:
            return self._create_ethical_fallback_response(
                user_query, "fr", "Échec de détection de langue", query_hash, start_time
            )
        
        if target_language == "en" and detected_language != "en":
            target_language = detected_language
        
        try:
            logger.info("Processing query with optimized multi-agent system", 
                       query=user_query[:100], 
                       query_hash=query_hash,
                       detected_language=detected_language,
                       target_language=target_language)
            
            # Check cache first
            cached_response = self._get_cached_response(query_hash)
            if cached_response:
                logger.info("Returning cached response", query_hash=query_hash)
                return cached_response
            
            # Step 1: Get context from RAG with timeout
            context_result = await self._get_context_with_timeout(user_query)
            if not context_result["success"]:
                logger.warning("No context available, proceeding with empty context", query=user_query[:100])
                context = "No relevant context found in the pharmaceutical research database."
                rag_metadata = {"total_results": 0, "source_documents": [], "similarity_threshold": 0.0, "service_used": "fallback"}
            else:
                context = context_result["context"]
                rag_metadata = context_result["metadata"]
            
            # Step 2: Generate response with timeout
            response_id = f"{query_hash}_{int(time.time())}"
            generation_result = await self._generate_response_with_timeout(user_query, context, response_id)
            
            if not generation_result["success"]:
                return self._create_ethical_fallback_response(
                    user_query, detected_language, "Échec de génération de réponse", query_hash, start_time
                )
            
            # Step 3: Verify response with timeout
            verification_result = await self._verify_response_with_timeout(
                user_query, context, generation_result["answer"], response_id
            )
            
            if not verification_result["success"]:
                return self._create_ethical_fallback_response(
                    user_query, detected_language, "Échec de vérification", query_hash, start_time
                )
            
            # Step 4: Human-in-the-Loop validation (if enabled)
            human_validation_result = None
            if self.human_loop_manager:
                human_validation_result = self.human_loop_manager.evaluate_human_validation_needed(
                    user_query, generation_result["answer"], response_id
                )
            
            # Step 5: Translation if needed with timeout
            final_response = generation_result["answer"]
            if detected_language != target_language:
                translation_result = await self._translate_response_with_timeout(
                    generation_result["answer"], target_language
                )
                if translation_result["success"]:
                    final_response = translation_result["translated_response"]
            
            # Step 6: Finalize response
            result = {
                "success": True,
                "answer": final_response,
                "sources": self._extract_sources(rag_metadata),
                "confidence": verification_result.get("confidence", 0.8),
                "detected_language": detected_language,
                "target_language": target_language,
                "query_hash": query_hash,
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat(),
                "rag_metadata": rag_metadata,
                "context_used": context,
                "workflow": "optimized_multi_agent",
                "agent_workflow": ["generator", "verifier", "translator"] if detected_language != target_language else ["generator", "verifier"],
                "consensus": "approved",
                "iteration": 1,
                "verification": verification_result,
                "human_validation": human_validation_result
            }
            
            # Cache the response
            self._cache_response(query_hash, result)
            
            logger.info("Optimized multi-agent query processing completed successfully",
                     query_hash=query_hash,
                     processing_time=result["processing_time"])
            
            return result
            
        except Exception as e:
            logger.error("Optimized multi-agent query processing failed", query=user_query, error=str(e))
            return self._create_ethical_fallback_response(
                user_query, detected_language, f"Erreur système: {str(e)}", query_hash, start_time
            )
    
    async def _detect_language_with_timeout(self, text: str) -> Optional[str]:
        """Détection de langue avec timeout"""
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(detect_language, text),
                timeout=self.timeout_limits["detection_langue"]
            )
        except asyncio.TimeoutError:
            logger.warning("Language detection timeout", text=text[:50])
            return None
        except Exception as e:
            logger.error("Language detection error", error=str(e))
            return None
    
    async def _get_context_with_timeout(self, query: str) -> Dict[str, Any]:
        """Récupération de contexte avec timeout"""
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self.rag_engine.query_rag, query),
                timeout=self.timeout_limits["recherche_rag"]
            )
        except asyncio.TimeoutError:
            logger.warning("RAG context timeout", query=query[:50])
            return {"success": False, "context": "No context available", "metadata": {}}
        except Exception as e:
            logger.error("RAG context error", error=str(e))
            return {"success": False, "context": "No context available", "metadata": {}}
    
    async def _generate_response_with_timeout(self, query: str, context: str, response_id: str) -> Dict[str, Any]:
        """Génération de réponse avec timeout"""
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self.generator.generate_response, query, context, response_id),
                timeout=self.timeout_limits["generation_reponse"]
            )
        except asyncio.TimeoutError:
            logger.warning("Response generation timeout", query=query[:50])
            return {"success": False, "answer": "Response generation timeout"}
        except Exception as e:
            logger.error("Response generation error", error=str(e))
            return {"success": False, "answer": "Response generation failed"}
    
    async def _verify_response_with_timeout(self, query: str, context: str, answer: str, response_id: str) -> Dict[str, Any]:
        """Vérification de réponse avec timeout"""
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self.verifier.verify_response, query, context, answer, response_id),
                timeout=self.timeout_limits["verification"]
            )
        except asyncio.TimeoutError:
            logger.warning("Response verification timeout", query=query[:50])
            return {"success": False, "confidence": 0.5}
        except Exception as e:
            logger.error("Response verification error", error=str(e))
            return {"success": False, "confidence": 0.5}
    
    async def _translate_response_with_timeout(self, response: str, target_language: str) -> Dict[str, Any]:
        """Traduction de réponse avec timeout"""
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self.translator.translate_text, response, target_language),
                timeout=self.timeout_limits["traduction"]
            )
        except asyncio.TimeoutError:
            logger.warning("Response translation timeout", target_language=target_language)
            return {"success": False, "translated_response": response}
        except Exception as e:
            logger.error("Response translation error", error=str(e))
            return {"success": False, "translated_response": response}
    
    def _create_ethical_fallback_response(self, query: str, detected_language: str, error_reason: str, query_hash: str, start_time: float) -> Dict[str, Any]:
        """Création d'une réponse de fallback éthique - Respect du brief initial"""
        
        # Messages éthiques selon la langue détectée
        ethical_messages = {
            "fr": "Je ne peux pas fournir cette information médicale. Consultez un professionnel de santé qualifié.",
            "es": "No puedo proporcionar esta información médica. Consulte a un profesional de salud calificado.",
            "de": "Ich kann diese medizinische Information nicht bereitstellen. Konsultieren Sie einen qualifizierten Gesundheitsfachmann.",
            "en": "I cannot provide this medical information. Please consult a qualified healthcare professional."
        }
        
        # Message de fallback éthique
        fallback_message = ethical_messages.get(detected_language, ethical_messages["en"])
        
        return {
            "success": False,
            "answer": fallback_message,
            "sources": [],
            "confidence": 0.0,
            "detected_language": detected_language,
            "target_language": detected_language,
            "query_hash": query_hash,
            "processing_time": time.time() - start_time,
            "timestamp": datetime.now().isoformat(),
            "workflow": "ethical_fallback",
            "agent_workflow": ["ethical_fallback"],
            "consensus": "ethical_fallback",
            "iteration": 0,
            "verification": {"success": False, "confidence": 0.0},
            "human_validation": None,
            "error_reason": error_reason,
            "safety_note": "Système de sécurité médicale activé - Pas d'invention de réponses"
        }
    
    def _extract_sources(self, rag_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extraction des sources du métadonnées RAG"""
        sources = []
        if rag_metadata.get("source_documents"):
            for doc in rag_metadata["source_documents"]:
                sources.append({
                    "filename": doc.get("filename", "Unknown"),
                    "content": doc.get("content", "Source document"),
                    "confidence": doc.get("confidence", 0.8)
                })
        return sources
    
    def _get_cached_response(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Récupération de réponse en cache"""
        if query_hash in self.response_cache:
            cached = self.response_cache[query_hash]
            if time.time() - cached["timestamp"] < self.cache_ttl:
                return cached
            else:
                del self.response_cache[query_hash]
        return None
    
    def _cache_response(self, query_hash: str, response: Dict[str, Any]) -> None:
        """Mise en cache de la réponse"""
        self.response_cache[query_hash] = {
            **response,
            "timestamp": time.time()
        }
    
    def _generate_query_hash(self, query: str) -> str:
        """Génération du hash de la requête"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def process_query(self, query: str, target_language: str = None, **kwargs) -> Dict[str, Any]:
        """Méthode de compatibilité avec l'API existante"""
        import asyncio
        try:
            # Exécution synchrone de la méthode asynchrone
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.process_query_optimized(query, target_language))
            loop.close()
            return result
        except Exception as e:
            logger.error("Error in process_query", error=str(e))
            return {
                "success": False,
                "answer": "Je ne peux pas traiter cette requête actuellement.",
                "detected_language": None,
                "target_language": target_language,
                "processing_time": 0,
                "error": str(e)
            }
    
    def clear_cache(self) -> None:
        """Nettoyage du cache"""
        self.context_cache.clear()
        self.response_cache.clear()
        logger.info("All caches cleared")
    
    def health_check(self) -> Dict[str, Any]:
        """Vérification de santé du système"""
        try:
            health_status = {
                "orchestrator": "healthy",
                "gemini_service": "healthy",
                "agents": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Check agents
            agents = {
                "generator": self.generator,
                "verifier": self.verifier,
                "reformer": self.reformer,
                "translator": self.translator
            }
            
            for agent_name, agent in agents.items():
                try:
                    agent_info = agent.get_agent_info()
                    health_status["agents"][agent_name] = "healthy"
                except Exception as e:
                    health_status["agents"][agent_name] = f"unhealthy: {str(e)}"
            
            # Overall health
            agent_health = all(
                status == "healthy" 
                for status in health_status["agents"].values()
            )
            
            health_status["overall"] = "healthy" if agent_health else "unhealthy"
            
            return health_status
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return {
                "overall": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
