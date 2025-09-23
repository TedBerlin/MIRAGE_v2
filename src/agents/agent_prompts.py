"""
Agent prompts definitions for MIRAGE v2.

Contains optimized prompts for Generator, Verifier, and Reformer agents
with focus on pharmaceutical research and ethical AI practices.
"""

from typing import Dict, Any
import structlog

logger = structlog.get_logger(__name__)

# Global shared instance
_shared_prompts_instance = None


def get_shared_prompts() -> 'AgentPrompts':
    """Get the shared AgentPrompts instance."""
    global _shared_prompts_instance
    if _shared_prompts_instance is None:
        _shared_prompts_instance = AgentPrompts()
    return _shared_prompts_instance


def reload_shared_prompts() -> 'AgentPrompts':
    """Force reload the shared AgentPrompts instance."""
    global _shared_prompts_instance
    _shared_prompts_instance = AgentPrompts()
    logger.info("Shared AgentPrompts instance reloaded")
    return _shared_prompts_instance


def detect_language(text: str) -> str:
    """
    Detect the language of the input text using enhanced word-by-word analysis.
    Optimized for complex queries with robust pattern matching.
    
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
    
    # Count matches for each language
    language_scores = {}
    for lang, words_list in language_words.items():
        score = sum(1 for word in words if word in words_list)
        language_scores[lang] = score
    
    # Debug logging
    logger.info(f"Language detection scores: {language_scores}")
    
    # Find the language with the highest score
    best_language = max(language_scores, key=language_scores.get)
    best_score = language_scores[best_language]
    
    # If no matches found, default to English
    if best_score == 0:
        return "en"
    
    # Special handling for language confusion
    if best_language == "fr" and language_scores.get("es", 0) > 0:
        # Check for Spanish-specific patterns
        spanish_patterns = ["¿", "á", "é", "í", "ó", "ú", "ñ"]
        if any(pattern in text for pattern in spanish_patterns):
            logger.info("Spanish patterns detected, overriding French detection")
            return "es"
    
    # Special handling for French vs German confusion
    if best_language == "fr" and language_scores.get("de", 0) > 0:
        # Check for German-specific patterns
        german_patterns = ["ä", "ö", "ü", "ß", "der", "die", "das", "und", "oder"]
        if any(pattern in text for pattern in german_patterns):
            logger.info("German patterns detected, overriding French detection")
            return "de"
    
    # Special handling for German vs French confusion
    if best_language == "de" and language_scores.get("fr", 0) > 0:
        # Check for French-specific patterns
        french_patterns = ["à", "è", "é", "ê", "ë", "î", "ï", "ô", "ù", "û", "ü", "ç"]
        if any(pattern in text for pattern in french_patterns):
            logger.info("French patterns detected, overriding German detection")
            return "fr"
    
    return best_language


class AgentPrompts:
    """Manages all agent prompts with optimization for pharmaceutical research."""
    
    def __init__(self):
        self.prompts = self._initialize_prompts()
        logger.info("AgentPrompts initialized with optimized pharmaceutical prompts")
    
    def _initialize_prompts(self) -> Dict[str, Dict[str, Any]]:
        """Initialize all agent prompts with pharmaceutical research focus."""
        
        return {
            "generator": {
                "name": "The Innovator",
                "role": "Primary response generator for pharmaceutical research queries",
                "system_prompt": """🎯 ROLE & OBJECTIVE
You are The Innovator, an expert AI assistant specialized in pharmaceutical research and medical intelligence. Your role is to provide accurate, evidence-based responses to pharmaceutical research questions.

🔒 CORE PRINCIPLES
• Always base your responses on the provided context from pharmaceutical documents
• If information is NOT in the provided context, respond strictly: "I cannot find this information in our pharmaceutical research database."
• Never hallucinate or invent medical information
• Prioritize patient safety and regulatory compliance
• Use precise medical terminology when appropriate
• Cite specific sources from the context when available

📝 RESPONSE GUIDELINES
• Provide clear, structured answers
• Include relevant details from the context
• Highlight important safety considerations
• Mention regulatory aspects when relevant
• Use bullet points for complex information
• Keep responses concise but comprehensive

📚 CONTEXT USAGE
• Always reference the provided context
• Quote relevant passages when helpful
• Explain how the context supports your answer
• If context is insufficient, clearly state limitations

⚠️ CRITICAL REMINDER
Your responses directly impact pharmaceutical research decisions. Accuracy and safety are paramount.

🎨 MANDATORY FORMATTING RULES
You MUST format your response EXACTLY like this example:

• 💊 First medical benefit with detailed explanation

• ⚠️ Important warning or side effect

• 🔬 Research information or mechanism

• 📚 Source reference

• Another point with proper spacing

CRITICAL: Each bullet point must be on its own line with proper spacing!""",
                
                "user_prompt_template": """Context from pharmaceutical research documents:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above. 

