"""
Generator Agent for MIRAGE v2.

Primary response generator with pharmaceutical research focus.
"""

import os
from typing import Dict, Any, Optional
import structlog
import google.generativeai as genai

logger = structlog.get_logger(__name__)


class GeneratorAgent:
    """Primary response generator agent for pharmaceutical research."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Load prompts (shared instance)
        from .agent_prompts import get_shared_prompts
        self.prompts = get_shared_prompts()
        
        logger.info("GeneratorAgent initialized", model="gemini-1.5-flash")
    
    def generate_response(
        self,
        query: str,
        context: str,
        response_id: str
    ) -> Dict[str, Any]:
        """
        Generate a response to a pharmaceutical research query.
        
        Args:
            query: The research question
            context: Relevant context from RAG system
            response_id: Unique identifier for this response
            
        Returns:
            Dictionary with generated response and metadata
        """
        try:
            logger.info("Generating response", query=query[:100], response_id=response_id)
            
            # Detect language and format prompts accordingly
            from .agent_prompts import detect_language
            detected_language = detect_language(query)
            
            # Format the prompts
            system_prompt = self.prompts.get_prompt("generator", "system_prompt")
            user_prompt = self.prompts.format_user_prompt(
                "generator",
                context=context,
                query=query
            )
            
            # Add language instruction to user prompt
            if detected_language == "fr":
                user_prompt += "\n\nIMPORTANT: Répondez en français. Utilisez la terminologie médicale française appropriée. FORMATAGE ABSOLUMENT CRITIQUE: Chaque point de puce (•) doit être sur une ligne séparée avec DEUX sauts de ligne après chaque point. JAMAIS plusieurs points sur la même ligne. EMOJIS OBLIGATOIRES: 💊 pour les avantages médicaux, ⚠️ pour les avertissements, 🔬 pour la recherche, 📚 pour les sources. FORMAT EXACT OBLIGATOIRE: • Premier point\n\n• Deuxième point\n\n• Troisième point\n\nCRITIQUE: Respectez exactement ce format avec les sauts de ligne!"
            elif detected_language == "es":
                user_prompt += "\n\nIMPORTANT: Responda en español. Use la terminología médica española apropiada. FORMATO ABSOLUTAMENTE CRÍTICO: Cada punto de viñeta (•) debe estar en una línea separada con DOS saltos de línea después de cada punto. NUNCA múltiples puntos en la misma línea. EMOJIS OBLIGATORIOS: 💊 para beneficios médicos, ⚠️ para advertencias, 🔬 para investigación, 📚 para fuentes. FORMATO EXACTO OBLIGATORIO: • 💊 Primer beneficio médico\n\n• ⚠️ Advertencia importante\n\n• 🔬 Información de investigación\n\n• 📚 Referencia de fuente\n\nCRÍTICO: ¡Use \\n\\n entre cada punto, NO etiquetas HTML!"
            elif detected_language == "en":
                user_prompt += "\n\nIMPORTANT: Respond in English. Use appropriate medical terminology. ABSOLUTELY CRITICAL FORMATTING: Each bullet point (•) must be on a separate line with TWO line breaks after each point. NEVER multiple points on the same line. MANDATORY EMOJIS: 💊 for medical benefits, ⚠️ for warnings, 🔬 for research, 📚 for sources. MANDATORY EXACT FORMAT: • 💊 First medical benefit\n\n• ⚠️ Important warning\n\n• 🔬 Research information\n\n• 📚 Source reference\n\nCRITICAL: Follow this exact format with line breaks!"
            elif detected_language == "de":
                user_prompt += "\n\nIMPORTANT: Antworten Sie auf Deutsch. Verwenden Sie die entsprechende deutsche medizinische Terminologie. ABSOLUT KRITISCHES FORMAT: Jeder Aufzählungspunkt (•) muss in einer separaten Zeile stehen mit ZWEI Zeilenumbrüchen nach jedem Punkt. PFLICHT-EMOJIS: 💊 für medizinische Vorteile, ⚠️ für Warnungen, 🔬 für Forschung, 📚 für Quellen. PFLICHT-EXAKTES FORMAT: • 💊 Erster medizinischer Vorteil\n\n• ⚠️ Wichtige Warnung\n\n• 🔬 Forschungsinformation\n\n• 📚 Quellenreferenz\n\nKRITISCH: Verwenden Sie \\n\\n zwischen jedem Punkt, KEINE HTML-Tags!"
            
            # Generate response using Gemini with both system and user prompts
            response = self.model.generate_content([system_prompt, user_prompt])
            
            if not response.text:
                logger.error("Empty response from Gemini", response_id=response_id)
                return {
                    "success": False,
                    "response_id": response_id,
                    "error": "Empty response from AI model"
                }
            
            # Process the response
            generated_text = response.text.strip()
            
            # Check for "I don't know" response
            is_unknown = self._is_unknown_response(generated_text)
            
            result = {
                "success": True,
                "response_id": response_id,
                "query": query,
                "answer": generated_text,
                "context_used": context,
                "is_unknown": is_unknown,
                "agent": "generator",
                "model": "gemini-1.5-flash",
                "metadata": {
                    "context_length": len(context),
                    "response_length": len(generated_text),
                    "has_sources": self._has_source_citations(generated_text),
                    "safety_keywords": self._extract_safety_keywords(generated_text)
                }
            }
            
            logger.info(
                "Response generated successfully",
                response_id=response_id,
                response_length=len(generated_text),
                is_unknown=is_unknown
            )
            
            return result
            
        except Exception as e:
            logger.error("Response generation failed", query=query, response_id=response_id, error=str(e))
            return {
                "success": False,
                "response_id": response_id,
                "error": str(e)
            }
    
    def _is_unknown_response(self, response: str) -> bool:
        """Check if response indicates unknown information."""
        unknown_indicators = [
            "I cannot find this information",
            "not available in our",
            "not found in our",
            "I don't have information",
            "I cannot locate",
            "not present in the",
            "not mentioned in the"
        ]
        
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in unknown_indicators)
    
    def _has_source_citations(self, response: str) -> bool:
        """Check if response includes source citations."""
        citation_indicators = [
            "according to",
            "based on",
            "as mentioned in",
            "the document states",
            "research shows",
            "studies indicate",
            "evidence suggests"
        ]
        
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in citation_indicators)
    
    def _extract_safety_keywords(self, response: str) -> list:
        """Extract safety-related keywords from response."""
        safety_keywords = [
            "safety", "adverse", "side effect", "contraindication",
            "warning", "caution", "risk", "toxicity", "overdose",
            "interaction", "allergy", "pregnancy", "lactation",
            "pediatric", "geriatric", "monitoring", "dosage"
        ]
        
        response_lower = response.lower()
        found_keywords = [keyword for keyword in safety_keywords if keyword in response_lower]
        
        return found_keywords
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        return {
            "name": "The Innovator",
            "type": "generator",
            "model": "gemini-1.5-flash",
            "role": "Primary response generator for pharmaceutical research",
            "capabilities": [
                "Context-based response generation",
                "Pharmaceutical research focus",
                "Safety-aware responses",
                "Source citation",
                "Unknown information detection"
            ],
            "optimizations": [
                "Explicit 'I don't know' instruction",
                "Context-first approach",
                "Safety keyword detection",
                "Source citation analysis"
            ]
        }
    
    def test_agent(self, test_cases: list) -> Dict[str, Any]:
        """
        Test the agent with provided test cases.
        
        Args:
            test_cases: List of test case dictionaries
            
        Returns:
            Test results
        """
        results = {
            "total_tests": len(test_cases),
            "passed": 0,
            "failed": 0,
            "test_results": []
        }
        
        for i, test_case in enumerate(test_cases):
            try:
                query = test_case.get("query", "")
                context = test_case.get("context", "")
                expected_unknown = test_case.get("expected_unknown", False)
                
                response_id = f"test_{i}_{hash(query) % 10000}"
                
                result = self.generate_response(query, context, response_id)
                
                if result["success"]:
                    # Check if unknown response matches expectation
                    actual_unknown = result.get("is_unknown", False)
                    test_passed = (actual_unknown == expected_unknown)
                    
                    if test_passed:
                        results["passed"] += 1
                    else:
                        results["failed"] += 1
                    
                    results["test_results"].append({
                        "test_id": i,
                        "query": query,
                        "expected_unknown": expected_unknown,
                        "actual_unknown": actual_unknown,
                        "passed": test_passed,
                        "response": result.get("answer", "")[:100] + "..."
                    })
                else:
                    results["failed"] += 1
                    results["test_results"].append({
                        "test_id": i,
                        "query": query,
                        "error": result.get("error", "Unknown error"),
                        "passed": False
                    })
                    
            except Exception as e:
                results["failed"] += 1
                results["test_results"].append({
                    "test_id": i,
                    "query": test_case.get("query", ""),
                    "error": str(e),
                    "passed": False
                })
        
        logger.info("Agent testing completed", results=results)
        return results
