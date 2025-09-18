#!/usr/bin/env python3
"""
MIRAGE v2 - API Quality Monitor
===============================

Script de surveillance continue de la qualité via API.
Déclenche automatiquement des actions correctives si nécessaire.

Fonctionnalités :
- Surveillance en temps réel via API
- Alertes automatiques
- Actions correctives automatiques
- Historique des métriques
"""

import sys
import os
import json
import time
import requests
import logging
import schedule
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('api_quality_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class APIQualityMonitor:
    """Surveillant de qualité via API pour MIRAGE v2."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8003", check_interval: int = 300):
        """Initialise le surveillant de qualité."""
        self.base_url = base_url
        self.check_interval = check_interval
        self.quality_history = []
        self.alert_threshold = 0.7
        self.critical_threshold = 0.5
        
    def check_api_health(self) -> bool:
        """Vérifie la santé de l'API."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_quality_metrics(self) -> Dict:
        """Récupère les métriques de qualité via API."""
        try:
            # Get system stats
            stats_response = requests.get(f"{self.base_url}/api/stats", timeout=10)
            if stats_response.status_code != 200:
                return {'error': 'Failed to get system stats'}
            
            stats = stats_response.json()
            
            # Test a simple query
            test_query = "What are the side effects of chemotherapy?"
            query_response = requests.post(
                f"{self.base_url}/api/query",
                json={"query": test_query, "enable_human_loop": False},
                timeout=30
            )
            
            if query_response.status_code == 200:
                query_result = query_response.json()
                answer = query_result.get('answer', '')
                sources = query_result.get('sources', [])
                
                # Calculate quality score
                has_content = len(answer) > 50
                has_sources = len(sources) > 0
                not_generic = "I cannot find this information" not in answer
                
                quality_score = 0
                if has_content: quality_score += 0.4
                if has_sources: quality_score += 0.3
                if not_generic: quality_score += 0.3
            else:
                quality_score = 0.0
            
            # Calculate performance score
            avg_response_time = stats.get('average_response_time', 0)
            performance_score = max(0, 1 - (avg_response_time / 30)) if avg_response_time > 0 else 0.5
            
            # Calculate overall score
            overall_score = (quality_score * 0.6) + (performance_score * 0.4)
            
            # Determine status
            if overall_score >= 0.9:
                status = "EXCELLENT"
            elif overall_score >= 0.8:
                status = "GOOD"
            elif overall_score >= 0.6:
                status = "FAIR"
            else:
                status = "POOR"
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'total_documents': stats.get('total_documents', 0),
                'total_chunks': stats.get('rag_chunks', 0),
                'quality_score': quality_score,
                'performance_score': performance_score,
                'overall_score': overall_score,
                'status': status,
                'avg_response_time': avg_response_time
            }
            
            # Store in history
            self.quality_history.append(metrics)
            
            # Keep only last 100 entries
            if len(self.quality_history) > 100:
                self.quality_history = self.quality_history[-100:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get quality metrics: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'status': 'ERROR'
            }
    
    def should_trigger_alert(self, metrics: Dict) -> bool:
        """Détermine si une alerte doit être déclenchée."""
        if 'error' in metrics:
            return True
        
        overall_score = metrics.get('overall_score', 0)
        return overall_score < self.alert_threshold
    
    def should_trigger_critical_action(self, metrics: Dict) -> bool:
        """Détermine si une action critique doit être déclenchée."""
        if 'error' in metrics:
            return True
        
        overall_score = metrics.get('overall_score', 0)
        return overall_score < self.critical_threshold
    
    def perform_corrective_action(self, metrics: Dict) -> bool:
        """Effectue une action corrective via API."""
        try:
            logger.warning("Performing corrective action via API...")
            
            # Force complete reingestion
            response = requests.post(
                f"{self.base_url}/api/rag/ingest",
                json={"force_reprocess": True},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    logger.info("✅ Corrective action completed successfully")
                    return True
                else:
                    logger.error(f"❌ Corrective action failed: {result.get('error', 'Unknown error')}")
                    return False
            else:
                logger.error(f"❌ Corrective action failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to perform corrective action: {e}")
            return False
    
    def send_alert(self, metrics: Dict, alert_type: str):
        """Envoie une alerte."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if alert_type == "CRITICAL":
            message = f"🚨 CRITICAL ALERT - Quality Score: {metrics.get('overall_score', 0):.2f}"
        else:
            message = f"⚠️ WARNING - Quality Score: {metrics.get('overall_score', 0):.2f}"
        
        logger.warning(f"{message} at {timestamp}")
        
        # Save alert to file
        alert_file = Path("api_quality_alerts.log")
        with open(alert_file, 'a') as f:
            f.write(f"{timestamp} - {alert_type}: {message}\n")
    
    def generate_quality_trend(self) -> Dict:
        """Génère une analyse de tendance de la qualité."""
        if len(self.quality_history) < 2:
            return {'trend': 'INSUFFICIENT_DATA'}
        
        recent_scores = [m.get('overall_score', 0) for m in self.quality_history[-10:]]
        older_scores = [m.get('overall_score', 0) for m in self.quality_history[-20:-10]]
        
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
        logger.info("Running API quality monitoring cycle...")
        
        # Check API health
        if not self.check_api_health():
            logger.error("API health check failed - server may be down")
            return
        
        # Get quality metrics
        metrics = self.get_quality_metrics()
        
        # Log current status
        if 'error' in metrics:
            logger.error(f"Quality check failed: {metrics['error']}")
        else:
            logger.info(f"Quality Status: {metrics.get('status', 'UNKNOWN')}")
            logger.info(f"Overall Score: {metrics.get('overall_score', 0):.2f}")
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
        logger.info(f"Starting API quality monitoring (interval: {self.check_interval}s)")
        
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
    print("🔍 MIRAGE v2 - API Quality Monitor")
    print("=" * 40)
    
    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:8003/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not running or not healthy")
            print("Please start the server with: python web_interface.py")
            return 1
    except:
        print("❌ Server not accessible")
        print("Please start the server with: python web_interface.py")
        return 1
    
    monitor = APIQualityMonitor(check_interval=300)  # 5 minutes
    
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
