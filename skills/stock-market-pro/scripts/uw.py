#!/usr/bin/env python3
# /// script
# dependencies = [
#   "playwright",
#   "rich",
#   "pandas"
# ]
# ///

import sys
import asyncio
import re
import signal
from playwright.async_api import async_playwright
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live

console = Console()

def parse_val(val_str):
    """Parses strings like '$1.31b', '$512.30m', '1,258,024' into numbers."""
    if not val_str or val_str == "-": return 0
    val_str = val_str.replace('$', '').replace(',', '').lower()
    multiplier = 1
    if 'b' in val_str:
        multiplier = 1_000_000_000
        val_str = val_str.replace('b', '')
    elif 'm' in val_str:
        multiplier = 1_000_000
        val_str = val_str.replace('m', '')
    elif 'k' in val_str:
        multiplier = 1_000
        val_str = val_str.replace('k', '')
    try:
        return float(val_str) * multiplier
    except:
        return 0

async def fetch_advanced_options(ticker):
    """Scrape UW option stats + (when available) a small sample of live flow.

    Hard constraints:
    - Must never hang indefinitely (timeouts + outer guard).
    - Free tier only has detailed live flow for: JPM, INTC, IWM, XSP.

    NOTE: In some environments Playwright can stall at launch/navigation.
    We wrap launch/navigation calls with asyncio.wait_for AND a process-level alarm.
    """

    url = f"https://unusualwhales.com/stock/{ticker}/overview"

    async with async_playwright() as p:
        # Browser launch can occasionally hang → hard cap
        browser = await asyncio.wait_for(
            p.chromium.launch(
                headless=True,
                args=["--disable-gpu", "--no-sandbox"],
            ),
            timeout=10,
        )
        context = await asyncio.wait_for(
            browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            timeout=5,
        )
        page = await asyncio.wait_for(context.new_page(), timeout=5)

        # Default timeouts (ms) to avoid indefinite waits
        page.set_default_timeout(8_000)
        page.set_default_navigation_timeout(12_000)

        overview = {}
        detailed_flow = []

        try:
            # 1. Overview Page Data (always attempt this)
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_timeout(800)  # allow client-rendered stats
            await page.wait_for_selector("text=Put Call Ratio", timeout=20_000)
            
            async def get_val(label):
                try:
                    element = page.locator(f"text='{label}' >> xpath=..").locator("div,span,p").last
                    return await element.inner_text()
                except: return "N/A"

            overview = {
                "pc_ratio": await get_val("Put Call Ratio"),
                "put_vol": await get_val("Put Volume"),
                "call_vol": await get_val("Call Volume"),
                "put_prem": await get_val("Put Premium"),
                "call_prem": await get_val("Call Premium"),
                "sentiment": "N/A" # Default, will try to get from element
            }
            
            sent_elem = page.locator("div:has-text('🐂'), div:has-text('🐻')").filter(has_text="%").first
            if await sent_elem.count() > 0:
                overview["sentiment"] = await sent_elem.inner_text()
            else: # Fallback if specific emoji not found, try a more general sentiment text
                general_sentiment_match = await page.locator("text=/\d+% (Bullish|Bearish|Neutral)/").first.inner_text()
                if general_sentiment_match:
                    overview["sentiment"] = general_sentiment_match


            # 2. Live Flow Data (conditional, only for free tickers)
            FREE_FLOW_TICKERS = ["JPM", "INTC", "IWM", "XSP"] # Per Unusual Whales free tier
            
            if ticker.upper() in FREE_FLOW_TICKERS:
                flow_url = f"https://unusualwhales.com/live-options-flow?ticker_symbol={ticker}"
                await page.goto(flow_url, wait_until="domcontentloaded")
                await page.wait_for_timeout(1200)  # allow table render
                
                # Check for the actual data table, not just a message saying "no data"
                # This selector is robust to empty tables vs. "no data" messages
                data_rows = await page.locator("table tr:has-not(th)").all()
                
                for row in data_rows[:30]: # Limit to first 30 rows for efficiency and relevance
                    cols = await row.locator("td").all()
                    if len(cols) >= 20: # Ensure enough columns for parsing
                        try:
                            # Adjusted column indices based on my previous manual observation and robustness
                            # Need to be careful with exact index as site might change, prioritizing common ones
                            # Time (cols[0]), Side (cols[3]), Contract (cols[4]), Type (cols[5]), DTE (cols[6])
                            # Stock (cols[7]), Bid-Ask (cols[8]), Spot (cols[9]), Size (cols[10]), Premium (cols[11])
                            # Volume (cols[12]), OI (cols[13]), Chain Bid/Ask (cols[14]), Legs (cols[15]), Code (cols[16])
                            # Flags (cols[17]), Tags (cols[18]), Sentiment (cols[19])
                            
                            contract_text = await cols[4].inner_text()
                            strike_match = re.findall(r'\d+\.?\d*', contract_text)
                            strike = strike_match[0] if strike_match else "N/A"
                            
                            # Using the observed column indices again, if they've shifted from prev attempt
                            # Let's assume most relevant ones for deep dive are Premium, Vol, OI, Sentiment
                            prem_val = parse_val(await cols[11].inner_text()) # Premium often col 11 or 12
                            vol_val = parse_val(await cols[12].inner_text())  # Volume often col 12 or 13
                            oi_val = parse_val(await cols[13].inner_text())    # OI often col 13 or 14
                            sent_val = await cols[19].inner_text() # Sentiment should be consistent
                            
                            detailed_flow.append({
                                "strike": strike,
                                "premium": prem_val,
                                "volume": vol_val,
                                "oi": oi_val,
                                "vol_gt_oi": vol_val > oi_val and oi_val > 0,
                                "sentiment": sent_val
                            })
                        except Exception as parse_e:
                            # print(f"Warning: Could not parse flow row: {parse_e}") # For debugging
                            continue # Skip malformed rows
            
        except Exception as e:
            # Handle potential timeout or navigation errors for either page
            return f"Error during scraping for {ticker}: {str(e)}"
        finally:
            await browser.close()
        
        return {"overview": overview, "flow": detailed_flow}

