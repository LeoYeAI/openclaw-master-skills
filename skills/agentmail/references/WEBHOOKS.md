# AgentMail Webhooks Guide

Webhooks enable real-time, event-driven email processing. When events occur (like receiving a message), AgentMail immediately sends a POST request to your registered endpoint.

## Event Types

### message.received
Triggered when a new email arrives. Contains full message and thread data.

**Use case:** Auto-reply to support emails, process attachments, route messages

```json
{
  "type": "event",
  "event_type": "message.received",
  "event_id": "evt_123abc",
  "message": {
    "inbox_id": "support@agentmail.to",
    "thread_id": "thd_789ghi",
    "message_id": "msg_123abc",
    "from": [{"name": "Jane Doe", "email": "jane@example.com"}],
    "to": [{"name": "Support", "email": "support@agentmail.to"}],
    "subject": "Question about my account",
    "text": "I need help with...",
    "html": "<p>I need help with...</p>",
    "timestamp": "2023-10-27T10:00:00Z",
    "labels": ["received"]
  },
  "thread": {
    "thread_id": "thd_789ghi",
    "subject": "Question about my account",
    "participants": ["jane@example.com", "support@agentmail.to"],
    "message_count": 1
  }
}
```

### message.sent
Triggered when you successfully send a message.

```json
{
  "type": "event",
  "event_type": "message.sent",
  "event_id": "evt_456def",
  "send": {
    "inbox_id": "support@agentmail.to",
    "thread_id": "thd_789ghi",
    "message_id": "msg_456def",
    "timestamp": "2023-10-27T10:05:00Z",
    "recipients": ["jane@example.com"]
  }
}
```

### message.delivered
Triggered when your message reaches the recipient's mail server.

### message.bounced
Triggered when a message fails to deliver.

```json
{
  "type": "event",
  "event_type": "message.bounced",
  "bounce": {
    "type": "Permanent",
    "sub_type": "General",
    "recipients": [{"address": "invalid@example.com", "status": "bounced"}]
  }
}
```

### message.complained
Triggered when recipients mark your message as spam.

## Local Development Setup

### Step 1: Install Dependencies

```bash
pip install agentmail flask ngrok python-dotenv
```

### Step 2: Set up ngrok

1. Create account at [ngrok.com](https://ngrok.com/)
2. Install: `brew install ngrok` (macOS) or download from website
3. Authenticate: `ngrok config add-authtoken YOUR_AUTHTOKEN`

### Step 3: Create Webhook Receiver

Create `webhook_receiver.py`:

```python
from flask import Flask, request, Response
import json
from agentmail import AgentMail
import os

app = Flask(__name__)
client = AgentMail(api_key=os.getenv("AGENTMAIL_API_KEY"))

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    payload = request.json
    
    if payload['event_type'] == 'message.received':
        message = payload['message']
        
        # Auto-reply example
        response_text = f"Thanks for your email about '{message['subject']}'. We'll get back to you soon!"
        
        client.inboxes.messages.send(
            inbox_id=message['inbox_id'],
            to=message['from'][0]['email'],
            subject=f"Re: {message['subject']}",
            text=response_text
        )
        
        print(f"Auto-replied to {message['from'][0]['email']}")
    
    return Response(status=200)

if __name__ == '__main__':
    app.run(port=3000)
```

### Step 4: Start Services

Terminal 1 - Start ngrok:
```bash
ngrok http 3000
```

Copy the forwarding URL (e.g., `https://abc123.ngrok-free.app`)

Terminal 2 - Start webhook receiver:
```bash
python webhook_receiver.py
```

### Step 5: Register Webhook

```python
from agentmail import AgentMail

client = AgentMail(api_key="your_api_key")

webhook = client.webhooks.create(
    url="https://abc123.ngrok-free.app/webhook",
    client_id="dev-webhook"
)
```

### Step 6: Test

Send an email to your AgentMail inbox and watch the console output.

## Production Deployment

### Webhook Verification

Verify incoming webhooks are from AgentMail:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected}", signature)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-AgentMail-Signature')
    if not verify_webhook(request.data.decode(), signature, webhook_secret):
        return Response(status=401)
    
    # Process webhook...
```

### Error Handling

Return 200 status quickly, process in background:

```python
from threading import Thread
import time

def process_webhook_async(payload):
    try:
        # Heavy processing here
        time.sleep(5)  # Simulate work
        handle_message(payload)
    except Exception as e:
        print(f"Webhook processing error: {e}")
        # Log to error tracking service

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    payload = request.json
    
    # Return 200 immediately
    Thread(target=process_webhook_async, args=(payload,)).start()
    return Response(status=200)
```

### Retry Logic

AgentMail retries failed webhooks with exponential backoff. Handle idempotency:

```python
processed_events = set()

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    event_id = request.json['event_id']
    
    if event_id in processed_events:
        return Response(status=200)  # Already processed
    
    # Process event...
    processed_events.add(event_id)
    return Response(status=200)
```

## Common Patterns

### Auto-Reply Bot

```python
def handle_message_received(message):
    if 'support' in message['to'][0]['email']:
        # Support auto-reply
        reply_text = "Thanks for contacting support! We'll respond within 24 hours."
    elif 'sales' in message['to'][0]['email']:
        # Sales auto-reply
        reply_text = "Thanks for your interest! A sales rep will contact you soon."
    else:
        return
    
    client.inboxes.messages.send(
        inbox_id=message['inbox_id'],
        to=message['from'][0]['email'],
        subject=f"Re: {message['subject']}",
        text=reply_text
    )
```

### Message Routing

```python
def route_message(message):
    subject = message['subject'].lower()
    
    if 'billing' in subject or 'payment' in subject:
        forward_to_slack('#billing-team', message)
    elif 'bug' in subject or 'error' in subject:
        create_github_issue(message)
    elif 'feature' in subject:
        add_to_feature_requests(message)
```

### Attachment Processing

```python
def process_attachments(message):
    for attachment in message.get('attachments', []):
        if attachment['content_type'] == 'application/pdf':
            # Process PDF
            pdf_content = base64.b64decode(attachment['content'])
            text = extract_pdf_text(pdf_content)
            
            # Reply with extracted text
            client.inboxes.messages.send(
                inbox_id=message['inbox_id'],
                to=message['from'][0]['email'],
                subject=f"Re: {message['subject']} - PDF processed",
                text=f"I extracted this text from your PDF:\n\n{text}"
            )
```

## Webhook Security

- **Always verify signatures** in production
- **Use HTTPS endpoints** only
- **Validate payload structure** before processing
- **Implement rate limiting** to prevent abuse
- **Return 200 quickly** to avoid retries