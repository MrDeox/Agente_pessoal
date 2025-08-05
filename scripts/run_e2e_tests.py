#!/usr/bin/env python3
"""
End-to-end test runner for Personal Agent.

This script runs all end-to-end tests and generates comprehensive reports.
"""

import sys
import os
import subprocess
import argparse
import time
from typing import List, Dict, Any
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tests', 'e2e'))

from test_report_generator import UnifiedTestReport, merge_test_reports


class TestRunner:
    """Main test runner for end-to-end tests."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.test_dir = os.path.join(os.path.dirname(__file__), '..', 'tests', 'e2e')
        self.reports_dir = os.path.join(os.path.dirname(__file__), '..', 'test_reports')
        self.ensure_reports_dir()
    
    def ensure_reports_dir(self):
        """Ensure the reports directory exists."""
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def run_test_suite(self, suite_name: str, script_name: str) -> Dict[str, Any]:
        """Run a single test suite."""
        print(f"\nRunning {suite_name}...")
        print("-" * 50)
        
        script_path = os.path.join(self.test_dir, script_name)
        if not os.path.exists(script_path):
            print(f"Error: Test script {script_path} not found")
            return {
                'suite': suite_name,
                'success': False,
                'error': f"Test script {script_name} not found",
                'duration': 0
            }
        
        start_time = time.time()
        
        try:
            # Run the test script
            result = subprocess.run(
                [sys.executable, script_path],
                cwd=os.path.dirname(script_path),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            duration = time.time() - start_time
            
            # Print output for visibility
            if result.stdout:
                print(result.stdout)
            
            if result.stderr:
                print("STDERR:", result.stderr)
            
            success = result.returncode == 0
            
            print(f"\n{suite_name} {'PASSED' if success else 'FAILED'} (Duration: {duration:.2f}s)")
            
            return {
                'suite': suite_name,
                'success': success,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'duration': duration
            }
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"Error: {suite_name} timed out after {duration:.2f}s")
            return {
                'suite': suite_name,
                'success': False,
                'error': 'Timeout',
                'duration': duration
            }
        except Exception as e:
            duration = time.time() - start_time
            print(f"Error running {suite_name}: {e}")
            return {
                'suite': suite_name,
                'success': False,
                'error': str(e),
                'duration': duration
            }
    
    def run_all_tests(self, selected_suites: List[str] = None) -> Dict[str, Any]:
        """Run all test suites."""
        print("Personal Agent End-to-End Test Runner")
        print("=" * 50)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Define test suites
        all_suites = {
            'conversation_flow': 'test_conversation_flow.py',
            'memory_functionality': 'test_memory_functionality.py',
            'llm_integration': 'test_llm_integration.py',
            'feedback_mechanism': 'test_feedback_mechanism.py',
            'error_handling': 'test_error_handling.py'
        }
        
        # Filter suites if specific ones were selected
        if selected_suites:
            suites_to_run = {k: v for k, v in all_suites.items() if k in selected_suites}
            if not suites_to_run:
                print(f"Warning: No matching suites found for {selected_suites}")
                print(f"Available suites: {list(all_suites.keys())}")
                return {'success': False, 'results': []}
        else:
            suites_to_run = all_suites
        
        print(f"Running {len(suites_to_run)} test suites: {list(suites_to_run.keys())}")
        
        # Run each suite
        results = []
        start_time = time.time()
        
        for suite_name, script_name in suites_to_run.items():
            result = self.run_test_suite(suite_name, script_name)
            results.append(result)
        
        total_duration = time.time() - start_time
        
        # Summary
        passed_suites = sum(1 for r in results if r['success'])
        total_suites = len(results)
        
        print("\n" + "=" * 50)
        print("TEST RUN SUMMARY")
        print("=" * 50)
        print(f"Total suites: {total_suites}")
        print(f"Passed: {passed_suites}")
        print(f"Failed: {total_suites - passed_suites}")
        print(f"Success rate: {passed_suites / total_suites * 100:.1f}%" if total_suites > 0 else "No suites run")
        print(f"Total duration: {total_duration:.2f}s")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        overall_success = passed_suites == total_suites
        print(f"Overall result: {'PASSED' if overall_success else 'FAILED'}")
        
        return {
            'success': overall_success,
            'results': results,
            'total_duration': total_duration,
            'passed_suites': passed_suites,
            'total_suites': total_suites
        }
    
    def generate_unified_report(self, test_results: Dict[str, Any]) -> str:
        """Generate a unified report from individual test results."""
        report = UnifiedTestReport("Personal Agent - End-to-End Test Results")
        
        # Add results from each suite
        for result in test_results['results']:
            suite_result = {
                'name': f"{result['suite']} Suite",
                'passed': result['success'],
                'message': f"Suite completed in {result['duration']:.2f}s",
                'error': result.get('error', None)
            }
            report.add_results_from_suite(result['suite'], [suite_result])
        
        report.set_end_time()
        
        # Save reports
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        text_report_path = os.path.join(self.reports_dir, f'unified_report_{timestamp}.txt')
        json_report_path = os.path.join(self.reports_dir, f'unified_report_{timestamp}.json')
        
        report.save_report(text_report_path, json_report_path)
        
        print(f"\nUnified reports saved:")
        print(f"  Text: {text_report_path}")
        print(f"  JSON: {json_report_path}")
        
        return text_report_path
    
    def merge_existing_reports(self):
        """Merge existing individual test reports into a unified report."""
        # Look for existing test result files
        report_files = []
        for filename in os.listdir('.'):
            if filename.startswith('test_results_') and filename.endswith('.txt'):
                report_files.append(filename)
        
        if report_files:
            print(f"Found {len(report_files)} existing report files:")
            for f in report_files:
                print(f"  - {f}")
            
            unified_report = merge_test_reports(report_files)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            text_report_path = os.path.join(self.reports_dir, f'merged_report_{timestamp}.txt')
            json_report_path = os.path.join(self.reports_dir, f'merged_report_{timestamp}.json')
            
            unified_report.save_report(text_report_path, json_report_path)
            
            print(f"\nMerged reports saved:")
            print(f"  Text: {text_report_path}")
            print(f"  JSON: {json_report_path}")
            
            return text_report_path
        else:
            print("No existing report files found to merge")
            return None


def main():
    """Main function to run the test runner."""
    parser = argparse.ArgumentParser(description='Run Personal Agent end-to-end tests')
    parser.add_argument(
        '--suites',
        nargs='*',
        help='Specific test suites to run (default: all)'
    )
    parser.add_argument(
        '--merge-only',
        action='store_true',
        help='Only merge existing reports, do not run tests'
    )
    parser.add_argument(
        '--list-suites',
        action='store_true',
        help='List available test suites'
    )
    
    args = parser.parse_args()
    
    # List suites if requested
    if args.list_suites:
        print("Available test suites:")
        suites = [
            'conversation_flow',
            'memory_functionality',
            'llm_integration',
            'feedback_mechanism',
            'error_handling'
        ]
        for suite in suites:
            print(f"  - {suite}")
        return 0
    
    # Create test runner
    runner = TestRunner()
    
    # Merge existing reports only if requested
    if args.merge_only:
        merged_report = runner.merge_existing_reports()
        if merged_report:
            print(f"\nMerged report generated: {merged_report}")
            return 0
        else:
            print("No reports to merge")
            return 1
    
    # Run tests
    test_results = runner.run_all_tests(args.suites)
    
    # Generate unified report
    if test_results['results']:
        unified_report_path = runner.generate_unified_report(test_results)
        print(f"\nUnified report generated: {unified_report_path}")
    
    # Return appropriate exit code
    return 0 if test_results['success'] else 1


if __name__ == "__main__":
    sys.exit(main())