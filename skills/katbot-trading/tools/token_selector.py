import argparse, requests

HL_TOKENS = {
    'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana',
    'ARB': 'arbitrum', 'HYPE': 'hyperliquid', 'AVAX': 'avalanche-2',
    'LINK': 'chainlink', 'OP': 'optimism', 'INJ': 'injective-protocol',
    'SUI': 'sui', 'APT': 'aptos', 'TIA': 'celestia',
    'DOGE': 'dogecoin', 'ADA': 'cardano', 'DOT': 'polkadot',
    'NEAR': 'near', 'FTM': 'fantom', 'ATOM': 'cosmos',
    'LTC': 'litecoin', 'BCH': 'bitcoin-cash', 'UNI': 'uniswap',
    'AAVE': 'aave', 'MKR': 'maker', 'CRV': 'curve-dao-token',
    'WIF': 'dogwifcoin', 'PEPE': 'pepe', 'BONK': 'bonk',
    'XRP': 'ripple', 'BNB': 'binancecoin', 'MATIC': 'matic-network',
    'RUNE': 'thorchain', 'IMX': 'immutable-x',
    'STX': 'blockstack', 'ALGO': 'algorand',
    'TAO': 'bittensor', 'SEI': 'sei-network',
}

def get_top_tokens(top: int = 5, bearish: bool = False):
    ids_str = ','.join(HL_TOKENS.values())
    r = requests.get(
        f'https://api.coingecko.com/api/v3/simple/price?ids={ids_str}&vs_currencies=usd&include_24hr_change=true',
        timeout=15)
    r.raise_for_status()
    data = r.json()
    id_to_sym = {v: k for k, v in HL_TOKENS.items()}
    results = [
        {'symbol': id_to_sym[cg_id], 'price': vals.get('usd', 0), 'pct_24h': vals.get('usd_24h_change') or 0}
        for cg_id, vals in data.items() if cg_id in id_to_sym
    ]
    return sorted(results, key=lambda x: x['pct_24h'], reverse=not bearish)[:top]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--top', type=int, default=5)
    parser.add_argument('--direction', choices=['bullish', 'bearish'], default='bullish')
    args = parser.parse_args()

    tokens = get_top_tokens(args.top, args.direction == 'bearish')
    print(json.dumps(tokens, indent=2))
