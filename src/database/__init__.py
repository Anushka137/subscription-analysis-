"""
Database layer for the subscription analytics platform.
"""

from .connection import get_db_manager, DatabaseConnectionManager

__all__ = ['get_db_manager', 'DatabaseConnectionManager'] 