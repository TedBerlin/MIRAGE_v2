"""
Simple Ethical Fallback System for MIRAGE v2
============================================
Version simplifiée pour éviter les erreurs de segmentation
"""

class SimpleEthicalFallbackSystem:
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
        """Check if ethical fallback should be triggered"""
        if not query or not detected_language:
            return False
        
        query_lower = query.lower()
        keywords = self.safety_keywords.get(detected_language, [])
        
        # Check for safety keywords
        for keyword in keywords:
            if keyword.lower() in query_lower:
                return True
        
        return False
    
    def create_ethical_fallback_response(self, query: str, detected_language: str, reason: str) -> dict:
        """Create ethical fallback response"""
        message = self.ethical_messages.get(detected_language, self.ethical_messages["en"])
        
        return {
            "success": False,
            "query_id": f"ethical_fallback_{hash(query) % 1000000}",
            "answer": message,
            "sources": [],
            "confidence": 0.0,
            "processing_time": 0.0,
            "human_validation_required": False,
            "timestamp": "2025-09-21T09:00:00",
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
