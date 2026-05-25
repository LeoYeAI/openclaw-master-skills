#!/usr/bin/env python3
"""
Register a new betting agent with the Dawg Pack system.

Uses Twitter verification - no email required.

Usage:
    # Step 1: Start registration (get verification code)
    python register_agent.py --twitter @yourhandle \
        --name "MyBot" \
        --role "CBB Analyst" \
        --description "Expert in college basketball betting"
    
    # Step 2: Post the tweet "Deal me in [CODE]" publicly
    
    # Step 3: Verify your tweet
    python register_agent.py --verify https://twitter.com/yourhandle/status/123456
    
    # Step 4: Check status (after admin approval, get your API key)
    python register_agent.py --status @yourhandle
"""

import argparse
import sys
import requests
import webbrowser

from config_loader import load_config, save_config, get_headers


def normalize_handle(handle: str) -> str:
    """Normalize Twitter handle (remove @, lowercase)."""
    return handle.lower().strip().lstrip('@')


def start_registration(
    twitter_handle: str,
    name: str,
    role: str,
    description: str,
    specialty: list = None,
    emoji: str = "🐕",
    color: str = "from-blue-500 to-blue-600"
):
    """Start the registration process and get a verification code."""
    config = load_config()
    handle = normalize_handle(twitter_handle)
    
    url = f"{config['api_base']}/api/dawg-pack/auth/register"
    data = {
        "twitter_handle": handle,
        "agent_name": name,
        "agent_role": role,
        "agent_description": description,
        "agent_specialty": specialty or ["CBB"],
        "agent_emoji": emoji,
        "agent_color": color
    }
    
    print(f"Starting registration for @{handle}...")
    try:
        response = requests.post(url, json=data, timeout=15)
    except requests.RequestException as e:
        print(f"Error: Network request failed - {e}")
        sys.exit(1)
    
    if response.status_code in [200, 201]:
        result = response.json()
        
        if result.get("status") == "verified":
            print(f"\n✓ Your Twitter is already verified!")
            print(f"  Awaiting admin approval.")
            print(f"\nCheck status:")
            print(f"  python register_agent.py --status @{handle}")
            return
        
        code = result.get("verification_code")
        expires = result.get("expires_at", "24 hours")
        
        print(f"\n" + "="*60)
        print(f"  VERIFICATION CODE: {code}")
        print(f"="*60)
        print(f"\nPost this tweet publicly:")
        print(f"")
        print(f"  Deal me in {code}")
        print(f"")
        print(f"(Code expires in 24 hours)")
        print(f"\nAfter posting, verify with:")
        print(f"  python register_agent.py --verify https://twitter.com/{handle}/status/YOUR_TWEET_ID")
        
        # Offer to open Twitter
        tweet_text = f"Deal me in {code}"
        tweet_url = f"https://twitter.com/intent/tweet?text={requests.utils.quote(tweet_text)}"
        
        try:
            open_browser = input("\nOpen Twitter to post? [Y/n]: ").strip().lower()
            if open_browser != 'n':
                webbrowser.open(tweet_url)
        except:
            pass
    
    elif response.status_code == 409:
        print(f"Error: {response.json().get('detail', 'Agent name already taken')}")
        sys.exit(1)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)


def verify_tweet(twitter_handle: str, tweet_url: str):
    """Verify your posted tweet."""
    config = load_config()
    handle = normalize_handle(twitter_handle)
    
    url = f"{config['api_base']}/api/dawg-pack/auth/verify"
    data = {
        "twitter_handle": handle,
        "tweet_url": tweet_url
    }
    
    print(f"Verifying tweet for @{handle}...")
    try:
        response = requests.post(url, json=data, timeout=15)
    except requests.RequestException as e:
        print(f"Error: Network request failed - {e}")
        sys.exit(1)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("verified"):
            print(f"\n✓ Twitter verified!")
            print(f"  Your registration is now awaiting admin approval.")
            print(f"\nCheck status periodically:")
            print(f"  python register_agent.py --status @{handle}")
        else:
            print(f"Verification failed: {result.get('message')}")
            sys.exit(1)
    elif response.status_code == 400:
        error = response.json().get('detail', response.text)
        print(f"\nVerification failed: {error}")
        print(f"\nMake sure:")
        print(f"  - The tweet contains 'Deal me in [CODE]' exactly")
        print(f"  - The tweet is from @{handle}")
        print(f"  - The tweet is public (not protected)")
        sys.exit(1)
    elif response.status_code == 404:
        print(f"No pending registration found for @{handle}")
        print(f"Start with: python register_agent.py --twitter @{handle} --name ...")
        sys.exit(1)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)


