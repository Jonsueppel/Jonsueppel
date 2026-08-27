#!/usr/bin/env python3
import html
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def esc(value):
    return html.escape(str(value), quote=True)


def truncate(value, limit=78):
    value = " ".join(str(value).split())
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: generate_security_pulse.py INPUT_JSON OUTPUT_SVG")

    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    vulnerabilities = data.get("vulnerabilities", [])
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=7)).date()
    recent = [
        item for item in vulnerabilities
        if datetime.strptime(item["dateAdded"], "%Y-%m-%d").date() >= cutoff
    ]
    latest = sorted(vulnerabilities, key=lambda item: item["dateAdded"], reverse=True)[:3]

    rows = []
    y = 164
    for item in latest:
        label = f'{item.get("cveID", "Unknown")} · {item.get("vendorProject", "Unknown")} · {item.get("product", "Unknown")}'
        rows.append(
            f'<text x="34" y="{y}" class="entry">{esc(truncate(label))}</text>'
        )
        y += 24

    svg = f'''<svg width="820" height="250" viewBox="0 0 820 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="CISA Security Pulse">
  <defs>
    <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#08170a"/>
      <stop offset="1" stop-color="#0d1117"/>
    </linearGradient>
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      .title {{ font: 700 18px 'JetBrains Mono',Consolas,monospace; fill: #8effa0; }}
      .label {{ font: 600 11px 'JetBrains Mono',Consolas,monospace; fill: #8b949e; letter-spacing: .6px; }}
      .value {{ font: 700 25px 'JetBrains Mono',Consolas,monospace; fill: #f0f6fc; }}
      .entry {{ font: 500 12px 'JetBrains Mono',Consolas,monospace; fill: #c9d1d9; }}
      .foot {{ font: 500 10px 'JetBrains Mono',Consolas,monospace; fill: #6e7681; }}
      @keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: .35; }} }}
      .dot {{ animation: pulse 2.2s ease-in-out infinite; }}
    </style>
  </defs>
  <rect x="1" y="1" width="818" height="248" rx="8" fill="url(#panel)" stroke="#51ff4a" stroke-width="1.3"/>
  <circle cx="26" cy="28" r="5" fill="#6dff69" class="dot" filter="url(#glow)"/>
  <text x="42" y="34" class="title">CISA SECURITY PULSE</text>
  <text x="646" y="31" class="label">LIVE KEV DATA</text>

  <text x="34" y="75" class="label">KNOWN EXPLOITED</text>
  <text x="34" y="107" class="value">{esc(data.get("count", len(vulnerabilities)))}</text>
  <text x="252" y="75" class="label">ADDED · LAST 7 DAYS</text>
  <text x="252" y="107" class="value">{len(recent)}</text>
  <text x="500" y="75" class="label">CATALOG VERSION</text>
  <text x="500" y="107" class="value">{esc(data.get("catalogVersion", "Unknown"))}</text>

  <line x1="24" y1="126" x2="796" y2="126" stroke="#238636" stroke-width="1"/>
  <text x="34" y="145" class="label">LATEST CATALOG ENTRIES</text>
  {''.join(rows)}

  <text x="34" y="232" class="foot">Source: CISA Known Exploited Vulnerabilities Catalog</text>
  <text x="588" y="232" class="foot">Refreshed {now.strftime("%Y-%m-%d %H:%M UTC")}</text>
</svg>
'''
    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[2]).write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
