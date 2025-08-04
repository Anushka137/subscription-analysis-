#!/usr/bin/env python3
"""
Script to verify accuracy calculations and show current feedback data.
"""

import sys
import os
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ai.feedback_learner import get_feedback_learner

def verify_accuracy():
    """Verify accuracy calculations."""
    print("🔍 VERIFYING ACCURACY CALCULATIONS")
    print("=" * 50)
    
    feedback_learner = get_feedback_learner()
    
    # Show raw feedback data
    print("\n📝 RAW FEEDBACK DATA:")
    print("-" * 30)
    for i, feedback in enumerate(feedback_learner.feedback_data, 1):
        print(f"{i}. Query: '{feedback['original_query']}'")
        print(f"   Helpful: {feedback['was_helpful']}")
        print(f"   Rating: {feedback.get('user_rating', 'N/A')}")
        print(f"   Keywords: {feedback.get('keywords', [])}")
        print()
    
    # Show query patterns
    print("\n📊 QUERY PATTERNS:")
    print("-" * 30)
    for keyword, pattern in feedback_learner.query_patterns.items():
        print(f"Keyword: '{keyword}'")
        print(f"  Total queries: {pattern['total_queries']}")
        print(f"  Successful queries: {pattern['successful_queries']}")
        print(f"  Accuracy: {pattern['successful_queries'] / pattern['total_queries']:.1%}")
        print()
    
    # Show accuracy metrics
    print("\n📈 ACCURACY METRICS:")
    print("-" * 30)
    metrics = feedback_learner.accuracy_metrics
    print(f"Overall Accuracy: {metrics.get('overall_accuracy', 0):.1%}")
    print(f"Total Queries: {metrics.get('total_queries', 0)}")
    print(f"Successful Queries: {metrics.get('successful_queries', 0)}")
    
    # Manual calculation verification
    print("\n🔢 MANUAL CALCULATION VERIFICATION:")
    print("-" * 30)
    total = len(feedback_learner.feedback_data)
    successful = sum(1 for f in feedback_learner.feedback_data if f.get('was_helpful', True))
    manual_accuracy = successful / total if total > 0 else 0
    print(f"Manual calculation: {successful}/{total} = {manual_accuracy:.1%}")
    print(f"System calculation: {metrics.get('overall_accuracy', 0):.1%}")
    print(f"Match: {'✅' if abs(manual_accuracy - metrics.get('overall_accuracy', 0)) < 0.001 else '❌'}")

if __name__ == "__main__":
    verify_accuracy() 