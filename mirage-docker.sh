#!/bin/bash
# mirage-docker.sh - Gestion Docker pour MIRAGE v2

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'affichage
print_status() {
    echo -e "${BLUE}[MIRAGE]${NC} $1"
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

# Fonction de nettoyage
cleanup() {
    print_status "Nettoyage des ressources..."
    docker-compose down 2>/dev/null || true
    docker system prune -f 2>/dev/null || true
    print_success "Nettoyage terminé"
}

# Fonction de vérification
check_requirements() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    if [ -z "$GEMINI_API_KEY" ]; then
        print_warning "GEMINI_API_KEY non défini, utilisation de la clé par défaut"
        export GEMINI_API_KEY="${GEMINI_API_KEY}"
    fi
}

# Fonction de démarrage
start() {
    print_status "Démarrage de MIRAGE v2 avec Docker..."
    check_requirements
    
    # Nettoyage préalable
    cleanup
    
    # Construction et démarrage
    print_status "Construction de l'image Docker..."
    docker-compose build
    
    print_status "Démarrage des services..."
    docker-compose up -d
    
    # Attente du démarrage
    print_status "Attente du démarrage du service..."
    sleep 10
    
    # Vérification de la santé
    if curl -f http://localhost:8005/health >/dev/null 2>&1; then
        print_success "MIRAGE v2 démarré avec succès !"
        print_success "URL: http://localhost:8005"
        print_success "Health: http://localhost:8005/health"
        print_success "API: http://localhost:8005/api/"
    else
        print_error "Échec du démarrage, vérifiez les logs"
        docker-compose logs
        exit 1
    fi
}

# Fonction d'arrêt
stop() {
    print_status "Arrêt de MIRAGE v2..."
    docker-compose down
    print_success "MIRAGE v2 arrêté"
}

# Fonction de redémarrage
restart() {
    print_status "Redémarrage de MIRAGE v2..."
    stop
    sleep 2
    start
}

# Fonction de statut
status() {
    print_status "Statut des services MIRAGE v2:"
    docker-compose ps
    
    if curl -f http://localhost:8005/health >/dev/null 2>&1; then
        print_success "Service opérationnel"
    else
        print_warning "Service non accessible"
    fi
}

# Fonction de logs
logs() {
    print_status "Affichage des logs MIRAGE v2:"
    docker-compose logs -f
}

# Fonction de nettoyage complet
clean() {
    print_status "Nettoyage complet de MIRAGE v2..."
    docker-compose down -v --rmi all
    docker system prune -af
    print_success "Nettoyage complet terminé"
}

# Fonction de test
test() {
    print_status "Test de MIRAGE v2..."
    if curl -f http://localhost:8005/health >/dev/null 2>&1; then
        print_success "Test de santé réussi"
        
        # Test API
        print_status "Test de l'API..."
        if curl -f http://localhost:8005/api/stats >/dev/null 2>&1; then
            print_success "Test API réussi"
        else
            print_warning "Test API échoué"
        fi
    else
        print_error "Test de santé échoué"
        exit 1
    fi
}

# Menu principal
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    clean)
        clean
        ;;
    test)
        test
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|clean|test}"
        echo ""
        echo "Commandes disponibles:"
        echo "  start   - Démarrer MIRAGE v2"
        echo "  stop    - Arrêter MIRAGE v2"
        echo "  restart - Redémarrer MIRAGE v2"
        echo "  status  - Afficher le statut"
        echo "  logs    - Afficher les logs"
        echo "  clean   - Nettoyage complet"
        echo "  test    - Tester le service"
        exit 1
        ;;
esac

