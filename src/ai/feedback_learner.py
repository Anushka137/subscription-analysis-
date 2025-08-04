"""
Advanced feedback and learning system for query improvement.
Handles feedback collection, pattern recognition, and continuous learning.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
import numpy as np
from collections import defaultdict, Counter
import re

from ..core.config import get_settings
from .semantic_learner import get_semantic_learner

logger = logging.getLogger(__name__)

class FeedbackLearner:
    """Advanced feedback and learning system for query improvement."""
    
    def __init__(self):
        self.settings = get_settings()
        self.semantic_learner = get_semantic_learner()
        self.feedback_data: List[Dict] = []
        self.query_patterns: Dict[str, Dict] = {}
        self.accuracy_metrics: Dict[str, float] = {}
        self.improvement_suggestions: List[str] = []
        self._load_feedback_data()
        self._analyze_patterns()
    
    def _load_feedback_data(self):
        """Load existing feedback data."""
        try:
            feedback_file = self.settings.data_dir / "feedback_data.json"
            if feedback_file.exists():
                with open(feedback_file, 'r') as f:
                    self.feedback_data = json.load(f)
                logger.info(f"📊 Loaded {len(self.feedback_data)} feedback records")
            else:
                logger.info("📊 Starting with empty feedback data")
        except Exception as e:
            logger.warning(f"⚠️ Could not load feedback data: {e}")
            self.feedback_data = []
    
    def _save_feedback_data(self):
        """Save feedback data to disk."""
        try:
            feedback_file = self.settings.data_dir / "feedback_data.json"
            with open(feedback_file, 'w') as f:
                json.dump(self.feedback_data, f, indent=2)
            logger.info("💾 Feedback data saved successfully")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save feedback data: {e}")
    
    def record_feedback(self, 
                       original_query: str,
                       generated_sql: str,
                       was_helpful: bool,
                       user_rating: int = None,
                       improvement_suggestion: str = None,
                       actual_sql: str = None,
                       chart_type: str = None,
                       execution_time: float = None,
                       result_count: int = None) -> None:
        """Record detailed feedback for learning."""
        
        feedback_record = {
            'id': len(self.feedback_data) + 1,
            'timestamp': datetime.now().isoformat(),
            'original_query': original_query,
            'generated_sql': generated_sql,
            'was_helpful': was_helpful,
            'user_rating': user_rating,
            'improvement_suggestion': improvement_suggestion,
            'actual_sql': actual_sql,
            'chart_type': chart_type,
            'execution_time': execution_time,
            'result_count': result_count,
            'query_length': len(original_query),
            'sql_complexity': self._calculate_sql_complexity(generated_sql),
            'keywords': self._extract_keywords(original_query)
        }
        
        self.feedback_data.append(feedback_record)
        
        # Also add to semantic learner
        self.semantic_learner.add_query_feedback(
            original_question=original_query,
            sql_query=generated_sql,
            was_helpful=was_helpful,
            improvement_suggestion=improvement_suggestion,
            chart_type=chart_type
        )
        
        # Update patterns and metrics
        self._update_patterns(feedback_record)
        self._update_accuracy_metrics()
        
        # Save to disk
        self._save_feedback_data()
        
        logger.info(f"📝 Recorded {'positive' if was_helpful else 'negative'} feedback")
    
    def _calculate_sql_complexity(self, sql: str) -> int:
        """Calculate SQL complexity score."""
        complexity = 0
        sql_upper = sql.upper()
        
        # Count different SQL components
        complexity += sql_upper.count('JOIN') * 2
        complexity += sql_upper.count('WHERE') * 1
        complexity += sql_upper.count('GROUP BY') * 2
        complexity += sql_upper.count('ORDER BY') * 1
        complexity += sql_upper.count('HAVING') * 2
        complexity += sql_upper.count('SUBQUERY') * 3
        complexity += sql_upper.count('UNION') * 3
        complexity += sql_upper.count('CASE') * 2
        
        return complexity
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query."""
        # Common analytics keywords
        keywords = [
            'revenue', 'payment', 'subscription', 'user', 'customer',
            'amount', 'count', 'sum', 'average', 'total', 'monthly',
            'yearly', 'trend', 'growth', 'top', 'highest', 'lowest',
            'percentage', 'distribution', 'breakdown', 'compare'
        ]
        
        found_keywords = []
        query_lower = query.lower()
        for keyword in keywords:
            if keyword in query_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _update_patterns(self, feedback_record: Dict):
        """Update query patterns based on feedback."""
        keywords = feedback_record.get('keywords', [])
        was_helpful = feedback_record.get('was_helpful', True)
        
        for keyword in keywords:
            if keyword not in self.query_patterns:
                self.query_patterns[keyword] = {
                    'total_queries': 0,
                    'successful_queries': 0,
                    'common_sql_patterns': [],
                    'improvement_suggestions': []
                }
            
            pattern = self.query_patterns[keyword]
            pattern['total_queries'] += 1
            
            if was_helpful:
                pattern['successful_queries'] += 1
            
            # Store SQL pattern
            sql = feedback_record.get('generated_sql', '')
            if sql:
                pattern['common_sql_patterns'].append(sql[:100])  # First 100 chars
            
            # Store improvement suggestions
            suggestion = feedback_record.get('improvement_suggestion')
            if suggestion:
                pattern['improvement_suggestions'].append(suggestion)
    
    def _update_accuracy_metrics(self):
        """Update accuracy metrics."""
        if not self.feedback_data:
            return
        
        total_queries = len(self.feedback_data)
        successful_queries = sum(1 for f in self.feedback_data if f.get('was_helpful', True))
        
        self.accuracy_metrics = {
            'overall_accuracy': successful_queries / total_queries if total_queries > 0 else 0,
            'total_queries': total_queries,
            'successful_queries': successful_queries,
            'recent_accuracy': self._calculate_recent_accuracy(),
            'keyword_accuracy': self._calculate_keyword_accuracy()
        }
    
    def _calculate_recent_accuracy(self, days: int = 7) -> float:
        """Calculate accuracy for recent queries."""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_feedback = [
            f for f in self.feedback_data 
            if datetime.fromisoformat(f['timestamp']) > cutoff_date
        ]
        
        if not recent_feedback:
            return 0.0
        
        successful = sum(1 for f in recent_feedback if f.get('was_helpful', True))
        return successful / len(recent_feedback)
    
    def _calculate_keyword_accuracy(self) -> Dict[str, float]:
        """Calculate accuracy by keyword."""
        keyword_accuracy = {}
        
        for keyword, pattern in self.query_patterns.items():
            if pattern['total_queries'] > 0:
                accuracy = pattern['successful_queries'] / pattern['total_queries']
                keyword_accuracy[keyword] = accuracy
        
        return keyword_accuracy
    
    def get_improvement_suggestions(self, query: str) -> List[str]:
        """Get improvement suggestions based on similar past queries."""
        suggestions = []
        
        # Get suggestions from semantic learner
        semantic_suggestions = self.semantic_learner.get_improvement_suggestions(query)
        suggestions.extend(semantic_suggestions)
        
        # Get suggestions from keyword patterns
        keywords = self._extract_keywords(query)
        for keyword in keywords:
            if keyword in self.query_patterns:
                pattern = self.query_patterns[keyword]
                if pattern['total_queries'] > 3:  # Only if we have enough data
                    accuracy = pattern['successful_queries'] / pattern['total_queries']
                    if accuracy < 0.7:  # Low accuracy keyword
                        suggestions.extend(pattern['improvement_suggestions'][-3:])  # Last 3 suggestions
        
        # Get general improvement suggestions
        suggestions.extend(self._get_general_improvements())
        
        return list(set(suggestions))  # Remove duplicates
    
    def _get_general_improvements(self) -> List[str]:
        """Get general improvement suggestions based on overall patterns."""
        improvements = []
        
        if self.accuracy_metrics.get('overall_accuracy', 0) < 0.8:
            improvements.append("Consider providing more specific details in your query")
        
        if self.accuracy_metrics.get('recent_accuracy', 0) < 0.7:
            improvements.append("Recent queries show lower accuracy - try being more explicit")
        
        # Check for common failure patterns
        failed_queries = [f for f in self.feedback_data if not f.get('was_helpful', True)]
        if failed_queries:
            common_issues = self._analyze_failure_patterns(failed_queries)
            improvements.extend(common_issues)
        
        return improvements
    
    def _analyze_failure_patterns(self, failed_queries: List[Dict]) -> List[str]:
        """Analyze patterns in failed queries."""
        issues = []
        
        # Check for vague queries
        vague_count = sum(1 for f in failed_queries if f.get('query_length', 0) < 20)
        if vague_count > len(failed_queries) * 0.3:
            issues.append("Queries that are too short or vague often fail - try being more specific")
        
        # Check for complex queries
        complex_count = sum(1 for f in failed_queries if f.get('sql_complexity', 0) > 5)
        if complex_count > len(failed_queries) * 0.4:
            issues.append("Complex queries may need to be broken down into simpler parts")
        
        return issues
    
    def enhance_prompt(self, base_prompt: str, query: str) -> str:
        """Enhance the base prompt with learned patterns."""
        enhanced_prompt = base_prompt
        
        # Add keyword-specific guidance
        keywords = self._extract_keywords(query)
        keyword_guidance = []
        
        for keyword in keywords:
            if keyword in self.query_patterns:
                pattern = self.query_patterns[keyword]
                if pattern['total_queries'] > 2:
                    accuracy = pattern['successful_queries'] / pattern['total_queries']
                    if accuracy < 0.6:
                        keyword_guidance.append(f"Note: '{keyword}' queries often need more specific context")
        
        if keyword_guidance:
            enhanced_prompt += "\n\nLEARNING-BASED GUIDANCE:\n" + "\n".join(keyword_guidance)
        
        # Add recent improvement suggestions
        recent_suggestions = self.get_improvement_suggestions(query)
        if recent_suggestions:
            enhanced_prompt += f"\n\nRECENT IMPROVEMENTS:\n" + "\n".join(recent_suggestions[:2])
        
        return enhanced_prompt
    
    def get_similar_successful_queries(self, query: str, limit: int = 3) -> List[Dict]:
        """Get similar successful queries for reference."""
        successful_queries = [
            f for f in self.feedback_data 
            if f.get('was_helpful', True) and f.get('generated_sql')
        ]
        
        # Use semantic similarity if available
        if self.semantic_learner.model:
            similar = self.semantic_learner.get_similar_queries(query, threshold=0.7)
            return [q for q in similar if q.get('was_helpful', True)][:limit]
        
        # Fallback to keyword matching
        query_keywords = set(self._extract_keywords(query))
        scored_queries = []
        
        for sq in successful_queries:
            sq_keywords = set(sq.get('keywords', []))
            overlap = len(query_keywords & sq_keywords)
            if overlap > 0:
                scored_queries.append((overlap, sq))
        
        scored_queries.sort(reverse=True)
        return [sq for _, sq in scored_queries[:limit]]
    
    def get_accuracy_report(self) -> Dict[str, Any]:
        """Get comprehensive accuracy report."""
        return {
            'metrics': self.accuracy_metrics,
            'patterns': {
                keyword: {
                    'accuracy': pattern['successful_queries'] / pattern['total_queries'] if pattern['total_queries'] > 0 else 0,
                    'total_queries': pattern['total_queries']
                }
                for keyword, pattern in self.query_patterns.items()
            },
            'recent_trends': self._get_recent_trends(),
            'top_improvements': self._get_top_improvements()
        }
    
    def _get_recent_trends(self) -> Dict[str, Any]:
        """Get recent accuracy trends."""
        if len(self.feedback_data) < 10:
            return {'message': 'Insufficient data for trend analysis'}
        
        # Group by week
        weekly_data = defaultdict(list)
        for feedback in self.feedback_data[-20:]:  # Last 20 queries
            date = datetime.fromisoformat(feedback['timestamp']).date()
            week = date - timedelta(days=date.weekday())
            weekly_data[str(week)].append(feedback)
        
        trends = {}
        for week, data in sorted(weekly_data.items()):
            successful = sum(1 for f in data if f.get('was_helpful', True))
            trends[week] = successful / len(data) if data else 0
        
        return trends
    
    def _get_top_improvements(self) -> List[str]:
        """Get top improvement suggestions."""
        all_suggestions = []
        for feedback in self.feedback_data:
            suggestion = feedback.get('improvement_suggestion')
            if suggestion:
                all_suggestions.append(suggestion)
        
        # Count and return most common
        suggestion_counts = Counter(all_suggestions)
        return [suggestion for suggestion, count in suggestion_counts.most_common(5)]
    
    def _analyze_patterns(self):
        """Analyze existing patterns from loaded data."""
        for feedback in self.feedback_data:
            self._update_patterns(feedback)
        self._update_accuracy_metrics()

# Global feedback learner instance
feedback_learner = FeedbackLearner()

def get_feedback_learner() -> FeedbackLearner:
    """Get the global feedback learner instance."""
    return feedback_learner 