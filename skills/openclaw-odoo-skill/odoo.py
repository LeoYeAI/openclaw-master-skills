#!/usr/bin/env python3
"""
Odoo ERP bridge for OpenClaw.

This script acts as the interface between OpenClaw and the Odoo connector.
OpenClaw will call this script with natural language commands.
"""
import sys
import os
import json

# Add skill directory to path
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SKILL_DIR)

from odoo_skill import OdooClient, SmartActionHandler
from odoo_skill.errors import OdooError


def main():
    """Main entry point for OpenClaw skill invocation."""
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "No command provided",
            "usage": "odoo.py '<natural language command>'"
        }))
        sys.exit(1)
    
    command = " ".join(sys.argv[1:])
    
    try:
        # Initialize Odoo client
        config_path = os.path.join(SKILL_DIR, "config.json")
        if not os.path.exists(config_path):
            print(json.dumps({
                "error": "Odoo not configured. Run setup.ps1 first.",
                "config_path": config_path
            }))
            sys.exit(1)
        
        client = OdooClient.from_env()
        smart = SmartActionHandler(client)
        
        # Parse and execute command
        result = execute_command(smart, command)
        
        # Return success
        print(json.dumps({
            "success": True,
            "result": result,
            "command": command
        }, default=str))
        
    except OdooError as e:
        print(json.dumps({
            "error": str(e),
            "type": e.__class__.__name__,
            "command": command
        }))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "error": str(e),
            "type": "UnexpectedError",
            "command": command
        }))
        sys.exit(1)


def execute_command(smart: SmartActionHandler, command: str) -> dict:
    """
    Parse natural language command and execute appropriate Odoo operation.
    
    This is a simple parser - in production, OpenClaw's LLM would handle
    the parsing and call specific methods directly.
    """
    cmd_lower = command.lower()
    
    # Sales/Quotations
    if "create quotation" in cmd_lower or "create quote" in cmd_lower:
        return handle_create_quotation(smart, command)
    
    elif "confirm order" in cmd_lower or "confirm quotation" in cmd_lower:
        return handle_confirm_order(smart, command)
    
    # CRM
    elif "create lead" in cmd_lower:
        return handle_create_lead(smart, command)
    
    elif "create opportunity" in cmd_lower:
        return handle_create_opportunity(smart, command)
    
    # Purchase
    elif "create purchase" in cmd_lower or "create po" in cmd_lower:
        return handle_create_purchase(smart, command)
    
    # Inventory
    elif "check stock" in cmd_lower or "stock level" in cmd_lower:
        return handle_check_stock(smart, command)
    
    # Projects
    elif "create task" in cmd_lower:
        return handle_create_task(smart, command)
    
    # HR
    elif "create employee" in cmd_lower:
        return handle_create_employee(smart, command)
    
    # Generic fallback
    else:
        return {
            "message": "Command not recognized. Please use SKILL.md for examples.",
            "command": command
        }


def handle_create_quotation(smart: SmartActionHandler, command: str) -> dict:
    """
    Parse create quotation command.
    
    Example: "Create quotation for Snake with 100 Snake Skin at $10"
    """
    # Simple regex-free parsing (in production, LLM does this)
    # For now, return an example
    return {
        "action": "create_quotation",
        "message": "Use smart.smart_create_quotation() with customer_name and product_lines",
        "example": {
            "customer_name": "Snake",
            "product_lines": [{"name": "Snake Skin", "quantity": 100, "price_unit": 10}]
        }
    }


def handle_confirm_order(smart: SmartActionHandler, command: str) -> dict:
    """Confirm a sales order."""
    return {"action": "confirm_order", "message": "Extract order ID and call sales.confirm_order()"}


def handle_create_lead(smart: SmartActionHandler, command: str) -> dict:
    """Create CRM lead."""
    return {"action": "create_lead", "message": "Use smart.smart_create_lead()"}


def handle_create_opportunity(smart: SmartActionHandler, command: str) -> dict:
    """Create CRM opportunity."""
    return {"action": "create_opportunity", "message": "Use crm.create_opportunity()"}


def handle_create_purchase(smart: SmartActionHandler, command: str) -> dict:
    """Create purchase order."""
    return {"action": "create_purchase", "message": "Use smart.smart_create_purchase()"}


def handle_check_stock(smart: SmartActionHandler, command: str) -> dict:
    """Check product stock."""
    return {"action": "check_stock", "message": "Use inventory.check_product_availability()"}


def handle_create_task(smart: SmartActionHandler, command: str) -> dict:
    """Create project task."""
    return {"action": "create_task", "message": "Use smart.smart_create_task()"}


def handle_create_employee(smart: SmartActionHandler, command: str) -> dict:
    """Create employee."""
    return {"action": "create_employee", "message": "Use smart.smart_create_employee()"}


if __name__ == "__main__":
    main()
