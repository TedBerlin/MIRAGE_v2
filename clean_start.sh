#!/bin/bash
# clean_start.sh - Script de nettoyage et démarrage propre

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[CLEAN]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Nettoyage des processus Python
cleanup_processes() {
    print_status "Nettoyage des processus Python..."
    
    # Arrêt des processus Python/uvicorn
    pkill -9 -f "python.*web_interface" 2>/dev/null || true
    pkill -9 -f "uvicorn" 2>/dev/null || true
    pkill -9 -f "fastapi" 2>/dev/null || true
    
    sleep 2
    print_success "Processus Python arrêtés"
}

# Libération des ports
free_ports() {
    print_status "Libération des ports..."
    
    for port in {8003..8005}; do
        if lsof -ti:$port >/dev/null 2>&1; then
            print_status "Libération du port $port..."
            lsof -ti:$port | xargs kill -9 2>/dev/null || true
        fi
    done
    
    sleep 1
    print_success "Ports libérés"
}

# Nettoyage des verrous et cache
cleanup_files() {
    print_status "Nettoyage des fichiers temporaires..."
    
    # Suppression des verrous
    find . -name "*.lock" -delete 2>/dev/null || true
    
    # Nettoyage des caches Python
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Nettoyage des caches de test
    rm -rf .pytest_cache .coverage htmlcov/ 2>/dev/null || true
    
    # Nettoyage des embeddings temporaires
    rm -rf ./data/embeddings_* 2>/dev/null || true
    
    print_success "Fichiers temporaires supprimés"
}

# Vérification des ports
check_ports() {
    print_status "Vérification des ports..."
    
    for port in {8003..8005}; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_warning "Port $port toujours occupé"
            return 1
        fi
    done
    
    print_success "Tous les ports sont libres"
    return 0
}

# Démarrage propre
start_clean() {
    print_status "Démarrage propre de MIRAGE v2..."
    
    # Activation de l'environnement conda
    if command -v conda &> /dev/null; then
        print_status "Activation de l'environnement conda..."
        source $(conda info --base)/etc/profile.d/conda.sh
        conda activate mirage-rag
    fi
    
    # Définition de la clé API
    export GEMINI_API_KEY="${GEMINI_API_KEY}"
    
    # Démarrage de l'application
    print_status "Lancement de l'application..."
    python web_interface.py
}

# Fonction principale
main() {
    print_status "=== NETTOYAGE ET DÉMARRAGE PROPRE MIRAGE v2 ==="
    
    # Nettoyage des processus
    cleanup_processes
    
    # Libération des ports
    free_ports
    
    # Nettoyage des fichiers
    cleanup_files
    
    # Vérification des ports
    if ! check_ports; then
        print_error "Impossible de libérer tous les ports"
        print_error "Utilisez Docker pour une solution définitive: ./mirage-docker.sh start"
        exit 1
    fi
    
    # Démarrage propre
    start_clean
}

# Exécution
main "$@"

