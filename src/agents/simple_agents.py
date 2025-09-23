"""
Simple Agents for MIRAGE v2
==========================
Version simplifiée pour éviter les erreurs de segmentation
"""

class SimpleGeneratorAgent:
    """Simple generator agent"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def generate_response(self, query: str, context: list) -> dict:
        """Generate response"""
        return {
            "success": True,
            "answer": "This is a simple response for testing purposes.",
            "confidence": 0.8
        }

class SimpleVerifierAgent:
    """Simple verifier agent"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def verify_response(self, query: str, context: list, response: str) -> dict:
        """Verify response"""
        return {
            "success": True,
            "vote": "OUI",
            "confidence": 0.8,
            "accuracy_score": 0.8,
            "completeness_score": 0.8,
            "verification_analysis": "Simple verification for testing purposes."
        }

class SimpleReformerAgent:
    """Simple reformer agent"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def reform_response(self, query: str, context: list, response: str, verification: dict) -> dict:
        """Reform response"""
        return {
            "success": True,
            "reformed_response": response,
            "confidence": 0.8
        }

class SimpleTranslatorAgent:
    """Simple translator agent"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def translate_response(self, response: str, target_language: str) -> dict:
        """Translate response"""
        return {
            "success": True,
            "translated_response": response,
            "target_language": target_language
        }
