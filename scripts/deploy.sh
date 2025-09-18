#!/bin/bash

# MIRAGE v2 - Deployment Script
# Automated deployment for production environments

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${1:-production}"
BACKUP_DIR="${PROJECT_DIR}/backups"
LOG_FILE="${PROJECT_DIR}/logs/deploy.log"

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check if .env file exists
    if [[ ! -f "${PROJECT_DIR}/.env" ]]; then
        error ".env file not found. Please create .env file from .env.template"
    fi
    
    # Check if GEMINI_API_KEY is set
    if ! grep -q "GEMINI_API_KEY=" "${PROJECT_DIR}/.env" || grep -q "GEMINI_API_KEY=your_key_here" "${PROJECT_DIR}/.env"; then
        error "GEMINI_API_KEY not configured in .env file"
    fi
    
    success "Prerequisites check passed"
}

# Create backup
create_backup() {
    log "Creating backup..."
    
    local backup_name="mirage_backup_$(date +%Y%m%d_%H%M%S)"
    local backup_path="${BACKUP_DIR}/${backup_name}"
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup data directory
    if [[ -d "${PROJECT_DIR}/data" ]]; then
        log "Backing up data directory..."
        tar -czf "${backup_path}_data.tar.gz" -C "$PROJECT_DIR" data/
    fi
    
    # Backup configuration
    if [[ -d "${PROJECT_DIR}/config" ]]; then
        log "Backing up configuration..."
        tar -czf "${backup_path}_config.tar.gz" -C "$PROJECT_DIR" config/
    fi
    
    # Backup logs
    if [[ -d "${PROJECT_DIR}/logs" ]]; then
        log "Backing up logs..."
        tar -czf "${backup_path}_logs.tar.gz" -C "$PROJECT_DIR" logs/
    fi
    
    success "Backup created: ${backup_name}"
}

# Build Docker images
build_images() {
    log "Building Docker images..."
    
    cd "$PROJECT_DIR"
    
    # Build main application image
    log "Building MIRAGE v2 application image..."
    docker build -t mirage:v2 -f Dockerfile .
    
    # Build development image if needed
    if [[ "$ENVIRONMENT" == "development" ]]; then
        log "Building development image..."
        docker build -t mirage:v2-dev -f Dockerfile.dev .
    fi
    
    success "Docker images built successfully"
}

# Deploy application
deploy_application() {
    log "Deploying MIRAGE v2 application..."
    
    cd "$PROJECT_DIR"
    
    # Stop existing containers
    log "Stopping existing containers..."
    docker-compose down --remove-orphans || true
    
    # Start services
    if [[ "$ENVIRONMENT" == "development" ]]; then
        log "Starting development environment..."
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
    else
        log "Starting production environment..."
        docker-compose up -d
    fi
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    check_service_health
    
    success "Application deployed successfully"
}

# Check service health
check_service_health() {
    log "Checking service health..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        log "Health check attempt $attempt/$max_attempts"
        
        # Check MIRAGE API
        if curl -f -s http://localhost:8000/health > /dev/null; then
            success "MIRAGE API is healthy"
        else
            warning "MIRAGE API health check failed"
        fi
        
        # Check Dashboard
        if curl -f -s http://localhost:8080 > /dev/null; then
            success "Dashboard is healthy"
        else
            warning "Dashboard health check failed"
        fi
        
        # Check ChromaDB
        if curl -f -s http://localhost:8001/api/v1/heartbeat > /dev/null; then
            success "ChromaDB is healthy"
        else
            warning "ChromaDB health check failed"
        fi
        
        # Check Prometheus
        if curl -f -s http://localhost:9090/-/healthy > /dev/null; then
            success "Prometheus is healthy"
        else
            warning "Prometheus health check failed"
        fi
        
        # Check Grafana
        if curl -f -s http://localhost:3000/api/health > /dev/null; then
            success "Grafana is healthy"
        else
            warning "Grafana health check failed"
        fi
        
        attempt=$((attempt + 1))
        sleep 10
    done
}

# Run tests
run_tests() {
    log "Running deployment tests..."
    
    cd "$PROJECT_DIR"
    
    # Run basic API tests
    log "Testing API endpoints..."
    
    # Test health endpoint
    if curl -f -s http://localhost:8000/health | grep -q "healthy"; then
        success "Health endpoint test passed"
    else
        error "Health endpoint test failed"
    fi
    
    # Test metrics endpoint
    if curl -f -s http://localhost:8000/metrics > /dev/null; then
        success "Metrics endpoint test passed"
    else
        warning "Metrics endpoint test failed"
    fi
    
    # Test dashboard
    if curl -f -s http://localhost:8080 > /dev/null; then
        success "Dashboard test passed"
    else
        warning "Dashboard test failed"
    fi
    
    success "Deployment tests completed"
}

# Show deployment status
show_status() {
    log "Deployment Status:"
    echo "=================="
    
    # Docker containers status
    echo "Docker Containers:"
    docker-compose ps
    
    echo ""
    echo "Service URLs:"
    echo "  API: http://localhost:8000"
    echo "  Dashboard: http://localhost:8080"
    echo "  ChromaDB: http://localhost:8001"
    echo "  Prometheus: http://localhost:9090"
    echo "  Grafana: http://localhost:3000"
    
    echo ""
    echo "Logs:"
    echo "  Application: docker-compose logs mirage"
    echo "  All services: docker-compose logs"
    
    echo ""
    echo "Management:"
    echo "  Stop: docker-compose down"
    echo "  Restart: docker-compose restart"
    echo "  Update: ./scripts/deploy.sh $ENVIRONMENT"
}

# Cleanup old backups
cleanup_backups() {
    log "Cleaning up old backups..."
    
    # Keep only last 10 backups
    if [[ -d "$BACKUP_DIR" ]]; then
        cd "$BACKUP_DIR"
        ls -t | tail -n +11 | xargs -r rm -rf
        success "Old backups cleaned up"
    fi
}

# Main deployment function
main() {
    log "Starting MIRAGE v2 deployment..."
    log "Environment: $ENVIRONMENT"
    log "Project directory: $PROJECT_DIR"
    
    # Create logs directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Run deployment steps
    check_prerequisites
    create_backup
    build_images
    deploy_application
    run_tests
    cleanup_backups
    show_status
    
    success "MIRAGE v2 deployment completed successfully!"
    log "Deployment log: $LOG_FILE"
}

# Handle script arguments
case "${1:-}" in
    "help"|"-h"|"--help")
        echo "MIRAGE v2 Deployment Script"
        echo "Usage: $0 [environment]"
        echo ""
        echo "Environments:"
        echo "  production  - Deploy production environment (default)"
        echo "  development - Deploy development environment"
        echo ""
        echo "Examples:"
        echo "  $0                    # Deploy production"
        echo "  $0 production         # Deploy production"
        echo "  $0 development        # Deploy development"
        echo ""
        echo "Commands:"
        echo "  $0 help               # Show this help"
        echo "  $0 status             # Show deployment status"
        echo "  $0 logs               # Show application logs"
        echo "  $0 stop               # Stop all services"
        echo "  $0 restart            # Restart all services"
        exit 0
        ;;
    "status")
        show_status
        exit 0
        ;;
    "logs")
        cd "$PROJECT_DIR"
        docker-compose logs -f
        exit 0
        ;;
    "stop")
        cd "$PROJECT_DIR"
        docker-compose down
        success "All services stopped"
        exit 0
        ;;
    "restart")
        cd "$PROJECT_DIR"
        docker-compose restart
        success "All services restarted"
        exit 0
        ;;
    *)
        main
        ;;
esac
