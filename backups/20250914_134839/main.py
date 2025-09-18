#!/usr/bin/env python3
"""
MIRAGE v2 - Main Application Entry Point

This is the main entry point for the MIRAGE v2 application.
It initializes all components and starts the services.
"""

import os
import sys
import asyncio
import signal
import threading
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

import structlog
from orchestrator.orchestrator import Orchestrator
from monitoring.dashboard import DashboardServer
from api.web_api import create_web_api
from cli.main import cli

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


class MIRAGEApplication:
    """Main MIRAGE v2 application class."""
    
    def __init__(self):
        """Initialize the MIRAGE application."""
        self.orchestrator: Optional[Orchestrator] = None
        self.dashboard: Optional[DashboardServer] = None
        self.web_api: Optional[Any] = None
        self.running = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info("Received shutdown signal", signal=signum)
        self.shutdown()
    
    def initialize(self):
        """Initialize all MIRAGE components."""
        try:
            logger.info("Initializing MIRAGE v2 application...")
            
            # Get API key
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.error("GEMINI_API_KEY not found in environment variables")
                sys.exit(1)
            
            # Initialize orchestrator
            logger.info("Initializing orchestrator...")
            self.orchestrator = Orchestrator(api_key=api_key)
            
            # Initialize dashboard
            logger.info("Initializing dashboard...")
            dashboard_host = os.getenv("DASHBOARD_HOST", "127.0.0.1")
            dashboard_port = int(os.getenv("DASHBOARD_PORT", "8080"))
            self.dashboard = DashboardServer(
                api_key=api_key,
                host=dashboard_host,
                port=dashboard_port
            )
            
            # Initialize web API
            logger.info("Initializing web API...")
            self.web_api = create_web_api(api_key)
            
            logger.info("MIRAGE v2 application initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize MIRAGE application", error=str(e))
            sys.exit(1)
    
    def start(self):
        """Start all MIRAGE services."""
        try:
            logger.info("Starting MIRAGE v2 services...")
            
            # Start dashboard in a separate thread
            if self.dashboard:
                dashboard_thread = threading.Thread(
                    target=self.dashboard.start,
                    daemon=True
                )
                dashboard_thread.start()
                logger.info("Dashboard started", 
                           host=self.dashboard.host, 
                           port=self.dashboard.port)
            
            self.running = True
            logger.info("MIRAGE v2 services started successfully")
            
            # Keep main thread alive
            while self.running:
                try:
                    # Check if orchestrator is healthy
                    if self.orchestrator:
                        health = self.orchestrator.get_system_stats()
                        if not health.get("success", False):
                            logger.warning("Orchestrator health check failed")
                    
                    # Sleep for a bit
                    threading.Event().wait(30)
                    
                except KeyboardInterrupt:
                    logger.info("Received keyboard interrupt")
                    break
                except Exception as e:
                    logger.error("Error in main loop", error=str(e))
                    threading.Event().wait(5)
            
        except Exception as e:
            logger.error("Failed to start MIRAGE services", error=str(e))
            sys.exit(1)
    
    def shutdown(self):
        """Shutdown all MIRAGE services."""
        try:
            logger.info("Shutting down MIRAGE v2 services...")
            
            self.running = False
            
            # Stop dashboard
            if self.dashboard:
                self.dashboard.stop()
                logger.info("Dashboard stopped")
            
            # Stop orchestrator monitoring
            if self.orchestrator and hasattr(self.orchestrator, 'stop_monitoring'):
                self.orchestrator.stop_monitoring()
                logger.info("Orchestrator monitoring stopped")
            
            logger.info("MIRAGE v2 services shutdown complete")
            
        except Exception as e:
            logger.error("Error during shutdown", error=str(e))


def main():
    """Main entry point."""
    try:
        # Check if running as CLI
        if len(sys.argv) > 1 and sys.argv[1] in ['query', 'health', 'monitor', 'config']:
            # Run CLI
            cli()
        else:
            # Run as service
            app = MIRAGEApplication()
            app.initialize()
            app.start()
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error("Application failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
