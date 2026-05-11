#!/usr/bin/env python3
"""
Send email via AgentMail API

Usage:
    python send_email.py --inbox "sender@agentmail.to" --to "recipient@example.com" --subject "Hello" --text "Message body"
    
    # With HTML content
    python send_email.py --inbox "sender@agentmail.to" --to "recipient@example.com" --subject "Hello" --html "<p>Message body</p>"
    
    # With attachment
    python send_email.py --inbox "sender@agentmail.to" --to "recipient@example.com" --subject "Hello" --text "See attachment" --attach "/path/to/file.pdf"

Environment:
    AGENTMAIL_API_KEY: Your AgentMail API key
"""

import argparse
import os
import sys
import base64
import mimetypes
from pathlib import Path

try:
    from agentmail import AgentMail
except ImportError:
    print("Error: agentmail package not found. Install with: pip install agentmail")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Send email via AgentMail')
    parser.add_argument('--inbox', required=True, help='Sender inbox email address')
    parser.add_argument('--to', required=True, help='Recipient email address')
    parser.add_argument('--cc', help='CC email address(es), comma-separated')
    parser.add_argument('--bcc', help='BCC email address(es), comma-separated')
    parser.add_argument('--subject', default='', help='Email subject')
    parser.add_argument('--text', help='Plain text body')
    parser.add_argument('--html', help='HTML body')
    parser.add_argument('--attach', action='append', help='Attachment file path (can be used multiple times)')
    parser.add_argument('--reply-to', help='Reply-to email address')
    
    args = parser.parse_args()
    
    # Get API key
    api_key = os.getenv('AGENTMAIL_API_KEY')
    if not api_key:
        print("Error: AGENTMAIL_API_KEY environment variable not set")
        sys.exit(1)
    
    # Validate required content
    if not args.text and not args.html:
        print("Error: Must provide either --text or --html content")
        sys.exit(1)
    
    # Initialize client
    client = AgentMail(api_key=api_key)
    
    # Prepare recipients
    recipients = [email.strip() for email in args.to.split(',')]
    cc_recipients = [email.strip() for email in args.cc.split(',')] if args.cc else None
    bcc_recipients = [email.strip() for email in args.bcc.split(',')] if args.bcc else None
    
    # Prepare attachments
    attachments = []
    if args.attach:
        for file_path in args.attach:
            path = Path(file_path)
            if not path.exists():
                print(f"Error: Attachment file not found: {file_path}")
                sys.exit(1)
            
            # Read and encode file
            with open(path, 'rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')
            
            # Detect content type
            content_type, _ = mimetypes.guess_type(str(path))
            if not content_type:
                content_type = 'application/octet-stream'
            
            attachments.append({
                'filename': path.name,
                'content': content,
                'content_type': content_type
            })
            print(f"Added attachment: {path.name} ({content_type})")
    
    # Send email
    try:
        print(f"Sending email from {args.inbox} to {', '.join(recipients)}")
        
        response = client.inboxes.messages.send(
            inbox_id=args.inbox,
            to=recipients,
            cc=cc_recipients,
            bcc=bcc_recipients,
            reply_to=args.reply_to,
            subject=args.subject,
            text=args.text,
            html=args.html,
            attachments=attachments if attachments else None
        )
        
        print(f"✅ Email sent successfully!")
        print(f"   Message ID: {response.message_id}")
        print(f"   Thread ID: {response.thread_id}")
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()