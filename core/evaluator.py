"""
Evaluator module for JarvisX
Handles skill auto-tests and performance evaluation
"""

import time
import json
import statistics
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from loguru import logger
from core.assistant import JarvisXAssistant
from skills.base_skill import BaseSkill

class SkillEvaluator:
    """Evaluates skill performance and functionality"""
    
    def __init__(self, assistant: JarvisXAssistant):
        self.assistant = assistant
        self.test_results = {}
        self.performance_metrics = {}
        
    def run_skill_tests(self, skill_name: Optional[str] = None) -> Dict:
        """Run tests for all skills or a specific skill"""
        try:
            logger.info("Starting skill evaluation")
            
            if skill_name:
                skills_to_test = [skill_name]
            else:
                skills_to_test = self._get_available_skills()
            
            results = {}
            for skill in skills_to_test:
                logger.info(f"Testing skill: {skill}")
                skill_results = self._test_skill(skill)
                results[skill] = skill_results
            
            self.test_results = results
            logger.info("Skill evaluation completed")
            return results
            
        except Exception as e:
            logger.error(f"Error during skill evaluation: {e}")
            return {'error': str(e)}
    
    def evaluate_performance(self, skill_name: str, num_iterations: int = 10) -> Dict:
        """Evaluate performance metrics for a specific skill"""
        try:
            logger.info(f"Evaluating performance for skill: {skill_name}")
            
            # Get test queries for the skill
            test_queries = self._get_test_queries(skill_name)
            if not test_queries:
                return {'error': 'No test queries available'}
            
            metrics = {
                'skill_name': skill_name,
                'iterations': num_iterations,
                'response_times': [],
                'success_rate': 0,
                'error_rate': 0,
                'average_response_time': 0,
                'min_response_time': 0,
                'max_response_time': 0,
                'std_deviation': 0
            }
            
            successful_runs = 0
            total_runs = num_iterations * len(test_queries)
            
            for _ in range(num_iterations):
                for query in test_queries:
                    start_time = time.time()
                    
                    try:
                        result = self.assistant.process_message(query, "test_user")
                        end_time = time.time()
                        
                        response_time = end_time - start_time
                        metrics['response_times'].append(response_time)
                        
                        if result.get('type') != 'error':
                            successful_runs += 1
                            
                    except Exception as e:
                        logger.warning(f"Error during performance test: {e}")
                        metrics['response_times'].append(float('inf'))
            
            # Calculate metrics
            if metrics['response_times']:
                valid_times = [t for t in metrics['response_times'] if t != float('inf')]
                if valid_times:
                    metrics['average_response_time'] = statistics.mean(valid_times)
                    metrics['min_response_time'] = min(valid_times)
                    metrics['max_response_time'] = max(valid_times)
                    if len(valid_times) > 1:
                        metrics['std_deviation'] = statistics.stdev(valid_times)
            
            metrics['success_rate'] = successful_runs / total_runs if total_runs > 0 else 0
            metrics['error_rate'] = 1 - metrics['success_rate']
            
            self.performance_metrics[skill_name] = metrics
            logger.info(f"Performance evaluation completed for {skill_name}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error during performance evaluation: {e}")
            return {'error': str(e)}
    
    def generate_evaluation_report(self) -> Dict:
        """Generate comprehensive evaluation report"""
        try:
            logger.info("Generating evaluation report")
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'summary': {},
                'skill_tests': self.test_results,
                'performance_metrics': self.performance_metrics,
                'recommendations': []
            }
            
            # Generate summary
            total_skills = len(self.test_results)
            passed_tests = sum(1 for skill_results in self.test_results.values() 
                             if skill_results.get('status') == 'passed')
            
            report['summary'] = {
                'total_skills': total_skills,
                'passed_tests': passed_tests,
                'failed_tests': total_skills - passed_tests,
                'success_rate': passed_tests / total_skills if total_skills > 0 else 0
            }
            
            # Generate recommendations
            recommendations = self._generate_recommendations()
            report['recommendations'] = recommendations
            
            logger.info("Evaluation report generated")
            return report
            
        except Exception as e:
            logger.error(f"Error generating evaluation report: {e}")
            return {'error': str(e)}
    
    def _test_skill(self, skill_name: str) -> Dict:
        """Test a specific skill"""
        try:
            # Get skill instance
            skill = self._get_skill_instance(skill_name)
            if not skill:
                return {'status': 'failed', 'error': 'Skill not found'}
            
            # Run basic functionality tests
            test_results = {
                'skill_name': skill_name,
                'status': 'passed',
                'tests': {},
                'errors': []
            }
            
            # Test 1: Skill initialization
            try:
                info = skill.get_info()
                test_results['tests']['initialization'] = {
                    'status': 'passed',
                    'name': info.get('name'),
                    'description': info.get('description'),
                    'capabilities': info.get('capabilities', [])
                }
            except Exception as e:
                test_results['tests']['initialization'] = {
                    'status': 'failed',
                    'error': str(e)
                }
                test_results['status'] = 'failed'
                test_results['errors'].append(f"Initialization failed: {e}")
            
            # Test 2: Input validation
            try:
                valid_input = "This is a valid test input"
                invalid_input = ""
                
                valid_result = skill.validate_input(valid_input)
                invalid_result = skill.validate_input(invalid_input)
                
                test_results['tests']['input_validation'] = {
                    'status': 'passed',
                    'valid_input_result': valid_result,
                    'invalid_input_result': invalid_result
                }
            except Exception as e:
                test_results['tests']['input_validation'] = {
                    'status': 'failed',
                    'error': str(e)
                }
                test_results['status'] = 'failed'
                test_results['errors'].append(f"Input validation failed: {e}")
            
            # Test 3: Query preprocessing
            try:
                test_query = "  Test query with whitespace  "
                processed = skill.preprocess_query(test_query)
                
                test_results['tests']['query_preprocessing'] = {
                    'status': 'passed',
                    'original': test_query,
                    'processed': processed
                }
            except Exception as e:
                test_results['tests']['query_preprocessing'] = {
                    'status': 'failed',
                    'error': str(e)
                }
                test_results['status'] = 'failed'
                test_results['errors'].append(f"Query preprocessing failed: {e}")
            
            # Test 4: Usage examples
            try:
                examples = skill.get_usage_examples()
                test_results['tests']['usage_examples'] = {
                    'status': 'passed',
                    'count': len(examples),
                    'examples': examples[:3]  # First 3 examples
                }
            except Exception as e:
                test_results['tests']['usage_examples'] = {
                    'status': 'failed',
                    'error': str(e)
                }
                test_results['status'] = 'failed'
                test_results['errors'].append(f"Usage examples failed: {e}")
            
            # Test 5: Help text
            try:
                help_text = skill.get_help_text()
                test_results['tests']['help_text'] = {
                    'status': 'passed',
                    'length': len(help_text),
                    'preview': help_text[:100] + "..." if len(help_text) > 100 else help_text
                }
            except Exception as e:
                test_results['tests']['help_text'] = {
                    'status': 'failed',
                    'error': str(e)
                }
                test_results['status'] = 'failed'
                test_results['errors'].append(f"Help text failed: {e}")
            
            # Test 6: Basic execution (if safe)
            if self._is_safe_to_execute(skill_name):
                try:
                    result = skill.run("Test query", {})
                    test_results['tests']['basic_execution'] = {
                        'status': 'passed',
                        'result_type': result.get('type'),
                        'has_content': bool(result.get('content')),
                        'has_metadata': bool(result.get('metadata'))
                    }
                except Exception as e:
                    test_results['tests']['basic_execution'] = {
                        'status': 'failed',
                        'error': str(e)
                    }
                    test_results['status'] = 'failed'
                    test_results['errors'].append(f"Basic execution failed: {e}")
            
            return test_results
            
        except Exception as e:
            logger.error(f"Error testing skill {skill_name}: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _get_available_skills(self) -> List[str]:
        """Get list of available skill names"""
        try:
            skills_info = self.assistant.get_available_skills()
            return [skill['name'].lower().replace(' ', '_') for skill in skills_info]
        except Exception:
            return ['nlp', 'ml', 'data_science', 'data_engineering', 'analytics', 
                   'automation', 'cybersecurity', 'system_control', 'ui_ux', 'web_search']
    
    def _get_skill_instance(self, skill_name: str) -> Optional[BaseSkill]:
        """Get skill instance by name"""
        try:
            # Map skill names to module paths
            skill_mapping = {
                'nlp': 'skills.nlp.NLPSkill',
                'ml': 'skills.ml.MLSkill',
                'data_science': 'skills.data_science.DataScienceSkill',
                'data_engineering': 'skills.data_engineering.DataEngineeringSkill',
                'analytics': 'skills.analytics.AnalyticsSkill',
                'automation': 'skills.automation.AutomationSkill',
                'cybersecurity': 'skills.cybersecurity.CybersecuritySkill',
                'system_control': 'skills.system_control.SystemControlSkill',
                'ui_ux': 'skills.ui_ux.UIUXSkill',
                'web_search': 'skills.web_search.WebSearchSkill'
            }
            
            if skill_name not in skill_mapping:
                return None
            
            module_path = skill_mapping[skill_name]
            module_name, class_name = module_path.rsplit('.', 1)
            
            module = __import__(module_name, fromlist=[class_name])
            skill_class = getattr(module, class_name)
            
            return skill_class()
            
        except Exception as e:
            logger.error(f"Error getting skill instance for {skill_name}: {e}")
            return None
    
    def _get_test_queries(self, skill_name: str) -> List[str]:
        """Get test queries for a specific skill"""
        # Define test queries for each skill
        test_queries = {
            'nlp': [
                "Summarize this text",
                "Translate 'Hello world' to Spanish",
                "Extract requirements from this document"
            ],
            'ml': [
                "Train a simple model",
                "Evaluate model performance",
                "Make a prediction"
            ],
            'data_science': [
                "Analyze this dataset",
                "Create a visualization",
                "Perform data profiling"
            ],
            'data_engineering': [
                "Process this data",
                "Transform data format",
                "Clean this dataset"
            ],
            'analytics': [
                "Generate insights",
                "Create a report",
                "Analyze trends"
            ],
            'automation': [
                "Automate this task",
                "Create a workflow",
                "Schedule a job"
            ],
            'cybersecurity': [
                "Scan for vulnerabilities",
                "Analyze security logs",
                "Check file integrity"
            ],
            'system_control': [
                "Check system status",
                "Monitor resources",
                "Get system info"
            ],
            'ui_ux': [
                "Design a wireframe",
                "Create a prototype",
                "Analyze user experience"
            ],
            'web_search': [
                "Search for information",
                "Scrape this website",
                "Extract data from web"
            ]
        }
        
        return test_queries.get(skill_name, ["Test query"])
    
    def _is_safe_to_execute(self, skill_name: str) -> bool:
        """Check if it's safe to execute a skill for testing"""
        # Skills that are safe to execute in test environment
        safe_skills = ['nlp', 'ui_ux', 'web_search']
        
        # Skills that might have side effects
        risky_skills = ['ml', 'data_science', 'data_engineering', 'analytics', 
                       'automation', 'cybersecurity', 'system_control']
        
        return skill_name in safe_skills
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Analyze test results
        failed_skills = [skill for skill, results in self.test_results.items() 
                        if results.get('status') == 'failed']
        
        if failed_skills:
            recommendations.append(f"Fix failing tests for skills: {', '.join(failed_skills)}")
        
        # Analyze performance metrics
        for skill_name, metrics in self.performance_metrics.items():
            if metrics.get('success_rate', 0) < 0.8:
                recommendations.append(f"Improve reliability of {skill_name} skill")
            
            avg_response_time = metrics.get('average_response_time', 0)
            if avg_response_time > 5.0:  # More than 5 seconds
                recommendations.append(f"Optimize performance of {skill_name} skill")
        
        # General recommendations
        if not recommendations:
            recommendations.append("All skills are performing well")
        
        return recommendations
    
    def save_report(self, report: Dict, filename: str = None) -> bool:
        """Save evaluation report to file"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"evaluation_report_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Evaluation report saved to: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving evaluation report: {e}")
            return False
    
    def load_report(self, filename: str) -> Optional[Dict]:
        """Load evaluation report from file"""
        try:
            with open(filename, 'r') as f:
                report = json.load(f)
            
            logger.info(f"Evaluation report loaded from: {filename}")
            return report
            
        except Exception as e:
            logger.error(f"Error loading evaluation report: {e}")
            return None