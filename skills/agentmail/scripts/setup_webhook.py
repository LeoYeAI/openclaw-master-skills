#!/usr/bin/env python3
"""
Set up AgentMail webhook endpoint

Usage:
    # Create webhook
    python setup_webhook.py --url "https://myapp.com/webhook" --create
    
    # List existing webhooks
    python setup_webhook.py --list
    
    # Delete webhook
    python setup_webhook.py --delete "webhook_id"
    
    # Test webhook with simple Flask receiver (for development)
    python setup_webhook.py --test-server

Environment:
    AGENTMAIL_API_KEY: Your AgentMail API key
"""

import argparse
import os
import sys
import json

try:
    from agentmail import AgentMail
except ImportError:
    print("Error: agentmail package not found. Install with: pip install agentmail")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Manage AgentMail webhooks')
    parser.add_argument('--create', action='store_true', help='Create new webhook')
    parser.add_argument('--url', help='Webhook URL (required for --create)')
    parser.add_argument('--events', default='message.received', help='Comma-separated event types (default: message.received)')
    parser.add_argument('--inbox-filter', help='Filter to specific inbox(es), comma-separated')
    parser.add_argument('--client-id', help='Client ID for idempotency')
    parser.add_argument('--list', action='store_true', help='List existing webhooks')
    parser.add_argument('--delete', metavar='WEBHOOK_ID', help='Delete webhook by ID')
    parser.add_argument('--test-server', action='store_true', help='Start test webhook receiver')
    
    args = parser.parse_args()
    
    if args.test_server:
        start_test_server()
        return
    
    # Get API key
    api_key = os.getenv('AGENTMAIL_API_KEY')
    if not api_key:
        print("Error: AGENTMAIL_API_KEY environment variable not set")
        sys.exit(1)
    
    # Initialize client
    client = AgentMail(api_key=api_key)
    
    if args.create:
        if not args.url:
            print("Error: --url is required when creating webhook")
            sys.exit(1)
        
        # Prepare event types
        event_types = [event.strip() for event in args.events.split(',')]
        
        # Prepare inbox filter
        inbox_ids = None
        if args.inbox_filter:
            inbox_ids = [inbox.strip() for inbox in args.inbox_filter.split(',')]
        
        try:
            webhook = client.webhooks.create(
                url=args.url,
                event_types=event_types,
                inbox_ids=inbox_ids,
                client_id=args.client_id
            )
            
            print(f"✅ Webhook created successfully!")
            print(f"   ID: {webhook.webhook_id}")
            print(f"   URL: {webhook.url}")
            print(f"   Events: {', '.join(webhook.event_types)}")
            print(f"   Enabled: {webhook.enabled}")
            if webhook.inbox_ids:
                print(f"   Inboxes: {', '.join(webhook.inbox_ids)}")
            print(f"   Created: {webhook.created_at}")
            
        except Exception as e:
            print(f"❌ Failed to create webhook: {e}")
            sys.exit(1)
    
    elif args.list:
        try:
            webhooks = client.webhooks.list()
            
            if not webhooks.webhooks:
                print("📭 No webhooks found")
                return
            
            print(f"🪝 Webhooks ({len(webhooks.webhooks)}):\n")
            for webhook in webhooks.webhooks:
                status = "✅ Enabled" if webhook.enabled else "❌ Disabled"
                print(f"{status} {webhook.webhook_id}")
                print(f"   URL: {webhook.url}")
                print(f"   Events: {', '.join(webhook.event_types)}")
                if webhook.inbox_ids:
                    print(f"   Inboxes: {', '.join(webhook.inbox_ids)}")
                print(f"   Created: {webhook.created_at}")
                print()
                
        except Exception as e:
            print(f"❌ Error listing webhooks: {e}")
            sys.exit(1)
    
    elif args.delete:
        try:
            client.webhooks.delete(args.delete)
            print(f"✅ Webhook {args.delete} deleted successfully")
            
        except Exception as e:
            print(f"❌ Failed to delete webhook: {e}")
            sys.exit(1)
    
    else:
        print("Error: Must specify --create, --list, --delete, or --test-server")
        parser.print_help()
        sys.exit(1)

def start_test_server():
    """Start a simple Flask webhook receiver for testing"""
    try:
        from flask import Flask, request, Response
    except ImportError:
        print("Error: flask package not found. Install with: pip install flask")
        sys.exit(1)
    
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return """
        <h1>AgentMail Webhook Test Server</h1>
        <p>✅ Server is running</p>
        <p>Webhook endpoint: <code>POST /webhook</code></p>
        <p>Check console output for incoming webhooks.</p>
        """
    
    @app.route('/webhook', methods=['POST'])
    def webhook():
        payload = request.json
        
        print("\n🪝 Webhook received:")
        print(f"   Event: {payload.get('event_type')}")
        print(f"   ID: {payload.get('event_id')}")
        
        if payload.get('event_type') == 'message.received':
            message = payload.get('message', {})
            print(f"   From: {message.get('from', [{}])[0].get('email')}")
            print(f"   Subject: {message.get('subject')}")
            print(f"   Preview: {message.get('preview', '')[:50]}...")
        
        print(f"   Full payload: {json.dumps(payload, indent=2)}")
        print()
        
        return Response(status=200)
    
    print("🚀 Starting webhook test server on http://localhost:3000")
    print("📡 Webhook endpoint: http://localhost:3000/webhook")
    print("\n💡 For external access, use ngrok:")
    print("   ngrok http 3000")
    print("\n🛑 Press Ctrl+C to stop\n")
    
    try:
        app.run(host='0.0.0.0', port=3000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Webhook server stopped")

if __name__ == '__main__':
    main()