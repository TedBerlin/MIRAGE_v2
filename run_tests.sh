#!/bin/bash
# Script de lancement automatique des tests du système multi-agent

echo "🚀 Lancement des tests du système multi-agent MIRAGE v2..."
echo "=" * 60

# Vérification de l'environnement
echo "🔍 Vérification de l'environnement..."

if [ ! -d "src" ]; then
    echo "❌ Erreur: Le dossier src/ n'existe pas"
    exit 1
fi

if [ ! -d "src/agents" ]; then
    echo "❌ Erreur: Le dossier src/agents/ n'existe pas"
    exit 1
fi

if [ ! -d "src/orchestrator" ]; then
    echo "❌ Erreur: Le dossier src/orchestrator/ n'existe pas"
    exit 1
fi

echo "✅ Structure des dossiers: OK"

# Vérification de la clé API
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY non définie dans l'environnement"
    echo "   Définissez-la avec: export GEMINI_API_KEY='votre_clé'"
    exit 1
fi

echo "✅ Clé API Gemini: Définie"

# Installation des dépendances si nécessaire
if [ -f "requirements.txt" ]; then
    echo "📦 Vérification des dépendances..."
    pip install -r requirements.txt > /dev/null 2>&1
    echo "✅ Dépendances: Installées"
else
    echo "⚠️  Fichier requirements.txt non trouvé"
fi

# Test de debug d'abord
echo ""
echo "🧪 PHASE 1: DEBUG INDIVIDUEL DES AGENTS"
echo "=" * 40
python debug_agents.py

if [ $? -ne 0 ]; then
    echo "💥 Échec du debug - Arrêt des tests"
    echo "🔧 Actions recommandées:"
    echo "   - Vérifier les imports dans les fichiers agents"
    echo "   - Vérifier la clé API Gemini"
    echo "   - Vérifier la structure des dossiers"
    exit 1
fi

echo ""
echo "🧪 PHASE 2: TEST RAPIDE"
echo "=" * 25
python quick_test.py

if [ $? -ne 0 ]; then
    echo "💥 Échec du test rapide - Arrêt des tests"
    echo "🔧 Actions recommandées:"
    echo "   - Vérifier la connexion à l'API Gemini"
    echo "   - Vérifier les prompts des agents"
    exit 1
fi

echo ""
echo "🧪 PHASE 3: TESTS COMPLETS"
echo "=" * 30
python test_multi_agent_cli.py

# Résultat final
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!"
    echo "📊 Prochaine étape: Intégration web"
    echo "🚀 Le système multi-agent est opérationnel"
else
    echo ""
    echo "💥 ÉCHEC DES TESTS COMPLETS"
    echo "🔧 Debug recommandé:"
    echo "   - Vérifier les logs détaillés ci-dessus"
    echo "   - Tester chaque agent individuellement"
    echo "   - Vérifier la configuration des prompts"
    echo "   - Vérifier la clé API Gemini"
fi
