"""
Ethical Fallback System for MIRAGE v2
=====================================
Respects the initial brief: "Je ne sais pas" in all 4 languages
Implements ethical medical AI principles
"""

import structlog
from typing import Dict, Any, Optional

logger = structlog.get_logger(__name__)

class EthicalFallbackSystem:
    """System for ethical fallback responses respecting medical safety"""
    
    def __init__(self):
        self.ethical_messages = {
            "fr": "Je ne peux pas fournir cette information médicale. Consultez un professionnel de santé qualifié.",
            "es": "No puedo proporcionar esta información médica. Consulte a un profesional de salud calificado.",
            "de": "Ich kann diese medizinische Information nicht bereitstellen. Konsultieren Sie einen qualifizierten Gesundheitsfachmann.",
            "en": "I cannot provide this medical information. Please consult a qualified healthcare professional."
        }
        
        self.safety_keywords = {
            "fr": ["effets", "secondaires", "contre-indications", "interactions", "allergies", "grossesse", "allaitement", "enfants", "personnes âgées", "insuffisance", "rénale", "hépatique", "cardiaque", "respiratoire", "digestive", "neurologique", "psychiatrique", "dermatologique", "ophtalmologique", "urologique", "gynécologique", "pédiatrique", "gériatrique", "urgences", "soins intensifs", "réanimation", "chirurgie", "anesthésie", "radiologie", "laboratoire", "analyses", "examens", "bilan", "suivi", "surveillance", "monitoring", "évaluation", "efficacité", "tolérance", "sécurité", "qualité", "coût", "remboursement", "assurance", "mutuelle", "sécurité sociale", "ameli", "cpam", "assurance maladie", "complémentaire", "tiers payant", "avance de frais", "ticket modérateur", "franchise", "forfait", "participation", "reste à charge"],
            "es": ["efectos", "secundarios", "contraindicaciones", "interacciones", "alergias", "embarazo", "lactancia", "niños", "personas mayores", "insuficiencia", "renal", "hepática", "cardíaca", "respiratoria", "digestiva", "neurológica", "psiquiátrica", "dermatológica", "oftalmológica", "urológica", "ginecológica", "pediátrica", "geriátrica", "urgencias", "cuidados intensivos", "reanimación", "cirugía", "anestesia", "radiología", "laboratorio", "análisis", "exámenes", "balance", "seguimiento", "vigilancia", "monitoreo", "evaluación", "eficacia", "tolerancia", "seguridad", "calidad", "costo", "reembolso", "seguro", "mutual", "seguridad social", "ameli", "cpam", "seguro de enfermedad", "complementario", "tercero pagador", "avance de gastos", "ticket moderador", "franquicia", "forfait", "participación", "resto a cargo"],
            "de": ["nebenwirkungen", "kontraindikationen", "wechselwirkungen", "allergien", "schwangerschaft", "stillzeit", "kinder", "ältere menschen", "insuffizienz", "niereninsuffizienz", "leberinsuffizienz", "herzinsuffizienz", "ateminsuffizienz", "magen-darm", "neurologisch", "psychiatrisch", "dermatologisch", "augenheilkunde", "urologisch", "gynäkologisch", "pädiatrisch", "geriatrisch", "notfall", "intensivstation", "reanimation", "chirurgie", "anästhesie", "radiologie", "labor", "analysen", "untersuchungen", "bilanz", "nachsorge", "überwachung", "monitoring", "bewertung", "wirksamkeit", "verträglichkeit", "sicherheit", "qualität", "kosten", "erstattung", "versicherung", "krankenkasse", "zusatzversicherung", "eigenanteil", "zuzahlung", "franchise", "pauschale", "beteiligung", "restkosten"],
            "en": ["side effects", "contraindications", "interactions", "allergies", "pregnancy", "breastfeeding", "children", "elderly", "insufficiency", "renal", "hepatic", "cardiac", "respiratory", "digestive", "neurological", "psychiatric", "dermatological", "ophthalmological", "urological", "gynecological", "pediatric", "geriatric", "emergency", "intensive care", "resuscitation", "surgery", "anesthesia", "radiology", "laboratory", "analyses", "examinations", "balance", "follow-up", "monitoring", "evaluation", "efficacy", "tolerance", "safety", "quality", "cost", "reimbursement", "insurance", "mutual", "social security", "ameli", "cpam", "health insurance", "complementary", "third party payer", "advance payment", "moderator ticket", "franchise", "forfait", "participation", "remaining cost"]
        }
    
    def should_trigger_ethical_fallback(self, query: str, detected_language: str) -> bool:
        """Determine if ethical fallback should be triggered"""
        query_lower = query.lower()
        
        # Check for safety keywords in the detected language
        if detected_language in self.safety_keywords:
            for keyword in self.safety_keywords[detected_language]:
                if keyword in query_lower:
                    logger.info(f"Safety keyword detected: {keyword} in {detected_language}")
                    return True
        
        # Check for complex medical queries that might be unsafe
        complex_patterns = [
            "effets secondaires", "side effects", "efectos secundarios", "nebenwirkungen",
            "contre-indications", "contraindications", "contraindicaciones", "kontraindikationen",
            "interactions", "interacciones", "wechselwirkungen",
            "allergies", "alergias", "allergien",
            "grossesse", "pregnancy", "embarazo", "schwangerschaft",
            "allaitement", "breastfeeding", "lactancia", "stillzeit",
            "enfants", "children", "niños", "kinder",
            "personnes âgées", "elderly", "personas mayores", "ältere menschen"
        ]
        
        for pattern in complex_patterns:
            if pattern in query_lower:
                logger.info(f"Complex medical pattern detected: {pattern}")
                return True
        
        return False
    
    def create_ethical_fallback_response(self, query: str, detected_language: str, error_reason: str = None) -> Dict[str, Any]:
        """Create an ethical fallback response respecting medical safety"""
        
        # Get the appropriate ethical message
        ethical_message = self.ethical_messages.get(detected_language, self.ethical_messages["en"])
        
        # Add context-specific safety note
        safety_note = self._get_safety_note(detected_language, error_reason)
        
        return {
            "success": False,
            "answer": ethical_message,
            "sources": [],
            "confidence": 0.0,
            "detected_language": detected_language,
            "target_language": detected_language,
            "processing_time": 0,
            "timestamp": None,
            "workflow": "ethical_fallback",
            "agent_workflow": ["ethical_fallback"],
            "consensus": "ethical_fallback",
            "iteration": 0,
            "verification": {"success": False, "confidence": 0.0},
            "human_validation": None,
            "error_reason": error_reason,
            "safety_note": safety_note,
            "ethical_fallback": True
        }
    
    def _get_safety_note(self, language: str, error_reason: str = None) -> str:
        """Get language-specific safety note"""
        safety_notes = {
            "fr": "Système de sécurité médicale activé - Pas d'invention de réponses. Consultez toujours un professionnel de santé qualifié.",
            "es": "Sistema de seguridad médica activado - Sin invención de respuestas. Consulte siempre a un profesional de salud calificado.",
            "de": "Medizinisches Sicherheitssystem aktiviert - Keine Erfindung von Antworten. Konsultieren Sie immer einen qualifizierten Gesundheitsfachmann.",
            "en": "Medical safety system activated - No invention of responses. Always consult a qualified healthcare professional."
        }
        
        base_note = safety_notes.get(language, safety_notes["en"])
        
        if error_reason:
            error_notes = {
                "fr": f" Raison technique: {error_reason}",
                "es": f" Razón técnica: {error_reason}",
                "de": f" Technischer Grund: {error_reason}",
                "en": f" Technical reason: {error_reason}"
            }
            base_note += error_notes.get(language, error_notes["en"])
        
        return base_note
    
    def get_helpful_suggestions(self, language: str) -> list:
        """Get helpful suggestions for the user"""
        suggestions = {
            "fr": [
                "Consultez votre médecin traitant",
                "Contactez un pharmacien",
                "Appelez le 15 en cas d'urgence",
                "Consultez les sources officielles (ANSM, HAS)"
            ],
            "es": [
                "Consulte a su médico de cabecera",
                "Contacte a un farmacéutico",
                "Llame al 112 en caso de emergencia",
                "Consulte fuentes oficiales (AEMPS, SNS)"
            ],
            "de": [
                "Konsultieren Sie Ihren Hausarzt",
                "Kontaktieren Sie einen Apotheker",
                "Rufen Sie 112 im Notfall",
                "Konsultieren Sie offizielle Quellen (BfArM, IQWiG)"
            ],
            "en": [
                "Consult your primary care physician",
                "Contact a pharmacist",
                "Call 911 in case of emergency",
                "Consult official sources (FDA, WHO)"
            ]
        }
        
        return suggestions.get(language, suggestions["en"])
