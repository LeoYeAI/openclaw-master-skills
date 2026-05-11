#!/usr/bin/env python3
"""
n8n Workflow Testing & Validation
Test workflows before activation with validation and dry-runs
"""

import sys
import json
import argparse
import time
from pathlib import Path
from typing import Dict, List, Any

# Import N8nClient - handle both direct and module imports
try:
    from n8n_api import N8nClient
except ImportError:
    from scripts.n8n_api import N8nClient


class WorkflowTester:
    """Workflow testing and validation"""
    
    def __init__(self, client: N8nClient = None):
        self.client = client  # Only initialize when needed
    
    def validate_workflow(self, workflow_id: str = None, workflow_file: str = None) -> Dict:
        """Validate workflow structure and configuration"""
        if workflow_id:
            if not self.client:
                self.client = N8nClient()
            workflow_data = self.client.get_workflow(workflow_id)
        elif workflow_file:
            with open(workflow_file, 'r') as f:
                workflow_data = json.load(f)
        else:
            raise ValueError("Either workflow_id or workflow_file required")
        
        # Perform validation - use standalone validation for files
        validation = self._perform_validation(workflow_data)
        
        # Additional validation checks
        self._check_credentials(workflow_data, validation)
        self._check_node_configurations(workflow_data, validation)
        self._check_execution_flow(workflow_data, validation)
        
        return validation
    
    def _perform_validation(self, workflow_data: Dict) -> Dict:
        """Perform standalone workflow validation"""
        issues = {
            'errors': [],
            'warnings': [],
            'valid': True
        }
        
        # Check required fields
        if 'nodes' not in workflow_data:
            issues['errors'].append("Missing 'nodes' field")
            issues['valid'] = False
            return issues
        
        nodes = workflow_data.get('nodes', [])
        connections = workflow_data.get('connections', {})
        
        # Validate nodes
        node_names = set()
        for node in nodes:
            if 'name' not in node:
                issues['errors'].append("Node missing 'name' field")
                issues['valid'] = False
            else:
                node_names.add(node['name'])
            
            if 'type' not in node:
                issues['errors'].append(f"Node '{node.get('name', 'unknown')}' missing 'type' field")
                issues['valid'] = False
        
        # Validate connections
        for source_node, targets in connections.items():
            if source_node not in node_names:
                issues['errors'].append(f"Connection references non-existent source node: {source_node}")
                issues['valid'] = False
            
            for output_type, output_connections in targets.items():
                for conn_list in output_connections:
                    for conn in conn_list:
                        target_node = conn.get('node')
                        if target_node and target_node not in node_names:
                            issues['errors'].append(f"Connection references non-existent target node: {target_node}")
                            issues['valid'] = False
        
        # Check for disconnected nodes
        connected_nodes = set(connections.keys())
        for targets in connections.values():
            for output_connections in targets.values():
                for conn_list in output_connections:
                    for conn in conn_list:
                        connected_nodes.add(conn.get('node'))
        
        disconnected = node_names - connected_nodes
        if disconnected and len(nodes) > 1:
            for node in disconnected:
                issues['warnings'].append(f"Node '{node}' appears to be disconnected")
        
        return issues
    
    def _check_credentials(self, workflow_data: Dict, validation: Dict):
        """Check for missing or invalid credentials"""
        nodes = workflow_data.get('nodes', [])
        
        # Nodes that typically require credentials
        credential_nodes = [
            'n8n-nodes-base.httpRequest',
            'n8n-nodes-base.googleSheets',
            'n8n-nodes-base.slack',
            'n8n-nodes-base.twitter',
            'n8n-nodes-base.stripe',
            'n8n-nodes-base.postgres',
            'n8n-nodes-base.mysql',
            'n8n-nodes-base.emailSend'
        ]
        
        for node in nodes:
            node_type = node.get('type', '')
            if node_type in credential_nodes:
                credentials = node.get('credentials', {})
                if not credentials:
                    validation['warnings'].append(
                        f"Node '{node['name']}' ({node_type}) likely requires credentials"
                    )
    
    def _check_node_configurations(self, workflow_data: Dict, validation: Dict):
        """Check for invalid node configurations"""
        nodes = workflow_data.get('nodes', [])
        
        for node in nodes:
            node_type = node.get('type', '')
            parameters = node.get('parameters', {})
            
            # Check HTTP Request nodes
            if node_type == 'n8n-nodes-base.httpRequest':
                if not parameters.get('url'):
                    validation['errors'].append(
                        f"Node '{node['name']}' missing required URL parameter"
                    )
                    validation['valid'] = False
            
            # Check webhook nodes
            elif node_type == 'n8n-nodes-base.webhook':
                if not parameters.get('path'):
                    validation['errors'].append(
                        f"Node '{node['name']}' missing required path parameter"
                    )
                    validation['valid'] = False
            
            # Check email nodes
            elif node_type == 'n8n-nodes-base.emailSend':
                if not parameters.get('subject') and not parameters.get('text'):
                    validation['warnings'].append(
                        f"Node '{node['name']}' missing subject or text"
                    )
    
    def _check_execution_flow(self, workflow_data: Dict, validation: Dict):
        """Check workflow execution flow for issues"""
        nodes = workflow_data.get('nodes', [])
        connections = workflow_data.get('connections', {})
        
        # Check for trigger nodes
        trigger_types = [
            'n8n-nodes-base.webhook',
            'n8n-nodes-base.scheduleTrigger',
            'n8n-nodes-base.manualTrigger',
            'n8n-nodes-base.start'
        ]
        
        has_trigger = any(node.get('type') in trigger_types for node in nodes)
        if not has_trigger and len(nodes) > 0:
            validation['warnings'].append(
                "Workflow has no trigger node. It can only be executed manually."
            )
        
        # Check for end nodes (nodes with no outgoing connections)
        node_names = {node['name'] for node in nodes}
        connected_as_source = set(connections.keys())
        end_nodes = node_names - connected_as_source
        
        if not end_nodes and len(nodes) > 1:
            validation['warnings'].append(
                "Workflow has no end nodes. This may indicate circular dependencies."
            )
    
    def dry_run(self, workflow_id: str, test_data: Dict = None, test_data_file: str = None) -> Dict:
        """Execute workflow with test data"""
        # Load test data if from file
        if test_data_file:
            with open(test_data_file, 'r') as f:
                test_data = json.load(f)
        
        print(f"Running workflow {workflow_id} with test data...")
        
        # Execute workflow
        execution_result = self.client.execute_workflow(workflow_id, data=test_data)
        execution_id = execution_result.get('data', {}).get('executionId')
        
        if not execution_id:
            return {
                'status': 'failed',
                'error': 'No execution ID returned',
                'result': execution_result
            }
        
        print(f"Execution started: {execution_id}")
        print("Waiting for execution to complete...")
        
        # Poll for execution completion
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            time.sleep(2)
            attempt += 1
            
            try:
                execution = self.client.get_execution(execution_id)
                finished = execution.get('finished', False)
                
                if finished:
                    # Execution completed
                    success = execution.get('data', {}).get('resultData', {}).get('error') is None
                    
                    result = {
                        'status': 'success' if success else 'failed',
                        'execution_id': execution_id,
                        'finished': True,
                        'started_at': execution.get('startedAt'),
                        'stopped_at': execution.get('stoppedAt'),
                        'mode': execution.get('mode'),
                        'data': execution.get('data', {})
                    }
                    
                    if not success:
                        error_data = execution.get('data', {}).get('resultData', {}).get('error', {})
                        result['error'] = {
                            'message': error_data.get('message'),
                            'description': error_data.get('description')
                        }
                    
                    return result
            except Exception as e:
                print(f"Error checking execution status: {e}")
                continue
        
        return {
            'status': 'timeout',
            'execution_id': execution_id,
            'message': 'Execution did not complete within expected time'
        }
    
    def test_suite(self, workflow_id: str, test_cases: List[Dict]) -> Dict:
        """Run multiple test cases against workflow"""
        results = {
            'workflow_id': workflow_id,
            'total_tests': len(test_cases),
            'passed': 0,
            'failed': 0,
            'test_results': []
        }
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nRunning test case {i}/{len(test_cases)}: {test_case.get('name', 'Unnamed')}")
            
            test_data = test_case.get('input', {})
            expected_output = test_case.get('expected', {})
            
            # Run test
            result = self.dry_run(workflow_id, test_data=test_data)
            
            # Check result
            passed = result.get('status') == 'success'
            
            test_result = {
                'test_name': test_case.get('name'),
                'passed': passed,
                'input': test_data,
                'output': result,
                'expected': expected_output
            }
            
            results['test_results'].append(test_result)
            
            if passed:
                results['passed'] += 1
                print(f"✓ Test passed")
            else:
                results['failed'] += 1
                print(f"✗ Test failed: {result.get('error', 'Unknown error')}")
        
        return results
    
    def generate_test_report(self, validation: Dict, dry_run: Dict = None) -> str:
        """Generate human-readable test report"""
        report = []
        report.append("=" * 60)
        report.append("n8n Workflow Test Report")
        report.append("=" * 60)
        
        # Validation results
        report.append("\n## Validation Results")
        report.append(f"Status: {'✓ VALID' if validation['valid'] else '✗ INVALID'}")
        
        if validation['errors']:
            report.append(f"\nErrors ({len(validation['errors'])}):")
            for error in validation['errors']:
                report.append(f"  ✗ {error}")
        
        if validation['warnings']:
            report.append(f"\nWarnings ({len(validation['warnings'])}):")
            for warning in validation['warnings']:
                report.append(f"  ⚠ {warning}")
        
        if not validation['errors'] and not validation['warnings']:
            report.append("\n✓ No issues found")
        
        # Dry run results
        if dry_run:
            report.append("\n## Dry Run Results")
            report.append(f"Status: {dry_run.get('status', 'unknown').upper()}")
            report.append(f"Execution ID: {dry_run.get('execution_id', 'N/A')}")
            
            if dry_run.get('started_at'):
                report.append(f"Started: {dry_run['started_at']}")
            if dry_run.get('stopped_at'):
                report.append(f"Stopped: {dry_run['stopped_at']}")
            
            if dry_run.get('error'):
                report.append(f"\nError: {dry_run['error'].get('message', 'Unknown error')}")
                if dry_run['error'].get('description'):
                    report.append(f"Description: {dry_run['error']['description']}")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description='n8n Workflow Testing & Validation')
    parser.add_argument('action', choices=['validate', 'dry-run', 'test-suite', 'report'])
    parser.add_argument('--id', help='Workflow ID')
    parser.add_argument('--file', help='Workflow JSON file')
    parser.add_argument('--data', help='Test data JSON string')
    parser.add_argument('--data-file', help='Test data JSON file')
    parser.add_argument('--test-suite', help='Test suite JSON file')
    parser.add_argument('--pretty', action='store_true', help='Pretty print output')
    parser.add_argument('--report', action='store_true', help='Generate human-readable report')
    
    args = parser.parse_args()
    
    try:
        tester = WorkflowTester()
        result = None
        
        if args.action == 'validate':
            result = tester.validate_workflow(workflow_id=args.id, workflow_file=args.file)
            
            if args.report:
                print(tester.generate_test_report(result))
            else:
                print(json.dumps(result, indent=2 if args.pretty else None))
        
        elif args.action == 'dry-run':
            if not args.id:
                raise ValueError("--id required for dry-run")
            
            test_data = None
            if args.data:
                test_data = json.loads(args.data)
            
            result = tester.dry_run(
                workflow_id=args.id,
                test_data=test_data,
                test_data_file=args.data_file
            )
            
            if args.report:
                validation = tester.validate_workflow(workflow_id=args.id)
                print(tester.generate_test_report(validation, result))
            else:
                print(json.dumps(result, indent=2 if args.pretty else None))
        
        elif args.action == 'test-suite':
            if not args.id:
                raise ValueError("--id required for test-suite")
            if not args.test_suite:
                raise ValueError("--test-suite required for test-suite")
            
            with open(args.test_suite, 'r') as f:
                test_cases = json.load(f)
            
            result = tester.test_suite(args.id, test_cases)
            print(json.dumps(result, indent=2 if args.pretty else None))
        
        elif args.action == 'report':
            if not args.id:
                raise ValueError("--id required for report")
            
            validation = tester.validate_workflow(workflow_id=args.id)
            print(tester.generate_test_report(validation))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
