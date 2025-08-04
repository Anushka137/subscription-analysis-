"""
API routes for the subscription analytics platform.
Handles HTTP endpoints with proper separation of concerns.
"""

import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, Header, status
from pydantic import BaseModel, Field

from ..core.config import get_settings
from ..analytics.query_processor import get_query_processor
from ..analytics.graph_generator import get_graph_generator
from ..ai.semantic_learner import get_semantic_learner
from ..ai.feedback_learner import get_feedback_learner
from ..database.connection import get_db_manager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Pydantic models
class ToolRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict = Field(default_factory=dict, description="Parameters for the tool")

class ToolResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None
    graph_data: Optional[Dict] = None
    graph_type: Optional[str] = None

class ToolInfo(BaseModel):
    name: str
    description: str
    parameters: Dict

# Dependency for API key validation
def verify_api_key(authorization: str = Header(None)):
    """Verify API key from Authorization header."""
    settings = get_settings()
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
    
    # Extract API key from Bearer token
    if authorization.startswith("Bearer "):
        api_key = authorization[7:]  # Remove "Bearer " prefix
    else:
        api_key = authorization
    
    if api_key != settings.api.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return api_key

# Health check endpoint
@router.get("/health")
def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        db_manager = get_db_manager()
        db_healthy = db_manager.test_connection()
        
        # Test AI model
        query_processor = get_query_processor()
        ai_healthy = query_processor.model is not None
        
        status_info = {
            "status": "healthy" if db_healthy and ai_healthy else "degraded",
            "database": "connected" if db_healthy else "disconnected",
            "ai_model": "loaded" if ai_healthy else "not_loaded",
            "version": "2.0.0"
        }
        
        if status_info["status"] == "healthy":
            return status_info
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=status_info
            )
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unhealthy", "error": str(e)}
        )

# List available tools
@router.get("/tools", response_model=List[ToolInfo], dependencies=[Depends(verify_api_key)])
def list_tools():
    """List all available tools."""
    tools = [
        ToolInfo(
            name="execute_dynamic_sql",
            description="Execute dynamic SQL queries with natural language processing and graph generation",
            parameters={
                "sql_query": "string",
                "wants_graph": "boolean (optional)",
                "graph_type": "string (optional) - pie, bar, line, scatter"
            }
        ),
        ToolInfo(
            name="record_query_feedback",
            description="Record feedback on query results for learning",
            parameters={
                "original_question": "string",
                "sql_query": "string",
                "was_helpful": "boolean",
                "improvement_suggestion": "string (optional)",
                "user_rating": "integer (optional, 1-5)"
            }
        ),
        ToolInfo(
            name="get_improvement_suggestions",
            description="Get improvement suggestions based on similar queries",
            parameters={
                "original_question": "string"
            }
        ),
        ToolInfo(
            name="get_similar_queries",
            description="Get similar successful queries from memory",
            parameters={
                "original_question": "string"
            }
        ),
        ToolInfo(
            name="get_accuracy_report",
            description="Get comprehensive accuracy report and learning metrics",
            parameters={}
        ),
        ToolInfo(
            name="get_database_status",
            description="Get database status and basic metrics",
            parameters={}
        ),
        ToolInfo(
            name="get_subscriptions_summary",
            description="Get summary of subscription data",
            parameters={
                "days": "integer (optional, default: 30)"
            }
        ),
        ToolInfo(
            name="get_payment_success_rates",
            description="Get payment success rate analytics",
            parameters={
                "days": "integer (optional, default: 30)"
            }
        )
    ]
    
    return tools

# Execute tool endpoint
@router.post("/execute", response_model=ToolResponse, dependencies=[Depends(verify_api_key)])
def execute_tool(request: ToolRequest):
    """Execute a specific tool with given parameters."""
    try:
        tool_name = request.tool_name
        parameters = request.parameters
        
        logger.info(f"🔧 Executing tool: {tool_name}")
        
        # Route to appropriate handler
        if tool_name == "execute_dynamic_sql":
            result = _handle_execute_dynamic_sql(parameters)
        elif tool_name == "record_query_feedback":
            result = _handle_record_feedback(parameters)
        elif tool_name == "get_improvement_suggestions":
            result = _handle_get_improvements(parameters)
        elif tool_name == "get_similar_queries":
            result = _handle_get_similar_queries(parameters)
        elif tool_name == "get_accuracy_report":
            result = _handle_get_accuracy_report(parameters)
        elif tool_name == "get_database_status":
            result = _handle_get_database_status()
        elif tool_name == "get_subscriptions_summary":
            result = _handle_get_subscriptions_summary(parameters)
        elif tool_name == "get_payment_success_rates":
            result = _handle_get_payment_success_rates(parameters)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown tool: {tool_name}"
            )
        
        return ToolResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Tool execution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tool execution failed: {str(e)}"
        )

# Tool handlers
def _handle_execute_dynamic_sql(parameters: Dict) -> Dict:
    """Handle dynamic SQL execution with graph generation."""
    sql_query = parameters.get("sql_query", "")
    wants_graph = parameters.get("wants_graph", False)
    graph_type = parameters.get("graph_type")
    original_query = parameters.get("original_query", "")
    
    if not sql_query:
        return {
            "success": False,
            "error": "SQL query is required"
        }
    
    query_processor = get_query_processor()
    data, error = query_processor.execute_sql(sql_query)
    
    if error:
        return {
            "success": False,
            "error": error,
            "data": None
        }
    
    result = {
        "success": True,
        "data": data,
        "message": f"Query executed successfully, returned {len(data) if data else 0} rows"
    }
    
    # Generate graph if requested and data is available
    if wants_graph and data and len(data) > 0:
        graph_generator = get_graph_generator()
        graph_result = graph_generator.generate_graph(data, original_query or sql_query, graph_type)
        if graph_result:
            result["graph_data"] = graph_result
            result["graph_type"] = graph_result.get("graph_type")
            result["message"] += f" and generated {graph_result.get('graph_type', 'graph')}"
    
    return result

