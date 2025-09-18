#!/usr/bin/env python3
"""
MIRAGE v2 - API Quality Test Script
===================================

Script de test de qualité via API pour éviter les conflits QDrant.
Garantit la qualité et la cohérence du système RAG.

Fonctionnalités :
- Test de qualité via API
- Validation des métriques
- Tests de performance
- Recommandations automatiques
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
        logging.FileHandler('api_quality_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class QualityMetrics:
    """Métriques de qualité du système RAG."""
    total_documents: int
    total_chunks: int
    chunks_per_document: float
    quality_score: float
    performance_score: float
    integrity_status: str
    recommendations: List[str]

class APIQualityTester:
    """Testeur de qualité via API pour MIRAGE v2."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8003"):
        """Initialise le testeur de qualité."""
        self.base_url = base_url
        self.quality_threshold = 0.8
        self.performance_threshold = 0.7
        
    def test_api_connectivity(self) -> bool:
        """Teste la connectivité à l'API."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ API connectivity test passed")
                return True
            else:
                logger.error(f"❌ API health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ API connectivity test failed: {e}")
            return False
    
    def get_system_stats(self) -> Dict:
        """Récupère les statistiques du système via API."""
        try:
            response = requests.get(f"{self.base_url}/api/stats", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get system stats: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return {}
    
    def test_query_quality(self, test_queries: List[str]) -> Dict[str, float]:
        """Teste la qualité des réponses avec des requêtes de test."""
        logger.info("Testing query quality...")
        
        quality_scores = {}
        
        for query in test_queries:
            try:
                start_time = time.time()
                
                # Test query via API
                response = requests.post(
                    f"{self.base_url}/api/query",
                    json={"query": query, "enable_human_loop": False},
                    timeout=30
                )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Calculate quality score
                    answer = result.get('answer', '')
                    sources = result.get('sources', [])
                    
                    # Quality factors
                    has_content = len(answer) > 50
                    has_sources = len(sources) > 0
                    not_generic = "I cannot find this information" not in answer
                    reasonable_time = response_time < 30
                    
                    # Calculate score
                    score = 0
                    if has_content: score += 0.3
                    if has_sources: score += 0.2
                    if not_generic: score += 0.3
                    if reasonable_time: score += 0.2
                    
                    quality_scores[query] = score
                    logger.info(f"Query: {query[:40]}... | Quality: {score:.2f} | Time: {response_time:.1f}s")
                else:
                    quality_scores[query] = 0.0
                    logger.warning(f"Query failed: {query[:40]}... | Status: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error testing query '{query}': {e}")
                quality_scores[query] = 0.0
        
        return quality_scores
    
    def calculate_quality_metrics(self, stats: Dict, response_scores: Dict[str, float]) -> QualityMetrics:
        """Calcule les métriques de qualité."""
        try:
            total_documents = stats.get('total_documents', 0)
            total_chunks = stats.get('rag_chunks', 0)
            
            # Calculate chunks per document
            chunks_per_document = total_chunks / max(total_documents, 1)
            
            # Calculate quality score based on response quality
            if response_scores:
                avg_response_quality = sum(response_scores.values()) / len(response_scores)
            else:
                avg_response_quality = 0.0
            
            # Calculate performance score
            avg_response_time = stats.get('average_response_time', 0)
            performance_score = max(0, 1 - (avg_response_time / 30)) if avg_response_time > 0 else 0.5
            
            # Calculate overall quality score
            quality_score = (avg_response_quality * 0.6) + (performance_score * 0.4)
            
            # Determine integrity status
            if quality_score >= 0.9:
                integrity_status = "EXCELLENT"
            elif quality_score >= 0.8:
                integrity_status = "GOOD"
            elif quality_score >= 0.6:
                integrity_status = "FAIR"
            else:
                integrity_status = "POOR"
            
            # Generate recommendations
            recommendations = []
            if quality_score < self.quality_threshold:
                recommendations.append("⚠️ Quality below threshold - consider system optimization")
            if total_chunks < 200:
                recommendations.append("📉 Low chunk count - consider adding more documents")
            if avg_response_quality < 0.7:
                recommendations.append("🔍 Response quality needs improvement")
            if performance_score < 0.7:
                recommendations.append("⚡ Performance needs optimization")
            
            if not recommendations:
                recommendations.append("✅ System quality is optimal")
            
            return QualityMetrics(
                total_documents=total_documents,
                total_chunks=total_chunks,
                chunks_per_document=chunks_per_document,
                quality_score=quality_score,
                performance_score=performance_score,
                integrity_status=integrity_status,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate quality metrics: {e}")
            return QualityMetrics(0, 0, 0, 0, 0, "ERROR", [f"Error: {e}"])
    
    def test_rag_ingestion(self) -> bool:
        """Teste l'ingestion RAG via API."""
        try:
            logger.info("Testing RAG ingestion...")
            
            response = requests.post(
                f"{self.base_url}/api/rag/ingest",
                json={"force_reprocess": True},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    logger.info("✅ RAG ingestion test passed")
                    return True
                else:
                    logger.error(f"❌ RAG ingestion failed: {result.get('error', 'Unknown error')}")
                    return False
            else:
                logger.error(f"❌ RAG ingestion test failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ RAG ingestion test failed: {e}")
            return False
    
    def generate_quality_report(self, metrics: QualityMetrics, response_scores: Dict[str, float]) -> str:
        """Génère un rapport de qualité détaillé."""
        report = []
        report.append("=" * 60)
        report.append("MIRAGE v2 - API QUALITY TEST REPORT")
        report.append("=" * 60)
        report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"API Endpoint: {self.base_url}")
        report.append("")
        
        # System Metrics
        report.append("📊 SYSTEM METRICS")
        report.append("-" * 30)
        report.append(f"Total Documents: {metrics.total_documents}")
        report.append(f"Total Chunks: {metrics.total_chunks}")
        report.append(f"Chunks per Document: {metrics.chunks_per_document:.1f}")
        report.append(f"Quality Score: {metrics.quality_score:.2f}")
        report.append(f"Performance Score: {metrics.performance_score:.2f}")
        report.append(f"Integrity Status: {metrics.integrity_status}")
        report.append("")
        
        # Response Quality
        if response_scores:
            avg_response_quality = sum(response_scores.values()) / len(response_scores)
            report.append("🎯 RESPONSE QUALITY")
            report.append("-" * 30)
            report.append(f"Average Response Quality: {avg_response_quality:.2f}")
            report.append("")
            for query, score in response_scores.items():
                report.append(f"  • {query[:50]}... : {score:.2f}")
            report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        report.append("-" * 30)
        for i, recommendation in enumerate(metrics.recommendations, 1):
            report.append(f"{i}. {recommendation}")
        report.append("")
        
        # Action Items
        report.append("🔧 ACTION ITEMS")
        report.append("-" * 30)
        if metrics.quality_score < self.quality_threshold:
            report.append("1. Perform system optimization")
            report.append("2. Check RAG document processing")
            report.append("3. Verify API endpoints")
        else:
            report.append("1. System quality is optimal")
            report.append("2. Continue monitoring")
        report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def run_quality_test(self) -> bool:
        """Exécute un test de qualité complet."""
        logger.info("Starting API quality test...")
        
        # Test API connectivity
        if not self.test_api_connectivity():
            logger.error("API connectivity test failed")
            return False
        
        # Get system stats
        stats = self.get_system_stats()
        if not stats:
            logger.error("Failed to get system stats")
            return False
        
        # Test query quality
        test_queries = [
            "What are the side effects of chemotherapy?",
            "How does immunotherapy work?",
            "What are the advantages of targeted therapy?",
            "What are the contraindications for radiation therapy?",
            "What is the mechanism of action of SSRIs?"
        ]
        
        response_scores = self.test_query_quality(test_queries)
        
        # Calculate quality metrics
        metrics = self.calculate_quality_metrics(stats, response_scores)
        
        # Generate report
        report = self.generate_quality_report(metrics, response_scores)
        
        # Save report
        report_path = Path("quality_reports")
        report_path.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = report_path / f"api_quality_report_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Quality report saved to: {report_file}")
        print(report)
        
        # Determine if quality is acceptable
        quality_acceptable = metrics.quality_score >= self.quality_threshold
        
        if quality_acceptable:
            logger.info("✅ Quality test passed - system is in good condition")
            return True
        else:
            logger.warning("⚠️ Quality test failed - system needs optimization")
            return False

def main():
    """Point d'entrée principal."""
    print("🔍 MIRAGE v2 - API Quality Test")
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
    
    tester = APIQualityTester()
    
    try:
        success = tester.run_quality_test()
        
        if success:
            print("\n✅ Quality test completed successfully")
            return 0
        else:
            print("\n⚠️ Quality test completed with warnings")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Quality test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Quality test failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
