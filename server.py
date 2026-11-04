"""Sekarungi PIMS - Production Application Server Entrypoint
Patches Streamlit's Tornado engine to support custom JSON health endpoints:
  - GET /health
  - GET /api/health
Alongside Streamlit built-ins:
  - GET /_stcore/health
  - GET /healthz

Ideal for Render web services and external uptime pingers (UptimeRobot, Better Stack, Cron-job.org).
"""

import os
import sys
from streamlit.web.cli import main
from backend.health import patch_tornado_health

# Patch Streamlit's Tornado server with health endpoints before server startup
patch_tornado_health()


if __name__ == "__main__":
    port = os.environ.get("PORT", "8501")
    # Forward options to Streamlit CLI
    sys.argv = [
        "streamlit",
        "run",
        "app.py",
        f"--server.port={port}",
        "--server.address=0.0.0.0",
        "--server.headless=true",
    ]
    sys.exit(main())
