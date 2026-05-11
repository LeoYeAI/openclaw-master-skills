#!/usr/bin/env python3
"""
Send HTML email with optional PDF attachment via msmtp or sendmail.

Properly constructs MIME multipart message so HTML body renders correctly
even when attachments are included.

Usage:
    python3 send-email.py --to user@example.com --subject "Daily Digest" \
        --html /tmp/td-email.html [--attach /tmp/td-digest.pdf] [--from "Bot <bot@example.com>"]
"""

import argparse
import base64
import subprocess
import sys
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formatdate
from pathlib import Path


def build_message(subject: str, from_addr: str, to_addrs: list,
                  html_path: Path, attach_path: Path = None) -> str:
    """Build a proper MIME message with HTML body and optional attachment."""
    
    html_content = html_path.read_text(encoding='utf-8')
    
    if attach_path and attach_path.exists():
        # Multipart mixed: HTML body + attachment
        msg = MIMEMultipart('mixed')
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        pdf_data = attach_path.read_bytes()
        pdf_part = MIMEApplication(pdf_data, _subtype='pdf')
        pdf_part.add_header('Content-Disposition', 'attachment',
                           filename=attach_path.name)
        msg.attach(pdf_part)
    else:
        # Simple HTML message
        msg = MIMEText(html_content, 'html', 'utf-8')
    
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = ', '.join(to_addrs)
    msg['Date'] = formatdate(localtime=True)
    
    return msg.as_string()


def send_via_msmtp(message: str, to_addrs: list) -> bool:
    """Send via msmtp (preferred)."""
    try:
        result = subprocess.run(
            ['msmtp', '--read-envelope-from'] + to_addrs,
            input=message.encode('utf-8'),
            capture_output=True,
            timeout=30
        )
        if result.returncode == 0:
            return True
        logging.error(f"msmtp failed: {result.stderr.decode()}")
        return False
    except FileNotFoundError:
        logging.debug("msmtp not found")
        return False
    except Exception as e:
        logging.error(f"msmtp error: {e}")
        return False


def send_via_sendmail(message: str, to_addrs: list) -> bool:
    """Send via sendmail (fallback)."""
    for cmd in ['sendmail', '/usr/sbin/sendmail']:
        try:
            result = subprocess.run(
                [cmd, '-t'] + to_addrs,
                input=message.encode('utf-8'),
                capture_output=True,
                timeout=30
            )
            if result.returncode == 0:
                return True
            logging.error(f"{cmd} failed: {result.stderr.decode()}")
        except FileNotFoundError:
            continue
        except Exception as e:
            logging.error(f"{cmd} error: {e}")
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Send HTML email with optional PDF attachment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
    python3 send-email.py --to user@example.com --subject "Daily Digest" --html /tmp/td-email.html
    python3 send-email.py --to a@x.com --to b@y.com --subject "Weekly" --html body.html --attach digest.pdf
    python3 send-email.py --to user@x.com --subject "Test" --html body.html --from "Bot <bot@x.com>"
"""
    )
    parser.add_argument('--to', action='append', required=True, help='Recipient email (repeatable)')
    parser.add_argument('--subject', '-s', required=True, help='Email subject')
    parser.add_argument('--html', required=True, type=Path, help='HTML body file')
    parser.add_argument('--attach', type=Path, default=None, help='PDF attachment file')
    parser.add_argument('--from', dest='from_addr', default=None, help='From address')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s"
    )
    
    if not args.html.exists():
        logging.error(f"HTML file not found: {args.html}")
        sys.exit(1)
    
    # Expand comma-separated addresses
    to_addrs = []
    for addr in args.to:
        to_addrs.extend([a.strip() for a in addr.split(',') if a.strip()])
    
    from_addr = args.from_addr or 'noreply@localhost'
    
    logging.info(f"Building email: {args.subject} → {', '.join(to_addrs)}")
    if args.attach:
        logging.info(f"Attachment: {args.attach} ({'exists' if args.attach.exists() else 'MISSING'})")
    
    message = build_message(args.subject, from_addr, to_addrs, args.html, args.attach)
    
    # Try msmtp first, then sendmail
    if send_via_msmtp(message, to_addrs):
        logging.info("✅ Sent via msmtp")
        return 0
    
    if send_via_sendmail(message, to_addrs):
        logging.info("✅ Sent via sendmail")
        return 0
    
    logging.error("❌ All send methods failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
