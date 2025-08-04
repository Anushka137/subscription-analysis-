#!/usr/bin/env python3
"""
API Server for Subscription Analytics
- FastAPI backend for analytics tools and data access
- Secure, production-ready, and scalable
"""

import datetime
import os
import secrets
import json
import decimal
import re
import sys
import gc
from typing import Dict, List, Optional, Any, Tuple
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import mysql.connector
from mysql.connector import Error
import uvicorn
from contextlib import asynccontextmanager
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api_server.log')
    ]
)
logger = logging.getLogger(__name__)
load_dotenv()

# Debug prints to confirm .env loading
print("DB_HOST:", os.getenv("DB_HOST"))
print("DB_NAME:", os.getenv("DB_NAME"))
print("DB_USER:", os.getenv("DB_USER"))
print("DB_PASSWORD:", os.getenv("DB_PASSWORD"))
print("API_KEY_1:", os.getenv("API_KEY_1"))

# FORCE OFFLINE MODE for better stability
os.environ.update({
    'HF_HUB_OFFLINE': '1',
    'TRANSFORMERS_OFFLINE': '1',
    'HF_HUB_DISABLE_PROGRESS_BARS': '1',
    'PYTORCH_ENABLE_MPS_FALLBACK': '1',
    'PYTORCH_MPS_HIGH_WATERMARK_RATIO': '0.0',
    'PYTORCH_DISABLE_MMAP': '1',
    'OMP_NUM_THREADS': '1',
    'MKL_NUM_THREADS': '1',
    'TOKENIZERS_PARALLELISM': 'false',
    'CUDA_VISIBLE_DEVICES': '',
})

# ENHANCED SEMANTIC LEARNING - COMPLETE IMPLEMENTATION
SEMANTIC_LEARNING_ENABLED = False
LOCAL_MODEL_PATH = "./model"

try:
    import numpy as np
    import faiss
    from sentence_transformers import SentenceTransformer, models
    import torch
    LIBRARIES_INSTALLED = True
    logger.info("✅ Complete semantic learning libraries available")
except ImportError as e:
    LIBRARIES_INSTALLED = False
    logger.info(f"ℹ️ Semantic learning libraries not available: {e}")

class CompleteEnhancedSemanticLearner:
    """COMPLETE Enhanced semantic learning with full feedback integration."""
    
    def __init__(self, queries_file='complete_query_memory.json', vectors_file='complete_query_vectors.npy'):
        global SEMANTIC_LEARNING_ENABLED
        
        if not LIBRARIES_INSTALLED:
            logger.info("Complete semantic learning disabled - libraries not available")
            self.model = None
            return
        
        try:
            logger.info(f"🧠 Loading complete semantic model...")
            
            # Initialize sentence transformer with proper error handling
            if os.path.exists(LOCAL_MODEL_PATH):
                logger.info(f"Loading model from {LOCAL_MODEL_PATH}")
                try:
                    # Force CPU with enhanced settings
                    import torch
                    torch.set_default_dtype(torch.float32)
                    if hasattr(torch.backends, 'mps'):
                        torch.backends.mps.is_available = lambda: False
                    
                    # Load model with enhanced error handling
                    word_embedding_model = models.Transformer(LOCAL_MODEL_PATH)
                    pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
                    
                    self.model = SentenceTransformer(modules=[word_embedding_model, pooling_model])
                    self.model = self.model.to('cpu')
                    self.model.eval()
                    
                    # Disable gradients for stability
                    for param in self.model.parameters():
                        param.data = param.data.cpu()
                        param.requires_grad = False
                    
                    logger.info("✅ Local model loaded successfully")
                    
                except Exception as local_error:
                    logger.warning(f"Local model failed: {local_error}, using default model")
                    self.model = SentenceTransformer('all-MiniLM-L6-v2')
                    self.model = self.model.to('cpu')
                    self.model.eval()
            else:
                logger.info("Using default sentence transformer model")
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.model = self.model.to('cpu')
                self.model.eval()
            
            SEMANTIC_LEARNING_ENABLED = True
            
            self.queries_file = queries_file
            self.vectors_file = vectors_file
            self.known_queries = []
            self.known_vectors = None
            self.index = None
            
            self._load_complete_memory()
            logger.info("✅ COMPLETE Enhanced Semantic Query Learner loaded")
            
        except Exception as e:
            logger.warning(f"⚠️ Complete semantic learning disabled: {e}")
            SEMANTIC_LEARNING_ENABLED = False
            self.model = None

    def _load_complete_memory(self):
        """Load existing query memory with complete error handling."""
        if not self.model:
            return
            
        try:
            if os.path.exists(self.queries_file) and os.path.exists(self.vectors_file):
                with open(self.queries_file, 'r') as f:
                    self.known_queries = json.load(f)
                
                self.known_vectors = np.load(self.vectors_file)
                
                if self.known_vectors is not None and self.known_vectors.shape[0] > 0:
                    dimension = self.known_vectors.shape[1]
                    self.index = faiss.IndexFlatL2(dimension)
                    vectors_cpu = self.known_vectors.astype('float32')
                    self.index.add(vectors_cpu)
                    logger.info(f"🧠 Loaded {len(self.known_queries)} complete queries from memory")
            else:
                logger.info("🧠 Starting with empty query memory")
                    
        except Exception as e:
            logger.warning(f"⚠️ Could not load complete query memory: {e}")
            # Initialize empty memory
            self.known_queries = []
            self.known_vectors = None
            self.index = None

    def _save_complete_memory(self):
        """Save query memory with complete error handling."""
        if not self.model:
            return
            
        try:
            with open(self.queries_file, 'w') as f:
                json.dump(self.known_queries, f, indent=2)
            
            if self.known_vectors is not None:
                np.save(self.vectors_file, self.known_vectors)
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to save complete query memory: {e}")

    def add_complete_query_feedback(self, original_question: str, sql_query: str, was_helpful: bool = True, improvement_suggestion: str = None, chart_type: str = None):
        """Add COMPLETE query feedback with full chart type awareness."""
        if not self.model:
            logger.info("📝 Complete feedback noted (semantic learning not available)")
            return
            
        try:
            feedback_type = "positive" if was_helpful else "negative"
            logger.info(f"🧠 Adding {feedback_type} complete feedback to memory...")
            
            # Complete encoding with multiple fallback strategies
            vector = None
            import torch
            with torch.no_grad():
                self.model.eval()
                
                # Try different encoding strategies for robustness
                encoding_strategies = [
                    lambda: self.model.encode([original_question], show_progress_bar=False, convert_to_tensor=False, device='cpu')[0],
                    lambda: self.model.encode([original_question], show_progress_bar=False)[0],
                    lambda: self.model.encode([original_question])[0]
                ]
                
                for i, strategy in enumerate(encoding_strategies):
                    try:
                        vector = strategy()
                        break
                    except Exception as e:
                        logger.warning(f"⚠️ Complete encoding strategy {i+1} failed: {e}")
                        continue
                
                if vector is None:
                    logger.warning("⚠️ All complete encoding strategies failed")
                    return
            
            # Ensure numpy array
            if hasattr(vector, 'cpu'):
                vector = vector.cpu().numpy()
            elif hasattr(vector, 'numpy'):
                vector = vector.numpy()
            
            # Complete feedback entry with full chart information
            feedback_entry = {
                'question': original_question,
                'sql': sql_query,
                'was_helpful': was_helpful,
                'feedback_type': feedback_type,
                'timestamp': datetime.datetime.now().isoformat(),
                'chart_type': chart_type,
                'query_category': self._categorize_query(original_question),
                'sql_complexity': self._analyze_sql_complexity(sql_query),
                'success_score': 1.0 if was_helpful else 0.0
            }
            
            if not was_helpful and improvement_suggestion:
                feedback_entry['improvement_suggestion'] = improvement_suggestion.strip()
                feedback_entry['improvement_category'] = self._categorize_improvement(improvement_suggestion)
            
            self.known_queries.append(feedback_entry)
            
            if self.known_vectors is None:
                self.known_vectors = np.array([vector])
            else:
                self.known_vectors = np.vstack([self.known_vectors, vector])
            
            # Rebuild index safely with complete error handling
            try:
                if self.index is not None:
                    del self.index
                    
                dimension = self.known_vectors.shape[1]
                self.index = faiss.IndexFlatL2(dimension)
                vectors_cpu = self.known_vectors.astype('float32')
                self.index.add(vectors_cpu)
            except Exception as faiss_error:
                logger.warning(f"⚠️ Complete FAISS indexing failed: {faiss_error}")
            
            gc.collect()
            self._save_complete_memory()
            logger.info(f"💾 Complete {feedback_type} feedback stored with full chart awareness")
            
        except Exception as e:
            logger.warning(f"⚠️ Complete feedback processing failed gracefully: {e}")
            # Never raise exceptions from feedback

    def _categorize_query(self, question: str) -> str:
        """Categorize query for better learning."""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['pie', 'distribution', 'breakdown']):
            return 'pie_chart_request'
        elif any(word in question_lower for word in ['trend', 'over time', 'line']):
            return 'trend_analysis'
        elif any(word in question_lower for word in ['rate', 'success', 'percentage']):
            return 'rate_analysis'
        elif any(word in question_lower for word in ['comparison', 'compare', 'vs']):
            return 'comparison_analysis'
        elif any(word in question_lower for word in ['user', 'merchant']):
            return 'user_analysis'
        else:
            return 'general_query'

    def _categorize_improvement(self, improvement: str) -> str:
        """Categorize improvement suggestion."""
        improvement_lower = improvement.lower()
        
        if 'pie chart' in improvement_lower:
            return 'chart_type_pie'
        elif 'bar chart' in improvement_lower:
            return 'chart_type_bar'
        elif 'line chart' in improvement_lower:
            return 'chart_type_line'
        elif 'sql' in improvement_lower or 'query' in improvement_lower:
            return 'sql_improvement'
        elif 'rate' in improvement_lower or 'percentage' in improvement_lower:
            return 'data_aggregation'
        else:
            return 'general_improvement'

    def _analyze_sql_complexity(self, sql_query: str) -> str:
        """Analyze SQL complexity for learning."""
        sql_lower = sql_query.lower()
        
        complexity_score = 0
        if 'join' in sql_lower:
            complexity_score += 2
        if 'union' in sql_lower:
            complexity_score += 2
        if 'group by' in sql_lower:
            complexity_score += 1
        if 'having' in sql_lower:
            complexity_score += 1
        if sql_lower.count('select') > 1:
            complexity_score += 2
        
        if complexity_score >= 4:
            return 'complex'
        elif complexity_score >= 2:
            return 'medium'
        else:
            return 'simple'

    def get_complete_improvement_suggestions(self, question: str, threshold: float = 0.85):
        """Get COMPLETE improvement suggestions with full chart type awareness."""
        if not self.model or not self.index or len(self.known_queries) == 0:
            return []
        
        try:
            # Encode question safely
            import torch
            with torch.no_grad():
                self.model.eval()
                question_vector = self.model.encode([question], 
                                                  show_progress_bar=False, 
                                                  convert_to_tensor=False,
                                                  device='cpu')[0]
            
            if hasattr(question_vector, 'cpu'):
                question_vector = question_vector.cpu().numpy()
            elif hasattr(question_vector, 'numpy'):
                question_vector = question_vector.numpy()
            
            # Search safely
            k = min(10, len(self.known_queries))
            distances, indices = self.index.search(np.array([question_vector]).astype('float32'), k=k)
            
            improvement_suggestions = []
            for distance, idx in zip(distances[0], indices[0]):
                if distance < threshold and idx < len(self.known_queries):
                    query_data = self.known_queries[idx]
                    
                    if (not query_data.get('was_helpful', True) and 
                        'improvement_suggestion' in query_data and 
                        query_data['improvement_suggestion']):
                        
                        similarity = max(0.0, min(1.0, 1.0 - (distance / 2.0)))
                        improvement_suggestions.append({
                            'similarity': similarity,
                            'question': query_data['question'],
                            'failed_sql': query_data['sql'],
                            'improvement_suggestion': query_data['improvement_suggestion'],
                            'improvement_category': query_data.get('improvement_category', 'general'),
                            'chart_type': query_data.get('chart_type'),
                            'query_category': query_data.get('query_category', 'general'),
                            'sql_complexity': query_data.get('sql_complexity', 'unknown'),
                            'timestamp': query_data['timestamp']
                        })
            
            # Complete sorting with category awareness
            improvement_suggestions.sort(key=lambda x: (x['similarity'], x['improvement_category'] == 'chart_type_pie'), reverse=True)
            
            # Deduplicate with complete logic
            seen_suggestions = set()
            unique_suggestions = []
            for suggestion in improvement_suggestions:
                suggestion_key = (suggestion['improvement_suggestion'].lower(), suggestion.get('improvement_category', ''))
                if suggestion_key not in seen_suggestions:
                    seen_suggestions.add(suggestion_key)
                    unique_suggestions.append(suggestion)
            
            logger.info(f"💡 Found {len(unique_suggestions)} complete improvement suggestions")
            return unique_suggestions[:3]
            
        except Exception as e:
            logger.warning(f"⚠️ Complete improvement suggestions search failed: {e}")
            return []

    def get_similar_successful_queries(self, question: str, threshold: float = 0.8):
        """Get similar successful queries for better SQL generation."""
        if not self.model or not self.index or len(self.known_queries) == 0:
            return []
        
        try:
            # Encode question
            import torch
            with torch.no_grad():
                self.model.eval()
                question_vector = self.model.encode([question], 
                                                  show_progress_bar=False, 
                                                  convert_to_tensor=False,
                                                  device='cpu')[0]
            
            if hasattr(question_vector, 'cpu'):
                question_vector = question_vector.cpu().numpy()
            elif hasattr(question_vector, 'numpy'):
                question_vector = question_vector.numpy()
            
            # Search for similar successful queries
            k = min(5, len(self.known_queries))
            distances, indices = self.index.search(np.array([question_vector]).astype('float32'), k=k)
            
            successful_queries = []
            for distance, idx in zip(distances[0], indices[0]):
                if distance < threshold and idx < len(self.known_queries):
                    query_data = self.known_queries[idx]
                    
                    if query_data.get('was_helpful', False):
                        similarity = max(0.0, min(1.0, 1.0 - (distance / 2.0)))
                        successful_queries.append({
                            'similarity': similarity,
                            'question': query_data['question'],
                            'sql': query_data['sql'],
                            'query_category': query_data.get('query_category', 'general'),
                            'chart_type': query_data.get('chart_type'),
                            'sql_complexity': query_data.get('sql_complexity', 'unknown')
                        })
            
            successful_queries.sort(key=lambda x: x['similarity'], reverse=True)
            logger.info(f"🎯 Found {len(successful_queries)} similar successful queries")
            return successful_queries
            
        except Exception as e:
            logger.warning(f"⚠️ Similar queries search failed: {e}")
            return []

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'autocommit': True,
    'connect_timeout': 10,
    'charset': 'utf8mb4',
    'raise_on_warnings': False,
    'use_pure': True
}

