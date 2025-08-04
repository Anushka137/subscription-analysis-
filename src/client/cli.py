"""
CLI client for the subscription analytics platform.
Provides command-line interface with the same functionality as the original.
"""

import asyncio
import aiohttp
import logging
import sys
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..core.config import get_settings, validate_config
from ..analytics.query_processor import get_query_processor
from ..analytics.graph_generator import get_graph_generator
from ..ai.semantic_learner import get_semantic_learner
from ..ai.feedback_learner import get_feedback_learner

logger = logging.getLogger(__name__)

class CLIClient:
    """Command-line interface client for subscription analytics."""
    
    def __init__(self):
        self.settings = get_settings()
        self.query_processor = get_query_processor()
        self.semantic_learner = get_semantic_learner()
        self.feedback_learner = get_feedback_learner()
        self.graph_generator = get_graph_generator()
        self.session = None
        self.history = []
        self.last_query_data = None
        self.last_graph_type = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._init_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _init_session(self):
        """Initialize HTTP session."""
        try:
            connector = aiohttp.TCPConnector(ssl=False)
            self.session = aiohttp.ClientSession(
                connector=connector,
                headers={"Authorization": f"Bearer {self.settings.api.api_key}"}
            )
            logger.info("✅ HTTP session initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize HTTP session: {e}")
            self.session = None
    
    async def call_api(self, tool_name: str, parameters: Dict = None) -> Dict:
        """Call the API server with retry logic."""
        if not self.session:
            return {"success": False, "error": "No HTTP session available"}
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                url = f"{self.settings.api.subscription_api_url}/api/v1/execute"
                payload = {
                    "tool_name": tool_name,
                    "parameters": parameters or {}
                }
                
                async with self.session.post(url, json=payload, timeout=30) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"API error {response.status}: {error_text}"
                        }
                        
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    logger.warning(f"Request timeout, retrying... (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(1)
                    continue
                return {"success": False, "error": "Request timeout after multiple attempts"}
                
            except aiohttp.ClientError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Connection error, retrying... (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(1)
                    continue
                return {"success": False, "error": f"Connection failed after multiple attempts: {str(e)}"}
                
            except Exception as e:
                return {"success": False, "error": f"Request failed: {str(e)}"}
        
        return {"success": False, "error": "All retry attempts failed"}
    
    async def process_query(self, query: str) -> Dict:
        """Process a natural language query."""
        try:
            # Generate SQL using the query processor
            sql_query, generation_result = self.query_processor.generate_sql(query)
            
            if generation_result.get("error"):
                return {
                    "success": False,
                    "error": generation_result["error"],
                    "sql_query": None,
                    "data": None
                }
            
            # Determine if user wants a graph based on query keywords
            wants_graph = any(word in query.lower() for word in [
                'graph', 'chart', 'pie', 'bar', 'line', 'visual', 'plot', 'show me', 
                'visualize', 'display', 'create', 'generate', 'breakdown', 'distribution'
            ])
            
            # Also check if the query suggests data that would benefit from visualization
            if not wants_graph:
                data_suggestions = any(word in query.lower() for word in [
                    'compare', 'trend', 'over time', 'percentage', 'rate', 'success', 'failure',
                    'total', 'sum', 'count', 'average', 'mean', 'distribution'
                ])
                if data_suggestions:
                    wants_graph = True
            
            # Execute the query via API
            result = await self.call_api("execute_dynamic_sql", {
                "sql_query": sql_query,
                "wants_graph": wants_graph,
                "original_query": query
            })
            
            if result.get("success"):
                # Store data for potential alternative generation
                self.last_query_data = result.get("data", [])
                self.last_graph_type = result.get("graph_type")
                
                # Add to history
                self.history.append(query)
                
                # Record feedback for learning
                self.semantic_learner.add_query_feedback(
                    original_question=query,
                    sql_query=sql_query,
                    was_helpful=True
                )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Query processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "sql_query": None,
                "data": None
            }
    
    async def generate_alternative_graph(self, query: str) -> Optional[Dict]:
        """Generate an alternative graph when user gives negative feedback."""
        if not self.last_query_data or not self.last_graph_type:
            return None
        
        try:
            # Generate alternative graph locally
            result = self.graph_generator.generate_alternative_graph(
                self.last_query_data, 
                query, 
                self.last_graph_type
            )
            
            if result:
                # Update the last graph type
                self.last_graph_type = result.get("graph_type")
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Alternative graph generation failed: {e}")
            return None
    
    async def submit_feedback(self, query: str, was_helpful: bool, 
                            improvement_suggestion: str = None, user_rating: int = None) -> Dict:
        """Submit feedback for a query."""
        try:
            # Get the SQL query from the query processor
            sql_query, _ = self.query_processor.generate_sql(query)
            
            result = await self.call_api("record_query_feedback", {
                "original_question": query,
                "sql_query": sql_query,
                "was_helpful": was_helpful,
                "improvement_suggestion": improvement_suggestion,
                "user_rating": user_rating
            })
            
            # Also record locally using both systems
            self.semantic_learner.add_query_feedback(
                original_question=query,
                sql_query=sql_query,
                was_helpful=was_helpful,
                improvement_suggestion=improvement_suggestion
            )
            
            # Record detailed feedback
            self.feedback_learner.record_feedback(
                original_query=query,
                generated_sql=sql_query,
                was_helpful=was_helpful,
                user_rating=user_rating,
                improvement_suggestion=improvement_suggestion
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Feedback submission failed: {e}")
            return {"success": False, "error": str(e)}
    
    def display_graph(self, graph_data: Dict):
        """Display graph on screen using terminal-based image display."""
        try:
            # Try to display using different methods
            if self._try_display_with_imgcat(graph_data):
                return True
            elif self._try_display_with_terminal_image(graph_data):
                return True
            else:
                # Fallback: show file path
                file_path = graph_data.get("file_path", "")
                if file_path:
                    print(f"📊 Graph saved to: {file_path}")
                    print("💡 Tip: Open the file to view the graph")
                return False
        except Exception as e:
            logger.warning(f"Could not display graph: {e}")
            return False
    
    def _try_display_with_imgcat(self, graph_data: Dict) -> bool:
        """Try to display using imgcat (iTerm2)."""
        try:
            import subprocess
            display_data = graph_data.get("display_data", "")
            if not display_data:
                return False
            
            # Decode base64 and pipe to imgcat
            import base64
            img_bytes = base64.b64decode(display_data)
            
            result = subprocess.run(['imgcat'], input=img_bytes, capture_output=True)
            if result.returncode == 0:
                return True
            return False
        except:
            return False
    
    def _try_display_with_terminal_image(self, graph_data: Dict) -> bool:
        """Try to display using terminal-image."""
        try:
            import subprocess
            file_path = graph_data.get("file_path", "")
            if not file_path or not os.path.exists(file_path):
                return False
            
            result = subprocess.run(['terminal-image', file_path], capture_output=True)
            if result.returncode == 0:
                print(result.stdout.decode())
                return True
            return False
        except:
            return False
    
    def format_result(self, result: Dict) -> str:
        """Format query result for display."""
        if not result.get("success"):
            return f"❌ Error: {result.get('error', 'Unknown error')}"
        
        data = result.get("data", [])
        message = result.get("message", "")
        graph_data = result.get("graph_data")
        
        if not data:
            return f"ℹ️ {message}\nNo data returned."
        
        # Format the data
        output = [f"✅ {message}\n"]
        
        if isinstance(data, list) and len(data) > 0:
            # Display as table
            headers = list(data[0].keys())
            output.append(" | ".join(headers))
            output.append("-" * len(" | ".join(headers)))
            
            for row in data[:10]:  # Limit to first 10 rows
                values = [str(row.get(h, "")) for h in headers]
                output.append(" | ".join(values))
            
            if len(data) > 10:
                output.append(f"... and {len(data) - 10} more rows")
        
        elif isinstance(data, dict):
            # Display as key-value pairs
            for key, value in data.items():
                output.append(f"{key}: {value}")
        
        # Display graph if available
        if graph_data:
            output.append("\n📊 Generated Graph:")
            if self.display_graph(graph_data):
                output.append("✅ Graph displayed above")
            else:
                output.append(f"💾 Graph saved to: {graph_data.get('file_path', 'unknown')}")
        
        return "\n".join(output)
    
    async def interactive_mode(self):
        """Run interactive mode that continues until user quits."""
        print("✨ Subscription Analytics CLI ✨")
        print("=" * 50)
        print("💬 Enter questions in natural language. Type 'quit' or 'exit' to exit.")
        print("📚 Examples:")
        print("  • Show me payment success rates")
        print("  • How many new subscriptions this month?")
        print("  • Compare subscription performance for last 30 days")
        print("  • Create a pie chart of payment status")
        print("  • Show me a bar chart of subscription trends")
        print("📊 Commands:")
        print("  • 'report' - Show accuracy report")
        print("  • 'suggestions <query>' - Get improvement suggestions")
        print("=" * 50)
        
        while True:
            try:
                query = input("\n🔍 Enter your query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not query:
                    continue
                
                # Handle special commands
                if query.lower() == 'report':
                    await self.show_accuracy_report()
                    continue
                
                if query.lower().startswith('suggestions '):
                    suggestion_query = query[12:]  # Remove 'suggestions ' prefix
                    await self.show_improvement_suggestions(suggestion_query)
                    continue
                
                print("🤔 Processing your query...")
                result = await self.process_query(query)
                
                # Display result
                print("\n" + self.format_result(result))
                
                # Ask for feedback with enhanced options
                feedback = input("\n💭 Was this helpful? (y/n/skip/rate): ").strip().lower()
                
                if feedback in ['y', 'yes']:
                    await self.submit_feedback(query, True)
                    print("✅ Feedback recorded!")
                elif feedback in ['n', 'no']:
                    improvement = input("💡 How could this be improved? (optional): ").strip()
                    
                    # Try to generate alternative graph if user was unhappy
                    if self.last_query_data and self.last_graph_type:
                        print("🔄 Generating alternative visualization...")
                        alt_graph = await self.generate_alternative_graph(query)
                        if alt_graph:
                            print("\n📊 Alternative Graph:")
                            if self.display_graph(alt_graph):
                                print("✅ Alternative graph displayed above")
                            else:
                                print(f"💾 Alternative graph saved to: {alt_graph.get('file_path', 'unknown')}")
                    
                    await self.submit_feedback(query, False, improvement)
                    print("✅ Feedback recorded!")
                elif feedback in ['rate', 'r']:
                    rating = input("⭐ Rate this result (1-5): ").strip()
                    try:
                        user_rating = int(rating)
                        if 1 <= user_rating <= 5:
                            improvement = input("💡 Any improvement suggestions? (optional): ").strip()
                            await self.submit_feedback(query, True, improvement, user_rating)
                            print("✅ Feedback recorded!")
                        else:
                            print("❌ Rating must be between 1 and 5")
                    except ValueError:
                        print("❌ Invalid rating format")
                elif feedback in ['skip', 's']:
                    print("⏭️ Skipped feedback")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def show_accuracy_report(self):
        """Show comprehensive accuracy report."""
        try:
            report = self.feedback_learner.get_accuracy_report()
            
            print("\n📊 ACCURACY REPORT")
            print("=" * 50)
            
            metrics = report.get('metrics', {})
            print(f"Overall Accuracy: {metrics.get('overall_accuracy', 0):.1%}")
            print(f"Recent Accuracy (7 days): {metrics.get('recent_accuracy', 0):.1%}")
            print(f"Total Queries: {metrics.get('total_queries', 0)}")
            print(f"Successful Queries: {metrics.get('successful_queries', 0)}")
            
            # Show keyword accuracy
            keyword_acc = metrics.get('keyword_accuracy', {})
            if keyword_acc:
                print("\n📈 Keyword Accuracy:")
                for keyword, accuracy in sorted(keyword_acc.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {keyword}: {accuracy:.1%}")
            
            # Show recent trends
            trends = report.get('recent_trends', {})
            if trends and isinstance(trends, dict):
                print("\n📈 Recent Trends:")
                for week, accuracy in sorted(trends.items())[-4:]:  # Last 4 weeks
                    if isinstance(accuracy, (int, float)):
                        print(f"  Week of {week}: {accuracy:.1%}")
                    else:
                        print(f"  Week of {week}: {accuracy}")
            
            # Show top improvements
            improvements = report.get('top_improvements', [])
            if improvements:
                print("\n💡 Top Improvement Suggestions:")
                for i, improvement in enumerate(improvements[:3], 1):
                    print(f"  {i}. {improvement}")
            
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ Failed to generate accuracy report: {e}")
    
    async def show_improvement_suggestions(self, query: str):
        """Show improvement suggestions for a query."""
        try:
            suggestions = self.feedback_learner.get_improvement_suggestions(query)
            
            print(f"\n💡 IMPROVEMENT SUGGESTIONS FOR: '{query}'")
            print("=" * 50)
            
            if suggestions:
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"{i}. {suggestion}")
            else:
                print("No specific suggestions available for this query.")
                print("💡 Try being more specific or providing additional context.")
            
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ Failed to get improvement suggestions: {e}")

async def main():
    """Main CLI entry point."""
    # Validate configuration
    if not validate_config():
        print("❌ Configuration validation failed. Please check your .env file.")
        sys.exit(1)
    
    # Run CLI
    async with CLIClient() as client:
        # Check if we have arguments beyond the script name
        if len(sys.argv) > 1:
            # If first argument is "cli", skip it and use the rest
            if sys.argv[1] == "cli" and len(sys.argv) > 2:
                query = " ".join(sys.argv[2:])
                print(f"🔍 Processing: {query}")
                result = await client.process_query(query)
                print(client.format_result(result))
            elif sys.argv[1] == "cli":
                # Just "cli" with no additional arguments - run interactive mode
                await client.interactive_mode()
            else:
                # Direct arguments (not from main.py)
                query = " ".join(sys.argv[1:])
                print(f"🔍 Processing: {query}")
                result = await client.process_query(query)
                print(client.format_result(result))
        else:
            # No arguments - run interactive mode
            await client.interactive_mode()

def run_cli():
    """Run the CLI."""
    asyncio.run(main())

if __name__ == "__main__":
    run_cli() 