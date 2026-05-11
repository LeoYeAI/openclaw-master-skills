---
name: n8n
description: Manage n8n workflows and automations via API. Use when working with n8n workflows, executions, or automation tasks - listing workflows, activating/deactivating, checking execution status, manually triggering workflows, or debugging automation issues.
metadata: {"openclaw":{"emoji":"\u2699\ufe0f","requires":{"env":["N8N_API_KEY","N8N_BASE_URL"]},"primaryEnv":"N8N_API_KEY"}}
---

# n8n Workflow Management

Comprehensive workflow automation management for n8n platform with creation, testing, execution monitoring, and performance optimization capabilities.

## ⚠️ CRITICAL: Workflow Creation Rules

**When creating n8n workflows, ALWAYS:**

1. ✅ **Generate COMPLETE workflows** with all functional nodes
2. ✅ **Include actual HTTP Request nodes** for API calls (ImageFX, Gemini, Veo, Suno, etc.)
3. ✅ **Add Code nodes** for data transformation and logic
4. ✅ **Create proper connections** between all nodes
5. ✅ **Use real node types** (n8n-nodes-base.httpRequest, n8n-nodes-base.code, n8n-nodes-base.set)

**NEVER:**
- ❌ Create "Setup Instructions" placeholder nodes
- ❌ Generate workflows with only TODO comments
- ❌ Make incomplete workflows requiring manual node addition
- ❌ Use text-only nodes as substitutes for real functionality

**Example GOOD workflow:**
```
Manual Trigger → Set Config → HTTP Request (API call) → Code (parse) → Response
```

**Example BAD workflow:**
```
Manual Trigger → Code ("Add HTTP nodes here, configure APIs...")
```

Always build the complete, functional workflow with all necessary nodes configured and connected.

## Setup

**Required environment variables:**
- `N8N_API_KEY` — Your n8n API key (Settings → API in the n8n UI)
- `N8N_BASE_URL` — Your n8n instance URL

**Configure credentials via OpenClaw settings:**

Add to `~/.config/openclaw/settings.json`:
```json
{
  "skills": {
    "n8n": {
      "env": {
        "N8N_API_KEY": "your-api-key-here",
        "N8N_BASE_URL": "your-n8n-url-here"
      }
    }
  }
}
```

Or set per-session (do **not** persist secrets in shell rc files):
```bash
export N8N_API_KEY="your-api-key-here"
export N8N_BASE_URL="your-n8n-url-here"
```

**Verify connection:**
```bash
python3 scripts/n8n_api.py list-workflows --pretty
```

> **Security note:** Never store API keys in plaintext shell config files (`~/.bashrc`, `~/.zshrc`). Use the OpenClaw settings file or a secure secret manager.

## Quick Reference

### Workflow Management

#### List Workflows
```bash
python3 scripts/n8n_api.py list-workflows --pretty
python3 scripts/n8n_api.py list-workflows --active true --pretty
```

#### Get Workflow Details
```bash
python3 scripts/n8n_api.py get-workflow --id <workflow-id> --pretty
```

#### Create Workflows
```bash
# From JSON file
python3 scripts/n8n_api.py create --from-file workflow.json
```

#### Activate/Deactivate
```bash
python3 scripts/n8n_api.py activate --id <workflow-id>
python3 scripts/n8n_api.py deactivate --id <workflow-id>
```

### Testing & Validation

#### Validate Workflow Structure
```bash
# Validate existing workflow
python3 scripts/n8n_tester.py validate --id <workflow-id>

# Validate from file
python3 scripts/n8n_tester.py validate --file workflow.json --pretty

# Generate validation report
python3 scripts/n8n_tester.py report --id <workflow-id>
```

#### Dry Run Testing
```bash
# Test with data
python3 scripts/n8n_tester.py dry-run --id <workflow-id> --data '{"email": "test@example.com"}'

# Test with data file
python3 scripts/n8n_tester.py dry-run --id <workflow-id> --data-file test-data.json

# Full test report (validation + dry run)
python3 scripts/n8n_tester.py dry-run --id <workflow-id> --data-file test.json --report
```

