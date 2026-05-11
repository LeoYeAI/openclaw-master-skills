#!/usr/bin/env python3
"""
n8n API client for Clawdbot
Manages workflows, executions, and credentials via n8n REST API
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List


class N8nClient:
    """n8n API client"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or os.getenv('N8N_BASE_URL')
        self.api_key = api_key or os.getenv('N8N_API_KEY')
        
        if not self.api_key:
            raise ValueError("N8N_API_KEY not found in environment")
        
        self.session = requests.Session()
        self.session.headers.update({
            'X-N8N-API-KEY': self.api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request"""
        url = f"{self.base_url}/api/v1/{endpoint.lstrip('/')}"
        response = self.session.request(method, url, **kwargs)
        
        try:
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            raise Exception(error_msg) from e
    
    # Workflows
    def list_workflows(self, active: bool = None) -> List[Dict]:
        """List all workflows"""
        params = {}
        if active is not None:
            params['active'] = str(active).lower()
        return self._request('GET', 'workflows', params=params)
    
    def get_workflow(self, workflow_id: str) -> Dict:
        """Get workflow details"""
        return self._request('GET', f'workflows/{workflow_id}')
    
    def create_workflow(self, workflow_data: Dict) -> Dict:
        """Create new workflow"""
        # Remove read-only fields that n8n API doesn't accept on create
        clean_data = workflow_data.copy()
        clean_data.pop('active', None)
        clean_data.pop('id', None)
        return self._request('POST', 'workflows', json=clean_data)
    
    def update_workflow(self, workflow_id: str, workflow_data: Dict) -> Dict:
        """Update existing workflow"""
        return self._request('PATCH', f'workflows/{workflow_id}', json=workflow_data)
    
    def delete_workflow(self, workflow_id: str) -> Dict:
        """Delete workflow"""
        return self._request('DELETE', f'workflows/{workflow_id}')
    
    def activate_workflow(self, workflow_id: str) -> Dict:
        """Activate workflow"""
        return self._request('PATCH', f'workflows/{workflow_id}', json={'active': True})
    
    def deactivate_workflow(self, workflow_id: str) -> Dict:
        """Deactivate workflow"""
        return self._request('PATCH', f'workflows/{workflow_id}', json={'active': False})
    
    # Executions
    def list_executions(self, workflow_id: str = None, limit: int = 20) -> List[Dict]:
        """List workflow executions"""
        params = {'limit': limit}
        if workflow_id:
            params['workflowId'] = workflow_id
        return self._request('GET', 'executions', params=params)
    
    def get_execution(self, execution_id: str) -> Dict:
        """Get execution details"""
        return self._request('GET', f'executions/{execution_id}')
    
    def delete_execution(self, execution_id: str) -> Dict:
        """Delete execution"""
        return self._request('DELETE', f'executions/{execution_id}')
    
    # Manual execution
    def execute_workflow(self, workflow_id: str, data: Dict = None) -> Dict:
        """Manually trigger workflow execution"""
        payload = {'workflowId': workflow_id}
        if data:
            payload['data'] = data
        return self._request('POST', f'workflows/{workflow_id}/execute', json=payload)
    
    # Testing & Validation
    def validate_workflow(self, workflow_data: Dict) -> Dict:
        """Validate workflow structure and configuration"""
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
            
            # Check for required credentials
            if node.get('type', '').startswith('n8n-nodes-base'):
                credentials = node.get('credentials', {})
                if not credentials and node['type'] not in ['n8n-nodes-base.start', 'n8n-nodes-base.set']:
                    issues['warnings'].append(f"Node '{node['name']}' may require credentials")
        
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
    
    def dry_run_workflow(self, workflow_id: str, test_data: Dict = None) -> Dict:
        """Test workflow execution with mock data (creates temp execution)"""
        # Execute workflow with test data and return results
        result = self.execute_workflow(workflow_id, data=test_data)
        return {
            'execution_id': result.get('data', {}).get('executionId'),
            'status': 'initiated',
            'test_data': test_data
        }
    
    # Optimization & Analytics
    def get_workflow_statistics(self, workflow_id: str, days: int = 7) -> Dict:
        """Get workflow execution statistics"""
        executions = self.list_executions(workflow_id=workflow_id, limit=100)
        
        stats = {
            'total_executions': len(executions),
            'successful': 0,
            'failed': 0,
            'execution_times': [],
            'error_patterns': {}
        }
        
        for execution in executions:
            status = execution.get('finished')
            if status:
                stats['successful'] += 1
            else:
                stats['failed'] += 1
                error = execution.get('data', {}).get('resultData', {}).get('error', {}).get('message', 'Unknown error')
                stats['error_patterns'][error] = stats['error_patterns'].get(error, 0) + 1
            
            # Execution time
            start = execution.get('startedAt')
            stop = execution.get('stoppedAt')
            if start and stop:
                # Calculate duration (simplified)
                stats['execution_times'].append({'start': start, 'stop': stop})
        
        # Calculate success rate
        if stats['total_executions'] > 0:
            stats['success_rate'] = (stats['successful'] / stats['total_executions']) * 100
        else:
            stats['success_rate'] = 0
        
        return stats
    
    def analyze_workflow_performance(self, workflow_id: str) -> Dict:
        """Analyze workflow performance and identify bottlenecks"""
        workflow = self.get_workflow(workflow_id)
        executions = self.list_executions(workflow_id=workflow_id, limit=10)
        
        analysis = {
            'node_count': len(workflow.get('nodes', [])),
            'connection_count': sum(len(conns) for conns in workflow.get('connections', {}).values()),
            'parallel_opportunities': [],
            'bottlenecks': [],
            'optimization_suggestions': []
        }
        
        # Analyze node structure for parallel opportunities
        nodes = workflow.get('nodes', [])
        connections = workflow.get('connections', {})
        
        # Find nodes that could be parallelized
        for node in nodes:
            node_name = node['name']
            if node_name in connections:
                outputs = connections[node_name]
                # If node has multiple outputs, suggest parallel execution
                total_connections = sum(len(conn_list) for output in outputs.values() for conn_list in output)
                if total_connections > 1:
                    analysis['parallel_opportunities'].append({
                        'node': node_name,
                        'connection_count': total_connections,
                        'suggestion': 'Consider using Split In Batches for parallel processing'
                    })
        
        # Analyze execution patterns
        if executions:
            analysis['optimization_suggestions'].append({
                'type': 'monitoring',
                'suggestion': 'Enable execution data retention for better debugging'
            })
        
        # Check for common anti-patterns
        for node in nodes:
            if node.get('type') == 'n8n-nodes-base.httpRequest':
                analysis['optimization_suggestions'].append({
                    'type': 'caching',
                    'node': node['name'],
                    'suggestion': 'Consider caching HTTP responses for frequently accessed data'
                })
        
        return analysis


def main():
    parser = argparse.ArgumentParser(description='n8n API Client')
    parser.add_argument('action', choices=[
        'list-workflows', 'get-workflow', 'create', 'activate', 'deactivate',
        'list-executions', 'get-execution', 'execute', 'validate', 'stats'
    ])
    parser.add_argument('--id', help='Workflow or execution ID')
    parser.add_argument('--active', type=lambda x: x.lower() == 'true', help='Filter by active status')
    parser.add_argument('--limit', type=int, default=20, help='Limit results')
    parser.add_argument('--data', help='JSON data for execution')
    parser.add_argument('--from-file', help='Create workflow from JSON file')
    parser.add_argument('--from-template', help='Create workflow from template name')
    parser.add_argument('--days', type=int, default=7, help='Days for statistics')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')
    
    args = parser.parse_args()
    
    try:
        client = N8nClient()
        result = None
        
        if args.action == 'list-workflows':
            result = client.list_workflows(active=args.active)
        elif args.action == 'get-workflow':
            if not args.id:
                raise ValueError("--id required for get-workflow")
            result = client.get_workflow(args.id)
        elif args.action == 'create':
            if args.from_file:
                with open(args.from_file, 'r') as f:
                    workflow_data = json.load(f)
                result = client.create_workflow(workflow_data)
            elif args.from_template:
                # Load template
                template_path = Path(__file__).parent.parent / 'templates' / f'{args.from_template}.json'
                if not template_path.exists():
                    raise ValueError(f"Template not found: {args.from_template}")
                with open(template_path, 'r') as f:
                    workflow_data = json.load(f)
                result = client.create_workflow(workflow_data)
            else:
                raise ValueError("--from-file or --from-template required for create")
        elif args.action == 'activate':
            if not args.id:
                raise ValueError("--id required for activate")
            result = client.activate_workflow(args.id)
        elif args.action == 'deactivate':
            if not args.id:
                raise ValueError("--id required for deactivate")
            result = client.deactivate_workflow(args.id)
        elif args.action == 'list-executions':
            result = client.list_executions(workflow_id=args.id, limit=args.limit)
        elif args.action == 'get-execution':
            if not args.id:
                raise ValueError("--id required for get-execution")
            result = client.get_execution(args.id)
        elif args.action == 'execute':
            if not args.id:
                raise ValueError("--id required for execute")
            data = json.loads(args.data) if args.data else None
            result = client.execute_workflow(args.id, data=data)
        elif args.action == 'validate':
            if args.from_file:
                with open(args.from_file, 'r') as f:
                    workflow_data = json.load(f)
            elif args.id:
                workflow_data = client.get_workflow(args.id)
            else:
                raise ValueError("--id or --from-file required for validate")
            result = client.validate_workflow(workflow_data)
        elif args.action == 'stats':
            if not args.id:
                raise ValueError("--id required for stats")
            result = client.get_workflow_statistics(args.id, days=args.days)
        
        # Output
        if args.pretty:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result))
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
