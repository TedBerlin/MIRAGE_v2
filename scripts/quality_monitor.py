#!/usr/bin/env python3
"""
MIRAGE v2 - Quality Monitor
===========================

Script de surveillance continue de la qualité du système RAG.
Déclenche automatiquement des actions correctives si nécessaire.

Fonctionnalités :
- Surveillance en temps réel
- Alertes automatiques
- Actions correctives automatiques
- Historique des métriques
"""

import sys
import os
import json
import time
import logging
import schedule
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.rag.rag_engine import RAGEngine
from src.orchestrator.multi_agent_orchestrator import MultiAgentOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('quality_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QualityMonitor:
    """Surveillant de qualité pour MIRAGE v2."""
    
    def __init__(self, check_interval: int = 300):  # 5 minutes par défaut
        """Initialise le surveillant de qualité."""
        self.check_interval = check_interval
        self.rag_engine = None
        self.orchestrator = None
        self.quality_history = []
        self.alert_threshold = 0.7
        self.critical_threshold = 0.5
        
    def initialize(self):
        """Initialise les composants de surveillance."""
        try:
            logger.info("Initializing quality monitor...")
            self.rag_engine = RAGEngine()
            self.orchestrator = MultiAgentOrchestrator()
            logger.info("Quality monitor initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize quality monitor: {e}")
            return False
    
    def check_quality(self) -> Dict:
        """Vérifie la qualité actuelle du système."""
        try:
            # Get RAG statistics
            rag_stats = self.rag_engine.embedding_manager.get_collection_stats()
            
            # Calculate quality metrics
            total_documents = rag_stats.get('total_documents', 0)
            total_chunks = rag_stats.get('total_chunks', 0)
            
            # Estimate expected chunks
            expected_chunks = self._estimate_expected_chunks()
            quality_score = min(total_chunks / max(expected_chunks, 1), 1.0)
            
            # Determine status
            if quality_score >= 0.85:
                status = "EXCELLENT"
            elif quality_score >= 0.7:
                status = "GOOD"
            elif quality_score >= 0.5:
                status = "FAIR"
            else:
                status = "POOR"
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'total_documents': total_documents,
                'total_chunks': total_chunks,
                'expected_chunks': expected_chunks,
                'quality_score': quality_score,
                'status': status,
                'chunks_per_document': total_chunks / max(total_documents, 1)
            }
            
            # Store in history
            self.quality_history.append(metrics)
            
            # Keep only last 100 entries
            if len(self.quality_history) > 100:
                self.quality_history = self.quality_history[-100:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to check quality: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'status': 'ERROR'
            }
    
    def _estimate_expected_chunks(self) -> int:
        """Estime le nombre de chunks attendus."""
        try:
            documents_path = Path("data/raw_documents")
            if not documents_path.exists():
                return 0
            
            total_expected = 0
            for file_path in documents_path.glob("*"):
                if file_path.is_file():
                    file_size = file_path.stat().st_size
                    if file_path.suffix.lower() == '.pdf':
                        expected_chunks = max(1, file_size // 1000)
                    elif file_path.suffix.lower() == '.txt':
                        expected_chunks = max(1, file_size // 500)
                    else:
                        expected_chunks = max(1, file_size // 2000)
                    
                    total_expected += expected_chunks
            
            return total_expected
            
        except Exception as e:
            logger.error(f"Failed to estimate expected chunks: {e}")
            return 0
    
    def should_trigger_alert(self, metrics: Dict) -> bool:
        """Détermine si une alerte doit être déclenchée."""
        if 'error' in metrics:
            return True
        
        quality_score = metrics.get('quality_score', 0)
        return quality_score < self.alert_threshold
    
    def should_trigger_critical_action(self, metrics: Dict) -> bool:
        """Détermine si une action critique doit être déclenchée."""
        if 'error' in metrics:
            return True
        
        quality_score = metrics.get('quality_score', 0)
        return quality_score < self.critical_threshold
    
    def perform_corrective_action(self, metrics: Dict) -> bool:
        """Effectue une action corrective."""
        try:
            logger.warning("Performing corrective action...")
            
            # Force complete reingestion
            result = self.rag_engine.ingest_documents(force_reprocess=True)
            
            if result.get('success', False):
                logger.info("Corrective action completed successfully")
                return True
            else:
                logger.error(f"Corrective action failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to perform corrective action: {e}")
            return False
    
    def send_alert(self, metrics: Dict, alert_type: str):
        """Envoie une alerte."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if alert_type == "CRITICAL":
            message = f"🚨 CRITICAL ALERT - Quality Score: {metrics.get('quality_score', 0):.2f}"
        else:
            message = f"⚠️ WARNING - Quality Score: {metrics.get('quality_score', 0):.2f}"
        
        logger.warning(f"{message} at {timestamp}")
        
        # Save alert to file
        alert_file = Path("quality_alerts.log")
        with open(alert_file, 'a') as f:
            f.write(f"{timestamp} - {alert_type}: {message}\n")
    
    def generate_quality_trend(self) -> Dict:
        """Génère une analyse de tendance de la qualité."""
        if len(self.quality_history) < 2:
            return {'trend': 'INSUFFICIENT_DATA'}
        
        recent_scores = [m.get('quality_score', 0) for m in self.quality_history[-10:]]
        older_scores = [m.get('quality_score', 0) for m in self.quality_history[-20:-10]]
        
        if not older_scores:
            return {'trend': 'INSUFFICIENT_DATA'}
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores)
        
        if recent_avg > older_avg * 1.05:
            return {'trend': 'IMPROVING', 'change': recent_avg - older_avg}
        elif recent_avg < older_avg * 0.95:
            return {'trend': 'DECLINING', 'change': recent_avg - older_avg}
        else:
            return {'trend': 'STABLE', 'change': recent_avg - older_avg}
    
    def run_monitoring_cycle(self):
        """Exécute un cycle de surveillance."""
        logger.info("Running quality monitoring cycle...")
        
        # Check current quality
        metrics = self.check_quality()
        
        # Log current status
        if 'error' in metrics:
            logger.error(f"Quality check failed: {metrics['error']}")
        else:
            logger.info(f"Quality Status: {metrics.get('status', 'UNKNOWN')}")
            logger.info(f"Quality Score: {metrics.get('quality_score', 0):.2f}")
            logger.info(f"Total Chunks: {metrics.get('total_chunks', 0)}")
        
        # Check for alerts
        if self.should_trigger_critical_action(metrics):
            self.send_alert(metrics, "CRITICAL")
            logger.critical("Critical quality issue detected - performing corrective action")
            self.perform_corrective_action(metrics)
        elif self.should_trigger_alert(metrics):
            self.send_alert(metrics, "WARNING")
            logger.warning("Quality below threshold - monitoring closely")
        
        # Generate trend analysis
        trend = self.generate_quality_trend()
        if trend['trend'] != 'INSUFFICIENT_DATA':
            logger.info(f"Quality trend: {trend['trend']} (change: {trend.get('change', 0):.3f})")
        
        return metrics
    
    def start_monitoring(self):
        """Démarre la surveillance continue."""
        logger.info(f"Starting quality monitoring (interval: {self.check_interval}s)")
        
        # Schedule monitoring
        schedule.every(self.check_interval).seconds.do(self.run_monitoring_cycle)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring failed: {e}")

def main():
    """Point d'entrée principal."""
    print("🔍 MIRAGE v2 - Quality Monitor")
    print("=" * 40)
    
    monitor = QualityMonitor(check_interval=300)  # 5 minutes
    
    if not monitor.initialize():
        print("❌ Failed to initialize quality monitor")
        return 1
    
    try:
        monitor.start_monitoring()
        return 0
    except KeyboardInterrupt:
        print("\n⚠️ Monitoring stopped by user")
        return 0
    except Exception as e:
        print(f"\n💥 Monitoring failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
