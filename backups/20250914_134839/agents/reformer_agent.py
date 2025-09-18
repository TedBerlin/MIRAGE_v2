"""
Reformer Agent for MIRAGE v2.

Response refinement and quality enhancement agent.
"""

import os
import json
from typing import Dict, Any, Optional
import structlog
import google.generativeai as genai

logger = structlog.get_logger(__name__)


class ReformerAgent:
    """Response refinement and quality enhancement agent."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Load prompts
        from .agent_prompts import AgentPrompts
        self.prompts = AgentPrompts()
        
        logger.info("ReformerAgent initialized", model="gemini-pro")
    
    def reform_response(
        self,
        query: str,
        context: str,
        response: str,
        verifier_analysis: str,
        response_id: str
    ) -> Dict[str, Any]:
        """
        Refine and enhance a pharmaceutical research response.
        
        Args:
            query: Original research question
            context: Context used for generation
            response: Original response to refine
            verifier_analysis: Analysis from verifier agent
            response_id: Unique identifier for this response
            
        Returns:
            Dictionary with refined response and metadata
        """
        try:
            logger.info("Reforming response", response_id=response_id, response_length=len(response))
            
            # Format the reform prompt
            user_prompt = self.prompts.format_user_prompt(
                "reformer",
                query=query,
                context=context,
                response=response,
                verifier_analysis=verifier_analysis
            )
            
            # Generate refined response
            reform_response = self.model.generate_content(user_prompt)
            
            if not reform_response.text:
                logger.error("Empty reform response", response_id=response_id)
                return {
                    "success": False,
                    "response_id": response_id,
                    "error": "Empty reform response"
                }
            
            # Parse the reform response
            reform_text = reform_response.text.strip()
            
            # Try to parse as JSON first
            try:
                reform_data = json.loads(reform_text)
                refined_response = reform_data.get("answer", reform_text)
                sources = reform_data.get("sources", [])
                safety_notes = reform_data.get("safety_notes", "")
                improvements = reform_data.get("improvements_made", [])
            except json.JSONDecodeError:
                # Fallback: treat as plain text
                refined_response = reform_text
                sources = []
                safety_notes = ""
                improvements = []
            
            # Analyze improvements made
            improvement_analysis = self._analyze_improvements(response, refined_response)
            
            result = {
                "success": True,
                "response_id": response_id,
                "query": query,
                "original_response": response,
                "refined_response": refined_response,
                "sources": sources,
                "safety_notes": safety_notes,
                "improvements_made": improvements,
                "improvement_analysis": improvement_analysis,
                "agent": "reformer",
                "model": "gemini-pro",
                "metadata": {
                    "original_length": len(response),
                    "refined_length": len(refined_response),
                    "length_change": len(refined_response) - len(response),
                    "has_sources": len(sources) > 0,
                    "has_safety_notes": len(safety_notes) > 0,
                    "improvements_count": len(improvements)
                }
            }
            
            logger.info(
                "Response reform completed",
                response_id=response_id,
                length_change=len(refined_response) - len(response),
                improvements_count=len(improvements)
            )
            
            return result
            
        except Exception as e:
            logger.error("Response reform failed", response_id=response_id, error=str(e))
            return {
                "success": False,
                "response_id": response_id,
                "error": str(e)
            }
    
    def _analyze_improvements(self, original: str, refined: str) -> Dict[str, Any]:
        """Analyze what improvements were made to the response."""
        analysis = {
            "length_change": len(refined) - len(original),
            "structure_improved": False,
            "safety_enhanced": False,
            "sources_added": False,
            "clarity_improved": False,
            "completeness_improved": False
        }
        
        try:
            # Check for structure improvements
            structure_indicators = [
                "•", "-", "1.", "2.", "3.", "First", "Second", "Third",
                "Additionally", "Furthermore", "Moreover", "In conclusion"
            ]
            
            original_lower = original.lower()
            refined_lower = refined.lower()
            
            for indicator in structure_indicators:
                if indicator in refined_lower and indicator not in original_lower:
                    analysis["structure_improved"] = True
                    break
            
            # Check for safety enhancements
            safety_keywords = [
                "safety", "warning", "caution", "risk", "adverse",
                "contraindication", "side effect", "monitoring"
            ]
            
            for keyword in safety_keywords:
                if keyword in refined_lower and keyword not in original_lower:
                    analysis["safety_enhanced"] = True
                    break
            
            # Check for source additions
            source_indicators = [
                "according to", "based on", "as mentioned in",
                "the document states", "research shows", "studies indicate"
            ]
            
            for indicator in source_indicators:
                if indicator in refined_lower and indicator not in original_lower:
                    analysis["sources_added"] = True
                    break
            
            # Check for clarity improvements
            clarity_indicators = [
                "in other words", "to clarify", "specifically",
                "for example", "for instance", "that is"
            ]
            
            for indicator in clarity_indicators:
                if indicator in refined_lower and indicator not in original_lower:
                    analysis["clarity_improved"] = True
                    break
            
            # Check for completeness improvements
            completeness_indicators = [
                "additionally", "furthermore", "moreover",
                "it is also important", "another consideration"
            ]
            
            for indicator in completeness_indicators:
                if indicator in refined_lower and indicator not in original_lower:
                    analysis["completeness_improved"] = True
                    break
            
        except Exception as e:
            logger.error("Improvement analysis failed", error=str(e))
        
        return analysis
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        return {
            "name": "The Editor",
            "type": "reformer",
            "model": "gemini-pro",
            "role": "Response refinement and quality enhancement",
            "capabilities": [
                "Response structure improvement",
                "Safety enhancement",
                "Source citation addition",
                "Clarity improvement",
                "Completeness enhancement",
                "JSON format output"
            ],
            "optimizations": [
                "Structured JSON output format",
                "Enhancement-focused approach",
                "Safety and regulatory emphasis",
                "Research optimization"
            ]
        }
    
    def test_agent(self, test_cases: list) -> Dict[str, Any]:
        """
        Test the reformer agent with provided test cases.
        
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
                response = test_case.get("response", "")
                verifier_analysis = test_case.get("verifier_analysis", "")
                
                response_id = f"test_{i}_{hash(query) % 10000}"
                
                result = self.reform_response(query, context, response, verifier_analysis, response_id)
                
                if result["success"]:
                    # Check if response was actually improved
                    improvement_analysis = result.get("improvement_analysis", {})
                    has_improvements = any([
                        improvement_analysis.get("structure_improved", False),
                        improvement_analysis.get("safety_enhanced", False),
                        improvement_analysis.get("sources_added", False),
                        improvement_analysis.get("clarity_improved", False),
                        improvement_analysis.get("completeness_improved", False)
                    ])
                    
                    test_passed = has_improvements or len(result.get("improvements_made", [])) > 0
                    
                    if test_passed:
                        results["passed"] += 1
                    else:
                        results["failed"] += 1
                    
                    results["test_results"].append({
                        "test_id": i,
                        "query": query,
                        "improvements_made": result.get("improvements_made", []),
                        "improvement_analysis": improvement_analysis,
                        "passed": test_passed,
                        "refined_response": result.get("refined_response", "")[:100] + "..."
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
        
        logger.info("Reformer agent testing completed", results=results)
        return results
