# Market Command Centre

A personal market dashboard — auto-refreshed daily via GitHub Actions using Yahoo Finance data.

**Live demo:** `https://YOUR-USERNAME.github.io/market-dashboard/`

---

## What's included

| File | Purpose |
|---|---|
| `index.html` | Dashboard frontend (pure HTML/CSS/JS, no build step) |
| `data/market_data.json` | Auto-generated data file read by the dashboard |
| `scripts/fetch_data.py` | Pulls data from Yahoo Finance via `yfinance` |
| `.github/workflows/update_data.yml` | GitHub Actions: runs the script daily and commits the result |

---

## Quick start

### 1. Fork / clone this repo

```bash
git clone https://github.com/YOUR-USERNAME/market-dashboard.git
cd market-dashboard
```

### 2. Install Python dependencies

```bash
pip install yfinance
```

### 3. Fetch data locally (first run)

```bash
python scripts/fetch_data.py
```

This writes `data/market_data.json`. Open `index.html` in your browser — you should see live data.

### 4. Push to GitHub

```bash
git add .
git commit -m "init"
git push origin main
```

### 5. Enable GitHub Pages

- Go to your repo → **Settings → Pages**
- Source: `Deploy from a branch` → branch: `main` → folder: `/ (root)`
- Save. Your dashboard will be live at `https://YOUR-USERNAME.github.io/market-dashboard/` in ~1 minute.

### 6. Enable GitHub Actions

The workflow at `.github/workflows/update_data.yml` runs daily at **06:00 UTC**.

To test it manually:
- Go to **Actions** tab → `Update Market Data` → **Run workflow**

The action will fetch fresh data and commit `market_data.json` automatically. GitHub Pages will pick up the change within minutes.

---

## Customising your data

All ticker configuration lives in **`scripts/fetch_data.py`** — one place, no touching HTML.

### Change the daily refresh time

In `.github/workflows/update_data.yml`:

```yaml
- cron: '0 6 * * *'   # 06:00 UTC = 18:00 HKT / ~19:00 NZST
```

Adjust to your preferred time. Use [crontab.guru](https://crontab.guru) if needed.

### Add tickers to My Watchlist

In `scripts/fetch_data.py`, find the `watchlist` section:

```python
"watchlist": {
    "label": "My Watchlist",
    "tickers": {
        "NVDA": "NVIDIA",
        "AAPL": "Apple",
        # ← add more here: "TICKER": "Display Name",
    }
},
```

### Add a new section entirely

Copy any existing section block and give it a new key:

```python
"hk_stocks": {
    "label": "Hong Kong Stocks",
    "tickers": {
        "0700.HK": "Tencent",
        "9988.HK": "Alibaba",
        "0005.HK": "HSBC",
    }
},
```

Then in `index.html`, add the new key to either `MACRO_SECTIONS` or `EQUITY_SECTIONS`:

```js
const MACRO_SECTIONS = ['us_futures', 'volatility_dollar', ..., 'hk_stocks'];
```

---

## Sections overview

| Section | Tickers |
|---|---|
| US Index Futures | ES, NQ, YM, RTY |
| Volatility & Dollar | VIX, VIX3M, DXY, EUR/USD |
| Crypto | BTC, ETH, SOL |
| Metals | Gold, Silver, Copper |
| Energy | WTI, Brent, Natural Gas |
| Treasury Yields | 3M, 5Y, 10Y, 30Y |
| Global Indices | SPX, NDX, DJI, HSI, Nikkei, FTSE, DAX |
| Major ETFs | SPY, QQQ, IWM, DIA, GLD, TLT |
| Sector ETFs | All 11 SPDR sectors (XLK through XLU) |
| Thematic ETFs | ARKK, SOXX, XBI, CIBR, BOTZ, ICLN, LIT... |
| Country ETFs | Japan, China, Brazil, Germany, UK, Korea, India... |
| My Watchlist | Fully customisable |

---

## Notes

- Data is end-of-day (previous close). Not real-time.
- `yfinance` is unofficial and may break if Yahoo Finance changes their API. Check for updates: `pip install --upgrade yfinance`
- This is for personal informational use only — not financial advice.
