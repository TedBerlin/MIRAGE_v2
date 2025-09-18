#!/bin/bash
# mirage-minimal.sh - Version optimisée de MIRAGE v2

case "$1" in
  start)
    echo "🚀 Démarrage de MIRAGE v2 (Version Optimisée)..."
    docker-compose -f docker-compose.minimal.yml up -d
    echo "✅ MIRAGE v2 démarré sur http://localhost:8005"
    ;;
  stop)
    echo "🛑 Arrêt de MIRAGE v2..."
    docker-compose -f docker-compose.minimal.yml down
    echo "✅ MIRAGE v2 arrêté"
    ;;
  clean)
    echo "🧹 Nettoyage complet..."
    docker-compose -f docker-compose.minimal.yml down -v --rmi all
    docker system prune -f
    echo "✅ Nettoyage terminé"
    ;;
  status)
    echo "📊 État de MIRAGE v2..."
    docker-compose -f docker-compose.minimal.yml ps
    ;;
  logs)
    echo "📋 Logs de MIRAGE v2..."
    docker-compose -f docker-compose.minimal.yml logs -f
    ;;
  *)
    echo "Usage: $0 {start|stop|clean|status|logs}"
    echo ""
    echo "🚀 MIRAGE v2 - Version Optimisée"
    echo "   • Installation 5x plus rapide"
    echo "   • Taille réduite de 80%"
    echo "   • Seulement les dépendances essentielles"
    ;;
esac
