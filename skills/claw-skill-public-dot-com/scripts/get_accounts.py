import os
import subprocess
import sys

try:
    from public_api_sdk import PublicApiClient, PublicApiClientConfiguration
    from public_api_sdk.auth_config import ApiKeyAuthConfig
except ImportError:
    print("Installing required dependency: publicdotcom-py...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "publicdotcom-py==0.1.8"])
    from public_api_sdk import PublicApiClient, PublicApiClientConfiguration
    from public_api_sdk.auth_config import ApiKeyAuthConfig

from config import get_api_secret


def get_accounts():
    secret = get_api_secret()

    if not secret:
        print("Error: PUBLIC_COM_SECRET is not set.")
        sys.exit(1)

    try:
        client = PublicApiClient(
            ApiKeyAuthConfig(api_secret_key=secret),
            config=PublicApiClientConfiguration()
        )

        accounts_response = client.get_accounts()

        print("Your Public.com Accounts:")
        print("-" * 40)
        for account in accounts_response.accounts:
            print(f"Account ID: {account.account_id}")
            print(f"Account Type: {account.account_type}")
            print("-" * 40)

        client.close()
    except Exception as e:
        print(f"Error fetching accounts: {e}")
        sys.exit(1)


if __name__ == "__main__":
    get_accounts()