#### Test Suite
```bash
# Run multiple test cases
python3 scripts/n8n_tester.py test-suite --id <workflow-id> --test-suite test-cases.json
```

### Execution Monitoring

#### List Executions
```bash
# Recent executions (all workflows)
python3 scripts/n8n_api.py list-executions --limit 10 --pretty

# Specific workflow executions
python3 scripts/n8n_api.py list-executions --id <workflow-id> --limit 20 --pretty
```

#### Get Execution Details
```bash
python3 scripts/n8n_api.py get-execution --id <execution-id> --pretty
```

#### Manual Execution
```bash
# Trigger workflow
python3 scripts/n8n_api.py execute --id <workflow-id>

# Execute with data
python3 scripts/n8n_api.py execute --id <workflow-id> --data '{"key": "value"}'
```

### Performance Optimization

#### Analyze Performance
```bash
# Full performance analysis
python3 scripts/n8n_optimizer.py analyze --id <workflow-id> --pretty

# Analyze specific period
python3 scripts/n8n_optimizer.py analyze --id <workflow-id> --days 30 --pretty
```

#### Get Optimization Suggestions
```bash
# Priority-ranked suggestions
python3 scripts/n8n_optimizer.py suggest --id <workflow-id> --pretty
```

#### Generate Optimization Report
```bash
# Human-readable report with metrics, bottlenecks, and suggestions
python3 scripts/n8n_optimizer.py report --id <workflow-id>
```

#### Get Workflow Statistics
```bash
# Execution statistics
python3 scripts/n8n_api.py stats --id <workflow-id> --days 7 --pretty
```

## Python API

### Basic Usage

```python
from scripts.n8n_api import N8nClient

client = N8nClient()

# List workflows
workflows = client.list_workflows(active=True)

# Get workflow
workflow = client.get_workflow('workflow-id')

# Create workflow
new_workflow = client.create_workflow({
    'name': 'My Workflow',
    'nodes': [...],
    'connections': {...}
})

# Activate/deactivate
client.activate_workflow('workflow-id')
client.deactivate_workflow('workflow-id')

# Executions
executions = client.list_executions(workflow_id='workflow-id', limit=10)
execution = client.get_execution('execution-id')

# Execute workflow
result = client.execute_workflow('workflow-id', data={'key': 'value'})
```

### Validation & Testing

```python
from scripts.n8n_api import N8nClient
from scripts.n8n_tester import WorkflowTester

client = N8nClient()
tester = WorkflowTester(client)

# Validate workflow
validation = tester.validate_workflow(workflow_id='123')
print(f"Valid: {validation['valid']}")
print(f"Errors: {validation['errors']}")
print(f"Warnings: {validation['warnings']}")

# Dry run
result = tester.dry_run(
    workflow_id='123',
    test_data={'email': 'test@example.com'}
)
print(f"Status: {result['status']}")

# Test suite
test_cases = [
    {'name': 'Test 1', 'input': {...}, 'expected': {...}},
    {'name': 'Test 2', 'input': {...}, 'expected': {...}}
]
results = tester.test_suite('123', test_cases)
print(f"Passed: {results['passed']}/{results['total_tests']}")

# Generate report
report = tester.generate_test_report(validation, result)
print(report)
```

### Performance Optimization

```python
from scripts.n8n_optimizer import WorkflowOptimizer

optimizer = WorkflowOptimizer()

# Analyze performance
analysis = optimizer.analyze_performance('workflow-id', days=7)
print(f"Performance Score: {analysis['performance_score']}/100")
print(f"Health: {analysis['execution_metrics']['health']}")

# Get suggestions
suggestions = optimizer.suggest_optimizations('workflow-id')
print(f"Priority Actions: {len(suggestions['priority_actions'])}")
print(f"Quick Wins: {len(suggestions['quick_wins'])}")

# Generate report
report = optimizer.generate_optimization_report(analysis)
print(report)
```

