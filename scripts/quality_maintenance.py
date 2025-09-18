#!/usr/bin/env python3
"""
MIRAGE v2 - Quality Maintenance Script
=====================================

Script spécialisé pour maintenir la qualité du système RAG et garantir
la cohérence des chunks lors de l'ajout de nouveaux documents.

Fonctionnalités :
- Vérification de l'intégrité des chunks
- Réingestion complète si nécessaire
- Validation de la qualité des réponses
- Monitoring des métriques de performance
"""

import sys
import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.rag.rag_engine import RAGEngine
from src.orchestrator.multi_agent_orchestrator import MultiAgentOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('quality_maintenance.log'),
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
    expected_chunks: int
    quality_score: float
    integrity_status: str
    recommendations: List[str]

class QualityMaintenance:
    """Gestionnaire de maintenance de qualité pour MIRAGE v2."""
    
    def __init__(self):
        """Initialise le gestionnaire de qualité."""
        self.rag_engine = None
        self.orchestrator = None
        self.quality_threshold = 0.85  # Seuil de qualité minimum
        self.chunk_efficiency_threshold = 0.8  # Seuil d'efficacité des chunks
        
    def initialize_components(self):
        """Initialise les composants du système."""
        try:
            logger.info("Initializing quality maintenance components...")
            self.rag_engine = RAGEngine()
            self.orchestrator = MultiAgentOrchestrator()
            logger.info("Components initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            return False
    
    def get_current_metrics(self) -> QualityMetrics:
        """Récupère les métriques actuelles du système."""
        try:
            # Get RAG statistics
            rag_stats = self.rag_engine.embedding_manager.get_collection_stats()
            total_documents = rag_stats.get('total_documents', 0)
            total_chunks = rag_stats.get('total_chunks', 0)
            
            # Calculate expected chunks based on document sizes
            expected_chunks = self._calculate_expected_chunks()
            
            # Calculate quality metrics
            chunks_per_document = total_chunks / max(total_documents, 1)
            quality_score = min(total_chunks / max(expected_chunks, 1), 1.0)
            
            # Determine integrity status
            if quality_score >= self.quality_threshold:
                integrity_status = "EXCELLENT"
            elif quality_score >= 0.7:
                integrity_status = "GOOD"
            elif quality_score >= 0.5:
                integrity_status = "FAIR"
            else:
                integrity_status = "POOR"
            
            # Generate recommendations
            recommendations = self._generate_recommendations(quality_score, total_chunks, expected_chunks)
            
            return QualityMetrics(
                total_documents=total_documents,
                total_chunks=total_chunks,
                chunks_per_document=chunks_per_document,
                expected_chunks=expected_chunks,
                quality_score=quality_score,
                integrity_status=integrity_status,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to get current metrics: {e}")
            return QualityMetrics(0, 0, 0, 0, 0, "ERROR", [f"Error: {e}"])
    
    def _calculate_expected_chunks(self) -> int:
        """Calcule le nombre de chunks attendus basé sur les documents."""
        try:
            documents_path = Path("data/raw_documents")
            if not documents_path.exists():
                return 0
            
            total_expected = 0
            for file_path in documents_path.glob("*"):
                if file_path.is_file():
                    # Estimate chunks based on file size and type
                    file_size = file_path.stat().st_size
                    if file_path.suffix.lower() == '.pdf':
                        # PDF: ~1 chunk per 1000 bytes
                        expected_chunks = max(1, file_size // 1000)
                    elif file_path.suffix.lower() == '.txt':
                        # TXT: ~1 chunk per 500 bytes
                        expected_chunks = max(1, file_size // 500)
                    else:
                        # Other formats: conservative estimate
                        expected_chunks = max(1, file_size // 2000)
                    
                    total_expected += expected_chunks
            
            return total_expected
            
        except Exception as e:
            logger.error(f"Failed to calculate expected chunks: {e}")
            return 0
    
    def _generate_recommendations(self, quality_score: float, current_chunks: int, expected_chunks: int) -> List[str]:
        """Génère des recommandations basées sur les métriques."""
        recommendations = []
        
        if quality_score < self.quality_threshold:
            recommendations.append("⚠️ Quality below threshold - consider full reingestion")
        
        if current_chunks < expected_chunks * 0.8:
            recommendations.append("📉 Chunk count significantly below expected - check document processing")
        
        if quality_score < 0.5:
            recommendations.append("🚨 Critical quality issue - immediate reingestion required")
        
        if current_chunks > expected_chunks * 1.5:
            recommendations.append("📈 Chunk count higher than expected - check for duplicates")
        
        if not recommendations:
            recommendations.append("✅ System quality is optimal")
        
        return recommendations
    
    def perform_quality_check(self) -> Tuple[bool, QualityMetrics]:
        """Effectue une vérification complète de la qualité."""
        logger.info("Starting quality check...")
        
        # Get current metrics
        metrics = self.get_current_metrics()
        
        # Log quality status
        logger.info(f"Quality Status: {metrics.integrity_status}")
        logger.info(f"Quality Score: {metrics.quality_score:.2f}")
        logger.info(f"Total Documents: {metrics.total_documents}")
        logger.info(f"Total Chunks: {metrics.total_chunks}")
        logger.info(f"Expected Chunks: {metrics.expected_chunks}")
        
        # Check if quality is acceptable
        quality_acceptable = metrics.quality_score >= self.quality_threshold
        
        # Log recommendations
        for recommendation in metrics.recommendations:
            logger.info(f"Recommendation: {recommendation}")
        
        return quality_acceptable, metrics
    
    def perform_full_reingestion(self) -> bool:
        """Effectue une réingestion complète du système RAG."""
        try:
            logger.info("Starting full system reingestion...")
            
            # Force complete reingestion
            result = self.rag_engine.ingest_documents(force_reprocess=True)
            
            if result.get('success', False):
                logger.info("Full reingestion completed successfully")
                return True
            else:
                logger.error(f"Reingestion failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to perform full reingestion: {e}")
            return False
    
    def test_response_quality(self, test_queries: List[str]) -> Dict[str, float]:
        """Teste la qualité des réponses avec des requêtes de test."""
        logger.info("Testing response quality...")
        
        quality_scores = {}
        
        for query in test_queries:
            try:
                # Process query through orchestrator
                result = self.orchestrator.process_query(query, enable_human_loop=False)
                
                if result.get('success', False):
                    # Calculate quality score based on response characteristics
                    answer = result.get('answer', '')
                    sources = result.get('sources', [])
                    
                    # Quality factors
                    has_content = len(answer) > 50
                    has_sources = len(sources) > 0
                    not_generic = "I cannot find this information" not in answer
                    
                    # Calculate score
                    score = 0
                    if has_content: score += 0.4
                    if has_sources: score += 0.3
                    if not_generic: score += 0.3
                    
                    quality_scores[query] = score
                    logger.info(f"Query: {query[:50]}... | Quality: {score:.2f}")
                else:
                    quality_scores[query] = 0.0
                    logger.warning(f"Query failed: {query[:50]}...")
                    
            except Exception as e:
                logger.error(f"Error testing query '{query}': {e}")
                quality_scores[query] = 0.0
        
        return quality_scores
    
    def generate_quality_report(self, metrics: QualityMetrics, response_scores: Dict[str, float]) -> str:
        """Génère un rapport de qualité détaillé."""
        report = []
        report.append("=" * 60)
        report.append("MIRAGE v2 - QUALITY MAINTENANCE REPORT")
        report.append("=" * 60)
        report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # System Metrics
        report.append("📊 SYSTEM METRICS")
        report.append("-" * 30)
        report.append(f"Total Documents: {metrics.total_documents}")
        report.append(f"Total Chunks: {metrics.total_chunks}")
        report.append(f"Expected Chunks: {metrics.expected_chunks}")
        report.append(f"Chunks per Document: {metrics.chunks_per_document:.1f}")
        report.append(f"Quality Score: {metrics.quality_score:.2f}")
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
                report.append(f"  • {query[:40]}... : {score:.2f}")
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
            report.append("1. Perform full system reingestion")
            report.append("2. Verify document processing pipeline")
            report.append("3. Check QDrant collection integrity")
        else:
            report.append("1. System quality is optimal")
            report.append("2. Continue monitoring")
        report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def run_maintenance_cycle(self) -> bool:
        """Exécute un cycle complet de maintenance."""
        logger.info("Starting quality maintenance cycle...")
        
        # Initialize components
        if not self.initialize_components():
            return False
        
        # Perform quality check
        quality_acceptable, metrics = self.perform_quality_check()
        
        # Test response quality with sample queries
        test_queries = [
            "What are the side effects of chemotherapy?",
            "How does immunotherapy work?",
            "What are the advantages of targeted therapy?",
            "What are the contraindications for radiation therapy?"
        ]
        
        response_scores = self.test_response_quality(test_queries)
        
        # Generate report
        report = self.generate_quality_report(metrics, response_scores)
        
        # Save report
        report_path = Path("quality_reports")
        report_path.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = report_path / f"quality_report_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Quality report saved to: {report_file}")
        print(report)
        
        # Perform corrective actions if needed
        if not quality_acceptable:
            logger.warning("Quality below threshold - performing corrective actions...")
            if self.perform_full_reingestion():
                logger.info("Corrective actions completed successfully")
                return True
            else:
                logger.error("Corrective actions failed")
                return False
        
        return True

def main():
    """Point d'entrée principal."""
    print("🔧 MIRAGE v2 - Quality Maintenance Script")
    print("=" * 50)
    
    maintenance = QualityMaintenance()
    
    try:
        success = maintenance.run_maintenance_cycle()
        
        if success:
            print("\n✅ Quality maintenance completed successfully")
            return 0
        else:
            print("\n❌ Quality maintenance failed")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Maintenance interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Maintenance failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