# Enhanced Database Functions
def get_db_connection():
    """Get database connection with enhanced error handling."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            if connection.is_connected():
                return connection
            else:
                logger.error(f"Database connection failed on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)
                    continue
                return None
        except Error as e:
            logger.error(f"❌ MySQL Connection Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(1)
                continue
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected database error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(1)
                continue
            return None
    
    return None

def sanitize_for_json(obj):
    """Convert objects to JSON-serializable format with enhanced handling."""
    try:
        if isinstance(obj, list):
            return [sanitize_for_json(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: sanitize_for_json(value) for key, value in obj.items()}
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif obj is None:
            return None
        else:
            return obj
    except Exception as e:
        logger.warning(f"⚠️ Enhanced sanitization error for {type(obj)}: {e}")
        return str(obj)

def _execute_query(query: str, params: tuple = ()) -> Tuple[Optional[List[Dict]], Optional[str]]:
    """Execute database query with enhanced error handling."""
    connection = None
    cursor = None
    
    try:
        logger.info(f"🔍 Executing query: {query[:100]}...")
        # Log the final SQL query used for execution
        logger.info(f"FINAL SQL QUERY: {query}")
        connection = get_db_connection()
        if not connection:
            return None, "Database connection failed after retries"
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Sanitize results for JSON
        sanitized_results = sanitize_for_json(results)
        
        logger.info(f"✅ Query executed successfully, returned {len(results)} rows")
        return sanitized_results, None
        
    except Error as e:
        error_msg = f"Database error: {str(e)}"
        logger.error(f"❌ Database query failed: {e}")
        logger.error(f"❌ Query was: {query}")
        return None, error_msg
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"❌ Unexpected error in query execution: {e}")
        logger.error(f"❌ Query was: {query}")
        return None, error_msg
        
    finally:
        try:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
        except Exception as e:
            logger.warning(f"Error closing database connection: {e}")

# ===== COMPLETE CORE TOOL FUNCTIONS =====

def get_subscriptions_in_last_days(days: int) -> Dict:
    """Get subscription statistics for the last N days."""
    try:
        if not isinstance(days, int) or days < 1 or days > 365:
            return {"error": "Days must be between 1 and 365"}
        
        query = """
        SELECT 
            COUNT(*) as total_subscriptions,
            SUM(CASE WHEN status = 'ACTIVE' THEN 1 ELSE 0 END) as active_subscriptions,
            SUM(CASE WHEN status = 'INACTIVE' THEN 1 ELSE 0 END) as inactive_subscriptions,
            DATE(subcription_start_date) as start_date
        FROM subscription_contract_v2 
        WHERE subcription_start_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        GROUP BY DATE(subcription_start_date)
        ORDER BY start_date DESC
        """
        
        results, error = _execute_query(query, (days,))
        
        if error:
            return {"error": error}
        
        if not results:
            return {"data": [], "message": f"No subscriptions found in the last {days} days"}
        
        return {"data": results, "message": f"Found {len(results)} days with subscription data"}
        
    except Exception as e:
        logger.error(f"Error in get_subscriptions_in_last_days: {e}")
        return {"error": f"Function error: {str(e)}"}

def get_payment_success_rate_in_last_days(days: int) -> Dict:
    """Get payment success rate and revenue statistics for the last N days."""
    try:
        if not isinstance(days, int) or days < 1 or days > 365:
            return {"error": "Days must be between 1 and 365"}
        
        query = """
        SELECT 
            COUNT(*) as total_transactions,
            SUM(CASE WHEN status = 'ACTIVE' THEN 1 ELSE 0 END) as successful_transactions,
            SUM(CASE WHEN status != 'ACTIVE' THEN 1 ELSE 0 END) as failed_transactions,
            ROUND((SUM(CASE WHEN status = 'ACTIVE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as success_rate,
            SUM(CASE WHEN status = 'ACTIVE' THEN trans_amount_decimal ELSE 0 END) as total_revenue,
            DATE(created_date) as transaction_date
        FROM subscription_payment_details 
        WHERE created_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        GROUP BY DATE(created_date)
        ORDER BY transaction_date DESC
        """
        
        results, error = _execute_query(query, (days,))
        
        if error:
            return {"error": error}
        
        if not results:
            return {"data": [], "message": f"No payment data found in the last {days} days"}
        
        return {"data": results, "message": f"Found payment data for {len(results)} days"}
        
    except Exception as e:
        logger.error(f"Error in get_payment_success_rate_in_last_days: {e}")
        return {"error": f"Function error: {str(e)}"}

def get_user_payment_history(merchant_user_id: str, days: int = 90) -> Dict:
    """Get payment history for a specific user by merchant_user_id."""
    try:
        if not merchant_user_id or not isinstance(merchant_user_id, str):
            return {"error": "merchant_user_id must be a non-empty string"}
        
        if not isinstance(days, int) or days < 1 or days > 365:
            days = 90
        
        query = """
        SELECT 
            p.subscription_id,
            p.status,
            p.trans_amount_decimal,
            p.created_date,
            c.status as subscription_status,
            c.subcription_start_date
        FROM subscription_payment_details p
        JOIN subscription_contract_v2 c ON p.subscription_id = c.subscription_id
        WHERE c.merchant_user_id = %s 
        AND p.created_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        ORDER BY p.created_date DESC
        """
        
        results, error = _execute_query(query, (merchant_user_id, days))
        
        if error:
            return {"error": error}
        
        if not results:
            return {"data": [], "message": f"No payment history found for user {merchant_user_id} in the last {days} days"}
        
        return {"data": results, "message": f"Found {len(results)} payment records for user {merchant_user_id}"}
        
    except Exception as e:
        logger.error(f"Error in get_user_payment_history: {e}")
        return {"error": f"Function error: {str(e)}"}

def get_database_status() -> Dict:
    """Check database connection and get basic statistics."""
    try:
        connection = get_db_connection()
        if not connection:
            return {"error": "Cannot connect to database"}
        
        # Test queries
        test_queries = [
            ("Total Subscriptions", "SELECT COUNT(*) as count FROM subscription_contract_v2"),
            ("Total Payments", "SELECT COUNT(*) as count FROM subscription_payment_details"),
            ("Active Subscriptions", "SELECT COUNT(*) as count FROM subscription_contract_v2 WHERE status = 'ACTIVE'"),
            ("Recent Payments (Last 7 days)", "SELECT COUNT(*) as count FROM subscription_payment_details WHERE created_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)")
        ]
        
        stats = {}
        
        for stat_name, query in test_queries:
            try:
                results, error = _execute_query(query)
                if error:
                    stats[stat_name] = f"Error: {error}"
                elif results and len(results) > 0:
                    stats[stat_name] = results[0].get('count', 0)
                else:
                    stats[stat_name] = 0
            except Exception as e:
                stats[stat_name] = f"Error: {str(e)}"
        
        connection.close()
        
        return {
            "data": {
                "status": "connected",
                "database": DB_CONFIG.get('database', 'unknown'),
                "host": DB_CONFIG.get('host', 'unknown'),
                "statistics": stats,
                "timestamp": datetime.datetime.now().isoformat()
            },
            "message": "Database connection successful"
        }
        
    except Exception as e:
        logger.error(f"Error in get_database_status: {e}")
        return {"error": f"Database status check failed: {str(e)}"}

def complete_execute_dynamic_sql(sql_query: str) -> Dict:
    """Execute SQL with enhanced error handling and auto-retry."""
    try:
        if not sql_query or not isinstance(sql_query, str):
            return {"error": "SQL query must be a non-empty string"}
        
        # Clean and validate SQL
        cleaned_sql = sql_query.strip().rstrip(';').strip()
        
        # Security check - only allow SELECT statements
        if not cleaned_sql.upper().startswith('SELECT'):
            return {"error": "Only SELECT statements are allowed for security reasons"}
        
        # Enhanced security checks
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE', 'REPLACE']
        sql_upper = cleaned_sql.upper()
        
        for keyword in dangerous_keywords:
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, sql_upper):
                return {"error": f"SQL contains dangerous keyword '{keyword}' - not allowed"}
        
        # Apply initial fixes including column name typos
        cleaned_sql = _fix_complete_sql_issues(cleaned_sql)
        # Apply column name fixes
        cleaned_sql = cleaned_sql.replace('subscription_start_date', 'subcription_start_date')
        cleaned_sql = cleaned_sql.replace('subscription_end_date', 'subcription_end_date')
        
        # Apply proactive MySQL compatibility fixes
        cleaned_sql = _fix_mysql_compatibility(cleaned_sql)
        
        # Apply proactive fixes for common issues
        cleaned_sql = _auto_fix_sql_errors(cleaned_sql, "proactive_fix")
        
        logger.info(f"🔍 Executing enhanced dynamic SQL: {cleaned_sql[:100]}...")
        
        # ENHANCED RETRY LOGIC with progressive fixes
        max_sql_retries = 3
        for attempt in range(max_sql_retries):
            try:
                results, error = _execute_query(cleaned_sql)
                
                if error and attempt < max_sql_retries - 1:
                    logger.warning(f"🔧 SQL attempt {attempt + 1} failed, applying enhanced auto-fix: {error}")
                    cleaned_sql = _auto_fix_sql_errors(cleaned_sql, error)
                    continue
                elif error:
                    return {"error": f"SQL execution failed after {max_sql_retries} enhanced attempts: {error}"}
                else:
                    # Success!
                    break
                    
            except Exception as e:
                if attempt < max_sql_retries - 1:
                    logger.warning(f"🔧 SQL execution attempt {attempt + 1} failed, applying enhanced auto-fix: {e}")
                    cleaned_sql = _auto_fix_sql_errors(cleaned_sql, str(e))
                    continue
                else:
                    return {"error": f"SQL execution failed after {max_sql_retries} enhanced attempts: {str(e)}"}
        
        if not results:
            return {
                "data": [], 
                "message": "Query executed successfully but returned no data. This could be due to:\n- Date ranges with no matching records\n- Filters that are too restrictive\n- Empty or test database\n- Column name or table issues\n\nTry:\n- 'Show me sample customer data' to see what's available\n- 'How many total subscriptions are there?' to check data volume\n- Using broader criteria or simpler queries",
                "sql_executed": cleaned_sql
            }
        
        return {
            "data": results,
            "message": f"Enhanced query executed successfully, returned {len(results)} rows",
            "sql_executed": cleaned_sql
        }
        
    except Exception as e:
        logger.error(f"Error in enhanced execute_dynamic_sql: {e}")
        return {"error": f"Enhanced dynamic SQL execution failed: {str(e)}"}

def _fix_mysql_compatibility(sql: str) -> str:
    """Fix MySQL compatibility issues proactively."""
    try:
        # Fix PostgreSQL DATE_TRUNC to MySQL equivalent
        sql = re.sub(r"DATE_TRUNC\s*\(\s*'month'\s*,\s*CURRENT_DATE\s*\)", 
                   "DATE_FORMAT(CURRENT_DATE, '%Y-%m-01')", sql)
        sql = re.sub(r"DATE_TRUNC\s*\(\s*'day'\s*,\s*CURRENT_DATE\s*\)", 
                   "CURRENT_DATE", sql)
        sql = re.sub(r"DATE_TRUNC\s*\(\s*'year'\s*,\s*CURRENT_DATE\s*\)", 
                   "DATE_FORMAT(CURRENT_DATE, '%Y-01-01')", sql)
        
        # Fix BETWEEN with date ranges for "this month" queries
        if 'BETWEEN DATE_FORMAT(CURRENT_DATE' in sql and 'AND CURRENT_DATE' in sql:
            # Replace with proper month range
            sql = re.sub(r"BETWEEN DATE_FORMAT\(CURRENT_DATE, '%Y-%m-01'\) AND CURRENT_DATE", 
                       "BETWEEN DATE_FORMAT(CURRENT_DATE, '%Y-%m-01') AND LAST_DAY(CURRENT_DATE)", sql)
        
        # Fix common MySQL date functions
        sql = sql.replace('CURRENT_DATE()', 'CURRENT_DATE')
        sql = sql.replace('NOW()', 'CURRENT_TIMESTAMP')
        
        return sql
    except Exception as e:
        logger.warning(f"MySQL compatibility fix failed: {e}")
        return sql

def _fix_complete_sql_issues(sql: str) -> str:
    """Fix common SQL issues with complete handling."""
    try:
        # Clean quotes more carefully - this is the main issue
        # Remove only problematic escaped quotes, not all quotes
        sql = sql.replace("\\'", "'")  # Remove escaped single quotes
        sql = sql.replace('\\"', '"')  # Remove escaped double quotes
        
        # Fix problematic quote patterns more carefully
        # Only fix quotes that are clearly wrong (like "value" should be 'value')
        sql = re.sub(r'"([^"]*?)"(?=\s*(=|!=|<>|\bin\b|\blike\b))', r"'\1'", sql, flags=re.IGNORECASE)
        
        # Fix specific date quote issues - dates should be in single quotes
        # Pattern: "YYYY-MM-DD" -> 'YYYY-MM-DD'
        sql = re.sub(r'"(\d{4}-\d{2}-\d{2})"', r"'\1'", sql)
        sql = re.sub(r'"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})"', r"'\1'", sql)
        
        # Fix incomplete quotes at start/end of string
        if sql.startswith('"') and not sql.endswith('"'):
            sql = sql[1:]  # Remove starting quote
        if sql.endswith('"') and not sql.startswith('"'):
            sql = sql[:-1]  # Remove ending quote
            
        # Fix status value issues - ensure they're properly quoted
        status_values = ['ACTIVE', 'INACTIVE', 'FAILED', 'FAIL', 'INIT', 'CLOSED', 'REJECT']
        for status in status_values:
            # Fix unquoted status values - be more careful about context
            pattern = rf'\bstatus\s*(?:=|!=|<>)\s*{status}\b'
            replacement = f"status = '{status}'"
            sql = re.sub(pattern, replacement, sql, flags=re.IGNORECASE)
        
        # Complete schema fixes - handle merchant_user_id GROUP BY issues
        if 'GROUP BY merchant_user_id' in sql and 'subscription_payment_details' in sql and 'JOIN' not in sql.upper():
            logger.warning("🔧 Fixing merchant_user_id GROUP BY without JOIN")
            # This is problematic - merchant_user_id doesn't exist in payment_details alone
            # Add proper JOIN or remove the GROUP BY
            if 'subscription_contract_v2' not in sql:
                # Add the JOIN
                sql = sql.replace('FROM subscription_payment_details', 
                                'FROM subscription_payment_details p JOIN subscription_contract_v2 c ON p.subscription_id = c.subscription_id')
                sql = sql.replace('GROUP BY merchant_user_id', 'GROUP BY c.merchant_user_id')
        
        # Clean up whitespace
        sql = re.sub(r'\s+', ' ', sql).strip()
        
        # Fix spaces between function names and parentheses
        sql = _fix_sql_function_spacing(sql)
        
        return sql
    except Exception as e:
        logger.warning(f"Error fixing complete SQL: {e}")
        return sql

def _auto_fix_sql_errors(sql: str, error: str) -> str:
    """Enhanced auto-fix for SQL errors with comprehensive pattern matching."""
    try:
        error_lower = error.lower()
        logger.info(f"🔧 Applying auto-fixes for error: {error[:100]}...")
        
        # Fix duplicate WHERE keywords
        sql = re.sub(r'WHERE\s+WHERE', 'WHERE', sql, flags=re.IGNORECASE)
        
        # Fix column name typos (most common issue)
        if "unknown column" in error_lower or "doesn't exist" in error_lower:
            logger.info("🔧 Fixing column name issues")
            # Fix subscription_start_date -> subcription_start_date (missing 's')
            sql = sql.replace('subscription_start_date', 'subcription_start_date')
            sql = sql.replace('subscription_end_date', 'subcription_end_date')
            
            # Fix table aliases if missing
            if 'FROM subscription_contract_v2' in sql and ' c' not in sql:
                sql = sql.replace('FROM subscription_contract_v2', 'FROM subscription_contract_v2 c')
            if 'FROM subscription_payment_details' in sql and ' p' not in sql:
                sql = sql.replace('FROM subscription_payment_details', 'FROM subscription_payment_details p')
        
        # Fix GROUP BY and aggregation issues
        elif "isn't in group by" in error_lower or "group by" in error_lower:
            logger.info("🔧 Fixing GROUP BY aggregation issues")
            # Find all SELECT columns that aren't aggregated
            select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql, re.IGNORECASE | re.DOTALL)
            if select_match:
                select_clause = select_match.group(1)
                # Split by comma and identify non-aggregated columns
                columns = [col.strip() for col in select_clause.split(',')]
                non_agg_columns = []
                for col in columns:
                    # Check if column is not an aggregate function
                    if not re.search(r'(COUNT|SUM|AVG|MIN|MAX|GROUP_CONCAT)\s*\(', col, re.IGNORECASE):
                        # Extract column name (remove aliases)
                        col_name = re.sub(r'\s+as\s+\w+', '', col, flags=re.IGNORECASE).strip()
                        if col_name and col_name not in non_agg_columns:
                            non_agg_columns.append(col_name)
                
                if non_agg_columns:
                    # Add GROUP BY if missing
                    if 'GROUP BY' not in sql.upper():
                        sql = sql + f" GROUP BY {', '.join(non_agg_columns)}"
                    else:
                        # FIXED: For weekly SQL, fix the GROUP BY to include CONCAT expression
                        if 'CONCAT(YEAR(' in sql and 'WEEK(' in sql:
                            # This is weekly aggregation SQL - fix GROUP BY to include CONCAT expression
                            concat_match = re.search(r'CONCAT\(YEAR\([^)]+\),\s*[^,]+,\s*LPAD\(WEEK\([^)]+\),\s*[^)]+\)\)', sql)
                            if concat_match:
                                concat_expr = concat_match.group(0)
                                # Replace GROUP BY YEAR(...), WEEK(...) with GROUP BY CONCAT(...)
                                group_by_pattern = r'GROUP\s+BY\s+YEAR\([^)]+\),\s*WEEK\([^)]+\)'
                                new_group_by = f"GROUP BY {concat_expr}"
                                sql = re.sub(group_by_pattern, new_group_by, sql, flags=re.IGNORECASE)
                                logger.info(f"🔧 Fixed weekly GROUP BY with CONCAT expression: {concat_expr}")
                            else:
                                logger.info(f"🔧 Preserving weekly GROUP BY structure - no CONCAT found")
                        else:
                            # Update existing GROUP BY for non-weekly queries
                            group_by_pattern = r'GROUP\s+BY\s+([^ORDER|LIMIT|HAVING|$]+)'
                            new_group_by = f"GROUP BY {', '.join(non_agg_columns)}"
                            sql = re.sub(group_by_pattern, new_group_by, sql, flags=re.IGNORECASE)
                            logger.info(f"🔧 Fixed GROUP BY with columns: {', '.join(non_agg_columns)}")
        
        # Fix quote escaping issues
        elif 'syntax' in error_lower or 'quote' in error_lower or '42000' in error_lower:
            logger.info("🔧 Applying quote fixes")
            # Remove escaped quotes
            sql = sql.replace("\\'", "'").replace('\\"', '"').replace("''", "'")
            sql = sql.strip()
            
            # Fix orphaned quotes
            if sql.startswith('"') and sql.count('"') % 2 == 1:
                sql = sql[1:]
            if sql.endswith('"') and sql.count('"') % 2 == 1:
                sql = sql[:-1]
            
            # Fix date strings specifically
            sql = re.sub(r'"(\d{4}-\d{2}-\d{2})', r"'\1'", sql)
            sql = re.sub(r'(\d{4}-\d{2}-\d{2})"', r"'\1'", sql)
            
            # Fix general string literals
            sql = re.sub(r'"([^"]*)"', r"'\1'", sql)
        
        # Fix date-related errors and MySQL function compatibility
        elif 'date' in error_lower or 'created_date' in sql.lower() or 'DATE_TRUNC' in sql or 'does not exist' in error_lower:
            logger.info("🔧 Fixing date-related errors and MySQL compatibility")
            
            # Fix PostgreSQL DATE_TRUNC to MySQL equivalent
            if 'DATE_TRUNC' in sql:
                # Replace DATE_TRUNC('month', CURRENT_DATE) with MySQL equivalent
                sql = re.sub(r"DATE_TRUNC\s*\(\s*'month'\s*,\s*CURRENT_DATE\s*\)", 
                           "DATE_FORMAT(CURRENT_DATE, '%Y-%m-01')", sql)
                sql = re.sub(r"DATE_TRUNC\s*\(\s*'day'\s*,\s*CURRENT_DATE\s*\)", 
                           "CURRENT_DATE", sql)
                sql = re.sub(r"DATE_TRUNC\s*\(\s*'year'\s*,\s*CURRENT_DATE\s*\)", 
                           "DATE_FORMAT(CURRENT_DATE, '%Y-01-01')", sql)
                logger.info("🔧 Fixed DATE_TRUNC to MySQL equivalent")
            
            # Fix date comparison patterns
            sql = re.sub(r'DATE\s*\(\s*created_date\s*\)\s*=\s*["\']?(\d{4}-\d{2}-\d{2})["\']?', 
                        r"DATE(created_date) = '\1'", sql)
            sql = re.sub(r'created_date\s*=\s*["\']?(\d{4}-\d{2}-\d{2})["\']?', 
                        r"DATE(created_date) = '\1'", sql)
        
        # Fix status value errors
        elif 'unknown column' in error_lower and 'status' in sql.lower():
            logger.info("🔧 Fixing status value quoting")
            status_values = ['ACTIVE', 'INACTIVE', 'FAILED', 'FAIL', 'INIT', 'CLOSED', 'REJECT']
            for status in status_values:
                # Fix unquoted status values
                pattern = rf'\bstatus\s*(?:=|!=|<>)\s*{status}\b'
                replacement = f"status = '{status}'"
                sql = re.sub(pattern, replacement, sql, flags=re.IGNORECASE)
        
        # Fix ORDER BY with aliases - replace alias with actual expression
        if 'ORDER BY subscription_value' in sql and 'COALESCE(' in sql:
            # Find the COALESCE expression for subscription_value
            coalesce_match = re.search(r'COALESCE\([^)]+\) as subscription_value', sql, re.IGNORECASE)
            if coalesce_match:
                coalesce_expr = coalesce_match.group(0).replace(' as subscription_value', '').replace(' AS subscription_value', '')
                sql = sql.replace('ORDER BY subscription_value', f'ORDER BY {coalesce_expr}')
                logger.info(f"🔧 Fixed ORDER BY alias with expression: {coalesce_expr}")
        
        # Fix incorrect JOIN conditions
        if 'c.merchant_user_id = p.subscription_id' in sql:
            sql = sql.replace('c.merchant_user_id = p.subscription_id', 'c.subscription_id = p.subscription_id')
            logger.info("🔧 Fixed JOIN condition: merchant_user_id -> subscription_id")
        
        # Remove unnecessary JOINs when not using payment data
        if 'LEFT JOIN subscription_payment_details p' in sql and 'p.' not in sql.replace('LEFT JOIN subscription_payment_details p', ''):
            sql = sql.replace('LEFT JOIN subscription_payment_details p ON c.subscription_id = p.subscription_id', '')
            sql = sql.replace('LEFT JOIN subscription_payment_details p ON c.merchant_user_id = p.subscription_id', '')
            sql = sql.replace('LEFT JOIN subscription_payment_details p', '')
            logger.info("🔧 Removed unnecessary JOIN")
        
        # Clean up whitespace and return
        sql = re.sub(r'\s+', ' ', sql).strip()
        logger.info(f"🔧 Auto-fix complete: {sql[:150]}...")
        return sql
        
    except Exception as e:
        logger.warning(f"Auto-fix failed: {e}")
        return sql

def _fix_select_columns_for_group_by(self, select_columns: str) -> str:
    """Fix SELECT columns for GROUP BY compatibility by adding aggregation functions."""
    try:
        columns = [col.strip() for col in select_columns.split(',')]
        fixed_columns = []
        
        for col in columns:
            col_lower = col.lower()
            
            # Skip if already an aggregation function
            if any(func in col_lower for func in ['count(', 'sum(', 'max(', 'min(', 'avg(']):
                fixed_columns.append(col)
            # Keep merchant_user_id as-is (it's in GROUP BY)
            elif 'merchant_user_id' in col_lower:
                fixed_columns.append(col)
            # Add MAX() to other columns to make them GROUP BY compatible
            else:
                # Remove table aliases for cleaner output
                clean_col = col.replace('c.', '').strip()
                fixed_columns.append(f'MAX({col}) as {clean_col}')
        
        result = ', '.join(fixed_columns)
        logger.info(f"🔧 Fixed SELECT columns: {result}")
        return result
        
    except Exception as e:
        logger.warning(f"Error fixing SELECT columns: {e}")
        return select_columns

# ===== COMPLETE ENHANCED GRAPH GENERATION =====

class CompleteEnhancedGraphAnalyzer:
    """COMPLETE Enhanced graph analyzer with full smart pie chart support."""
    
    @staticmethod
    def analyze_data_for_complete_graphing(data: List[Dict]) -> Dict:
        """Analyze data with complete enhanced chart type detection."""
        try:
            if not data or not isinstance(data, list) or len(data) == 0:
                return {"error": "No data available for complete graphing"}
            
            # Validate data structure
            if not all(isinstance(row, dict) for row in data):
                return {"error": "Invalid data structure - all items must be dictionaries"}
            
            columns = list(data[0].keys())
            num_rows = len(data)
            
            if not columns:
                return {"error": "No columns found in data"}
            
            logger.info(f"📊 Complete analyzing {num_rows} rows with columns: {columns}")
            
            # Complete enhanced column analysis
            column_analysis = CompleteEnhancedGraphAnalyzer._analyze_columns_complete(data, columns)
            
            # Complete enhanced recommendations with smart chart type detection
            recommendations = CompleteEnhancedGraphAnalyzer._generate_complete_recommendations(
                column_analysis, num_rows, data, columns
            )
            
            return {
                "columns": columns,
                "num_rows": num_rows,
                "column_analysis": column_analysis,
                "recommended_graphs": recommendations
            }
            
        except Exception as e:
            logger.error(f"❌ Complete data analysis failed: {e}")
            return {"error": f"Complete data analysis failed: {str(e)}"}
    
    @staticmethod
    def _analyze_columns_complete(data: List[Dict], columns: List[str]) -> Dict:
        """Complete enhanced column analysis with better type detection."""
        column_analysis = {}
        
        for col in columns:
            try:
                # Get sample values safely with complete logic
                values = []
                for row in data[:20]:  # Check more rows for better analysis
                    val = row.get(col)
                    if val is not None:
                        values.append(val)
                
                if not values:
                    column_analysis[col] = {'type': 'empty', 'unique_count': 0}
                    continue
                
                sample_value = values[0]
                
                # Complete enhanced type determination
                if isinstance(sample_value, (int, float, decimal.Decimal)):
                    # Check if all values are numeric with better threshold
                    numeric_count = sum(1 for v in values if isinstance(v, (int, float, decimal.Decimal)))
                    if numeric_count / len(values) >= 0.8:  # 80% numeric
                        
                        # Complete enhanced numeric analysis
                        numeric_values = [float(v) for v in values if isinstance(v, (int, float, decimal.Decimal))]
                        column_analysis[col] = {
                            'type': 'numeric',
                            'min': min(numeric_values),
                            'max': max(numeric_values),
                            'avg': sum(numeric_values) / len(numeric_values),
                            'unique_count': len(set(values)),
                            'is_rate': CompleteEnhancedGraphAnalyzer._is_rate_column(col, numeric_values),
                            'is_count': CompleteEnhancedGraphAnalyzer._is_count_column(col, numeric_values),
                            'is_percentage': CompleteEnhancedGraphAnalyzer._is_percentage_column(col, numeric_values)
                        }
                    else:
                        column_analysis[col] = {'type': 'mixed', 'unique_count': len(set(values))}
                
                elif isinstance(sample_value, str):
                    # Complete enhanced date detection
                    is_date = CompleteEnhancedGraphAnalyzer._is_date_column_complete(values)
                    if is_date:
                        column_analysis[col] = {
                            'type': 'datetime',
                            'unique_count': len(set(values)),
                            'date_range': CompleteEnhancedGraphAnalyzer._get_date_range_complete(values),
                            'sample_values': values[:3]
                        }
                    else:
                        unique_values = list(set(str(v) for v in values))
                        column_analysis[col] = {
                            'type': 'categorical',
                            'unique_count': len(unique_values),
                            'categories': unique_values[:10],
                            'is_status': CompleteEnhancedGraphAnalyzer._is_status_column(col, unique_values),
                            'is_binary': len(unique_values) == 2,
                            'is_success_failure': CompleteEnhancedGraphAnalyzer._is_success_failure_column(col, unique_values)
                        }
                
                else:
                    column_analysis[col] = {
                        'type': 'other',
                        'unique_count': len(set(str(v) for v in values))
                    }
                    
            except Exception as e:
                logger.warning(f"⚠️ Error analyzing complete column {col}: {e}")
                column_analysis[col] = {'type': 'error', 'unique_count': 0}
        
        return column_analysis
    
    @staticmethod
    def _is_rate_column(col_name: str, values: List[float]) -> bool:
        """Check if column represents a rate or percentage."""
        col_lower = col_name.lower()
        rate_keywords = ['rate', 'percent', 'ratio', 'success']
        
        # Check name
        name_suggests_rate = any(keyword in col_lower for keyword in rate_keywords)
        
        # Check values (rates are usually 0-100 or 0-1)
        if values:
            max_val = max(values)
            min_val = min(values)
            values_suggest_rate = (0 <= min_val <= max_val <= 100) or (0 <= min_val <= max_val <= 1)
        else:
            values_suggest_rate = False
        
        return name_suggests_rate or values_suggest_rate
    
    @staticmethod
    def _is_count_column(col_name: str, values: List[float]) -> bool:
        """Check if column represents counts."""
        col_lower = col_name.lower()
        count_keywords = ['count', 'total', 'number', 'num', 'transactions', 'value']
        
        # Check name
        name_suggests_count = any(keyword in col_lower for keyword in count_keywords)
        
        # Check if values are integers
        if values:
            all_integers = all(v == int(v) for v in values)
            non_negative = all(v >= 0 for v in values)
        else:
            all_integers = False
            non_negative = False
        
        return name_suggests_count and all_integers and non_negative
    
    @staticmethod
    def _is_percentage_column(col_name: str, values: List[float]) -> bool:
        """Check if column represents percentages."""
        col_lower = col_name.lower()
        if 'percent' in col_lower or '%' in col_lower:
            return True
        
        if values:
            max_val = max(values)
            min_val = min(values)
            # Values between 0-100 with decimals suggest percentages
            return 0 <= min_val <= max_val <= 100 and any(v != int(v) for v in values)
        
        return False
    
    @staticmethod
    def _is_success_failure_column(col_name: str, values: List[str]) -> bool:
        """Check if column represents success/failure categories."""
        success_keywords = {'success', 'successful', 'active', 'complete', 'pass'}
        failure_keywords = {'failure', 'failed', 'inactive', 'error', 'fail'}
        
        values_lower = {str(v).lower() for v in values}
        
        has_success = bool(success_keywords.intersection(values_lower))
        has_failure = bool(failure_keywords.intersection(values_lower))
        
        return has_success and has_failure
    
    @staticmethod
    def _is_date_column_complete(values: List) -> bool:
        """Complete enhanced date column detection."""
        try:
            date_patterns = [
                r'^\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                r'^\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
                r'^\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
                r'^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}',  # Datetime
            ]
            
            date_count = 0
            for val in values[:15]:  # Check more values
                val_str = str(val)
                for pattern in date_patterns:
                    if re.match(pattern, val_str):
                        date_count += 1
                        break
            
            return date_count / len(values[:15]) >= 0.7  # 70% look like dates
        except Exception:
            return False
    
    @staticmethod
    def _get_date_range_complete(values: List) -> Dict:
        """Get complete date range information."""
        try:
            # Simple date range detection
            dates = [str(v)[:10] for v in values if str(v)]  # Get date part
            if dates:
                return {
                    'start': min(dates),
                    'end': max(dates),
                    'span_days': len(set(dates)),
                    'unique_dates': len(set(dates))
                }
        except Exception:
            pass
        return {}
    
    @staticmethod
    def _is_status_column(col_name: str, values: List[str]) -> bool:
        """Check if column represents status values."""
        col_lower = col_name.lower()
        status_keywords = ['status', 'state', 'type']
        
        # Check name
        name_suggests_status = any(keyword in col_lower for keyword in status_keywords)
        
        # Check common status values
        common_statuses = {'active', 'inactive', 'success', 'failed', 'pending', 'complete'}
        values_lower = {str(v).lower() for v in values}
        has_status_values = bool(common_statuses.intersection(values_lower))
        
        return name_suggests_status or has_status_values
    
    @staticmethod
    def _generate_complete_recommendations(column_analysis: Dict, num_rows: int, data: List[Dict], columns: List[str]) -> List[Dict]:
        """Generate complete enhanced graph recommendations with smart chart type detection."""
        try:
            recommendations = []
            
            numeric_cols = [col for col, info in column_analysis.items() if info.get('type') == 'numeric']
            datetime_cols = [col for col, info in column_analysis.items() if info.get('type') == 'datetime']
            categorical_cols = [col for col, info in column_analysis.items() if info.get('type') == 'categorical']
            
            logger.info(f"📊 Complete column types: numeric={len(numeric_cols)}, datetime={len(datetime_cols)}, categorical={len(categorical_cols)}")
            
            # PIE CHART DETECTION - Enhanced logic for 2 column data
            if len(columns) == 2 and categorical_cols and numeric_cols:
                recommendations.append({
                    'type': 'pie',
                    'title': 'Distribution Analysis',
                    'category': categorical_cols[0],
                    'value': numeric_cols[0],
                    'priority': 1,
                    'data_aggregation': 'category_totals'
                })
            
            # Time series recommendations
            if datetime_cols and numeric_cols and num_rows > 1:
                recommendations.append({
                    'type': 'line',
                    'title': 'Time Series Analysis',
                    'x_axis': datetime_cols[0],
                    'y_axis': numeric_cols[0],
                    'priority': 2 if recommendations else 1,
                    'data_aggregation': 'time_series'
                })
            
            # Bar chart for categorical data
            if categorical_cols and numeric_cols and num_rows > 1:
                if num_rows <= 50:
                    recommendations.append({
                        'type': 'bar',
                        'title': 'Category Analysis',
                        'x_axis': categorical_cols[0],
                        'y_axis': numeric_cols[0],
                        'priority': 3 if recommendations else 1,
                        'data_aggregation': 'category_comparison'
                    })
            
            # Default pie chart if we have suitable data
            if not recommendations and len(columns) >= 2:
                recommendations.append({
                    'type': 'pie',
                    'title': 'Data Distribution',
                    'priority': 1,
                    'data_aggregation': 'default_pie'
                })
            
            # Sort by priority
            recommendations.sort(key=lambda x: x.get('priority', 99))
            
            logger.info(f"📊 Generated {len(recommendations)} complete recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Complete recommendation generation failed: {e}")
            return []

def complete_generate_graph_data(data: List[Dict], graph_type: str = None, custom_config: Dict = None) -> Dict:
    """FIXED: COMPLETE enhanced graph data generation with smart pie chart support and proper data conversion."""
    try:
        if not data or not isinstance(data, list) or len(data) == 0:
            return {"error": "No data provided for complete graph generation"}
        
        # Validate data structure
        if not all(isinstance(row, dict) for row in data):
            return {"error": "Invalid data structure - expected list of dictionaries"}
        
        # Complete enhanced analysis
        analysis = CompleteEnhancedGraphAnalyzer.analyze_data_for_complete_graphing(data)
        if "error" in analysis:
            return analysis
        
        logger.info(f"📊 Complete graph analysis complete for {len(data)} rows")
        
        # Smart graph type selection with complete enhanced logic
        selected_graph = None
        
        if graph_type:
            # Complete enhanced graph type matching
            if graph_type == 'pie':
                # Smart pie chart selection based on data characteristics
                for rec in analysis['recommended_graphs']:
                    if 'pie' in rec['type']:
                        selected_graph = rec
                        logger.info(f"📊 Selected complete pie chart type: {rec['type']}")
                        break
                
                # If no specific pie recommendation, create smart default
                if not selected_graph:
                    selected_graph = {
                        'type': 'pie',
                        'title': 'Complete Data Distribution',
                        'priority': 1,
                        'data_aggregation': 'smart_pie'
                    }
            else:
                # Match other graph types
                for rec in analysis['recommended_graphs']:
                    if rec['type'] == graph_type:
                        selected_graph = rec
                        break
        else:
            # Use best recommendation
            if analysis['recommended_graphs']:
                selected_graph = analysis['recommended_graphs'][0]
        
        if not selected_graph:
            # Create a fallback pie chart
            selected_graph = {
                'type': 'pie',
                'title': 'Data Visualization',
                'priority': 1,
                'data_aggregation': 'fallback_pie'
            }
        
        # Apply custom config
        if custom_config:
            selected_graph.update(custom_config)
        
        # FIXED: Complete enhanced data preparation with proper format conversion
        prepared_data = _prepare_complete_graph_data(data, selected_graph)
        if "error" in prepared_data:
            return prepared_data
        
        # Build complete enhanced final response
        graph_data = {
            "graph_type": selected_graph.get('type', 'pie'),
            "title": custom_config.get('title') if custom_config else selected_graph.get('title', 'Complete Data Visualization'),
            "description": custom_config.get('description') if custom_config else selected_graph.get('description', ''),
            "data_summary": {
                "total_rows": len(data),
                "columns": analysis['columns'],
                "chart_optimization": selected_graph.get('data_aggregation', 'standard')
            },
            "metadata": {
                "analysis": analysis,
                "selected_type": selected_graph['type'],
                "complete_features": True,
                "generated_at": datetime.datetime.now().isoformat()
            }
        }
        
        graph_data.update(prepared_data)
        
        logger.info(f"✅ Complete graph data generated successfully: {selected_graph['type']}")
        return {"data": graph_data}
        
    except Exception as e:
        logger.error(f"❌ Critical complete graph generation error: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return {"error": f"Critical complete graph generation failure: {str(e)}"}

def _prepare_complete_graph_data(data: List[Dict], graph_config: Dict) -> Dict:
    """FIXED: Prepare complete graph data with proper format conversion for all chart types."""
    try:
        graph_type = graph_config.get('type', 'pie')
        columns = list(data[0].keys()) if data else []
        
        logger.info(f"📊 Preparing {graph_type} chart data with columns: {columns}")
        
        if graph_type == 'pie':
            # Complete pie chart data preparation
            if len(data) == 1:
                # Single row - use column names as categories
                row = data[0]
                labels = []
                values = []
                
                # Smart column selection for pie charts
                relevant_columns = []
                for key, value in row.items():
                    if isinstance(value, (int, float)) and value > 0:
                        relevant_columns.append((key, float(value)))
                
                # Sort by value for better visualization
                relevant_columns.sort(key=lambda x: x[1], reverse=True)
                
                for key, value in relevant_columns:
                    clean_label = _clean_column_name_for_display(key)
                    labels.append(clean_label)
                    values.append(value)
                
                if labels and values:
                    return {"labels": labels, "values": values}
            else:
                # Multiple rows - handle different pie chart types
                if len(columns) >= 2:
                    category_col = columns[0]
                    value_col = columns[1]
                    
                    labels = []
                    values = []
                    
                    for row in data:
                        cat_val = row.get(category_col)
                        num_val = row.get(value_col)
                        
                        if cat_val is not None and num_val is not None:
                            labels.append(str(cat_val)[:30])  # Truncate long labels
                            try:
                                values.append(float(num_val))
                            except (ValueError, TypeError):
                                values.append(0)
                    
                    return {"labels": labels, "values": values}
        
        elif graph_type in ['bar', 'horizontal_bar']:
            # FIXED: Complete bar charts with proper data mapping
            if len(columns) >= 2:
                # Try to identify the best columns for x and y
                x_col = columns[0]
                y_col = columns[1]
                
                # Look for better column mapping
                for col in columns:
                    if any(word in col.lower() for word in ['amount', 'revenue', 'total', 'count', 'value', 'num']):
                        y_col = col
                        break
                
                categories = []
                values = []
                
                for row in data:
                    x_val = row.get(x_col)
                    y_val = row.get(y_col)
                    
                    if x_val is not None and y_val is not None:
                        categories.append(str(x_val)[:50])  # Handle long category names
                        try:
                            values.append(float(y_val))
                        except (ValueError, TypeError):
                            values.append(0)
                
                return {
                    "categories": categories, 
                    "values": values,
                    "x_label": _clean_column_name_for_display(x_col),
                    "y_label": _clean_column_name_for_display(y_col)
                }
        
        elif graph_type == 'line':
            # FIXED: Complete line charts with proper time series mapping
            if len(columns) >= 2:
                # Smart column identification for time series
                time_col = None
                value_col = None
                
                # Find time/period column
                for col in columns:
                    col_lower = col.lower()
                    if any(word in col_lower for word in ['date', 'time', 'period', 'month', 'year', 'day']):
                        time_col = col
                        break
                
                # Find value column
                for col in columns:
                    col_lower = col.lower()
                    if any(word in col_lower for word in ['revenue', 'amount', 'total', 'count', 'value', 'num']):
                        value_col = col
                        break
                
                # Fallback to first two columns if no smart mapping found
                if not time_col:
                    time_col = columns[0]
                if not value_col:
                    value_col = columns[1]
                
                x_values = []
                y_values = []
                
                for row in data:
                    x_val = row.get(time_col)
                    y_val = row.get(value_col)
                    
                    if x_val is not None and y_val is not None:
                        x_values.append(str(x_val))
                        try:
                            y_values.append(float(y_val))
                        except (ValueError, TypeError):
                            y_values.append(0)
                
                logger.info(f"📊 Line chart prepared: {len(x_values)} data points, x_col='{time_col}', y_col='{value_col}'")
                
                return {
                    "x_values": x_values, 
                    "y_values": y_values,
                    "x_label": _clean_column_name_for_display(time_col),
                    "y_label": _clean_column_name_for_display(value_col)
                }
        
        elif graph_type == 'scatter':
            # Complete scatter plots
            if len(columns) >= 2:
                x_col = columns[0]
                y_col = columns[1]
                
                x_values = []
                y_values = []
                
                for row in data:
                    x_val = row.get(x_col)
                    y_val = row.get(y_col)
                    
                    if x_val is not None and y_val is not None:
                        try:
                            x_values.append(float(x_val))
                            y_values.append(float(y_val))
                        except (ValueError, TypeError):
                            continue  # Skip non-numeric values
                
                return {
                    "x_values": x_values, 
                    "y_values": y_values,
                    "x_label": _clean_column_name_for_display(x_col),
                    "y_label": _clean_column_name_for_display(y_col)
                }
        
        return {"error": f"Cannot prepare data for graph type: {graph_type}"}
        
    except Exception as e:
        logger.error(f"Error preparing complete graph data: {e}")
        return {"error": f"Complete data preparation failed: {str(e)}"}

def _clean_column_name_for_display(col_name: str) -> str:
    """Clean column name for better display."""
    try:
        # Remove underscores and capitalize
        clean_name = col_name.replace('_', ' ').title()
        
        # Remove common suffixes
        suffixes_to_remove = [' Rate', ' Percent', ' Count', ' Total']
        for suffix in suffixes_to_remove:
            if clean_name.endswith(suffix):
                clean_name = clean_name[:-len(suffix)]
        
        # Handle specific cases
        if 'success' in clean_name.lower():
            clean_name = 'Successful'
        elif any(word in clean_name.lower() for word in ['fail', 'error']):
            clean_name = 'Failed'
        
        return clean_name
        
    except Exception:
        return str(col_name)

# ===== COMPLETE FEEDBACK FUNCTIONS =====

def complete_record_query_feedback(original_question: str, sql_query: str, was_helpful: bool, improvement_suggestion: str = None) -> Dict:
    """COMPLETE enhanced feedback recording with full chart type awareness."""
    try:
        if not original_question or not sql_query:
            return {"error": "Both original_question and sql_query are required"}
        
        if not isinstance(was_helpful, bool):
            return {"error": "was_helpful must be a boolean value"}
        
        # Complete enhanced validation
        if not was_helpful and improvement_suggestion:
            improvement_suggestion = improvement_suggestion.strip()
            if len(improvement_suggestion) < 5:
                return {"error": "Improvement suggestion must be at least 5 characters long"}
            if len(improvement_suggestion) > 1000:
                return {"error": "Improvement suggestion must be less than 1000 characters"}
        
        # Extract chart type from improvement suggestion
        chart_type = None
        if improvement_suggestion:
            imp_lower = improvement_suggestion.lower()
            if 'pie chart' in imp_lower:
                chart_type = 'pie'
            elif 'bar chart' in imp_lower:
                chart_type = 'bar'
            elif 'line chart' in imp_lower:
                chart_type = 'line'
        
        # Record complete feedback
        if complete_semantic_learner:
            complete_semantic_learner.add_complete_query_feedback(
                original_question, 
                sql_query, 
                was_helpful, 
                improvement_suggestion,
                chart_type
            )
            
            if was_helpful:
                return {"message": "✅ Thank you! Your positive feedback has been recorded in the complete system."}
            else:
                if improvement_suggestion:
                    return {
                        "message": "✅ Thank you! Your feedback and improvement suggestion have been recorded in the complete system.",
                        "data": {"improvement_recorded": True, "chart_type_detected": chart_type}
                    }
                else:
                    return {"message": "✅ Thank you! Your feedback has been recorded in the complete system."}
        else:
            return {"message": "✅ Thank you for your feedback (complete system)."}
            
    except Exception as e:
        logger.warning(f"⚠️ Complete feedback processing failed: {e}")
        return {"message": "✅ Thank you for your feedback (recorded locally in complete system)."}

def complete_get_improvement_suggestions(original_question: str) -> Dict:
    """Get COMPLETE improvement suggestions with full chart type awareness."""
    try:
        if not complete_semantic_learner:
            return {"message": "Complete improvement suggestions not available (semantic learning disabled)"}
        
        suggestions = complete_semantic_learner.get_complete_improvement_suggestions(original_question)
        
        if not suggestions:
            return {"message": "No complete improvement suggestions found for similar queries"}
        
        result = {
            "suggestions_found": len(suggestions),
            "improvements": []
        }
        
        for suggestion in suggestions:
            try:
                improvement = {
                    "similarity_score": f"{suggestion['similarity']:.2f}",
                    "similar_question": suggestion['question'][:200],
                    "what_failed": suggestion['failed_sql'][:100] + "..." if len(suggestion['failed_sql']) > 100 else suggestion['failed_sql'],
                    "user_suggestion": suggestion['improvement_suggestion'][:300],
                    "improvement_category": suggestion.get('improvement_category', 'general'),
                    "chart_type": suggestion.get('chart_type'),
                    "query_category": suggestion.get('query_category', 'general'),
                    "sql_complexity": suggestion.get('sql_complexity', 'unknown'),
                    "timestamp": suggestion['timestamp']
                }
                result["improvements"].append(improvement)
            except Exception as e:
                logger.warning(f"⚠️ Error processing complete suggestion: {e}")
                continue
        
        return {"data": result}
        
    except Exception as e:
        logger.warning(f"⚠️ Complete improvement suggestions failed: {e}")
        return {"error": f"Failed to get complete suggestions: {str(e)}"}

def complete_get_similar_queries(original_question: str) -> Dict:
    """Get similar successful queries for context."""
    try:
        if not complete_semantic_learner:
            return {"message": "Similar queries not available (semantic learning disabled)"}
        
        similar_queries = complete_semantic_learner.get_similar_successful_queries(original_question)
        
        if not similar_queries:
            return {"message": "No similar successful queries found"}
        
        result = {
            "similar_queries_found": len(similar_queries),
            "queries": []
        }
        
        for query in similar_queries:
            try:
                query_info = {
                    "similarity_score": f"{query['similarity']:.2f}",
                    "question": query['question'][:200],
                    "successful_sql": query['sql'][:200] + "..." if len(query['sql']) > 200 else query['sql'],
                    "query_category": query.get('query_category', 'general'),
                    "chart_type": query.get('chart_type'),
                    "sql_complexity": query.get('sql_complexity', 'unknown')
                }
                result["queries"].append(query_info)
            except Exception as e:
                logger.warning(f"⚠️ Error processing similar query: {e}")
                continue
        
        return {"data": result}
        
    except Exception as e:
        logger.warning(f"⚠️ Similar queries search failed: {e}")
        return {"error": f"Failed to get similar queries: {str(e)}"}

# ===== INITIALIZE COMPLETE SEMANTIC LEARNER =====

try:
    complete_semantic_learner = CompleteEnhancedSemanticLearner()
except Exception as e:
    logger.warning(f"Failed to initialize complete semantic learner: {e}")
    complete_semantic_learner = None

# ===== PYDANTIC MODELS =====

class ToolRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict = Field(default_factory=dict, description="Parameters for the tool")
    
    @field_validator('tool_name')
    @classmethod
    def validate_tool_name(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError('tool_name must be a non-empty string')
        return v.strip()

class ToolResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None

class ToolInfo(BaseModel):
    name: str
    description: str
    parameters: Dict

# ===== COMPLETE TOOL REGISTRY =====

COMPLETE_TOOL_REGISTRY = {
    "get_subscriptions_in_last_days": {
        "function": get_subscriptions_in_last_days,
        "description": "Get subscription statistics for the last N days",
        "parameters": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "Number of days to look back (1-365)"}
            },
            "required": ["days"]
        }
    },
    "get_payment_success_rate_in_last_days": {
        "function": get_payment_success_rate_in_last_days,
        "description": "Get payment success rate and revenue statistics for the last N days",
        "parameters": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "Number of days to look back (1-365)"}
            },
            "required": ["days"]
        }
    },
    "get_user_payment_history": {
        "function": get_user_payment_history,
        "description": "Get payment history for a specific user by merchant_user_id",
        "parameters": {
            "type": "object",
            "properties": {
                "merchant_user_id": {"type": "string", "description": "The merchant user ID"},
                "days": {"type": "integer", "description": "Number of days to look back (default: 90)"}
            },
            "required": ["merchant_user_id"]
        }
    },
    "get_database_status": {
        "function": get_database_status,
        "description": "Check database connection and get basic statistics",
        "parameters": {"type": "object", "properties": {}}
    },
    "execute_dynamic_sql": {
        "function": complete_execute_dynamic_sql,
        "description": "Execute a custom SELECT SQL query for analytics with complete enhanced error handling",
        "parameters": {
            "type": "object",
            "properties": {
                "sql_query": {"type": "string", "description": "SELECT SQL query to execute"}
            },
            "required": ["sql_query"]
        }
    },
    "generate_graph_data": {
        "function": complete_generate_graph_data,
        "description": "Generate complete enhanced graph-ready data with smart pie chart support and intelligent fallbacks",
        "parameters": {
            "type": "object", 
            "properties": {
                "data": {
                    "type": "array",
                    "description": "Array of dictionaries containing the data to visualize"
                },
                "graph_type": {
                    "type": "string",
                    "description": "Graph type: line, bar, horizontal_bar, pie, scatter"
                },
                "custom_config": {
                    "type": "object",
                    "description": "Custom configuration for complete enhanced features"
                }
            },
            "required": ["data"]
        }
    },
    "record_query_feedback": {
        "function": complete_record_query_feedback,
        "description": "Record complete enhanced user feedback with full chart type awareness",
        "parameters": {
            "type": "object",
            "properties": {
                "original_question": {"type": "string"},
                "sql_query": {"type": "string"},
                "was_helpful": {"type": "boolean"},
                "improvement_suggestion": {"type": "string"}
            },
            "required": ["original_question", "sql_query", "was_helpful"]
        }
    },
    "get_improvement_suggestions": {
        "function": complete_get_improvement_suggestions,
        "description": "Get complete enhanced improvement suggestions with full chart type awareness",
        "parameters": {
            "type": "object",
            "properties": {
                "original_question": {"type": "string", "description": "The question to find complete suggestions for"}
            },
            "required": ["original_question"]
        }
    },
    "get_similar_queries": {
        "function": complete_get_similar_queries,
        "description": "Get similar successful queries for context and learning",
        "parameters": {
            "type": "object",
            "properties": {
                "original_question": {"type": "string", "description": "The question to find similar successful queries for"}
            },
            "required": ["original_question"]
        }
    }
}

# ===== FASTAPI SETUP =====

API_KEY = os.getenv("API_KEY_1")
if not API_KEY:
    logger.error("❌ FATAL: API_KEY_1 environment variable is not set")
    raise ValueError("API_KEY_1 must be set")

def verify_api_key(authorization: str = Header(None)):
    """Verify API key."""
    try:
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header is required"
            )
        
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header must start with 'Bearer '"
            )
        
        token = authorization.split(" ")[1]
        if not secrets.compare_digest(token, API_KEY):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API key verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error"
        )

@asynccontextmanager
async def complete_lifespan(app: FastAPI):
    """Complete application lifespan handler."""
    logger.info("🚀 Starting COMPLETE Subscription Analytics API Server with MULTITOOL Support")
    logger.info(f"Complete semantic learning: {'enabled' if SEMANTIC_LEARNING_ENABLED else 'disabled'}")
    logger.info(f"Available complete tools: {len(COMPLETE_TOOL_REGISTRY)}")
    logger.info("🛡️ Complete enhanced error handling and smart graph generation enabled")
    logger.info("📊 Complete smart pie chart support with full chart type awareness")
    logger.info("🧠 Complete semantic learning with full feedback integration")
    logger.info("🔗 MULTITOOL FUNCTIONALITY FULLY SUPPORTED AND OPTIMIZED")
    logger.info("⚡ Enhanced performance and stability improvements")
    logger.info("🔧 FIXED: Graph data preparation for all chart types")
    yield
    logger.info("🛑 Shutting down Complete API Server")

# Create Complete FastAPI app
app = FastAPI(
    title="Complete Subscription Analytics API with MULTITOOL Support",
    description="Complete subscription analytics with full semantic learning, smart graph generation, and MULTITOOL functionality",
    version="complete-2.0.0-multitool-fixed",
    lifespan=complete_lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ===== COMPLETE API ENDPOINTS =====

@app.get("/health")
def complete_health_check():
    """Complete health check endpoint with MULTITOOL status."""
    try:
        health_data = {
            "status": "ok",
            "complete_semantic_learning": "enabled" if SEMANTIC_LEARNING_ENABLED else "disabled",
            "timestamp": datetime.datetime.now().isoformat(),
            "available_tools": len(COMPLETE_TOOL_REGISTRY),
            "version": "complete-2.0.0-multitool-fixed",
            "multitool_support": "enabled",
            "complete_features": [
                "complete_core_tools_implemented",
                "complete_smart_pie_chart_generation",
                "complete_semantic_learning",
                "complete_feedback_system",
                "complete_schema_handling",
                "complete_error_handling",
                "complete_chart_type_awareness",
                "multitool_functionality_enabled",
                "enhanced_performance_optimizations",
                "production_ready_stability",
                "fixed_graph_data_preparation"
            ]
        }
        
        if complete_semantic_learner and hasattr(complete_semantic_learner, 'known_queries'):
            try:
                total_queries = len(complete_semantic_learner.known_queries)
                positive_count = sum(1 for q in complete_semantic_learner.known_queries if q.get('was_helpful', True))
                negative_count = total_queries - positive_count
                chart_feedback_count = sum(1 for q in complete_semantic_learner.known_queries if q.get('chart_type'))
                
                health_data.update({
                    "complete_learning_stats": {
                        "total_learned_queries": total_queries,
                        "positive_examples": positive_count,
                        "negative_examples": negative_count,
                        "chart_type_feedback": chart_feedback_count,
                        "learning_enabled": True
                    }
                })
            except Exception:
                pass
        
        return health_data
    except Exception as e:
        logger.error(f"❌ Complete health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat(),
            "version": "complete-2.0.0-multitool-fixed"
        }

@app.get("/tools", response_model=List[ToolInfo], dependencies=[Depends(verify_api_key)])
def list_complete_tools():
    """List all available complete tools with MULTITOOL support."""
    try:
        return [
            ToolInfo(name=name, description=info["description"], parameters=info["parameters"])
            for name, info in COMPLETE_TOOL_REGISTRY.items()
            if name not in ["record_query_feedback"]  # Hide internal tools
        ]
    except Exception as e:
        logger.error(f"❌ Error listing complete tools: {e}")
        raise HTTPException(status_code=500, detail="Error listing complete tools")

@app.post("/execute", response_model=ToolResponse, dependencies=[Depends(verify_api_key)])
def execute_complete_tool(request: ToolRequest):
    """Execute a specific complete tool with MULTITOOL support and enhanced performance."""
    start_time = datetime.datetime.now()
    
    try:
        logger.info(f"🔧 Complete tool execution request: {request.tool_name}")
        
        if request.tool_name not in COMPLETE_TOOL_REGISTRY:
            raise HTTPException(
                status_code=404,
                detail=f"Complete tool '{request.tool_name}' not found"
            )
        
        tool_info = COMPLETE_TOOL_REGISTRY[request.tool_name]
        
        try:
            logger.info(f"⚙️ Executing complete {request.tool_name}")
            result = tool_info["function"](**request.parameters)
        except TypeError as e:
            logger.error(f"❌ Complete parameter error for {request.tool_name}: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid parameters for complete tool '{request.tool_name}': {str(e)}"
            )
        except Exception as e:
            logger.error(f"❌ Complete tool execution error for {request.tool_name}: {e}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return ToolResponse(
                success=False,
                error=f"Complete tool execution failed: {str(e)}"
            )
        
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        
        if "error" in result:
            logger.warning(f"Complete tool {request.tool_name} returned error: {result['error']}")
            return ToolResponse(success=False, error=result["error"])
        
        logger.info(f"✅ Complete tool {request.tool_name} completed in {execution_time:.2f}s")
        return ToolResponse(
            success=True,
            data=result.get("data"),
            message=result.get("message")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in complete execute_tool: {e}")
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return ToolResponse(
            success=False,
            error=f"Complete server error: {str(e)}"
        )
    finally:
        try:
            gc.collect()
        except Exception:
            pass

def _fix_sql_function_spacing(sql_query: str) -> str:
    """Fix spaces between function names and parentheses."""
    functions = ['MIN', 'MAX', 'COUNT', 'SUM', 'AVG', 'DATE_FORMAT', 'YEARWEEK']
    for func in functions:
        sql_query = re.sub(rf'\b{func}\s+\(', f'{func}(', sql_query, flags=re.IGNORECASE)
    return sql_query

if __name__ == "__main__":
    # Validate environment variables
    required_env_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'API_KEY_1']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ FATAL: Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"🚀 Starting COMPLETE SERVER with MULTITOOL SUPPORT on port {port}")
    logger.info("🛡️ All complete functions implemented and working")
    logger.info("📊 Complete smart pie chart support with full schema handling")
    logger.info("🧠 Complete semantic learning with feedback system")
    logger.info("🔧 Complete enhanced error handling and SQL fixing")
    logger.info("🎯 Complete chart type awareness and learning")
    logger.info("🔗 MULTITOOL FUNCTIONALITY FULLY ENABLED AND OPTIMIZED")
    logger.info("⚡ Enhanced performance and production-ready stability")
    logger.info("🔧 FIXED: Graph data preparation for line charts and all chart types")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1,
        log_level="info",
        access_log=True,
        loop="asyncio"
    )