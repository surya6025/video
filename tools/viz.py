"""
Visualization Tool for JarvisX
Advanced charting and plotting capabilities
"""

import os
import json
import base64
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import numpy as np
import pandas as pd
from loguru import logger
from core.io import FileManager

# Set matplotlib backend for non-interactive use
plt.switch_backend('Agg')

class VisualizationTool:
    """Advanced visualization and charting tool"""
    
    def __init__(self, temp_dir: str):
        self.temp_dir = Path(temp_dir)
        self.file_manager = FileManager(str(self.temp_dir))
        
        # Set default style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Configure matplotlib
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
    
    def create_line_chart(self, data: Dict, title: str = "", save_path: str = None) -> str:
        """Create a line chart"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            x_values = data.get('x', [])
            y_values = data.get('y', [])
            labels = data.get('labels', [])
            colors = data.get('colors', None)
            
            if isinstance(y_values[0], list):
                # Multiple lines
                for i, y_data in enumerate(y_values):
                    label = labels[i] if i < len(labels) else f"Series {i+1}"
                    color = colors[i] if colors and i < len(colors) else None
                    ax.plot(x_values, y_data, label=label, color=color, linewidth=2, marker='o')
            else:
                # Single line
                ax.plot(x_values, y_values, linewidth=2, marker='o', color=colors[0] if colors else None)
            
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel(data.get('xlabel', 'X Axis'))
            ax.set_ylabel(data.get('ylabel', 'Y Axis'))
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Save or return base64
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close()
                return save_path
            else:
                return self._fig_to_base64(fig)
                
        except Exception as e:
            logger.error(f"Error creating line chart: {e}")
            return ""
    
    def create_bar_chart(self, data: Dict, title: str = "", save_path: str = None) -> str:
        """Create a bar chart"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            x_values = data.get('x', [])
            y_values = data.get('y', [])
            colors = data.get('colors', None)
            
            bars = ax.bar(x_values, y_values, color=colors, alpha=0.7, edgecolor='black')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'{height:.1f}', ha='center', va='bottom')
            
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel(data.get('xlabel', 'Categories'))
            ax.set_ylabel(data.get('ylabel', 'Values'))
            ax.grid(True, alpha=0.3, axis='y')
            
            # Rotate x-axis labels if needed
            if len(x_values) > 8:
                plt.xticks(rotation=45, ha='right')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close()
                return save_path
            else:
                return self._fig_to_base64(fig)
                
        except Exception as e:
            logger.error(f"Error creating bar chart: {e}")
            return ""
    
    def create_scatter_plot(self, data: Dict, title: str = "", save_path: str = None) -> str:
        """Create a scatter plot"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            x_values = data.get('x', [])
            y_values = data.get('y', [])
            colors = data.get('colors', None)
            sizes = data.get('sizes', None)
            labels = data.get('labels', [])
            
            if isinstance(x_values[0], list):
                # Multiple series
                for i, (x_data, y_data) in enumerate(zip(x_values, y_values)):
                    label = labels[i] if i < len(labels) else f"Series {i+1}"
                    color = colors[i] if colors and i < len(colors) else None
                    size = sizes[i] if sizes and i < len(sizes) else 50
                    ax.scatter(x_data, y_data, label=label, color=color, s=size, alpha=0.6)
            else:
                # Single series
                ax.scatter(x_values, y_values, c=colors, s=sizes, alpha=0.6)
            
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel(data.get('xlabel', 'X Axis'))
            ax.set_ylabel(data.get('ylabel', 'Y Axis'))
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close()
                return save_path
            else:
                return self._fig_to_base64(fig)
                
        except Exception as e:
            logger.error(f"Error creating scatter plot: {e}")
            return ""
    
    def create_histogram(self, data: Dict, title: str = "", save_path: str = None) -> str:
        """Create a histogram"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            values = data.get('values', [])
            bins = data.get('bins', 30)
            colors = data.get('colors', 'skyblue')
            
            ax.hist(values, bins=bins, color=colors, alpha=0.7, edgecolor='black')
            
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel(data.get('xlabel', 'Values'))
            ax.set_ylabel(data.get('ylabel', 'Frequency'))
            ax.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close()
                return save_path
            else:
                return self._fig_to_base64(fig)
                
        except Exception as e:
            logger.error(f"Error creating histogram: {e}")
            return ""
    
    def create_heatmap(self, data: Dict, title: str = "", save_path: str = None) -> str:
        """Create a heatmap"""
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            matrix = data.get('matrix', [])
            x_labels = data.get('x_labels', [])
            y_labels = data.get('y_labels', [])
            cmap = data.get('cmap', 'viridis')
            
            # Create DataFrame for seaborn
            df = pd.DataFrame(matrix, index=y_labels, columns=x_labels)
            
            # Create heatmap
            sns.heatmap(df, annot=True, cmap=cmap, fmt='.2f', ax=ax, cbar_kws={'label': 'Values'})
            
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel(data.get('xlabel', 'X Axis'))
            ax.set_ylabel(data.get('ylabel', 'Y Axis'))
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close()
                return save_path
            else:
                return self._fig_to_base64(fig)
                
        except Exception as e:
            logger.error(f"Error creating heatmap: {e}")
            return ""
    
    def create_pie_chart(self, data: Dict, title: str = "", save_path: str = None) -> str:
        """Create a pie chart"""
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            values = data.get('values', [])
            labels = data.get('labels', [])
            colors = data.get('colors', None)
            
            # Calculate percentages
            total = sum(values)
            percentages = [f'{(v/total)*100:.1f}%' for v in values]
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                             colors=colors, startangle=90)
            
            # Customize text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title(title, fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close()
                return save_path
            else:
                return self._fig_to_base64(fig)
                
        except Exception as e:
            logger.error(f"Error creating pie chart: {e}")
            return ""
    
    def create_box_plot(self, data: Dict, title: str = "", save_path: str = None) -> str:
        """Create a box plot"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            values = data.get('values', [])
            labels = data.get('labels', [])
            colors = data.get('colors', None)
            
            if isinstance(values[0], list):
                # Multiple groups
                bp = ax.boxplot(values, labels=labels, patch_artist=True)
                
                # Color boxes
                if colors:
                    for patch, color in zip(bp['boxes'], colors):
                        patch.set_facecolor(color)
                        patch.set_alpha(0.7)
            else:
                # Single group
                ax.boxplot(values, patch_artist=True)
            
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_ylabel(data.get('ylabel', 'Values'))
            ax.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close()
                return save_path
            else:
                return self._fig_to_base64(fig)
                
        except Exception as e:
            logger.error(f"Error creating box plot: {e}")
            return ""
    
    def create_dashboard(self, charts: List[Dict], layout: str = "2x2", save_path: str = None) -> str:
        """Create a dashboard with multiple charts"""
        try:
            # Parse layout
            if layout == "2x2":
                rows, cols = 2, 2
            elif layout == "3x2":
                rows, cols = 3, 2
            elif layout == "2x3":
                rows, cols = 2, 3
            else:
                rows, cols = 2, 2
            
            fig, axes = plt.subplots(rows, cols, figsize=(15, 10))
            if rows == 1:
                axes = axes.reshape(1, -1)
            if cols == 1:
                axes = axes.reshape(-1, 1)
            
            # Create charts
            for i, chart_data in enumerate(charts):
                if i >= rows * cols:
                    break
                
                row = i // cols
                col = i % cols
                ax = axes[row, col]
                
                chart_type = chart_data.get('type', 'line')
                data = chart_data.get('data', {})
                title = chart_data.get('title', f'Chart {i+1}')
                
                self._create_chart_on_axes(ax, chart_type, data, title)
            
            # Hide empty subplots
            for i in range(len(charts), rows * cols):
                row = i // cols
                col = i % cols
                axes[row, col].set_visible(False)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close()
                return save_path
            else:
                return self._fig_to_base64(fig)
                
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            return ""
    
    def create_interactive_chart(self, data: Dict, chart_type: str = "line") -> Dict:
        """Create an interactive chart (returns data for frontend rendering)"""
        try:
            chart_data = {
                'type': chart_type,
                'data': data,
                'options': self._get_chart_options(chart_type),
                'interactive': True
            }
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error creating interactive chart: {e}")
            return {}
    
    def export_chart_data(self, chart_data: Dict, format: str = "json") -> str:
        """Export chart data in various formats"""
        try:
            if format == "json":
                return json.dumps(chart_data, indent=2)
            elif format == "csv":
                # Convert to CSV format
                df = pd.DataFrame(chart_data)
                return df.to_csv(index=False)
            elif format == "excel":
                # Save as Excel file
                filename = self.file_manager.create_temp_file("chart_data.xlsx")
                df = pd.DataFrame(chart_data)
                df.to_excel(filename, index=False)
                return filename
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting chart data: {e}")
            return ""
    
    def _create_chart_on_axes(self, ax, chart_type: str, data: Dict, title: str):
        """Create a specific chart type on given axes"""
        try:
            if chart_type == "line":
                x_values = data.get('x', [])
                y_values = data.get('y', [])
                ax.plot(x_values, y_values, marker='o')
                
            elif chart_type == "bar":
                x_values = data.get('x', [])
                y_values = data.get('y', [])
                ax.bar(x_values, y_values)
                
            elif chart_type == "scatter":
                x_values = data.get('x', [])
                y_values = data.get('y', [])
                ax.scatter(x_values, y_values)
                
            elif chart_type == "histogram":
                values = data.get('values', [])
                ax.hist(values, bins=30)
                
            ax.set_title(title)
            ax.grid(True, alpha=0.3)
            
        except Exception as e:
            logger.error(f"Error creating chart on axes: {e}")
    
    def _get_chart_options(self, chart_type: str) -> Dict:
        """Get default options for chart types"""
        options = {
            'line': {
                'responsive': True,
                'scales': {'y': {'beginAtZero': True}},
                'plugins': {'legend': {'display': True}}
            },
            'bar': {
                'responsive': True,
                'scales': {'y': {'beginAtZero': True}},
                'plugins': {'legend': {'display': True}}
            },
            'scatter': {
                'responsive': True,
                'scales': {'y': {'beginAtZero': True}},
                'plugins': {'legend': {'display': True}}
            }
        }
        
        return options.get(chart_type, {})
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        try:
            import io
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode()
            plt.close(fig)
            return img_str
        except Exception as e:
            logger.error(f"Error converting figure to base64: {e}")
            return ""
    
    def get_available_chart_types(self) -> List[str]:
        """Get list of available chart types"""
        return [
            'line', 'bar', 'scatter', 'histogram', 'heatmap', 
            'pie', 'box', 'area', 'radar', 'bubble'
        ]
    
    def get_chart_templates(self) -> Dict:
        """Get predefined chart templates"""
        return {
            'sales_report': {
                'type': 'dashboard',
                'layout': '2x2',
                'charts': [
                    {'type': 'line', 'title': 'Monthly Sales'},
                    {'type': 'bar', 'title': 'Product Performance'},
                    {'type': 'pie', 'title': 'Sales by Region'},
                    {'type': 'heatmap', 'title': 'Sales Heatmap'}
                ]
            },
            'data_analysis': {
                'type': 'dashboard',
                'layout': '3x2',
                'charts': [
                    {'type': 'histogram', 'title': 'Data Distribution'},
                    {'type': 'box', 'title': 'Outlier Analysis'},
                    {'type': 'scatter', 'title': 'Correlation Plot'},
                    {'type': 'line', 'title': 'Trend Analysis'},
                    {'type': 'bar', 'title': 'Category Comparison'},
                    {'type': 'heatmap', 'title': 'Correlation Matrix'}
                ]
            }
        }