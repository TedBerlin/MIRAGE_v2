"""
Human-in-the-Loop Manager for MIRAGE v2.

Manages human validation and intervention in the orchestration process.
"""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class HumanValidationType(Enum):
    """Types of human validation required."""
    SAFETY_REVIEW = "safety_review"
    MEDICAL_APPROVAL = "medical_approval"
    QUALITY_ASSURANCE = "quality_assurance"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    CRITICAL_DECISION = "critical_decision"


class HumanValidationStatus(Enum):
    """Status of human validation."""
    PENDING = "pending"
    APPROVED = "approved"
    MODIFIED = "modified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class HumanLoopManager:
    """Manages human-in-the-loop validation and intervention."""
    
    def __init__(
        self,
        safety_keywords: List[str] = None,
        medical_keywords: List[str] = None,
        regulatory_keywords: List[str] = None,
        validation_timeout: int = 3600  # 1 hour
    ):
        # Keywords for triggering human validation (multilingual)
        self.safety_keywords = safety_keywords or [
            # English
            "contraindication", "adverse", "side effect", "toxicity", "overdose",
            "allergy", "pregnancy", "lactation", "pediatric", "geriatric",
            "warning", "caution", "danger", "risk", "monitoring",
            # French
            "contre-indication", "effet", "secondaire", "toxicité", "surdose",
            "allergie", "grossesse", "allaitement", "pédiatrique", "gériatrique",
            "avertissement", "précaution", "danger", "risque", "surveillance",
            # Spanish
            "contraindicación", "adverso", "efecto", "secundario", "toxicidad", "sobredosis",
            "alergia", "embarazo", "lactancia", "pediátrico", "geriátrico",
            "advertencia", "precaución", "peligro", "riesgo", "monitoreo",
            # German
            "kontraindikation", "unerwünscht", "nebenwirkung", "toxizität", "überdosis",
            "allergie", "schwangerschaft", "stillzeit", "pädiatrisch", "geriatrisch",
            "warnung", "vorsicht", "gefahr", "risiko", "überwachung"
        ]
        
        self.medical_keywords = medical_keywords or [
            # English
            "diagnosis", "treatment", "therapy", "medication", "dosage",
            "prescription", "clinical", "trial", "study", "efficacy",
            "safety", "pharmacokinetics", "pharmacodynamics",
            # French
            "diagnostic", "traitement", "thérapie", "médicament", "posologie",
            "ordonnance", "clinique", "essai", "étude", "efficacité",
            "sécurité", "pharmacocinétique", "pharmacodynamie",
            # Spanish
            "diagnóstico", "tratamiento", "terapia", "medicamento", "dosificación",
            "receta", "clínico", "ensayo", "estudio", "eficacia",
            "seguridad", "farmacocinética", "farmacodinamia",
            # German
            "diagnose", "behandlung", "therapie", "medikament", "dosierung",
            "rezept", "klinisch", "versuch", "studie", "wirksamkeit",
            "sicherheit", "pharmakokinetik", "pharmakodynamik"
        ]
        
        self.regulatory_keywords = regulatory_keywords or [
            # English
            "fda", "ema", "regulatory", "approval", "compliance",
            "guideline", "standard", "protocol", "informed consent",
            # French
            "ansm", "réglementaire", "approbation", "conformité",
            "ligne", "directrice", "norme", "protocole", "consentement",
            # Spanish
            "aemps", "regulatorio", "aprobación", "cumplimiento",
            "guía", "estándar", "protocolo", "consentimiento",
            # German
            "b farm", "regulatorisch", "zulassung", "compliance",
            "richtlinie", "standard", "protokoll", "einverständnis"
        ]
        
        self.validation_timeout = validation_timeout
        
        # Human validation queue and history
        self.validation_queue = {}
        self.validation_history = []
        
        logger.info(
            "HumanLoopManager initialized",
            safety_keywords_count=len(self.safety_keywords),
            medical_keywords_count=len(self.medical_keywords),
            regulatory_keywords_count=len(self.regulatory_keywords),
            validation_timeout=validation_timeout
        )
    
    def evaluate_human_validation_needed(
        self,
        query: str,
        response: str,
        response_id: str
    ) -> Dict[str, Any]:
        """
        Evaluate if human validation is needed for a response.
        
        Args:
            query: Original query
            response: Generated response
            response_id: Response identifier
            
        Returns:
            Evaluation result with validation requirements
        """
        try:
            # Analyze content for validation triggers
            validation_triggers = self._analyze_validation_triggers(query, response)
            
            # Determine if human validation is needed
            requires_human = self._determine_human_validation_need(validation_triggers)
            
            if requires_human:
                # Create validation request
                validation_request = self._create_validation_request(
                    query, response, response_id, validation_triggers
                )
                
                # Add to queue
                self.validation_queue[response_id] = validation_request
                
                logger.info(
                    "Human validation required",
                    response_id=response_id,
                    validation_type=validation_request["validation_type"].value,
                    triggers=validation_triggers
                )
                
                return {
                    "requires_human": True,
                    "validation_request": validation_request,
                    "triggers": validation_triggers
                }
            else:
                return {
                    "requires_human": False,
                    "reason": "No validation triggers detected"
                }
                
        except Exception as e:
            logger.error("Human validation evaluation failed", response_id=response_id, error=str(e))
            return {
                "requires_human": False,
                "error": str(e)
            }
    
    def _analyze_validation_triggers(self, query: str, response: str) -> Dict[str, Any]:
        """Analyze content for validation triggers."""
        triggers = {
            "safety_triggers": [],
            "medical_triggers": [],
            "regulatory_triggers": [],
            "confidence_issues": [],
            "complexity_issues": []
        }
        
        # Combine query and response for analysis
        content = f"{query} {response}".lower()
        
        # Check for safety keywords
        for keyword in self.safety_keywords:
            if keyword in content:
                triggers["safety_triggers"].append(keyword)
        
        # Check for medical keywords
        for keyword in self.medical_keywords:
            if keyword in content:
                triggers["medical_triggers"].append(keyword)
        
        # Check for regulatory keywords
        for keyword in self.regulatory_keywords:
            if keyword in content:
                triggers["regulatory_triggers"].append(keyword)
        
        # Check for confidence issues (multilingual)
        confidence_indicators = [
            # English
            "uncertain", "unclear", "may be", "could be", "possibly",
            "might", "suggest", "indicate", "appears to",
            # French
            "incertain", "imprécis", "peut être", "pourrait être", "possiblement",
            "pourrait", "suggère", "indique", "semble",
            # Spanish
            "incierto", "impreciso", "puede ser", "podría ser", "posiblemente",
            "podría", "sugiere", "indica", "parece",
            # German
            "unsicher", "unklar", "könnte sein", "möglich", "möglicherweise",
            "könnte", "schlägt vor", "zeigt", "scheint"
        ]
        
        for indicator in confidence_indicators:
            if indicator in content:
                triggers["confidence_issues"].append(indicator)
        
        # Check for complexity issues (multilingual)
        complexity_indicators = [
            # English
            "complex", "complicated", "multiple", "various", "different",
            "several", "numerous", "extensive", "comprehensive",
            # French
            "complexe", "compliqué", "multiple", "divers", "différent",
            "plusieurs", "nombreux", "étendu", "complet",
            # Spanish
            "complejo", "complicado", "múltiple", "varios", "diferente",
            "varios", "numerosos", "extenso", "completo",
            # German
            "komplex", "kompliziert", "mehrfach", "verschieden", "unterschiedlich",
            "mehrere", "zahlreich", "umfangreich", "umfassend"
        ]
        
        for indicator in complexity_indicators:
            if indicator in content:
                triggers["complexity_issues"].append(indicator)
        
        return triggers
    
    def _determine_human_validation_need(self, triggers: Dict[str, Any]) -> bool:
        """Determine if human validation is needed based on triggers."""
        # Always require validation for safety concerns
        if triggers["safety_triggers"]:
            return True
        
        # Require validation for regulatory compliance
        if triggers["regulatory_triggers"]:
            return True
        
        # Require validation for complex medical decisions
        if triggers["medical_triggers"] and triggers["complexity_issues"]:
            return True
        
        # Require validation for high uncertainty
        if len(triggers["confidence_issues"]) >= 3:
            return True
        
        return False
    
    def _create_validation_request(
        self,
        query: str,
        response: str,
        response_id: str,
        triggers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a human validation request."""
        # Determine validation type
        validation_type = self._determine_validation_type(triggers)
        
        # Determine priority
        priority = self._determine_priority(triggers, validation_type)
        
        return {
            "id": response_id,
            "query": query,
            "response": response,
            "validation_type": validation_type,
            "priority": priority,
            "triggers": triggers,
            "status": HumanValidationStatus.PENDING,
            "created_at": datetime.now().isoformat(),
            "expires_at": datetime.fromtimestamp(
                time.time() + self.validation_timeout
            ).isoformat(),
            "assigned_to": None,
            "validation_notes": None,
            "human_decision": None,
            "modified_response": None
        }
    
    def _determine_validation_type(self, triggers: Dict[str, Any]) -> HumanValidationType:
        """Determine the type of validation needed."""
        if triggers["safety_triggers"]:
            return HumanValidationType.SAFETY_REVIEW
        elif triggers["regulatory_triggers"]:
            return HumanValidationType.REGULATORY_COMPLIANCE
        elif triggers["medical_triggers"]:
            return HumanValidationType.MEDICAL_APPROVAL
        else:
            return HumanValidationType.QUALITY_ASSURANCE
    
    def _determine_priority(self, triggers: Dict[str, Any], validation_type: HumanValidationType) -> int:
        """Determine validation priority (1-5, 5 being highest)."""
        priority = 1
        
        # Safety concerns get highest priority
        if validation_type == HumanValidationType.SAFETY_REVIEW:
            priority = 5
        elif validation_type == HumanValidationType.REGULATORY_COMPLIANCE:
            priority = 4
        elif validation_type == HumanValidationType.MEDICAL_APPROVAL:
            priority = 3
        else:
            priority = 2
        
        # Increase priority for multiple triggers
        total_triggers = sum(len(triggers[key]) for key in triggers)
        if total_triggers > 5:
            priority = min(5, priority + 1)
        
        return priority
    
    def submit_human_validation(
        self,
        response_id: str,
        human_decision: str,
        validation_notes: str = "",
        modified_response: str = ""
    ) -> bool:
        """
        Submit human validation decision.
        
        Args:
            response_id: Response identifier
            human_decision: Human decision (approve, modify, reject)
            validation_notes: Notes from human validator
            modified_response: Modified response if applicable
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if response_id not in self.validation_queue:
                logger.error("Validation request not found", response_id=response_id)
                return False
            
            validation_request = self.validation_queue[response_id]
            
            # Update validation request
            validation_request["status"] = HumanValidationStatus.APPROVED if human_decision == "approve" else HumanValidationStatus.MODIFIED if human_decision == "modify" else HumanValidationStatus.REJECTED
            validation_request["human_decision"] = human_decision
            validation_request["validation_notes"] = validation_notes
            validation_request["modified_response"] = modified_response
            validation_request["validated_at"] = datetime.now().isoformat()
            validation_request["validated_by"] = "human_validator"  # In real implementation, this would be the actual user ID
            
            # Move to history
            self.validation_history.append(validation_request)
            del self.validation_queue[response_id]
            
            logger.info(
                "Human validation submitted",
                response_id=response_id,
                decision=human_decision,
                validation_type=validation_request["validation_type"].value
            )
            
            return True
            
        except Exception as e:
            logger.error("Human validation submission failed", response_id=response_id, error=str(e))
            return False
    
    def get_validation_queue(self) -> List[Dict[str, Any]]:
        """Get current validation queue."""
        return list(self.validation_queue.values())
    
    def get_validation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get validation history."""
        return self.validation_history[-limit:]
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation statistics."""
        total_validations = len(self.validation_history) + len(self.validation_queue)
        
        if total_validations == 0:
            return {
                "total_validations": 0,
                "pending_validations": 0,
                "completed_validations": 0,
                "validation_types": {},
                "average_processing_time": 0.0,
                "approval_rate": 0.0
            }
        
        # Count by validation type
        validation_types = {}
        for validation in self.validation_history:
            vtype = validation["validation_type"].value
            validation_types[vtype] = validation_types.get(vtype, 0) + 1
        
        # Count by status
        status_counts = {}
        for validation in self.validation_history:
            status = validation["status"].value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate average processing time
        completed_validations = [v for v in self.validation_history if v["status"] != HumanValidationStatus.PENDING]
        avg_processing_time = 0.0
        if completed_validations:
            processing_times = []
            for validation in completed_validations:
                if "validated_at" in validation:
                    created_time = datetime.fromisoformat(validation["created_at"]).timestamp()
                    validated_time = datetime.fromisoformat(validation["validated_at"]).timestamp()
                    processing_times.append(validated_time - created_time)
            
            if processing_times:
                avg_processing_time = sum(processing_times) / len(processing_times)
        
        # Calculate approval rate
        approved_count = status_counts.get("approved", 0) + status_counts.get("modified", 0)
        approval_rate = approved_count / len(self.validation_history) if self.validation_history else 0.0
        
        return {
            "total_validations": total_validations,
            "pending_validations": len(self.validation_queue),
            "completed_validations": len(self.validation_history),
            "validation_types": validation_types,
            "status_counts": status_counts,
            "average_processing_time": avg_processing_time,
            "approval_rate": approval_rate
        }
    
    def cleanup_expired_validations(self):
        """Clean up expired validation requests."""
        current_time = time.time()
        expired_count = 0
        
        expired_ids = []
        for response_id, validation_request in self.validation_queue.items():
            expires_at = datetime.fromisoformat(validation_request["expires_at"]).timestamp()
            if current_time > expires_at:
                expired_ids.append(response_id)
        
        for response_id in expired_ids:
            validation_request = self.validation_queue[response_id]
            validation_request["status"] = HumanValidationStatus.EXPIRED
            validation_request["expired_at"] = datetime.now().isoformat()
            
            self.validation_history.append(validation_request)
            del self.validation_queue[response_id]
            expired_count += 1
        
        if expired_count > 0:
            logger.info("Cleaned up expired validations", expired_count=expired_count)
        
        return expired_count
