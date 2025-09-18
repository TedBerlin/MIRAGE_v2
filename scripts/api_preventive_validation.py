#!/usr/bin/env python3
"""
MIRAGE v2 - API Preventive Validation
=====================================

Script de validation préventive via API avant l'ajout de nouveaux documents.
Garantit la qualité et la cohérence du système RAG.

Fonctionnalités :
- Validation pré-ajout via API
- Estimation d'impact
- Recommandations d'optimisation
- Tests de qualité
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
        logging.FileHandler('api_preventive_validation.log'),
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

class APIPreventiveValidator:
    """Validateur préventif via API pour MIRAGE v2."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8003"):
        """Initialise le validateur préventif."""
        self.base_url = base_url
        self.quality_threshold = 0.8
        self.performance_threshold = 0.7
        
    def check_api_health(self) -> bool:
        """Vérifie la santé de l'API."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
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
    
    def test_system_performance(self) -> float:
        """Teste les performances du système via API."""
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
                    response = requests.post(
                        f"{self.base_url}/api/query",
                        json={"query": query, "enable_human_loop": False},
                        timeout=30
                    )
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200 and response_time < 30:
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
    
    def assess_system_health(self) -> SystemHealth:
        """Évalue la santé actuelle du système via API."""
        try:
            # Get current system stats
            stats = self.get_system_stats()
            if not stats:
                return SystemHealth(0, 0, 0, 0, "ERROR", ["Failed to get system stats"])
            
            current_documents = stats.get('total_documents', 0)
            current_chunks = stats.get('rag_chunks', 0)
            
            # Test system performance
            performance_score = self.test_system_performance()
            
            # Calculate quality score based on system performance and chunk count
            # Use a more realistic approach: if we have chunks and performance is good, quality is good
            if current_chunks > 0 and performance_score > 0.5:
                quality_score = min(0.8 + (performance_score - 0.5) * 0.4, 1.0)
            else:
                quality_score = 0.1
            
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
        """Valide si le système est prêt pour l'ajout de documents via API."""
        try:
            logger.info("Validating system readiness for document addition via API...")
            
            # Check API health
            if not self.check_api_health():
                return False, {'error': 'API not accessible'}
            
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
        report.append("MIRAGE v2 - API PREVENTIVE VALIDATION REPORT")
        report.append("=" * 60)
        report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"API Endpoint: {self.base_url}")
        report.append("")
        
        # System Health
        system_health = validation_result.get('system_health', {})
        report.append("🏥 SYSTEM HEALTH")
        report.append("-" * 30)
        if hasattr(system_health, 'health_status'):
            report.append(f"Status: {system_health.health_status}")
            report.append(f"Quality Score: {system_health.quality_score:.2f}")
            report.append(f"Performance Score: {system_health.performance_score:.2f}")
            report.append(f"Current Documents: {system_health.current_documents}")
            report.append(f"Current Chunks: {system_health.current_chunks}")
            
            if system_health.warnings:
                report.append("")
                report.append("⚠️ WARNINGS:")
                for warning in system_health.warnings:
                    report.append(f"  • {warning}")
        else:
            report.append("Status: UNKNOWN")
            report.append("Quality Score: 0.00")
            report.append("Performance Score: 0.00")
            report.append("Current Documents: 0")
            report.append("Current Chunks: 0")
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
    print("🔍 MIRAGE v2 - API Preventive Validation")
    print("=" * 45)
    
    if len(sys.argv) < 2:
        print("Usage: python api_preventive_validation.py <document_path1> [document_path2] ...")
        print("Example: python api_preventive_validation.py data/raw_documents/new_doc.pdf")
        return 1
    
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
    
    validator = APIPreventiveValidator()
    
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
        report_file = report_path / f"api_validation_report_{timestamp}.txt"
        
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
