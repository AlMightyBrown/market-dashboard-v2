#!/usr/bin/env python3
"""
Market Dashboard Data Fetcher
Pulls data from Yahoo Finance and writes to data/market_data.json
Run locally or via GitHub Actions daily.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yfinance as yf
except ImportError:
    print("yfinance not installed. Run: pip install yfinance")
    sys.exit(1)

# ─────────────────────────────────────────────
# CONFIGURATION — edit tickers here freely
# ─────────────────────────────────────────────

SECTIONS = {
    "us_futures": {
        "label": "US Index Futures",
        "tickers": {
            "ES=F": "S&P 500 Futures",
            "NQ=F": "Nasdaq 100 Futures",
            "YM=F": "Dow Futures",
            "RTY=F": "Russell 2000 Futures",
        }
    },
    "volatility_dollar": {
        "label": "Volatility & Dollar",
        "tickers": {
            "^VIX": "VIX",
            "^VIX3M": "VIX3M",
            "DX-Y.NYB": "DXY (US Dollar Index)",
            "EURUSD=X": "EUR/USD",
        }
    },
    "crypto": {
        "label": "Crypto",
        "tickers": {
            "BTC-USD": "Bitcoin",
            "ETH-USD": "Ethereum",
            "SOL-USD": "Solana",
        }
    },
    "metals": {
        "label": "Precious & Base Metals",
        "tickers": {
            "GC=F": "Gold",
            "SI=F": "Silver",
            "HG=F": "Copper",
        }
    },
    "energy": {
        "label": "Energy Commodities",
        "tickers": {
            "CL=F": "Crude Oil (WTI)",
            "BZ=F": "Brent Crude",
            "NG=F": "Natural Gas",
        }
    },
    "treasuries": {
        "label": "US Treasury Yields",
        "tickers": {
            "^IRX": "3-Month T-Bill",
            "^FVX": "5-Year Yield",
            "^TNX": "10-Year Yield",
            "^TYX": "30-Year Yield",
        }
    },
    "global_indices": {
        "label": "Global Market Indices",
        "tickers": {
            "^GSPC": "S&P 500",
            "^NDX": "Nasdaq 100",
            "^DJI": "Dow Jones",
            "^RUT": "Russell 2000",
            "^HSI": "Hang Seng",
            "^N225": "Nikkei 225",
            "^FTSE": "FTSE 100",
            "^GDAXI": "DAX",
        }
    },
    "major_etfs": {
        "label": "Major ETFs",
        "tickers": {
            "SPY": "SPDR S&P 500",
            "QQQ": "Invesco Nasdaq 100",
            "IWM": "iShares Russell 2000",
            "DIA": "SPDR Dow Jones",
            "GLD": "SPDR Gold",
            "TLT": "iShares 20Y Treasury",
        }
    },
    "sector_etfs": {
        "label": "S&P 500 Sectors",
        "tickers": {
            "XLK": "Technology",
            "XLF": "Financials",
            "XLV": "Health Care",
            "XLE": "Energy",
            "XLI": "Industrials",
            "XLC": "Communication Services",
            "XLY": "Consumer Discretionary",
            "XLP": "Consumer Staples",
            "XLB": "Materials",
            "XLRE": "Real Estate",
            "XLU": "Utilities",
        }
    },
    "thematic_etfs": {
        "label": "Thematic ETFs",
        "tickers": {
            "ARKK": "ARK Innovation",
            "SOXX": "iShares Semiconductor",
            "XBI": "SPDR Biotech",
            "CIBR": "First Trust Cybersecurity",
            "BOTZ": "Global Robotics & AI",
            "ICLN": "iShares Clean Energy",
            "LIT": "Global Lithium & Battery",
            "ROBO": "Robo Global Robotics",
            "HACK": "ETFMG Cybersecurity",
            "FANG": "Direxion FANG+",
        }
    },
    "country_etfs": {
        "label": "Country ETFs",
        "tickers": {
            "EWJ": "Japan (EWJ)",
            "FXI": "China Large-Cap (FXI)",
            "EWZ": "Brazil (EWZ)",
            "EWG": "Germany (EWG)",
            "EWU": "United Kingdom (EWU)",
            "EWY": "South Korea (EWY)",
            "EWA": "Australia (EWA)",
            "EWC": "Canada (EWC)",
            "INDA": "India (INDA)",
            "EWT": "Taiwan (EWT)",
        }
    },
    "watchlist": {
        "label": "My Watchlist",
        "tickers": {
            # ← ADD YOUR OWN TICKERS HERE
            "NVDA": "NVIDIA",
            "AAPL": "Apple",
            "MSFT": "Microsoft",
            "TSLA": "Tesla",
            "META": "Meta",
            "AMZN": "Amazon",
        }
    }
}

# Breadth proxies (% above 200MA approximation using ETFs vs their 52w data)
BREADTH_TICKERS = ["SPY", "QQQ", "IWM", "RSP"]

def safe_round(val, decimals=2):
    try:
        return round(float(val), decimals)
    except (TypeError, ValueError):
        return None

def pct_change(current, previous):
    try:
        return safe_round(((float(current) - float(previous)) / float(previous)) * 100)
    except (TypeError, ValueError, ZeroDivisionError):
        return None

def fetch_ticker_data(ticker_symbol):
    try:
        t = yf.Ticker(ticker_symbol)
        hist = t.history(period="1y", interval="1d")
        if hist.empty or len(hist) < 2:
            return None

        close = hist["Close"]
        current = close.iloc[-1]
        prev_close = close.iloc[-2]
        week_ago = close.iloc[-6] if len(close) >= 6 else close.iloc[0]
        ytd_start = close[close.index.year == datetime.now().year].iloc[0] if any(close.index.year == datetime.now().year) else close.iloc[0]
        high_52w = close.rolling(252).max().iloc[-1]

        # Sparkline: last 5 days
        sparkline = [safe_round(v) for v in close.iloc[-5:].tolist()]

        return {
            "price": safe_round(current),
            "prev_close": safe_round(prev_close),
            "change_1d_pct": pct_change(current, prev_close),
            "change_1w_pct": pct_change(current, week_ago),
            "change_ytd_pct": pct_change(current, ytd_start),
            "pct_from_52w_high": pct_change(current, high_52w),
            "high_52w": safe_round(high_52w),
            "sparkline": sparkline,
        }
    except Exception as e:
        print(f"  Error fetching {ticker_symbol}: {e}")
        return None

def fetch_breadth():
    """Simple breadth: check RSP vs SPY (equal weight vs cap weight spread)"""
    try:
        rsp = yf.Ticker("RSP").history(period="5d")
        spy = yf.Ticker("SPY").history(period="5d")
        spx = yf.Ticker("^GSPC").history(period="1y")
        
        # % of S&P above 200MA approximation
        above_200 = None
        if not spx.empty and len(spx) >= 200:
            close = spx["Close"]
            ma200 = close.rolling(200).mean().iloc[-1]
            above_200 = safe_round((close.iloc[-1] / ma200 - 1) * 100)

        rsp_spy_spread = None
        if not rsp.empty and not spy.empty:
            rsp_1w = pct_change(rsp["Close"].iloc[-1], rsp["Close"].iloc[0])
            spy_1w = pct_change(spy["Close"].iloc[-1], spy["Close"].iloc[0])
            if rsp_1w is not None and spy_1w is not None:
                rsp_spy_spread = safe_round(rsp_1w - spy_1w)

        return {
            "spx_vs_200ma_pct": above_200,
            "rsp_spy_spread_1w": rsp_spy_spread,
        }
    except Exception as e:
        print(f"  Breadth error: {e}")
        return {}

def main():
    print(f"Fetching market data... [{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}]")
    
    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "sections": {},
        "breadth": {}
    }

    for section_key, section_config in SECTIONS.items():
        print(f"\n[{section_config['label']}]")
        section_data = {
            "label": section_config["label"],
            "rows": []
        }
        for ticker, name in section_config["tickers"].items():
            print(f"  {ticker}...", end=" ")
            data = fetch_ticker_data(ticker)
            if data:
                data["ticker"] = ticker
                data["name"] = name
                section_data["rows"].append(data)
                print(f"${data['price']} ({data['change_1d_pct']:+.2f}%)" if data['change_1d_pct'] is not None else "ok")
            else:
                print("FAILED")
        output["sections"][section_key] = section_data

    print("\n[Breadth]")
    output["breadth"] = fetch_breadth()

    out_path = Path(__file__).parent.parent / "data" / "market_data.json"
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Data written to {out_path}")
    print(f"  Sections: {len(output['sections'])}")
    total_rows = sum(len(s['rows']) for s in output['sections'].values())
    print(f"  Total tickers fetched: {total_rows}")

if __name__ == "__main__":
    main()
