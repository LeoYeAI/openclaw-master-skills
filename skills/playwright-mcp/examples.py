#!/usr/bin/env python3
"""Example script for using Playwright MCP server with OpenClaw.

This script demonstrates how to programmatically interact with
the Playwright MCP server for browser automation.
"""

import subprocess
import json
import sys


def run_mcp_command(tool_name: str, params: dict) -> dict:
    """Run a single MCP tool command via playwright-mcp.
    
    Note: In real usage with OpenClaw, the MCP server runs continuously
    and tools are called via the MCP protocol. This script shows the
    conceptual flow.
    """
    # Build MCP request
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": params
        },
        "id": 1
    }
    
    # In real implementation, this would be sent to running MCP server
    # For now, we just print what would happen
    print(f"MCP Call: {tool_name}")
    print(f"Params: {json.dumps(params, indent=2)}")
    return {"status": "example", "tool": tool_name}


def example_navigate_and_click():
    """Example: Navigate to a page and click a button."""
    print("=== Example: Navigate and Click ===\n")
    
    # Step 1: Navigate
    run_mcp_command("browser_navigate", {
        "url": "https://example.com",
        "waitUntil": "networkidle"
    })
    
    # Step 2: Click element
    run_mcp_command("browser_click", {
        "selector": "button#submit",
        "timeout": 5000
    })
    
    # Step 3: Get text to verify
    run_mcp_command("browser_get_text", {
        "selector": ".result-message"
    })


def example_fill_form():
    """Example: Fill and submit a form."""
    print("\n=== Example: Fill Form ===\n")
    
    steps = [
        ("browser_navigate", {"url": "https://example.com/login"}),
        ("browser_type", {"selector": "#username", "text": "myuser"}),
        ("browser_type", {"selector": "#password", "text": "mypass"}),
        ("browser_click", {"selector": "button[type=submit]"}),
    ]
    
    for tool, params in steps:
        run_mcp_command(tool, params)


def example_extract_data():
    """Example: Extract data using JavaScript."""
    print("\n=== Example: Extract Data ===\n")
    
    run_mcp_command("browser_navigate", {
        "url": "https://example.com/products"
    })
    
    # Extract product data
    run_mcp_command("browser_evaluate", {
        "script": """
            () => {
                return Array.from(document.querySelectorAll('.product')).map(p => ({
                    name: p.querySelector('.name')?.textContent,
                    price: p.querySelector('.price')?.textContent
                }));
            }
        """
    })


def main():
    """Run examples."""
    print("Playwright MCP Usage Examples")
    print("=" * 50)
    print()
    print("Note: These are conceptual examples showing MCP tool calls.")
    print("In practice, OpenClaw manages the MCP server lifecycle.")
    print()
    
    example_navigate_and_click()
    example_fill_form()
    example_extract_data()
    
    print("\n" + "=" * 50)
    print("For actual usage, configure MCP server in OpenClaw config.")


if __name__ == "__main__":
    main()
