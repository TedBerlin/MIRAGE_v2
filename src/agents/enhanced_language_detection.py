"""
Enhanced Language Detection for MIRAGE v2
=========================================
Optimized for complex queries with robust pattern matching
"""

import structlog

logger = structlog.get_logger(__name__)

def detect_language_enhanced(text: str) -> str:
    """
    Enhanced language detection optimized for complex queries.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Language code (en, fr, es, de)
    """
    text_lower = text.lower()
    words = text_lower.split()
    
    # Enhanced language-specific words for complex queries
    language_words = {
        'fr': ['quels', 'quelles', 'comment', 'pourquoi', 'quand', 'où', 'qui', 'que', 'sont', 'est', 'ont', 'peut', 'doit', 'les', 'des', 'du', 'de', 'la', 'le', 'un', 'une', 'dans', 'sur', 'avec', 'bénéfices', 'paracétamol', 'traitement', 'cancer', 'chimiothérapie', 'effets', 'secondaires', 'médicament', 'thérapie', 'patient', 'maladie', 'symptômes', 'diagnostic', 'prévention', 'guérison', 'soins', 'médecin', 'hôpital', 'pharmacie', 'posologie', 'contre-indications', 'interactions', 'allergies', 'grossesse', 'allaitement', 'enfants', 'personnes âgées', 'insuffisance', 'rénale', 'hépatique', 'cardiaque', 'respiratoire', 'digestive', 'neurologique', 'psychiatrique', 'dermatologique', 'ophtalmologique', 'urologique', 'gynécologique', 'pédiatrique', 'gériatrique', 'urgences', 'soins intensifs', 'réanimation', 'chirurgie', 'anesthésie', 'radiologie', 'laboratoire', 'analyses', 'examens', 'bilan', 'suivi', 'surveillance', 'monitoring', 'évaluation', 'efficacité', 'tolérance', 'sécurité', 'qualité', 'coût', 'remboursement', 'assurance', 'mutuelle', 'sécurité sociale', 'ameli', 'cpam', 'sécurité sociale', 'assurance maladie', 'mutuelle', 'complémentaire', 'tiers payant', 'avance de frais', 'ticket modérateur', 'franchise', 'forfait', 'participation', 'reste à charge', 'tiers payant', 'avance de frais', 'ticket modérateur', 'franchise', 'forfait', 'participation', 'reste à charge', 'quels', 'sont', 'les', 'effets', 'secondaires', 'de', 'la', 'chimiothérapie', 'quelles', 'sont', 'les', 'contre-indications', 'du', 'traitement', 'comment', 'fonctionne', 'ce', 'médicament', 'pourquoi', 'doit-on', 'prendre', 'cette', 'posologie', 'quand', 'consulter', 'un', 'médecin', 'où', 'trouver', 'des', 'informations', 'qui', 'peut', 'prescrire', 'ce', 'traitement', 'que', 'faire', 'en', 'cas', 'd\'effets', 'indésirables'],
        'es': ['qué', 'cómo', 'por', 'cuándo', 'dónde', 'quién', 'son', 'es', 'los', 'las', 'del', 'en', 'con', 'para', 'efectos', 'secundarios', 'niños', 'cuáles', 'tratamiento', 'cáncer', 'quimioterapia', 'diabetes', 'insulina', 'cuáles', 'son', 'los', 'efectos', 'secundarios', 'de', 'la', 'quimioterapia', 'cuáles', 'son', 'las', 'contraindicaciones', 'del', 'tratamiento', 'cómo', 'funciona', 'este', 'medicamento', 'por', 'qué', 'debe', 'tomarse', 'esta', 'dosis', 'cuándo', 'consultar', 'un', 'médico', 'dónde', 'encontrar', 'información', 'quién', 'puede', 'recetar', 'este', 'tratamiento', 'qué', 'hacer', 'en', 'caso', 'de', 'efectos', 'adversos'],
        'de': ['was', 'wie', 'warum', 'wann', 'wo', 'wer', 'sind', 'ist', 'der', 'die', 'das', 'und', 'oder', 'mit', 'von', 'für', 'effekte', 'wirkungen', 'vorteile', 'nachteile', 'welche', 'hat', 'behandlung', 'krebs', 'chemotherapie', 'nebenwirkungen', 'medikament', 'therapie', 'patient', 'krankheit', 'symptome', 'diagnose', 'prävention', 'heilung', 'pflege', 'arzt', 'krankenhaus', 'apotheke', 'dosierung', 'kontraindikationen', 'wechselwirkungen', 'allergien', 'schwangerschaft', 'stillzeit', 'kinder', 'ältere menschen', 'niereninsuffizienz', 'leberinsuffizienz', 'herzinsuffizienz', 'ateminsuffizienz', 'magen-darm', 'neurologisch', 'psychiatrisch', 'dermatologisch', 'augenheilkunde', 'urologisch', 'gynäkologisch', 'pädiatrisch', 'geriatrisch', 'notfall', 'intensivstation', 'reanimation', 'chirurgie', 'anästhesie', 'radiologie', 'labor', 'analysen', 'untersuchungen', 'bilanz', 'nachsorge', 'überwachung', 'monitoring', 'bewertung', 'wirksamkeit', 'verträglichkeit', 'sicherheit', 'qualität', 'kosten', 'erstattung', 'versicherung', 'krankenkasse', 'zusatzversicherung', 'eigenanteil', 'zuzahlung', 'franchise', 'pauschale', 'beteiligung', 'restkosten', 'welche', 'sind', 'die', 'nebenwirkungen', 'der', 'chemotherapie', 'welche', 'sind', 'die', 'kontraindikationen', 'der', 'behandlung', 'wie', 'funktioniert', 'dieses', 'medikament', 'warum', 'muss', 'diese', 'dosis', 'eingenommen', 'werden', 'wann', 'einen', 'arzt', 'konsultieren', 'wo', 'informationen', 'finden', 'wer', 'kann', 'diese', 'behandlung', 'verschreiben', 'was', 'tun', 'bei', 'nebenwirkungen'],
        'en': ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'are', 'is', 'was', 'the', 'and', 'or', 'but', 'advantages', 'side', 'effects', 'contraindications', 'overdose', 'treatment', 'cancer', 'chemotherapy', 'diabetes', 'insulin']
    }
    
    # Enhanced scoring system for complex queries
    language_scores = {}
    
    for lang, words_list in language_words.items():
        score = 0
        # Basic word matching
        for word in words:
            if word in words_list:
                score += 1
        
        # Enhanced scoring for complex patterns
        if lang == 'fr':
            # French-specific patterns for complex queries
            if 'quels' in text_lower and 'sont' in text_lower:
                score += 3
            if 'quelles' in text_lower and 'sont' in text_lower:
                score += 3
            if 'comment' in text_lower and 'fonctionne' in text_lower:
                score += 2
            if 'pourquoi' in text_lower and 'doit' in text_lower:
                score += 2
            if 'quand' in text_lower and 'consulter' in text_lower:
                score += 2
            if 'où' in text_lower and 'trouver' in text_lower:
                score += 2
            if 'qui' in text_lower and 'peut' in text_lower:
                score += 2
            if 'que' in text_lower and 'faire' in text_lower:
                score += 2
            # Medical terminology patterns
            if 'effets' in text_lower and 'secondaires' in text_lower:
                score += 4
            if 'chimiothérapie' in text_lower:
                score += 3
            if 'traitement' in text_lower:
                score += 2
            if 'médicament' in text_lower:
                score += 2
            if 'médecin' in text_lower:
                score += 2
            if 'hôpital' in text_lower:
                score += 2
            if 'pharmacie' in text_lower:
                score += 2
            if 'posologie' in text_lower:
                score += 2
            if 'contre-indications' in text_lower:
                score += 3
            if 'interactions' in text_lower:
                score += 2
            if 'allergies' in text_lower:
                score += 2
            if 'grossesse' in text_lower:
                score += 2
            if 'allaitement' in text_lower:
                score += 2
            if 'enfants' in text_lower:
                score += 2
            if 'personnes âgées' in text_lower:
                score += 2
            if 'insuffisance' in text_lower:
                score += 2
            if 'rénale' in text_lower:
                score += 2
            if 'hépatique' in text_lower:
                score += 2
            if 'cardiaque' in text_lower:
                score += 2
            if 'respiratoire' in text_lower:
                score += 2
            if 'digestive' in text_lower:
                score += 2
            if 'neurologique' in text_lower:
                score += 2
            if 'psychiatrique' in text_lower:
                score += 2
            if 'dermatologique' in text_lower:
                score += 2
            if 'ophtalmologique' in text_lower:
                score += 2
            if 'urologique' in text_lower:
                score += 2
            if 'gynécologique' in text_lower:
                score += 2
            if 'pédiatrique' in text_lower:
                score += 2
            if 'gériatrique' in text_lower:
                score += 2
            if 'urgences' in text_lower:
                score += 2
            if 'soins intensifs' in text_lower:
                score += 2
            if 'réanimation' in text_lower:
                score += 2
            if 'chirurgie' in text_lower:
                score += 2
            if 'anesthésie' in text_lower:
                score += 2
            if 'radiologie' in text_lower:
                score += 2
            if 'laboratoire' in text_lower:
                score += 2
            if 'analyses' in text_lower:
                score += 2
            if 'examens' in text_lower:
                score += 2
            if 'bilan' in text_lower:
                score += 2
            if 'suivi' in text_lower:
                score += 2
            if 'surveillance' in text_lower:
                score += 2
            if 'monitoring' in text_lower:
                score += 2
            if 'évaluation' in text_lower:
                score += 2
            if 'efficacité' in text_lower:
                score += 2
            if 'tolérance' in text_lower:
                score += 2
            if 'sécurité' in text_lower:
                score += 2
            if 'qualité' in text_lower:
                score += 2
            if 'coût' in text_lower:
                score += 2
            if 'remboursement' in text_lower:
                score += 2
            if 'assurance' in text_lower:
                score += 2
            if 'mutuelle' in text_lower:
                score += 2
            if 'sécurité sociale' in text_lower:
                score += 2
            if 'ameli' in text_lower:
                score += 2
            if 'cpam' in text_lower:
                score += 2
            if 'assurance maladie' in text_lower:
                score += 2
            if 'complémentaire' in text_lower:
                score += 2
            if 'tiers payant' in text_lower:
                score += 2
            if 'avance de frais' in text_lower:
                score += 2
            if 'ticket modérateur' in text_lower:
                score += 2
            if 'franchise' in text_lower:
                score += 2
            if 'forfait' in text_lower:
                score += 2
            if 'participation' in text_lower:
                score += 2
            if 'reste à charge' in text_lower:
                score += 2
        
        elif lang == 'es':
            # Spanish-specific patterns for complex queries
            if 'cuáles' in text_lower and 'son' in text_lower:
                score += 3
            if 'cómo' in text_lower and 'funciona' in text_lower:
                score += 2
            if 'por' in text_lower and 'qué' in text_lower:
                score += 2
            if 'cuándo' in text_lower and 'consultar' in text_lower:
                score += 2
            if 'dónde' in text_lower and 'encontrar' in text_lower:
                score += 2
            if 'quién' in text_lower and 'puede' in text_lower:
                score += 2
            if 'qué' in text_lower and 'hacer' in text_lower:
                score += 2
            # Medical terminology patterns
            if 'efectos' in text_lower and 'secundarios' in text_lower:
                score += 4
            if 'quimioterapia' in text_lower:
                score += 3
            if 'tratamiento' in text_lower:
                score += 2
            if 'medicamento' in text_lower:
                score += 2
            if 'médico' in text_lower:
                score += 2
            if 'hospital' in text_lower:
                score += 2
            if 'farmacia' in text_lower:
                score += 2
            if 'dosis' in text_lower:
                score += 2
            if 'contraindicaciones' in text_lower:
                score += 3
            if 'interacciones' in text_lower:
                score += 2
            if 'alergias' in text_lower:
                score += 2
            if 'embarazo' in text_lower:
                score += 2
            if 'lactancia' in text_lower:
                score += 2
            if 'niños' in text_lower:
                score += 2
            if 'personas mayores' in text_lower:
                score += 2
            if 'insuficiencia' in text_lower:
                score += 2
            if 'renal' in text_lower:
                score += 2
            if 'hepática' in text_lower:
                score += 2
            if 'cardíaca' in text_lower:
                score += 2
            if 'respiratoria' in text_lower:
                score += 2
            if 'digestiva' in text_lower:
                score += 2
            if 'neurológica' in text_lower:
                score += 2
            if 'psiquiátrica' in text_lower:
                score += 2
            if 'dermatológica' in text_lower:
                score += 2
            if 'oftalmológica' in text_lower:
                score += 2
            if 'urológica' in text_lower:
                score += 2
            if 'ginecológica' in text_lower:
                score += 2
            if 'pediátrica' in text_lower:
                score += 2
            if 'geriátrica' in text_lower:
                score += 2
            if 'urgencias' in text_lower:
                score += 2
            if 'cuidados intensivos' in text_lower:
                score += 2
            if 'reanimación' in text_lower:
                score += 2
            if 'cirugía' in text_lower:
                score += 2
            if 'anestesia' in text_lower:
                score += 2
            if 'radiología' in text_lower:
                score += 2
            if 'laboratorio' in text_lower:
                score += 2
            if 'análisis' in text_lower:
                score += 2
            if 'exámenes' in text_lower:
                score += 2
            if 'balance' in text_lower:
                score += 2
            if 'seguimiento' in text_lower:
                score += 2
            if 'vigilancia' in text_lower:
                score += 2
            if 'monitoreo' in text_lower:
                score += 2
            if 'evaluación' in text_lower:
                score += 2
            if 'eficacia' in text_lower:
                score += 2
            if 'tolerancia' in text_lower:
                score += 2
            if 'seguridad' in text_lower:
                score += 2
            if 'calidad' in text_lower:
                score += 2
            if 'costo' in text_lower:
                score += 2
            if 'reembolso' in text_lower:
                score += 2
            if 'seguro' in text_lower:
                score += 2
            if 'mutual' in text_lower:
                score += 2
            if 'seguridad social' in text_lower:
                score += 2
            if 'ameli' in text_lower:
                score += 2
            if 'cpam' in text_lower:
                score += 2
            if 'seguro de enfermedad' in text_lower:
                score += 2
            if 'complementario' in text_lower:
                score += 2
            if 'tercero pagador' in text_lower:
                score += 2
            if 'avance de gastos' in text_lower:
                score += 2
            if 'ticket moderador' in text_lower:
                score += 2
            if 'franquicia' in text_lower:
                score += 2
            if 'forfait' in text_lower:
                score += 2
            if 'participación' in text_lower:
                score += 2
            if 'resto a cargo' in text_lower:
                score += 2
        
        elif lang == 'de':
            # German-specific patterns for complex queries
            if 'welche' in text_lower and 'sind' in text_lower:
                score += 3
            if 'wie' in text_lower and 'funktioniert' in text_lower:
                score += 2
            if 'warum' in text_lower and 'muss' in text_lower:
                score += 2
            if 'wann' in text_lower and 'konsultieren' in text_lower:
                score += 2
            if 'wo' in text_lower and 'finden' in text_lower:
                score += 2
            if 'wer' in text_lower and 'kann' in text_lower:
                score += 2
            if 'was' in text_lower and 'tun' in text_lower:
                score += 2
            # Medical terminology patterns
            if 'nebenwirkungen' in text_lower:
                score += 4
            if 'chemotherapie' in text_lower:
                score += 3
            if 'behandlung' in text_lower:
                score += 2
            if 'medikament' in text_lower:
                score += 2
            if 'arzt' in text_lower:
                score += 2
            if 'krankenhaus' in text_lower:
                score += 2
            if 'apotheke' in text_lower:
                score += 2
            if 'dosierung' in text_lower:
                score += 2
            if 'kontraindikationen' in text_lower:
                score += 3
            if 'wechselwirkungen' in text_lower:
                score += 2
            if 'allergien' in text_lower:
                score += 2
            if 'schwangerschaft' in text_lower:
                score += 2
            if 'stillzeit' in text_lower:
                score += 2
            if 'kinder' in text_lower:
                score += 2
            if 'ältere menschen' in text_lower:
                score += 2
            if 'insuffizienz' in text_lower:
                score += 2
            if 'niereninsuffizienz' in text_lower:
                score += 2
            if 'leberinsuffizienz' in text_lower:
                score += 2
            if 'herzinsuffizienz' in text_lower:
                score += 2
            if 'ateminsuffizienz' in text_lower:
                score += 2
            if 'magen-darm' in text_lower:
                score += 2
            if 'neurologisch' in text_lower:
                score += 2
            if 'psychiatrisch' in text_lower:
                score += 2
            if 'dermatologisch' in text_lower:
                score += 2
            if 'augenheilkunde' in text_lower:
                score += 2
            if 'urologisch' in text_lower:
                score += 2
            if 'gynäkologisch' in text_lower:
                score += 2
            if 'pädiatrisch' in text_lower:
                score += 2
            if 'geriatrisch' in text_lower:
                score += 2
            if 'notfall' in text_lower:
                score += 2
            if 'intensivstation' in text_lower:
                score += 2
            if 'reanimation' in text_lower:
                score += 2
            if 'chirurgie' in text_lower:
                score += 2
            if 'anästhesie' in text_lower:
                score += 2
            if 'radiologie' in text_lower:
                score += 2
            if 'labor' in text_lower:
                score += 2
            if 'analysen' in text_lower:
                score += 2
            if 'untersuchungen' in text_lower:
                score += 2
            if 'bilanz' in text_lower:
                score += 2
            if 'nachsorge' in text_lower:
                score += 2
            if 'überwachung' in text_lower:
                score += 2
            if 'monitoring' in text_lower:
                score += 2
            if 'bewertung' in text_lower:
                score += 2
            if 'wirksamkeit' in text_lower:
                score += 2
            if 'verträglichkeit' in text_lower:
                score += 2
            if 'sicherheit' in text_lower:
                score += 2
            if 'qualität' in text_lower:
                score += 2
            if 'kosten' in text_lower:
                score += 2
            if 'erstattung' in text_lower:
                score += 2
            if 'versicherung' in text_lower:
                score += 2
            if 'krankenkasse' in text_lower:
                score += 2
            if 'zusatzversicherung' in text_lower:
                score += 2
            if 'eigenanteil' in text_lower:
                score += 2
            if 'zuzahlung' in text_lower:
                score += 2
            if 'franchise' in text_lower:
                score += 2
            if 'pauschale' in text_lower:
                score += 2
            if 'beteiligung' in text_lower:
                score += 2
            if 'restkosten' in text_lower:
                score += 2
        
        elif lang == 'en':
            # English-specific patterns for complex queries
            if 'what' in text_lower and 'are' in text_lower:
                score += 3
            if 'how' in text_lower and 'does' in text_lower:
                score += 2
            if 'why' in text_lower and 'should' in text_lower:
                score += 2
            if 'when' in text_lower and 'consult' in text_lower:
                score += 2
            if 'where' in text_lower and 'find' in text_lower:
                score += 2
            if 'who' in text_lower and 'can' in text_lower:
                score += 2
            if 'which' in text_lower and 'is' in text_lower:
                score += 2
            # Medical terminology patterns
            if 'side' in text_lower and 'effects' in text_lower:
                score += 4
            if 'chemotherapy' in text_lower:
                score += 3
            if 'treatment' in text_lower:
                score += 2
            if 'medication' in text_lower:
                score += 2
            if 'doctor' in text_lower:
                score += 2
            if 'hospital' in text_lower:
                score += 2
            if 'pharmacy' in text_lower:
                score += 2
            if 'dosage' in text_lower:
                score += 2
            if 'contraindications' in text_lower:
                score += 3
            if 'interactions' in text_lower:
                score += 2
            if 'allergies' in text_lower:
                score += 2
            if 'pregnancy' in text_lower:
                score += 2
            if 'breastfeeding' in text_lower:
                score += 2
            if 'children' in text_lower:
                score += 2
            if 'elderly' in text_lower:
                score += 2
            if 'insufficiency' in text_lower:
                score += 2
            if 'renal' in text_lower:
                score += 2
            if 'hepatic' in text_lower:
                score += 2
            if 'cardiac' in text_lower:
                score += 2
            if 'respiratory' in text_lower:
                score += 2
            if 'digestive' in text_lower:
                score += 2
            if 'neurological' in text_lower:
                score += 2
            if 'psychiatric' in text_lower:
                score += 2
            if 'dermatological' in text_lower:
                score += 2
            if 'ophthalmological' in text_lower:
                score += 2
            if 'urological' in text_lower:
                score += 2
            if 'gynecological' in text_lower:
                score += 2
            if 'pediatric' in text_lower:
                score += 2
            if 'geriatric' in text_lower:
                score += 2
            if 'emergency' in text_lower:
                score += 2
            if 'intensive care' in text_lower:
                score += 2
            if 'resuscitation' in text_lower:
                score += 2
            if 'surgery' in text_lower:
                score += 2
            if 'anesthesia' in text_lower:
                score += 2
            if 'radiology' in text_lower:
                score += 2
            if 'laboratory' in text_lower:
                score += 2
            if 'analyses' in text_lower:
                score += 2
            if 'examinations' in text_lower:
                score += 2
            if 'balance' in text_lower:
                score += 2
            if 'follow-up' in text_lower:
                score += 2
            if 'monitoring' in text_lower:
                score += 2
            if 'evaluation' in text_lower:
                score += 2
            if 'efficacy' in text_lower:
                score += 2
            if 'tolerance' in text_lower:
                score += 2
            if 'safety' in text_lower:
                score += 2
            if 'quality' in text_lower:
                score += 2
            if 'cost' in text_lower:
                score += 2
            if 'reimbursement' in text_lower:
                score += 2
            if 'insurance' in text_lower:
                score += 2
            if 'mutual' in text_lower:
                score += 2
            if 'social security' in text_lower:
                score += 2
            if 'ameli' in text_lower:
                score += 2
            if 'cpam' in text_lower:
                score += 2
            if 'health insurance' in text_lower:
                score += 2
            if 'complementary' in text_lower:
                score += 2
            if 'third party payer' in text_lower:
                score += 2
            if 'advance payment' in text_lower:
                score += 2
            if 'moderator ticket' in text_lower:
                score += 2
            if 'franchise' in text_lower:
                score += 2
            if 'forfait' in text_lower:
                score += 2
            if 'participation' in text_lower:
                score += 2
            if 'remaining cost' in text_lower:
                score += 2
        
        language_scores[lang] = score
    
    # Debug logging
    logger.info(f"Enhanced language detection scores: {language_scores}")
    
    # Find the language with the highest score
    best_language = max(language_scores, key=language_scores.get)
    best_score = language_scores[best_language]
    
    # Enhanced confidence threshold for complex queries
    if best_score >= 2:
        return best_language
    else:
        # Special handling for language confusion
        if best_language == "fr" and language_scores.get("es", 0) > 0:
            # Check for Spanish-specific patterns
            spanish_patterns = ["¿", "á", "é", "í", "ó", "ú", "ñ"]
            if any(pattern in text for pattern in spanish_patterns):
                logger.info("Spanish patterns detected, overriding French detection")
                return "es"
        
        if best_language == "fr" and language_scores.get("de", 0) > 0:
            # Check for German-specific patterns
            german_patterns = ["ä", "ö", "ü", "ß"]
            if any(pattern in text for pattern in german_patterns):
                logger.info("German patterns detected, overriding French detection")
                return "de"
        
        # Default to English for low confidence
        return "en"
