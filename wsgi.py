"""
WSGI entry point for Cloud Run deployment
"""
import os
import logging
from api_server import app

# Configure logging for Cloud Run
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Ensure the application starts properly
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🚀 Starting WSGI server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
else:
    logger.info("📦 WSGI module imported successfully")
