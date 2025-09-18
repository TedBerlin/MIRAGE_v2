"""
Alert management for MIRAGE v2.

Provides comprehensive alerting system for system monitoring and notifications.
"""

import os
import sys
import time
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class Alert:
    """Alert representation."""
    
    def __init__(self, alert_id: str, alert_type: str, message: str, 
                 severity: AlertSeverity, component: str, 
                 threshold: Optional[float] = None, current_value: Optional[float] = None):
        """
        Initialize alert.
        
        Args:
            alert_id: Unique alert identifier
            alert_type: Type of alert
            message: Alert message
            severity: Alert severity
            component: Component that generated the alert
            threshold: Threshold value that triggered the alert
            current_value: Current value that exceeded threshold
        """
        self.alert_id = alert_id
        self.alert_type = alert_type
        self.message = message
        self.severity = severity
        self.component = component
        self.threshold = threshold
        self.current_value = current_value
        self.status = AlertStatus.ACTIVE
        self.created_at = datetime.now()
        self.acknowledged_at = None
        self.acknowledged_by = None
        self.resolved_at = None
        self.resolution_notes = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "id": self.alert_id,
            "type": self.alert_type,
            "message": self.message,
            "severity": self.severity.value,
            "component": self.component,
            "threshold": self.threshold,
            "current_value": self.current_value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "acknowledged_by": self.acknowledged_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution_notes": self.resolution_notes
        }
    
    def acknowledge(self, acknowledged_by: str = "system"):
        """Acknowledge the alert."""
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_at = datetime.now()
        self.acknowledged_by = acknowledged_by
    
    def resolve(self, resolution_notes: str = ""):
        """Resolve the alert."""
        self.status = AlertStatus.RESOLVED
        self.resolved_at = datetime.now()
        self.resolution_notes = resolution_notes


