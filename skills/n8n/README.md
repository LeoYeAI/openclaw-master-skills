# n8n Enhanced Workflow Management Skill

Comprehensive n8n automation skill with workflow creation, testing, execution monitoring, and performance optimization capabilities.

## Features

### ✨ Workflow Creation
- **Template Library:** 6 pre-built SaaS automation workflows
- **Interactive Builder:** Guided workflow creation
- **JSON Import:** Create from existing workflow files
- **Programmatic API:** Build workflows in Python

### 🧪 Testing & Validation
- **Structure Validation:** Check workflow integrity
- **Dry-Run Testing:** Test with sample data before activation
- **Test Suites:** Run multiple test cases
- **Validation Reports:** Detailed error and warning reports

### 📊 Execution Monitoring
- **Real-time Tracking:** Monitor workflow execution status
- **Execution Logs:** Detailed execution history
- **Error Analysis:** Identify and debug failures
- **Retry Logic:** Built-in failure handling

### ⚡ Performance Optimization
- **Performance Analysis:** Comprehensive workflow metrics
- **Bottleneck Detection:** Identify slow operations
- **Optimization Suggestions:** Actionable improvement recommendations
- **Performance Scoring:** 0-100 workflow health score

## Quick Start

### 1. Setup

```bash
# Set environment variables
export N8N_API_KEY="your-api-key"
export N8N_BASE_URL="your-n8n-url-here"

# Verify connection
python3 scripts/n8n_api.py list-workflows --pretty
```

### 2. Create Your First Workflow

```bash
# Deploy a template
python3 scripts/n8n_api.py create --from-template waitlist-pipeline

# Output: {"id": "123", "name": "Waitlist to Customer Pipeline", ...}
```

### 3. Test Before Activating

```bash
# Validate structure
python3 scripts/n8n_tester.py validate --id 123

# Dry run with test data
python3 scripts/n8n_tester.py dry-run --id 123 \
  --data '{"email": "test@example.com", "name": "Test User"}'
```

### 4. Activate & Monitor

```bash
# Activate workflow
python3 scripts/n8n_api.py activate --id 123

# Monitor executions
python3 scripts/n8n_api.py list-executions --id 123 --limit 10 --pretty
```

### 5. Optimize Performance

```bash
# Generate optimization report
python3 scripts/n8n_optimizer.py report --id 123
```

## Available Templates

| Template | Description | Trigger | Key Features |
|----------|-------------|---------|--------------|
| **waitlist-pipeline** | Waitlist to customer automation | Webhook | Email validation, CRM integration, welcome emails |
| **product-hunt** | Monitor Product Hunt launches | Schedule (hourly) | Vote filtering, Slack notifications, Sheets logging |
| **social-media-crosspost** | Multi-platform posting | Webhook | Twitter, LinkedIn, Facebook parallel posting |
| **revenue-dashboard** | Revenue data collection | Schedule (daily) | Stripe integration, Sheets updates |
| **customer-onboarding** | Multi-day email sequence | Webhook | Time-delayed follow-ups, progressive engagement |
| **lead-scraping** | Lead generation pipeline | Schedule (daily) | Web scraping, data enrichment, DB storage |

## CLI Commands

### Workflow Management

```bash
# List all workflows
python3 scripts/n8n_api.py list-workflows --pretty

# Get workflow details
python3 scripts/n8n_api.py get-workflow --id <id> --pretty

# Create from template
python3 scripts/n8n_api.py create --from-template waitlist-pipeline

# Create from file
python3 scripts/n8n_api.py create --from-file workflow.json

# Activate/Deactivate
python3 scripts/n8n_api.py activate --id <id>
python3 scripts/n8n_api.py deactivate --id <id>
```

### Testing & Validation

```bash
# Validate workflow
python3 scripts/n8n_tester.py validate --id <id> --pretty

# Validate from file
python3 scripts/n8n_tester.py validate --file workflow.json --pretty

# Dry run with data
python3 scripts/n8n_tester.py dry-run --id <id> --data '{"key": "value"}'

# Dry run with file
python3 scripts/n8n_tester.py dry-run --id <id> --data-file test-data.json

# Generate test report
python3 scripts/n8n_tester.py report --id <id>

# Run test suite
python3 scripts/n8n_tester.py test-suite --id <id> --test-suite tests.json
```

### Execution Monitoring

```bash
# List executions
python3 scripts/n8n_api.py list-executions --limit 20 --pretty

# Get execution details
python3 scripts/n8n_api.py get-execution --id <exec-id> --pretty

# Execute manually
python3 scripts/n8n_api.py execute --id <workflow-id>

# Execute with data
python3 scripts/n8n_api.py execute --id <id> --data '{"key": "value"}'

# Get statistics
python3 scripts/n8n_api.py stats --id <id> --days 7 --pretty
```

### Performance Optimization

```bash
# Analyze performance
python3 scripts/n8n_optimizer.py analyze --id <id> --pretty

# Get suggestions
python3 scripts/n8n_optimizer.py suggest --id <id> --pretty

# Generate report
python3 scripts/n8n_optimizer.py report --id <id>
```

