"""
Verifier Agent for MIRAGE v2.

Quality assurance and validation agent with voting system.
"""

import os
from typing import Dict, Any, Optional
import structlog
import google.generativeai as genai
import re

logger = structlog.get_logger(__name__)


class VerifierAgent:
    """Quality assurance and validation agent for pharmaceutical responses."""
    
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
        
        logger.info("VerifierAgent initialized", model="gemini-pro")
    
    def verify_response(
        self,
        query: str,
        context: str,
        response: str,
        response_id: str
    ) -> Dict[str, Any]:
        """
        Verify a generated response for accuracy and quality.
        
        Args:
            query: Original research question
            context: Context used for generation
            response: Generated response to verify
            response_id: Unique identifier for this response
            
        Returns:
            Dictionary with verification results and vote
        """
        try:
            logger.info("Verifying response", response_id=response_id, response_length=len(response))
            
            # Format the verification prompt
            user_prompt = self.prompts.format_user_prompt(
                "verifier",
                query=query,
                context=context,
                response=response
            )
            
            # Generate verification analysis
            verification_response = self.model.generate_content(user_prompt)
            
            if not verification_response.text:
                logger.error("Empty verification response", response_id=response_id)
                return {
                    "success": False,
                    "response_id": response_id,
                    "error": "Empty verification response"
                }
            
            # Parse the verification response
            verification_text = verification_response.text.strip()
            
            # Extract vote
            vote = self._extract_vote(verification_text)
            
            # Analyze verification quality
            verification_analysis = self._analyze_verification(verification_text, vote)
            
            result = {
                "success": True,
                "response_id": response_id,
                "query": query,
                "original_response": response,
                "verification_analysis": verification_text,
                "vote": vote,
                "confidence": verification_analysis["confidence"],
                "issues_found": verification_analysis["issues_found"],
                "safety_concerns": verification_analysis["safety_concerns"],
                "accuracy_score": verification_analysis["accuracy_score"],
                "completeness_score": verification_analysis["completeness_score"],
                "agent": "verifier",
                "model": "gemini-pro",
                "metadata": {
                    "verification_length": len(verification_text),
                    "has_vote": vote is not None,
                    "vote_confidence": verification_analysis["vote_confidence"]
                }
            }
            
            logger.info(
                "Response verification completed",
                response_id=response_id,
                vote=vote,
                confidence=verification_analysis["confidence"]
            )
            
            return result
            
        except Exception as e:
            logger.error("Response verification failed", response_id=response_id, error=str(e))
            return {
                "success": False,
                "response_id": response_id,
                "error": str(e)
            }
    
    def _extract_vote(self, verification_text: str) -> Optional[str]:
        """Extract vote from verification response."""
        # Look for VOTE: pattern
        vote_pattern = r'VOTE:\s*(OUI|NON)'
        match = re.search(vote_pattern, verification_text, re.IGNORECASE)
        
        if match:
            vote = match.group(1).upper()
            return vote
        
        # Fallback: look for OUI/NON keywords
        if 'OUI' in verification_text.upper():
            return 'OUI'
        elif 'NON' in verification_text.upper():
            return 'NON'
        
        return None
    
    def _analyze_verification(self, verification_text: str, vote: Optional[str]) -> Dict[str, Any]:
        """Analyze the quality of verification response."""
        analysis = {
            "confidence": 0.0,
            "issues_found": [],
            "safety_concerns": [],
            "accuracy_score": 0.0,
            "completeness_score": 0.0,
            "vote_confidence": 0.0
        }
        
        try:
            text_lower = verification_text.lower()
            
            # Extract issues mentioned
            issue_keywords = [
                "inaccurate", "incorrect", "wrong", "error", "mistake",
                "incomplete", "missing", "lacks", "insufficient",
                "unclear", "confusing", "ambiguous", "vague"
            ]
            
            for keyword in issue_keywords:
                if keyword in text_lower:
                    analysis["issues_found"].append(keyword)
            
            # Extract safety concerns
            safety_keywords = [
                "safety", "dangerous", "harmful", "risk", "warning",
                "contraindication", "adverse", "side effect", "toxicity"
            ]
            
            for keyword in safety_keywords:
                if keyword in text_lower:
                    analysis["safety_concerns"].append(keyword)
            
            # Calculate confidence based on vote presence and analysis quality
            if vote is not None:
                analysis["vote_confidence"] = 0.8
                
                # Increase confidence if analysis is detailed
                if len(verification_text) > 100:
                    analysis["vote_confidence"] += 0.1
                
                # Increase confidence if specific issues are mentioned
                if analysis["issues_found"]:
                    analysis["vote_confidence"] += 0.1
            
            # Calculate accuracy score (simplified)
            if vote == "OUI":
                analysis["accuracy_score"] = 0.8
            elif vote == "NON":
                analysis["accuracy_score"] = 0.2
            else:
                analysis["accuracy_score"] = 0.5
            
            # Calculate completeness score
            if "complete" in text_lower or "comprehensive" in text_lower:
                analysis["completeness_score"] = 0.8
            elif "incomplete" in text_lower or "missing" in text_lower:
                analysis["completeness_score"] = 0.3
            else:
                analysis["completeness_score"] = 0.6
            
            # Overall confidence
            analysis["confidence"] = (
                analysis["vote_confidence"] * 0.4 +
                analysis["accuracy_score"] * 0.3 +
                analysis["completeness_score"] * 0.3
            )
            
        except Exception as e:
            logger.error("Verification analysis failed", error=str(e))
        
        return analysis
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        return {
            "name": "The Analyst",
            "type": "verifier",
            "model": "gemini-pro",
            "role": "Quality assurance and validation of generated responses",
            "capabilities": [
                "Response accuracy validation",
                "Completeness assessment",
                "Safety concern detection",
                "Voting system (OUI/NON)",
                "Quality scoring"
            ],
            "optimizations": [
                "Explicit voting system",
                "Comprehensive validation criteria",
                "Safety-first approach",
                "Context verification requirement"
            ]
        }
    
    def test_agent(self, test_cases: list) -> Dict[str, Any]:
        """
        Test the verifier agent with provided test cases.
        
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
                expected_vote = test_case.get("expected_vote", None)
                
                response_id = f"test_{i}_{hash(query) % 10000}"
                
                result = self.verify_response(query, context, response, response_id)
                
                if result["success"]:
                    # Check if vote matches expectation
                    actual_vote = result.get("vote")
                    test_passed = (actual_vote == expected_vote) if expected_vote else True
                    
                    if test_passed:
                        results["passed"] += 1
                    else:
                        results["failed"] += 1
                    
                    results["test_results"].append({
                        "test_id": i,
                        "query": query,
                        "expected_vote": expected_vote,
                        "actual_vote": actual_vote,
                        "confidence": result.get("confidence", 0.0),
                        "passed": test_passed,
                        "verification": result.get("verification_analysis", "")[:100] + "..."
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
        
        logger.info("Verifier agent testing completed", results=results)
        return results