## Common Workflows

### 1. Validate and Test Workflow

```bash
# Validate workflow structure
python3 scripts/n8n_tester.py validate --id <workflow-id> --pretty

# Test with sample data
python3 scripts/n8n_tester.py dry-run --id <workflow-id> \
  --data '{"email": "test@example.com", "name": "Test User"}'

# If tests pass, activate
python3 scripts/n8n_api.py activate --id <workflow-id>
```

### 2. Debug Failed Workflow

```bash
# Check recent executions
python3 scripts/n8n_api.py list-executions --id <workflow-id> --limit 10 --pretty

# Get specific execution details
python3 scripts/n8n_api.py get-execution --id <execution-id> --pretty

# Validate workflow structure
python3 scripts/n8n_tester.py validate --id <workflow-id>

# Generate test report
python3 scripts/n8n_tester.py report --id <workflow-id>

# Check for optimization issues
python3 scripts/n8n_optimizer.py report --id <workflow-id>
```

### 3. Optimize Workflow Performance

```bash
# Analyze current performance
python3 scripts/n8n_optimizer.py analyze --id <workflow-id> --days 30 --pretty

# Get actionable suggestions
python3 scripts/n8n_optimizer.py suggest --id <workflow-id> --pretty

# Generate comprehensive report
python3 scripts/n8n_optimizer.py report --id <workflow-id>

# Review execution statistics
python3 scripts/n8n_api.py stats --id <workflow-id> --days 30 --pretty

# Test optimizations with dry run
python3 scripts/n8n_tester.py dry-run --id <workflow-id> --data-file test-data.json
```

### 4. Monitor Workflow Health

```bash
# Check active workflows
python3 scripts/n8n_api.py list-workflows --active true --pretty

# Review recent execution status
python3 scripts/n8n_api.py list-executions --limit 20 --pretty

# Get statistics for each critical workflow
python3 scripts/n8n_api.py stats --id <workflow-id> --pretty

# Generate health reports
python3 scripts/n8n_optimizer.py report --id <workflow-id>
```

## Validation Checks

The testing module performs comprehensive validation:

### Structure Validation
- ✓ Required fields present (nodes, connections)
- ✓ All nodes have names and types
- ✓ Connection targets exist
- ✓ No disconnected nodes (warning)

### Configuration Validation
- ✓ Nodes requiring credentials are configured
- ✓ Required parameters are set
- ✓ HTTP nodes have URLs
- ✓ Webhook nodes have paths
- ✓ Email nodes have content

### Flow Validation
- ✓ Workflow has trigger nodes
- ✓ Proper execution flow
- ✓ No circular dependencies
- ✓ End nodes identified

## Optimization Analysis

The optimizer analyzes multiple dimensions:

### Execution Metrics
- Total executions
- Success/failure rates
- Health status (excellent/good/fair/poor)
- Error patterns

### Performance Metrics
- Node count and complexity
- Connection patterns
- Expensive operations (API calls, database queries)
- Parallel execution opportunities

### Bottleneck Detection
- Sequential expensive operations
- High failure rates
- Missing error handling
- Rate limit issues

### Optimization Opportunities
- **Parallel Execution:** Identify nodes that can run concurrently
- **Caching:** Suggest caching for repeated API calls
- **Batch Processing:** Recommend batching for large datasets
- **Error Handling:** Add error recovery mechanisms
- **Complexity Reduction:** Split complex workflows
- **Timeout Settings:** Configure execution limits

## Performance Scoring

Workflows receive a performance score (0-100) based on:

- **Success Rate:** Higher is better (50% weight)
- **Complexity:** Lower is better (30% weight)
- **Bottlenecks:** Fewer is better (critical: -20, high: -10, medium: -5)
- **Optimizations:** Implemented best practices (+5 each)

