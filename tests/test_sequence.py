"""Master test sequence for Geometra AI system.

This module orchestrates the execution of all test suites in the correct order,
following the system's development flow from setup to deployment.
"""

import os
import sys
import logging
import pytest
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    filename='bootstrap_status.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TestSequence:
    """Manages the execution of test suites in sequence."""
    
    def __init__(self, start_from: Optional[str] = None):
        self.test_suites = [
            {
                'name': 'System Overview',
                'path': 'tests/unit/system/test_system_overview.py',
                'dependencies': []
            },
            {
                'name': 'Project Setup',
                'path': 'tests/unit/setup/test_project_setup.py',
                'dependencies': ['System Overview']
            },
            {
                'name': 'Memory Configuration',
                'path': 'tests/unit/memory/test_memory_config.py',
                'dependencies': ['Project Setup']
            },
            {
                'name': 'Backend Setup',
                'path': 'tests/unit/backend/test_backend_setup.py',
                'dependencies': ['Memory Configuration']
            },
            {
                'name': 'Frontend Setup',
                'path': 'tests/unit/frontend/test_frontend_setup.py',
                'dependencies': ['Backend Setup']
            },
            {
                'name': 'AI Setup',
                'path': 'tests/unit/ai/test_ai_setup.py',
                'dependencies': ['Frontend Setup']
            },
            {
                'name': 'AI Routing',
                'path': 'tests/unit/ai/test_ai_routing.py',
                'dependencies': ['AI Setup']
            },
            {
                'name': 'Fallback Logic',
                'path': 'tests/unit/ai/test_fallback_logic.py',
                'dependencies': ['AI Routing']
            },
            {
                'name': 'System Check',
                'path': 'tests/unit/system/test_system_check.py',
                'dependencies': ['Fallback Logic']
            },
            {
                'name': 'Testing Setup',
                'path': 'tests/unit/test/test_test_setup.py',
                'dependencies': ['System Check']
            },
            {
                'name': 'CI Setup',
                'path': 'tests/unit/ci/test_ci_setup.py',
                'dependencies': ['Testing Setup']
            },
            {
                'name': 'CD Setup',
                'path': 'tests/unit/cd/test_cd_setup.py',
                'dependencies': ['CI Setup']
            },
            {
                'name': 'Post-Deployment Monitoring',
                'path': 'tests/unit/monitoring/test_post_deploy_monitoring.py',
                'dependencies': ['CD Setup']
            },
            {
                'name': 'Security',
                'path': 'tests/unit/security/test_security.py',
                'dependencies': ['Post-Deployment Monitoring']
            },
            {
                'name': 'Documentation',
                'path': 'tests/unit/docs/test_documentation.py',
                'dependencies': ['Security']
            },
            {
                'name': 'Backup',
                'path': 'tests/unit/backup/test_backup.py',
                'dependencies': ['Documentation']
            },
            {
                'name': 'Disaster Recovery',
                'path': 'tests/unit/dr/test_disaster_recovery.py',
                'dependencies': ['Backup']
            },
            {
                'name': 'Architecture Diagrams',
                'path': 'tests/unit/architecture/test_architecture_diagrams.py',
                'dependencies': ['Disaster Recovery']
            }
        ]
        
        self.completed_tests = set()
        self.failed_tests = set()
        self.start_from = start_from
        
        if start_from:
            self._load_completed_tests()
        
    def _load_completed_tests(self):
        """Load completed tests from bootstrap_status.log."""
        try:
            with open('bootstrap_status.log', 'r') as f:
                for line in f:
                    if '✓' in line:
                        test_name = line.split('✓')[1].strip()
                        self.completed_tests.add(test_name)
        except FileNotFoundError:
            self.log_status("No bootstrap_status.log found, starting fresh")
            
    def log_status(self, message: str, level: str = 'INFO'):
        """Log status message to bootstrap_status.log."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        
        if level == 'ERROR':
            logging.error(log_message)
            print(f"\033[91m{log_message}\033[0m")  # Red color for errors
        elif level == 'WARNING':
            logging.warning(log_message)
            print(f"\033[93m{log_message}\033[0m")  # Yellow color for warnings
        else:
            logging.info(log_message)
            print(f"\033[92m{log_message}\033[0m")  # Green color for info
            
    def check_dependencies(self, test_suite: Dict) -> bool:
        """Check if all dependencies for a test suite are met."""
        for dep in test_suite['dependencies']:
            if dep not in self.completed_tests:
                return False
        return True
        
    def run_test_suite(self, test_suite: Dict) -> bool:
        """Run a single test suite and return success status."""
        self.log_status(f"Running test suite: {test_suite['name']}")
        
        try:
            # Run pytest for the specific test file
            result = pytest.main([test_suite['path'], '-v'])
            
            if result == 0:  # pytest returns 0 on success
                self.completed_tests.add(test_suite['name'])
                self.log_status(f"✓ {test_suite['name']} completed successfully")
                return True
            else:
                self.failed_tests.add(test_suite['name'])
                self.log_status(
                    f"✗ {test_suite['name']} failed with exit code {result}",
                    level='ERROR'
                )
                return False
                
        except Exception as e:
            self.failed_tests.add(test_suite['name'])
            self.log_status(
                f"✗ Error running {test_suite['name']}: {str(e)}",
                level='ERROR'
            )
            return False
            
    def run_all_tests(self) -> bool:
        """Run all test suites in sequence."""
        if self.start_from:
            self.log_status(f"Resuming test sequence from: {self.start_from}")
        else:
            self.log_status("Starting test sequence")
        
        while len(self.completed_tests) + len(self.failed_tests) < len(self.test_suites):
            progress_made = False
            
            for test_suite in self.test_suites:
                if (test_suite['name'] not in self.completed_tests and 
                    test_suite['name'] not in self.failed_tests):
                    
                    # Skip tests before start_from if resuming
                    if self.start_from and test_suite['name'] != self.start_from:
                        continue
                        
                    if self.check_dependencies(test_suite):
                        success = self.run_test_suite(test_suite)
                        progress_made = True
                        
                        if not success:
                            self.log_status(
                                f"Test sequence paused due to failure in {test_suite['name']}",
                                level='ERROR'
                            )
                            return False
                            
            if not progress_made:
                self.log_status(
                    "No progress can be made due to failed dependencies",
                    level='ERROR'
                )
                return False
                
        self.log_status("All test suites completed successfully")
        return True

def main():
    """Main entry point for test sequence."""
    parser = argparse.ArgumentParser(description='Run test sequence')
    parser.add_argument(
        '--start-from',
        help='Resume test sequence from specified test suite'
    )
    args = parser.parse_args()
    
    # Set PYTHONPATH to project root
    project_root = Path(__file__).parent.parent
    os.environ['PYTHONPATH'] = str(project_root)
    
    sequence = TestSequence(start_from=args.start_from)
    success = sequence.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main() 