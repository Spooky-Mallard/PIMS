"""Health check endpoint and Tornado route handlers for PIMS.
Sekarungi Pharmaceuticals Ltd
Makerere University - BCS 2206 Database Management Systems

Provides:
  - HealthApiHandler: Tornado RequestHandler returning JSON status and Neon PostgreSQL connectivity
  - patch_tornado_health(): Monkeypatches Streamlit's Server._create_app so that:
      * GET /health
      * GET /api/health
    are routed directly to return JSON status.
  - setup_health_routes(): Injects routes into existing running Tornado web applications.
"""

import gc
import json
import os
import tornado.web
import tornado.routing
from backend.db import test_connection


class HealthApiHandler(tornado.web.RequestHandler):
    """Custom HTTP handler returning JSON system and database status."""

    def get(self):
        self.set_header("Content-Type", "application/json")
        try:
            db_ok, db_info = test_connection()
        except Exception as e:
            db_ok, db_info = False, {"error": str(e)}

        response = {
            "status": "healthy" if db_ok else "degraded",
            "service": "Sekarungi PIMS",
            "database": {
                "connected": db_ok,
                "engine": db_info.get("database", "neondb") if db_ok else "disconnected",
                "host": db_info.get("host", "neon.tech") if db_ok else "unknown",
            },
        }
        status_code = 200 if db_ok else 503
        self.set_status(status_code)
        self.finish(json.dumps(response, indent=2))


def patch_tornado_health():
    """Patches Streamlit's Server._create_app to prepend /health and /api/health routes."""
    import streamlit.web.server.server as server_module

    if getattr(server_module.Server, "_health_patched", False):
        return

    orig_create_app = server_module.Server._create_app

    def patched_create_app(self):
        app = orig_create_app(self)
        app.wildcard_router.rules.insert(
            0,
            tornado.routing.Rule(
                tornado.routing.PathMatches(r"/health"), HealthApiHandler
            ),
        )
        app.wildcard_router.rules.insert(
            0,
            tornado.routing.Rule(
                tornado.routing.PathMatches(r"/api/health"), HealthApiHandler
            ),
        )
        return app

    server_module.Server._create_app = patched_create_app
    server_module.Server._health_patched = True


def setup_health_routes():
    """Dynamically finds any active Tornado Application and attaches health handlers if missing."""
    patch_tornado_health()
    apps = [obj for obj in gc.get_objects() if isinstance(obj, tornado.web.Application)]
    for app in apps:
        existing = [
            rule
            for rule in app.wildcard_router.rules
            if hasattr(rule, "matcher")
            and hasattr(rule.matcher, "regex")
            and "/api/health" in rule.matcher.regex.pattern
        ]
        if not existing:
            app.wildcard_router.rules.insert(
                0,
                tornado.routing.Rule(
                    tornado.routing.PathMatches(r"/health"), HealthApiHandler
                ),
            )
            app.wildcard_router.rules.insert(
                0,
                tornado.routing.Rule(
                    tornado.routing.PathMatches(r"/api/health"), HealthApiHandler
                ),
            )
