# Day Trader Dashboard

A tiny local web page for the `trader-*` skills in `../.claude/skills`.
Standard library only, bound to 127.0.0.1, read-only (no order endpoint).

```bash
python3 day-trader-dashboard/server.py
# open http://127.0.0.1:8765, type SOXL, click "Entry + exit + time machine"
```

Run it on a machine that can reach Yahoo Finance. Set `PORT` to change the
port and `TRADER_SKILLS_DIR` to point at another copy of the skills. Each
ticker gets its own working folder under `data/` (gitignored).
Not financial advice.

## Scan the market

The "Scan the market" button runs `trader-scanner` as a background job and
streams its output. Pick pre-market setups (daily charts) or today's
opening-range breakouts, a size (200 / 1,000 / whole market) or type tickers
to scan only those. The first full-universe scan downloads Nasdaq Trader's
symbol lists once into `data/_market/`. The whole market is about 5,900
charts at a polite 0.3s pause, so expect it to take a while. One scan runs at
a time. A scan is a list of charts matching a rule, not a list to buy.
