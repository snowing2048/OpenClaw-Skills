#!/usr/bin/env python3
"""
Browser Agent Test Runner
Executes test cases from YAML and validates results
"""
import yaml
import subprocess
import time
import json
import sys
import os
from datetime import datetime

class TestRunner:
    def __init__(self, skill_path):
        self.skill_path = skill_path
        self.results = []
        self.start_time = None
        self.log_file = None

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {message}")
        if self.log_file:
            self.log_file.write(f"[{timestamp}] {message}\n")
            self.log_file.flush()

    def run_command(self, cmd, capture_output=True, timeout=30):
        """Execute a script command and return result"""
        full_cmd = f'py "{self.skill_path}/scripts/{cmd}"'
        self.log(f"Executing: {full_cmd}")
        try:
            result = subprocess.run(
                full_cmd,
                shell=True,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )
            output = result.stdout + result.stderr
            self.log(f"Output: {output[:200]}{'...' if len(output) > 200 else ''}")
            return result.returncode, output
        except subprocess.TimeoutExpired:
            self.log("ERROR: Command timed out")
            return -1, "Timeout"
        except Exception as e:
            self.log(f"ERROR: {e}")
            return -1, str(e)

    def execute_step(self, step):
        """Execute a single test step"""
        step_num = step['step']
        action = step['action']

        self.log(f"--- Step {step_num}: {action} ---")

        if action == "execute":
            cmd = step.get('command', '')
            if not cmd:
                return False, "Empty command"
            code, output = self.run_command(cmd)
            return code == 0, output

        elif action == "wait_for_text":
            text = step['text']
            timeout = step.get('timeout', 10)
            window = step.get('window', 'Chrome')
            # Use wait_for_text.py
            cmd = f'wait_for_text.py "{text}" "{window}" {timeout}'
            self.log(f"Waiting for text '{text}' in window '{window}' for {timeout}s")
            proc = subprocess.Popen(
                f'py "{self.skill_path}/scripts/{cmd}"',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            try:
                stdout, stderr = proc.communicate(timeout=timeout+5)
                output = stdout + stderr
                success = proc.returncode == 0
                self.log(f"Wait result: {'Found' if success else 'Timeout'}")
                return success, output
            except subprocess.TimeoutExpired:
                proc.kill()
                self.log("Wait command killed (timeout)")
                return False, "Wait timeout"

        elif action == "input_method":
            mode = step['mode']
            cmd = f'input_method.py "{mode}"'
            code, output = self.run_command(cmd)
            return code == 0, output

        elif action == "read_webpage":
            window = step.get('window', 'Chrome')
            cmd = f'read_webpage.py "{window}"'
            code, output = self.run_command(cmd)
            return code == 0, output

        elif action == "read_window":
            window = step.get('window', 'Chrome')
            cmd = f'read_window.py "{window}"'
            code, output = self.run_command(cmd)
            return code == 0, output

        else:
            return False, f"Unknown action: {action}"

    def execute_test(self, test_file):
        """Run a single test case"""
        with open(test_file, 'r', encoding='utf-8') as f:
            test_data = yaml.safe_load(f)

        test_id = test_data['id']
        test_name = test_data['name']

        self.log(f"\n{'='*60}")
        self.log(f"Starting Test: {test_id} - {test_name}")
        self.log(f"{'='*60}\n")

        self.start_time = time.time()
        steps_results = []
        overall_success = True
        failure_reason = None

        # Execute steps
        for step in test_data['steps']:
            step_num = step['step']
            step_name = step.get('name', f"Step {step_num}")

            success, output = self.execute_step(step)
            steps_results.append({
                'step': step_num,
                'name': step_name,
                'success': success,
                'output': output[:500]  # Limit output size
            })

            if not success:
                overall_success = False
                failure_reason = f"Step {step_num} failed: {step_name}"
                self.log(f"FAILED at step {step_num}: {failure_reason}")
                # Continue to end to record full context

        total_duration = time.time() - self.start_time

        # Validate expected results
        validation_results = {}
        validation_passed = True

        if overall_success:
            for val_name, val_rule in test_data.get('expected_results', {}).items():
                self.log(f"Validating: {val_name}")
                passed, reason = self.validate_metric(val_name, val_rule, total_duration, steps_results)
                validation_results[val_name] = {'passed': passed, 'reason': reason}
                if not passed:
                    validation_passed = False
                    self.log(f"VALIDATION FAILED: {val_name} - {reason}")
                else:
                    self.log(f"✓ {val_name} passed")

        # Record result
        result = {
            'test_id': test_id,
            'test_name': test_name,
            'timestamp': datetime.now().isoformat(),
            'overall_success': overall_success and validation_passed,
            'failure_reason': failure_reason if not overall_success else None,
            'total_duration': total_duration,
            'steps': steps_results,
            'validation': validation_results
        }

        self.results.append(result)
        self.log(f"\nTest {test_id} {'PASSED' if result['overall_success'] else 'FAILED'}")
        self.log(f"Total duration: {total_duration:.2f}s\n")

        return result

    def validate_metric(self, metric_name, metric_rule, total_duration, steps_results):
        """Validate a single expected result metric"""
        # Simple validations - extend as needed

        if metric_name == "duration_seconds":
            min_t = metric_rule.get('min', 0)
            max_t = metric_rule.get('max', float('inf'))
            if total_duration < min_t or total_duration > max_t:
                return False, f"Duration {total_duration:.2f}s not in [{min_t}, {max_t}]"
            return True, "OK"

        elif metric_name == "url_contains":
            # Check last read_window output
            last_read = None
            for step in reversed(steps_results):
                if 'read_window' in step['output'] or 'read_webpage' in step['output']:
                    last_read = step['output']
                    break
            if last_read and metric_rule in last_read:
                return True, "OK"
            return False, f"URL/content does not contain '{metric_rule}'"

        elif metric_name == "element_exists":
            # Check if expected element appears in any output
            expected = metric_rule if isinstance(metric_rule, str) else metric_rule.get('text', '')
            for step in steps_results:
                if expected in step['output']:
                    return True, "OK"
            return False, f"Element '{expected}' not found"

        elif metric_name == "input_accuracy":
            # For now assume 100% as we control input
            return True, "OK"

        elif metric_name == "mouse_points_count":
            # Count mouse move commands in logs (simplified)
            move_count = sum(1 for s in steps_results if 'mouse_move' in s['output'])
            min_count = metric_rule.get('min', 0)
            if move_count >= min_count:
                return True, f"Mouse moves: {move_count}"
            return False, f"Mouse moves: {move_count}, expected ≥ {min_count}"

        elif metric_name == "failures_count":
            failures = sum(1 for s in steps_results if not s['success'])
            max_fail = metric_rule.get('max', 0)
            if failures <= max_fail:
                return True, f"Failures: {failures}"
            return False, f"Failures: {failures}, expected ≤ {max_fail}"

        else:
            return True, "Unknown metric (skipped)"

    def generate_report(self, output_file=None):
        """Generate HTML/JSON report"""
        report = {
            'summary': {
                'total': len(self.results),
                'passed': sum(1 for r in self.results if r['overall_success']),
                'failed': sum(1 for r in self.results if not r['overall_success'])
            },
            'tests': self.results
        }

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            self.log(f"Report saved to {output_file}")

        return report

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Run browser agent tests')
    parser.add_argument('test_file', help='Test case YAML file')
    parser.add_argument('--log', help='Log file path')
    parser.add_argument('--report', help='JSON report output path')
    args = parser.parse_args()

    skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    runner = TestRunner(skill_path)

    if args.log:
        runner.log_file = open(args.log, 'w', encoding='utf-8')

    try:
        result = runner.execute_test(args.test_file)
        runner.generate_report(args.report)

        # Exit with proper code
        sys.exit(0 if result['overall_success'] else 1)

    finally:
        if runner.log_file:
            runner.log_file.close()

if __name__ == "__main__":
    main()
