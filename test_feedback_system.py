#!/usr/bin/env python3
"""
Test script for the feedback and learning system.
Demonstrates how the system learns from feedback and improves over time.
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ai.feedback_learner import get_feedback_learner
from src.analytics.query_processor import get_query_processor

async def test_feedback_system():
    """Test the feedback and learning system."""
    print("🧪 Testing Feedback and Learning System")
    print("=" * 50)
    
    # Initialize components
    feedback_learner = get_feedback_learner()
    query_processor = get_query_processor()
    
    # Test queries with different levels of success
    test_queries = [
        {
            "query": "Show me total revenue for this month",
            "was_helpful": True,
            "rating": 5,
            "suggestion": None
        },
        {
            "query": "How many subscriptions are active",
            "was_helpful": True,
            "rating": 4,
            "suggestion": None
        },
        {
            "query": "revenue",
            "was_helpful": False,
            "rating": 2,
            "suggestion": "Please be more specific about what revenue data you want to see"
        },
        {
            "query": "Show me payment success rates over time",
            "was_helpful": True,
            "rating": 5,
            "suggestion": None
        },
        {
            "query": "subscriptions",
            "was_helpful": False,
            "rating": 1,
            "suggestion": "Please specify what subscription information you need"
        }
    ]
    
    print("📝 Recording test feedback...")
    
    # Record feedback for each test query
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{i}. Recording feedback for: '{test_case['query']}'")
        
        # Generate a mock SQL query
        mock_sql = f"SELECT * FROM test_table WHERE query = '{test_case['query']}'"
        
        # Record feedback
        feedback_learner.record_feedback(
            original_query=test_case['query'],
            generated_sql=mock_sql,
            was_helpful=test_case['was_helpful'],
            user_rating=test_case['rating'],
            improvement_suggestion=test_case['suggestion']
        )
        
        print(f"   ✅ Feedback recorded (Rating: {test_case['rating']}/5)")
    
    print("\n📊 Generating accuracy report...")
    
    # Get accuracy report
    report = feedback_learner.get_accuracy_report()
    
    print("\n📈 ACCURACY METRICS:")
    metrics = report.get('metrics', {})
    print(f"Overall Accuracy: {metrics.get('overall_accuracy', 0):.1%}")
    print(f"Total Queries: {metrics.get('total_queries', 0)}")
    print(f"Successful Queries: {metrics.get('successful_queries', 0)}")
    
    # Show keyword accuracy
    keyword_acc = metrics.get('keyword_accuracy', {})
    if keyword_acc:
        print("\n📊 Keyword Accuracy:")
        for keyword, accuracy in sorted(keyword_acc.items(), key=lambda x: x[1], reverse=True):
            print(f"  {keyword}: {accuracy:.1%}")
    
    # Test improvement suggestions
    print("\n💡 Testing improvement suggestions...")
    
    test_queries_for_suggestions = [
        "revenue",
        "subscriptions",
        "Show me payment data"
    ]
    
    for query in test_queries_for_suggestions:
        suggestions = feedback_learner.get_improvement_suggestions(query)
        print(f"\nSuggestions for '{query}':")
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
        else:
            print("  No specific suggestions available")
    
    # Test similar queries
    print("\n🔍 Testing similar query retrieval...")
    
    similar_queries = feedback_learner.get_similar_successful_queries("Show me revenue data")
    print(f"Found {len(similar_queries)} similar successful queries")
    
    for i, sq in enumerate(similar_queries[:2], 1):
        print(f"  {i}. '{sq.get('original_query', '')}' (Rating: {sq.get('user_rating', 'N/A')})")
    
    print("\n✅ Feedback system test completed!")
    print("=" * 50)

def test_prompt_enhancement():
    """Test prompt enhancement functionality."""
    print("\n🧪 Testing Prompt Enhancement")
    print("=" * 30)
    
    feedback_learner = get_feedback_learner()
    
    base_prompt = """
    You are a SQL expert. Convert the following natural language query to MySQL SQL.
    
    Database Schema:
    - subscription_contract_v2 (c)
    - subscription_payment_details (p)
    
    Query: "{query}"
    
    Generate ONLY the SQL query, no explanations:
    """
    
    test_queries = [
        "revenue",
        "Show me total revenue for this month",
        "subscriptions"
    ]
    
    for query in test_queries:
        print(f"\nEnhancing prompt for: '{query}'")
        enhanced_prompt = feedback_learner.enhance_prompt(base_prompt, query)
        
        # Show the difference
        print("Enhanced sections:")
        if "LEARNING-BASED GUIDANCE:" in enhanced_prompt:
            guidance_start = enhanced_prompt.find("LEARNING-BASED GUIDANCE:")
            guidance_end = enhanced_prompt.find("\n\n", guidance_start)
            if guidance_end == -1:
                guidance_end = len(enhanced_prompt)
            guidance = enhanced_prompt[guidance_start:guidance_end]
            print(f"  {guidance}")
        
        if "RECENT IMPROVEMENTS:" in enhanced_prompt:
            improvements_start = enhanced_prompt.find("RECENT IMPROVEMENTS:")
            improvements_end = enhanced_prompt.find("\n\n", improvements_start)
            if improvements_end == -1:
                improvements_end = len(enhanced_prompt)
            improvements = enhanced_prompt[improvements_start:improvements_end]
            print(f"  {improvements}")
    
    print("\n✅ Prompt enhancement test completed!")

if __name__ == "__main__":
    print("🚀 Starting Feedback System Tests")
    print("=" * 50)
    
    # Run tests
    asyncio.run(test_feedback_system())
    test_prompt_enhancement()
    
    print("\n🎉 All tests completed successfully!")
    print("\n💡 The system is now learning from feedback and will provide:")
    print("   • More accurate query generation")
    print("   • Personalized improvement suggestions")
    print("   • Enhanced prompts based on past success patterns")
    print("   • Detailed accuracy metrics and trends") 