def print_advanced_report(ticker, data):
    if isinstance(data, str):
        console.print(f"[red]{data}[/red]")
        return

    ov = data.get('overview', {})
    flow = data.get('flow', [])

    # 1. Overview Panel
    ov_table = Table.grid(expand=True)
    ov_table.add_column(style="cyan", justify="left")
    ov_table.add_column(style="magenta", justify="right")
    
    # Check if overview data is actually populated
    if ov:
        ov_table.add_row("Put/Call Ratio", ov.get('pc_ratio', 'N/A'))
        ov_table.add_row("Call Premium", ov.get('call_prem', 'N/A'))
        ov_table.add_row("Put Premium", ov.get('put_prem', 'N/A'))
        
        sent_text = ov.get('sentiment', 'N/A')
        sent_color = "green" if "🐂" in sent_text or "Bullish" in sent_text else "red" if "🐻" in sent_text or "Bearish" in sent_text else "yellow"
        
        console.print(Panel(ov_table, title=f"🐳 {ticker} Option Overview", border_style="bright_blue"))
        console.print(Panel(f"Market Sentiment: [{sent_color}]{sent_text}[/{sent_color}]", box=None, justify="center"))
    else:
        console.print(Panel(f"[red]Could not retrieve overview data for {ticker}.[/red]", border_style="red"))


    # 2. Advanced Insights (only if flow data is available)
    if flow:
        whales = [f for f in flow if f['premium'] >= 100000] # $100k+ premium
        unusual_vol_gt_oi = [f for f in flow if f['vol_gt_oi']]
        
        # Target Strike Estimation (simple mode: most frequent strike)
        strikes = [f['strike'] for f in flow if f['strike'] != "N/A"]
        target_strike = max(set(strikes), key=strikes.count) if strikes else "N/A"

        # Calculate sentiment breakdown from flow for the last few trades
        flow_bull_count = sum(1 for f in flow if "bullish" in f['sentiment'].lower())
        flow_bear_count = sum(1 for f in flow if "bearish" in f['sentiment'].lower())
        total_flow_sentiment_trades = flow_bull_count + flow_bear_count
        
        flow_sentiment_display = "N/A"
        if total_flow_sentiment_trades > 0:
            flow_bull_pct = (flow_bull_count / total_flow_sentiment_trades) * 100
            flow_bear_pct = (flow_bear_count / total_flow_sentiment_trades) * 100
            flow_sentiment_display = f"[green]{flow_bull_pct:.1f}% Bullish[/green] | [red]{flow_bear_pct:.1f}% Bearish[/red]"

        insight_text = f"🎯 [bold]Most Active Strike:[/bold] ${target_strike}\n"
        insight_text += f"📊 [bold]Recent Flow Sentiment:[/bold] {flow_sentiment_display}\n"
        insight_text += f"🐋 [bold]Large Whale Trades (>$100k):[/bold] {len(whales)} detected\n"
        insight_text += f"⚠️ [bold]Unusual Entries (Volume > OI):[/bold] {len(unusual_vol_gt_oi)} detected (potential new positions)"
        
        console.print(Panel(insight_text, title="🔍 Deep Insights from Live Flow", border_style="yellow"))
        
        if whales:
            w_table = Table(title="Top Whale Bets (>$100k Premium)", box=None)
            w_table.add_column("Strike", style="cyan")
            w_table.add_column("Premium", style="green")
            w_table.add_column("Sentiment", style="bold")
            for w in whales[:5]: # Show top 5 whale trades
                w_color = "green" if "bullish" in w['sentiment'].lower() else "red"
                w_table.add_row(f"${w['strike']}", f"${w['premium']:,.0f}", f"[{w_color}]{w['sentiment']}[/{w_color}]")
            console.print(w_table)
    else:
        console.print(Panel("[dim]Detailed live option flow data is not available for this ticker (free tier limitation or no recent trades).[/dim]", border_style="dim"))


class _AlarmTimeout(Exception):
    pass


def _alarm_handler(signum, frame):
    raise _AlarmTimeout()


async def _run_with_timeout(ticker: str, total_timeout_s: int = 20):
    """Global timeout guard.

    Why both?
    - asyncio.wait_for covers awaited coroutines
    - signal alarm covers rare stalls where the event loop doesn't progress
    """
    try:
        signal.signal(signal.SIGALRM, _alarm_handler)
        signal.alarm(total_timeout_s)
        return await asyncio.wait_for(fetch_advanced_options(ticker), timeout=total_timeout_s)
    except asyncio.TimeoutError:
        return f"Error during scraping for {ticker}: TIMEOUT after {total_timeout_s}s"
    except _AlarmTimeout:
        return f"Error during scraping for {ticker}: ALARM TIMEOUT after {total_timeout_s}s"
    finally:
        try:
            signal.alarm(0)
        except Exception:
            pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python uw.py TICKER")
        sys.exit(1)

    ticker = sys.argv[1].upper()
    total_timeout_s = 25

    with console.status(f"[bold green]Scraping Option Data for {ticker} (UW, timeout {total_timeout_s}s)..."):
        data = asyncio.run(_run_with_timeout(ticker, total_timeout_s=total_timeout_s))

    print_advanced_report(ticker, data)
