"""
Production startup script with proper initialization
Handles graceful startup, shutdown, and signal management
"""

import os
import sys
import signal
import logging
from app import app, config, logger, initialize_components

def handle_sigterm(signum, frame):
    """Handle SIGTERM signal for graceful shutdown"""
    logger.warning("SIGTERM signal received. Initiating graceful shutdown...")
    sys.exit(0)

def handle_sigint(signum, frame):
    """Handle SIGINT signal (Ctrl+C) for graceful shutdown"""
    logger.warning("SIGINT signal received. Initiating graceful shutdown...")
    sys.exit(0)

def run_production():
    """Run application in production mode with gunicorn"""
    logger.info(f"Starting {config.APP_NAME} in production mode")
    logger.info(f"Binding to {config.HOST}:{config.PORT}")
    
    # Use gunicorn command
    os.system(f"""
        gunicorn \
            --workers {config.MAX_WORKERS} \
            --worker-class sync \
            --bind {config.HOST}:{config.PORT} \
            --timeout {config.REQUEST_TIMEOUT} \
            --access-logfile - \
            --error-logfile - \
            --log-level {config.LOG_LEVEL.lower()} \
            app:app
    """)

def run_development():
    """Run application in development mode"""
    logger.info(f"Starting {config.APP_NAME} in development mode")
    logger.info(f"Debug mode: {config.DEBUG}")
    logger.info(f"Binding to http://{config.HOST}:{config.PORT}")
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigint)
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        threaded=True,
        use_reloader=False
    )

def main():
    """Main entry point"""
    logger.info("="*60)
    logger.info(f"Application: {config.APP_NAME}")
    logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    logger.info(f"Log Level: {config.LOG_LEVEL}")
    logger.info("="*60)
    
    # Run in appropriate mode
    if config.DEBUG:
        run_development()
    else:
        run_production()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
