#!/usr/bin/env python3
"""
Test reporter for Geometra AI system.

Collects test results from pytest runs and generates reports in various formats.
Handles test failures, performance metrics, and generates alerts.
"""

import os
import json
import time
import datetime
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        RotatingFileHandler('logs/test_reporter.log', maxBytes=1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)

@dataclass
class TestResult:
    """Test result data class."""
    test_id: str
    name: str
    status: str
    duration: float
    timestamp: str
    component: str
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    stack_trace: Optional[str] = None

class TestReporter:
    """Test reporter implementation."""
    
    def __init__(self, output_dir: str = 'test_reports'):
        """Initialize test reporter.
        
        Args:
            output_dir: Directory to store test reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[TestResult] = []
        self.start_time = time.time()
    
    def run_tests(self) -> bool:
        """Run pytest suite and collect results.
        
        Returns:
            bool: True if all tests passed, False otherwise
        """
        try:
            # Run pytest with JSON output
            result = subprocess.run(
                ['pytest', 'tests', '--json-report', '--json-report-file=none'],
                capture_output=True,
                text=True
            )
            
            # Parse JSON output
            if result.stdout:
                try:
                    report = json.loads(result.stdout)
                    self._process_report(report)
                except json.JSONDecodeError:
                    logging.error("Failed to parse pytest JSON output")
                    return False
            
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Error running tests: {e}")
            return False
    
    def _process_report(self, report: Dict[str, Any]):
        """Process pytest report.
        
        Args:
            report: Pytest report dictionary
        """
        for test in report.get('tests', []):
            result = TestResult(
                test_id=test.get('nodeid', ''),
                name=test.get('name', ''),
                status=test.get('outcome', ''),
                duration=test.get('duration', 0.0),
                timestamp=datetime.datetime.now().isoformat(),
                component=self._extract_component(test.get('nodeid', '')),
                error_message=test.get('error_message'),
                error_type=test.get('error_type'),
                stack_trace=test.get('stack_trace')
            )
            self.results.append(result)
    
    def _extract_component(self, test_id: str) -> str:
        """Extract component name from test ID.
        
        Args:
            test_id: Test identifier
            
        Returns:
            str: Component name
        """
        parts = test_id.split('::')
        if len(parts) > 1:
            return parts[0]
        return 'unknown'
    
    def generate_reports(self):
        """Generate test reports in various formats."""
        # Generate JSON report
        self._generate_json_report()
        
        # Generate HTML report
        self._generate_html_report()
        
        # Generate summary
        self._generate_summary()
        
        # Generate alerts if needed
        self._generate_alerts()
    
    def _generate_json_report(self):
        """Generate JSON report."""
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'duration': time.time() - self.start_time,
            'total_tests': len(self.results),
            'passed_tests': len([r for r in self.results if r.status == 'passed']),
            'failed_tests': len([r for r in self.results if r.status == 'failed']),
            'skipped_tests': len([r for r in self.results if r.status == 'skipped']),
            'results': [asdict(r) for r in self.results]
        }
        
        output_file = self.output_dir / 'test_report.json'
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logging.info(f"Generated JSON report: {output_file}")
    
    def _generate_html_report(self):
        """Generate HTML report."""
        html = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<title>Test Report</title>',
            '<style>',
            'body { font-family: Arial, sans-serif; margin: 20px; }',
            '.test { margin: 10px 0; padding: 10px; border: 1px solid #ddd; }',
            '.passed { background-color: #dff0d8; }',
            '.failed { background-color: #f2dede; }',
            '.skipped { background-color: #fcf8e3; }',
            '</style>',
            '</head>',
            '<body>',
            f'<h1>Test Report - {datetime.datetime.now().isoformat()}</h1>',
            f'<p>Total tests: {len(self.results)}</p>',
            f'<p>Passed: {len([r for r in self.results if r.status == "passed"])}</p>',
            f'<p>Failed: {len([r for r in self.results if r.status == "failed"])}</p>',
            f'<p>Skipped: {len([r for r in self.results if r.status == "skipped"])}</p>',
            '<h2>Test Results</h2>'
        ]
        
        for result in self.results:
            html.extend([
                f'<div class="test {result.status}">',
                f'<h3>{result.name}</h3>',
                f'<p>Component: {result.component}</p>',
                f'<p>Status: {result.status}</p>',
                f'<p>Duration: {result.duration:.2f}s</p>'
            ])
            
            if result.error_message:
                html.extend([
                    f'<p>Error: {result.error_message}</p>',
                    f'<p>Type: {result.error_type}</p>',
                    f'<pre>{result.stack_trace}</pre>'
                ])
            
            html.append('</div>')
        
        html.extend(['</body>', '</html>'])
        
        output_file = self.output_dir / 'test_report.html'
        with open(output_file, 'w') as f:
            f.write('\n'.join(html))
        
        logging.info(f"Generated HTML report: {output_file}")
    
    def _generate_summary(self):
        """Generate test summary."""
        summary = {
            'timestamp': datetime.datetime.now().isoformat(),
            'duration': time.time() - self.start_time,
            'total_tests': len(self.results),
            'passed_tests': len([r for r in self.results if r.status == 'passed']),
            'failed_tests': len([r for r in self.results if r.status == 'failed']),
            'skipped_tests': len([r for r in self.results if r.status == 'skipped']),
            'components': {
                component: {
                    'total': len([r for r in self.results if r.component == component]),
                    'passed': len([r for r in self.results if r.component == component and r.status == 'passed']),
                    'failed': len([r for r in self.results if r.component == component and r.status == 'failed']),
                    'skipped': len([r for r in self.results if r.component == component and r.status == 'skipped'])
                }
                for component in set(r.component for r in self.results)
            }
        }
        
        output_file = self.output_dir / 'test_summary.json'
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logging.info(f"Generated test summary: {output_file}")
    
    def _generate_alerts(self):
        """Generate alerts for test failures."""
        failed_tests = [r for r in self.results if r.status == 'failed']
        if not failed_tests:
            return
        
        alerts = {
            'timestamp': datetime.datetime.now().isoformat(),
            'total_failures': len(failed_tests),
            'failures': [
                {
                    'test_id': r.test_id,
                    'name': r.name,
                    'component': r.component,
                    'error_message': r.error_message,
                    'error_type': r.error_type
                }
                for r in failed_tests
            ]
        }
        
        output_file = self.output_dir / 'test_alerts.json'
        with open(output_file, 'w') as f:
            json.dump(alerts, f, indent=2)
        
        logging.info(f"Generated alerts for {len(failed_tests)} failed tests: {output_file}")

def main():
    """Main entry point."""
    reporter = TestReporter()
    
    # Run tests
    success = reporter.run_tests()
    
    # Generate reports
    reporter.generate_reports()
    
    # Exit with appropriate status code
    exit(0 if success else 1)

if __name__ == '__main__':
    main() 