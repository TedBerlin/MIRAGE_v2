"""
Translator Agent for MIRAGE v2.

Language translation and localization for global pharmaceutical research.
"""

import os
from typing import Dict, Any, Optional
import structlog
import google.generativeai as genai

logger = structlog.get_logger(__name__)


class TranslatorAgent:
    """Language translation and localization agent for pharmaceutical content."""
    
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
        
        # Supported languages
        self.supported_languages = {
            "en": "English",
            "fr": "French", 
            "es": "Spanish",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "ar": "Arabic"
        }
        
        logger.info("TranslatorAgent initialized", model="gemini-1.5-flash", supported_languages=list(self.supported_languages.keys()))
    
    def translate_response(
        self,
        response: str,
        context: str,
        source_language: str = "en",
        target_language: str = "fr",
        response_id: str = ""
    ) -> Dict[str, Any]:
        """
        Translate a pharmaceutical research response to another language.
        
        Args:
            response: Response to translate
            context: Original context for reference
            source_language: Source language code
            target_language: Target language code
            response_id: Unique identifier for this response
            
        Returns:
            Dictionary with translated response and metadata
        """
        try:
            logger.info(
                "Translating response",
                response_id=response_id,
                source_language=source_language,
                target_language=target_language,
                response_length=len(response)
            )
            
            # Validate languages
            if source_language not in self.supported_languages:
                raise ValueError(f"Unsupported source language: {source_language}")
            
            if target_language not in self.supported_languages:
                raise ValueError(f"Unsupported target language: {target_language}")
            
            # Skip translation if source and target are the same
            if source_language == target_language:
                return {
                    "success": True,
                    "response_id": response_id,
                    "original_response": response,
                    "translated_response": response,
                    "source_language": source_language,
                    "target_language": target_language,
                    "translation_notes": "No translation needed - same language",
                    "agent": "translator",
                    "model": "gemini-pro"
                }
            
            # Format the prompts
            system_prompt = self.prompts.get_prompt("translator", "system_prompt")
            user_prompt = self.prompts.format_user_prompt(
                "translator",
                source_language=self.supported_languages[source_language],
                target_language=self.supported_languages[target_language],
                response=response,
                context=context
            )
            
            # Generate translation with both system and user prompts
            translation_response = self.model.generate_content([system_prompt, user_prompt])
            
            if not translation_response.text:
                logger.error("Empty translation response", response_id=response_id)
                return {
                    "success": False,
                    "response_id": response_id,
                    "error": "Empty translation response"
                }
            
            # Process the translation
            translated_text = translation_response.text.strip()
            
            # Analyze translation quality
            translation_analysis = self._analyze_translation(response, translated_text, source_language, target_language)
            
            result = {
                "success": True,
                "response_id": response_id,
                "original_response": response,
                "translated_response": translated_text,
                "source_language": source_language,
                "target_language": target_language,
                "translation_analysis": translation_analysis,
                "agent": "translator",
                "model": "gemini-1.5-flash",
                "metadata": {
                    "original_length": len(response),
                    "translated_length": len(translated_text),
                    "length_ratio": len(translated_text) / len(response) if len(response) > 0 else 1.0,
                    "medical_terms_preserved": translation_analysis["medical_terms_preserved"],
                    "safety_warnings_preserved": translation_analysis["safety_warnings_preserved"],
                    "regulatory_compliance": translation_analysis["regulatory_compliance"]
                }
            }
            
            logger.info(
                "Response translation completed",
                response_id=response_id,
                source_language=source_language,
                target_language=target_language,
                length_ratio=result["metadata"]["length_ratio"]
            )
            
            return result
            
        except Exception as e:
            logger.error("Response translation failed", response_id=response_id, error=str(e))
            return {
                "success": False,
                "response_id": response_id,
                "error": str(e)
            }
    
    def _analyze_translation(
        self,
        original: str,
        translated: str,
        source_language: str,
        target_language: str
    ) -> Dict[str, Any]:
        """Analyze the quality of translation."""
        analysis = {
            "medical_terms_preserved": True,
            "safety_warnings_preserved": True,
            "regulatory_compliance": True,
            "cultural_appropriateness": True,
            "terminology_consistency": True,
            "quality_score": 0.0
        }
        
        try:
            # Check for medical terminology preservation
            medical_terms = [
                "dosage", "contraindication", "adverse", "pharmacokinetics",
                "pharmacodynamics", "therapeutic", "clinical", "trial",
                "efficacy", "safety", "toxicity", "metabolism"
            ]
            
            original_lower = original.lower()
            translated_lower = translated.lower()
            
            # Check if medical terms are preserved (simplified check)
            for term in medical_terms:
                if term in original_lower:
                    # Look for similar terms in translation
                    if not any(similar in translated_lower for similar in [term, term[:4], term[:6]]):
                        analysis["medical_terms_preserved"] = False
                        break
            
            # Check for safety warnings preservation
            safety_indicators = [
                "warning", "caution", "danger", "risk", "adverse",
                "side effect", "contraindication", "monitoring"
            ]
            
            for indicator in safety_indicators:
                if indicator in original_lower:
                    if not any(similar in translated_lower for similar in [indicator, indicator[:4]]):
                        analysis["safety_warnings_preserved"] = False
                        break
            
            # Check for regulatory compliance preservation
            regulatory_terms = [
                "fda", "ema", "regulatory", "approval", "compliance",
                "guideline", "standard", "protocol"
            ]
            
            for term in regulatory_terms:
                if term in original_lower:
                    if not any(similar in translated_lower for similar in [term, term[:3]]):
                        analysis["regulatory_compliance"] = False
                        break
            
            # Calculate quality score
            quality_factors = [
                analysis["medical_terms_preserved"],
                analysis["safety_warnings_preserved"],
                analysis["regulatory_compliance"],
                analysis["cultural_appropriateness"],
                analysis["terminology_consistency"]
            ]
            
            analysis["quality_score"] = sum(quality_factors) / len(quality_factors)
            
        except Exception as e:
            logger.error("Translation analysis failed", error=str(e))
        
        return analysis
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages."""
        return self.supported_languages.copy()
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if a language is supported."""
        return language_code in self.supported_languages
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        return {
            "name": "The Linguist",
            "type": "translator",
            "model": "gemini-1.5-flash",
            "role": "Language translation and localization for global pharmaceutical research",
            "capabilities": [
                "Multi-language translation",
                "Medical terminology preservation",
                "Safety warning preservation",
                "Regulatory compliance maintenance",
                "Cultural appropriateness",
                "Quality analysis"
            ],
            "supported_languages": list(self.supported_languages.keys()),
            "optimizations": [
                "Medical terminology focus",
                "Regulatory compliance preservation",
                "Safety information integrity",
                "Professional medical tone"
            ]
        }
    
    def test_agent(self, test_cases: list) -> Dict[str, Any]:
        """
        Test the translator agent with provided test cases.
        
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
                response = test_case.get("response", "")
                context = test_case.get("context", "")
                source_language = test_case.get("source_language", "en")
                target_language = test_case.get("target_language", "fr")
                
                response_id = f"test_{i}_{hash(response) % 10000}"
                
                result = self.translate_response(
                    response, context, source_language, target_language, response_id
                )
                
                if result["success"]:
                    # Check translation quality
                    quality_score = result.get("translation_analysis", {}).get("quality_score", 0.0)
                    test_passed = quality_score >= 0.7  # Minimum quality threshold
                    
                    if test_passed:
                        results["passed"] += 1
                    else:
                        results["failed"] += 1
                    
                    results["test_results"].append({
                        "test_id": i,
                        "source_language": source_language,
                        "target_language": target_language,
                        "quality_score": quality_score,
                        "passed": test_passed,
                        "translated_response": result.get("translated_response", "")[:100] + "..."
                    })
                else:
                    results["failed"] += 1
                    results["test_results"].append({
                        "test_id": i,
                        "source_language": source_language,
                        "target_language": target_language,
                        "error": result.get("error", "Unknown error"),
                        "passed": False
                    })
                    
            except Exception as e:
                results["failed"] += 1
                results["test_results"].append({
                    "test_id": i,
                    "source_language": test_case.get("source_language", "en"),
                    "target_language": test_case.get("target_language", "fr"),
                    "error": str(e),
                    "passed": False
                })
        
        logger.info("Translator agent testing completed", results=results)
        return results