## Python API

### Basic Usage

```python
from scripts.n8n_api import N8nClient

client = N8nClient()

# List workflows
workflows = client.list_workflows(active=True)
print(f"Active workflows: {len(workflows)}")

# Create workflow
workflow = client.create_workflow({
    'name': 'My Workflow',
    'nodes': [...],
    'connections': {...}
})

# Execute workflow
result = client.execute_workflow(workflow['id'], data={'test': True})
```

### Testing

```python
from scripts.n8n_tester import WorkflowTester

tester = WorkflowTester()

# Validate
validation = tester.validate_workflow(workflow_id='123')
if validation['valid']:
    print("✓ Workflow is valid")
else:
    print(f"✗ Errors: {validation['errors']}")

# Dry run
result = tester.dry_run('123', test_data={'email': 'test@example.com'})
print(f"Status: {result['status']}")
```

### Optimization

```python
from scripts.n8n_optimizer import WorkflowOptimizer

optimizer = WorkflowOptimizer()

# Analyze
analysis = optimizer.analyze_performance('123', days=30)
print(f"Performance Score: {analysis['performance_score']}/100")
print(f"Health: {analysis['execution_metrics']['health']}")

# Get suggestions
suggestions = optimizer.suggest_optimizations('123')
print(f"Priority Actions: {len(suggestions['priority_actions'])}")
```

## Common Workflows

### Create → Test → Deploy

```bash
# 1. Create from template
python3 scripts/n8n_api.py create --from-template waitlist-pipeline > workflow.json
WORKFLOW_ID=$(cat workflow.json | jq -r '.id')

# 2. Validate structure
python3 scripts/n8n_tester.py validate --id $WORKFLOW_ID

# 3. Test with sample data
python3 scripts/n8n_tester.py dry-run --id $WORKFLOW_ID \
  --data '{"email": "test@example.com", "name": "Test User"}' --report

# 4. If tests pass, activate
python3 scripts/n8n_api.py activate --id $WORKFLOW_ID
```

### Debug Failed Workflow

```bash
# 1. Check recent executions
python3 scripts/n8n_api.py list-executions --id $WORKFLOW_ID --limit 5

# 2. Get execution details
python3 scripts/n8n_api.py get-execution --id $EXEC_ID --pretty

# 3. Validate workflow structure
python3 scripts/n8n_tester.py report --id $WORKFLOW_ID

# 4. Check for optimization issues
python3 scripts/n8n_optimizer.py report --id $WORKFLOW_ID
```

### Optimize Performance

```bash
# 1. Analyze current state
python3 scripts/n8n_optimizer.py analyze --id $WORKFLOW_ID --days 30 --pretty

# 2. Get recommendations
python3 scripts/n8n_optimizer.py suggest --id $WORKFLOW_ID --pretty

# 3. Generate full report
python3 scripts/n8n_optimizer.py report --id $WORKFLOW_ID > optimization-report.txt

# 4. Review execution stats
python3 scripts/n8n_api.py stats --id $WORKFLOW_ID --days 30 --pretty
```

## File Structure

```
~/clawd/skills/n8n/
├── README.md                   # This file
├── SKILL.md                    # Comprehensive documentation
├── scripts/
│   ├── n8n_api.py             # Core API client
│   ├── n8n_tester.py          # Testing & validation
│   └── n8n_optimizer.py       # Performance optimization
├── templates/
│   ├── README.md              # Template documentation
│   ├── *.json                 # Workflow templates
│   └── test-data-*.json       # Test data files
└── references/
    └── api.md                 # API reference
```

## Best Practices

1. **Always validate before activating:** Catch errors early
2. **Test with sample data:** Use dry-run to verify behavior
3. **Monitor execution metrics:** Track success rates and failures
4. **Regular optimization reviews:** Monthly performance analysis
5. **Use templates as starting points:** Proven patterns save time
6. **Document customizations:** Keep changelog of modifications
7. **Implement error handling:** Add error nodes for reliability
8. **Gradual rollout:** Test with limited traffic initially

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication error | Set `N8N_API_KEY` environment variable |
| Connection error | Verify `N8N_BASE_URL` and network access |
| Validation errors | Check workflow JSON structure |
| Execution timeout | Optimize expensive operations, reduce dataset size |
| Rate limiting | Add Wait nodes, implement backoff |
| Missing credentials | Configure in n8n UI, assign to nodes |

## Resources

- **Documentation:** [SKILL.md](SKILL.md)
- **Templates:** [templates/README.md](templates/README.md)
- **n8n Docs:** https://docs.n8n.io
- **n8n API:** https://docs.n8n.io/api/
- **n8n Community:** https://community.n8n.io

## Support

For issues or questions:
1. Check validation output: `python3 scripts/n8n_tester.py validate --id <id>`
2. Review execution logs: `python3 scripts/n8n_api.py get-execution --id <exec-id>`
3. Generate optimization report: `python3 scripts/n8n_optimizer.py report --id <id>`
4. Consult [SKILL.md](SKILL.md) for detailed documentation

## License

Part of the Clawdbot skills library.
