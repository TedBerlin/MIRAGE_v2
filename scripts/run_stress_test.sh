#!/bin/bash

# 🧪 SCRIPT DE STRESS TEST MIRAGE v2
# Exécute le plan de test complet pour valider l'alignement au brief initial

set -e

# Configuration
BASE_URL="http://127.0.0.1:8003"
LOG_FILE="stress_test_results_$(date +%Y%m%d_%H%M%S).log"
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions utilitaires
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
    ((PASSED_TESTS++))
}

error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
    ((FAILED_TESTS++))
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}" | tee -a "$LOG_FILE"
}

# Fonction de test d'API
test_api_call() {
    local test_name="$1"
    local query="$2"
    local expected_language="$3"
    local expected_format="$4"
    
    ((TOTAL_TESTS++))
    log "Test: $test_name"
    
    response=$(curl -s -X POST "$BASE_URL/api/query" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\", \"enable_human_loop\": true}")
    
    if [ $? -eq 0 ]; then
        # Vérifier la réponse
        answer=$(echo "$response" | jq -r '.answer // "ERROR"')
        
        if [ "$answer" != "ERROR" ]; then
            # Vérifier le formatage (bullet points)
            if echo "$answer" | grep -q "•"; then
                success "$test_name - Formatage correct"
            else
                error "$test_name - Formatage manquant"
            fi
            
            # Vérifier les emojis
            if echo "$answer" | grep -q "💊\|⚠️\|🔬\|📚"; then
                success "$test_name - Emojis présents"
            else
                warning "$test_name - Emojis manquants"
            fi
            
        else
            error "$test_name - Erreur de réponse"
        fi
    else
        error "$test_name - Erreur de connexion"
    fi
}

# Fonction de test de statut
test_system_status() {
    local test_name="$1"
    
    ((TOTAL_TESTS++))
    log "Test: $test_name"
    
    response=$(curl -s "$BASE_URL/health")
    
    if [ $? -eq 0 ]; then
        status=$(echo "$response" | jq -r '.status // "ERROR"')
        if [ "$status" = "healthy" ]; then
            success "$test_name - Système sain"
        else
            error "$test_name - Système défaillant"
        fi
    else
        error "$test_name - Impossible de contacter le système"
    fi
}

# Fonction de test de charge
test_load() {
    local test_name="$1"
    local num_requests="$2"
    
    ((TOTAL_TESTS++))
    log "Test: $test_name ($num_requests requêtes)"
    
    start_time=$(date +%s)
    
    # Lancer les requêtes en parallèle
    for i in $(seq 1 $num_requests); do
        curl -s -X POST "$BASE_URL/api/query" \
            -H "Content-Type: application/json" \
            -d "{\"query\": \"Test query $i\", \"enable_human_loop\": true}" &
    done
    
    # Attendre la fin de toutes les requêtes
    wait
    
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    if [ $duration -lt 60 ]; then
        success "$test_name - Performance acceptable ($duration s)"
    else
        warning "$test_name - Performance lente ($duration s)"
    fi
}

# Début du stress test
log "🚀 DÉBUT DU STRESS TEST MIRAGE v2"
log "📊 Log des résultats: $LOG_FILE"

# PHASE 1: Tests de détection de langue
log "🌍 PHASE 1: Tests de détection de langue"

# Tests EN
test_api_call "EN - Side effects" "What are the side effects of paracetamol overdose?" "en" "bullet"
test_api_call "EN - Mechanism" "What is the mechanism of action of paracetamol?" "en" "bullet"
test_api_call "EN - Contraindications" "What are the contraindications for paracetamol in children?" "en" "bullet"

# Tests FR
test_api_call "FR - Effets secondaires" "Quels sont les effets secondaires du paracétamol?" "fr" "bullet"
test_api_call "FR - Mécanisme" "Quel est le mécanisme d'action du paracétamol?" "fr" "bullet"
test_api_call "FR - Contre-indications" "Quelles sont les contre-indications du paracétamol chez les enfants?" "fr" "bullet"

