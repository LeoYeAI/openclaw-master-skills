#!/usr/bin/env python3
"""
Warden Agent Tester
Test your Warden Protocol agent's API endpoints.
"""

import argparse
import requests
import json
import sys
import time
from typing import Dict, Any


class AgentTester:
    def __init__(self, url: str, api_key: str = None):
        self.url = url.rstrip('/')
        self.headers = {
            'Content-Type': 'application/json'
        }
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def test_health(self) -> bool:
        """Test health endpoint."""
        print("Testing /health endpoint...")
        try:
            response = requests.get(f"{self.url}/health", timeout=5)
            if response.status_code == 200:
                print("✓ Health check passed")
                print(f"  Response: {response.json()}")
                return True
            else:
                print(f"✗ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Health check error: {e}")
            return False
    
    def test_invoke(self, input_text: str) -> Dict[str, Any]:
        """Test invoke endpoint."""
        print(f"\nTesting /invoke with input: '{input_text}'...")
        try:
            payload = {"input": input_text}
            start_time = time.time()
            
            response = requests.post(
                f"{self.url}/invoke",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print("✓ Invoke successful")
                print(f"  Duration: {elapsed_time:.2f}s")
                print(f"  Response:")
                print(json.dumps(result, indent=2))
                return result
            else:
                print(f"✗ Invoke failed: {response.status_code}")
                print(f"  Error: {response.text}")
                return None
        except Exception as e:
            print(f"✗ Invoke error: {e}")
            return None
    
    def test_stream(self, input_text: str) -> None:
        """Test streaming endpoint."""
        print(f"\nTesting /stream with input: '{input_text}'...")
        try:
            payload = {"input": input_text}
            
            response = requests.post(
                f"{self.url}/stream",
                json=payload,
                headers=self.headers,
                stream=True,
                timeout=30
            )
            
            if response.status_code == 200:
                print("✓ Stream started")
                print("  Receiving chunks:")
                
                for line in response.iter_lines():
                    if line:
                        decoded = line.decode('utf-8')
                        if decoded.startswith('data: '):
                            data = decoded[6:]  # Remove 'data: ' prefix
                            try:
                                chunk = json.loads(data)
                                print(f"    {chunk}")
                            except json.JSONDecodeError:
                                print(f"    {data}")
            else:
                print(f"✗ Stream failed: {response.status_code}")
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"✗ Stream error: {e}")
    
    def run_test_suite(self, test_inputs: list = None):
        """Run complete test suite."""
        print("=" * 60)
        print("Warden Agent Test Suite")
        print("=" * 60)
        print(f"URL: {self.url}")
        print()
        
        # Test health
        if not self.test_health():
            print("\n⚠ Health check failed, continuing with other tests...")
        
        # Default test inputs if none provided
        if not test_inputs:
            test_inputs = [
                "Hello, can you help me?",
                "What's the weather like?",
                "Analyze Bitcoin price"
            ]
        
        # Test invoke
        print("\n" + "-" * 60)
        print("Testing Invoke Endpoint")
        print("-" * 60)
        
        for input_text in test_inputs:
            self.test_invoke(input_text)
        
        # Test stream
        print("\n" + "-" * 60)
        print("Testing Stream Endpoint")
        print("-" * 60)
        
        if len(test_inputs) > 0:
            self.test_stream(test_inputs[0])
        
        print("\n" + "=" * 60)
        print("Test Suite Complete")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Test Warden Protocol agent API"
    )
    parser.add_argument(
        "url",
        help="Agent API URL (e.g., https://api.example.com)"
    )
    parser.add_argument(
        "--api-key",
        "-k",
        help="API key for authentication"
    )
    parser.add_argument(
        "--input",
        "-i",
        action="append",
        help="Test input (can be specified multiple times)"
    )
    parser.add_argument(
        "--health-only",
        action="store_true",
        help="Only test health endpoint"
    )
    parser.add_argument(
        "--invoke-only",
        action="store_true",
        help="Only test invoke endpoint"
    )
    parser.add_argument(
        "--stream-only",
        action="store_true",
        help="Only test stream endpoint"
    )
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        print("Error: URL must start with http:// or https://")
        sys.exit(1)
    
    # Create tester
    tester = AgentTester(args.url, args.api_key)
    
    # Run specific tests if requested
    if args.health_only:
        tester.test_health()
    elif args.invoke_only:
        inputs = args.input or ["Test query"]
        for input_text in inputs:
            tester.test_invoke(input_text)
    elif args.stream_only:
        inputs = args.input or ["Test query"]
        tester.test_stream(inputs[0])
    else:
        # Run full test suite
        tester.run_test_suite(args.input)


if __name__ == "__main__":
    main()
