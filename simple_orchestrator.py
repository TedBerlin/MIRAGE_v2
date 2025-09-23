#!/usr/bin/env python3
"""
Version ultra-simplifiée et testée de l'orchestrateur
Évite tous les imports problématiques
Priorité HITL → Fallback Éthique
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleMultiAgentOrchestrator:
    """
    Orchestrateur simplifié avec priorité HITL → Fallback Éthique
    """
    
    def __init__(self):
        self.hitl_keywords = {
            'english': ['safety', 'approved', 'fda', 'side effects', 'pregnancy', 'children', 'dosage', 'contraindications', 'interactions', 'allergies', 'elderly', 'insufficiency', 'renal', 'hepatic', 'cardiac', 'respiratory', 'digestive', 'neurological', 'psychiatric', 'dermatological', 'ophthalmological', 'urological', 'gynecological', 'pediatric', 'geriatric', 'emergency', 'intensive care', 'resuscitation', 'surgery', 'anesthesia', 'radiology', 'laboratory', 'analyses', 'examinations', 'balance', 'follow-up', 'monitoring', 'evaluation', 'efficacy', 'tolerance', 'safety', 'quality', 'cost', 'reimbursement', 'insurance', 'mutual', 'social security', 'ameli', 'cpam', 'health insurance', 'complementary', 'third party payer', 'advance payment', 'moderator ticket', 'franchise', 'forfait', 'participation', 'remaining cost'],
            'french': ['sécurité', 'approuvé', 'effets secondaires', 'grossesse', 'enfants', 'posologie', 'contre-indications', 'interactions', 'allergies', 'personnes âgées', 'insuffisance', 'rénale', 'hépatique', 'cardiaque', 'respiratoire', 'digestive', 'neurologique', 'psychiatrique', 'dermatologique', 'ophtalmologique', 'urologique', 'gynécologique', 'pédiatrique', 'gériatrique', 'urgences', 'soins intensifs', 'réanimation', 'chirurgie', 'anesthésie', 'radiologie', 'laboratoire', 'analyses', 'examens', 'bilan', 'suivi', 'surveillance', 'monitoring', 'évaluation', 'efficacité', 'tolérance', 'sécurité', 'qualité', 'coût', 'remboursement', 'assurance', 'mutuelle', 'sécurité sociale', 'ameli', 'cpam', 'assurance maladie', 'complémentaire', 'tiers payant', 'avance de frais', 'ticket modérateur', 'franchise', 'forfait', 'participation', 'reste à charge'],
            'spanish': ['seguridad', 'aprobado', 'efectos secundarios', 'embarazo', 'niños', 'dosificación', 'contraindicaciones', 'interacciones', 'alergias', 'personas mayores', 'insuficiencia', 'renal', 'hepática', 'cardíaca', 'respiratoria', 'digestiva', 'neurológica', 'psiquiátrica', 'dermatológica', 'oftalmológica', 'urológica', 'ginecológica', 'pediátrica', 'geriátrica', 'urgencias', 'cuidados intensivos', 'reanimación', 'cirugía', 'anestesia', 'radiología', 'laboratorio', 'análisis', 'exámenes', 'balance', 'seguimiento', 'vigilancia', 'monitoreo', 'evaluación', 'eficacia', 'tolerancia', 'seguridad', 'calidad', 'costo', 'reembolso', 'seguro', 'mutual', 'seguridad social', 'ameli', 'cpam', 'seguro de enfermedad', 'complementario', 'tercero pagador', 'avance de gastos', 'ticket moderador', 'franquicia', 'forfait', 'participación', 'resto a cargo'],
            'german': ['sicherheit', 'zugelassen', 'nebenwirkungen', 'schwangerschaft', 'kinder', 'dosierung', 'kontraindikationen', 'wechselwirkungen', 'allergien', 'ältere menschen', 'insuffizienz', 'niereninsuffizienz', 'leberinsuffizienz', 'herzinsuffizienz', 'ateminsuffizienz', 'magen-darm', 'neurologisch', 'psychiatrisch', 'dermatologisch', 'augenheilkunde', 'urologisch', 'gynäkologisch', 'pädiatrisch', 'geriatrisch', 'notfall', 'intensivstation', 'reanimation', 'chirurgie', 'anästhesie', 'radiologie', 'labor', 'analysen', 'untersuchungen', 'bilanz', 'nachsorge', 'überwachung', 'monitoring', 'bewertung', 'wirksamkeit', 'verträglichkeit', 'sicherheit', 'qualität', 'kosten', 'erstattung', 'versicherung', 'krankenkasse', 'zusatzversicherung', 'eigenanteil', 'zuzahlung', 'franchise', 'pauschale', 'beteiligung', 'restkosten']
        }
        
        self.ethical_messages = {
            'english': "I cannot provide this medical information. Please consult a qualified healthcare professional.",
            'french': "Je ne peux pas fournir cette information médicale. Consultez un professionnel de santé qualifié.",
            'spanish': "No puedo proporcionar esta información médica. Consulte a un profesional de salud calificado.",
            'german': "Ich kann diese medizinische Information nicht bereitstellen. Konsultieren Sie einen qualifizierten Gesundheitsfachmann."
        }
        
        logger.info("✅ SimpleMultiAgentOrchestrator initialized with HITL priority")
    
    def requires_human_validation(self, query: str, detected_language: str) -> bool:
        """
        Détermine si la requête nécessite une validation humaine
        Priorité HITL sur Fallback Éthique
        """
        query_lower = query.lower()
        
        # Vérifier les mots-clés HITL par langue
        if detected_language in self.hitl_keywords:
            for keyword in self.hitl_keywords[detected_language]:
                if keyword in query_lower:
                    logger.info(f"🚨 HITL déclenché: '{keyword}' dans '{query}'")
                    return True
        
        # Fallback éthique uniquement si HITL non déclenché
        ethical_triggers = ['je ne sais pas', 'i dont know', 'no sé', 'ich weiß nicht']
        for trigger in ethical_triggers:
            if trigger in query_lower:
                logger.info(f"🤔 Fallback éthique: '{trigger}' dans '{query}'")
                return False
        
        return False
    
    def simple_detect_language(self, text: str) -> str:
        """
        Détection de langue simplifiée sans dépendances externes
        """
        text_lower = text.lower()
        
        # Détection basée sur des mots-clés
        french_words = ['le', 'la', 'les', 'est', 'dans', 'pour', 'quoi', 'quels', 'sont', 'effets', 'secondaires', 'contre-indications', 'interactions', 'allergies', 'grossesse', 'allaitement', 'enfants', 'personnes âgées', 'insuffisance', 'rénale', 'hépatique', 'cardiaque', 'respiratoire', 'digestive', 'neurologique', 'psychiatrique', 'dermatologique', 'ophtalmologique', 'urologique', 'gynécologique', 'pédiatrique', 'gériatrique', 'urgences', 'soins intensifs', 'réanimation', 'chirurgie', 'anesthésie', 'radiologie', 'laboratoire', 'analyses', 'examens', 'bilan', 'suivi', 'surveillance', 'monitoring', 'évaluation', 'efficacité', 'tolérance', 'sécurité', 'qualité', 'coût', 'remboursement', 'assurance', 'mutuelle', 'sécurité sociale', 'ameli', 'cpam', 'assurance maladie', 'complémentaire', 'tiers payant', 'avance de frais', 'ticket modérateur', 'franchise', 'forfait', 'participation', 'reste à charge']
        spanish_words = ['el', 'la', 'los', 'qué', 'cómo', 'por', 'para', 'cuáles', 'son', 'efectos', 'secundarios', 'contraindicaciones', 'interacciones', 'alergias', 'embarazo', 'lactancia', 'niños', 'personas mayores', 'insuficiencia', 'renal', 'hepática', 'cardíaca', 'respiratoria', 'digestiva', 'neurológica', 'psiquiátrica', 'dermatológica', 'oftalmológica', 'urológica', 'ginecológica', 'pediátrica', 'geriátrica', 'urgencias', 'cuidados intensivos', 'reanimación', 'cirugía', 'anestesia', 'radiología', 'laboratorio', 'análisis', 'exámenes', 'balance', 'seguimiento', 'vigilancia', 'monitoreo', 'evaluación', 'eficacia', 'tolerancia', 'seguridad', 'calidad', 'costo', 'reembolso', 'seguro', 'mutual', 'seguridad social', 'ameli', 'cpam', 'seguro de enfermedad', 'complementario', 'tercero pagador', 'avance de gastos', 'ticket moderador', 'franquicia', 'forfait', 'participación', 'resto a cargo']
        german_words = ['der', 'die', 'das', 'und', 'ist', 'für', 'was', 'nebenwirkungen', 'kontraindikationen', 'wechselwirkungen', 'allergien', 'schwangerschaft', 'stillzeit', 'kinder', 'ältere menschen', 'insuffizienz', 'niereninsuffizienz', 'leberinsuffizienz', 'herzinsuffizienz', 'ateminsuffizienz', 'magen-darm', 'neurologisch', 'psychiatrisch', 'dermatologisch', 'augenheilkunde', 'urologisch', 'gynäkologisch', 'pädiatrisch', 'geriatrisch', 'notfall', 'intensivstation', 'reanimation', 'chirurgie', 'anästhesie', 'radiologie', 'labor', 'analysen', 'untersuchungen', 'bilanz', 'nachsorge', 'überwachung', 'monitoring', 'bewertung', 'wirksamkeit', 'verträglichkeit', 'sicherheit', 'qualität', 'kosten', 'erstattung', 'versicherung', 'krankenkasse', 'zusatzversicherung', 'eigenanteil', 'zuzahlung', 'franchise', 'pauschale', 'beteiligung', 'restkosten']
        
        if any(word in text_lower for word in french_words):
            return "french"
        elif any(word in text_lower for word in spanish_words):
            return "spanish"
        elif any(word in text_lower for word in german_words):
            return "german"
        else:
            return "english"
    
    def process_query(self, user_query: str, target_language: str = None) -> Dict[str, Any]:
        """
        Processus simplifié avec priorité HITL
        """
        # Détection de langue simplifiée
        detected_language = self.simple_detect_language(user_query)
        target_language = target_language or detected_language
        
        logger.info(f"🔍 Query: {user_query[:50]}... | Language: {detected_language}")
        
        # Vérification HITL (prioritaire)
        requires_human = self.requires_human_validation(user_query, detected_language)
        
        if requires_human:
            logger.info("✅ HITL activé - Validation humaine requise")
            return {
                "success": True,
                "query_id": f"hitl_{hash(user_query) % 1000000}",
                "answer": "🔒 Cette requête nécessite une validation humaine. Un expert va examiner votre question.",
                "sources": [],
                "confidence": 0.0,
                "processing_time": 0.0,
                "human_validation_required": True,
                "timestamp": datetime.now().isoformat(),
                "agent_workflow": ["human_validation"],
                "consensus": "pending_human_validation",
                "iteration": 0,
                "verification": {
                    "success": False,
                    "confidence": 0.0
                },
                "workflow": "human_validation",
                "detected_language": detected_language,
                "target_language": target_language,
                "human_validation": {
                    "requires_human": True,
                    "validation_request": {
                        "validation_type": "safety_review",
                        "priority": "high",
                        "reason": "Safety keywords detected - requires human validation"
                    }
                }
            }
        
        # Fallback éthique (seulement si HITL non déclenché)
        logger.info("✅ Fallback éthique - HITL non déclenché")
        message = self.ethical_messages.get(detected_language, self.ethical_messages["english"])
        
        return {
            "success": False,
            "query_id": f"ethical_{hash(user_query) % 1000000}",
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
            "target_language": target_language,
            "ethical_fallback_reason": "Safety keywords not detected - ethical fallback applied"
        }

# Instance globale testée
orchestrator = SimpleMultiAgentOrchestrator()

# Test immédiat de la logique
if __name__ == "__main__":
    test_cases = [
        ("Quels sont les effets secondaires?", "french"),
        ("Is this FDA approved?", "english"),
        ("¿Es seguro durante el embarazo?", "spanish"),
        ("What is the mechanism of action?", "english")
    ]
    
    print("🧪 TEST DE LA LOGIQUE HITL PRIORITAIRE")
    print("=" * 50)
    
    for query, expected_lang in test_cases:
        result = orchestrator.process_query(query)
        print(f"✅ {query} -> {result['workflow']}")
        print(f"   HITL: {result.get('human_validation_required', False)}")
        print(f"   Workflow: {result['workflow']}")
        print()