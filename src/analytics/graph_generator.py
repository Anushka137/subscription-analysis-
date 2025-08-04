"""
Graph generation module for creating charts and visualizations.
Restores the chart functionality from the original system.
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import matplotlib
# Set matplotlib to use non-interactive backend for server environments
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
import io
import base64

from ..core.config import get_settings

logger = logging.getLogger(__name__)

class GraphGenerator:
    """Generates various types of charts and graphs."""
    
    def __init__(self):
        self.settings = get_settings()
        self.graphs_dir = self.settings.graphs_dir
        self.supported_types = ['line', 'bar', 'horizontal_bar', 'pie', 'scatter']
        
        # Ensure graphs directory exists
        self.graphs_dir.mkdir(exist_ok=True)
    
    def can_generate_graphs(self) -> bool:
        """Check if matplotlib is available for graph generation."""
        try:
            import matplotlib
            return True
        except ImportError:
            logger.warning("⚠️ Matplotlib not available - graphs will be disabled")
            return False
    
    def generate_graph(self, data: List[Dict], query: str, graph_type: str = None) -> Optional[Dict]:
        """Generate a graph from data and return file path and display data."""
        if not self.can_generate_graphs():
            logger.warning("Cannot generate graph - matplotlib not available")
            return None
        
        if not data:
            logger.warning("No data provided for graph generation")
            return None
        
        try:
            # Determine graph type if not specified
            if not graph_type:
                graph_type = self._determine_optimal_graph_type(data, query)
            
            # Set up matplotlib with non-interactive backend
            plt.style.use('default')
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Generate graph based on type
            success = self._create_graph_by_type(ax, data, graph_type)
            if not success:
                logger.error(f"Failed to create {graph_type} chart")
                plt.close(fig)
                return None
            
            # Enhance graph appearance
            self._enhance_graph_appearance(fig, ax, data, graph_type, query)
            
            # Save graph to file
            filepath = self._save_graph_safely(fig, graph_type)
            
            # Generate base64 for display
            display_data = self._generate_display_data(fig)
            
            plt.close(fig)
            
            if filepath and filepath.exists():
                logger.info(f"✅ Generated {graph_type} chart: {filepath}")
                return {
                    "file_path": str(filepath),
                    "graph_type": graph_type,
                    "display_data": display_data
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Graph generation failed: {e}")
            return None
    
    def generate_alternative_graph(self, data: List[Dict], query: str, current_type: str) -> Optional[Dict]:
        """Generate an alternative graph type when user gives negative feedback."""
        if not self.can_generate_graphs():
            return None
        
        if not data:
            return None
        
        # Try different chart types
        alternative_types = [t for t in self.supported_types if t != current_type]
        
        for alt_type in alternative_types:
            try:
                result = self.generate_graph(data, query, alt_type)
                if result:
                    logger.info(f"🔄 Generated alternative {alt_type} chart based on feedback")
                    return result
            except Exception as e:
                logger.warning(f"Failed to generate alternative {alt_type} chart: {e}")
                continue
        
        return None
    
    def _generate_display_data(self, fig) -> str:
        """Generate base64 encoded image data for display."""
        try:
            # Save figure to bytes buffer
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            
            # Convert to base64
            img_data = base64.b64encode(buf.getvalue()).decode()
            buf.close()
            
            return img_data
        except Exception as e:
            logger.error(f"Failed to generate display data: {e}")
            return ""
    
    def _determine_optimal_graph_type(self, data: List[Dict], query: str) -> str:
        """Determine the best graph type based on data and query."""
        query_lower = query.lower()
        
        # Check for specific chart keywords
        if any(word in query_lower for word in ['pie', 'breakdown', 'distribution', 'percentage']):
            return 'pie'
        elif any(word in query_lower for word in ['bar', 'compare', 'ranking', 'top']):
            return 'bar'
        elif any(word in query_lower for word in ['line', 'trend', 'over time', 'timeline']):
            return 'line'
        elif any(word in query_lower for word in ['scatter', 'correlation']):
            return 'scatter'
        
        # Analyze data structure
        if len(data) == 0:
            return 'bar'
        
        columns = list(data[0].keys())
        
        # Check for date/time columns
        date_columns = [col for col in columns if any(word in col.lower() for word in ['date', 'time', 'created', 'updated'])]
        if date_columns:
            return 'line'
        
        # Check for categorical vs numerical data
        numerical_columns = []
        categorical_columns = []
        
        for col in columns:
            if col.lower() in ['count', 'total', 'sum', 'amount', 'value', 'rate']:
                numerical_columns.append(col)
            else:
                categorical_columns.append(col)
        
        if len(categorical_columns) >= 1 and len(numerical_columns) >= 1:
            return 'bar'
        elif len(categorical_columns) >= 2:
            return 'pie'
        else:
            return 'bar'
    
    def _create_graph_by_type(self, ax, data: List[Dict], graph_type: str) -> bool:
        """Create graph based on type."""
        try:
            if graph_type == 'pie':
                return self._create_pie_chart(ax, data)
            elif graph_type == 'bar':
                return self._create_bar_chart(ax, data)
            elif graph_type == 'horizontal_bar':
                return self._create_horizontal_bar_chart(ax, data)
            elif graph_type == 'line':
                return self._create_line_chart(ax, data)
            elif graph_type == 'scatter':
                return self._create_scatter_plot(ax, data)
            else:
                logger.warning(f"Unknown graph type: {graph_type}")
                return False
        except Exception as e:
            logger.error(f"Failed to create {graph_type} chart: {e}")
            return False
    
    def _create_pie_chart(self, ax, data: List[Dict]) -> bool:
        """Create a pie chart."""
        try:
            if len(data) == 0:
                return False
            
            # Find the best columns for pie chart
            columns = list(data[0].keys())
            label_col = None
            value_col = None
            
            # Look for common pie chart column patterns
            for col in columns:
                col_lower = col.lower()
                if any(word in col_lower for word in ['category', 'type', 'status', 'name', 'label']):
                    label_col = col
                elif any(word in col_lower for word in ['count', 'total', 'value', 'amount']):
                    value_col = col
            
            # If not found, use first two columns
            if not label_col and not value_col and len(columns) >= 2:
                label_col = columns[0]
                value_col = columns[1]
            elif not label_col:
                label_col = columns[0]
                value_col = columns[0]  # Use same column for both
            
            # Extract data
            labels = [str(row.get(label_col, f'Item {i}')) for i, row in enumerate(data)]
            values = [float(row.get(value_col, 1)) for row in data]
            
            # Create pie chart
            ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.set_title(f'Distribution by {label_col}')
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create pie chart: {e}")
            return False
    
    def _create_bar_chart(self, ax, data: List[Dict]) -> bool:
        """Create a bar chart."""
        try:
            if len(data) == 0:
                return False
            
            columns = list(data[0].keys())
            
            # For bar charts, we need to find categorical and numerical columns
            categorical_col = None
            numerical_col = None
            
            for col in columns:
                col_lower = col.lower()
                # Look for categorical columns (status, type, category, etc.)
                if any(word in col_lower for word in ['status', 'type', 'category', 'name', 'label']):
                    categorical_col = col
                # Look for numerical columns (count, total, amount, etc.)
                elif any(word in col_lower for word in ['count', 'total', 'sum', 'amount', 'value', 'rate']):
                    numerical_col = col
            
            # If we don't have both, try to use the first two columns
            if not categorical_col and not numerical_col and len(columns) >= 2:
                categorical_col = columns[0]
                numerical_col = columns[1]
            elif not categorical_col:
                categorical_col = columns[0]
                numerical_col = columns[0]
            
            # Extract data
            categories = [str(row.get(categorical_col, f'Item {i}')) for i, row in enumerate(data)]
            
            # For numerical values, try to convert to float, otherwise count occurrences
            try:
                values = [float(row.get(numerical_col, 1)) for row in data]
            except (ValueError, TypeError):
                # If conversion fails, count occurrences of each category
                from collections import Counter
                cat_counts = Counter(categories)
                categories = list(cat_counts.keys())
                values = list(cat_counts.values())
            
            # Create bar chart
            bars = ax.bar(categories, values)
            ax.set_xlabel(categorical_col)
            ax.set_ylabel(numerical_col if numerical_col != categorical_col else 'Count')
            ax.set_title(f'{numerical_col if numerical_col != categorical_col else "Count"} by {categorical_col}')
            
            # Rotate x-axis labels if too long
            if max(len(str(x)) for x in categories) > 10:
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}', ha='center', va='bottom')
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create bar chart: {e}")
            return False
    
    def _create_horizontal_bar_chart(self, ax, data: List[Dict]) -> bool:
        """Create a horizontal bar chart."""
        try:
            if len(data) == 0:
                return False
            
            columns = list(data[0].keys())
            y_col = columns[0]
            x_col = columns[1] if len(columns) > 1 else columns[0]
            
            # Extract data
            y_values = [str(row.get(y_col, f'Item {i}')) for i, row in enumerate(data)]
            x_values = [float(row.get(x_col, 1)) for row in data]
            
            # Create horizontal bar chart
            bars = ax.barh(y_values, x_values)
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f'{x_col} by {y_col}')
            
            # Add value labels on bars
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                       f'{width:.1f}', ha='left', va='center')
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create horizontal bar chart: {e}")
            return False
    
    def _create_line_chart(self, ax, data: List[Dict]) -> bool:
        """Create a line chart."""
        try:
            if len(data) == 0:
                return False
            
            columns = list(data[0].keys())
            x_col = columns[0]
            y_col = columns[1] if len(columns) > 1 else columns[0]
            
            # Extract data
            x_values = []
            y_values = []
            
            for row in data:
                x_val = row.get(x_col)
                y_val = row.get(y_col)
                
                # Try to convert to datetime if it looks like a date
                if isinstance(x_val, str) and any(word in x_col.lower() for word in ['date', 'time', 'created', 'updated']):
                    try:
                        x_val = datetime.strptime(x_val, '%Y-%m-%d')
                    except:
                        pass
                
                if x_val is not None and y_val is not None:
                    x_values.append(x_val)
                    y_values.append(float(y_val))
            
            if not x_values:
                return False
            
            # Create line chart
            ax.plot(x_values, y_values, marker='o', linewidth=2, markersize=6)
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f'{y_col} over {x_col}')
            
            # Format x-axis for dates
            if isinstance(x_values[0], datetime):
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create line chart: {e}")
            return False
    
    def _create_scatter_plot(self, ax, data: List[Dict]) -> bool:
        """Create a scatter plot."""
        try:
            if len(data) == 0:
                return False
            
            columns = list(data[0].keys())
            if len(columns) < 2:
                return False
            
            x_col = columns[0]
            y_col = columns[1]
            
            # Extract data
            x_values = [float(row.get(x_col, 0)) for row in data]
            y_values = [float(row.get(y_col, 0)) for row in data]
            
            # Create scatter plot
            ax.scatter(x_values, y_values, alpha=0.6, s=50)
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f'{y_col} vs {x_col}')
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create scatter plot: {e}")
            return False
    
    def _enhance_graph_appearance(self, fig, ax, data: List[Dict], graph_type: str, query: str):
        """Enhance the appearance of the graph."""
        try:
            # Set title
            title = f"Subscription Analytics: {query[:50]}{'...' if len(query) > 50 else ''}"
            fig.suptitle(title, fontsize=16, fontweight='bold')
            
            # Adjust layout
            plt.tight_layout()
            
            # Add grid for better readability
            if graph_type in ['line', 'bar', 'scatter']:
                ax.grid(True, alpha=0.3)
            
        except Exception as e:
            logger.warning(f"Could not enhance graph appearance: {e}")
    
    def _save_graph_safely(self, fig, graph_type: str) -> Optional[Path]:
        """Save the graph safely with a unique filename."""
        try:
            timestamp = int(datetime.now().timestamp())
            filename = f"graph_{graph_type}_{timestamp}.png"
            filepath = self.graphs_dir / filename
            
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save graph: {e}")
            return None

# Global graph generator instance
graph_generator = GraphGenerator()

def get_graph_generator() -> GraphGenerator:
    """Get the global graph generator instance."""
    return graph_generator 