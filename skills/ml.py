"""
Machine Learning Skill for JarvisX
Model training, evaluation, and prediction
"""

import os
import pickle
import json
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, mean_squared_error, r2_score
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
from skills.base_skill import BaseSkill
from core.io import file_manager
from core.permissions import Capability

class MLSkill(BaseSkill):
    """Machine Learning skill"""
    
    def __init__(self):
        super().__init__()
        self.name = "Machine Learning"
        self.description = "Train and evaluate ML models, make predictions, and analyze model performance"
        self.capabilities = [
            "Model Training",
            "Model Evaluation", 
            "Prediction",
            "Feature Analysis",
            "Hyperparameter Tuning",
            "Model Persistence"
        ]
        self.requires_permission = Capability.MODEL_TRAINING
    
    def run(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute ML operations"""
        try:
            # Validate input
            if not self.validate_input(query, context):
                return self.handle_error(ValueError("Invalid input"), context)
            
            # Preprocess query
            processed_query = self.preprocess_query(query)
            
            # Determine operation type
            if self._is_training_request(processed_query):
                return self._train_model(processed_query, context)
            elif self._is_prediction_request(processed_query):
                return self._make_prediction(processed_query, context)
            elif self._is_evaluation_request(processed_query):
                return self._evaluate_model(processed_query, context)
            elif self._is_feature_analysis_request(processed_query):
                return self._analyze_features(processed_query, context)
            else:
                return self._general_ml_help(processed_query, context)
                
        except Exception as e:
            return self.handle_error(e, context)
    
    def _is_training_request(self, query: str) -> bool:
        """Check if this is a training request"""
        keywords = ["train", "training", "fit", "model", "classifier", "regression"]
        return any(keyword in query.lower() for keyword in keywords)
    
    def _is_prediction_request(self, query: str) -> bool:
        """Check if this is a prediction request"""
        keywords = ["predict", "prediction", "inference", "forecast", "estimate"]
        return any(keyword in query.lower() for keyword in keywords)
    
    def _is_evaluation_request(self, query: str) -> bool:
        """Check if this is an evaluation request"""
        keywords = ["evaluate", "evaluation", "accuracy", "performance", "metrics", "score"]
        return any(keyword in query.lower() for keyword in keywords)
    
    def _is_feature_analysis_request(self, query: str) -> bool:
        """Check if this is a feature analysis request"""
        keywords = ["feature", "importance", "correlation", "selection", "analysis"]
        return any(keyword in query.lower() for keyword in keywords)
    
    def _train_model(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Train a machine learning model"""
        try:
            # Extract data file path from context or query
            data_file = self._extract_data_file(context, query)
            
            if not data_file or not os.path.exists(data_file):
                return {
                    "type": "text",
                    "content": "Please provide a data file (CSV) to train the model on.",
                    "artifacts": [],
                    "metadata": {"operation": "model_training"}
                }
            
            # Load and prepare data
            data = pd.read_csv(data_file)
            
            # Determine target column and model type
            target_col = self._determine_target_column(data, query)
            if not target_col:
                return {
                    "type": "text",
                    "content": "Could not determine target column. Please specify which column to predict.",
                    "artifacts": [],
                    "metadata": {"operation": "model_training"}
                }
            
            # Prepare features and target
            X = data.drop(columns=[target_col])
            y = data[target_col]
            
            # Handle categorical variables
            X = self._encode_categorical_features(X)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Determine model type and train
            model_type = self._determine_model_type(y, query)
            model, model_info = self._train_model_by_type(
                X_train, y_train, X_test, y_test, model_type
            )
            
            # Save model
            model_filename = f"model_{model_type}_{target_col}.pkl"
            model_path = file_manager.create_temp_file(extension=".pkl", prefix="model_")
            with open(str(model_path), 'wb') as f:
                pickle.dump(model, f)
            
            # Save model info
            info_filename = f"model_info_{model_type}_{target_col}.json"
            info_path = file_manager.create_temp_file(extension=".json", prefix="model_info_")
            with open(str(info_path), 'w') as f:
                json.dump(model_info, f, indent=2)
            
            # Generate training report
            training_report = self._generate_training_report(
                model_info, data_file, target_col, model_type
            )
            
            return {
                "type": "text",
                "content": training_report,
                "artifacts": [str(model_path), str(info_path)],
                "metadata": {
                    "operation": "model_training",
                    "model_type": model_type,
                    "target_column": target_col,
                    "training_samples": len(X_train),
                    "test_samples": len(X_test),
                    "features": len(X.columns),
                    "model_file": str(model_path),
                    "info_file": str(info_path)
                }
            }
            
        except Exception as e:
            return self.handle_error(e, context)
    
    def _make_prediction(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make predictions using a trained model"""
        try:
            # Extract model file and data file from context
            model_file = self._extract_model_file(context)
            data_file = self._extract_data_file(context, query)
            
            if not model_file or not os.path.exists(model_file):
                return {
                    "type": "text",
                    "content": "Please provide a trained model file to make predictions.",
                    "artifacts": [],
                    "metadata": {"operation": "prediction"}
                }
            
            if not data_file or not os.path.exists(data_file):
                return {
                    "type": "text",
                    "content": "Please provide data file to make predictions on.",
                    "artifacts": [],
                    "metadata": {"operation": "prediction"}
                }
            
            # Load model
            with open(model_file, 'rb') as f:
                model = pickle.load(f)
            
            # Load data
            data = pd.read_csv(data_file)
            
            # Prepare features
            X = self._encode_categorical_features(data)
            
            # Make predictions
            predictions = model.predict(X)
            
            # Create results dataframe
            results_df = data.copy()
            results_df['prediction'] = predictions
            
            # Save results
            results_filename = f"predictions_{os.path.basename(data_file)}"
            results_path = file_manager.create_temp_file(extension=".csv", prefix="predictions_")
            results_df.to_csv(str(results_path), index=False)
            
            # Generate prediction report
            prediction_report = self._generate_prediction_report(
                predictions, data_file, len(predictions)
            )
            
            return {
                "type": "text",
                "content": prediction_report,
                "artifacts": [str(results_path)],
                "metadata": {
                    "operation": "prediction",
                    "predictions_count": len(predictions),
                    "results_file": str(results_path)
                }
            }
            
        except Exception as e:
            return self.handle_error(e, context)
    
    def _evaluate_model(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a trained model"""
        try:
            # Extract model file and test data from context
            model_file = self._extract_model_file(context)
            test_data_file = self._extract_data_file(context, query)
            
            if not model_file or not os.path.exists(model_file):
                return {
                    "type": "text",
                    "content": "Please provide a trained model file to evaluate.",
                    "artifacts": [],
                    "metadata": {"operation": "model_evaluation"}
                }
            
            # Load model
            with open(model_file, 'rb') as f:
                model = pickle.load(f)
            
            # Load test data
            test_data = pd.read_csv(test_data_file)
            
            # Determine target column
            target_col = self._determine_target_column(test_data, query)
            if not target_col:
                return {
                    "type": "text",
                    "content": "Could not determine target column for evaluation.",
                    "artifacts": [],
                    "metadata": {"operation": "model_evaluation"}
                }
            
            # Prepare features and target
            X_test = test_data.drop(columns=[target_col])
            y_test = test_data[target_col]
            
            # Handle categorical variables
            X_test = self._encode_categorical_features(X_test)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            metrics = self._calculate_metrics(y_test, y_pred, model)
            
            # Generate evaluation report
            evaluation_report = self._generate_evaluation_report(metrics, test_data_file)
            
            # Save evaluation results
            eval_filename = f"evaluation_results.json"
            eval_path = file_manager.create_temp_file(extension=".json", prefix="evaluation_")
            with open(str(eval_path), 'w') as f:
                json.dump(metrics, f, indent=2)
            
            return {
                "type": "text",
                "content": evaluation_report,
                "artifacts": [str(eval_path)],
                "metadata": {
                    "operation": "model_evaluation",
                    "test_samples": len(X_test),
                    "evaluation_file": str(eval_path)
                }
            }
            
        except Exception as e:
            return self.handle_error(e, context)
    
    def _analyze_features(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze feature importance and correlations"""
        try:
            # Extract model file from context
            model_file = self._extract_model_file(context)
            
            if not model_file or not os.path.exists(model_file):
                return {
                    "type": "text",
                    "content": "Please provide a trained model file to analyze features.",
                    "artifacts": [],
                    "metadata": {"operation": "feature_analysis"}
                }
            
            # Load model
            with open(model_file, 'rb') as f:
                model = pickle.load(f)
            
            # Get feature importance if available
            if hasattr(model, 'feature_importances_'):
                feature_importance = model.feature_importances_
                feature_names = getattr(model, 'feature_names_in_', [f"Feature_{i}" for i in range(len(feature_importance))])
                
                # Create feature importance dataframe
                importance_df = pd.DataFrame({
                    'feature': feature_names,
                    'importance': feature_importance
                }).sort_values('importance', ascending=False)
                
                # Save feature importance
                importance_filename = f"feature_importance.csv"
                importance_path = file_manager.create_temp_file(extension=".csv", prefix="feature_importance_")
                importance_df.to_csv(str(importance_path), index=False)
                
                # Generate feature analysis report
                analysis_report = self._generate_feature_analysis_report(importance_df)
                
                return {
                    "type": "text",
                    "content": analysis_report,
                    "artifacts": [str(importance_path)],
                    "metadata": {
                        "operation": "feature_analysis",
                        "features_count": len(feature_names),
                        "importance_file": str(importance_path)
                    }
                }
            else:
                return {
                    "type": "text",
                    "content": "This model type does not support feature importance analysis.",
                    "artifacts": [],
                    "metadata": {"operation": "feature_analysis"}
                }
                
        except Exception as e:
            return self.handle_error(e, context)
    
    def _train_model_by_type(self, X_train, y_train, X_test, y_test, model_type: str):
        """Train model based on type"""
        if model_type == "classification":
            # Try different classifiers
            models = {
                "Logistic Regression": LogisticRegression(random_state=42, max_iter=1000),
                "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42)
            }
            
            best_model = None
            best_score = 0
            best_name = ""
            
            for name, model in models.items():
                model.fit(X_train, y_train)
                score = model.score(X_test, y_test)
                if score > best_score:
                    best_score = score
                    best_model = model
                    best_name = name
            
            model_info = {
                "model_type": "classification",
                "algorithm": best_name,
                "accuracy": best_score,
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "features": X_train.shape[1]
            }
            
        else:  # regression
            # Try different regressors
            models = {
                "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42)
            }
            
            best_model = None
            best_score = 0
            best_name = ""
            
            for name, model in models.items():
                model.fit(X_train, y_train)
                score = model.score(X_test, y_test)
                if score > best_score:
                    best_score = score
                    best_model = model
                    best_name = name
            
            model_info = {
                "model_type": "regression",
                "algorithm": best_name,
                "r2_score": best_score,
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "features": X_train.shape[1]
            }
        
        return best_model, model_info
    
    def _determine_model_type(self, y, query: str) -> str:
        """Determine if this is classification or regression"""
        if "classification" in query.lower() or "classify" in query.lower():
            return "classification"
        elif "regression" in query.lower() or "predict" in query.lower():
            return "regression"
        
        # Auto-detect based on target variable
        if y.dtype == 'object' or len(y.unique()) < len(y) * 0.1:
            return "classification"
        else:
            return "regression"
    
    def _determine_target_column(self, data: pd.DataFrame, query: str) -> Optional[str]:
        """Determine target column from data or query"""
        # Check if query specifies target column
        for col in data.columns:
            if col.lower() in query.lower():
                return col
        
        # Try to infer from data
        # Look for common target column names
        target_candidates = ['target', 'label', 'class', 'outcome', 'result', 'prediction']
        for candidate in target_candidates:
            if candidate in data.columns:
                return candidate
        
        # Look for binary or categorical columns
        for col in data.columns:
            if data[col].dtype == 'object' or len(data[col].unique()) < len(data) * 0.1:
                return col
        
        # Default to last column
        return data.columns[-1]
    
    def _encode_categorical_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features"""
        X_encoded = X.copy()
        
        for col in X_encoded.columns:
            if X_encoded[col].dtype == 'object':
                # Simple label encoding
                le = LabelEncoder()
                X_encoded[col] = le.fit_transform(X_encoded[col].astype(str))
        
        return X_encoded
    
    def _calculate_metrics(self, y_true, y_pred, model) -> Dict[str, Any]:
        """Calculate model performance metrics"""
        metrics = {}
        
        if hasattr(model, '_estimator_type'):
            if model._estimator_type == 'classifier':
                metrics['accuracy'] = accuracy_score(y_true, y_pred)
                metrics['precision'] = precision_score(y_true, y_pred, average='weighted')
                metrics['recall'] = recall_score(y_true, y_pred, average='weighted')
                metrics['f1'] = f1_score(y_true, y_pred, average='weighted')
                metrics['classification_report'] = classification_report(y_true, y_pred, output_dict=True)
            else:  # regressor
                metrics['mse'] = mean_squared_error(y_true, y_pred)
                metrics['rmse'] = np.sqrt(mean_squared_error(y_true, y_pred))
                metrics['r2'] = r2_score(y_true, y_pred)
        
        return metrics
    
    def _generate_training_report(self, model_info: Dict[str, Any], data_file: str, 
                                 target_col: str, model_type: str) -> str:
        """Generate training report"""
        report = f"""
        **Model Training Complete! 🎉**
        
        **Model Details:**
        - **Type:** {model_type.title()}
        - **Algorithm:** {model_info['algorithm']}
        - **Target Column:** {target_col}
        - **Training Samples:** {model_info['training_samples']:,}
        - **Test Samples:** {model_info['test_samples']:,}
        - **Features:** {model_info['features']}
        
        **Performance:**
        """
        
        if model_type == "classification":
            report += f"- **Accuracy:** {model_info['accuracy']:.3f}"
        else:
            report += f"- **R² Score:** {model_info['r2_score']:.3f}"
        
        report += f"""
        
        **Data Source:** {os.path.basename(data_file)}
        
        The model has been saved and is ready for predictions!
        """
        
        return report
    
    def _generate_prediction_report(self, predictions, data_file: str, count: int) -> str:
        """Generate prediction report"""
        return f"""
        **Predictions Generated! 📊**
        
        **Summary:**
        - **Data Source:** {os.path.basename(data_file)}
        - **Predictions Made:** {count:,}
        
        **Prediction Range:**
        - **Min:** {np.min(predictions):.3f}
        - **Max:** {np.max(predictions):.3f}
        - **Mean:** {np.mean(predictions):.3f}
        
        Results have been saved to a CSV file for your review.
        """
    
    def _generate_evaluation_report(self, metrics: Dict[str, Any], test_data_file: str) -> str:
        """Generate evaluation report"""
        report = f"""
        **Model Evaluation Results 📈**
        
        **Test Data:** {os.path.basename(test_data_file)}
        
        **Performance Metrics:**
        """
        
        if 'accuracy' in metrics:
            report += f"""
        - **Accuracy:** {metrics['accuracy']:.3f}
        - **Precision:** {metrics['precision']:.3f}
        - **Recall:** {metrics['recall']:.3f}
        - **F1 Score:** {metrics['f1']:.3f}
        """
        elif 'r2' in metrics:
            report += f"""
        - **R² Score:** {metrics['r2']:.3f}
        - **MSE:** {metrics['mse']:.3f}
        - **RMSE:** {metrics['rmse']:.3f}
        """
        
        report += "\nDetailed metrics have been saved to a JSON file."
        return report
    
    def _generate_feature_analysis_report(self, importance_df: pd.DataFrame) -> str:
        """Generate feature analysis report"""
        top_features = importance_df.head(10)
        
        report = f"""
        **Feature Importance Analysis 🔍**
        
        **Top 10 Most Important Features:**
        """
        
        for idx, row in top_features.iterrows():
            report += f"\n{idx+1}. **{row['feature']}:** {row['importance']:.4f}"
        
        report += f"""
        
        **Total Features Analyzed:** {len(importance_df)}
        
        Feature importance data has been saved to a CSV file.
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
    
    def _extract_model_file(self, context: Dict[str, Any]) -> Optional[str]:
        """Extract model file path from context"""
        # Check context for model files
        if "uploaded_files" in context:
            for file_info in context["uploaded_files"]:
                if file_info.get("path") and file_info["path"].endswith('.pkl'):
                    return file_info["path"]
        
        # Check for model files in temp directory
        temp_dir = "temp"
        if os.path.exists(temp_dir):
            model_files = [f for f in os.listdir(temp_dir) if f.endswith('.pkl') and 'model_' in f]
            if model_files:
                # Return most recent model file
                model_files.sort(key=lambda x: os.path.getmtime(os.path.join(temp_dir, x)), reverse=True)
                return os.path.join(temp_dir, model_files[0])
        
        return None
    
    def _general_ml_help(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide general ML help"""
        help_text = """
        **Machine Learning Help 🤖**
        
        I can help you with various machine learning tasks:
        
        **Training Models:**
        - "Train a classifier on my data.csv file"
        - "Create a regression model for sales prediction"
        - "Fit a model to predict customer churn"
        
        **Making Predictions:**
        - "Use my trained model to predict on new data"
        - "Make predictions on test_data.csv"
        - "Forecast sales for next quarter"
        
        **Evaluating Models:**
        - "Evaluate my model performance"
        - "Calculate accuracy and other metrics"
        - "Test model on validation data"
        
        **Feature Analysis:**
        - "Show feature importance"
        - "Analyze which features matter most"
        - "Rank features by importance"
        
        **Requirements:**
        - Data should be in CSV format
        - Target column should be clearly identifiable
        - Numerical or categorical features supported
        
        Upload a CSV file and let me know what you'd like to do!
        """
        
        return {
            "type": "text",
            "content": help_text,
            "artifacts": [],
            "metadata": {"operation": "ml_help"}
        }
    
    def get_usage_examples(self) -> List[str]:
        """Get example usage queries for this skill"""
        return [
            "Train a classifier on my data.csv file",
            "Create a regression model for sales prediction",
            "Use my trained model to make predictions",
            "Evaluate my model performance",
            "Show feature importance for my model",
            "Help me with machine learning tasks"
        ]