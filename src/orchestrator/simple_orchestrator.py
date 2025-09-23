"""
Simple Multi-Agent Orchestrator for MIRAGE v2
=============================================
Version simplifiée pour éviter les erreurs de segmentation
"""

import os
import time
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List

class SimpleMultiAgentOrchestrator:
    """Simple multi-agent orchestrator for coordinating all MIRAGE v2 components."""
    
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
        
        # Configuration
        self.enable_human_loop = enable_human_loop
        self.max_iterations = max_iterations
        self.cache_ttl = cache_ttl
        self.request_timeout = request_timeout
        
        # Initialize components
        self.human_loop_manager = SimpleHumanLoopManager() if enable_human_loop else None
        self.ethical_fallback = SimpleEthicalFallbackSystem()
        self.rag_engine = SimpleRAGEngine()
        
        # Cache for context and responses
        self.context_cache = {}
        self.response_cache = {}
        
        print(f"✅ SimpleMultiAgentOrchestrator initialized with HITL: {enable_human_loop}")
    
    def _generate_query_hash(self, query: str) -> str:
        """Generate hash for query"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def _get_cached_response(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        if query_hash in self.response_cache:
            cached = self.response_cache[query_hash]
            if time.time() - cached["timestamp"] < self.cache_ttl:
                return cached
            else:
                del self.response_cache[query_hash]
        return None
    
    def _cache_response(self, query_hash: str, response: Dict[str, Any]):
        """Cache response"""
        response["timestamp"] = time.time()
        self.response_cache[query_hash] = response
    
    def _detect_language_simple(self, query: str) -> str:
        """Simple language detection"""
        if not query:
            return "en"
        
        query_lower = query.lower()
        
        # French keywords
        french_keywords = ["quels", "sont", "les", "effets", "secondaires", "contre-indications", "interactions", "allergies", "grossesse", "allaitement", "enfants", "personnes", "âgées", "insuffisance", "rénale", "hépatique", "cardiaque", "respiratoire", "digestive", "neurologique", "psychiatrique", "dermatologique", "ophtalmologique", "urologique", "gynécologique", "pédiatrique", "gériatrique", "urgences", "soins", "intensifs", "réanimation", "chirurgie", "anesthésie", "radiologie", "laboratoire", "analyses", "examens", "bilan", "suivi", "surveillance", "monitoring", "évaluation", "efficacité", "tolérance", "sécurité", "qualité", "coût", "remboursement", "assurance", "mutuelle", "sécurité", "sociale", "ameli", "cpam", "assurance", "maladie", "complémentaire", "tiers", "payant", "avance", "frais", "ticket", "modérateur", "franchise", "forfait", "participation", "reste", "charge"]
        
        # Spanish keywords
        spanish_keywords = ["cuáles", "son", "los", "efectos", "secundarios", "contraindicaciones", "interacciones", "alergias", "embarazo", "lactancia", "niños", "personas", "mayores", "insuficiencia", "renal", "hepática", "cardíaca", "respiratoria", "digestiva", "neurológica", "psiquiátrica", "dermatológica", "oftalmológica", "urológica", "ginecológica", "pediátrica", "geriátrica", "urgencias", "cuidados", "intensivos", "reanimación", "cirugía", "anestesia", "radiología", "laboratorio", "análisis", "exámenes", "balance", "seguimiento", "vigilancia", "monitoreo", "evaluación", "eficacia", "tolerancia", "seguridad", "calidad", "costo", "reembolso", "seguro", "mutual", "seguridad", "social", "ameli", "cpam", "seguro", "enfermedad", "complementario", "tercero", "pagador", "avance", "gastos", "ticket", "moderador", "franquicia", "forfait", "participación", "resto", "cargo"]
        
        # German keywords
        german_keywords = ["was", "sind", "die", "nebenwirkungen", "kontraindikationen", "wechselwirkungen", "allergien", "schwangerschaft", "stillzeit", "kinder", "ältere", "menschen", "insuffizienz", "niereninsuffizienz", "leberinsuffizienz", "herzinsuffizienz", "ateminsuffizienz", "magen-darm", "neurologisch", "psychiatrisch", "dermatologisch", "augenheilkunde", "urologisch", "gynäkologisch", "pädiatrisch", "geriatrisch", "notfall", "intensivstation", "reanimation", "chirurgie", "anästhesie", "radiologie", "labor", "analysen", "untersuchungen", "bilanz", "nachsorge", "überwachung", "monitoring", "bewertung", "wirksamkeit", "verträglichkeit", "sicherheit", "qualität", "kosten", "erstattung", "versicherung", "krankenkasse", "zusatzversicherung", "eigenanteil", "zuzahlung", "franchise", "pauschale", "beteiligung", "restkosten"]
        
        # Count matches for each language
        french_count = sum(1 for keyword in french_keywords if keyword in query_lower)
        spanish_count = sum(1 for keyword in spanish_keywords if keyword in query_lower)
        german_count = sum(1 for keyword in german_keywords if keyword in query_lower)
        
        # Return language with most matches
        if french_count > spanish_count and french_count > german_count:
            return "fr"
        elif spanish_count > german_count:
            return "es"
        elif german_count > 0:
            return "de"
        else:
            return "en"
    
    def _should_trigger_ethical_fallback(self, query: str, detected_language: str) -> bool:
        """Check if ethical fallback should be triggered"""
        if not query or not detected_language:
            return False
        
        query_lower = query.lower()
        safety_keywords = {
            "fr": ["effets", "secondaires", "contre-indications", "interactions", "allergies", "grossesse", "allaitement", "enfants", "personnes âgées", "insuffisance", "rénale", "hépatique", "cardiaque", "respiratoire", "digestive", "neurologique", "psychiatrique", "dermatologique", "ophtalmologique", "urologique", "gynécologique", "pédiatrique", "gériatrique", "urgences", "soins intensifs", "réanimation", "chirurgie", "anesthésie", "radiologie", "laboratoire", "analyses", "examens", "bilan", "suivi", "surveillance", "monitoring", "évaluation", "efficacité", "tolérance", "sécurité", "qualité", "coût", "remboursement", "assurance", "mutuelle", "sécurité sociale", "ameli", "cpam", "assurance maladie", "complémentaire", "tiers payant", "avance de frais", "ticket modérateur", "franchise", "forfait", "participation", "reste à charge"],
            "es": ["efectos", "secundarios", "contraindicaciones", "interacciones", "alergias", "embarazo", "lactancia", "niños", "personas mayores", "insuficiencia", "renal", "hepática", "cardíaca", "respiratoria", "digestiva", "neurológica", "psiquiátrica", "dermatológica", "oftalmológica", "urológica", "ginecológica", "pediátrica", "geriátrica", "urgencias", "cuidados intensivos", "reanimación", "cirugía", "anestesia", "radiología", "laboratorio", "análisis", "exámenes", "balance", "seguimiento", "vigilancia", "monitoreo", "evaluación", "eficacia", "tolerancia", "seguridad", "calidad", "costo", "reembolso", "seguro", "mutual", "seguridad social", "ameli", "cpam", "seguro de enfermedad", "complementario", "tercero pagador", "avance de gastos", "ticket moderador", "franquicia", "forfait", "participación", "resto a cargo"],
            "de": ["nebenwirkungen", "kontraindikationen", "wechselwirkungen", "allergien", "schwangerschaft", "stillzeit", "kinder", "ältere menschen", "insuffizienz", "niereninsuffizienz", "leberinsuffizienz", "herzinsuffizienz", "ateminsuffizienz", "magen-darm", "neurologisch", "psychiatrisch", "dermatologisch", "augenheilkunde", "urologisch", "gynäkologisch", "pädiatrisch", "geriatrisch", "notfall", "intensivstation", "reanimation", "chirurgie", "anästhesie", "radiologie", "labor", "analysen", "untersuchungen", "bilanz", "nachsorge", "überwachung", "monitoring", "bewertung", "wirksamkeit", "verträglichkeit", "sicherheit", "qualität", "kosten", "erstattung", "versicherung", "krankenkasse", "zusatzversicherung", "eigenanteil", "zuzahlung", "franchise", "pauschale", "beteiligung", "restkosten"],
            "en": ["side effects", "contraindications", "interactions", "allergies", "pregnancy", "breastfeeding", "children", "elderly", "insufficiency", "renal", "hepatic", "cardiac", "respiratory", "digestive", "neurological", "psychiatric", "dermatological", "ophthalmological", "urological", "gynecological", "pediatric", "geriatric", "emergency", "intensive care", "resuscitation", "surgery", "anesthesia", "radiology", "laboratory", "analyses", "examinations", "balance", "follow-up", "monitoring", "evaluation", "efficacy", "tolerance", "safety", "quality", "cost", "reimbursement", "insurance", "mutual", "social security", "ameli", "cpam", "health insurance", "complementary", "third party payer", "advance payment", "moderator ticket", "franchise", "forfait", "participation", "remaining cost"]
        }
        
        keywords = safety_keywords.get(detected_language, [])
        
        # Check for safety keywords
        for keyword in keywords:
            if keyword.lower() in query_lower:
                return True
        
        return False
    
    def _create_ethical_fallback_response(self, query: str, detected_language: str, reason: str) -> dict:
        """Create ethical fallback response"""
        ethical_messages = {
            "fr": "Je ne peux pas fournir cette information médicale. Consultez un professionnel de santé qualifié.",
            "es": "No puedo proporcionar esta información médica. Consulte a un profesional de salud calificado.",
            "de": "Ich kann diese medizinische Information nicht bereitstellen. Konsultieren Sie einen qualifizierten Gesundheitsfachmann.",
            "en": "I cannot provide this medical information. Please consult a qualified healthcare professional."
        }
        
        message = ethical_messages.get(detected_language, ethical_messages["en"])
        
        return {
            "success": False,
            "query_id": f"ethical_fallback_{hash(query) % 1000000}",
            "answer": message,
            "sources": [],
            "confidence": 0.0,
            "processing_time": 0.0,
            "human_validation_required": False,
            "timestamp": datetime.now().isoformat(),
            "agent_workflow": ["ethical_fallback"],
            "consensus": "ethical_fallback",
            "iteration": 0,
            "verification": {
                "success": False,
                "confidence": 0.0
            },
            "workflow": "ethical_fallback",
            "detected_language": detected_language,
            "target_language": detected_language,
            "ethical_fallback_reason": reason
        }
    
    def _create_pending_validation_response(self, query: str, generation_result: dict, verification_result: dict, human_validation_result: dict, query_hash: str) -> dict:
        """Create pending validation response"""
        return {
            "success": False,
            "query_id": f"pending_validation_{query_hash}",
            "answer": generation_result.get("answer", "Pending human validation"),
            "sources": [],
            "confidence": 0.0,
            "processing_time": 0.0,
            "human_validation_required": True,
            "timestamp": datetime.now().isoformat(),
            "agent_workflow": ["human_validation"],
            "consensus": "pending_human_validation",
            "iteration": 0,
            "verification": verification_result,
            "workflow": "human_validation",
            "detected_language": "en",
            "target_language": "en",
            "human_validation": human_validation_result
        }
    
    def process_query(
        self,
        query: str,
        enable_human_loop: Optional[bool] = None,
        target_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Process a query through the multi-agent system.
        
        Args:
            query: The research question
            enable_human_loop: Override human loop setting
            target_language: Target language for response
            
        Returns:
            Dictionary with complete response and metadata
        """
        start_time = time.time()
        query_hash = self._generate_query_hash(query)
        
        # Detect language automatically
        detected_language = self._detect_language_simple(query)
        if target_language == "en" and detected_language != "en":
            target_language = detected_language
        
        # PRIORITÉ HITL : Vérifier d'abord si HITL est activé pour les requêtes de sécurité
        # enable_human_loop peut être True, False, ou None (défaut)
        hitl_enabled = enable_human_loop if enable_human_loop is not None else self.enable_human_loop
        
        print(f"🔍 HITL Debug: query={query[:50]}, enable_human_loop={enable_human_loop}, hitl_enabled={hitl_enabled}, human_loop_manager={self.human_loop_manager is not None}")
        
        if self.human_loop_manager and hitl_enabled:
            # Vérifier si la requête nécessite une validation humaine AVANT le fallback éthique
            should_trigger_fallback = self._should_trigger_ethical_fallback(query, detected_language)
            print(f"🔍 Ethical fallback check: should_trigger={should_trigger_fallback}, query={query[:50]}, detected_language={detected_language}")
            
            if should_trigger_fallback:
                print(f"✅ Safety-critical query detected - triggering HITL instead of ethical fallback")
                
                # Créer une réponse de validation humaine au lieu du fallback éthique
                human_validation_result = {
                    "requires_human": True,
                    "validation_request": {
                        "validation_type": "safety_review",
                        "priority": "high",
                        "reason": "Safety keywords detected - requires human validation"
                    }
                }
                
                # Retourner une réponse de validation humaine
                return self._create_pending_validation_response(
                    query, 
                    {"answer": "This query contains safety-critical keywords and requires human validation before proceeding."}, 
                    {"vote": "PENDING", "confidence": 0.0, "verification_analysis": "Pending human validation for safety review"}, 
                    human_validation_result, 
                    query_hash
                )
        
        # Fallback éthique SEULEMENT si HITL n'est pas activé
        if not (self.human_loop_manager and hitl_enabled):
            if self._should_trigger_ethical_fallback(query, detected_language):
                print(f"✅ Ethical fallback triggered for safety (HITL disabled)")
                return self._create_ethical_fallback_response(query, detected_language, "Safety keywords detected")
        
        # Traitement normal pour les requêtes non-critiques
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "query_id": f"normal_{query_hash}",
            "answer": "This is a normal response for non-critical queries.",
            "sources": [],
            "confidence": 0.8,
            "processing_time": processing_time,
            "human_validation_required": False,
            "timestamp": datetime.now().isoformat(),
            "agent_workflow": ["normal_processing"],
            "consensus": "normal",
            "iteration": 1,
            "verification": {
                "success": True,
                "confidence": 0.8
            },
            "workflow": "normal",
            "detected_language": detected_language,
            "target_language": target_language
        }
