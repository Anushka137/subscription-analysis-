"""
Query processing module for SQL generation and execution.
Handles natural language to SQL conversion and query optimization.
"""

import logging
import re
import time
from typing import Dict, List, Optional, Any, Tuple
import google.generativeai as genai

from ..core.config import get_settings
from ..database.connection import get_db_manager
from ..ai.feedback_learner import get_feedback_learner

logger = logging.getLogger(__name__)

class QueryProcessor:
    """Processes natural language queries and converts them to SQL."""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_manager = get_db_manager()
        self.feedback_learner = get_feedback_learner()
        self._initialize_ai()
    
    def _initialize_ai(self):
        """Initialize the AI model for query processing."""
        try:
            genai.configure(api_key=self.settings.api.google_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("✅ AI model initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI model: {e}")
            self.model = None
    
    def get_database_schema(self) -> str:
        """Get the database schema for AI context."""
        return """
        Database Schema:
        
        subscription_contract_v2 (c):
        - subscription_id (VARCHAR)
        - merchant_user_id (VARCHAR)
        - user_email (VARCHAR)
        - renewal_amount (DECIMAL)
        - max_amount_decimal (DECIMAL)
        - subcription_start_date (DATE)
        - subcription_end_date (DATE)
        - status (VARCHAR)
        
        subscription_payment_details (p):
        - payment_id (VARCHAR)
        - subscription_id (VARCHAR)
        - trans_amount_decimal (DECIMAL)
        - status (VARCHAR) - 'ACTIVE' for successful payments
        - created_date (DATETIME)
        - updated_date (DATETIME)
        
        Key Relationships:
        - p.subscription_id = c.subscription_id
        """
    
    def get_chart_keywords(self) -> Dict[str, List[str]]:
        """Get chart type keywords for AI guidance."""
        return {
            'pie': ['pie', 'breakdown', 'distribution', 'percentage', 'proportion', 'share'],
            'bar': ['bar', 'compare', 'ranking', 'top', 'highest', 'lowest'],
            'line': ['line', 'trend', 'over time', 'timeline', 'progression', 'growth'],
            'scatter': ['scatter', 'correlation', 'relationship', 'pattern']
        }
    
    def generate_sql(self, query: str, chart_analysis: Dict = None) -> Tuple[str, Dict]:
        """Generate SQL from natural language query."""
        if not self.model:
            return "", {"error": "AI model not available"}
        
        try:
            # Build the base prompt
            base_prompt = self._build_sql_prompt(query, chart_analysis)
            
            # Enhance prompt with learned patterns
            enhanced_prompt = self.feedback_learner.enhance_prompt(base_prompt, query)
            
            # Get similar successful queries for context
            similar_queries = self.feedback_learner.get_similar_successful_queries(query)
            if similar_queries:
                context_examples = "\n\nSIMILAR SUCCESSFUL QUERIES:\n"
                for i, sq in enumerate(similar_queries[:2], 1):
                    context_examples += f"Example {i}: '{sq.get('original_query', '')}' → {sq.get('generated_sql', '')[:100]}...\n"
                enhanced_prompt += context_examples
            
            # Generate SQL
            start_time = time.time()
            response = self.model.generate_content(enhanced_prompt)
            generation_time = time.time() - start_time
            sql_text = response.text.strip()
            
            # Extract SQL from response
            sql_query = self._extract_sql_from_response(sql_text)
            
            # Validate and fix SQL
            sql_query = self._validate_and_fix_sql(sql_query, query)
            
            return sql_query, {
                "success": True, 
                "original_response": sql_text,
                "generation_time": generation_time,
                "enhanced_prompt": enhanced_prompt
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate SQL: {e}")
            return "", {"error": str(e)}
    
    def _build_sql_prompt(self, query: str, chart_analysis: Dict = None) -> str:
        """Build the prompt for SQL generation."""
        schema = self.get_database_schema()
        chart_guidance = self._get_chart_guidance(chart_analysis) if chart_analysis else ""
        
        prompt = f"""
        You are a SQL expert. Convert the following natural language query to MySQL SQL.
        
        {schema}
        
        {chart_guidance}
        
        CRITICAL RULES:
        1. Use proper JOIN syntax: FROM subscription_payment_details p JOIN subscription_contract_v2 c ON p.subscription_id = c.subscription_id
        2. For revenue queries: Use p.trans_amount_decimal WHERE p.status = 'ACTIVE'
        3. For subscription value: Use c.renewal_amount OR c.max_amount_decimal
        4. Always use COALESCE for NULL handling: COALESCE(c.user_email, 'Not provided')
        5. Use proper date functions: DATE(), DATE_SUB(), DATE_ADD()
        6. Limit results appropriately: LIMIT 20 for large datasets
        
        Query: "{query}"
        
        Generate ONLY the SQL query, no explanations:
        """
        
        return prompt
    
    def _get_chart_guidance(self, chart_analysis: Dict) -> str:
        """Get chart-specific guidance for SQL generation."""
        chart_type = chart_analysis.get('recommended_chart_type', '')
        
        if chart_type == 'pie':
            return """
            For pie charts, structure data as:
            SELECT category, COUNT(*) as value FROM table GROUP BY category
            """
        elif chart_type == 'line':
            return """
            For line charts, include date/time columns and ORDER BY date
            """
        elif chart_type == 'bar':
            return """
            For bar charts, use categorical data with counts or sums
            """
        
        return ""
    
    def _extract_sql_from_response(self, response: str) -> str:
        """Extract SQL query from AI response."""
        # Look for SQL between backticks
        sql_match = re.search(r'```sql\s*(.*?)\s*```', response, re.DOTALL | re.IGNORECASE)
        if sql_match:
            return sql_match.group(1).strip()
        
        # Look for SQL between single backticks
        sql_match = re.search(r'`(SELECT.*?)`', response, re.DOTALL | re.IGNORECASE)
        if sql_match:
            return sql_match.group(1).strip()
        
        # Assume the entire response is SQL if it starts with SELECT
        if response.strip().upper().startswith('SELECT'):
            return response.strip()
        
        return response.strip()
    
    def _validate_and_fix_sql(self, sql_query: str, original_query: str) -> str:
        """Validate and fix common SQL issues."""
        # Fix common column name typos
        sql_query = sql_query.replace('subscription_start_date', 'subcription_start_date')
        sql_query = sql_query.replace('subscription_end_date', 'subcription_end_date')
        
        # Ensure proper spacing
        sql_query = re.sub(r'\s+', ' ', sql_query)
        
        # Fix common syntax issues
        sql_query = sql_query.replace(' ,', ',')
        sql_query = sql_query.replace(', ', ',')
        
        # Ensure proper quotes
        sql_query = self._fix_sql_quotes(sql_query)
        
        return sql_query
    
    def _fix_sql_quotes(self, sql_query: str) -> str:
        """Fix SQL quote issues."""
        # Count quotes to ensure they're balanced
        single_quotes = sql_query.count("'")
        if single_quotes % 2 != 0:
            # Add missing quote at the end
            sql_query += "'"
        
        return sql_query
    
    def execute_sql(self, sql_query: str) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """Execute SQL query and return results."""
        return self.db_manager.execute_query(sql_query)
    
    def process_query(self, query: str, chart_analysis: Dict = None) -> Dict:
        """Process a natural language query end-to-end."""
        try:
            # Generate SQL
            sql_query, generation_result = self.generate_sql(query, chart_analysis)
            
            if generation_result.get("error"):
                return {
                    "success": False,
                    "error": generation_result["error"],
                    "sql_query": None,
                    "data": None
                }
            
            # Execute SQL
            start_time = time.time()
            data, error = self.execute_sql(sql_query)
            execution_time = time.time() - start_time
            
            if error:
                return {
                    "success": False,
                    "error": error,
                    "sql_query": sql_query,
                    "data": None
                }
            
            result = {
                "success": True,
                "sql_query": sql_query,
                "data": data,
                "row_count": len(data) if data else 0,
                "generation_time": generation_result.get("generation_time", 0),
                "execution_time": execution_time,
                "enhanced_prompt": generation_result.get("enhanced_prompt", "")
            }
            
            # Store query context for potential feedback
            self._store_query_context(query, sql_query, result, chart_analysis)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Query processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "sql_query": None,
                "data": None
            }
    
    def _store_query_context(self, query: str, sql_query: str, result: Dict, chart_analysis: Dict = None):
        """Store query context for feedback processing."""
        try:
            # Store context for potential feedback collection
            context = {
                'original_query': query,
                'generated_sql': sql_query,
                'result': result,
                'chart_analysis': chart_analysis,
                'timestamp': time.time()
            }
            
            # Store in a way that can be accessed later for feedback
            if not hasattr(self, '_query_contexts'):
                self._query_contexts = {}
            
            query_id = f"{query}_{int(time.time())}"
            self._query_contexts[query_id] = context
            
            # Clean up old contexts (keep last 10)
            if len(self._query_contexts) > 10:
                oldest_keys = sorted(self._query_contexts.keys(), key=lambda k: self._query_contexts[k]['timestamp'])[:-10]
                for key in oldest_keys:
                    del self._query_contexts[key]
                    
        except Exception as e:
            logger.warning(f"⚠️ Failed to store query context: {e}")
    
    def record_feedback(self, query: str, was_helpful: bool, improvement_suggestion: str = None, user_rating: int = None):
        """Record feedback for the most recent query."""
        try:
            # Find the most recent context for this query
            matching_contexts = [
                (k, v) for k, v in self._query_contexts.items() 
                if v['original_query'] == query
            ]
            
            if not matching_contexts:
                logger.warning("⚠️ No query context found for feedback")
                return
            
            # Get the most recent context
            latest_context = max(matching_contexts, key=lambda x: x[1]['timestamp'])[1]
            
            # Record feedback
            self.feedback_learner.record_feedback(
                original_query=query,
                generated_sql=latest_context['generated_sql'],
                was_helpful=was_helpful,
                user_rating=user_rating,
                improvement_suggestion=improvement_suggestion,
                chart_type=latest_context.get('chart_analysis', {}).get('recommended_chart_type'),
                execution_time=latest_context['result'].get('execution_time'),
                result_count=latest_context['result'].get('row_count')
            )
            
            logger.info(f"📝 Feedback recorded: {'positive' if was_helpful else 'negative'}")
            
        except Exception as e:
            logger.error(f"❌ Failed to record feedback: {e}")
    
    def get_improvement_suggestions(self, query: str) -> List[str]:
        """Get improvement suggestions for a query."""
        return self.feedback_learner.get_improvement_suggestions(query)
    
    def get_accuracy_report(self) -> Dict[str, Any]:
        """Get comprehensive accuracy report."""
        return self.feedback_learner.get_accuracy_report()

# Global query processor instance
query_processor = QueryProcessor()

def get_query_processor() -> QueryProcessor:
    """Get the global query processor instance."""
    return query_processor 