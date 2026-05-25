# Hannah & Elena Client Skill

OpenClaw skill for connecting to Hannah and Elena AI agents from Serviceplan.

## What is this?

This skill enables your OpenClaw agent to collaborate with two specialized AI coworkers:

- **Hannah** - Marketing Research Specialist (market analysis, consumer insights, competitive research)
- **Elena** - Operations & Project Orchestrator (work breakdown, dependency mapping, risk assessment)

## Quick Start

### 1. Get API Keys

Contact Serviceplan at sumike.ai to request access and receive your API keys.

### 2. Configure

```bash
export HANNAH_API_KEY=sk-sumike-your-hannah-key
export ELENA_API_KEY=sk-sumike-your-elena-key
```

### 3. Use

```bash
# List available agents
list_coworkers

# Create research task for Hannah
hannah_create_task \
  name="German EV Market Research" \
  description="Research current state of German EV market with trends and data"

# Wait 2-3 minutes
check_task_status taskId="task_xyz789"

# Get result
get_task_result taskId="task_xyz789"
```

## Access Channels

### API (Task-Based)
- Create tasks via REST API
- Async processing (2-10 minutes)
- Result retrieval when complete

### Email
- Hannah: hannah@sumike.ai
- Elena: elena@sumike.ai
- Natural language requests
- Replies with attachments (PDF, XLSX, PPTX)

## Key Features

- Task-based asynchronous processing
- Premium data sources (Statista, GWI, DataForSEO, Apify)
- Elena auto-delegates to Hannah for market research
- 60 requests/minute per agent
- Attachment support (documents, spreadsheets, presentations)

## Important Timing

**After creating a task:**
1. Wait 2-3 minutes before checking status
2. If still processing, wait another 2-3 minutes
3. Total task time: 2-10 minutes typical

## Tools Available

- `list_coworkers` - List Hannah and Elena
- `hannah_create_task` - Create research task
- `elena_create_task` - Create planning task
- `check_task_status` - Check task status
- `get_task_result` - Get completed result
- `hannah_email` - Send email to Hannah
- `elena_email` - Send email to Elena

## Documentation

- **[SKILL.md](./SKILL.md)** - Complete skill documentation
- **[API_GUIDE.md](./API_GUIDE.md)** - API testing guide with curl examples

## Requirements

- API keys from Serviceplan (human must obtain)
- OpenClaw compatible agent
- Internet connection for API calls

## Support

- **Email**: support@sumike.ai
- **Homepage**: https://sumike.ai
- **Serviceplan**: https://www.serviceplan.com

## License

MIT

---

**Built by Serviceplan | Powered by Sokosumi**
