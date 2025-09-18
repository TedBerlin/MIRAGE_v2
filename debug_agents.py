#!/usr/bin/env python3
"""
Debug Individuel des Agents MIRAGE v2
Test chaque agent séparément pour identifier les problèmes
"""

import asyncio
import sys
import os
sys.path.append('src')

def test_imports():
    """Test des imports des agents"""
    print("🔍 TEST DES IMPORTS")
    print("=" * 30)
    
    try:
        from agents.generator_agent import GeneratorAgent
        print("✅ GeneratorAgent: Import OK")
    except Exception as e:
        print(f"❌ GeneratorAgent: Erreur - {e}")
        return False
    
    try:
        from agents.verifier_agent import VerifierAgent
        print("✅ VerifierAgent: Import OK")
    except Exception as e:
        print(f"❌ VerifierAgent: Erreur - {e}")
        return False
    
    try:
        from agents.reformer_agent import ReformerAgent
        print("✅ ReformerAgent: Import OK")
    except Exception as e:
        print(f"❌ ReformerAgent: Erreur - {e}")
        return False
    
    try:
        from agents.translator_agent import TranslatorAgent
        print("✅ TranslatorAgent: Import OK")
    except Exception as e:
        print(f"❌ TranslatorAgent: Erreur - {e}")
        return False
    
    try:
        from orchestrator.multi_agent_orchestrator import MultiAgentOrchestrator
        print("✅ MultiAgentOrchestrator: Import OK")
    except Exception as e:
        print(f"❌ MultiAgentOrchestrator: Erreur - {e}")
        return False
    
    return True

def test_agent_initialization():
    """Test de l'initialisation des agents"""
    print("\n🔧 TEST D'INITIALISATION DES AGENTS")
    print("=" * 40)
    
    try:
        from agents.generator_agent import GeneratorAgent
        generator = GeneratorAgent()
        print("✅ GeneratorAgent: Initialisation OK")
    except Exception as e:
        print(f"❌ GeneratorAgent: Erreur - {e}")
        return False
    
    try:
        from agents.verifier_agent import VerifierAgent
        verifier = VerifierAgent()
        print("✅ VerifierAgent: Initialisation OK")
    except Exception as e:
        print(f"❌ VerifierAgent: Erreur - {e}")
        return False
    
    try:
        from agents.reformer_agent import ReformerAgent
        reformer = ReformerAgent()
        print("✅ ReformerAgent: Initialisation OK")
    except Exception as e:
        print(f"❌ ReformerAgent: Erreur - {e}")
        return False
    
    try:
        from agents.translator_agent import TranslatorAgent
        translator = TranslatorAgent()
        print("✅ TranslatorAgent: Initialisation OK")
    except Exception as e:
        print(f"❌ TranslatorAgent: Erreur - {e}")
        return False
    
    return True

def test_orchestrator_initialization():
    """Test de l'initialisation de l'orchestrateur"""
    print("\n🎯 TEST D'INITIALISATION DE L'ORCHESTRATEUR")
    print("=" * 45)
    
    try:
        from orchestrator.multi_agent_orchestrator import MultiAgentOrchestrator
        orchestrator = MultiAgentOrchestrator()
        print("✅ MultiAgentOrchestrator: Initialisation OK")
        
        # Test des stats
        stats = orchestrator.get_system_stats()
        print(f"✅ Stats système: {len(stats)} composants")
        
        # Test du health check
        health = orchestrator.health_check()
        print(f"✅ Health check: {health.get('overall', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ MultiAgentOrchestrator: Erreur - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment():
    """Test de l'environnement"""
    print("\n🌍 TEST DE L'ENVIRONNEMENT")
    print("=" * 25)
    
    # Test de la clé API
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"✅ GEMINI_API_KEY: Définie ({api_key[:10]}...)")
    else:
        print("❌ GEMINI_API_KEY: Non définie")
        return False
    
    # Test du répertoire src
    if os.path.exists("src"):
        print("✅ Répertoire src/: Existe")
    else:
        print("❌ Répertoire src/: Manquant")
        return False
    
    # Test des agents
    agents_path = "src/agents"
    if os.path.exists(agents_path):
        print("✅ Répertoire agents/: Existe")
    else:
        print("❌ Répertoire agents/: Manquant")
        return False
    
    return True

def main():
    """Fonction principale de debug"""
    print("🧪 DEBUG INDIVIDUEL DES AGENTS MIRAGE v2")
    print("=" * 50)
    
    # Tests séquentiels
    tests = [
        ("Environnement", test_environment),
        ("Imports", test_imports),
        ("Initialisation Agents", test_agent_initialization),
        ("Initialisation Orchestrateur", test_orchestrator_initialization)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name.upper()}")
        try:
            success = test_func()
            results.append(success)
            if success:
                print(f"✅ {test_name}: RÉUSSI")
            else:
                print(f"❌ {test_name}: ÉCHOUÉ")
        except Exception as e:
            print(f"💥 {test_name}: ERREUR CRITIQUE - {e}")
            results.append(False)
    
    # Résumé final
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS DU DEBUG")
    print(f"✅ Tests réussis: {sum(results)}/{len(results)}")
    print(f"❌ Tests échoués: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 TOUS LES TESTS DE DEBUG SONT PASSÉS!")
        print("🚀 Le système multi-agent est prêt pour les tests complets")
        return True
    else:
        print("💥 CERTAINS TESTS DE DEBUG ONT ÉCHOUÉ!")
        print("🔧 Correction nécessaire avant de continuer")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
