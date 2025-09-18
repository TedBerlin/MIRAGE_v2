"""
Metrics collection for MIRAGE v2.

Provides detailed metrics collection and analysis for system performance.
"""

import time
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import structlog

logger = structlog.get_logger(__name__)


class MetricsCollector:
    """Advanced metrics collector for MIRAGE v2."""
    
    def __init__(self, max_history: int = 10000):
        """
        Initialize metrics collector.
        
        Args:
            max_history: Maximum number of metrics to keep in history
        """
        self.max_history = max_history
        self.metrics_lock = threading.Lock()
        
        # Metrics storage
        self.query_metrics = deque(maxlen=max_history)
        self.agent_metrics = defaultdict(lambda: deque(maxlen=max_history))
        self.rag_metrics = deque(maxlen=max_history)
        self.system_metrics = deque(maxlen=max_history)
        self.error_metrics = deque(maxlen=max_history)
        
        # Performance counters
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)
        self.gauges = defaultdict(float)
        
        # Aggregation windows
        self.aggregation_windows = [1, 5, 15, 60]  # minutes
    
    def record_query_metric(self, query_id: str, query: str, duration: float, 
                           success: bool, iteration: int, consensus: str):
        """Record query processing metric."""
        with self.metrics_lock:
            metric = {
                "timestamp": datetime.now().isoformat(),
                "type": "query",
                "query_id": query_id,
                "query_length": len(query),
                "duration": duration,
                "success": success,
                "iteration": iteration,
                "consensus": consensus,
                "query_hash": hash(query)
            }
            
            self.query_metrics.append(metric)
            self._update_counters("query", success)
            self._update_timers("query_duration", duration)
    
    def record_agent_metric(self, agent_name: str, operation: str, duration: float, 
                           success: bool, input_size: int, output_size: int):
        """Record agent operation metric."""
        with self.metrics_lock:
            metric = {
                "timestamp": datetime.now().isoformat(),
                "type": "agent",
                "agent_name": agent_name,
                "operation": operation,
                "duration": duration,
                "success": success,
                "input_size": input_size,
                "output_size": output_size
            }
            
            self.agent_metrics[agent_name].append(metric)
            self._update_counters(f"agent_{agent_name}", success)
            self._update_timers(f"agent_{agent_name}_duration", duration)
    
    def record_rag_metric(self, operation: str, duration: float, success: bool,
                         documents_processed: int, chunks_created: int):
        """Record RAG operation metric."""
        with self.metrics_lock:
            metric = {
                "timestamp": datetime.now().isoformat(),
                "type": "rag",
                "operation": operation,
                "duration": duration,
                "success": success,
                "documents_processed": documents_processed,
                "chunks_created": chunks_created
            }
            
            self.rag_metrics.append(metric)
            self._update_counters("rag", success)
            self._update_timers("rag_duration", duration)
    
    def record_system_metric(self, metric_name: str, value: float, unit: str = ""):
        """Record system metric."""
        with self.metrics_lock:
            metric = {
                "timestamp": datetime.now().isoformat(),
                "type": "system",
                "metric_name": metric_name,
                "value": value,
                "unit": unit
            }
            
            self.system_metrics.append(metric)
            self.gauges[metric_name] = value
    
    def record_error_metric(self, error_type: str, error_message: str, 
                           component: str, severity: str = "error"):
        """Record error metric."""
        with self.metrics_lock:
            metric = {
                "timestamp": datetime.now().isoformat(),
                "type": "error",
                "error_type": error_type,
                "error_message": error_message,
                "component": component,
                "severity": severity
            }
            
            self.error_metrics.append(metric)
            self._update_counters("error", True)
            self._update_counters(f"error_{error_type}", True)
    
    def _update_counters(self, name: str, increment: bool = True):
        """Update counter metric."""
        if increment:
            self.counters[name] += 1
        else:
            self.counters[name] = max(0, self.counters[name] - 1)
    
    def _update_timers(self, name: str, value: float):
        """Update timer metric."""
        self.timers[name].append(value)
        
        # Keep only recent values (last 1000)
        if len(self.timers[name]) > 1000:
            self.timers[name] = self.timers[name][-1000:]
    
    def get_query_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get query processing statistics."""
        with self.metrics_lock:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_queries = [
                q for q in self.query_metrics
                if datetime.fromisoformat(q["timestamp"]) > cutoff_time
            ]
            
            if not recent_queries:
                return {"total_queries": 0}
            
            # Calculate statistics
            total_queries = len(recent_queries)
            successful_queries = sum(1 for q in recent_queries if q["success"])
            failed_queries = total_queries - successful_queries
            
            durations = [q["duration"] for q in recent_queries]
            avg_duration = sum(durations) / len(durations) if durations else 0
            max_duration = max(durations) if durations else 0
            min_duration = min(durations) if durations else 0
            
            iterations = [q["iteration"] for q in recent_queries]
            avg_iterations = sum(iterations) / len(iterations) if iterations else 0
            
            consensus_counts = defaultdict(int)
            for q in recent_queries:
                consensus_counts[q["consensus"]] += 1
            
            return {
                "total_queries": total_queries,
                "successful_queries": successful_queries,
                "failed_queries": failed_queries,
                "success_rate": (successful_queries / total_queries) * 100 if total_queries > 0 else 0,
                "avg_duration": avg_duration,
                "max_duration": max_duration,
                "min_duration": min_duration,
                "avg_iterations": avg_iterations,
                "consensus_distribution": dict(consensus_counts),
                "time_range": {
                    "start": min(q["timestamp"] for q in recent_queries),
                    "end": max(q["timestamp"] for q in recent_queries)
                }
            }
    
    def get_agent_statistics(self, agent_name: Optional[str] = None, 
                           hours: int = 24) -> Dict[str, Any]:
        """Get agent performance statistics."""
        with self.metrics_lock:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            if agent_name:
                agents_to_check = [agent_name]
            else:
                agents_to_check = list(self.agent_metrics.keys())
            
            statistics = {}
            
            for agent in agents_to_check:
                if agent not in self.agent_metrics:
                    continue
                
                recent_metrics = [
                    m for m in self.agent_metrics[agent]
                    if datetime.fromisoformat(m["timestamp"]) > cutoff_time
                ]
                
                if not recent_metrics:
                    statistics[agent] = {"total_operations": 0}
                    continue
                
                # Calculate statistics for this agent
                total_ops = len(recent_metrics)
                successful_ops = sum(1 for m in recent_metrics if m["success"])
                failed_ops = total_ops - successful_ops
                
                durations = [m["duration"] for m in recent_metrics]
                avg_duration = sum(durations) / len(durations) if durations else 0
                max_duration = max(durations) if durations else 0
                
                input_sizes = [m["input_size"] for m in recent_metrics]
                output_sizes = [m["output_size"] for m in recent_metrics]
                
                statistics[agent] = {
                    "total_operations": total_ops,
                    "successful_operations": successful_ops,
                    "failed_operations": failed_ops,
                    "success_rate": (successful_ops / total_ops) * 100 if total_ops > 0 else 0,
                    "avg_duration": avg_duration,
                    "max_duration": max_duration,
                    "avg_input_size": sum(input_sizes) / len(input_sizes) if input_sizes else 0,
                    "avg_output_size": sum(output_sizes) / len(output_sizes) if output_sizes else 0,
                    "operations": list(set(m["operation"] for m in recent_metrics))
                }
            
            return statistics
    
    def get_rag_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get RAG system statistics."""
        with self.metrics_lock:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [
                m for m in self.rag_metrics
                if datetime.fromisoformat(m["timestamp"]) > cutoff_time
            ]
            
            if not recent_metrics:
                return {"total_operations": 0}
            
            # Calculate statistics
            total_ops = len(recent_metrics)
            successful_ops = sum(1 for m in recent_metrics if m["success"])
            failed_ops = total_ops - successful_ops
            
            durations = [m["duration"] for m in recent_metrics]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            total_docs = sum(m["documents_processed"] for m in recent_metrics)
            total_chunks = sum(m["chunks_created"] for m in recent_metrics)
            
            operations = defaultdict(int)
            for m in recent_metrics:
                operations[m["operation"]] += 1
            
            return {
                "total_operations": total_ops,
                "successful_operations": successful_ops,
                "failed_operations": failed_ops,
                "success_rate": (successful_ops / total_ops) * 100 if total_ops > 0 else 0,
                "avg_duration": avg_duration,
                "total_documents_processed": total_docs,
                "total_chunks_created": total_chunks,
                "operation_distribution": dict(operations)
            }
    
    def get_system_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get system metrics statistics."""
        with self.metrics_lock:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [
                m for m in self.system_metrics
                if datetime.fromisoformat(m["timestamp"]) > cutoff_time
            ]
            
            if not recent_metrics:
                return {"total_metrics": 0}
            
            # Group by metric name
            metric_groups = defaultdict(list)
            for m in recent_metrics:
                metric_groups[m["metric_name"]].append(m["value"])
            
            statistics = {}
            for metric_name, values in metric_groups.items():
                statistics[metric_name] = {
                    "count": len(values),
                    "avg": sum(values) / len(values),
                    "max": max(values),
                    "min": min(values),
                    "current": self.gauges.get(metric_name, 0)
                }
            
            return statistics
    
    def get_error_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get error statistics."""
        with self.metrics_lock:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_errors = [
                e for e in self.error_metrics
                if datetime.fromisoformat(e["timestamp"]) > cutoff_time
            ]
            
            if not recent_errors:
                return {"total_errors": 0}
            
            # Calculate statistics
            total_errors = len(recent_errors)
            
            error_types = defaultdict(int)
            components = defaultdict(int)
            severities = defaultdict(int)
            
            for error in recent_errors:
                error_types[error["error_type"]] += 1
                components[error["component"]] += 1
                severities[error["severity"]] += 1
            
            return {
                "total_errors": total_errors,
                "error_types": dict(error_types),
                "components": dict(components),
                "severities": dict(severities),
                "recent_errors": recent_errors[-10:]  # Last 10 errors
            }
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        return {
            "timestamp": datetime.now().isoformat(),
            "time_range_hours": hours,
            "queries": self.get_query_statistics(hours),
            "agents": self.get_agent_statistics(hours=hours),
            "rag": self.get_rag_statistics(hours),
            "system": self.get_system_statistics(hours),
            "errors": self.get_error_statistics(hours),
            "counters": dict(self.counters),
            "gauges": dict(self.gauges)
        }
    
    def get_aggregated_metrics(self, window_minutes: int = 5) -> Dict[str, Any]:
        """Get aggregated metrics for specified time window."""
        with self.metrics_lock:
            cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
            
            # Aggregate query metrics
            recent_queries = [
                q for q in self.query_metrics
                if datetime.fromisoformat(q["timestamp"]) > cutoff_time
            ]
            
            # Aggregate agent metrics
            agent_aggregates = {}
            for agent_name, metrics in self.agent_metrics.items():
                recent_metrics = [
                    m for m in metrics
                    if datetime.fromisoformat(m["timestamp"]) > cutoff_time
                ]
                if recent_metrics:
                    agent_aggregates[agent_name] = {
                        "count": len(recent_metrics),
                        "avg_duration": sum(m["duration"] for m in recent_metrics) / len(recent_metrics),
                        "success_rate": (sum(1 for m in recent_metrics if m["success"]) / len(recent_metrics)) * 100
                    }
            
            return {
                "window_minutes": window_minutes,
                "timestamp": datetime.now().isoformat(),
                "queries": {
                    "count": len(recent_queries),
                    "success_rate": (sum(1 for q in recent_queries if q["success"]) / len(recent_queries)) * 100 if recent_queries else 0,
                    "avg_duration": sum(q["duration"] for q in recent_queries) / len(recent_queries) if recent_queries else 0
                },
                "agents": agent_aggregates,
                "counters": dict(self.counters),
                "gauges": dict(self.gauges)
            }
    
    def clear_metrics(self):
        """Clear all metrics data."""
        with self.metrics_lock:
            self.query_metrics.clear()
            self.agent_metrics.clear()
            self.rag_metrics.clear()
            self.system_metrics.clear()
            self.error_metrics.clear()
            self.counters.clear()
            self.timers.clear()
            self.gauges.clear()
        
        logger.info("All metrics data cleared")
    
    def export_metrics(self, format: str = "json") -> str:
        """Export all metrics in specified format."""
        import json
        
        with self.metrics_lock:
            data = {
                "timestamp": datetime.now().isoformat(),
                "query_metrics": list(self.query_metrics),
                "agent_metrics": {k: list(v) for k, v in self.agent_metrics.items()},
                "rag_metrics": list(self.rag_metrics),
                "system_metrics": list(self.system_metrics),
                "error_metrics": list(self.error_metrics),
                "counters": dict(self.counters),
                "gauges": dict(self.gauges)
            }
            
            if format == "json":
                return json.dumps(data, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
