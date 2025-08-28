"""
Intent classification and skill routing for JarvisX
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import pickle
import os
from pathlib import Path
from .logging_utils import get_logger

logger = get_logger(__name__)

class IntentClassifier:
    """Hybrid intent classifier using rules and ML"""
    
    def __init__(self):
        self.rule_patterns = {
            "nlp": [
                r"\b(summarize|summarization|rewrite|translate|extract|plan|brief|requirements?)\b",
                r"\b(project plan|technical brief|user story|acceptance criteria)\b",
                r"\b(paraphrase|rephrase|simplify|complexify)\b"
            ],
            "ml": [
                r"\b(train|training|model|classifier|regression|random.?forest|logistic|svm)\b",
                r"\b(predict|prediction|inference|accuracy|f1|confusion matrix)\b",
                r"\b(feature importance|hyperparameter|cross.?validation)\b"
            ],
            "data_science": [
                r"\b(eda|exploratory|analysis|describe|profile|missing|correlation)\b",
                r"\b(histogram|box.?plot|scatter|distribution|outlier)\b",
                r"\b(statistics|summary|insights|trends|patterns)\b"
            ],
            "data_engineering": [
                r"\b(etl|extract|transform|load|pipeline|data.?pipeline)\b",
                r"\b(clean|filter|join|merge|aggregate|validate)\b",
                r"\b(csv|json|sqlite|database|schema)\b"
            ],
            "analytics": [
                r"\b(sql|query|kpi|dashboard|report|metrics|aggregation)\b",
                r"\b(revenue|sales|performance|trend|comparison)\b",
                r"\b(table|chart|visualization|business.?intelligence)\b"
            ],
            "automation": [
                r"\b(automate|workflow|batch|schedule|task.?scheduler)\b",
                r"\b(rename|compress|backup|copy|move|organize)\b",
                r"\b(yaml|sequence|pipeline|orchestration)\b"
            ],
            "cybersecurity": [
                r"\b(scan|audit|security|password|hash|sha256|md5)\b",
                r"\b(vulnerability|threat|risk|compliance|log.?analysis)\b",
                r"\b(ip.?address|suspicious|error|anomaly)\b"
            ],
            "system_control": [
                r"\b(open|launch|start|run|execute|shell|command)\b",
                r"\b(chrome|notepad|calculator|vscode|explorer)\b",
                r"\b(file|folder|directory|path|system)\b"
            ],
            "web_search": [
                r"\b(search|web|internet|scrape|fetch|api|http)\b",
                r"\b(url|website|link|content|extract|parse)\b",
                r"\b(google|bing|yahoo|news|trends)\b"
            ],
            "uiux": [
                r"\b(wireframe|ui|ux|interface|design|component|css|qss)\b",
                r"\b(heuristic|usability|accessibility|user.?experience)\b",
                r"\b(layout|navigation|interaction|prototype)\b"
            ]
        }
        
        self.ml_classifier = None
        self.vectorizer = None
        self.skills = list(self.rule_patterns.keys())
        self.confidence_threshold = 0.3
        self.setup_ml_classifier()
    
    def setup_ml_classifier(self):
        """Initialize ML classifier with synthetic training data"""
        try:
            # Generate synthetic training data
            training_data = self._generate_synthetic_data()
            
            if training_data:
                # Create and train the classifier
                self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
                self.ml_classifier = LogisticRegression(max_iter=1000, random_state=42)
                
                # Create pipeline
                self.pipeline = Pipeline([
                    ('vectorizer', self.vectorizer),
                    ('classifier', self.ml_classifier)
                ])
                
                # Train the model
                texts, labels = zip(*training_data)
                self.pipeline.fit(texts, labels)
                
                logger.info("ML intent classifier trained successfully")
            else:
                logger.warning("Could not generate synthetic training data")
                
        except Exception as e:
            logger.error(f"Failed to setup ML classifier: {e}")
    
    def _generate_synthetic_data(self) -> List[Tuple[str, str]]:
        """Generate synthetic training data for intent classification"""
        synthetic_data = []
        
        # NLP examples
        nlp_examples = [
            "summarize this text for me",
            "rewrite this paragraph",
            "extract requirements from this document",
            "create a project plan",
            "generate a technical brief",
            "write user stories",
            "paraphrase this content"
        ]
        
        # ML examples
        ml_examples = [
            "train a model on this dataset",
            "create a binary classifier",
            "evaluate model performance",
            "show feature importance",
            "run cross validation",
            "tune hyperparameters",
            "make predictions"
        ]
        
        # Data Science examples
        ds_examples = [
            "perform EDA on this data",
            "show data distribution",
            "find missing values",
            "analyze correlations",
            "create visualizations",
            "identify outliers",
            "generate insights"
        ]
        
        # Data Engineering examples
        de_examples = [
            "build an ETL pipeline",
            "extract data from CSV",
            "transform and clean data",
            "load data to database",
            "validate data schema",
            "merge multiple datasets",
            "create data pipeline"
        ]
        
        # Analytics examples
        analytics_examples = [
            "run SQL query",
            "create KPI dashboard",
            "generate business report",
            "analyze sales data",
            "show performance metrics",
            "create data table",
            "build visualization"
        ]
        
        # Automation examples
        automation_examples = [
            "automate file operations",
            "create workflow",
            "schedule backup task",
            "batch rename files",
            "run automation pipeline",
            "organize files",
            "create task sequence"
        ]
        
        # Cybersecurity examples
        security_examples = [
            "scan for security issues",
            "check password strength",
            "verify file hash",
            "analyze log files",
            "audit system security",
            "check for vulnerabilities",
            "monitor suspicious activity"
        ]
        
        # System Control examples
        system_examples = [
            "open chrome browser",
            "launch notepad",
            "start calculator",
            "run shell command",
            "open file explorer",
            "execute system command",
            "launch application"
        ]
        
        # Web Search examples
        web_examples = [
            "search the web",
            "scrape website content",
            "fetch data from API",
            "extract links",
            "parse HTML content",
            "search for information",
            "get web data"
        ]
        
        # UI/UX examples
        ui_examples = [
            "create wireframe",
            "design user interface",
            "review usability",
            "generate CSS",
            "create component tree",
            "evaluate accessibility",
            "design user experience"
        ]
        
        # Add all examples to training data
        for example in nlp_examples:
            synthetic_data.append((example, "nlp"))
        for example in ml_examples:
            synthetic_data.append((example, "ml"))
        for example in ds_examples:
            synthetic_data.append((example, "data_science"))
        for example in de_examples:
            synthetic_data.append((example, "data_engineering"))
        for example in analytics_examples:
            synthetic_data.append((example, "analytics"))
        for example in automation_examples:
            synthetic_data.append((example, "automation"))
        for example in security_examples:
            synthetic_data.append((example, "cybersecurity"))
        for example in system_examples:
            synthetic_data.append((example, "system_control"))
        for example in web_examples:
            synthetic_data.append((example, "web_search"))
        for example in ui_examples:
            synthetic_data.append((example, "uiux"))
        
        return synthetic_data
    
    def classify_intent(self, query: str) -> Tuple[str, float, str]:
        """Classify user intent using hybrid approach"""
        query_lower = query.lower()
        
        # Try rule-based classification first
        rule_result = self._rule_based_classification(query_lower)
        if rule_result:
            skill, confidence = rule_result
            return skill, confidence, "rule_based"
        
        # Fallback to ML classification
        if self.ml_classifier and self.vectorizer:
            try:
                ml_result = self._ml_classification(query_lower)
                if ml_result:
                    skill, confidence = ml_result
                    return skill, confidence, "ml_based"
            except Exception as e:
                logger.warning(f"ML classification failed: {e}")
        
        # Default fallback
        return "nlp", 0.1, "fallback"
    
    def _rule_based_classification(self, query: str) -> Optional[Tuple[str, float]]:
        """Rule-based intent classification"""
        best_match = None
        best_score = 0
        
        for skill, patterns in self.rule_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, query, re.IGNORECASE)
                if matches:
                    score += len(matches) * 0.3  # Weight for pattern matches
            
            # Additional keyword scoring
            skill_keywords = {
                "nlp": ["text", "language", "word", "sentence", "document"],
                "ml": ["machine learning", "ai", "algorithm", "dataset", "training"],
                "data_science": ["data", "analysis", "statistics", "visualization"],
                "data_engineering": ["etl", "pipeline", "data", "process"],
                "analytics": ["sql", "query", "business", "kpi", "report"],
                "automation": ["workflow", "batch", "schedule", "task"],
                "cybersecurity": ["security", "password", "hash", "scan", "audit"],
                "system_control": ["system", "file", "open", "launch", "execute"],
                "web_search": ["web", "internet", "search", "url", "website"],
                "uiux": ["interface", "design", "user", "experience", "ui"]
            }
            
            for keyword in skill_keywords.get(skill, []):
                if keyword in query:
                    score += 0.2
            
            if score > best_score:
                best_score = score
                best_match = skill
        
        if best_match and best_score > 0.1:
            # Normalize confidence to 0-1 range
            confidence = min(best_score / 2.0, 1.0)
            return best_match, confidence
        
        return None
    
    def _ml_classification(self, query: str) -> Optional[Tuple[str, float]]:
        """ML-based intent classification"""
        try:
            # Get prediction probabilities
            proba = self.pipeline.predict_proba([query])[0]
            predicted_class = self.pipeline.predict([query])[0]
            
            # Get confidence for predicted class
            confidence = proba[self.pipeline.classes_.tolist().index(predicted_class)]
            
            if confidence > self.confidence_threshold:
                return predicted_class, confidence
            
            return None
            
        except Exception as e:
            logger.error(f"ML classification error: {e}")
            return None
    
    def get_confidence_threshold(self) -> float:
        """Get current confidence threshold"""
        return self.confidence_threshold
    
    def set_confidence_threshold(self, threshold: float):
        """Set confidence threshold for classification"""
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"Confidence threshold set to: {self.confidence_threshold}")
    
    def get_available_skills(self) -> List[str]:
        """Get list of available skills"""
        return self.skills.copy()
    
    def save_classifier(self, path: str = "temp/intent_classifier.pkl"):
        """Save trained classifier to disk"""
        try:
            if self.pipeline:
                Path(path).parent.mkdir(exist_ok=True)
                with open(path, 'wb') as f:
                    pickle.dump(self.pipeline, f)
                logger.info(f"Intent classifier saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save classifier: {e}")
    
    def load_classifier(self, path: str = "temp/intent_classifier.pkl"):
        """Load trained classifier from disk"""
        try:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    self.pipeline = pickle.load(f)
                self.vectorizer = self.pipeline.named_steps['vectorizer']
                self.ml_classifier = self.pipeline.named_steps['classifier']
                logger.info(f"Intent classifier loaded from {path}")
        except Exception as e:
            logger.error(f"Failed to load classifier: {e}")

class SkillRouter:
    """Routes user queries to appropriate skills"""
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.skill_mappings = {
            "nlp": "skills.nlp.NLPSkill",
            "ml": "skills.ml.MLSkill",
            "data_science": "skills.data_science.DataScienceSkill",
            "data_engineering": "skills.data_engineering.DataEngineeringSkill",
            "analytics": "skills.analytics.AnalyticsSkill",
            "automation": "skills.automation.AutomationSkill",
            "cybersecurity": "skills.cybersecurity.CybersecuritySkill",
            "system_control": "skills.system_control.SystemControlSkill",
            "web_search": "skills.web_search.WebSearchSkill",
            "uiux": "skills.uiux.UIUXSkill"
        }
    
    def route_query(self, query: str, context: Dict[str, Any] = None) -> Tuple[str, float, str, str]:
        """Route a user query to the appropriate skill"""
        context = context or {}
        
        # Classify intent
        skill_name, confidence, method = self.intent_classifier.classify_intent(query)
        
        # Get skill class path
        skill_class_path = self.skill_mappings.get(skill_name, "skills.nlp.NLPSkill")
        
        logger.info(f"Routed query to {skill_name} (confidence: {confidence:.2f}, method: {method})")
        
        return skill_name, confidence, method, skill_class_path
    
    def get_skill_info(self, skill_name: str) -> Dict[str, Any]:
        """Get information about a specific skill"""
        skill_info = {
            "nlp": {
                "name": "Natural Language Processing",
                "description": "Text summarization, rewriting, project planning, and requirement extraction",
                "capabilities": ["Summarization", "Rewriting", "Translation", "Project Planning", "Requirements"]
            },
            "ml": {
                "name": "Machine Learning",
                "description": "Train and evaluate ML models, make predictions, and analyze model performance",
                "capabilities": ["Model Training", "Evaluation", "Prediction", "Feature Analysis", "Hyperparameter Tuning"]
            },
            "data_science": {
                "name": "Data Science",
                "description": "Exploratory data analysis, statistical summaries, and data visualization",
                "capabilities": ["EDA", "Statistical Analysis", "Visualization", "Data Profiling", "Insights Generation"]
            },
            "data_engineering": {
                "name": "Data Engineering",
                "description": "ETL pipelines, data transformation, and database operations",
                "capabilities": ["Data Extraction", "Transformation", "Loading", "Schema Validation", "Pipeline Building"]
            },
            "analytics": {
                "name": "Analytics",
                "description": "SQL queries, KPI dashboards, and business intelligence",
                "capabilities": ["SQL Queries", "Dashboard Creation", "KPI Analysis", "Reporting", "Data Aggregation"]
            },
            "automation": {
                "name": "Automation",
                "description": "Workflow automation, batch operations, and task scheduling",
                "capabilities": ["Workflow Design", "Batch Processing", "Task Scheduling", "File Operations", "Process Orchestration"]
            },
            "cybersecurity": {
                "name": "Cybersecurity",
                "description": "Security scanning, password analysis, and log auditing",
                "capabilities": ["Security Scanning", "Password Analysis", "Hash Verification", "Log Analysis", "Threat Detection"]
            },
            "system_control": {
                "name": "System Control",
                "description": "Application launching, file operations, and system monitoring",
                "capabilities": ["App Launching", "File Operations", "System Monitoring", "Process Control", "System Integration"]
            },
            "web_search": {
                "name": "Web Search",
                "description": "Web scraping, API integration, and content extraction",
                "capabilities": ["Web Scraping", "API Integration", "Content Extraction", "Link Gathering", "Data Collection"]
            },
            "uiux": {
                "name": "UI/UX Design",
                "description": "Interface design, usability review, and component generation",
                "capabilities": ["Wireframe Generation", "Component Design", "Usability Review", "CSS Generation", "User Experience Design"]
            }
        }
        
        return skill_info.get(skill_name, {
            "name": "Unknown Skill",
            "description": "Skill information not available",
            "capabilities": []
        })
    
    def get_all_skills_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available skills"""
        skills_info = {}
        for skill_name in self.skill_mappings.keys():
            skills_info[skill_name] = self.get_skill_info(skill_name)
        return skills_info

# Global router instance
skill_router = SkillRouter()