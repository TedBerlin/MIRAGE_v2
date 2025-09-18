"""
Dashboard server for MIRAGE v2.

Provides web-based monitoring dashboard with real-time metrics and controls.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import structlog

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .monitor import SystemMonitor
from .metrics import MetricsCollector
from .alerts import AlertManager

logger = structlog.get_logger(__name__)


class DashboardServer:
    """Web-based monitoring dashboard for MIRAGE v2."""
    
    def __init__(self, api_key: str, host: str = "127.0.0.1", port: int = 8080):
        """
        Initialize dashboard server.
        
        Args:
            api_key: Gemini API key
            host: Server host
            port: Server port
        """
        self.api_key = api_key
        self.host = host
        self.port = port
        
        # Initialize components
        self.system_monitor = SystemMonitor(api_key)
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        
        # WebSocket connections
        self.active_connections: list[WebSocket] = []
        
        # Create FastAPI app
        self.app = FastAPI(
            title="MIRAGE v2 Dashboard",
            description="Real-time monitoring dashboard for MIRAGE v2",
            version="1.0.0"
        )
        
        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self._setup_routes()
        
        # Setup WebSocket
        self._setup_websocket()
    
    def _setup_routes(self):
        """Setup dashboard routes."""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard():
            """Serve main dashboard page."""
            return self._get_dashboard_html()
        
        @self.app.get("/api/status")
        async def get_status():
            """Get current system status."""
            try:
                status = self.system_monitor.get_current_status()
                return JSONResponse(content=status)
            except Exception as e:
                logger.error("Error getting status", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/health")
        async def get_health():
            """Get system health summary."""
            try:
                health = self.system_monitor.get_health_summary()
                return JSONResponse(content=health)
            except Exception as e:
                logger.error("Error getting health", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/metrics")
        async def get_metrics(hours: int = 24):
            """Get metrics data."""
            try:
                metrics = self.metrics_collector.get_performance_summary(hours)
                return JSONResponse(content=metrics)
            except Exception as e:
                logger.error("Error getting metrics", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/metrics/query")
        async def get_query_metrics(hours: int = 24):
            """Get query metrics."""
            try:
                metrics = self.metrics_collector.get_query_statistics(hours)
                return JSONResponse(content=metrics)
            except Exception as e:
                logger.error("Error getting query metrics", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/metrics/agents")
        async def get_agent_metrics(hours: int = 24):
            """Get agent metrics."""
            try:
                metrics = self.metrics_collector.get_agent_statistics(hours=hours)
                return JSONResponse(content=metrics)
            except Exception as e:
                logger.error("Error getting agent metrics", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/metrics/rag")
        async def get_rag_metrics(hours: int = 24):
            """Get RAG metrics."""
            try:
                metrics = self.metrics_collector.get_rag_statistics(hours)
                return JSONResponse(content=metrics)
            except Exception as e:
                logger.error("Error getting RAG metrics", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/metrics/system")
        async def get_system_metrics(hours: int = 24):
            """Get system metrics."""
            try:
                metrics = self.metrics_collector.get_system_statistics(hours)
                return JSONResponse(content=metrics)
            except Exception as e:
                logger.error("Error getting system metrics", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/metrics/errors")
        async def get_error_metrics(hours: int = 24):
            """Get error metrics."""
            try:
                metrics = self.metrics_collector.get_error_statistics(hours)
                return JSONResponse(content=metrics)
            except Exception as e:
                logger.error("Error getting error metrics", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/alerts")
        async def get_alerts():
            """Get active alerts."""
            try:
                alerts = self.alert_manager.get_active_alerts()
                return JSONResponse(content=alerts)
            except Exception as e:
                logger.error("Error getting alerts", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/alerts/{alert_id}/acknowledge")
        async def acknowledge_alert(alert_id: str):
            """Acknowledge an alert."""
            try:
                result = self.alert_manager.acknowledge_alert(alert_id)
                return JSONResponse(content=result)
            except Exception as e:
                logger.error("Error acknowledging alert", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/control/clear-metrics")
        async def clear_metrics():
            """Clear all metrics data."""
            try:
                self.metrics_collector.clear_metrics()
                self.system_monitor.clear_metrics()
                return JSONResponse(content={"success": True, "message": "Metrics cleared"})
            except Exception as e:
                logger.error("Error clearing metrics", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/control/export-metrics")
        async def export_metrics(format: str = "json"):
            """Export metrics data."""
            try:
                data = self.metrics_collector.export_metrics(format)
                return JSONResponse(content={"success": True, "data": data})
            except Exception as e:
                logger.error("Error exporting metrics", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
    
    def _setup_websocket(self):
        """Setup WebSocket for real-time updates."""
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates."""
            await websocket.accept()
            self.active_connections.append(websocket)
            
            try:
                while True:
                    # Send real-time updates
                    await self._send_realtime_update(websocket)
                    await asyncio.sleep(5)  # Update every 5 seconds
                    
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
            except Exception as e:
                logger.error("WebSocket error", error=str(e))
                if websocket in self.active_connections:
                    self.active_connections.remove(websocket)
    
    async def _send_realtime_update(self, websocket: WebSocket):
        """Send real-time update via WebSocket."""
        try:
            # Get current metrics
            metrics = self.metrics_collector.get_aggregated_metrics(window_minutes=1)
            status = self.system_monitor.get_current_status()
            alerts = self.alert_manager.get_active_alerts()
            
            update = {
                "timestamp": datetime.now().isoformat(),
                "type": "realtime_update",
                "metrics": metrics,
                "status": status,
                "alerts": alerts
            }
            
            await websocket.send_text(json.dumps(update))
            
        except Exception as e:
            logger.error("Error sending realtime update", error=str(e))
    
    def _get_dashboard_html(self) -> str:
        """Get dashboard HTML content."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIRAGE v2 Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .card h3 {
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .metric-value {
            font-weight: bold;
            color: #667eea;
        }
        .status-healthy { color: #28a745; }
        .status-warning { color: #ffc107; }
        .status-critical { color: #dc3545; }
        .chart-container {
            position: relative;
            height: 300px;
            margin: 20px 0;
        }
        .controls {
            display: flex;
            gap: 10px;
            margin: 20px 0;
        }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        .btn-primary { background: #667eea; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-success { background: #28a745; color: white; }
        .alerts {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }
        .alert {
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
        }
        .alert-critical { border-left-color: #dc3545; }
        .alert-warning { border-left-color: #ffc107; }
        .alert-info { border-left-color: #17a2b8; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 MIRAGE v2 Dashboard</h1>
        <p>Real-time monitoring and control center</p>
        <div id="connection-status">Connecting...</div>
    </div>

    <div class="controls">
        <button class="btn btn-primary" onclick="refreshData()">🔄 Refresh</button>
        <button class="btn btn-success" onclick="exportMetrics()">📊 Export</button>
        <button class="btn btn-danger" onclick="clearMetrics()">🗑️ Clear</button>
    </div>

    <div class="dashboard-grid">
        <!-- System Status -->
        <div class="card">
            <h3>📊 System Status</h3>
            <div id="system-status">
                <div class="metric">
                    <span>Overall Health:</span>
                    <span class="metric-value" id="overall-health">Loading...</span>
                </div>
                <div class="metric">
                    <span>CPU Usage:</span>
                    <span class="metric-value" id="cpu-usage">Loading...</span>
                </div>
                <div class="metric">
                    <span>Memory Usage:</span>
                    <span class="metric-value" id="memory-usage">Loading...</span>
                </div>
                <div class="metric">
                    <span>Disk Usage:</span>
                    <span class="metric-value" id="disk-usage">Loading...</span>
                </div>
            </div>
        </div>

        <!-- Query Metrics -->
        <div class="card">
            <h3>🔍 Query Metrics</h3>
            <div id="query-metrics">
                <div class="metric">
                    <span>Total Queries:</span>
                    <span class="metric-value" id="total-queries">Loading...</span>
                </div>
                <div class="metric">
                    <span>Success Rate:</span>
                    <span class="metric-value" id="success-rate">Loading...</span>
                </div>
                <div class="metric">
                    <span>Avg Duration:</span>
                    <span class="metric-value" id="avg-duration">Loading...</span>
                </div>
                <div class="metric">
                    <span>Avg Iterations:</span>
                    <span class="metric-value" id="avg-iterations">Loading...</span>
                </div>
            </div>
        </div>

        <!-- Agent Metrics -->
        <div class="card">
            <h3>🤖 Agent Metrics</h3>
            <div id="agent-metrics">
                <div class="metric">
                    <span>Generator:</span>
                    <span class="metric-value" id="generator-ops">Loading...</span>
                </div>
                <div class="metric">
                    <span>Verifier:</span>
                    <span class="metric-value" id="verifier-ops">Loading...</span>
                </div>
                <div class="metric">
                    <span>Reformer:</span>
                    <span class="metric-value" id="reformer-ops">Loading...</span>
                </div>
                <div class="metric">
                    <span>Translator:</span>
                    <span class="metric-value" id="translator-ops">Loading...</span>
                </div>
            </div>
        </div>

        <!-- RAG Metrics -->
        <div class="card">
            <h3>📚 RAG Metrics</h3>
            <div id="rag-metrics">
                <div class="metric">
                    <span>Total Operations:</span>
                    <span class="metric-value" id="rag-ops">Loading...</span>
                </div>
                <div class="metric">
                    <span>Success Rate:</span>
                    <span class="metric-value" id="rag-success">Loading...</span>
                </div>
                <div class="metric">
                    <span>Documents Processed:</span>
                    <span class="metric-value" id="rag-docs">Loading...</span>
                </div>
                <div class="metric">
                    <span>Chunks Created:</span>
                    <span class="metric-value" id="rag-chunks">Loading...</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Performance Chart -->
    <div class="card">
        <h3>📈 Performance Trends</h3>
        <div class="chart-container">
            <canvas id="performance-chart"></canvas>
        </div>
    </div>

    <!-- Alerts -->
    <div class="card">
        <h3>🚨 Active Alerts</h3>
        <div id="alerts-container">
            <div class="alerts">
                <p>No active alerts</p>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let performanceChart = null;
        let chartData = {
            labels: [],
            datasets: [{
                label: 'CPU Usage (%)',
                data: [],
                borderColor: 'rgb(102, 126, 234)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.1
            }, {
                label: 'Memory Usage (%)',
                data: [],
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                tension: 0.1
            }]
        };

        // Initialize WebSocket connection
        function initWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                document.getElementById('connection-status').textContent = '🟢 Connected';
                document.getElementById('connection-status').style.color = '#28a745';
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            ws.onclose = function() {
                document.getElementById('connection-status').textContent = '🔴 Disconnected';
                document.getElementById('connection-status').style.color = '#dc3545';
                setTimeout(initWebSocket, 5000); // Reconnect after 5 seconds
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        }

        // Update dashboard with new data
        function updateDashboard(data) {
            if (data.type === 'realtime_update') {
                updateSystemStatus(data.status);
                updateMetrics(data.metrics);
                updateAlerts(data.alerts);
                updatePerformanceChart(data.metrics);
            }
        }

        // Update system status
        function updateSystemStatus(status) {
            if (status.health) {
                const health = status.health.overall;
                document.getElementById('overall-health').textContent = health;
                document.getElementById('overall-health').className = `metric-value status-${health}`;
            }
            
            if (status.performance) {
                document.getElementById('cpu-usage').textContent = 
                    status.performance.avg_cpu_usage ? status.performance.avg_cpu_usage.toFixed(1) + '%' : 'N/A';
                document.getElementById('memory-usage').textContent = 
                    status.performance.avg_memory_usage ? status.performance.avg_memory_usage.toFixed(1) + '%' : 'N/A';
            }
        }

        // Update metrics
        function updateMetrics(metrics) {
            if (metrics.queries) {
                document.getElementById('total-queries').textContent = metrics.queries.count || 0;
                document.getElementById('success-rate').textContent = 
                    metrics.queries.success_rate ? metrics.queries.success_rate.toFixed(1) + '%' : 'N/A';
                document.getElementById('avg-duration').textContent = 
                    metrics.queries.avg_duration ? metrics.queries.avg_duration.toFixed(2) + 's' : 'N/A';
            }
            
            if (metrics.agents) {
                document.getElementById('generator-ops').textContent = 
                    metrics.agents.GeneratorAgent ? metrics.agents.GeneratorAgent.count : 0;
                document.getElementById('verifier-ops').textContent = 
                    metrics.agents.VerifierAgent ? metrics.agents.VerifierAgent.count : 0;
                document.getElementById('reformer-ops').textContent = 
                    metrics.agents.ReformerAgent ? metrics.agents.ReformerAgent.count : 0;
                document.getElementById('translator-ops').textContent = 
                    metrics.agents.TranslatorAgent ? metrics.agents.TranslatorAgent.count : 0;
            }
        }

        // Update alerts
        function updateAlerts(alerts) {
            const container = document.getElementById('alerts-container');
            
            if (!alerts || alerts.length === 0) {
                container.innerHTML = '<div class="alerts"><p>No active alerts</p></div>';
                return;
            }
            
            let alertsHtml = '<div class="alerts">';
            alerts.forEach(alert => {
                alertsHtml += `
                    <div class="alert alert-${alert.severity}">
                        <strong>${alert.type}</strong>: ${alert.message}
                        <button onclick="acknowledgeAlert('${alert.id}')" style="float: right;">Acknowledge</button>
                    </div>
                `;
            });
            alertsHtml += '</div>';
            
            container.innerHTML = alertsHtml;
        }

        // Update performance chart
        function updatePerformanceChart(metrics) {
            if (!performanceChart) {
                const ctx = document.getElementById('performance-chart').getContext('2d');
                performanceChart = new Chart(ctx, {
                    type: 'line',
                    data: chartData,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        }
                    }
                });
            }
            
            const now = new Date().toLocaleTimeString();
            chartData.labels.push(now);
            chartData.datasets[0].data.push(metrics.queries?.avg_duration || 0);
            chartData.datasets[1].data.push(metrics.queries?.success_rate || 0);
            
            // Keep only last 20 data points
            if (chartData.labels.length > 20) {
                chartData.labels.shift();
                chartData.datasets[0].data.shift();
                chartData.datasets[1].data.shift();
            }
            
            performanceChart.update();
        }

        // Control functions
        function refreshData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => updateDashboard({type: 'realtime_update', status: data}))
                .catch(error => console.error('Error refreshing data:', error));
        }

        function exportMetrics() {
            fetch('/api/control/export-metrics')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const blob = new Blob([data.data], {type: 'application/json'});
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `mirage-metrics-${new Date().toISOString()}.json`;
                        a.click();
                        URL.revokeObjectURL(url);
                    }
                })
                .catch(error => console.error('Error exporting metrics:', error));
        }

        function clearMetrics() {
            if (confirm('Are you sure you want to clear all metrics data?')) {
                fetch('/api/control/clear-metrics', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('Metrics cleared successfully');
                            refreshData();
                        }
                    })
                    .catch(error => console.error('Error clearing metrics:', error));
            }
        }

        function acknowledgeAlert(alertId) {
            fetch(`/api/alerts/${alertId}/acknowledge`, {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        refreshData();
                    }
                })
                .catch(error => console.error('Error acknowledging alert:', error));
        }

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initWebSocket();
            refreshData();
        });
    </script>
</body>
</html>
        """
    
    def start(self):
        """Start the dashboard server."""
        logger.info("Starting MIRAGE v2 Dashboard", host=self.host, port=self.port)
        
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
    
    def stop(self):
        """Stop the dashboard server."""
        logger.info("Stopping MIRAGE v2 Dashboard")
        self.system_monitor.stop_monitoring()
        
        # Close WebSocket connections
        for connection in self.active_connections:
            try:
                connection.close()
            except Exception:
                pass
        
        self.active_connections.clear()
