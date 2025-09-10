"""
Data Science Skill for JarvisX
Exploratory data analysis, visualization, and insights
"""

import os
import json
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from skills.base_skill import BaseSkill
from core.io import file_manager

class DataScienceSkill(BaseSkill):
    """Data Science skill"""
    
    def __init__(self):
        super().__init__()
        self.name = "Data Science"
        self.description = "Exploratory data analysis, statistical summaries, and data visualization"
        self.capabilities = [
            "Exploratory Data Analysis (EDA)",
            "Statistical Summaries",
            "Data Visualization",
            "Data Profiling",
            "Missing Data Analysis",
            "Correlation Analysis"
        ]
        self.requires_permission = None  # No special permissions needed
    
    def run(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data science operations"""
        try:
            # Validate input
            if not self.validate_input(query, context):
                return self.handle_error(ValueError("Invalid input"), context)
            
            # Preprocess query
            processed_query = self.preprocess_query(query)
            
            # Determine operation type
            if self._is_eda_request(processed_query):
                return self._perform_eda(processed_query, context)
            elif self._is_visualization_request(processed_query):
                return self._create_visualizations(processed_query, context)
            elif self._is_profiling_request(processed_query):
                return self._profile_data(processed_query, context)
            elif self._is_correlation_request(processed_query):
                return self._analyze_correlations(processed_query, context)
            else:
                return self._general_data_analysis(processed_query, context)
                
        except Exception as e:
            return self.handle_error(e, context)
    
    def _is_eda_request(self, query: str) -> bool:
        """Check if this is an EDA request"""
        keywords = ["eda", "exploratory", "explore", "analyze", "analysis", "describe", "summary"]
        return any(keyword in query.lower() for keyword in keywords)
    
    def _is_visualization_request(self, query: str) -> bool:
        """Check if this is a visualization request"""
        keywords = ["plot", "chart", "graph", "visualize", "histogram", "scatter", "box"]
        return any(keyword in query.lower() for keyword in keywords)
    
    def _is_profiling_request(self, query: str) -> bool:
        """Check if this is a profiling request"""
        keywords = ["profile", "profile", "overview", "structure", "schema"]
        return any(keyword in query.lower() for keyword in keywords)
    
    def _is_correlation_request(self, query: str) -> bool:
        """Check if this is a correlation request"""
        keywords = ["correlation", "correlate", "relationship", "association"]
        return any(keyword in query.lower() for keyword in keywords)
    
    def _perform_eda(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform exploratory data analysis"""
        try:
            # Extract data file path from context or query
            data_file = self._extract_data_file(context, query)
            
            if not data_file or not os.path.exists(data_file):
                return {
                    "type": "text",
                    "content": "Please provide a data file (CSV) to analyze.",
                    "artifacts": [],
                    "metadata": {"operation": "eda"}
                }
            
            # Load data
            data = pd.read_csv(data_file)
            
            # Generate EDA report
            eda_report = self._generate_eda_report(data, data_file)
            
            # Create basic visualizations
            charts = self._create_basic_charts(data)
            
            # Save EDA report
            report_filename = f"eda_report_{os.path.basename(data_file).replace('.csv', '')}.md"
            report_path = file_manager.create_temp_file(extension=".md", prefix="eda_report_")
            file_manager.save_file(eda_report, str(report_path))
            
            return {
                "type": "text",
                "content": eda_report,
                "artifacts": [str(report_path)] + charts,
                "metadata": {
                    "operation": "eda",
                    "data_file": data_file,
                    "rows": len(data),
                    "columns": len(data.columns),
                    "report_file": str(report_path),
                    "charts_generated": len(charts)
                }
            }
            
        except Exception as e:
            return self.handle_error(e, context)
    
    def _create_visualizations(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create data visualizations"""
        try:
            # Extract data file path from context or query
            data_file = self._extract_data_file(context, query)
            
            if not data_file or not os.path.exists(data_file):
                return {
                    "type": "text",
                    "content": "Please provide a data file (CSV) to visualize.",
                    "artifacts": [],
                    "metadata": {"operation": "visualization"}
                }
            
            # Load data
            data = pd.read_csv(data_file)
            
            # Determine visualization types from query
            viz_types = self._extract_visualization_types(query)
            
            # Create visualizations
            charts = self._create_specific_charts(data, viz_types)
            
            # Generate visualization report
            viz_report = self._generate_visualization_report(charts, data_file)
            
            return {
                "type": "text",
                "content": viz_report,
                "artifacts": charts,
                "metadata": {
                    "operation": "visualization",
                    "data_file": data_file,
                    "charts_created": len(charts),
                    "visualization_types": viz_types
                }
            }
            
        except Exception as e:
            return self.handle_error(e, context)
    
    def _profile_data(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Profile and analyze data structure"""
        try:
            # Extract data file path from context or query
            data_file = self._extract_data_file(context, query)
            
            if not data_file or not os.path.exists(data_file):
                return {
                    "type": "text",
                    "content": "Please provide a data file (CSV) to profile.",
                    "artifacts": [],
                    "metadata": {"operation": "profiling"}
                }
            
            # Load data
            data = pd.read_csv(data_file)
            
            # Generate data profile
            profile = self._generate_data_profile(data)
            
            # Save profile
            profile_filename = f"data_profile_{os.path.basename(data_file).replace('.csv', '')}.json"
            profile_path = file_manager.create_temp_file(extension=".json", prefix="data_profile_")
            file_manager.save_file(json.dumps(profile, indent=2), str(profile_path))
            
            # Generate profile report
            profile_report = self._generate_profile_report(profile, data_file)
            
            return {
                "type": "text",
                "content": profile_report,
                "artifacts": [str(profile_path)],
                "metadata": {
                    "operation": "profiling",
                    "data_file": data_file,
                    "profile_file": str(profile_path)
                }
            }
            
        except Exception as e:
            return self.handle_error(e, context)
    
    def _analyze_correlations(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze correlations between variables"""
        try:
            # Extract data file path from context or query
            data_file = self._extract_data_file(context, query)
            
            if not data_file or not os.path.exists(data_file):
                return {
                    "type": "text",
                    "content": "Please provide a data file (CSV) to analyze correlations.",
                    "artifacts": [],
                    "metadata": {"operation": "correlation_analysis"}
                }
            
            # Load data
            data = pd.read_csv(data_file)
            
            # Calculate correlations
            correlation_matrix = self._calculate_correlations(data)
            
            # Create correlation heatmap
            heatmap_path = self._create_correlation_heatmap(data, correlation_matrix)
            
            # Generate correlation report
            correlation_report = self._generate_correlation_report(correlation_matrix, data_file)
            
            # Save correlation matrix
            corr_filename = f"correlation_matrix_{os.path.basename(data_file).replace('.csv', '')}.csv"
            corr_path = file_manager.create_temp_file(extension=".csv", prefix="correlation_")
            correlation_matrix.to_csv(str(corr_path))
            
            return {
                "type": "text",
                "content": correlation_report,
                "artifacts": [str(corr_path), heatmap_path],
                "metadata": {
                    "operation": "correlation_analysis",
                    "data_file": data_file,
                    "correlation_file": str(corr_path),
                    "heatmap_file": heatmap_path
                }
            }
            
        except Exception as e:
            return self.handle_error(e, context)
    
    def _generate_eda_report(self, data: pd.DataFrame, data_file: str) -> str:
        """Generate comprehensive EDA report"""
        report = f"""
        # Exploratory Data Analysis Report
        
        **Dataset:** {os.path.basename(data_file)}
        **Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        ## Dataset Overview
        
        - **Rows:** {len(data):,}
        - **Columns:** {len(data.columns):,}
        - **Memory Usage:** {data.memory_usage(deep=True).sum() / 1024**2:.2f} MB
        
        ## Data Types
        
        """
        
        for col, dtype in data.dtypes.items():
            report += f"- **{col}:** {dtype}\n"
        
        report += "\n## Missing Values\n\n"
        
        missing_data = data.isnull().sum()
        missing_percent = (missing_data / len(data)) * 100
        
        for col in data.columns:
            if missing_data[col] > 0:
                report += f"- **{col}:** {missing_data[col]:,} ({missing_percent[col]:.1f}%)\n"
            else:
                report += f"- **{col}:** No missing values\n"
        
        report += "\n## Statistical Summary\n\n"
        
        # Numerical columns summary
        numerical_cols = data.select_dtypes(include=[np.number]).columns
        if len(numerical_cols) > 0:
            report += "### Numerical Columns\n\n"
            summary_stats = data[numerical_cols].describe()
            report += summary_stats.to_string()
            report += "\n\n"
        
        # Categorical columns summary
        categorical_cols = data.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            report += "### Categorical Columns\n\n"
            for col in categorical_cols:
                value_counts = data[col].value_counts().head(10)
                report += f"**{col}** (Top 10 values):\n"
                for value, count in value_counts.items():
                    report += f"- {value}: {count:,}\n"
                report += "\n"
        
        report += "\n## Key Insights\n\n"
        
        # Add insights based on data characteristics
        if len(numerical_cols) > 0:
            report += "- Numerical columns analyzed for distributions and outliers\n"
        if len(categorical_cols) > 0:
            report += "- Categorical columns analyzed for value distributions\n"
        if missing_data.sum() > 0:
            report += "- Missing value patterns identified\n"
        
        report += "- Data quality assessment completed\n"
        
        return report
    
    def _create_basic_charts(self, data: pd.DataFrame) -> List[str]:
        """Create basic charts for EDA"""
        charts = []
        
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Numerical columns distributions
        numerical_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numerical_cols[:5]:  # Limit to first 5 columns
            try:
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                
                # Histogram
                ax1.hist(data[col].dropna(), bins=30, alpha=0.7, edgecolor='black')
                ax1.set_title(f'Distribution of {col}')
                ax1.set_xlabel(col)
                ax1.set_ylabel('Frequency')
                
                # Box plot
                ax2.boxplot(data[col].dropna())
                ax2.set_title(f'Box Plot of {col}')
                ax2.set_ylabel(col)
                
                plt.tight_layout()
                
                # Save chart
                chart_filename = f"distribution_{col}.png"
                chart_path = file_manager.create_temp_file(extension=".png", prefix="chart_")
                plt.savefig(str(chart_path), dpi=300, bbox_inches='tight')
                plt.close()
                
                charts.append(str(chart_path))
                
            except Exception as e:
                print(f"Error creating chart for {col}: {e}")
                continue
        
        return charts
    
    def _extract_visualization_types(self, query: str) -> List[str]:
        """Extract visualization types from query"""
        viz_types = []
        
        if "histogram" in query.lower():
            viz_types.append("histogram")
        if "scatter" in query.lower():
            viz_types.append("scatter")
        if "box" in query.lower() or "boxplot" in query.lower():
            viz_types.append("boxplot")
        if "correlation" in query.lower() or "heatmap" in query.lower():
            viz_types.append("heatmap")
        if "line" in query.lower() or "trend" in query.lower():
            viz_types.append("line")
        
        # Default to common types if none specified
        if not viz_types:
            viz_types = ["histogram", "scatter", "boxplot"]
        
        return viz_types
    
    def _create_specific_charts(self, data: pd.DataFrame, viz_types: List[str]) -> List[str]:
        """Create specific types of charts"""
        charts = []
        
        plt.style.use('default')
        sns.set_palette("husl")
        
        numerical_cols = data.select_dtypes(include=[np.number]).columns
        
        for viz_type in viz_types:
            try:
                if viz_type == "histogram" and len(numerical_cols) > 0:
                    # Create histogram grid
                    n_cols = min(3, len(numerical_cols))
                    n_rows = (len(numerical_cols) + n_cols - 1) // n_cols
                    
                    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
                    if n_rows == 1:
                        axes = [axes]
                    
                    for i, col in enumerate(numerical_cols):
                        row = i // n_cols
                        col_idx = i % n_cols
                        axes[row][col_idx].hist(data[col].dropna(), bins=30, alpha=0.7, edgecolor='black')
                        axes[row][col_idx].set_title(f'Distribution of {col}')
                        axes[row][col_idx].set_xlabel(col)
                        axes[row][col_idx].set_ylabel('Frequency')
                    
                    plt.tight_layout()
                    
                    chart_path = file_manager.create_temp_file(extension=".png", prefix="histograms_")
                    plt.savefig(str(chart_path), dpi=300, bbox_inches='tight')
                    plt.close()
                    
                    charts.append(str(chart_path))
                
                elif viz_type == "scatter" and len(numerical_cols) >= 2:
                    # Create scatter plot matrix
                    fig, axes = plt.subplots(len(numerical_cols), len(numerical_cols), figsize=(15, 15))
                    
                    for i, col1 in enumerate(numerical_cols):
                        for j, col2 in enumerate(numerical_cols):
                            if i == j:
                                axes[i, j].hist(data[col1].dropna(), bins=20, alpha=0.7)
                                axes[i, j].set_title(f'Distribution of {col1}')
                            else:
                                axes[i, j].scatter(data[col1], data[col2], alpha=0.6)
                                axes[i, j].set_xlabel(col1)
                                axes[i, j].set_ylabel(col2)
                    
                    plt.tight_layout()
                    
                    chart_path = file_manager.create_temp_file(extension=".png", prefix="scatter_matrix_")
                    plt.savefig(str(chart_path), dpi=300, bbox_inches='tight')
                    plt.close()
                    
                    charts.append(str(chart_path))
                
                elif viz_type == "boxplot" and len(numerical_cols) > 0:
                    # Create box plot
                    fig, ax = plt.subplots(figsize=(12, 6))
                    data[numerical_cols].boxplot(ax=ax)
                    ax.set_title('Box Plots of Numerical Variables')
                    ax.set_ylabel('Values')
                    ax.tick_params(axis='x', rotation=45)
                    
                    plt.tight_layout()
                    
                    chart_path = file_manager.create_temp_file(extension=".png", prefix="boxplots_")
                    plt.savefig(str(chart_path), dpi=300, bbox_inches='tight')
                    plt.close()
                    
                    charts.append(str(chart_path))
                
            except Exception as e:
                print(f"Error creating {viz_type} chart: {e}")
                continue
        
        return charts
    
    def _generate_visualization_report(self, charts: List[str], data_file: str) -> str:
        """Generate visualization report"""
        report = f"""
        # Data Visualization Report
        
        **Dataset:** {os.path.basename(data_file)}
        **Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        ## Charts Created
        
        """
        
        for i, chart_path in enumerate(charts, 1):
            chart_name = os.path.basename(chart_path).replace('.png', '').replace('_', ' ').title()
            report += f"{i}. **{chart_name}** - Saved as: {os.path.basename(chart_path)}\n"
        
        report += f"""
        
        **Total Charts:** {len(charts)}
        
        All charts have been saved as PNG files and are available for download.
        """
        
        return report
    
    def _generate_data_profile(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive data profile"""
        profile = {
            "basic_info": {
                "rows": len(data),
                "columns": len(data.columns),
                "memory_usage_mb": data.memory_usage(deep=True).sum() / 1024**2,
                "duplicate_rows": data.duplicated().sum()
            },
            "data_types": data.dtypes.to_dict(),
            "missing_values": data.isnull().sum().to_dict(),
            "missing_percentages": (data.isnull().sum() / len(data) * 100).to_dict(),
            "numerical_summary": {},
            "categorical_summary": {},
            "unique_values": {}
        }
        
        # Numerical columns summary
        numerical_cols = data.select_dtypes(include=[np.number]).columns
        if len(numerical_cols) > 0:
            profile["numerical_summary"] = data[numerical_cols].describe().to_dict()
        
        # Categorical columns summary
        categorical_cols = data.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            profile["categorical_summary"] = {}
            for col in categorical_cols:
                profile["categorical_summary"][col] = {
                    "unique_count": data[col].nunique(),
                    "top_values": data[col].value_counts().head(5).to_dict()
                }
        
        # Unique values count for all columns
        for col in data.columns:
            profile["unique_values"][col] = data[col].nunique()
        
        return profile
    
    def _generate_profile_report(self, profile: Dict[str, Any], data_file: str) -> str:
        """Generate profile report"""
        report = f"""
        # Data Profile Report
        
        **Dataset:** {os.path.basename(data_file)}
        **Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        ## Basic Information
        
        - **Rows:** {profile['basic_info']['rows']:,}
        - **Columns:** {profile['basic_info']['columns']:,}
        - **Memory Usage:** {profile['basic_info']['memory_usage_mb']:.2f} MB
        - **Duplicate Rows:** {profile['basic_info']['duplicate_rows']:,}
        
        ## Data Quality
        
        """
        
        # Missing values summary
        missing_cols = [col for col, missing in profile['missing_values'].items() if missing > 0]
        if missing_cols:
            report += "**Columns with Missing Values:**\n"
            for col in missing_cols:
                missing_count = profile['missing_values'][col]
                missing_pct = profile['missing_percentages'][col]
                report += f"- **{col}:** {missing_count:,} ({missing_pct:.1f}%)\n"
        else:
            report += "**No missing values found**\n"
        
        report += "\n## Column Analysis\n\n"
        
        for col, dtype in profile['data_types'].items():
            report += f"**{col}** ({dtype})\n"
            report += f"- Unique values: {profile['unique_values'][col]:,}\n"
            
            if col in profile['numerical_summary']:
                stats = profile['numerical_summary'][col]
                report += f"- Range: {stats['min']:.2f} to {stats['max']:.2f}\n"
                report += f"- Mean: {stats['mean']:.2f}\n"
                report += f"- Median: {stats['50%']:.2f}\n"
            
            if col in profile['categorical_summary']:
                cat_stats = profile['categorical_summary'][col]
                report += f"- Top values: {', '.join([f'{k} ({v})' for k, v in list(cat_stats['top_values'].items())[:3]])}\n"
            
            report += "\n"
        
        return report
    
    def _calculate_correlations(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate correlation matrix for numerical columns"""
        numerical_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numerical_cols) < 2:
            return pd.DataFrame()
        
        return data[numerical_cols].corr()
    
    def _create_correlation_heatmap(self, data: pd.DataFrame, correlation_matrix: pd.DataFrame) -> str:
        """Create correlation heatmap"""
        if correlation_matrix.empty:
            return ""
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, linewidths=0.5)
        plt.title('Correlation Heatmap')
        plt.tight_layout()
        
        chart_path = file_manager.create_temp_file(extension=".png", prefix="correlation_heatmap_")
        plt.savefig(str(chart_path), dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(chart_path)
    
    def _generate_correlation_report(self, correlation_matrix: pd.DataFrame, data_file: str) -> str:
        """Generate correlation analysis report"""
        if correlation_matrix.empty:
            return "No numerical columns found for correlation analysis."
        
        report = f"""
        # Correlation Analysis Report
        
        **Dataset:** {os.path.basename(data_file)}
        **Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        ## Correlation Matrix
        
        The correlation matrix shows relationships between numerical variables.
        Values range from -1 (perfect negative correlation) to +1 (perfect positive correlation).
        
        **Strong Correlations (|r| > 0.7):**
        """
        
        # Find strong correlations
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    col1 = correlation_matrix.columns[i]
                    col2 = correlation_matrix.columns[j]
                    strong_correlations.append((col1, col2, corr_value))
        
        if strong_correlations:
            for col1, col2, corr_value in strong_correlations:
                direction = "positive" if corr_value > 0 else "negative"
                report += f"- **{col1}** and **{col2}**: {corr_value:.3f} ({direction})\n"
        else:
            report += "No strong correlations found.\n"
        
        report += f"""
        
        **Total Variables Analyzed:** {len(correlation_matrix.columns)}
        
        A correlation heatmap has been generated and saved as an image file.
        The correlation matrix has been saved as a CSV file for further analysis.
        """
        
        return report
    
    def _extract_data_file(self, context: Dict[str, Any], query: str) -> Optional[str]:
        """Extract data file path from context or query"""
        # Check context for uploaded files
        if "uploaded_files" in context:
            for file_info in context["uploaded_files"]:
                if file_info.get("path") and file_info["path"].endswith('.csv'):
                    return file_info["path"]
        
        # Check for CSV files in current directory
        current_dir = os.getcwd()
        csv_files = [f for f in os.listdir(current_dir) if f.endswith('.csv')]
        
        if csv_files:
            # Try to match with query
            for csv_file in csv_files:
                if csv_file.lower() in query.lower():
                    return os.path.join(current_dir, csv_file)
            
            # Return first CSV file if no match
            return os.path.join(current_dir, csv_files[0])
        
        return None
    
    def _general_data_analysis(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide general data analysis help"""
        help_text = """
        # Data Science Help 📊
        
        I can help you with various data analysis tasks:
        
        ## Exploratory Data Analysis (EDA)
        - "Perform EDA on my data.csv file"
        - "Explore and analyze my dataset"
        - "Give me a summary of my data"
        
        ## Data Visualization
        - "Create charts and plots for my data"
        - "Show me histograms and distributions"
        - "Generate scatter plots and correlations"
        
        ## Data Profiling
        - "Profile my dataset structure"
        - "Analyze data quality and missing values"
        - "Get detailed information about my data"
        
        ## Correlation Analysis
        - "Find correlations between variables"
        - "Show relationships in my data"
        - "Create correlation heatmaps"
        
        ## Requirements
        - Data should be in CSV format
        - Numerical and categorical data supported
        - Automatic chart generation and saving
        
        Upload a CSV file and let me know what you'd like to analyze!
        """
        
        return {
            "type": "text",
            "content": help_text,
            "artifacts": [],
            "metadata": {"operation": "data_science_help"}
        }
    
    def get_usage_examples(self) -> List[str]:
        """Get example usage queries for this skill"""
        return [
            "Perform EDA on my data.csv file",
            "Create visualizations for my dataset",
            "Profile and analyze my data structure",
            "Find correlations between variables",
            "Generate charts and plots",
            "Help me understand my data"
        ]