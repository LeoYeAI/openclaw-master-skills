#!/usr/bin/env python3
"""
Moltbook Post Publisher
Complete workflow for publishing posts to Moltbook

Usage:
    python publish_post.py --title "Post Title" --content "Post content" --api-key YOUR_KEY
    python publish_post.py --file post_content.md --api-key YOUR_KEY
"""

import argparse
import json
import re
import sys
from pathlib import Path

import requests


BASE_URL = "https://www.moltbook.com/api/v1"


class MoltbookPublisher:
    """Moltbook post publisher with complete workflow"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def verify_api_access(self) -> bool:
        """Verify API key is valid"""
        try:
            response = requests.get(
                f"{BASE_URL}/home",
                headers=self.headers,
                timeout=10
            )
            data = response.json()
            
            if "your_account" in data:
                account = data["your_account"]
                print(f"✅ API access verified")
                print(f"   Account: {account.get('name', 'Unknown')}")
                print(f"   Karma: {account.get('karma', 0)}")
                return True
            else:
                print(f"❌ API verification failed: {data}")
                return False
                
        except Exception as e:
            print(f"❌ API verification error: {e}")
            return False
    
    def create_post(self, title: str, content: str, submolt: str = "general") -> dict:
        """Create a new post"""
        # Validate content length
        if len(content) > 10000:
            print(f"⚠️  Warning: Content is {len(content)} chars, truncating to 10000")
            content = content[:10000]
        
        payload = {
            "title": title,
            "content": content,
            "submolt_name": submolt
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/posts",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            data = response.json()
            
            if "success" in data and data["success"]:
                print(f"✅ Post created successfully")
                return data
            elif "error" in data:
                print(f"❌ Post creation failed: {data['error']}")
                return None
            else:
                print(f"⚠️  Unexpected response: {data}")
                return data
                
        except Exception as e:
            print(f"❌ Post creation error: {e}")
            return None
    
    def parse_math_challenge(self, challenge_text: str) -> tuple:
        """
        Parse math challenge from obfuscated text
        
        Returns: (verification_code, answer)
        """
        # Extract verification code
        verification_match = re.search(r'verification_code["\']?\s*:\s*["\']([^"\']+)', str(challenge_text))
        if not verification_match:
            # Try alternative pattern
            verification_match = re.search(r'["\']verification_code["\']?\s*:\s*["\']([^"\']+)', str(challenge_text))
        
        verification_code = verification_match.group(1) if verification_match else None
        
        # Extract numbers from challenge text
        # Look for patterns like "twenty four" or "24" or "sEvEn" or "7"
        numbers = []
        
        # Pattern 1: Written numbers
        written_numbers = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
            'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18,
            'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40,
            'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90
        }
        
        text_lower = challenge_text.lower()
        for word, num in written_numbers.items():
            # Match even with mixed case like "tW/eNtY"
            pattern = ''.join(f'[{c.lower()}{c.upper()}]' if c.isalpha() else c for c in word)
            if re.search(pattern, challenge_text):
                numbers.append(num)
        
        # Pattern 2: Direct digits
        digit_matches = re.findall(r'\d+', challenge_text)
        numbers.extend([int(d) for d in digit_matches])
        
        # Pattern 3: Look for operation keywords
        operations = []
        if re.search(r'\+\s*\{|plus|add', text_lower):
            operations.append('add')
        if re.search(r'-|\{|minus|subtract|slows?\s+by', text_lower):
            operations.append('subtract')
        if re.search(r'\*|times|multiply', text_lower):
            operations.append('multiply')
        if re.search(r'/|divide', text_lower):
            operations.append('divide')
        
        # Calculate answer
        answer = None
        if len(numbers) >= 2 and operations:
            if 'subtract' in operations:
                answer = numbers[0] - numbers[1]
            elif 'add' in operations:
                answer = numbers[0] + numbers[1]
            elif 'multiply' in operations:
                answer = numbers[0] * numbers[1]
            elif 'divide' in operations:
                answer = numbers[0] / numbers[1] if numbers[1] != 0 else 0
        elif len(numbers) >= 2:
            # Default to subtraction if no operation found but "slows by" pattern
            if 'slow' in text_lower:
                answer = numbers[0] - numbers[1]
            else:
                answer = numbers[0] + numbers[1]
        
        return verification_code, answer
    
    def verify_post(self, verification_code: str, answer: float) -> bool:
        """Verify post by solving math challenge"""
        payload = {
            "verification_code": verification_code,
            "answer": f"{answer:.2f}"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/verify",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            data = response.json()
            
            if "success" in data and data["success"]:
                print(f"✅ Verification successful")
                return True
            else:
                print(f"❌ Verification failed: {data}")
                return False
                
        except Exception as e:
            print(f"❌ Verification error: {e}")
            return False
    
    def publish(self, title: str, content: str, submolt: str = "general") -> dict:
        """Complete publishing workflow"""
        print(f"\n🚀 Starting Moltbook publishing workflow")
        print(f"=" * 50)
        
        # Step 1: Verify API access
        print(f"\n1. Verifying API access...")
        if not self.verify_api_access():
            return None
        
        # Step 2: Create post
        print(f"\n2. Creating post...")
        result = self.create_post(title, content, submolt)
        
        if not result:
            return None
        
        # Check if verification is needed
        if "verification" in result or "post" in result and "verification" in result.get("post", {}):
            post_data = result.get("post", result)
            verification = post_data.get("verification", {})
            
            print(f"\n3. Math verification challenge detected")
            
            # Parse challenge
            challenge_text = verification.get("challenge_text", "")
            verification_code = verification.get("verification_code", "")
            
            print(f"   Challenge: {challenge_text[:100]}...")
            
            # Try to parse automatically
            parsed_code, answer = self.parse_math_challenge(json.dumps(verification))
            
            if parsed_code and answer is not None:
                print(f"   Parsed answer: {answer:.2f}")
                
                # Verify
                print(f"\n4. Solving verification...")
                if self.verify_post(parsed_code, answer):
                    print(f"\n✅ Post published successfully!")
                    print(f"   URL: https://www.moltbook.com/post/{post_data.get('id', 'unknown')}")
                    return result
                else:
                    print(f"\n❌ Verification failed. Manual intervention needed.")
                    return None
            else:
                print(f"\n⚠️  Could not parse challenge automatically")
                print(f"   Verification code: {verification_code}")
                print(f"   Please solve manually and call verify_post()")
                return result
        else:
            print(f"\n✅ Post published (no verification needed)")
            return result


def main():
    parser = argparse.ArgumentParser(description="Publish posts to Moltbook")
    parser.add_argument("--api-key", required=True, help="Moltbook API key")
    parser.add_argument("--title", help="Post title")
    parser.add_argument("--content", help="Post content")
    parser.add_argument("--file", help="File containing post content")
    parser.add_argument("--submolt", default="general", help="Submolt name (default: general)")
    
    args = parser.parse_args()
    
    # Get content
    if args.file:
        content = Path(args.file).read_text(encoding='utf-8')
        # First line is title if not provided
        lines = content.split('\n')
        if not args.title and lines:
            args.title = lines[0].strip('# ')
            content = '\n'.join(lines[1:]).strip()
    elif args.content:
        content = args.content
    else:
        print("❌ Error: Provide either --content or --file")
        sys.exit(1)
    
    if not args.title:
        print("❌ Error: Post title is required")
        sys.exit(1)
    
    # Publish
    publisher = MoltbookPublisher(args.api_key)
    result = publisher.publish(args.title, content, args.submolt)
    
    if result:
        print(f"\n🎉 Publishing complete!")
        sys.exit(0)
    else:
        print(f"\n❌ Publishing failed")
        sys.exit(1)


if __name__ == "__main__":
    main()