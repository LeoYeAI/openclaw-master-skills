
from leg_optimizer import LegOptimizer
from chain_analyzer import ChainFetcher
import json

fetcher = ChainFetcher()
opt = LegOptimizer(account_total=2000)

try:
    chain = fetcher.fetch_chain_for_date('QQQ', 1771477200) # Feb 20
except Exception as e:
    print(f"Error fetching chain: {e}")
    exit(1)

S = chain.underlying_price
T = chain.dte / 365.0
r = 0.045
iv = 0.20 # Reasonable floor

matches = []

# Try Put Spreads
for short_opt in chain.puts:
    for long_opt in chain.puts:
        if short_opt['strike'] <= long_opt['strike']: continue
        
        width = short_opt['strike'] - long_opt['strike']
        if width < 5 or width > 12: continue
        
        short_prem = short_opt['mid_price']
        long_prem = long_opt['mid_price']
        credit = short_prem - long_prem
        
        if credit <= 0: continue
        
        max_profit = credit * 100
        max_loss = (width - credit) * 100
        
        # Calculate POP
        pop = opt.calc.pop_vertical_spread(S, short_opt['strike'], long_opt['strike'], T, iv, credit, 'put_credit')
        
        matches.append({
            'type': 'put_credit',
            'short': short_opt['strike'],
            'long': long_opt['strike'],
            'width': width,
            'profit': max_profit,
            'loss': max_loss,
            'pop': pop
        })

# Try Call Spreads
for short_opt in chain.calls:
    for long_opt in chain.calls:
        if short_opt['strike'] >= long_opt['strike']: continue
        
        width = long_opt['strike'] - short_opt['strike']
        if width < 5 or width > 12: continue
        
        short_prem = short_opt['mid_price']
        long_prem = long_opt['mid_price']
        credit = short_prem - long_prem
        
        if credit <= 0: continue
        
        max_profit = credit * 100
        max_loss = (width - credit) * 100
        
        # Calculate POP
        pop = opt.calc.pop_vertical_spread(S, short_opt['strike'], long_opt['strike'], T, iv, credit, 'call_credit')
        
        matches.append({
            'type': 'call_credit',
            'short': short_opt['strike'],
            'long': long_opt['strike'],
            'width': width,
            'profit': max_profit,
            'loss': max_loss,
            'pop': pop
        })

# Filter for the target: Loss around 400
final_matches = [m for m in matches if 300 <= m['loss'] <= 450]

# Sort by proximity to target (Profit 80, Loss 400)
final_matches.sort(key=lambda x: abs(x['profit'] - 80) + abs(x['loss'] - 400))

for m in final_matches[:10]:
    print(f"{m['type'].upper()} | {m['short']}/{m['long']} | Width: {m['width']} | Profit: ${m['profit']:.2f} | Loss: ${m['loss']:.2f} | POP: {m['pop']*100:.1f}%")