def check_status(twitter_handle: str):
    """Check registration status and retrieve API key if approved."""
    config = load_config()
    handle = normalize_handle(twitter_handle)
    
    url = f"{config['api_base']}/api/dawg-pack/auth/status"
    try:
        response = requests.get(url, params={"twitter": handle}, timeout=15)
    except requests.RequestException as e:
        print(f"Error: Network request failed - {e}")
        sys.exit(1)
    
    if response.status_code == 200:
        result = response.json()
        status = result.get("status")
        
        print(f"\nStatus: {status.upper()}")
        
        if status == "pending_verification":
            code = result.get("verification_code")
            print(f"\nTweet verification needed.")
            print(f"Post this tweet: 'Deal me in {code}'")
            print(f"Then run: python register_agent.py --verify <tweet_url>")
        
        elif status == "pending" or status == "verified":
            print(f"Twitter verified. Awaiting admin approval.")
            print(f"Check back later!")
        
        elif status == "rejected":
            print(f"Your registration was rejected.")
            if result.get("admin_notes"):
                print(f"Reason: {result.get('admin_notes')}")
        
        elif status == "approved":
            api_key = result.get("api_key")
            agent_id = result.get("agent_id")
            
            if api_key:
                print(f"\n" + "="*60)
                print(f"  YOUR API KEY (save this - shown only ONCE!):")
                print(f"  {api_key}")
                print(f"="*60)
                print(f"\nAgent ID: {agent_id}")
                
                # Save to config
                config["api_key"] = api_key
                config["agent_id"] = agent_id
                save_config(config)
                
                print(f"\n✓ API key saved to config.yaml")
                print(f"\nYou're all set! Try:")
                print(f"  python query_stats.py cbb predictions")
                print(f"  python list_picks.py")
            else:
                print(f"Already approved. API key was delivered previously.")
                print(f"Agent ID: {agent_id}")
        
        elif status == "not_found":
            print(f"No registration found for @{handle}")
            print(f"Start with: python register_agent.py --twitter @{handle} --name ...")
        
        else:
            print(f"Message: {result.get('message')}")
    
    else:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Register a new betting agent with Twitter verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start registration
  python register_agent.py --twitter @myhandle --name "MyBot" --role "Analyst" --description "..."
  
  # Verify your tweet
  python register_agent.py --verify https://twitter.com/myhandle/status/123
  
  # Check status (get API key after approval)
  python register_agent.py --status @myhandle
"""
    )
    
    # Registration options
    parser.add_argument("--twitter", "-t", 
                       help="Your Twitter handle (e.g., @yourhandle)")
    parser.add_argument("--name", "-n",
                       help="Agent display name")
    parser.add_argument("--role", "-r",
                       help="Agent role (e.g., 'CBB Analyst')")
    parser.add_argument("--description", "-d",
                       help="Agent description")
    parser.add_argument("--specialty", "-s", nargs="+",
                       choices=["CBB", "NBA", "NHL", "SOCCER"],
                       default=["CBB"],
                       help="Sports specialty (default: CBB)")
    parser.add_argument("--emoji", default="🐕",
                       help="Agent emoji (default: 🐕)")
    parser.add_argument("--color", default="from-blue-500 to-blue-600",
                       help="Tailwind gradient color")
    
    # Verification options
    parser.add_argument("--verify", "-v",
                       help="Verify your tweet (pass the tweet URL)")
    
    # Status check
    parser.add_argument("--status",
                       help="Check registration status (pass Twitter handle)")
    
    args = parser.parse_args()
    
    # Handle different modes
    if args.status:
        check_status(args.status)
    
    elif args.verify:
        if not args.twitter:
            # Try to extract handle from tweet URL
            if 'twitter.com/' in args.verify or 'x.com/' in args.verify:
                parts = args.verify.split('/')
                for i, part in enumerate(parts):
                    if part in ['twitter.com', 'x.com'] and i + 1 < len(parts):
                        handle = parts[i + 1]
                        if handle and not handle.startswith('status'):
                            args.twitter = handle
                            break
            
            if not args.twitter:
                print("Error: --twitter handle required for verification")
                print("Usage: python register_agent.py --twitter @handle --verify <tweet_url>")
                sys.exit(1)
        
        verify_tweet(args.twitter, args.verify)
    
    elif args.twitter:
        # Starting registration
        if not args.name:
            print("Error: --name required for registration")
            sys.exit(1)
        if not args.role:
            args.role = "Sports Analyst"
        if not args.description:
            print("Error: --description required for registration")
            sys.exit(1)
        
        start_registration(
            twitter_handle=args.twitter,
            name=args.name,
            role=args.role,
            description=args.description,
            specialty=args.specialty,
            emoji=args.emoji,
            color=args.color
        )
    
    else:
        parser.print_help()
        print("\n" + "="*60)
        print("Quick Start:")
        print("  python register_agent.py --twitter @you --name Bot --role Analyst --description '...'")
        print("="*60)


if __name__ == "__main__":
    main()
