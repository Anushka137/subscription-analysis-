# Feedback and Learning System

## Overview

The Feedback and Learning System is an advanced AI-powered feature that continuously improves query accuracy by learning from user feedback and past query patterns. The system uses multiple learning approaches to enhance the natural language to SQL conversion process.

## Key Features

### 1. **Multi-Layer Learning Architecture**
- **Semantic Learning**: Uses sentence transformers to find semantically similar queries
- **Pattern Recognition**: Identifies successful query patterns and common failure modes
- **Keyword Analysis**: Tracks accuracy by query keywords and provides targeted improvements
- **Temporal Learning**: Monitors accuracy trends over time

### 2. **Comprehensive Feedback Collection**
- User ratings (1-5 scale)
- Binary helpful/not helpful feedback
- Detailed improvement suggestions
- Query execution metrics (time, result count)
- Chart type preferences

### 3. **Intelligent Prompt Enhancement**
- Dynamically enhances AI prompts based on learned patterns
- Provides context from similar successful queries
- Includes specific guidance for problematic query types
- Incorporates recent improvement suggestions

### 4. **Advanced Analytics and Reporting**
- Real-time accuracy metrics
- Keyword-specific performance tracking
- Trend analysis over time
- Top improvement suggestions
- Similar query recommendations

## How It Works

### 1. **Feedback Collection Process**

```python
# Record detailed feedback
feedback_learner.record_feedback(
    original_query="Show me revenue data",
    generated_sql="SELECT SUM(amount) FROM payments",
    was_helpful=True,
    user_rating=5,
    improvement_suggestion="Include date range for better context",
    chart_type="bar",
    execution_time=0.5,
    result_count=100
)
```

### 2. **Pattern Recognition**

The system automatically:
- Extracts keywords from queries
- Calculates SQL complexity scores
- Identifies successful patterns
- Tracks failure modes
- Updates accuracy metrics

### 3. **Prompt Enhancement**

Before generating SQL, the system enhances prompts with:

```python
# Enhanced prompt includes:
- Learning-based guidance for problematic keywords
- Recent improvement suggestions
- Examples from similar successful queries
- Context-specific optimizations
```

### 4. **Continuous Improvement**

The system continuously:
- Updates accuracy metrics
- Refines keyword patterns
- Incorporates new feedback
- Adjusts learning thresholds
- Saves progress to disk

## Usage Examples

### CLI Interface

```bash
# Start interactive mode with enhanced feedback
python main.py cli

# Available commands:
# - 'report' - Show accuracy report
# - 'suggestions <query>' - Get improvement suggestions
```

### API Endpoints

```python
# Record feedback
POST /api/v1/execute
{
    "tool_name": "record_query_feedback",
    "parameters": {
        "original_question": "Show me revenue",
        "sql_query": "SELECT SUM(amount) FROM payments",
        "was_helpful": false,
        "improvement_suggestion": "Be more specific about time period",
        "user_rating": 2
    }
}

# Get improvement suggestions
POST /api/v1/execute
{
    "tool_name": "get_improvements",
    "parameters": {
        "original_question": "Show me revenue"
    }
}

# Get accuracy report
POST /api/v1/execute
{
    "tool_name": "get_accuracy_report",
    "parameters": {}
}
```

### Programmatic Usage

```python
from src.ai.feedback_learner import get_feedback_learner
from src.analytics.query_processor import get_query_processor

# Initialize components
feedback_learner = get_feedback_learner()
query_processor = get_query_processor()

# Process query with enhanced learning
result = query_processor.process_query("Show me payment trends")

# Record feedback
query_processor.record_feedback(
    query="Show me payment trends",
    was_helpful=True,
    improvement_suggestion="Include more granular time periods",
    user_rating=4
)

# Get improvement suggestions
suggestions = query_processor.get_improvement_suggestions("Show me revenue")

# Get accuracy report
report = query_processor.get_accuracy_report()
```

## Configuration

### Environment Variables

```bash
# Data directory for storing feedback data
DATA_DIR=./data

# Model settings for semantic learning
MODEL_PATH=./models/sentence-transformer
```

### Data Storage

The system stores data in:
- `data/feedback_data.json` - Detailed feedback records
- `data/query_memory.json` - Semantic learning data
- `data/query_vectors.npy` - Vector embeddings

## Accuracy Metrics

### Overall Metrics
- **Overall Accuracy**: Percentage of successful queries
- **Recent Accuracy**: Accuracy for the last 7 days
- **Total Queries**: Total number of processed queries
- **Successful Queries**: Number of helpful queries

### Keyword-Specific Metrics
- Accuracy by query keywords (revenue, subscription, payment, etc.)
- Pattern recognition for common query types
- Failure analysis for problematic keywords

### Trend Analysis
- Weekly accuracy trends
- Performance improvements over time
- Seasonal patterns in query success

## Improvement Suggestions

The system provides targeted suggestions based on:

### 1. **Query-Specific Issues**
- Vague queries that need more context
- Complex queries that should be simplified
- Missing time periods or filters

### 2. **Pattern-Based Improvements**
- Common failure modes for specific keywords
- Successful patterns from similar queries
- User preference patterns

### 3. **General Guidance**
- Overall system performance trends
- Recent accuracy improvements
- Best practices for query formulation

## Testing

Run the test script to see the system in action:

```bash
python test_feedback_system.py
```

This will:
- Record sample feedback data
- Generate accuracy reports
- Test improvement suggestions
- Demonstrate prompt enhancement

## Benefits

### 1. **Improved Accuracy**
- Learning from past mistakes
- Pattern recognition for common queries
- Context-aware prompt enhancement

### 2. **Personalized Experience**
- User-specific improvement suggestions
- Adaptive learning based on feedback
- Tailored query recommendations

### 3. **Continuous Improvement**
- Real-time learning from feedback
- Automatic pattern discovery
- Self-optimizing prompts

### 4. **Better User Experience**
- More accurate query results
- Helpful improvement suggestions
- Transparent accuracy reporting

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Query Processor │───▶│  AI Model       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Feedback      │◀───│  Feedback        │◀───│  Generated SQL  │
│   Collection    │    │  Learner         │    │  & Results      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Pattern       │    │   Accuracy       │    │   Prompt        │
│   Recognition   │    │   Metrics        │    │   Enhancement   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Future Enhancements

### Planned Features
1. **Advanced NLP**: Integration with more sophisticated language models
2. **User Profiles**: Personalized learning based on user history
3. **A/B Testing**: Automatic testing of different prompt strategies
4. **Real-time Learning**: Immediate incorporation of feedback
5. **Multi-language Support**: Learning from queries in different languages

### Performance Optimizations
1. **Vector Indexing**: Faster similarity search
2. **Caching**: Improved response times
3. **Batch Processing**: Efficient bulk feedback processing
4. **Compression**: Optimized data storage

## Troubleshooting

### Common Issues

1. **Low Accuracy**
   - Check feedback data quality
   - Review keyword patterns
   - Analyze failure modes

2. **Slow Performance**
   - Optimize vector search
   - Reduce data storage size
   - Enable caching

3. **Missing Suggestions**
   - Ensure sufficient feedback data
   - Check keyword extraction
   - Verify pattern recognition

### Debug Mode

Enable debug logging to see detailed system behavior:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Conclusion

The Feedback and Learning System provides a robust foundation for continuous improvement of query accuracy. By learning from user feedback and query patterns, the system becomes more intelligent and helpful over time, providing a better user experience and more accurate results. 