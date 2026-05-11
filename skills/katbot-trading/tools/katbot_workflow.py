import sys, os, time, json, argparse, importlib.util, pathlib, subprocess
import requests
from katbot_client import get_token, request_recommendation, poll_recommendation, execute_recommendation, get_portfolio, get_config
from token_selector import get_top_tokens

_TOOLS_DIR = str(pathlib.Path(__file__).parent.resolve())

def get_bmi():
    """Fetch BMI by running btc_momentum.py --json with the current interpreter."""
    script_path = os.path.join(_TOOLS_DIR, "btc_momentum.py")
    result = subprocess.run(
        [sys.executable, script_path, "--json"],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": _TOOLS_DIR},
    )
    if result.returncode != 0:
        raise RuntimeError(f"btc_momentum.py failed: {result.stderr.strip()}")
    data = json.loads(result.stdout)
    return {"bmi": data["bmi"], "signal": data["signal"], "btc_24h_pct": data["btc_24h_pct"]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--portfolio-id', type=int, help="Optional override for portfolio ID from config")
    parser.add_argument('--top', type=int, default=5)
    args = parser.parse_args()

    token = get_token()
    
    # Load portfolio ID from config if not provided
    portfolio_id = args.portfolio_id
    if not portfolio_id:
        config = get_config()
        portfolio_id = config.get("portfolio_id")
    
    if not portfolio_id:
        print("Error: --portfolio-id is required or must be set in katbot_config.json via onboarding")
        sys.exit(1)

    bmi_data = get_bmi()
    bullish = bmi_data['bmi'] >= 15
    bearish = bmi_data['bmi'] <= -15

    if not bullish and not bearish:
        print("Market is neutral. Skipping.")
        return

    tokens = get_top_tokens(args.top, bearish)
    symbols = [t['symbol'] for t in tokens]
    
    msg = f"Market is {'bullish' if bullish else 'bearish'}. Tokens: {symbols}. Get recommendation."
    ticket = request_recommendation(token, portfolio_id, msg)
    result = poll_recommendation(token, ticket['ticket_id'])
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
