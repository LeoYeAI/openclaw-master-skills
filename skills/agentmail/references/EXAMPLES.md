# AgentMail Usage Examples

Common patterns and use cases for AgentMail in AI agent workflows.

## Basic Agent Email Setup

### 1. Create Agent Identity

```python
from agentmail import AgentMail
import os

client = AgentMail(api_key=os.getenv("AGENTMAIL_API_KEY"))

# Create inbox for your agent
agent_inbox = client.inboxes.create(
    username="spike-assistant",
    display_name="Spike - AI Assistant",
    client_id="spike-main-inbox"  # Prevents duplicates
)

print(f"Agent email: {agent_inbox.inbox_id}")
# Output: spike-assistant@agentmail.to
```

### 2. Send Status Updates

```python
def send_task_completion(task_name, details, recipient):
    client.inboxes.messages.send(
        inbox_id="spike-assistant@agentmail.to",
        to=recipient,
        subject=f"Task Completed: {task_name}",
        text=f"Hello! I've completed the task: {task_name}\n\nDetails:\n{details}\n\nBest regards,\nSpike 🦝",
        html=f"""
        <p>Hello!</p>
        <p>I've completed the task: <strong>{task_name}</strong></p>
        <h3>Details:</h3>
        <p>{details.replace(chr(10), '<br>')}</p>
        <p>Best regards,<br>Spike 🦝</p>
        """
    )

# Usage
send_task_completion(
    "PDF Processing", 
    "Rotated 5 pages, extracted text, and saved output to /tmp/processed.pdf",
    "adam@example.com"
)
```

## Customer Support Automation

### Auto-Reply System

```python
def setup_support_auto_reply():
    """Set up webhook to auto-reply to support emails"""
    
    # Create support inbox
    support_inbox = client.inboxes.create(
        username="support",
        display_name="Customer Support",
        client_id="support-inbox"
    )
    
    # Register webhook for auto-replies
    webhook = client.webhooks.create(
        url="https://your-app.com/webhook/support",
        event_types=["message.received"],
        inbox_ids=[support_inbox.inbox_id],
        client_id="support-webhook"
    )
    
    return support_inbox, webhook

def handle_support_message(message):
    """Process incoming support message and send auto-reply"""
    
    subject = message['subject'].lower()
    sender = message['from'][0]['email']
    
    # Determine response based on subject keywords
    if 'billing' in subject or 'payment' in subject:
        response = """
        Thank you for your billing inquiry. 
        
        Our billing team will review your request and respond within 24 hours. 
        For urgent billing issues, please call 1-800-SUPPORT.
        
        Best regards,
        Customer Support Team
        """
    elif 'bug' in subject or 'error' in subject:
        response = """
        Thank you for reporting this issue.
        
        Our technical team has been notified and will investigate. 
        We'll update you within 48 hours with our findings.
        
        If you have additional details, please reply to this email.
        
        Best regards,
        Technical Support
        """
    else:
        response = """
        Thank you for contacting us!
        
        We've received your message and will respond within 24 hours.
        For urgent issues, please call our support line.
        
        Best regards,
        Customer Support Team
        """
    
    # Send auto-reply
    client.inboxes.messages.send(
        inbox_id=message['inbox_id'],
        to=sender,
        subject=f"Re: {message['subject']}",
        text=response
    )
    
    # Log for human follow-up
    print(f"Auto-replied to {sender} about: {message['subject']}")
```

## Document Processing Workflow

### Email → Process → Reply

