"""
Simple Human Loop Manager for MIRAGE v2
======================================
Version simplifiée pour éviter les erreurs de segmentation
"""

class SimpleHumanLoopManager:
    """Simple human loop manager"""
    
    def __init__(self):
        self.validation_queue = []
        self.validation_history = []
    
    def evaluate_human_validation_needed(self, query: str, answer: str, response_id: str) -> dict:
        """Evaluate if human validation is needed"""
        # Simple logic: if query contains safety keywords, require validation
        safety_keywords = ["effets", "secondaires", "contre-indications", "interactions", "allergies", "grossesse", "allaitement", "enfants", "personnes âgées", "insuffisance", "rénale", "hépatique", "cardiaque", "respiratoire", "digestive", "neurologique", "psychiatrique", "dermatologique", "ophtalmologique", "urologique", "gynécologique", "pédiatrique", "gériatrique", "urgences", "soins intensifs", "réanimation", "chirurgie", "anesthésie", "radiologie", "laboratoire", "analyses", "examens", "bilan", "suivi", "surveillance", "monitoring", "évaluation", "efficacité", "tolérance", "sécurité", "qualité", "coût", "remboursement", "assurance", "mutuelle", "sécurité sociale", "ameli", "cpam", "assurance maladie", "complémentaire", "tiers payant", "avance de frais", "ticket modérateur", "franchise", "forfait", "participation", "reste à charge"]
        
        query_lower = query.lower()
        requires_validation = any(keyword.lower() in query_lower for keyword in safety_keywords)
        
        if requires_validation:
            validation_request = {
                "validation_type": "safety_review",
                "priority": "high",
                "reason": "Safety keywords detected - requires human validation"
            }
            
            return {
                "requires_human": True,
                "validation_request": validation_request
            }
        
        return {
            "requires_human": False,
            "validation_request": None
        }
    
    def get_validation_queue(self):
        """Get validation queue"""
        return self.validation_queue
    
    def get_validation_history(self, limit: int = 100):
        """Get validation history"""
        return self.validation_history[-limit:]
    
    def get_validation_statistics(self):
        """Get validation statistics"""
        return {
            "total_validations": len(self.validation_history),
            "pending_validations": len(self.validation_queue),
            "approved_validations": len([v for v in self.validation_history if v.get("decision") == "approved"]),
            "rejected_validations": len([v for v in self.validation_history if v.get("decision") == "rejected"])
        }
    
    def submit_human_validation(self, response_id: str, decision: str, notes: str = ""):
        """Submit human validation decision"""
        validation_record = {
            "response_id": response_id,
            "decision": decision,
            "notes": notes,
            "timestamp": "2025-09-21T09:00:00"
        }
        
        self.validation_history.append(validation_record)
        
        # Remove from queue if it exists
        self.validation_queue = [v for v in self.validation_queue if v.get("response_id") != response_id]
        
        return True