Score interpretation:
- **90-100:** Excellent - Well-optimized
- **70-89:** Good - Minor improvements possible
- **50-69:** Fair - Optimization recommended
- **0-49:** Poor - Significant issues

## Best Practices

### Development
1. **Plan Structure:** Design workflow nodes and connections before building
2. **Validate First:** Always validate before deployment
3. **Test Thoroughly:** Use dry-run with multiple test cases
4. **Error Handling:** Add error nodes for reliability
5. **Documentation:** Comment complex logic in Code nodes

### Testing
1. **Sample Data:** Create realistic test data files
2. **Edge Cases:** Test boundary conditions and errors
3. **Incremental:** Test each node addition
4. **Regression:** Retest after changes
5. **Production-like:** Use staging environment that mirrors production

### Deployment
1. **Inactive First:** Deploy workflows in inactive state
2. **Gradual Rollout:** Test with limited traffic initially
3. **Monitor Closely:** Watch first executions carefully
4. **Quick Rollback:** Be ready to deactivate if issues arise
5. **Document Changes:** Keep changelog of modifications

### Optimization
1. **Baseline Metrics:** Capture performance before changes
2. **One Change at a Time:** Isolate optimization impacts
3. **Measure Results:** Compare before/after metrics
4. **Regular Reviews:** Schedule monthly optimization reviews
5. **Cost Awareness:** Monitor API usage and execution costs

### Maintenance
1. **Health Checks:** Weekly execution statistics review
2. **Error Analysis:** Investigate failure patterns
3. **Performance Monitoring:** Track execution times
4. **Credential Rotation:** Update credentials regularly
5. **Cleanup:** Archive or delete unused workflows

## Troubleshooting

### Authentication Error
```
Error: N8N_API_KEY not found in environment
```
**Solution:** Set environment variable:
```bash
export N8N_API_KEY="your-api-key"
```

### Connection Error
```
Error: HTTP 401: Unauthorized
```
**Solution:** 
1. Verify API key is correct
2. Check N8N_BASE_URL is set correctly
3. Confirm API access is enabled in n8n

### Validation Errors
```
Validation failed: Node missing 'name' field
```
**Solution:** Check workflow JSON structure, ensure all required fields present

### Execution Timeout
```
Status: timeout - Execution did not complete
```
**Solution:** 
1. Check workflow for infinite loops
2. Reduce dataset size for testing
3. Optimize expensive operations
4. Set execution timeout in workflow settings

### Rate Limiting
```
Error: HTTP 429: Too Many Requests
```
**Solution:**
1. Add Wait nodes between API calls
2. Implement exponential backoff
3. Use batch processing
4. Check API rate limits

### Missing Credentials
```
Warning: Node 'HTTP_Request' may require credentials
```
**Solution:**
1. Configure credentials in n8n UI
2. Assign credentials to node
3. Test connection before activating

## File Structure

```
~/clawd/skills/n8n/
├── SKILL.md                    # This file
├── scripts/
│   ├── n8n_api.py             # Core API client (extended)
│   ├── n8n_tester.py          # Testing & validation
│   └── n8n_optimizer.py       # Performance optimization
└── references/
    └── api.md                 # n8n API reference
```

## API Reference

For detailed n8n REST API documentation, see [references/api.md](references/api.md) or visit:
https://docs.n8n.io/api/

## Support

**Documentation:**
- n8n Official Docs: https://docs.n8n.io
- n8n Community Forum: https://community.n8n.io
- n8n API Reference: https://docs.n8n.io/api/

**Debugging:**
1. Use validation: `python3 scripts/n8n_tester.py validate --id <workflow-id>`
2. Check execution logs: `python3 scripts/n8n_api.py get-execution --id <execution-id>`
3. Review optimization report: `python3 scripts/n8n_optimizer.py report --id <workflow-id>`
4. Test with dry-run: `python3 scripts/n8n_tester.py dry-run --id <workflow-id> --data-file test.json`