```python
import base64
import tempfile
from pathlib import Path

def process_pdf_attachment(message):
    """Extract attachments, process PDFs, and reply with results"""
    
    processed_files = []
    
    for attachment in message.get('attachments', []):
        if attachment['content_type'] == 'application/pdf':
            # Decode attachment
            pdf_data = base64.b64decode(attachment['content'])
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(pdf_data)
                temp_path = tmp.name
            
            try:
                # Process PDF (example: extract text)
                extracted_text = extract_pdf_text(temp_path)
                
                # Save processed result
                output_path = f"/tmp/processed_{attachment['filename']}.txt"
                with open(output_path, 'w') as f:
                    f.write(extracted_text)
                
                processed_files.append({
                    'original': attachment['filename'],
                    'output': output_path,
                    'preview': extracted_text[:200] + '...'
                })
                
            finally:
                Path(temp_path).unlink()  # Clean up temp file
    
    if processed_files:
        # Send results back
        results_text = "\n".join([
            f"Processed {f['original']}:\n{f['preview']}\n"
            for f in processed_files
        ])
        
        # Attach processed files
        attachments = []
        for f in processed_files:
            with open(f['output'], 'r') as file:
                content = base64.b64encode(file.read().encode()).decode()
            attachments.append({
                'filename': Path(f['output']).name,
                'content': content,
                'content_type': 'text/plain'
            })
        
        client.inboxes.messages.send(
            inbox_id=message['inbox_id'],
            to=message['from'][0]['email'],
            subject=f"Re: {message['subject']} - Processed",
            text=f"I've processed your PDF files:\n\n{results_text}",
            attachments=attachments
        )

def extract_pdf_text(pdf_path):
    """Extract text from PDF file"""
    # Implementation depends on your PDF library
    # Example with pdfplumber:
    import pdfplumber
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text
```

## Task Assignment and Tracking

### Email-Based Task Management

```python
def create_task_tracker_inbox():
    """Set up inbox for task assignments via email"""
    
    inbox = client.inboxes.create(
        username="tasks",
        display_name="Task Assignment Bot",
        client_id="task-tracker"
    )
    
    # Webhook for processing task emails
    webhook = client.webhooks.create(
        url="https://your-app.com/webhook/tasks",
        event_types=["message.received"],
        inbox_ids=[inbox.inbox_id]
    )
    
    return inbox

def process_task_assignment(message):
    """Parse email and create task from content"""
    
    subject = message['subject']
    body = message.get('text', '')
    sender = message['from'][0]['email']
    
    # Simple task parsing
    if subject.startswith('TASK:'):
        task_title = subject[5:].strip()
        
        # Extract due date, priority, etc. from body
        lines = body.split('\n')
        due_date = None
        priority = 'normal'
        description = body
        
        for line in lines:
            if line.startswith('Due:'):
                due_date = line[4:].strip()
            elif line.startswith('Priority:'):
                priority = line[9:].strip().lower()
        
        # Create task in your system
        task_id = create_task_in_system({
            'title': task_title,
            'description': description,
            'due_date': due_date,
            'priority': priority,
            'assigned_by': sender
        })
        
        # Confirm task creation
        client.inboxes.messages.send(
            inbox_id=message['inbox_id'],
            to=sender,
            subject=f"Task Created: {task_title} (#{task_id})",
            text=f"""
Task successfully created!

ID: #{task_id}
Title: {task_title}
Priority: {priority}
Due: {due_date or 'Not specified'}

I'll send updates as work progresses.

Best regards,
Task Bot
            """
        )
        
        # Start processing task...
        process_task_async(task_id)

def create_task_in_system(task_data):
    """Create task in your task management system"""
    # Implementation depends on your system
    # Return task ID
    return "T-12345"

def send_task_update(task_id, status, details, assignee_email):
    """Send task progress update"""
    
    client.inboxes.messages.send(
        inbox_id="tasks@agentmail.to",
        to=assignee_email,
        subject=f"Task Update: #{task_id} - {status}",
        text=f"""
Task #{task_id} Status Update

Status: {status}
Details: {details}

View full details: https://your-app.com/tasks/{task_id}

Best regards,
Task Bot
        """
    )
```

## Integration with External Services

### GitHub Issue Creation from Email

