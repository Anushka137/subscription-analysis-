"""
Database connection management with connection pooling and proper error handling.
"""

import logging
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import mysql.connector
from mysql.connector import Error, pooling
from mysql.connector.pooling import MySQLConnectionPool

from ..core.config import get_settings

logger = logging.getLogger(__name__)

class DatabaseConnectionManager:
    """Manages database connections with pooling and error handling."""
    
    def __init__(self):
        self.settings = get_settings()
        self.pool: Optional[MySQLConnectionPool] = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize the connection pool."""
        try:
            pool_config = {
                'pool_name': 'subscription_analytics_pool',
                'pool_size': 5,
                'host': self.settings.database.host,
                'port': self.settings.database.port,
                'database': self.settings.database.database,
                'user': self.settings.database.username,
                'password': self.settings.database.password,
                'charset': self.settings.database.charset,
                'autocommit': True,
                'connection_timeout': 10,
                'pool_reset_session': True
            }
            
            self.pool = mysql.connector.pooling.MySQLConnectionPool(**pool_config)
            logger.info("✅ Database connection pool initialized successfully")
            
        except Error as e:
            logger.error(f"❌ Failed to initialize database pool: {e}")
            self.pool = None
    
    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool."""
        connection = None
        try:
            if self.pool:
                connection = self.pool.get_connection()
                yield connection
            else:
                # Fallback to direct connection if pool is not available
                connection = mysql.connector.connect(
                    host=self.settings.database.host,
                    port=self.settings.database.port,
                    database=self.settings.database.database,
                    user=self.settings.database.username,
                    password=self.settings.database.password,
                    charset=self.settings.database.charset,
                    autocommit=True
                )
                yield connection
                
        except Error as e:
            logger.error(f"❌ Database connection error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> tuple[Optional[List[Dict]], Optional[str]]:
        """Execute a query and return results or error."""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, params)
                
                if query.strip().upper().startswith('SELECT'):
                    results = cursor.fetchall()
                    return results, None
                else:
                    connection.commit()
                    return None, None
                    
        except Error as e:
            error_msg = f"Database error: {e}"
            logger.error(error_msg)
            return None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logger.error(error_msg)
            return None, error_msg
    
    def test_connection(self) -> bool:
        """Test database connectivity."""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            return False

# Global database manager instance
db_manager = DatabaseConnectionManager()

def get_db_manager() -> DatabaseConnectionManager:
    """Get the global database manager instance."""
    return db_manager 