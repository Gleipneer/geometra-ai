"""
Evaluation reports implementation for Geometra AI.
Handles generation of evaluation reports and visualizations.
"""

from typing import List, Dict, Any
import json
import datetime
import matplotlib.pyplot as plt
import seaborn as sns

class ReportGenerator:
    """Report generator for Geometra AI."""
    
    def __init__(self):
        """Initialize report generator."""
        self.reports = []
    
    def generate_metrics_report(
        self,
        metrics: Dict[str, float],
        model_name: str,
        timestamp: str = None
    ) -> Dict[str, Any]:
        """Generate metrics report.
        
        Args:
            metrics: Dictionary of metrics
            model_name: Name of the model
            timestamp: Optional timestamp
            
        Returns:
            Report dictionary
        """
        if timestamp is None:
            timestamp = datetime.datetime.now().isoformat()
            
        report = {
            'timestamp': timestamp,
            'model_name': model_name,
            'metrics': metrics
        }
        
        self.reports.append(report)
        return report
    
    def generate_performance_report(
        self,
        response_times: List[float],
        token_usage: List[Dict[str, int]],
        model_name: str
    ) -> Dict[str, Any]:
        """Generate performance report.
        
        Args:
            response_times: List of response times
            token_usage: List of token usage dictionaries
            model_name: Name of the model
            
        Returns:
            Report dictionary
        """
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'model_name': model_name,
            'performance': {
                'avg_response_time': sum(response_times) / len(response_times),
                'total_tokens': sum(usage['total_tokens'] for usage in token_usage),
                'avg_tokens_per_request': sum(usage['total_tokens'] for usage in token_usage) / len(token_usage)
            }
        }
        
        self.reports.append(report)
        return report
    
    def plot_metrics_history(
        self,
        metrics_history: List[Dict[str, float]],
        save_path: str = None
    ):
        """Plot metrics history.
        
        Args:
            metrics_history: List of metric dictionaries
            save_path: Optional path to save plot
        """
        plt.figure(figsize=(10, 6))
        
        for metric in ['accuracy', 'precision', 'recall', 'f1_score']:
            values = [m[metric] for m in metrics_history]
            plt.plot(values, label=metric)
        
        plt.title('Metrics History')
        plt.xlabel('Evaluation Step')
        plt.ylabel('Score')
        plt.legend()
        plt.grid(True)
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
    
    def save_reports(self, filepath: str):
        """Save reports to file.
        
        Args:
            filepath: Path to save reports
        """
        with open(filepath, 'w') as f:
            json.dump(self.reports, f, indent=2)
    
    def load_reports(self, filepath: str):
        """Load reports from file.
        
        Args:
            filepath: Path to load reports from
        """
        with open(filepath, 'r') as f:
            self.reports = json.load(f) 