```python
def setup_github_integration():
    """Create inbox for GitHub issue creation"""
    
    inbox = client.inboxes.create(
        username="github-issues",
        display_name="GitHub Issue Creator",
        client_id="github-integration"
    )
    
    return inbox

def create_github_issue_from_email(message):
    """Convert email to GitHub issue"""
    
    import requests
    
    # Extract issue details
    title = message['subject'].replace('BUG:', '').replace('FEATURE:', '').strip()
    body_content = message.get('text', '')
    sender = message['from'][0]['email']
    
    # Determine issue type and labels
    labels = ['email-created']
    if 'BUG:' in message['subject']:
        labels.append('bug')
    elif 'FEATURE:' in message['subject']:
        labels.append('enhancement')
    
    # Create GitHub issue
    github_token = os.getenv('GITHUB_TOKEN')
    repo = 'your-org/your-repo'
    
    issue_data = {
        'title': title,
        'body': f"""
**Reported via email by:** {sender}

**Original message:**
{body_content}

**Email Thread:** {message.get('thread_id')}
        """,
        'labels': labels
    }
    
    response = requests.post(
        f'https://api.github.com/repos/{repo}/issues',
        json=issue_data,
        headers={
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    )
    
    if response.status_code == 201:
        issue = response.json()
        
        # Reply with GitHub issue link
        client.inboxes.messages.send(
            inbox_id=message['inbox_id'],
            to=sender,
            subject=f"Re: {message['subject']} - GitHub Issue Created",
            text=f"""
Thank you for your report!

I've created a GitHub issue for tracking:

Issue #{issue['number']}: {issue['title']}
Link: {issue['html_url']}

You can track progress and add comments directly on GitHub.

Best regards,
GitHub Bot
            """
        )
        
        print(f"Created GitHub issue #{issue['number']} from email")
    else:
        print(f"Failed to create GitHub issue: {response.text}")

# Usage in webhook handler
def handle_github_webhook(payload):
    if payload['event_type'] == 'message.received':
        message = payload['message']
        if message['inbox_id'] == 'github-issues@agentmail.to':
            create_github_issue_from_email(message)
```

## Notification and Alert System

### Multi-Channel Alerts

```python
def setup_alert_system():
    """Create alert inbox for system notifications"""
    
    alerts_inbox = client.inboxes.create(
        username="alerts",
        display_name="System Alerts",
        client_id="alert-system"
    )
    
    return alerts_inbox

def send_system_alert(alert_type, message, severity='info', recipients=None):
    """Send system alert via email"""
    
    if recipients is None:
        recipients = ['admin@company.com', 'ops@company.com']
    
    severity_emoji = {
        'critical': '🚨',
        'warning': '⚠️',
        'info': 'ℹ️',
        'success': '✅'
    }
    
    emoji = severity_emoji.get(severity, 'ℹ️')
    
    client.inboxes.messages.send(
        inbox_id="alerts@agentmail.to",
        to=recipients,
        subject=f"{emoji} [{severity.upper()}] {alert_type}",
        text=f"""
System Alert

Type: {alert_type}
Severity: {severity}
Time: {datetime.now().isoformat()}

Message:
{message}

This is an automated alert from the monitoring system.
        """,
        html=f"""
<h2>{emoji} System Alert</h2>
<table>
<tr><td><strong>Type:</strong></td><td>{alert_type}</td></tr>
<tr><td><strong>Severity:</strong></td><td style="color: {'red' if severity == 'critical' else 'orange' if severity == 'warning' else 'blue'}">{severity}</td></tr>
<tr><td><strong>Time:</strong></td><td>{datetime.now().isoformat()}</td></tr>
</table>

<h3>Message:</h3>
<p>{message.replace(chr(10), '<br>')}</p>

<p><em>This is an automated alert from the monitoring system.</em></p>
        """
    )

# Usage examples
send_system_alert("Database Connection", "Unable to connect to primary database", "critical")
send_system_alert("Backup Complete", "Daily backup completed successfully", "success")
send_system_alert("High CPU Usage", "CPU usage above 80% for 5 minutes", "warning")
```

## Testing and Development

### Local Development Setup

```python
def setup_dev_environment():
    """Set up AgentMail for local development"""
    
    # Create development inboxes
    dev_inbox = client.inboxes.create(
        username="dev-test",
        display_name="Development Testing",
        client_id="dev-testing"
    )
    
    print(f"Development inbox: {dev_inbox.inbox_id}")
    print("Use this for testing email workflows locally")
    
    # Test email sending
    test_response = client.inboxes.messages.send(
        inbox_id=dev_inbox.inbox_id,
        to="your-personal-email@gmail.com",
        subject="AgentMail Development Test",
        text="This is a test email from your AgentMail development setup."
    )
    
    print(f"Test email sent: {test_response.message_id}")
    
    return dev_inbox

# Run development setup
if __name__ == "__main__":
    setup_dev_environment()
```