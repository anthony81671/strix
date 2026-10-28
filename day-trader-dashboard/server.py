#!/usr/bin/env python3
"""Local dashboard for the day-trader-skill tools.

Serves one page on http://127.0.0.1:8765 and runs the read-only trader-*
scripts for a ticker you type. It never places an order: there is no broker,
budget or risk endpoint here, on purpose. Standard library only.

    python3 day-trader-dashboard/server.py            # then open the URL
    PORT=9000 python3 day-trader-dashboard/server.py
"""
import json
import os
import re
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.environ.get("TRADER_SKILLS_DIR") or os.path.join(HERE, "..", ".claude", "skills")
DATA = os.path.join(HERE, "data")          # per-ticker working folders (gitignored)
SYMBOL = re.compile(r"^[A-Z][A-Z0-9.\-]{0,9}$")
TIMEOUT = 120


def script(skill, name):
    return [sys.executable, os.path.join(SKILLS, "trader-" + skill, name)]


def stages(tool, sym, q):
    """The fixed command lines each button may run. Nothing user-typed except
    the validated ticker and two small whitelisted options reaches argv."""
    setup = "level" if q.get("setup") == "level" else "orb"
    hours = str(min(max(int(q.get("hours", "24") or 24), 1), 168))
    if tool == "entry":
        return [script("entry", "entry.py") + ["check", sym, "--setup", setup, "--write"]]
    if tool == "news":
        return [script("news", "news.py") + ["--tickers", sym, "--hours", hours]]
    if tool == "exit":
        return [script("exit", "exit.py") + ["plan", "--write"]]
    if tool == "timemachine":
        return [script("timemachine", "timemachine.py") + ["run", "--plan", "trader/plan.json", "--write"]]
    if tool == "pipeline":      # entry -> exit -> time machine, stops at the plan
        return (stages("entry", sym, q) + stages("exit", sym, q) + stages("timemachine", sym, q))
    if tool == "alerts":
        return [script("alerts", "alerts.py") + ["quote", sym]]
    return None


def run(tool, sym, q):
    cmds = stages(tool, sym, q)
    if cmds is None:
        return {"error": "unknown tool"}
    cwd = os.path.join(DATA, sym)
    os.makedirs(cwd, exist_ok=True)
    results = []
    for argv in cmds:
        label = " ".join(["python3"] + [os.path.relpath(argv[1], SKILLS)] + argv[2:])
        try:
            p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT)
            out, code = (p.stdout + p.stderr).strip(), p.returncode
        except subprocess.TimeoutExpired:
            out, code = "timed out after %ds" % TIMEOUT, 124
        results.append({"cmd": label, "code": code, "output": out})
    return {"symbol": sym, "results": results}


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body, ctype):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/":
            with open(os.path.join(HERE, "index.html"), "rb") as fh:
                return self._send(200, fh.read(), "text/html; charset=utf-8")
        if u.path == "/api/run":
            q = {k: v[0] for k, v in parse_qs(u.query).items()}
            sym = (q.get("symbol") or "").strip().upper()
            if not SYMBOL.match(sym):
                return self._send(400, json.dumps({"error": "bad ticker"}), "application/json")
            try:
                body = run(q.get("tool", ""), sym, q)
            except ValueError:
                return self._send(400, json.dumps({"error": "bad option"}), "application/json")
            return self._send(200, json.dumps(body), "application/json")
        self._send(404, "not found", "text/plain")

    def log_message(self, fmt, *a):
        sys.stderr.write("%s\n" % (fmt % a))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8765"))
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)   # localhost only
    print("Day Trader dashboard: http://127.0.0.1:%d  (Ctrl+C to stop)" % port)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
