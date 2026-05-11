"""
SkillPay Payment Module for Web Scraper Pro
============================================
Based on official SkillPay API: https://skillpay.me

API Endpoints:
    GET  /api/v1/billing/balance      - Check balance
    POST /api/v1/billing/charge       - Charge per call (auto returns payment link if insufficient)
    POST /api/v1/billing/payment-link - Generate payment link

Usage:
    from payment import charge_user, check_balance, get_payment_link

    # Charge before each fetch
    result = charge_user("user_123")
    if result["ok"]:
        # proceed with fetch
        pass
    else:
        print(f"Insufficient balance. Top up at: {result['payment_url']}")
"""

import requests
import os
import functools

# ═══════════════════════════════════════════════════
# SkillPay Billing Configuration
# ═══════════════════════════════════════════════════
BILLING_API_URL = 'https://skillpay.me'
BILLING_API_KEY = 'sk_d6d26f291dafc43acc8c2b6215b87cbc9b19c7d093aebdb2deeba42a3a0fea4b'
SKILL_ID = '4fb2d57e-e583-4ca3-8170-52df37a6572b'
AMOUNT_PER_CALL = 0.001  # USDT
HEADERS = {'X-API-Key': BILLING_API_KEY, 'Content-Type': 'application/json'}


def check_balance(user_id: str) -> float:
    """
    Check user's USDT balance.
    
    Args:
        user_id: Unique user identifier
    
    Returns:
        float: USDT balance amount
    """
    resp = requests.get(
        f'{BILLING_API_URL}/api/v1/billing/balance',
        params={'user_id': user_id},
        headers=HEADERS,
        timeout=30
    )
    return resp.json()['balance']


def charge_user(user_id: str) -> dict:
    """
    Charge user per call. If balance is insufficient, 
    automatically returns a BNB Chain USDT payment link.
    
    Args:
        user_id: Unique user identifier
    
    Returns:
        dict: {"ok": True, "balance": float} if charge successful
              {"ok": False, "balance": float, "payment_url": str} if insufficient balance
    """
    resp = requests.post(
        f'{BILLING_API_URL}/api/v1/billing/charge',
        headers=HEADERS,
        json={
            'user_id': user_id,
            'skill_id': SKILL_ID,
            'amount': AMOUNT_PER_CALL,
        },
        timeout=30
    )
    data = resp.json()
    if data['success']:
        return {'ok': True, 'balance': data['balance']}
    return {'ok': False, 'balance': data['balance'], 'payment_url': data.get('payment_url')}


def get_payment_link(user_id: str, amount: float = 1.0) -> str:
    """
    Generate a BNB Chain USDT top-up payment link.
    
    Args:
        user_id: Unique user identifier
        amount: USDT amount to top up
    
    Returns:
        str: Payment URL (BNB Chain USDT)
    """
    resp = requests.post(
        f'{BILLING_API_URL}/api/v1/billing/payment-link',
        headers=HEADERS,
        json={'user_id': user_id, 'amount': amount},
        timeout=30
    )
    return resp.json()['payment_url']


def require_payment(func):
    """Decorator that enforces payment before function execution."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user_id = kwargs.pop("user_id", None) or os.environ.get("SKILLPAY_USER_ID", "anonymous_user")
        
        result = charge_user(user_id)
        
        if not result['ok']:
            raise PermissionError(
                f"Insufficient balance ({result['balance']} USDT). "
                f"Top up at: {result['payment_url']}"
            )
        
        return func(*args, **kwargs)
    
    return wrapper


class PaymentContext:
    """Context manager for payment verification."""
    
    def __init__(self, user_id: str = None):
        self.user_id = user_id or os.environ.get("SKILLPAY_USER_ID", "anonymous_user")
        self.charge_result = None
    
    def __enter__(self):
        self.charge_result = charge_user(self.user_id)
        if not self.charge_result['ok']:
            raise PermissionError(
                f"Insufficient balance ({self.charge_result['balance']} USDT). "
                f"Top up at: {self.charge_result['payment_url']}"
            )
        return self.charge_result
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


if __name__ == "__main__":
    user = os.environ.get("SKILLPAY_USER_ID", "test_user")
    print(f"Checking balance for {user}...")
    try:
        balance = check_balance(user)
        print(f"Balance: {balance} USDT")
    except Exception as e:
        print(f"Error: {e}")