# Tests ES
test_api_call "ES - Efectos secundarios" "¿Cuáles son los efectos secundarios del paracetamol?" "es" "bullet"
test_api_call "ES - Mecanismo" "¿Cuál es el mecanismo de acción del paracetamol?" "es" "bullet"
test_api_call "ES - Contraindicaciones" "¿Cuáles son las contraindicaciones del paracetamol en niños?" "es" "bullet"

# Tests DE
test_api_call "DE - Nebenwirkungen" "Welche Nebenwirkungen hat Paracetamol?" "de" "bullet"
test_api_call "DE - Wirkmechanismus" "Wie wirkt Paracetamol?" "de" "bullet"
test_api_call "DE - Kontraindikationen" "Welche Kontraindikationen hat Paracetamol bei Kindern?" "de" "bullet"

# PHASE 2: Tests de contenu RAG
log "📚 PHASE 2: Tests de contenu RAG"

# Questions liées aux documents
test_api_call "RAG - Safety research" "What does the research say about paracetamol safety in pregnancy?" "en" "bullet"
test_api_call "RAG - Efficacy studies" "Are there any recent studies on paracetamol efficacy in chronic pain?" "en" "bullet"
test_api_call "RAG - Regulatory guidelines" "What are the regulatory guidelines for paracetamol dosing?" "en" "bullet"

# Questions hors documents (test "Je ne sais pas")
test_api_call "HORS RAG - Aspirin" "What are the side effects of aspirin overdose?" "en" "bullet"
test_api_call "HORS RAG - Ibuprofen" "What is the mechanism of action of ibuprofen?" "en" "bullet"
test_api_call "HORS RAG - Non-pharma" "What is the weather like today?" "en" "bullet"

# PHASE 3: Tests de formatage
log "🎨 PHASE 3: Tests de formatage"

# Test de formatage détaillé
test_api_call "FORMAT - Bullet points" "What are the benefits and risks of paracetamol?" "en" "bullet"
test_api_call "FORMAT - Emojis" "What are the clinical uses of paracetamol?" "en" "bullet"
test_api_call "FORMAT - Line breaks" "What are the dosage recommendations for paracetamol?" "en" "bullet"

# PHASE 4: Tests des agents
log "🤖 PHASE 4: Tests des agents"

# Test de statut système
test_system_status "SYSTEM - Health check"

# Test des statistiques
log "Test: STATS - Vérification des agents"
stats_response=$(curl -s "$BASE_URL/api/stats")
if [ $? -eq 0 ]; then
    success "STATS - Agents accessibles"
else
    error "STATS - Agents inaccessibles"
fi

# PHASE 5: Tests Human-in-the-Loop
log "👥 PHASE 5: Tests Human-in-the-Loop"

# Questions avec déclenchement automatique
test_api_call "HUMAN - Safety keywords" "What are the side effects of paracetamol overdose?" "en" "bullet"
test_api_call "HUMAN - Medical keywords" "Is paracetamol safe during pregnancy?" "en" "bullet"
test_api_call "HUMAN - Regulatory keywords" "What happens if a child takes too much paracetamol?" "en" "bullet"

# PHASE 6: Tests de gestion d'erreurs
log "⚠️ PHASE 6: Tests de gestion d'erreurs"

# Test de questions vides
test_api_call "ERROR - Empty query" "" "en" "bullet"
test_api_call "ERROR - Whitespace" "   " "en" "bullet"

# PHASE 7: Tests de performance
log "⚡ PHASE 7: Tests de performance"

# Test de charge
test_load "LOAD - 5 requêtes simultanées" 5
test_load "LOAD - 10 requêtes simultanées" 10

# Résumé final
log "📊 RÉSUMÉ DU STRESS TEST"
log "Total des tests: $TOTAL_TESTS"
log "Tests réussis: $PASSED_TESTS"
log "Tests échoués: $FAILED_TESTS"

if [ $FAILED_TESTS -eq 0 ]; then
    success "🎉 TOUS LES TESTS SONT PASSÉS !"
    exit 0
else
    error "❌ $FAILED_TESTS TESTS ONT ÉCHOUÉ"
    exit 1
fi
