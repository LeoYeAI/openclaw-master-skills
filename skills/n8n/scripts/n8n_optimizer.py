#!/usr/bin/env python3
"""
n8n Workflow Optimizer
Analyze and optimize workflow performance
"""

import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict

# Import N8nClient - handle both direct and module imports
try:
    from n8n_api import N8nClient
except ImportError:
    from scripts.n8n_api import N8nClient


class WorkflowOptimizer:
    """Workflow performance analyzer and optimizer"""
    
    def __init__(self, client: N8nClient = None):
        self.client = client or N8nClient()
    
    def analyze_performance(self, workflow_id: str, days: int = 7) -> Dict:
        """Comprehensive performance analysis"""
        workflow = self.client.get_workflow(workflow_id)
        statistics = self.client.get_workflow_statistics(workflow_id, days=days)
        
        analysis = {
            'workflow_id': workflow_id,
            'workflow_name': workflow.get('name'),
            'analysis_period_days': days,
            'execution_metrics': self._analyze_execution_metrics(statistics),
            'node_analysis': self._analyze_nodes(workflow),
            'connection_analysis': self._analyze_connections(workflow),
            'performance_score': 0,
            'bottlenecks': [],
            'optimization_opportunities': []
        }
        
        # Identify bottlenecks
        analysis['bottlenecks'] = self._identify_bottlenecks(workflow, statistics)
        
        # Find optimization opportunities
        analysis['optimization_opportunities'] = self._find_optimizations(workflow, statistics)
        
        # Calculate performance score (0-100)
        analysis['performance_score'] = self._calculate_performance_score(analysis)
        
        return analysis
    
    def _analyze_execution_metrics(self, statistics: Dict) -> Dict:
        """Analyze execution metrics"""
        metrics = {
            'total_executions': statistics.get('total_executions', 0),
            'successful_executions': statistics.get('successful', 0),
            'failed_executions': statistics.get('failed', 0),
            'success_rate': statistics.get('success_rate', 0),
            'failure_rate': 0
        }
        
        if metrics['total_executions'] > 0:
            metrics['failure_rate'] = (metrics['failed_executions'] / metrics['total_executions']) * 100
        
        # Categorize health
        if metrics['success_rate'] >= 95:
            metrics['health'] = 'excellent'
        elif metrics['success_rate'] >= 80:
            metrics['health'] = 'good'
        elif metrics['success_rate'] >= 60:
            metrics['health'] = 'fair'
        else:
            metrics['health'] = 'poor'
        
        return metrics
    
    def _analyze_nodes(self, workflow: Dict) -> Dict:
        """Analyze workflow nodes"""
        nodes = workflow.get('nodes', [])
        
        analysis = {
            'total_nodes': len(nodes),
            'node_types': defaultdict(int),
            'complexity_score': 0,
            'expensive_nodes': []
        }
        
        # Count node types
        for node in nodes:
            node_type = node.get('type', '').split('.')[-1]
            analysis['node_types'][node_type] += 1
        
        # Identify potentially expensive operations
        expensive_types = [
            'httpRequest',
            'postgres',
            'mysql',
            'mongodb',
            'googleSheets',
            'airtable',
            'webhook'
        ]
        
        for node in nodes:
            node_type = node.get('type', '')
            for exp_type in expensive_types:
                if exp_type in node_type:
                    analysis['expensive_nodes'].append({
                        'name': node.get('name'),
                        'type': node_type,
                        'reason': self._get_expense_reason(exp_type)
                    })
        
        # Calculate complexity score
        analysis['complexity_score'] = self._calculate_complexity(workflow)
        
        return analysis
    
    def _get_expense_reason(self, node_type: str) -> str:
        """Get reason why node type is expensive"""
        reasons = {
            'httpRequest': 'External API calls can be slow and rate-limited',
            'postgres': 'Database queries can be slow with large datasets',
            'mysql': 'Database queries can be slow with large datasets',
            'mongodb': 'Database queries can be slow with large datasets',
            'googleSheets': 'Google Sheets API has rate limits and can be slow',
            'airtable': 'Airtable API has rate limits',
            'webhook': 'Waiting for webhook responses can cause delays'
        }
        return reasons.get(node_type, 'Potentially expensive operation')
    
    def _analyze_connections(self, workflow: Dict) -> Dict:
        """Analyze workflow connections"""
        connections = workflow.get('connections', {})
        
        analysis = {
            'total_connections': 0,
            'parallel_paths': 0,
            'sequential_paths': 0,
            'max_path_length': 0
        }
        
        # Count connections
        for source, targets in connections.items():
            for output_type, output_conns in targets.items():
                for conn_list in output_conns:
                    analysis['total_connections'] += len(conn_list)
                    
                    # Check for parallel paths
                    if len(conn_list) > 1:
                        analysis['parallel_paths'] += 1
        
        return analysis
    
    def _calculate_complexity(self, workflow: Dict) -> int:
        """Calculate workflow complexity score (0-100)"""
        nodes = workflow.get('nodes', [])
        connections = workflow.get('connections', {})
        
        # Base complexity from node count
        complexity = min(len(nodes) * 5, 50)
        
        # Add complexity for connections
        total_connections = sum(
            len(conn)
            for targets in connections.values()
            for output_conns in targets.values()
            for conn in output_conns
        )
        complexity += min(total_connections * 3, 30)
        
        # Add complexity for conditional logic
        for node in nodes:
            if node.get('type') == 'n8n-nodes-base.if':
                complexity += 5
            elif node.get('type') == 'n8n-nodes-base.switch':
                complexity += 10
        
        return min(complexity, 100)
    
    def _identify_bottlenecks(self, workflow: Dict, statistics: Dict) -> List[Dict]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        nodes = workflow.get('nodes', [])
        
        # Check for sequential expensive operations
        expensive_types = ['httpRequest', 'postgres', 'mysql', 'mongodb']
        expensive_nodes = [
            node for node in nodes
            if any(exp in node.get('type', '') for exp in expensive_types)
        ]
        
        if len(expensive_nodes) > 3:
            bottlenecks.append({
                'type': 'sequential_expensive_operations',
                'severity': 'high',
                'description': f'Workflow has {len(expensive_nodes)} potentially expensive operations running sequentially',
                'affected_nodes': [node['name'] for node in expensive_nodes],
                'impact': 'High execution time'
            })
        
        # Check for high failure rate
        if statistics.get('failed', 0) > statistics.get('successful', 0):
            bottlenecks.append({
                'type': 'high_failure_rate',
                'severity': 'critical',
                'description': 'Workflow has more failures than successes',
                'impact': 'Unreliable execution'
            })
        
        # Check for missing error handling
        has_error_handling = any(
            node.get('type') in ['n8n-nodes-base.errorTrigger', 'n8n-nodes-base.if']
            for node in nodes
        )
        
        if not has_error_handling and len(nodes) > 3:
            bottlenecks.append({
                'type': 'missing_error_handling',
                'severity': 'medium',
                'description': 'Workflow lacks error handling nodes',
                'impact': 'Failures may not be handled gracefully'
            })
        
        return bottlenecks
    
    def _find_optimizations(self, workflow: Dict, statistics: Dict) -> List[Dict]:
        """Find optimization opportunities"""
        optimizations = []
        nodes = workflow.get('nodes', [])
        connections = workflow.get('connections', {})
        
        # Opportunity 1: Parallel execution
        for source_node, targets in connections.items():
            for output_conns in targets.values():
                for conn_list in output_conns:
                    if len(conn_list) > 1:
                        optimizations.append({
                            'type': 'parallel_execution',
                            'priority': 'high',
                            'description': f'Node "{source_node}" branches to multiple nodes - already optimized for parallel execution',
                            'node': source_node,
                            'benefit': 'Reduced execution time through parallelization'
                        })
        
        # Opportunity 2: Caching
        http_nodes = [node for node in nodes if 'httpRequest' in node.get('type', '')]
        if http_nodes:
            optimizations.append({
                'type': 'caching',
                'priority': 'medium',
                'description': f'Found {len(http_nodes)} HTTP request nodes - consider caching responses',
                'affected_nodes': [node['name'] for node in http_nodes],
                'benefit': 'Reduced API calls and faster execution',
                'implementation': 'Use Function or Code nodes to implement simple caching'
            })
        
        # Opportunity 3: Batch processing
        loop_nodes = [node for node in nodes if 'loop' in node.get('type', '').lower()]
        if not loop_nodes:
            optimizations.append({
                'type': 'batch_processing',
                'priority': 'low',
                'description': 'Consider using "Split In Batches" node for processing large datasets',
                'benefit': 'Better memory management and parallel processing',
                'implementation': 'Add "Split In Batches" node before expensive operations'
            })
        
        # Opportunity 4: Error handling
        error_nodes = [node for node in nodes if 'error' in node.get('type', '').lower()]
        if not error_nodes and len(nodes) > 3:
            optimizations.append({
                'type': 'error_handling',
                'priority': 'high',
                'description': 'Add error handling to improve reliability',
                'benefit': 'Graceful error recovery and better debugging',
                'implementation': 'Add "Error Trigger" or "IF" nodes to handle failures'
            })
        
        # Opportunity 5: Reduce complexity
        complexity = self._calculate_complexity(workflow)
        if complexity > 70:
            optimizations.append({
                'type': 'reduce_complexity',
                'priority': 'medium',
                'description': f'Workflow complexity score is {complexity}/100 - consider splitting into sub-workflows',
                'benefit': 'Easier maintenance and debugging',
                'implementation': 'Break workflow into smaller, reusable workflows'
            })
        
        # Opportunity 6: Execution settings
        workflow_settings = workflow.get('settings', {})
        if not workflow_settings.get('executionTimeout'):
            optimizations.append({
                'type': 'execution_timeout',
                'priority': 'low',
                'description': 'Set execution timeout to prevent hanging workflows',
                'benefit': 'Prevent resource waste from stuck executions',
                'implementation': 'Add timeout in workflow settings'
            })
        
        return optimizations
    
    def _calculate_performance_score(self, analysis: Dict) -> int:
        """Calculate overall performance score (0-100)"""
        score = 100
        
        # Deduct for execution failures
        metrics = analysis.get('execution_metrics', {})
        success_rate = metrics.get('success_rate', 100)
        score -= (100 - success_rate) * 0.5
        
        # Deduct for complexity
        complexity = analysis.get('node_analysis', {}).get('complexity_score', 0)
        if complexity > 70:
            score -= (complexity - 70) * 0.3
        
        # Deduct for bottlenecks
        bottlenecks = analysis.get('bottlenecks', [])
        for bottleneck in bottlenecks:
            severity = bottleneck.get('severity', 'low')
            if severity == 'critical':
                score -= 20
            elif severity == 'high':
                score -= 10
            elif severity == 'medium':
                score -= 5
        
        # Deduct for high-priority optimizations not implemented
        optimizations = analysis.get('optimization_opportunities', [])
        high_priority = [opt for opt in optimizations if opt.get('priority') == 'high']
        score -= len(high_priority) * 5
        
        return max(0, min(100, int(score)))
    
    def suggest_optimizations(self, workflow_id: str) -> Dict:
        """Generate optimization suggestions"""
        analysis = self.analyze_performance(workflow_id)
        
        suggestions = {
            'workflow_id': workflow_id,
            'performance_score': analysis['performance_score'],
            'health': analysis['execution_metrics']['health'],
            'priority_actions': [],
            'quick_wins': [],
            'long_term_improvements': []
        }
        
        # Categorize optimizations by effort and impact
        for opt in analysis['optimization_opportunities']:
            priority = opt.get('priority', 'low')
            
            if priority == 'high':
                suggestions['priority_actions'].append(opt)
            elif priority == 'medium':
                suggestions['quick_wins'].append(opt)
            else:
                suggestions['long_term_improvements'].append(opt)
        
        # Add bottleneck fixes as priority actions
        for bottleneck in analysis['bottlenecks']:
            if bottleneck.get('severity') in ['critical', 'high']:
                suggestions['priority_actions'].append({
                    'type': 'fix_bottleneck',
                    'priority': 'critical',
                    'description': f"Fix bottleneck: {bottleneck['description']}",
                    'benefit': f"Resolve: {bottleneck['impact']}"
                })
        
        return suggestions
    
    def generate_optimization_report(self, analysis: Dict) -> str:
        """Generate human-readable optimization report"""
        report = []
        report.append("=" * 70)
        report.append("n8n Workflow Optimization Report")
        report.append("=" * 70)
        
        report.append(f"\nWorkflow: {analysis['workflow_name']}")
        report.append(f"Analysis Period: {analysis['analysis_period_days']} days")
        report.append(f"Performance Score: {analysis['performance_score']}/100")
        
        # Execution Metrics
        metrics = analysis['execution_metrics']
        report.append(f"\n## Execution Metrics")
        report.append(f"Health Status: {metrics['health'].upper()}")
        report.append(f"Total Executions: {metrics['total_executions']}")
        report.append(f"Success Rate: {metrics['success_rate']:.1f}%")
        report.append(f"Failure Rate: {metrics['failure_rate']:.1f}%")
        
        # Node Analysis
        node_analysis = analysis['node_analysis']
        report.append(f"\n## Workflow Structure")
        report.append(f"Total Nodes: {node_analysis['total_nodes']}")
        report.append(f"Complexity Score: {node_analysis['complexity_score']}/100")
        
        if node_analysis['expensive_nodes']:
            report.append(f"\nExpensive Operations ({len(node_analysis['expensive_nodes'])}):")
            for node in node_analysis['expensive_nodes'][:5]:
                report.append(f"  • {node['name']}: {node['reason']}")
        
        # Bottlenecks
        if analysis['bottlenecks']:
            report.append(f"\n## Bottlenecks ({len(analysis['bottlenecks'])})")
            for bottleneck in analysis['bottlenecks']:
                severity = bottleneck['severity'].upper()
                report.append(f"\n[{severity}] {bottleneck['type']}")
                report.append(f"  Description: {bottleneck['description']}")
                report.append(f"  Impact: {bottleneck['impact']}")
        
        # Optimization Opportunities
        optimizations = analysis['optimization_opportunities']
        if optimizations:
            report.append(f"\n## Optimization Opportunities ({len(optimizations)})")
            
            # Group by priority
            high_priority = [opt for opt in optimizations if opt.get('priority') == 'high']
            medium_priority = [opt for opt in optimizations if opt.get('priority') == 'medium']
            low_priority = [opt for opt in optimizations if opt.get('priority') == 'low']
            
            if high_priority:
                report.append(f"\n### High Priority ({len(high_priority)})")
                for opt in high_priority:
                    report.append(f"\n• {opt['type'].replace('_', ' ').title()}")
                    report.append(f"  {opt['description']}")
                    report.append(f"  Benefit: {opt['benefit']}")
                    if 'implementation' in opt:
                        report.append(f"  How: {opt['implementation']}")
            
            if medium_priority:
                report.append(f"\n### Medium Priority ({len(medium_priority)})")
                for opt in medium_priority:
                    report.append(f"\n• {opt['type'].replace('_', ' ').title()}")
                    report.append(f"  {opt['description']}")
            
            if low_priority:
                report.append(f"\n### Low Priority ({len(low_priority)})")
                for opt in low_priority:
                    report.append(f"  • {opt['description']}")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description='n8n Workflow Optimizer')
    parser.add_argument('action', choices=['analyze', 'suggest', 'report'])
    parser.add_argument('--id', required=True, help='Workflow ID')
    parser.add_argument('--days', type=int, default=7, help='Analysis period in days')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')
    
    args = parser.parse_args()
    
    try:
        optimizer = WorkflowOptimizer()
        
        if args.action == 'analyze':
            result = optimizer.analyze_performance(args.id, days=args.days)
            print(json.dumps(result, indent=2 if args.pretty else None))
        
        elif args.action == 'suggest':
            result = optimizer.suggest_optimizations(args.id)
            print(json.dumps(result, indent=2 if args.pretty else None))
        
        elif args.action == 'report':
            analysis = optimizer.analyze_performance(args.id, days=args.days)
            print(optimizer.generate_optimization_report(analysis))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
