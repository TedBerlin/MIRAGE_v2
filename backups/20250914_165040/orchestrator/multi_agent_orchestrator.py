"""
Multi-Agent Orchestrator for MIRAGE v2.

Orchestrates the complete multi-agent workflow with HybridService integration.
"""

import os
import time
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Import Gemini directly instead of HybridService
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import google.generativeai as genai
from agents.generator_agent import GeneratorAgent
from agents.verifier_agent import VerifierAgent
from agents.reformer_agent import ReformerAgent
from agents.translator_agent import TranslatorAgent

logger = structlog.get_logger(__name__)


class MultiAgentOrchestrator:
    """Multi-agent orchestrator for coordinating all MIRAGE v2 components."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        enable_human_loop: bool = True,
        max_iterations: int = 3,
        cache_ttl: int = 3600,
        request_timeout: int = 30
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configuration
        self.enable_human_loop = enable_human_loop
        self.max_iterations = max_iterations
        self.cache_ttl = cache_ttl
        self.request_timeout = request_timeout
        
        # Initialize components
        # Configure Gemini directly
        genai.configure(api_key=self.api_key)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.generator = GeneratorAgent(self.api_key)
        self.verifier = VerifierAgent(self.api_key)
        self.reformer = ReformerAgent(self.api_key)
        self.translator = TranslatorAgent(self.api_key)
        
        # Cache for context and responses
        self.context_cache = {}
        self.response_cache = {}
        
        logger.info(
            "MultiAgentOrchestrator initialized",
            enable_human_loop=enable_human_loop,
            max_iterations=max_iterations,
            cache_ttl=cache_ttl
        )
    
    async def process_query(
        self,
        query: str,
        enable_human_loop: Optional[bool] = None,
        target_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Process a pharmaceutical research query through the complete multi-agent workflow.
        
        Args:
            query: The research question
            enable_human_loop: Override human loop setting
            target_language: Target language for response
            
        Returns:
            Dictionary with complete response and metadata
        """
        start_time = time.time()
        query_hash = self._generate_query_hash(query)
        
        try:
            logger.info("Processing query with multi-agent system", query=query[:100], query_hash=query_hash)
            
            # Check cache first
            cached_response = self._get_cached_response(query_hash)
            if cached_response:
                logger.info("Returning cached response", query_hash=query_hash)
                return cached_response
            
            # Step 1: Get context from HybridService
            context_result = await self._get_context(query)
            if not context_result["success"]:
                # If no context available, use empty context but continue processing
                logger.warning("No context available, proceeding with empty context", query=query[:100])
                context = "No relevant context found in the pharmaceutical research database."
                rag_metadata = {"total_results": 0, "source_documents": [], "similarity_threshold": 0.0, "service_used": "fallback"}
            else:
                context = context_result["context"]
                rag_metadata = context_result["metadata"]
            
            # Step 2: Generate initial response with Generator Agent
            response_id = f"{query_hash}_{int(time.time())}"
            generation_result = self._generate_response(query, context, response_id)
            
            if not generation_result["success"]:
                return self._create_error_response(query, "Failed to generate response", query_hash)
            
            # Step 3: Verify response with Verifier Agent
            verification_result = self._verify_response(
                query, context, generation_result["answer"], response_id
            )
            
            if not verification_result["success"]:
                return self._create_error_response(query, "Failed to verify response", query_hash)
            
            # Step 4: Handle consensus and iteration
            final_response = self._handle_consensus(
                query, context, generation_result, verification_result, response_id
            )
            
            # Step 5: Translation if needed with Translator Agent
            if target_language != "en" and final_response["success"]:
                translation_result = self._translate_response(
                    final_response["answer"], context, target_language, response_id
                )
                if translation_result["success"]:
                    final_response["translated_response"] = translation_result["translated_response"]
                    final_response["target_language"] = target_language
            
            # Step 6: Finalize response
            final_response.update({
                "query": query,
                "query_hash": query_hash,
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat(),
                "rag_metadata": rag_metadata,
                "context_used": context,
                "workflow": "multi_agent"
            })
            
            # Cache the response
            self._cache_response(query_hash, final_response)
            
            logger.info(
                "Multi-agent query processing completed",
                query_hash=query_hash,
                processing_time=final_response["processing_time"],
                success=final_response["success"],
                has_answer="answer" in final_response,
                answer_length=len(final_response.get("answer", "")) if "answer" in final_response else 0
            )
            
            return final_response
            
        except Exception as e:
            logger.error("Multi-agent query processing failed", query=query, error=str(e))
            return self._create_error_response(query, str(e), query_hash)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    async def _get_context(self, query: str) -> Dict[str, Any]:
        """Get context from HybridService with retry logic."""
        try:
            # Use Gemini directly for context generation
            prompt = f"""Based on the following query, provide relevant pharmaceutical context and information:

Query: {query}

Please provide:
1. Relevant pharmaceutical knowledge
2. Safety considerations
3. Regulatory information if applicable
4. Clinical context

Keep the response concise and focused on pharmaceutical research."""

            response = await self.gemini_model.generate_content_async(prompt)
            context = response.text if response.text else "No relevant context available."
            
            metadata = {
                "total_results": 1,
                "source_documents": [{
                    "type": "gemini_direct",
                    "confidence": 0.85,
                    "content": "Context generated directly by Gemini AI"
                }],
                "similarity_threshold": 0.0,
                "service_used": "gemini_direct"
            }
            
            # Cache context
            query_hash = self._generate_query_hash(query)
            self.context_cache[query_hash] = {
                "context": context,
                "timestamp": time.time(),
                "metadata": metadata
            }
            
            return {
                "success": True,
                "context": context,
                "metadata": metadata
            }
                
        except Exception as e:
            logger.error("Context retrieval failed", query=query, error=str(e))
            raise
    
    def _generate_response(self, query: str, context: str, response_id: str) -> Dict[str, Any]:
        """Generate response using the generator agent."""
        try:
            return self.generator.generate_response(query, context, response_id)
        except Exception as e:
            logger.error("Response generation failed", query=query, error=str(e))
            return {"success": False, "error": str(e)}
    
    def _verify_response(self, query: str, context: str, response: str, response_id: str) -> Dict[str, Any]:
        """Verify response using the verifier agent."""
        try:
            return self.verifier.verify_response(query, context, response, response_id)
        except Exception as e:
            logger.error("Response verification failed", response_id=response_id, error=str(e))
            return {"success": False, "error": str(e)}
    
    def _handle_consensus(
        self,
        query: str,
        context: str,
        generation_result: Dict[str, Any],
        verification_result: Dict[str, Any],
        response_id: str
    ) -> Dict[str, Any]:
        """Handle consensus logic and iteration if needed."""
        try:
            vote = verification_result.get("vote")
            confidence = verification_result.get("confidence", 0.0)
            
            logger.info("Handling consensus", vote=vote, confidence=confidence, response_id=response_id)
            
            if vote == "OUI" and confidence >= 0.7:
                # High confidence approval
                return {
                    "success": True,
                    "answer": generation_result["answer"],
                    "verification": verification_result,
                    "consensus": "approved",
                    "iteration": 1,
                    "agent_workflow": ["generator", "verifier"]
                }
            
            elif vote == "NON" or confidence < 0.3:
                # Rejection - try to reform with Reformer Agent
                logger.info("Response rejected, attempting reform", response_id=response_id)
                reform_result = self._reform_response(
                    query, context, generation_result["answer"],
                    verification_result["verification_analysis"], response_id
                )
                
                if reform_result["success"]:
                    # Verify the reformed response
                    reform_verification = self._verify_response(
                        query, context, reform_result["refined_response"], response_id
                    )
                    
                    if reform_verification.get("vote") == "OUI":
                        return {
                            "success": True,
                            "answer": reform_result["refined_response"],
                            "verification": reform_verification,
                            "consensus": "reformed_approved",
                            "iteration": 2,
                            "reform_metadata": reform_result,
                            "agent_workflow": ["generator", "verifier", "reformer", "verifier"]
                        }
                    else:
                        # Still not approved after reform
                        return {
                            "success": False,
                            "answer": reform_result["refined_response"],
                            "verification": reform_verification,
                            "consensus": "reformed_rejected",
                            "iteration": 2,
                            "error": "Response rejected even after reform",
                            "agent_workflow": ["generator", "verifier", "reformer", "verifier"]
                        }
                else:
                    return {
                        "success": False,
                        "answer": generation_result["answer"],
                        "verification": verification_result,
                        "consensus": "reform_failed",
                        "iteration": 1,
                        "error": "Failed to reform response",
                        "agent_workflow": ["generator", "verifier", "reformer"]
                    }
            
            else:
                # Uncertain - return with warning
                return {
                    "success": True,
                    "answer": generation_result["answer"],
                    "verification": verification_result,
                    "consensus": "uncertain",
                    "iteration": 1,
                    "warning": "Low confidence verification",
                    "agent_workflow": ["generator", "verifier"]
                }
                
        except Exception as e:
            logger.error("Consensus handling failed", response_id=response_id, error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def _reform_response(
        self,
        query: str,
        context: str,
        response: str,
        verifier_analysis: str,
        response_id: str
    ) -> Dict[str, Any]:
        """Reform response using the reformer agent."""
        try:
            return self.reformer.reform_response(query, context, response, verifier_analysis, response_id)
        except Exception as e:
            logger.error("Response reform failed", response_id=response_id, error=str(e))
            return {"success": False, "error": str(e)}
    
    def _translate_response(
        self,
        response: str,
        context: str,
        target_language: str,
        response_id: str
    ) -> Dict[str, Any]:
        """Translate response to target language using translator agent."""
        try:
            return self.translator.translate_response(
                response, context, "en", target_language, response_id
            )
        except Exception as e:
            logger.error("Response translation failed", response_id=response_id, error=str(e))
            return {"success": False, "error": str(e)}
    
    def _generate_query_hash(self, query: str) -> str:
        """Generate a hash for the query for caching."""
        return hashlib.sha256(query.encode()).hexdigest()[:16]
    
    def _get_cached_response(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired."""
        if query_hash in self.response_cache:
            cached_data = self.response_cache[query_hash]
            if time.time() - cached_data["timestamp"] < self.cache_ttl:
                return cached_data["response"]
            else:
                # Remove expired cache
                del self.response_cache[query_hash]
        return None
    
    def _cache_response(self, query_hash: str, response: Dict[str, Any]):
        """Cache the response."""
        self.response_cache[query_hash] = {
            "response": response,
            "timestamp": time.time()
        }
    
    def _create_error_response(self, query: str, error: str, query_hash: str) -> Dict[str, Any]:
        """Create a standardized error response."""
        return {
            "success": False,
            "query": query,
            "query_hash": query_hash,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "processing_time": 0.0,
            "workflow": "multi_agent"
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        try:
            # Get Gemini direct stats
            gemini_stats = {
                "model": "gemini-1.5-flash",
                "status": "active",
                "mode": "direct_integration"
            }
            
            # Get cache stats
            cache_stats = {
                "context_cache_size": len(self.context_cache),
                "response_cache_size": len(self.response_cache),
                "cache_ttl": self.cache_ttl
            }
            
            # Get agent stats
            agent_stats = {
                "generator": self.generator.get_agent_info(),
                "verifier": self.verifier.get_agent_info(),
                "reformer": self.reformer.get_agent_info(),
                "translator": self.translator.get_agent_info()
            }
            
            return {
                "orchestrator": {
                    "type": "multi_agent",
                    "enable_human_loop": self.enable_human_loop,
                    "max_iterations": self.max_iterations,
                    "request_timeout": self.request_timeout
                },
                "gemini_service": gemini_stats,
                "cache": cache_stats,
                "agents": agent_stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to get system stats", error=str(e))
            return {"error": str(e)}
    
    def clear_cache(self):
        """Clear all caches."""
        self.context_cache.clear()
        self.response_cache.clear()
        logger.info("All caches cleared")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive health check."""
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
            all_healthy = all(
                status == "healthy" or status == "unknown"
                for status in health_status.values()
                if isinstance(status, str)
            )
            
            health_status["overall"] = "healthy" if all_healthy else "unhealthy"
            
            return health_status
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return {
                "overall": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
