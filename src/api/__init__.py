"""
API layer for the subscription analytics platform.
"""

from .server import app, run_server
from .routes import router

__all__ = ['app', 'run_server', 'router'] 