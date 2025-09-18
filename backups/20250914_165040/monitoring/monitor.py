"""
System monitoring for MIRAGE v2.

Provides comprehensive system monitoring, health checks, and performance tracking.
"""

import os
import sys
import time
import psutil
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.orchestrator import Orchestrator
from rag.rag_engine import RAGEngine

logger = structlog.get_logger(__name__)


class SystemMonitor:
    """Comprehensive system monitoring for MIRAGE v2."""
    
    def __init__(self, api_key: str, monitoring_interval: int = 30):
        """
        Initialize system monitor.
        
        Args:
            api_key: Gemini API key
            monitoring_interval: Monitoring interval in seconds
        """
        self.api_key = api_key
        self.monitoring_interval = monitoring_interval
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # Initialize components
        self.orchestrator = Orchestrator(api_key=api_key)
        self.rag_engine = RAGEngine()
        
        # Monitoring data
        self.metrics_history = []
        self.health_status = {}
        self.performance_stats = {}
        self.error_logs = []
        
        # Performance thresholds
        self.thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "response_time": 5.0,
            "error_rate": 5.0
        }
        
        # Start monitoring
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start system monitoring."""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            logger.info("System monitoring started", interval=self.monitoring_interval)
    
    def stop_monitoring(self):
        """Stop system monitoring."""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("System monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                # Collect system metrics
                metrics = self._collect_system_metrics()
                
                # Update health status
                self._update_health_status(metrics)
                
                # Check performance thresholds
                self._check_performance_thresholds(metrics)
                
                # Store metrics history
                self._store_metrics(metrics)
                
                # Log monitoring status
                logger.debug("System metrics collected", 
                           cpu=metrics.get("cpu_usage", 0),
                           memory=metrics.get("memory_usage", 0),
                           disk=metrics.get("disk_usage", 0))
                
            except Exception as e:
                logger.error("Error in monitoring loop", error=str(e))
                self.error_logs.append({
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e),
                    "type": "monitoring_error"
                })
            
            # Wait for next monitoring cycle
            time.sleep(self.monitoring_interval)
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics."""
        try:
            # System metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # MIRAGE-specific metrics
            mirage_metrics = self._collect_mirage_metrics()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "system": {
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory.percent,
                    "memory_available": memory.available,
                    "memory_total": memory.total,
                    "disk_usage": (disk.used / disk.total) * 100,
                    "disk_available": disk.free,
                    "disk_total": disk.total
                },
                "process": {
                    "cpu_usage": process_cpu,
                    "memory_usage": process_memory.rss,
                    "memory_percent": process.memory_percent(),
                    "threads": process.num_threads(),
                    "open_files": len(process.open_files())
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "mirage": mirage_metrics
            }
            
        except Exception as e:
            logger.error("Error collecting system metrics", error=str(e))
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _collect_mirage_metrics(self) -> Dict[str, Any]:
        """Collect MIRAGE-specific metrics."""
        try:
            # Get orchestrator stats
            orch_stats = self.orchestrator.get_system_stats()
            
            # Get RAG stats
            rag_stats = self.rag_engine.get_system_stats()
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics()
            
            return {
                "orchestrator": orch_stats,
                "rag": rag_stats,
                "performance": performance_metrics,
                "health": self._get_component_health()
            }
            
        except Exception as e:
            logger.error("Error collecting MIRAGE metrics", error=str(e))
            return {"error": str(e)}
    
    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics from recent data."""
        if not self.metrics_history:
            return {}
        
        # Get recent metrics (last 10 minutes)
        recent_metrics = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m["timestamp"]) > datetime.now() - timedelta(minutes=10)
        ]
        
        if not recent_metrics:
            return {}
        
        # Calculate averages
        cpu_values = [m["system"]["cpu_usage"] for m in recent_metrics if "system" in m]
        memory_values = [m["system"]["memory_usage"] for m in recent_metrics if "system" in m]
        
        return {
            "avg_cpu_usage": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            "avg_memory_usage": sum(memory_values) / len(memory_values) if memory_values else 0,
            "max_cpu_usage": max(cpu_values) if cpu_values else 0,
            "max_memory_usage": max(memory_values) if memory_values else 0,
            "sample_count": len(recent_metrics)
        }
    
    def _get_component_health(self) -> Dict[str, str]:
        """Get health status of MIRAGE components."""
        try:
            # Check orchestrator health
            orch_health = self.orchestrator.health_check()
            
            # Check RAG health
            rag_health = self.rag_engine.get_system_stats()
            
            return {
                "orchestrator": "healthy" if orch_health.get("success") else "unhealthy",
                "rag": "healthy" if rag_health.get("success") else "unhealthy",
                "overall": "healthy" if (
                    orch_health.get("success") and rag_health.get("success")
                ) else "unhealthy"
            }
            
        except Exception as e:
            logger.error("Error checking component health", error=str(e))
            return {
                "orchestrator": "unknown",
                "rag": "unknown", 
                "overall": "unknown"
            }
    
    def _update_health_status(self, metrics: Dict[str, Any]):
        """Update system health status."""
        try:
            # Check system health
            system_health = "healthy"
            if "system" in metrics:
                if metrics["system"]["cpu_usage"] > self.thresholds["cpu_usage"]:
                    system_health = "warning"
                if metrics["system"]["memory_usage"] > self.thresholds["memory_usage"]:
                    system_health = "warning"
                if metrics["system"]["disk_usage"] > self.thresholds["disk_usage"]:
                    system_health = "critical"
            
            # Check MIRAGE health
            mirage_health = "healthy"
            if "mirage" in metrics and "health" in metrics["mirage"]:
                mirage_health = metrics["mirage"]["health"]["overall"]
            
            # Overall health
            overall_health = "healthy"
            if system_health == "critical" or mirage_health == "unhealthy":
                overall_health = "critical"
            elif system_health == "warning" or mirage_health == "warning":
                overall_health = "warning"
            
            self.health_status = {
                "timestamp": datetime.now().isoformat(),
                "overall": overall_health,
                "system": system_health,
                "mirage": mirage_health,
                "details": {
                    "cpu_usage": metrics.get("system", {}).get("cpu_usage", 0),
                    "memory_usage": metrics.get("system", {}).get("memory_usage", 0),
                    "disk_usage": metrics.get("system", {}).get("disk_usage", 0)
                }
            }
            
        except Exception as e:
            logger.error("Error updating health status", error=str(e))
            self.health_status = {
                "timestamp": datetime.now().isoformat(),
                "overall": "unknown",
                "error": str(e)
            }
    
    def _check_performance_thresholds(self, metrics: Dict[str, Any]):
        """Check performance thresholds and generate alerts."""
        try:
            alerts = []
            
            if "system" in metrics:
                # CPU threshold
                if metrics["system"]["cpu_usage"] > self.thresholds["cpu_usage"]:
                    alerts.append({
                        "type": "cpu_usage",
                        "level": "warning",
                        "value": metrics["system"]["cpu_usage"],
                        "threshold": self.thresholds["cpu_usage"],
                        "message": f"CPU usage is {metrics['system']['cpu_usage']:.1f}% (threshold: {self.thresholds['cpu_usage']}%)"
                    })
                
                # Memory threshold
                if metrics["system"]["memory_usage"] > self.thresholds["memory_usage"]:
                    alerts.append({
                        "type": "memory_usage",
                        "level": "warning",
                        "value": metrics["system"]["memory_usage"],
                        "threshold": self.thresholds["memory_usage"],
                        "message": f"Memory usage is {metrics['system']['memory_usage']:.1f}% (threshold: {self.thresholds['memory_usage']}%)"
                    })
                
                # Disk threshold
                if metrics["system"]["disk_usage"] > self.thresholds["disk_usage"]:
                    alerts.append({
                        "type": "disk_usage",
                        "level": "critical",
                        "value": metrics["system"]["disk_usage"],
                        "threshold": self.thresholds["disk_usage"],
                        "message": f"Disk usage is {metrics['system']['disk_usage']:.1f}% (threshold: {self.thresholds['disk_usage']}%)"
                    })
            
            # Log alerts
            for alert in alerts:
                logger.warning("Performance threshold exceeded", **alert)
                
        except Exception as e:
            logger.error("Error checking performance thresholds", error=str(e))
    
    def _store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics in history."""
        self.metrics_history.append(metrics)
        
        # Keep only last 1000 entries
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            "timestamp": datetime.now().isoformat(),
            "monitoring": {
                "active": self.is_monitoring,
                "interval": self.monitoring_interval,
                "metrics_count": len(self.metrics_history)
            },
            "health": self.health_status,
            "performance": self._calculate_performance_metrics(),
            "errors": len(self.error_logs)
        }
    
    def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics history for specified hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            m for m in self.metrics_history
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary."""
        return {
            "timestamp": datetime.now().isoformat(),
            "health": self.health_status,
            "uptime": self._get_uptime(),
            "component_status": self._get_component_health(),
            "recent_errors": len([
                e for e in self.error_logs
                if datetime.fromisoformat(e["timestamp"]) > datetime.now() - timedelta(hours=1)
            ])
        }
    
    def _get_uptime(self) -> str:
        """Get system uptime."""
        try:
            uptime_seconds = time.time() - psutil.boot_time()
            uptime = timedelta(seconds=uptime_seconds)
            return str(uptime)
        except Exception:
            return "unknown"
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        try:
            if format == "json":
                return json.dumps({
                    "timestamp": datetime.now().isoformat(),
                    "metrics_history": self.metrics_history,
                    "health_status": self.health_status,
                    "performance_stats": self.performance_stats,
                    "error_logs": self.error_logs
                }, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error("Error exporting metrics", error=str(e))
            return json.dumps({"error": str(e)})
    
    def clear_metrics(self):
        """Clear all metrics data."""
        self.metrics_history.clear()
        self.health_status.clear()
        self.performance_stats.clear()
        self.error_logs.clear()
        logger.info("All metrics data cleared")
    
    def set_thresholds(self, thresholds: Dict[str, float]):
        """Update performance thresholds."""
        self.thresholds.update(thresholds)
        logger.info("Performance thresholds updated", thresholds=thresholds)
    
    def get_thresholds(self) -> Dict[str, float]:
        """Get current performance thresholds."""
        return self.thresholds.copy()
