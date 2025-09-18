#!/usr/bin/env python3
"""
MIRAGE v2 - Automated Quality Maintenance
=========================================

Script de maintenance automatisé de la qualité.
Garantit la qualité et la cohérence du système RAG.

Fonctionnalités :
- Maintenance automatisée
- Optimisation des performances
- Surveillance continue
- Actions correctives automatiques
"""

import sys
import os
import json
import time
import requests
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('quality_maintenance_automated.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MaintenanceAction:
    """Action de maintenance."""
    action_type: str
    description: str
    priority: int
    success: bool
    details: str

class AutomatedQualityMaintenance:
    """Maintenance automatisée de qualité pour MIRAGE v2."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8003"):
        """Initialise la maintenance automatisée."""
        self.base_url = base_url
        self.quality_threshold = 0.8
        self.performance_threshold = 0.7
        self.maintenance_history = []
        
    def check_system_health(self) -> Dict:
        """Vérifie la santé du système."""
        try:
            # Get system stats
            stats_response = requests.get(f"{self.base_url}/api/stats", timeout=10)
            if stats_response.status_code != 200:
                return {'status': 'ERROR', 'error': 'Failed to get system stats'}
            
            stats = stats_response.json()
            
            # Test system performance
            test_query = "What are the side effects of chemotherapy?"
            start_time = time.time()
            
            query_response = requests.post(
                f"{self.base_url}/api/query",
                json={"query": test_query, "enable_human_loop": False},
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if query_response.status_code == 200:
                query_result = query_response.json()
                answer = query_result.get('answer', '')
                sources = query_result.get('sources', [])
                
                # Calculate quality metrics
                has_content = len(answer) > 50
                has_sources = len(sources) > 0
                not_generic = "I cannot find this information" not in answer
                reasonable_time = response_time < 30
                
                quality_score = 0
                if has_content: quality_score += 0.3
                if has_sources: quality_score += 0.2
                if not_generic: quality_score += 0.3
                if reasonable_time: quality_score += 0.2
                
                performance_score = max(0, 1 - (response_time / 30))
                overall_score = (quality_score * 0.6) + (performance_score * 0.4)
                
                return {
                    'status': 'HEALTHY',
                    'quality_score': quality_score,
                    'performance_score': performance_score,
                    'overall_score': overall_score,
                    'response_time': response_time,
                    'total_documents': stats.get('total_documents', 0),
                    'total_chunks': stats.get('rag_chunks', 0)
                }
            else:
                return {'status': 'ERROR', 'error': 'Query test failed'}
                
        except Exception as e:
            logger.error(f"Failed to check system health: {e}")
            return {'status': 'ERROR', 'error': str(e)}
    
    def perform_rag_optimization(self) -> MaintenanceAction:
        """Effectue une optimisation RAG."""
        try:
            logger.info("Performing RAG optimization...")
            
            # Force complete reingestion
            response = requests.post(
                f"{self.base_url}/api/rag/ingest",
                json={"force_reprocess": True},
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    return MaintenanceAction(
                        action_type="RAG_OPTIMIZATION",
                        description="Complete RAG system reingestion",
                        priority=1,
                        success=True,
                        details=f"Successfully processed {result.get('documents_processed', 0)} documents, {result.get('chunks_created', 0)} chunks"
                    )
                else:
                    return MaintenanceAction(
                        action_type="RAG_OPTIMIZATION",
                        description="Complete RAG system reingestion",
                        priority=1,
                        success=False,
                        details=f"Failed: {result.get('error', 'Unknown error')}"
                    )
            else:
                return MaintenanceAction(
                    action_type="RAG_OPTIMIZATION",
                    description="Complete RAG system reingestion",
                    priority=1,
                    success=False,
                    details=f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            logger.error(f"RAG optimization failed: {e}")
            return MaintenanceAction(
                action_type="RAG_OPTIMIZATION",
                description="Complete RAG system reingestion",
                priority=1,
                success=False,
                details=f"Exception: {e}"
            )
    
    def perform_performance_optimization(self) -> MaintenanceAction:
        """Effectue une optimisation des performances."""
        try:
            logger.info("Performing performance optimization...")
            
            # Test multiple queries to warm up the system
            test_queries = [
                "What are the side effects of chemotherapy?",
                "How does immunotherapy work?",
                "What are the advantages of targeted therapy?"
            ]
            
            successful_queries = 0
            total_time = 0
            
            for query in test_queries:
                try:
                    start_time = time.time()
                    response = requests.post(
                        f"{self.base_url}/api/query",
                        json={"query": query, "enable_human_loop": False},
                        timeout=30
                    )
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        successful_queries += 1
                        total_time += response_time
                        
                except Exception as e:
                    logger.warning(f"Query failed: {e}")
                    continue
            
            if successful_queries > 0:
                avg_time = total_time / successful_queries
                return MaintenanceAction(
                    action_type="PERFORMANCE_OPTIMIZATION",
                    description="System warm-up and performance testing",
                    priority=2,
                    success=True,
                    details=f"Tested {successful_queries} queries, avg time: {avg_time:.1f}s"
                )
            else:
                return MaintenanceAction(
                    action_type="PERFORMANCE_OPTIMIZATION",
                    description="System warm-up and performance testing",
                    priority=2,
                    success=False,
                    details="All test queries failed"
                )
                
        except Exception as e:
            logger.error(f"Performance optimization failed: {e}")
            return MaintenanceAction(
                action_type="PERFORMANCE_OPTIMIZATION",
                description="System warm-up and performance testing",
                priority=2,
                success=False,
                details=f"Exception: {e}"
            )
    
    def perform_quality_validation(self) -> MaintenanceAction:
        """Effectue une validation de qualité."""
        try:
            logger.info("Performing quality validation...")
            
            # Test comprehensive quality
            test_queries = [
                "What are the side effects of chemotherapy?",
                "How does immunotherapy work?",
                "What are the advantages of targeted therapy?",
                "What are the contraindications for radiation therapy?",
                "What is the mechanism of action of SSRIs?"
            ]
            
            quality_scores = []
            
            for query in test_queries:
                try:
                    response = requests.post(
                        f"{self.base_url}/api/query",
                        json={"query": query, "enable_human_loop": False},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        answer = result.get('answer', '')
                        sources = result.get('sources', [])
                        
                        # Calculate quality score
                        has_content = len(answer) > 50
                        has_sources = len(sources) > 0
                        not_generic = "I cannot find this information" not in answer
                        
                        score = 0
                        if has_content: score += 0.4
                        if has_sources: score += 0.3
                        if not_generic: score += 0.3
                        
                        quality_scores.append(score)
                        
                except Exception as e:
                    logger.warning(f"Quality test failed for query: {e}")
                    quality_scores.append(0.0)
            
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                return MaintenanceAction(
                    action_type="QUALITY_VALIDATION",
                    description="Comprehensive quality testing",
                    priority=3,
                    success=avg_quality >= 0.7,
                    details=f"Average quality: {avg_quality:.2f} ({len(quality_scores)} tests)"
                )
            else:
                return MaintenanceAction(
                    action_type="QUALITY_VALIDATION",
                    description="Comprehensive quality testing",
                    priority=3,
                    success=False,
                    details="No successful quality tests"
                )
                
        except Exception as e:
            logger.error(f"Quality validation failed: {e}")
            return MaintenanceAction(
                action_type="QUALITY_VALIDATION",
                description="Comprehensive quality testing",
                priority=3,
                success=False,
                details=f"Exception: {e}"
            )
    
    def run_maintenance_cycle(self) -> List[MaintenanceAction]:
        """Exécute un cycle de maintenance complet."""
        logger.info("Starting automated quality maintenance cycle...")
        
        actions = []
        
        # Check system health
        health = self.check_system_health()
        logger.info(f"System health: {health.get('status', 'UNKNOWN')}")
        
        if health.get('status') == 'ERROR':
            logger.error(f"System health check failed: {health.get('error', 'Unknown error')}")
            return actions
        
        # Check if optimization is needed
        overall_score = health.get('overall_score', 0)
        performance_score = health.get('performance_score', 0)
        
        if overall_score < self.quality_threshold:
            logger.warning("Quality below threshold - performing RAG optimization")
            action = self.perform_rag_optimization()
            actions.append(action)
            
            if action.success:
                # Wait for optimization to complete
                time.sleep(10)
                
                # Recheck health
                health = self.check_system_health()
                overall_score = health.get('overall_score', 0)
        
        if performance_score < self.performance_threshold:
            logger.warning("Performance below threshold - performing performance optimization")
            action = self.perform_performance_optimization()
            actions.append(action)
        
        # Always perform quality validation
        logger.info("Performing quality validation...")
        action = self.perform_quality_validation()
        actions.append(action)
        
        # Store actions in history
        self.maintenance_history.extend(actions)
        
        # Keep only last 50 actions
        if len(self.maintenance_history) > 50:
            self.maintenance_history = self.maintenance_history[-50:]
        
        return actions
    
    def generate_maintenance_report(self, actions: List[MaintenanceAction]) -> str:
        """Génère un rapport de maintenance."""
        report = []
        report.append("=" * 60)
        report.append("MIRAGE v2 - AUTOMATED QUALITY MAINTENANCE REPORT")
        report.append("=" * 60)
        report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"API Endpoint: {self.base_url}")
        report.append("")
        
        # Maintenance Actions
        report.append("🔧 MAINTENANCE ACTIONS")
        report.append("-" * 30)
        for i, action in enumerate(actions, 1):
            status = "✅ SUCCESS" if action.success else "❌ FAILED"
            report.append(f"{i}. {action.action_type} - {status}")
            report.append(f"   Description: {action.description}")
            report.append(f"   Priority: {action.priority}")
            report.append(f"   Details: {action.details}")
            report.append("")
        
        # Summary
        successful_actions = sum(1 for action in actions if action.success)
        total_actions = len(actions)
        
        report.append("📊 SUMMARY")
        report.append("-" * 30)
        report.append(f"Total Actions: {total_actions}")
        report.append(f"Successful: {successful_actions}")
        report.append(f"Failed: {total_actions - successful_actions}")
        report.append(f"Success Rate: {(successful_actions / max(total_actions, 1)) * 100:.1f}%")
        report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        report.append("-" * 30)
        if successful_actions == total_actions:
            report.append("1. ✅ All maintenance actions completed successfully")
            report.append("2. 🔄 Continue regular monitoring")
            report.append("3. 📊 Monitor system performance")
        else:
            report.append("1. ⚠️ Some maintenance actions failed")
            report.append("2. 🔍 Check system logs for errors")
            report.append("3. 🔧 Consider manual intervention")
        report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)

def main():
    """Point d'entrée principal."""
    print("🔧 MIRAGE v2 - Automated Quality Maintenance")
    print("=" * 50)
    
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
    
    maintenance = AutomatedQualityMaintenance()
    
    try:
        # Run maintenance cycle
        actions = maintenance.run_maintenance_cycle()
        
        # Generate report
        report = maintenance.generate_maintenance_report(actions)
        print(report)
        
        # Save report
        report_path = Path("maintenance_reports")
        report_path.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = report_path / f"maintenance_report_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n📄 Maintenance report saved to: {report_file}")
        
        # Determine success
        successful_actions = sum(1 for action in actions if action.success)
        total_actions = len(actions)
        
        if successful_actions == total_actions:
            print("\n✅ Maintenance completed successfully")
            return 0
        else:
            print("\n⚠️ Maintenance completed with some failures")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Maintenance interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Maintenance failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