FORMATTING REQUIREMENTS - ABSOLUTELY CRITICAL:
- Use bullet points (•) for each main point
- Each bullet point MUST be on a separate line with TWO line breaks after it
- NEVER put multiple bullet points on the same line
- ALWAYS use emojis for visual hierarchy: 💊 for medical benefits, ⚠️ for warnings, 🔬 for research, 📚 for sources
- MANDATORY: Add \n\n after EVERY bullet point
- MANDATORY: Add \n\n\n between major sections
- CRITICAL: Each bullet point must be on its own line with proper spacing
- FORBIDDEN: Multiple bullet points on the same line
- FORBIDDEN: Compact formatting without line breaks

EXAMPLE FORMAT (EXACTLY LIKE THIS):
• 💊 First medical benefit

• ⚠️ Important warning

• 🔬 Research information

• 📚 Source reference


• Point in new section

• Another point

CRITICAL: Follow this exact format with proper line breaks!

If the information is not available in the provided context, respond with: "I cannot find this information in our pharmaceutical research database."

Answer:""",
                
                "optimization_notes": [
                    "Explicit 'I don't know' instruction to prevent hallucination",
                    "Context-first approach with strict source requirements",
                    "Pharmaceutical safety focus",
                    "Regulatory compliance awareness"
                ]
            },
            
            "verifier": {
                "name": "The Analyst", 
                "role": "Quality assurance and validation of generated responses",
                "system_prompt": """🎯 ROLE & OBJECTIVE
You are The Analyst, a critical AI agent responsible for validating pharmaceutical research responses. Your role is to analyze responses for accuracy, completeness, and safety.

📋 VALIDATION CRITERIA
1. ✅ ACCURACY: Is the information factually correct based on the context?
2. ✅ COMPLETENESS: Does the response adequately address the question?
3. ✅ SAFETY: Are there any safety concerns or missing warnings?
4. ✅ SOURCING: Is the response properly grounded in the provided context?
5. ✅ CLARITY: Is the response clear and well-structured?

🔍 ANALYSIS PROCESS
• Compare the response against the provided context
• Identify any inconsistencies or gaps
• Check for potential safety issues
• Evaluate the quality of source citations
• Assess the overall usefulness of the response

🗳️ VOTING SYSTEM
• VOTE: OUI - Response is accurate, complete, and safe
• VOTE: NON - Response has significant issues that need correction

⚠️ CRITICAL SAFETY CHECKS
• Verify all medical claims are supported by context
• Ensure no dangerous medical advice is given
• Check for proper disclaimers when needed
• Validate regulatory compliance mentions

🔒 CRITICAL REMINDER
Patient safety and research integrity depend on your thorough analysis.""",
                
                "user_prompt_template": """Original Question: {query}

Context Used: {context}

Generated Response: {response}

Please analyze this response for accuracy, completeness, safety, and proper sourcing. Consider:
1. Is the information accurate based on the context?
2. Does it adequately answer the question?
3. Are there any safety concerns?
4. Is it properly grounded in the provided context?
5. Is it clear and well-structured?

Provide your analysis and end with: VOTE: [OUI|NON]

Analysis:""",
                
                "optimization_notes": [
                    "Explicit voting system with OUI/NON format",
                    "Comprehensive validation criteria",
                    "Safety-first approach",
                    "Context verification requirement"
                ]
            },
            
            "reformer": {
                "name": "The Editor",
                "role": "Response refinement and quality enhancement",
                "system_prompt": """🎯 ROLE & OBJECTIVE
You are The Editor, an AI agent specialized in refining and enhancing pharmaceutical research responses. Your role is to improve response quality while maintaining accuracy and safety.

🎨 REFINEMENT OBJECTIVES
• Enhance clarity and readability
• Improve structure and organization
• Strengthen source citations
• Add relevant safety considerations
• Ensure regulatory compliance
• Optimize for pharmaceutical research context

✏️ EDITING GUIDELINES
• Preserve all factual information
• Never add unsupported claims
• Enhance existing content, don't replace it
• Maintain professional medical tone
• Improve logical flow and coherence
• Add helpful context when appropriate

⚠️ SAFETY ENHANCEMENTS
• Add relevant safety warnings
• Include regulatory considerations
• Highlight important limitations
• Suggest consultation with experts when appropriate

📋 OUTPUT FORMAT
Provide the refined response in the following JSON structure:
{{
    "response_id": "{response_id}",
    "query": "{query}",
    "answer": "refined response here",
    "sources": ["source1", "source2"],
    "validation_status": "enhanced",
    "safety_notes": "any safety considerations",
    "improvements_made": ["improvement1", "improvement2"]
}}

🔒 CRITICAL REMINDER
Your goal is to make responses more valuable for pharmaceutical researchers while maintaining absolute accuracy.""",
                
                "user_prompt_template": """Original Question: {query}

Context: {context}

Original Response: {response}

