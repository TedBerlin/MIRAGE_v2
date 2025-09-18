#!/bin/bash

# 🖥️ TEST FRONTEND MIRAGE v2
# Tests spécifiques à l'interface utilisateur

BASE_URL="http://127.0.0.1:8003"

echo "🖥️ TEST FRONTEND MIRAGE v2"
echo "=========================="

# Test 1: Interface web accessible
echo "1️⃣ Test d'accès à l'interface web..."
if curl -s "$BASE_URL" | grep -q "MIRAGE v2"; then
    echo "✅ Interface web accessible"
else
    echo "❌ Interface web inaccessible"
    exit 1
fi

# Test 2: API endpoints fonctionnels
echo "2️⃣ Test des endpoints API..."
if curl -s "$BASE_URL/health" | jq -e '.status' > /dev/null; then
    echo "✅ Endpoint /health fonctionnel"
else
    echo "❌ Endpoint /health défaillant"
fi

if curl -s "$BASE_URL/api/stats" | jq -e '.agents' > /dev/null; then
    echo "✅ Endpoint /api/stats fonctionnel"
else
    echo "❌ Endpoint /api/stats défaillant"
fi

# Test 3: Test de requête avec interface
echo "3️⃣ Test de requête via interface..."
response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "What are the side effects of paracetamol overdose?", "enable_human_loop": true}')

if echo "$response" | jq -e '.answer' > /dev/null; then
    echo "✅ Requête via interface fonctionnelle"
    
    # Vérifier les éléments de l'interface
    if echo "$response" | jq -e '.agent_workflow' > /dev/null; then
        echo "✅ Workflow des agents affiché"
    else
        echo "⚠️ Workflow des agents manquant"
    fi
    
    if echo "$response" | jq -e '.human_validation_required' > /dev/null; then
        echo "✅ Human-in-the-Loop affiché"
    else
        echo "⚠️ Human-in-the-Loop manquant"
    fi
    
    if echo "$response" | jq -e '.verification' > /dev/null; then
        echo "✅ Détails de vérification affichés"
    else
        echo "⚠️ Détails de vérification manquants"
    fi
    
else
    echo "❌ Requête via interface défaillante"
fi

# Test 4: Test de formatage dans l'interface
echo "4️⃣ Test de formatage dans l'interface..."
answer=$(echo "$response" | jq -r '.answer')

if echo "$answer" | grep -q "•"; then
    echo "✅ Bullet points présents dans l'interface"
else
    echo "❌ Bullet points manquants dans l'interface"
fi

if echo "$answer" | grep -q "💊\|⚠️\|🔬\|📚"; then
    echo "✅ Emojis présents dans l'interface"
else
    echo "❌ Emojis manquants dans l'interface"
fi

# Test 5: Test de performance de l'interface
echo "5️⃣ Test de performance de l'interface..."
start_time=$(date +%s)

curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "What are the benefits of paracetamol?", "enable_human_loop": true}' > /dev/null

end_time=$(date +%s)
duration=$((end_time - start_time))

if [ $duration -lt 30 ]; then
    echo "✅ Performance acceptable ($duration s)"
else
    echo "⚠️ Performance lente ($duration s)"
fi

# Test 6: Test de gestion d'erreurs de l'interface
echo "6️⃣ Test de gestion d'erreurs de l'interface..."

# Test avec requête vide
error_response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "", "enable_human_loop": true}')

if echo "$error_response" | jq -e '.error' > /dev/null; then
    echo "✅ Gestion d'erreurs fonctionnelle"
else
    echo "⚠️ Gestion d'erreurs à améliorer"
fi

# Test 7: Test de l'interface multilingue
echo "7️⃣ Test de l'interface multilingue..."

# Test français
fr_response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "Quels sont les effets secondaires du paracétamol?", "enable_human_loop": true}')

if echo "$fr_response" | jq -e '.answer' > /dev/null; then
    echo "✅ Interface multilingue fonctionnelle (FR)"
else
    echo "❌ Interface multilingue défaillante (FR)"
fi

# Test espagnol
es_response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "¿Cuáles son los efectos secundarios del paracetamol?", "enable_human_loop": true}')

if echo "$es_response" | jq -e '.answer' > /dev/null; then
    echo "✅ Interface multilingue fonctionnelle (ES)"
else
    echo "❌ Interface multilingue défaillante (ES)"
fi

# Test allemand
de_response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "Welche Nebenwirkungen hat Paracetamol?", "enable_human_loop": true}')

if echo "$de_response" | jq -e '.answer' > /dev/null; then
    echo "✅ Interface multilingue fonctionnelle (DE)"
else
    echo "❌ Interface multilingue défaillante (DE)"
fi

echo "=========================="
echo "🎯 Tests frontend terminés !"
echo "📊 Ouvrez http://127.0.0.1:8003 dans votre navigateur pour tester l'interface graphique"
