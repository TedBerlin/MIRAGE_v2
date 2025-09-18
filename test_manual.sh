#!/bin/bash

# 🧪 TEST MANUEL MIRAGE v2
# Tests rapides pour valider les fonctionnalités critiques

BASE_URL="http://127.0.0.1:8003"

echo "🚀 TEST MANUEL MIRAGE v2"
echo "========================="

# Test 1: Santé du système
echo "1️⃣ Test de santé du système..."
health=$(curl -s "$BASE_URL/health" | jq -r '.status')
if [ "$health" = "healthy" ]; then
    echo "✅ Système sain"
else
    echo "❌ Système défaillant"
    exit 1
fi

# Test 2: Détection de langue EN
echo "2️⃣ Test détection langue EN..."
response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "What are the side effects of paracetamol overdose?", "enable_human_loop": true}')

if echo "$response" | jq -e '.answer' > /dev/null; then
    echo "✅ Réponse EN générée"
    echo "$response" | jq -r '.answer' | head -3
else
    echo "❌ Erreur de réponse EN"
fi

# Test 3: Détection de langue FR
echo "3️⃣ Test détection langue FR..."
response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "Quels sont les effets secondaires du paracétamol?", "enable_human_loop": true}')

if echo "$response" | jq -e '.answer' > /dev/null; then
    echo "✅ Réponse FR générée"
    echo "$response" | jq -r '.answer' | head -3
else
    echo "❌ Erreur de réponse FR"
fi

# Test 4: Détection de langue ES
echo "4️⃣ Test détection langue ES..."
response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "¿Cuáles son los efectos secundarios del paracetamol?", "enable_human_loop": true}')

if echo "$response" | jq -e '.answer' > /dev/null; then
    echo "✅ Réponse ES générée"
    echo "$response" | jq -r '.answer' | head -3
else
    echo "❌ Erreur de réponse ES"
fi

# Test 5: Détection de langue DE
echo "5️⃣ Test détection langue DE..."
response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "Welche Nebenwirkungen hat Paracetamol?", "enable_human_loop": true}')

if echo "$response" | jq -e '.answer' > /dev/null; then
    echo "✅ Réponse DE générée"
    echo "$response" | jq -r '.answer' | head -3
else
    echo "❌ Erreur de réponse DE"
fi

# Test 6: Formatage (bullet points et emojis)
echo "6️⃣ Test de formatage..."
response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "What are the benefits and risks of paracetamol?", "enable_human_loop": true}')

answer=$(echo "$response" | jq -r '.answer')

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

# Test 7: Human-in-the-Loop
echo "7️⃣ Test Human-in-the-Loop..."
response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "What are the side effects of paracetamol overdose?", "enable_human_loop": true}')

human_validation=$(echo "$response" | jq -r '.human_validation_required // false')
if [ "$human_validation" = "true" ]; then
    echo "✅ Human-in-the-Loop déclenché"
else
    echo "⚠️ Human-in-the-Loop non déclenché"
fi

# Test 8: Question hors RAG
echo "8️⃣ Test question hors RAG..."
response=$(curl -s -X POST "$BASE_URL/api/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "What is the weather like today?", "enable_human_loop": true}')

if echo "$response" | jq -e '.answer' > /dev/null; then
    echo "✅ Réponse générée pour question hors RAG"
    echo "$response" | jq -r '.answer' | head -2
else
    echo "❌ Erreur pour question hors RAG"
fi

echo "========================="
echo "🎯 Tests terminés !"
