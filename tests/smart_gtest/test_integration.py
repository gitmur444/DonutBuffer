#!/usr/bin/env python3
"""
Test Integration Module for Smart GTest Agent
Provides integration with actual test results and PostgreSQL database
"""

import psycopg2
import json
import subprocess
from typing import Dict, List, Optional, Any
from datetime import datetime

class TestResultsAnalyzer:
    """Analyzes test results from Smart GTest PostgreSQL database"""
    
    def __init__(self, db_config: Optional[Dict[str, str]] = None):
        """Initialize with database configuration"""
        self.db_config = db_config or {
            'host': 'localhost',
            'database': 'testdb',
            'user': 'postgres',
            'password': ''
        }
        
    def get_recent_test_results(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent test results from the database"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            query = """
            SELECT test_suite, test_name, status, execution_time_ms, 
                   failure_message, tags, start_time, end_time
            FROM actual_tests 
            ORDER BY start_time DESC 
            LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            
            # Convert to dictionary format
            test_results = []
            for row in results:
                test_results.append({
                    'test_suite': row[0],
                    'test_name': row[1],
                    'status': row[2],
                    'execution_time_ms': row[3],
                    'failure_message': row[4],
                    'tags': row[5],
                    'start_time': row[6],
                    'end_time': row[7]
                })
            
            cursor.close()
            conn.close()
            
            return test_results
            
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return []
        except Exception as e:
            print(f"Error retrieving test results: {e}")
            return []
    
    def get_performance_trends(self, test_suite: str, days: int = 7) -> Dict[str, Any]:
        """Get performance trends for a specific test suite"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            query = """
            SELECT test_name, execution_time_ms, start_time
            FROM actual_tests 
            WHERE test_suite = %s 
            AND start_time >= NOW() - INTERVAL '%s days'
            AND status = 'PASSED'
            ORDER BY start_time ASC
            """
            
            cursor.execute(query, (test_suite, days))
            results = cursor.fetchall()
            
            # Group by test name and calculate trends
            trends = {}
            for row in results:
                test_name = row[0]
                exec_time = row[1]
                timestamp = row[2]
                
                if test_name not in trends:
                    trends[test_name] = []
                trends[test_name].append({
                    'execution_time_ms': exec_time,
                    'timestamp': timestamp
                })
            
            cursor.close()
            conn.close()
            
            return trends
            
        except Exception as e:
            print(f"Error retrieving performance trends: {e}")
            return {}
    
    def run_test_command(self, test_name: str) -> Dict[str, Any]:
        """Run a specific test and capture results"""
        try:
            # Run the test command
            cmd = f"./ringbuffer_tests --gtest_filter=*{test_name}*"
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                cwd="../.."  # Go back to DonutBuffer root
            )
            
            return {
                'command': cmd,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
            
        except Exception as e:
            return {
                'command': f"./ringbuffer_tests --gtest_filter=*{test_name}*",
                'return_code': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }

class EnhancedTestAgent:
    """Enhanced version of Smart GTest Agent with test integration"""
    
    def __init__(self):
        """Initialize with test results analyzer"""
        self.analyzer = TestResultsAnalyzer()
    
    def analyze_test_performance(self, test_suite: str = "RingBuffer") -> str:
        """Analyze recent test performance"""
        results = self.analyzer.get_recent_test_results(20)
        
        if not results:
            return "❌ No test results found. Make sure the PostgreSQL database is running and contains test data."
        
        # Filter by test suite
        suite_results = [r for r in results if test_suite in r['test_suite']]
        
        if not suite_results:
            return f"❌ No results found for test suite: {test_suite}"
        
        # Analyze results
        total_tests = len(suite_results)
        passed_tests = len([r for r in suite_results if r['status'] == 'PASSED'])
        failed_tests = len([r for r in suite_results if r['status'] == 'FAILED'])
        
        avg_execution_time = sum(r['execution_time_ms'] for r in suite_results) / total_tests
        
        # Performance analysis
        performance_tests = [r for r in suite_results if 'performance' in r['tags'].lower()]
        mutex_tests = [r for r in suite_results if 'mutex' in r['tags'].lower()]
        lockfree_tests = [r for r in suite_results if 'lockfree' in r['tags'].lower()]
        
        analysis = f"""📊 **Test Performance Analysis for {test_suite}**

**Overall Results:**
- Total tests: {total_tests}
- Passed: {passed_tests} ✅
- Failed: {failed_tests} ❌
- Success rate: {(passed_tests/total_tests*100):.1f}%
- Average execution time: {avg_execution_time:.1f}ms

**Performance Breakdown:**
- Performance tests: {len(performance_tests)}
- Mutex-related: {len(mutex_tests)}
- Lockfree-related: {len(lockfree_tests)}
"""

        if failed_tests > 0:
            failed_details = [r for r in suite_results if r['status'] == 'FAILED']
            analysis += "\n**Failed Tests:**\n"
            for test in failed_details[:3]:  # Show first 3 failures
                analysis += f"- {test['test_name']}: {test['failure_message'][:100]}...\n"
        
        return analysis
    
    def get_performance_recommendations(self, test_results: List[Dict[str, Any]]) -> str:
        """Generate performance recommendations based on test results"""
        
        # Analyze execution times
        slow_tests = [r for r in test_results if r['execution_time_ms'] > 1000]
        fast_tests = [r for r in test_results if r['execution_time_ms'] < 100]
        
        recommendations = "🎯 **Performance Recommendations:**\n\n"
        
        if slow_tests:
            recommendations += f"**Optimization Opportunities ({len(slow_tests)} slow tests):**\n"
            for test in slow_tests[:3]:
                recommendations += f"- {test['test_name']}: {test['execution_time_ms']}ms - Consider optimization\n"
            recommendations += "\n"
        
        if fast_tests:
            recommendations += f"**Well-performing tests ({len(fast_tests)} fast tests):**\n"
            recommendations += "- These tests show good performance patterns to replicate\n\n"
        
        recommendations += """**General Recommendations:**
1. **Lockfree vs Mutex**: Compare execution times between implementations
2. **Memory patterns**: Monitor for memory allocation bottlenecks  
3. **Concurrency**: Test with varying thread counts
4. **Cache efficiency**: Ensure proper memory alignment
5. **Batch operations**: Consider batching for better throughput"""
        
        return recommendations

# Example usage function
def demo_integration():
    """Demonstrate the enhanced test integration"""
    print("🔧 Smart GTest Agent - Test Integration Demo")
    print("=" * 50)
    
    agent = EnhancedTestAgent()
    
    # Analyze recent performance
    analysis = agent.analyze_test_performance()
    print(analysis)
    
    # Get recent results for recommendations
    results = agent.analyzer.get_recent_test_results(10)
    if results:
        recommendations = agent.get_performance_recommendations(results)
        print(f"\n{recommendations}")
    
    print("\n" + "=" * 50)
    print("Integration demo complete!")

if __name__ == "__main__":
    demo_integration() 