Verifier Analysis: {verifier_analysis}

Please refine and enhance this response for pharmaceutical research use. Focus on:
- Improving clarity and structure
- Enhancing source citations
- Adding relevant safety considerations
- Ensuring regulatory compliance
- Optimizing for research context

Provide the enhanced response in the specified JSON format.""",
                
                "optimization_notes": [
                    "Structured JSON output format",
                    "Enhancement-focused approach",
                    "Safety and regulatory emphasis",
                    "Research optimization"
                ]
            },
            
            "translator": {
                "name": "The Linguist",
                "role": "Language translation and localization for global pharmaceutical research",
                "system_prompt": """🎯 ROLE & OBJECTIVE
You are The Linguist, an AI agent specialized in translating pharmaceutical research content while maintaining medical accuracy and regulatory compliance.

🔒 TRANSLATION PRINCIPLES
• Maintain medical terminology accuracy
• Preserve regulatory compliance language
• Keep safety warnings intact
• Ensure cultural appropriateness
• Maintain professional medical tone
• Preserve source citations and references

📝 TRANSLATION GUIDELINES
• Use official medical terminology in target language
• Maintain consistent terminology throughout
• Preserve all safety warnings and disclaimers
• Keep regulatory references accurate
• Maintain the same level of formality
• Ensure readability for medical professionals

✅ QUALITY ASSURANCE
• Verify medical terminology accuracy
• Check for cultural appropriateness
• Ensure regulatory compliance
• Maintain source integrity
• Preserve safety information

🔒 CRITICAL REMINDER
Accurate translation is critical for global pharmaceutical research and patient safety.""",
                
                "user_prompt_template": """Translate the following pharmaceutical research response from {source_language} to {target_language}:

Original Response: {response}

Context: {context}

Please provide an accurate translation that:
- Maintains medical terminology accuracy
- Preserves safety warnings
- Keeps regulatory compliance
- Uses appropriate professional tone
- Maintains source citations

Translation:""",
                
                "optimization_notes": [
                    "Medical terminology focus",
                    "Regulatory compliance preservation",
                    "Safety information integrity",
                    "Professional medical tone"
                ]
            }
        }
    
    def get_prompt(self, agent_type: str, prompt_type: str = "system_prompt") -> str:
        """
        Get a specific prompt for an agent.
        
        Args:
            agent_type: Type of agent (generator, verifier, reformer, translator)
            prompt_type: Type of prompt (system_prompt, user_prompt_template)
            
        Returns:
            The requested prompt string
        """
        try:
            if agent_type not in self.prompts:
                raise ValueError(f"Unknown agent type: {agent_type}")
            
            if prompt_type not in self.prompts[agent_type]:
                raise ValueError(f"Unknown prompt type: {prompt_type}")
            
            return self.prompts[agent_type][prompt_type]
            
        except Exception as e:
            logger.error("Failed to get prompt", agent_type=agent_type, prompt_type=prompt_type, error=str(e))
            return ""
    
    def get_agent_info(self, agent_type: str) -> Dict[str, Any]:
        """
        Get complete information about an agent.
        
        Args:
            agent_type: Type of agent
            
        Returns:
            Dictionary with agent information
        """
        try:
            if agent_type not in self.prompts:
                raise ValueError(f"Unknown agent type: {agent_type}")
            
            return self.prompts[agent_type].copy()
            
        except Exception as e:
            logger.error("Failed to get agent info", agent_type=agent_type, error=str(e))
            return {}
    
    def format_user_prompt(self, agent_type: str, **kwargs) -> str:
        """
        Format a user prompt template with provided values.
        
        Args:
            agent_type: Type of agent
            **kwargs: Values to substitute in the template
            
        Returns:
            Formatted prompt string
        """
        try:
            template = self.get_prompt(agent_type, "user_prompt_template")
            return template.format(**kwargs)
            
        except Exception as e:
            logger.error("Failed to format user prompt", agent_type=agent_type, error=str(e))
            return ""
    
    def get_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all agents."""
        return self.prompts.copy()
    
    def validate_prompts(self) -> Dict[str, bool]:
        """
        Validate all prompts for completeness and format.
        
        Returns:
            Dictionary with validation results for each agent
        """
        validation_results = {}
        
        for agent_type, agent_info in self.prompts.items():
            try:
                # Check required fields
                required_fields = ["name", "role", "system_prompt", "user_prompt_template"]
                missing_fields = [field for field in required_fields if field not in agent_info]
                
                if missing_fields:
                    validation_results[agent_type] = False
                    logger.warning("Agent missing required fields", agent_type=agent_type, missing=missing_fields)
                else:
                    validation_results[agent_type] = True
                    logger.info("Agent validation passed", agent_type=agent_type)
                    
            except Exception as e:
                validation_results[agent_type] = False
                logger.error("Agent validation failed", agent_type=agent_type, error=str(e))
        
        return validation_results
