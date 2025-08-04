#!/usr/bin/env python3
"""
Main entry point for the Subscription Analytics Platform.
Run the server or CLI from the terminal.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Subscription Analytics Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run the API server
  python main.py server
  
  # Run CLI in interactive mode
  python main.py cli
  
  # Run CLI with a single query
  python main.py cli "Show me payment success rates"
  
  # Run CLI with a specific query
  python main.py cli "How many new subscriptions this month?"
        """
    )
    
    parser.add_argument(
        "command",
        choices=["server", "cli"],
        help="Command to run: 'server' or 'cli'"
    )
    
    parser.add_argument(
        "query",
        nargs="*",
        help="Query to process (for CLI mode)"
    )
    
    args = parser.parse_args()
    
    if args.command == "server":
        # Run the server
        from src.api.server import run_server
        run_server()
        
    elif args.command == "cli":
        # Run the CLI
        from src.client.cli import run_cli
        
        # Only pass query arguments if they exist
        if args.query:
            sys.argv = ["cli"] + args.query
        else:
            # Clear sys.argv to ensure interactive mode
            sys.argv = ["cli"]
        
        run_cli()

if __name__ == "__main__":
    main() 