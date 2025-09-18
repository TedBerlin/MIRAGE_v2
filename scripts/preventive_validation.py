#!/usr/bin/env python3
"""
MIRAGE v2 - Preventive Validation Script
========================================

Script de validation préventive avant l'ajout de nouveaux documents.
Garantit la qualité et la cohérence du système RAG.

Fonctionnalités :
- Validation pré-ajout
- Estimation d'impact
- Recommandations d'optimisation
- Tests de qualité
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
        logging.FileHandler('preventive_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DocumentImpact:
    """Impact d'un nouveau document sur le système."""
    filename: str
    estimated_chunks: int
    file_size: int
    processing_time: float
    quality_impact: float
    recommendations: List[str]

@dataclass
class SystemHealth:
    """État de santé du système avant ajout."""
    current_documents: int
    current_chunks: int
    quality_score: float
    performance_score: float
    health_status: str
    warnings: List[str]

class PreventiveValidator:
    """Validateur préventif pour MIRAGE v2."""
    
    def __init__(self):
        """Initialise le validateur préventif."""
        self.rag_engine = None
        self.orchestrator = None
        self.quality_threshold = 0.8
        self.performance_threshold = 0.7
        
    def initialize(self):
        """Initialise les composants de validation."""
        try:
            logger.info("Initializing preventive validator...")
            self.rag_engine = RAGEngine()
            self.orchestrator = MultiAgentOrchestrator()
            logger.info("Preventive validator initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize preventive validator: {e}")
            return False
    
    def assess_system_health(self) -> SystemHealth:
        """Évalue la santé actuelle du système."""
        try:
            # Get current RAG statistics
            rag_stats = self.rag_engine.embedding_manager.get_collection_stats()
            current_documents = rag_stats.get('total_documents', 0)
            current_chunks = rag_stats.get('total_chunks', 0)
            
            # Calculate quality score
            expected_chunks = self._calculate_expected_chunks()
            quality_score = min(current_chunks / max(expected_chunks, 1), 1.0)
            
            # Test performance with sample queries
            performance_score = self._test_system_performance()
            
            # Determine health status
            if quality_score >= 0.9 and performance_score >= 0.8:
                health_status = "EXCELLENT"
            elif quality_score >= 0.8 and performance_score >= 0.7:
                health_status = "GOOD"
            elif quality_score >= 0.6 and performance_score >= 0.5:
                health_status = "FAIR"
            else:
                health_status = "POOR"
            
            # Generate warnings
            warnings = []
            if quality_score < self.quality_threshold:
                warnings.append("Quality below recommended threshold")
            if performance_score < self.performance_threshold:
                warnings.append("Performance below recommended threshold")
            if current_chunks > 1000:
                warnings.append("High chunk count may impact performance")
            
            return SystemHealth(
                current_documents=current_documents,
                current_chunks=current_chunks,
                quality_score=quality_score,
                performance_score=performance_score,
                health_status=health_status,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Failed to assess system health: {e}")
            return SystemHealth(0, 0, 0, 0, "ERROR", [f"Error: {e}"])
    
    def _calculate_expected_chunks(self) -> int:
        """Calcule le nombre de chunks attendus."""
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
            logger.error(f"Failed to calculate expected chunks: {e}")
            return 0
    
    def _test_system_performance(self) -> float:
        """Teste les performances du système."""
        try:
            test_queries = [
                "What are the side effects of chemotherapy?",
                "How does immunotherapy work?",
                "What are the advantages of targeted therapy?"
            ]
            
            successful_queries = 0
            total_response_time = 0
            
            for query in test_queries:
                start_time = time.time()
                try:
                    result = self.orchestrator.process_query(query, enable_human_loop=False)
                    response_time = time.time() - start_time
                    
                    if result.get('success', False) and response_time < 30:  # 30s timeout
                        successful_queries += 1
                        total_response_time += response_time
                        
                except Exception as e:
                    logger.warning(f"Query test failed: {e}")
                    continue
            
            if successful_queries == 0:
                return 0.0
            
            # Calculate performance score
            success_rate = successful_queries / len(test_queries)
            avg_response_time = total_response_time / successful_queries
            time_score = max(0, 1 - (avg_response_time / 30))  # Penalize slow responses
            
            performance_score = (success_rate * 0.7) + (time_score * 0.3)
            return min(performance_score, 1.0)
            
        except Exception as e:
            logger.error(f"Failed to test system performance: {e}")
            return 0.0
    
    def analyze_document_impact(self, document_path: str) -> DocumentImpact:
        """Analyse l'impact d'un nouveau document."""
        try:
            file_path = Path(document_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Document not found: {document_path}")
            
            filename = file_path.name
            file_size = file_path.stat().st_size
            
            # Estimate chunks based on file type and size
            if file_path.suffix.lower() == '.pdf':
                estimated_chunks = max(1, file_size // 1000)
            elif file_path.suffix.lower() == '.txt':
                estimated_chunks = max(1, file_size // 500)
            else:
                estimated_chunks = max(1, file_size // 2000)
            
            # Estimate processing time
            processing_time = estimated_chunks * 0.1  # 0.1s per chunk
            
            # Estimate quality impact
            quality_impact = min(estimated_chunks / 100, 1.0)  # Cap at 1.0
            
            # Generate recommendations
            recommendations = []
            if file_size > 10 * 1024 * 1024:  # 10MB
                recommendations.append("Large file - consider splitting for better processing")
            if estimated_chunks > 200:
                recommendations.append("High chunk count - monitor processing time")
            if file_path.suffix.lower() not in ['.pdf', '.txt', '.docx']:
                recommendations.append("Unsupported format - may require conversion")
            
            if not recommendations:
                recommendations.append("Document ready for processing")
            
            return DocumentImpact(
                filename=filename,
                estimated_chunks=estimated_chunks,
                file_size=file_size,
                processing_time=processing_time,
                quality_impact=quality_impact,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze document impact: {e}")
            return DocumentImpact(
                filename=document_path,
                estimated_chunks=0,
                file_size=0,
                processing_time=0,
                quality_impact=0,
                recommendations=[f"Error: {e}"]
            )
    
    def validate_addition_readiness(self, document_paths: List[str]) -> Tuple[bool, Dict]:
        """Valide si le système est prêt pour l'ajout de documents."""
        try:
            logger.info("Validating system readiness for document addition...")
            
            # Assess current system health
            system_health = self.assess_system_health()
            
            # Analyze impact of new documents
            document_impacts = []
            total_estimated_chunks = 0
            total_processing_time = 0
            
            for doc_path in document_paths:
                impact = self.analyze_document_impact(doc_path)
                document_impacts.append(impact)
                total_estimated_chunks += impact.estimated_chunks
                total_processing_time += impact.processing_time
            
            # Calculate projected metrics
            projected_documents = system_health.current_documents + len(document_paths)
            projected_chunks = system_health.current_chunks + total_estimated_chunks
            
            # Determine readiness
            readiness_issues = []
            
            if system_health.health_status == "POOR":
                readiness_issues.append("System health is poor - address issues first")
            
            if total_estimated_chunks > 500:
                readiness_issues.append("High chunk count may impact performance")
            
            if total_processing_time > 300:  # 5 minutes
                readiness_issues.append("Long processing time expected")
            
            if projected_chunks > 2000:
                readiness_issues.append("Total chunk count may impact performance")
            
            is_ready = len(readiness_issues) == 0
            
            # Generate recommendations
            recommendations = []
            if not is_ready:
                recommendations.extend(readiness_issues)
            else:
                recommendations.append("System ready for document addition")
                recommendations.append("Consider running quality check after addition")
            
            validation_result = {
                'is_ready': is_ready,
                'system_health': system_health,
                'document_impacts': document_impacts,
                'projected_metrics': {
                    'documents': projected_documents,
                    'chunks': projected_chunks,
                    'processing_time': total_processing_time
                },
                'readiness_issues': readiness_issues,
                'recommendations': recommendations
            }
            
            return is_ready, validation_result
            
        except Exception as e:
            logger.error(f"Failed to validate addition readiness: {e}")
            return False, {'error': str(e)}
    
    def generate_validation_report(self, validation_result: Dict) -> str:
        """Génère un rapport de validation."""
        report = []
        report.append("=" * 60)
        report.append("MIRAGE v2 - PREVENTIVE VALIDATION REPORT")
        report.append("=" * 60)
        report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # System Health
        system_health = validation_result.get('system_health', {})
        report.append("🏥 SYSTEM HEALTH")
        report.append("-" * 30)
        report.append(f"Status: {system_health.get('health_status', 'UNKNOWN')}")
        report.append(f"Quality Score: {system_health.get('quality_score', 0):.2f}")
        report.append(f"Performance Score: {system_health.get('performance_score', 0):.2f}")
        report.append(f"Current Documents: {system_health.get('current_documents', 0)}")
        report.append(f"Current Chunks: {system_health.get('current_chunks', 0)}")
        
        if system_health.get('warnings'):
            report.append("")
            report.append("⚠️ WARNINGS:")
            for warning in system_health['warnings']:
                report.append(f"  • {warning}")
        report.append("")
        
        # Document Impacts
        document_impacts = validation_result.get('document_impacts', [])
        if document_impacts:
            report.append("📄 DOCUMENT IMPACTS")
            report.append("-" * 30)
            for impact in document_impacts:
                report.append(f"File: {impact.filename}")
                report.append(f"  Size: {impact.file_size:,} bytes")
                report.append(f"  Estimated Chunks: {impact.estimated_chunks}")
                report.append(f"  Processing Time: {impact.processing_time:.1f}s")
                report.append(f"  Quality Impact: {impact.quality_impact:.2f}")
                if impact.recommendations:
                    report.append("  Recommendations:")
                    for rec in impact.recommendations:
                        report.append(f"    • {rec}")
                report.append("")
        
        # Projected Metrics
        projected = validation_result.get('projected_metrics', {})
        if projected:
            report.append("📊 PROJECTED METRICS")
            report.append("-" * 30)
            report.append(f"Total Documents: {projected.get('documents', 0)}")
            report.append(f"Total Chunks: {projected.get('chunks', 0)}")
            report.append(f"Processing Time: {projected.get('processing_time', 0):.1f}s")
            report.append("")
        
        # Readiness Status
        is_ready = validation_result.get('is_ready', False)
        report.append("✅ READINESS STATUS")
        report.append("-" * 30)
        if is_ready:
            report.append("🟢 SYSTEM READY FOR DOCUMENT ADDITION")
        else:
            report.append("🔴 SYSTEM NOT READY - ISSUES DETECTED")
        
        readiness_issues = validation_result.get('readiness_issues', [])
        if readiness_issues:
            report.append("")
            report.append("❌ READINESS ISSUES:")
            for issue in readiness_issues:
                report.append(f"  • {issue}")
        report.append("")
        
        # Recommendations
        recommendations = validation_result.get('recommendations', [])
        if recommendations:
            report.append("💡 RECOMMENDATIONS")
            report.append("-" * 30)
            for i, rec in enumerate(recommendations, 1):
                report.append(f"{i}. {rec}")
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)

def main():
    """Point d'entrée principal."""
    print("🔍 MIRAGE v2 - Preventive Validation")
    print("=" * 45)
    
    if len(sys.argv) < 2:
        print("Usage: python preventive_validation.py <document_path1> [document_path2] ...")
        print("Example: python preventive_validation.py data/raw_documents/new_doc.pdf")
        return 1
    
    validator = PreventiveValidator()
    
    if not validator.initialize():
        print("❌ Failed to initialize preventive validator")
        return 1
    
    try:
        # Get document paths from command line
        document_paths = sys.argv[1:]
        
        # Validate addition readiness
        is_ready, validation_result = validator.validate_addition_readiness(document_paths)
        
        # Generate and display report
        report = validator.generate_validation_report(validation_result)
        print(report)
        
        # Save report
        report_path = Path("validation_reports")
        report_path.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = report_path / f"validation_report_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n📄 Validation report saved to: {report_file}")
        
        if is_ready:
            print("\n✅ System is ready for document addition")
            return 0
        else:
            print("\n❌ System is not ready - address issues first")
            return 1
            
    except Exception as e:
        print(f"\n💥 Validation failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
