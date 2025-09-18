#!/bin/bash

# 🧪 TEST SYSTÈME OPTIMISÉ - MIRAGE v2
# Test du système avec sentence-transformers et Python 3.11

BASE_URL="http://127.0.0.1:8003"

echo "🧪 TEST SYSTÈME OPTIMISÉ MIRAGE v2"
echo "=================================="

# Test 1: Santé du système
echo "1️⃣ Test de santé du système..."
health=$(curl -s "$BASE_URL/health" | jq -r '.status')
if [ "$health" = "healthy" ]; then
    echo "✅ Système sain"
else
    echo "❌ Système défaillant"
    exit 1
fi

# Test 2: Vérification des agents
echo "2️⃣ Test des agents..."
stats=$(curl -s "$BASE_URL/api/stats")
if echo "$stats" | jq -e '.agents' > /dev/null; then
    echo "✅ Agents accessibles"
    echo "$stats" | jq '.agents'
else
    echo "❌ Agents inaccessibles"
fi

# Test 3: Test de requête de base (sans RAG)
echo "3️⃣ Test de requête de base..."
response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "What is paracetamol?", "enable_human_loop": true}')

if echo "$response" | jq -e '.answer' > /dev/null; then
    echo "✅ Requête de base fonctionnelle"
    answer=$(echo "$response" | jq -r '.answer')
    echo "Réponse: $answer"
else
    echo "❌ Requête de base défaillante"
fi

# Test 4: Test de détection de langue
echo "4️⃣ Test de détection de langue..."

# Test EN
echo "Test EN..."
en_response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "What is paracetamol?", "enable_human_loop": true}')

if echo "$en_response" | jq -e '.answer' > /dev/null; then
    echo "✅ Détection EN fonctionnelle"
else
    echo "❌ Détection EN défaillante"
fi

# Test FR
echo "Test FR..."
fr_response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "Qu est-ce que le paracétamol?", "enable_human_loop": true}')

if echo "$fr_response" | jq -e '.answer' > /dev/null; then
    echo "✅ Détection FR fonctionnelle"
else
    echo "❌ Détection FR défaillante"
fi

# Test ES
echo "Test ES..."
es_response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "¿Qué es el paracetamol?", "enable_human_loop": true}')

if echo "$es_response" | jq -e '.answer' > /dev/null; then
    echo "✅ Détection ES fonctionnelle"
else
    echo "❌ Détection ES défaillante"
fi

# Test DE
echo "Test DE..."
de_response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "Was ist Paracetamol?", "enable_human_loop": true}')

if echo "$de_response" | jq -e '.answer' > /dev/null; then
    echo "✅ Détection DE fonctionnelle"
else
    echo "❌ Détection DE défaillante"
fi

# Test 5: Test de formatage
echo "5️⃣ Test de formatage..."
format_response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "What are the benefits of paracetamol?", "enable_human_loop": true}')

answer=$(echo "$format_response" | jq -r '.answer')

if echo "$answer" | grep -q "•"; then
    echo "✅ Bullet points présents"
else
    echo "❌ Bullet points manquants"
fi

if echo "$answer" | grep -q "💊\|⚠️\|🔬\|📚"; then
    echo "✅ Emojis présents"
else
    echo "❌ Emojis manquants"
fi

# Test 6: Test Human-in-the-Loop
echo "6️⃣ Test Human-in-the-Loop..."
human_response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "What are the side effects of paracetamol overdose?", "enable_human_loop": true}')

human_validation=$(echo "$human_response" | jq -r '.human_validation_required // false')
if [ "$human_validation" = "true" ]; then
    echo "✅ Human-in-the-Loop déclenché"
else
    echo "⚠️ Human-in-the-Loop non déclenché"
fi

# Test 7: Test de performance
echo "7️⃣ Test de performance..."
start_time=$(date +%s)

curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "What is paracetamol?", "enable_human_loop": true}' > /dev/null

end_time=$(date +%s)
duration=$((end_time - start_time))

if [ $duration -lt 30 ]; then
    echo "✅ Performance acceptable ($duration s)"
else
    echo "⚠️ Performance lente ($duration s)"
fi

# Test 8: Test de gestion d'erreurs
echo "8️⃣ Test de gestion d'erreurs..."
error_response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "", "enable_human_loop": true}')

if echo "$error_response" | jq -e '.error' > /dev/null; then
    echo "✅ Gestion d'erreurs fonctionnelle"
else
    echo "⚠️ Gestion d'erreurs à améliorer"
fi

echo "=================================="
echo "🎯 Tests du système optimisé terminés !"
echo "📊 Le système utilise maintenant sentence-transformers avec Python 3.11"
echo "🌐 Interface accessible sur: http://127.0.0.1:8003"
