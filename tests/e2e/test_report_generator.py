#!/usr/bin/env python3
"""
Test report generator for personal agent end-to-end tests.

This module provides unified reporting functionality for all test suites.
"""

import os
import json
import sys
from datetime import datetime
from typing import List, Dict, Any


class UnifiedTestResult:
    """Represents a unified test result from any test suite."""
    
    def __init__(self, suite_name: str, test_name: str, passed: bool, message: str = "", error: str = None):
        self.suite_name = suite_name
        self.test_name = test_name
        self.passed = passed
        self.message = message
        self.error = error
        self.timestamp = datetime.now()


class UnifiedTestReport:
    """Generates and manages unified test reports across all test suites."""
    
    def __init__(self, report_title: str = "Personal Agent - Unified Test Report"):
        self.report_title = report_title
        self.results: List[UnifiedTestResult] = []
        self.start_time = datetime.now()
        self.end_time = None
    
    def add_result(self, result: UnifiedTestResult):
        """Add a test result to the unified report."""
        self.results.append(result)
    
    def add_results_from_suite(self, suite_name: str, results: List[Any]):
        """Add results from a test suite."""
        for result in results:
            unified_result = UnifiedTestResult(
                suite_name=suite_name,
                test_name=result.name if hasattr(result, 'name') else 'Unknown Test',
                passed=result.passed if hasattr(result, 'passed') else False,
                message=result.message if hasattr(result, 'message') else '',
                error=str(result.error) if hasattr(result, 'error') and result.error else None
            )
            self.add_result(unified_result)
    
    def set_end_time(self):
        """Set the end time for the test run."""
        self.end_time = datetime.now()
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for the test run."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        # Group by suite
        suite_stats = {}
        for result in self.results:
            if result.suite_name not in suite_stats:
                suite_stats[result.suite_name] = {'total': 0, 'passed': 0, 'failed': 0}
            suite_stats[result.suite_name]['total'] += 1
            if result.passed:
                suite_stats[result.suite_name]['passed'] += 1
            else:
                suite_stats[result.suite_name]['failed'] += 1
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': passed_tests / total_tests * 100 if total_tests > 0 else 0,
            'suite_stats': suite_stats,
            'duration': (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        }
    
    def generate_text_report(self) -> str:
        """Generate a formatted text report."""
        stats = self.get_summary_stats()
        
        report = []
        report.append("=" * 80)
        report.append(self.report_title.upper())
        report.append("=" * 80)
        report.append(f"Test Run: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        if self.end_time:
            report.append(f"Completed: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            report.append(f"Duration: {stats['duration']:.2f} seconds")
        report.append(f"Total Tests: {stats['total_tests']}")
        report.append(f"Passed: {stats['passed_tests']}")
        report.append(f"Failed: {stats['failed_tests']}")
        report.append(f"Success Rate: {stats['success_rate']:.1f}%")
        report.append("")
        
        # Suite breakdown
        report.append("SUITE BREAKDOWN:")
        report.append("-" * 40)
        for suite_name, suite_data in stats['suite_stats'].items():
            suite_rate = suite_data['passed'] / suite_data['total'] * 100 if suite_data['total'] > 0 else 0
            report.append(f"{suite_name}:")
            report.append(f"  Total: {suite_data['total']}, Passed: {suite_data['passed']}, Failed: {suite_data['failed']} ({suite_rate:.1f}%)")
        report.append("")
        
        # Failed tests details
        failed_results = [r for r in self.results if not r.passed]
        if failed_results:
            report.append("FAILED TESTS DETAILS:")
            report.append("-" * 40)
            for result in failed_results:
                report.append(f"[{result.suite_name}] {result.test_name}")
                report.append(f"  Message: {result.message}")
                if result.error:
                    report.append(f"  Error: {result.error}")
                report.append("")
        
        # Summary
        report.append("-" * 40)
        overall_status = "PASSED" if stats['failed_tests'] == 0 else "FAILED"
        report.append(f"OVERALL STATUS: {overall_status}")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def generate_json_report(self) -> str:
        """Generate a JSON report."""
        stats = self.get_summary_stats()
        
        report_data = {
            "title": self.report_title,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": stats['duration'],
            "summary": {
                "total_tests": stats['total_tests'],
                "passed_tests": stats['passed_tests'],
                "failed_tests": stats['failed_tests'],
                "success_rate": stats['success_rate']
            },
            "suite_breakdown": stats['suite_stats'],
            "failed_tests": [
                {
                    "suite": result.suite_name,
                    "test": result.test_name,
                    "message": result.message,
                    "error": result.error
                }
                for result in self.results if not result.passed
            ],
            "all_results": [
                {
                    "suite": result.suite_name,
                    "test": result.test_name,
                    "passed": result.passed,
                    "message": result.message,
                    "error": result.error,
                    "timestamp": result.timestamp.isoformat()
                }
                for result in self.results
            ]
        }
        
        return json.dumps(report_data, indent=2)
    
    def save_report(self, text_path: str = None, json_path: str = None):
        """Save the report to files."""
        if text_path:
            with open(text_path, 'w') as f:
                f.write(self.generate_text_report())
        
        if json_path:
            with open(json_path, 'w') as f:
                f.write(self.generate_json_report())


def merge_test_reports(report_files: List[str]) -> UnifiedTestReport:
    """Merge individual test reports into a unified report."""
    unified_report = UnifiedTestReport()
    
    for report_file in report_files:
        if not os.path.exists(report_file):
            print(f"Warning: Report file {report_file} not found")
            continue
            
        # Try to parse as JSON first (more structured data)
        try:
            with open(report_file, 'r') as f:
                content = f.read()
            
            # If it's a JSON report, parse it
            if content.strip().startswith('{'):
                report_data = json.loads(content)
                if 'all_results' in report_data:
                    for result_data in report_data['all_results']:
                        result = UnifiedTestResult(
                            suite_name=result_data['suite'],
                            test_name=result_data['test'],
                            passed=result_data['passed'],
                            message=result_data['message'],
                            error=result_data['error']
                        )
                        result.timestamp = datetime.fromisoformat(result_data['timestamp'])
                        unified_report.add_result(result)
            else:
                # If it's a text report, we can't easily parse individual results
                # Just add a placeholder result
                suite_name = os.path.basename(report_file).replace('test_results_', '').replace('.txt', '')
                result = UnifiedTestResult(
                    suite_name=suite_name,
                    test_name="Suite Summary",
                    passed="FAILED" not in content,
                    message=f"Results from {report_file}"
                )
                unified_report.add_result(result)
                
        except Exception as e:
            print(f"Warning: Could not parse report file {report_file}: {e}")
            # Add a placeholder result
            suite_name = os.path.basename(report_file).replace('test_results_', '').replace('.txt', '')
            result = UnifiedTestResult(
                suite_name=suite_name,
                test_name="Parse Error",
                passed=False,
                message=f"Could not parse report file: {e}"
            )
            unified_report.add_result(result)
    
    unified_report.set_end_time()
    return unified_report


def main():
    """Main function for testing the report generator."""
    # This is just for testing the report generator itself
    report = UnifiedTestReport("Test Report Generator Test")
    
    # Add some sample results
    from unittest import TestCase
    sample_results = [
        TestCase().assertTrue(True),  # This is just to create a mock result object
    ]
    
    # In practice, we would add real results from test suites
    print("Test report generator created successfully")
    print("Use merge_test_reports() to combine individual test reports")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())