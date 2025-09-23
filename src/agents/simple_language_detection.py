"""
Simple Language Detection for MIRAGE v2
======================================
Version simplifiée pour éviter les erreurs de segmentation
"""

def detect_language_simple(query: str) -> str:
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
