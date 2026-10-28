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