class AlertManager:
    """Alert management system for MIRAGE v2."""
    
    def __init__(self, max_alerts: int = 1000):
        """
        Initialize alert manager.
        
        Args:
            max_alerts: Maximum number of alerts to keep in memory
        """
        self.max_alerts = max_alerts
        self.alerts: Dict[str, Alert] = {}
        self.alert_lock = threading.Lock()
        
        # Alert rules
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        
        # Notification callbacks
        self.notification_callbacks: List[Callable] = []
        
        # Alert suppression
        self.suppressed_alerts: Dict[str, datetime] = {}
        self.suppression_duration = timedelta(minutes=5)
        
        # Initialize default alert rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default alert rules."""
        self.alert_rules = {
            "cpu_usage": {
                "threshold": 80.0,
                "severity": AlertSeverity.WARNING,
                "message_template": "CPU usage is {current_value:.1f}% (threshold: {threshold}%)"
            },
            "memory_usage": {
                "threshold": 85.0,
                "severity": AlertSeverity.WARNING,
                "message_template": "Memory usage is {current_value:.1f}% (threshold: {threshold}%)"
            },
            "disk_usage": {
                "threshold": 90.0,
                "severity": AlertSeverity.CRITICAL,
                "message_template": "Disk usage is {current_value:.1f}% (threshold: {threshold}%)"
            },
            "response_time": {
                "threshold": 5.0,
                "severity": AlertSeverity.WARNING,
                "message_template": "Response time is {current_value:.2f}s (threshold: {threshold}s)"
            },
            "error_rate": {
                "threshold": 5.0,
                "severity": AlertSeverity.WARNING,
                "message_template": "Error rate is {current_value:.1f}% (threshold: {threshold}%)"
            },
            "query_failure": {
                "threshold": 1.0,
                "severity": AlertSeverity.WARNING,
                "message_template": "Query processing failed: {message}"
            },
            "agent_failure": {
                "threshold": 1.0,
                "severity": AlertSeverity.WARNING,
                "message_template": "Agent {component} failed: {message}"
            },
            "rag_failure": {
                "threshold": 1.0,
                "severity": AlertSeverity.WARNING,
                "message_template": "RAG operation failed: {message}"
            }
        }
    
    def add_alert_rule(self, rule_name: str, threshold: float, severity: AlertSeverity, 
                      message_template: str):
        """Add a new alert rule."""
        self.alert_rules[rule_name] = {
            "threshold": threshold,
            "severity": severity,
            "message_template": message_template
        }
        logger.info("Alert rule added", rule=rule_name, threshold=threshold, severity=severity.value)
    
    def remove_alert_rule(self, rule_name: str):
        """Remove an alert rule."""
        if rule_name in self.alert_rules:
            del self.alert_rules[rule_name]
            logger.info("Alert rule removed", rule=rule_name)
    
    def check_threshold(self, metric_name: str, current_value: float, 
                       component: str = "system") -> Optional[Alert]:
        """Check if a metric exceeds its threshold and create alert if needed."""
        if metric_name not in self.alert_rules:
            return None
        
        rule = self.alert_rules[metric_name]
        threshold = rule["threshold"]
        
        if current_value <= threshold:
            return None
        
        # Check if alert is suppressed
        suppression_key = f"{metric_name}_{component}"
        if suppression_key in self.suppressed_alerts:
            if datetime.now() - self.suppressed_alerts[suppression_key] < self.suppression_duration:
                return None
            else:
                # Remove expired suppression
                del self.suppressed_alerts[suppression_key]
        
        # Create alert
        alert_id = f"{metric_name}_{component}_{int(time.time())}"
        message = rule["message_template"].format(
            current_value=current_value,
            threshold=threshold,
            component=component
        )
        
        alert = Alert(
            alert_id=alert_id,
            alert_type=metric_name,
            message=message,
            severity=rule["severity"],
            component=component,
            threshold=threshold,
            current_value=current_value
        )
        
        # Store alert
        with self.alert_lock:
            self.alerts[alert_id] = alert
            
            # Remove old alerts if we exceed max
            if len(self.alerts) > self.max_alerts:
                oldest_alert = min(self.alerts.values(), key=lambda a: a.created_at)
                del self.alerts[oldest_alert.alert_id]
        
        # Send notifications
        self._send_notifications(alert)
        
        # Suppress similar alerts
        self.suppressed_alerts[suppression_key] = datetime.now()
        
        logger.warning("Alert created", 
                      alert_id=alert_id, 
                      type=metric_name, 
                      severity=severity.value,
                      component=component)
        
        return alert
    
    def create_custom_alert(self, alert_type: str, message: str, severity: AlertSeverity,
                           component: str, **kwargs) -> Alert:
        """Create a custom alert."""
        alert_id = f"{alert_type}_{component}_{int(time.time())}"
        
        alert = Alert(
            alert_id=alert_id,
            alert_type=alert_type,
            message=message,
            severity=severity,
            component=component,
            **kwargs
        )
        
        # Store alert
        with self.alert_lock:
            self.alerts[alert_id] = alert
            
            # Remove old alerts if we exceed max
            if len(self.alerts) > self.max_alerts:
                oldest_alert = min(self.alerts.values(), key=lambda a: a.created_at)
                del self.alerts[oldest_alert.alert_id]
        
        # Send notifications
        self._send_notifications(alert)
        
        logger.warning("Custom alert created", 
                      alert_id=alert_id, 
                      type=alert_type, 
                      severity=severity.value,
                      component=component)
        
        return alert
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "user") -> bool:
        """Acknowledge an alert."""
        with self.alert_lock:
            if alert_id in self.alerts:
                self.alerts[alert_id].acknowledge(acknowledged_by)
                logger.info("Alert acknowledged", alert_id=alert_id, acknowledged_by=acknowledged_by)
                return True
            return False
    
    def resolve_alert(self, alert_id: str, resolution_notes: str = "") -> bool:
        """Resolve an alert."""
        with self.alert_lock:
            if alert_id in self.alerts:
                self.alerts[alert_id].resolve(resolution_notes)
                logger.info("Alert resolved", alert_id=alert_id, notes=resolution_notes)
                return True
            return False
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts."""
        with self.alert_lock:
            active_alerts = [
                alert.to_dict() for alert in self.alerts.values()
                if alert.status == AlertStatus.ACTIVE
            ]
            return sorted(active_alerts, key=lambda a: a["created_at"], reverse=True)
    
    def get_acknowledged_alerts(self) -> List[Dict[str, Any]]:
        """Get all acknowledged alerts."""
        with self.alert_lock:
            acknowledged_alerts = [
                alert.to_dict() for alert in self.alerts.values()
                if alert.status == AlertStatus.ACKNOWLEDGED
            ]
            return sorted(acknowledged_alerts, key=lambda a: a["acknowledged_at"], reverse=True)
    
    def get_resolved_alerts(self) -> List[Dict[str, Any]]:
        """Get all resolved alerts."""
        with self.alert_lock:
            resolved_alerts = [
                alert.to_dict() for alert in self.alerts.values()
                if alert.status == AlertStatus.RESOLVED
            ]
            return sorted(resolved_alerts, key=lambda a: a["resolved_at"], reverse=True)
    
    def get_all_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get all alerts from the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.alert_lock:
            recent_alerts = [
                alert.to_dict() for alert in self.alerts.values()
                if alert.created_at > cutoff_time
            ]
            return sorted(recent_alerts, key=lambda a: a["created_at"], reverse=True)
    
    def get_alert_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get alert statistics."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.alert_lock:
            recent_alerts = [
                alert for alert in self.alerts.values()
                if alert.created_at > cutoff_time
            ]
            
            if not recent_alerts:
                return {
                    "total_alerts": 0,
                    "active_alerts": 0,
                    "acknowledged_alerts": 0,
                    "resolved_alerts": 0,
                    "severity_distribution": {},
                    "component_distribution": {},
                    "type_distribution": {}
                }
            
            # Calculate statistics
            total_alerts = len(recent_alerts)
            active_alerts = sum(1 for a in recent_alerts if a.status == AlertStatus.ACTIVE)
            acknowledged_alerts = sum(1 for a in recent_alerts if a.status == AlertStatus.ACKNOWLEDGED)
            resolved_alerts = sum(1 for a in recent_alerts if a.status == AlertStatus.RESOLVED)
            
            # Severity distribution
            severity_dist = {}
            for alert in recent_alerts:
                severity = alert.severity.value
                severity_dist[severity] = severity_dist.get(severity, 0) + 1
            
            # Component distribution
            component_dist = {}
            for alert in recent_alerts:
                component = alert.component
                component_dist[component] = component_dist.get(component, 0) + 1
            
            # Type distribution
            type_dist = {}
            for alert in recent_alerts:
                alert_type = alert.alert_type
                type_dist[alert_type] = type_dist.get(alert_type, 0) + 1
            
            return {
                "total_alerts": total_alerts,
                "active_alerts": active_alerts,
                "acknowledged_alerts": acknowledged_alerts,
                "resolved_alerts": resolved_alerts,
                "severity_distribution": severity_dist,
                "component_distribution": component_dist,
                "type_distribution": type_dist,
                "time_range": {
                    "start": min(a.created_at for a in recent_alerts).isoformat(),
                    "end": max(a.created_at for a in recent_alerts).isoformat()
                }
            }
    
    def add_notification_callback(self, callback: Callable):
        """Add a notification callback."""
        self.notification_callbacks.append(callback)
        logger.info("Notification callback added")
    
    def remove_notification_callback(self, callback: Callable):
        """Remove a notification callback."""
        if callback in self.notification_callbacks:
            self.notification_callbacks.remove(callback)
            logger.info("Notification callback removed")
    
    def _send_notifications(self, alert: Alert):
        """Send notifications for an alert."""
        for callback in self.notification_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error("Error in notification callback", error=str(e))
    
    def clear_alerts(self, status: Optional[AlertStatus] = None):
        """Clear alerts by status."""
        with self.alert_lock:
            if status is None:
                # Clear all alerts
                self.alerts.clear()
                logger.info("All alerts cleared")
            else:
                # Clear alerts by status
                alerts_to_remove = [
                    alert_id for alert_id, alert in self.alerts.items()
                    if alert.status == status
                ]
                for alert_id in alerts_to_remove:
                    del self.alerts[alert_id]
                logger.info("Alerts cleared", status=status.value, count=len(alerts_to_remove))
    
    def export_alerts(self, format: str = "json") -> str:
        """Export alerts in specified format."""
        import json
        
        with self.alert_lock:
            alerts_data = {
                "timestamp": datetime.now().isoformat(),
                "alerts": [alert.to_dict() for alert in self.alerts.values()],
                "rules": self.alert_rules,
                "statistics": self.get_alert_statistics(24)
            }
            
            if format == "json":
                return json.dumps(alerts_data, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
    
    def get_alert_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get all alert rules."""
        return self.alert_rules.copy()
    
    def update_alert_rule(self, rule_name: str, **kwargs):
        """Update an alert rule."""
        if rule_name in self.alert_rules:
            self.alert_rules[rule_name].update(kwargs)
            logger.info("Alert rule updated", rule=rule_name, updates=kwargs)
        else:
            logger.warning("Alert rule not found", rule=rule_name)