def _handle_record_feedback(parameters: Dict) -> Dict:
    """Handle feedback recording."""
    original_question = parameters.get("original_question", "")
    sql_query = parameters.get("sql_query", "")
    was_helpful = parameters.get("was_helpful", True)
    improvement_suggestion = parameters.get("improvement_suggestion")
    user_rating = parameters.get("user_rating")
    
    if not original_question or not sql_query:
        return {
            "success": False,
            "error": "Original question and SQL query are required"
        }
    
    # Record feedback using both systems
    semantic_learner = get_semantic_learner()
    feedback_learner = get_feedback_learner()
    
    semantic_learner.add_query_feedback(
        original_question=original_question,
        sql_query=sql_query,
        was_helpful=was_helpful,
        improvement_suggestion=improvement_suggestion
    )
    
    feedback_learner.record_feedback(
        original_query=original_question,
        generated_sql=sql_query,
        was_helpful=was_helpful,
        user_rating=user_rating,
        improvement_suggestion=improvement_suggestion
    )
    
    return {
        "success": True,
        "message": "Feedback recorded successfully"
    }

def _handle_get_improvements(parameters: Dict) -> Dict:
    """Handle getting improvement suggestions."""
    original_question = parameters.get("original_question", "")
    
    if not original_question:
        return {
            "success": False,
            "error": "Original question is required"
        }
    
    # Get suggestions from both systems
    semantic_learner = get_semantic_learner()
    feedback_learner = get_feedback_learner()
    
    semantic_suggestions = semantic_learner.get_improvement_suggestions(original_question)
    feedback_suggestions = feedback_learner.get_improvement_suggestions(original_question)
    
    # Combine and deduplicate suggestions
    all_suggestions = list(set(semantic_suggestions + feedback_suggestions))
    
    return {
        "success": True,
        "data": all_suggestions,
        "message": f"Found {len(all_suggestions)} improvement suggestions",
        "semantic_suggestions": semantic_suggestions,
        "feedback_suggestions": feedback_suggestions
    }

def _handle_get_similar_queries(parameters: Dict) -> Dict:
    """Handle getting similar queries."""
    original_question = parameters.get("original_question", "")
    
    if not original_question:
        return {
            "success": False,
            "error": "Original question is required"
        }
    
    semantic_learner = get_semantic_learner()
    feedback_learner = get_feedback_learner()
    
    semantic_similar = semantic_learner.get_similar_queries(original_question)
    feedback_similar = feedback_learner.get_similar_successful_queries(original_question)
    
    return {
        "success": True,
        "data": {
            "semantic_similar": semantic_similar,
            "feedback_similar": feedback_similar
        },
        "message": f"Found {len(semantic_similar)} semantic similar queries and {len(feedback_similar)} feedback similar queries"
    }

def _handle_get_accuracy_report(parameters: Dict) -> Dict:
    """Handle getting accuracy report."""
    feedback_learner = get_feedback_learner()
    report = feedback_learner.get_accuracy_report()
    
    return {
        "success": True,
        "data": report,
        "message": "Accuracy report generated successfully"
    }

def _handle_get_database_status() -> Dict:
    """Handle getting database status."""
    db_manager = get_db_manager()
    
    # Test connection
    is_connected = db_manager.test_connection()
    
    if not is_connected:
        return {
            "success": False,
            "error": "Database connection failed"
        }
    
    # Get basic metrics
    try:
        # Get table counts
        tables_query = "SHOW TABLES"
        tables, _ = db_manager.execute_query(tables_query)
        
        table_counts = {}
        for table in tables:
            table_name = list(table.values())[0]
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            count_result, _ = db_manager.execute_query(count_query)
            if count_result:
                table_counts[table_name] = count_result[0]['count']
        
        return {
            "success": True,
            "data": {
                "status": "connected",
                "tables": table_counts,
                "total_records": sum(table_counts.values())
            },
            "message": "Database is healthy"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get database status: {str(e)}"
        }

def _handle_get_subscriptions_summary(parameters: Dict) -> Dict:
    """Handle getting subscriptions summary."""
    days = parameters.get("days", 30)
    
    query = f"""
    SELECT 
        COUNT(*) as total_subscriptions,
        COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) as active_subscriptions,
        SUM(renewal_amount) as total_value
    FROM subscription_contract_v2 
    WHERE subcription_start_date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
    """
    
    db_manager = get_db_manager()
    data, error = db_manager.execute_query(query)
    
    if error:
        return {
            "success": False,
            "error": error
        }
    
    return {
        "success": True,
        "data": data[0] if data else {},
        "message": f"Subscription summary for last {days} days"
    }

def _handle_get_payment_success_rates(parameters: Dict) -> Dict:
    """Handle getting payment success rates."""
    days = parameters.get("days", 30)
    
    query = f"""
    SELECT 
        COUNT(*) as total_payments,
        COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) as successful_payments,
        ROUND(COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) * 100.0 / COUNT(*), 2) as success_rate
    FROM subscription_payment_details 
    WHERE created_date >= DATE_SUB(NOW(), INTERVAL {days} DAY)
    """
    
    db_manager = get_db_manager()
    data, error = db_manager.execute_query(query)
    
    if error:
        return {
            "success": False,
            "error": error
        }
    
    return {
        "success": True,
        "data": data[0] if data else {},
        "message": f"Payment success rates for last {days} days"
    } 