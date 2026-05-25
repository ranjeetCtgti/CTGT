from __future__ import annotations

import argparse
import html
import os
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv() -> bool:
        return False

from db import DatabaseError, init_database


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CTGT lead dashboard")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind.")
    parser.add_argument("--port", type=int, default=8787, help="Port to serve the dashboard on.")
    parser.add_argument("--limit", type=int, default=200, help="Maximum number of signal rows to render.")
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    args = parse_args()

    try:
        database = init_database()
    except DatabaseError as exc:
        print(f"Dashboard startup failed: {exc}")
        return 1

    handler_class = build_handler(database=database, signal_limit=args.limit)
    server = ThreadingHTTPServer((args.host, args.port), handler_class)
    print(f"Dashboard running on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def build_handler(database: Any, signal_limit: int) -> type[BaseHTTPRequestHandler]:
    class DashboardHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path not in {"/", "/index.html"}:
                self.send_error(404, "Not found")
                return

            filters = _coerce_filters(parse_qs(parsed.query))
            try:
                all_leads = database.get_leads()
                leads = all_leads[:12]
                signals = database.get_signals(
                    source=filters["source"] or None,
                    lead_score=filters["lead_score"] or None,
                    company_query=filters["company"] or None,
                    limit=signal_limit,
                )
                source_stats = database.get_dashboard_source_stats()
            except Exception as exc:
                self._write_html(_render_error_page(str(exc)))
                return

            page = _render_dashboard(
                all_leads=all_leads,
                leads=leads,
                signals=signals,
                source_stats=source_stats,
                filters=filters,
                signal_limit=signal_limit,
            )
            self._write_html(page)

        def log_message(self, format: str, *args: object) -> None:
            return

        def _write_html(self, body: str) -> None:
            encoded = body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

    return DashboardHandler


def _coerce_filters(query: dict[str, list[str]]) -> dict[str, str]:
    return {
        "source": (query.get("source", [""])[0] or "").strip().lower(),
        "lead_score": (query.get("lead_score", [""])[0] or "").strip().lower(),
        "company": (query.get("company", [""])[0] or "").strip(),
    }


def _render_dashboard(
    all_leads: list[Any],
    leads: list[Any],
    signals: list[Any],
    source_stats: list[Any],
    filters: dict[str, str],
    signal_limit: int,
) -> str:
    lead_counts = Counter(lead.lead_score for lead in all_leads)
    total_signals = sum(stat.signal_count for stat in source_stats)
    total_companies = len(all_leads)
    displayed_leads = len(leads)
    active_filter_count = sum(1 for value in filters.values() if value)

    source_cards = "".join(_render_source_card(stat) for stat in source_stats) or _empty_state("No source stats yet.")
    lead_cards = "".join(_render_lead_card(lead) for lead in leads) or _empty_state("No company leads yet.")
    signal_rows = "".join(_render_signal_row(signal) for signal in signals) or _empty_state_row(10, "No NLP-clean signals match the current filters.")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CTGT Lead Dashboard</title>
  <style>
    :root {{
      --bg: #f3efe6;
      --panel: #fffaf1;
      --panel-strong: #fffdf8;
      --ink: #1d2a33;
      --muted: #61707c;
      --line: #d8cfbf;
      --accent: #0d7a6b;
      --accent-soft: #d9efe9;
      --hot: #b33a3a;
      --warm: #cb7b18;
      --cold: #3d6f93;
      --shadow: 0 12px 28px rgba(37, 41, 46, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(13, 122, 107, 0.12), transparent 28%),
        linear-gradient(180deg, #f8f3ea 0%, var(--bg) 100%);
    }}
    a {{ color: var(--accent); }}
    .shell {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 28px;
    }}
    .hero {{
      background: linear-gradient(135deg, rgba(255, 250, 241, 0.96), rgba(247, 240, 225, 0.96));
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 28px;
      box-shadow: var(--shadow);
    }}
    .eyebrow {{
      letter-spacing: 0.16em;
      text-transform: uppercase;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 10px;
    }}
    h1 {{
      margin: 0;
      font-size: 40px;
      line-height: 1.05;
    }}
    .sub {{
      margin-top: 12px;
      max-width: 840px;
      color: var(--muted);
      font-size: 16px;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin-top: 24px;
    }}
    .stat {{
      background: var(--panel-strong);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px;
    }}
    .stat .label {{
      color: var(--muted);
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .stat .value {{
      font-size: 34px;
      margin-top: 6px;
      line-height: 1.1;
    }}
    .stat .value.compact {{
      font-size: 24px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 22px;
      margin-top: 22px;
    }}
    .panel {{
      background: rgba(255, 253, 248, 0.94);
      border: 1px solid var(--line);
      border-radius: 22px;
      padding: 22px;
      box-shadow: var(--shadow);
    }}
    .panel h2 {{
      margin: 0 0 14px;
      font-size: 24px;
    }}
    .panel + .panel {{
      margin-top: 22px;
    }}
    .filters {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      align-items: end;
    }}
    label {{
      display: block;
      font-size: 13px;
      color: var(--muted);
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    input, select {{
      width: 100%;
      padding: 11px 12px;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: #fffdfa;
      color: var(--ink);
      font: inherit;
    }}
    .actions {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .button {{
      display: inline-block;
      border: 1px solid var(--accent);
      background: var(--accent);
      color: white;
      text-decoration: none;
      border-radius: 999px;
      padding: 11px 16px;
      font-size: 14px;
    }}
    .button.secondary {{
      background: transparent;
      color: var(--accent);
    }}
    .source-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 14px;
    }}
    .source-card, .lead-card {{
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px;
      background: var(--panel-strong);
    }}
    .card-head {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: flex-start;
    }}
    .card-title {{
      font-size: 19px;
      line-height: 1.2;
    }}
    .metric-value {{
      font-size: 30px;
      line-height: 1;
      margin-top: 6px;
    }}
    .lead-list {{
      display: grid;
      gap: 12px;
    }}
    .section-note {{
      margin-top: 14px;
    }}
    .token-list {{
      margin-top: 10px;
    }}
    .pill {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .pill.hot {{ background: rgba(179, 58, 58, 0.12); color: var(--hot); }}
    .pill.warm {{ background: rgba(203, 123, 24, 0.14); color: var(--warm); }}
    .pill.cold {{ background: rgba(61, 111, 147, 0.12); color: var(--cold); }}
    .meta {{
      color: var(--muted);
      font-size: 14px;
      margin-top: 8px;
      line-height: 1.5;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 8px;
      min-width: 1120px;
    }}
    th, td {{
      text-align: left;
      padding: 12px 10px;
      border-bottom: 1px solid #e5dccd;
      vertical-align: top;
      font-size: 14px;
    }}
    th {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      background: rgba(255, 253, 248, 0.98);
      position: sticky;
      top: 0;
      z-index: 1;
    }}
    .table-wrap {{
      overflow-x: auto;
      border: 1px solid #e5dccd;
      border-radius: 18px;
      background: rgba(255, 253, 248, 0.82);
    }}
    .muted {{
      color: var(--muted);
    }}
    .tag {{
      display: inline-block;
      margin: 0 6px 6px 0;
      padding: 4px 8px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: #0b5f54;
      font-size: 12px;
    }}
    .empty {{
      padding: 20px;
      border: 1px dashed var(--line);
      border-radius: 16px;
      color: var(--muted);
      background: rgba(255,255,255,0.4);
    }}
    .section-spacer {{
      margin-top: 22px;
    }}
    @media (max-width: 980px) {{
      .grid {{
        grid-template-columns: 1fr;
      }}
      .shell {{
        padding: 16px;
      }}
      h1 {{
        font-size: 32px;
      }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <div class="eyebrow">CTGT Lead Engine</div>
      <h1>Scrape Results and NLP-Clean Lead Signals</h1>
      <div class="sub">
        This dashboard reads the persisted database and shows source coverage, scored company leads, and cleaned NLP signals with direct job-posting links.
      </div>
      <div class="stats">
        <div class="stat"><div class="label">Signal Rows</div><div class="value">{total_signals}</div></div>
        <div class="stat"><div class="label">Companies Seen</div><div class="value">{total_companies}</div></div>
        <div class="stat"><div class="label">Lead Cards Shown</div><div class="value">{displayed_leads}</div></div>
        <div class="stat"><div class="label">Hot / Warm / Cold</div><div class="value compact">{lead_counts.get("hot", 0)} / {lead_counts.get("warm", 0)} / {lead_counts.get("cold", 0)}</div></div>
        <div class="stat"><div class="label">Active Filters</div><div class="value">{active_filter_count}</div></div>
      </div>
    </section>

    <div class="grid">
      <section class="panel">
        <h2>Source Summary</h2>
        <div class="source-grid">{source_cards}</div>
      </section>

      <section class="panel">
        <h2>Signal Filters</h2>
        <form method="get" class="filters">
          <div>
            <label for="source">Source</label>
            <select id="source" name="source">
              {_option("", "All sources", filters["source"])}
              {_option("linkedin", "LinkedIn", filters["source"])}
              {_option("indeed", "Indeed", filters["source"])}
              {_option("google", "Google", filters["source"])}
              {_option("stepstone", "Stepstone", filters["source"])}
              {_option("career_page", "Career page", filters["source"])}
              {_option("news", "News", filters["source"])}
            </select>
          </div>
          <div>
            <label for="lead_score">Lead band</label>
            <select id="lead_score" name="lead_score">
              {_option("", "All bands", filters["lead_score"])}
              {_option("hot", "HOT", filters["lead_score"])}
              {_option("warm", "WARM", filters["lead_score"])}
              {_option("cold", "COLD", filters["lead_score"])}
            </select>
          </div>
          <div>
            <label for="company">Company search</label>
            <input id="company" name="company" value="{_escape(filters["company"])}" placeholder="Search company name">
          </div>
          <div class="actions">
            <button class="button" type="submit">Apply filters</button>
            <a class="button secondary" href="/">Clear</a>
          </div>
        </form>
        <div class="meta section-note">
          Showing up to {signal_limit} cleaned signal rows. Use the job link in the table to open the original posting.
        </div>
      </section>
    </div>

    <div class="grid">
      <section class="panel">
        <h2>Top Company Leads</h2>
        <div class="lead-list">{lead_cards}</div>
      </section>

      <section class="panel">
        <h2>Quick Links</h2>
        <div class="lead-list">
          <div class="lead-card">
            <div class="card-title"><strong>All signals</strong></div>
            <div class="meta">Review every cleaned NLP signal row currently stored in PostgreSQL.</div>
            <div class="meta"><a href="/?{_query_string({'source': '', 'lead_score': '', 'company': ''})}">Reset all filters</a></div>
          </div>
          <div class="lead-card">
            <div class="card-title"><strong>Hot accounts</strong></div>
            <div class="meta">Focus on the most actionable companies first.</div>
            <div class="meta"><a href="/?{_query_string({'lead_score': 'hot'})}">Show hot signal rows</a></div>
          </div>
          <div class="lead-card">
            <div class="card-title"><strong>LinkedIn-only</strong></div>
            <div class="meta">Inspect cleaned results coming from LinkedIn job scraping.</div>
            <div class="meta"><a href="/?{_query_string({'source': 'linkedin'})}">Show LinkedIn rows</a></div>
          </div>
        </div>
      </section>
    </div>

    <section class="panel section-spacer">
      <h2>Clean NLP Signals</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Company</th>
              <th>Job Posting</th>
              <th>Source</th>
              <th>Lead</th>
              <th>Software</th>
              <th>Location / Industry</th>
              <th>Confidence</th>
              <th>Reason</th>
              <th>Signals</th>
              <th>Detected</th>
            </tr>
          </thead>
          <tbody>
            {signal_rows}
          </tbody>
        </table>
      </div>
    </section>
  </div>
</body>
</html>"""


def _render_source_card(stat: Any) -> str:
    return f"""
    <div class="source-card">
      <div class="eyebrow">{_escape(stat.source)}</div>
      <div class="metric-value">{stat.signal_count}</div>
      <div class="meta">
        Companies: {stat.company_count}<br>
        HOT / WARM / COLD: {stat.hot_count} / {stat.warm_count} / {stat.cold_count}
      </div>
    </div>
    """


def _render_lead_card(lead: Any) -> str:
    software = "".join(f'<span class="tag">{_escape(item)}</span>' for item in lead.software) or '<span class="muted">No software tags</span>'
    sources = ", ".join(lead.signal_sources) or "-"
    domain = _escape(lead.company_domain or "No domain")
    location = _escape(lead.location or "Unknown location")
    industry = _escape(lead.industry or "Unknown industry")
    return f"""
    <div class="lead-card">
      <div class="card-head">
        <div>
          <div class="card-title"><strong>{_escape(lead.company_name)}</strong></div>
          <div class="meta">{location} | {industry}</div>
        </div>
        <span class="pill {lead.lead_score}">{lead.lead_score}</span>
      </div>
      <div class="meta">Score: {lead.total_score} | Signals: {lead.signal_count} | Sources: {_escape(sources)}</div>
      <div class="meta">{domain}</div>
      <div class="token-list">{software}</div>
    </div>
    """


def _render_signal_row(signal: Any) -> str:
    software = "".join(f'<span class="tag">{_escape(item)}</span>' for item in signal.software) or '<span class="muted">-</span>'
    indicators: list[str] = []
    if signal.migration:
        detail = f"Migration from {_escape(signal.migration_from)}" if signal.migration_from else "Migration detected"
        indicators.append(f'<span class="tag">{detail}</span>')
    for item in signal.pain_signals:
        indicators.append(f'<span class="tag">Pain: {_escape(item)}</span>')
    for item in signal.expansion_signals:
        indicators.append(f'<span class="tag">Expansion: {_escape(item)}</span>')
    if not indicators:
        indicators.append('<span class="muted">No extra indicators</span>')

    title = _escape(signal.source_title or "Open posting")
    reason = _escape(signal.reason or "-")
    location_industry = f"{_escape(signal.location or '-')}<br><span class=\"muted\">{_escape(signal.industry or '-')}</span>"
    detected = signal.detected_at.strftime("%Y-%m-%d %H:%M UTC")
    return f"""
    <tr>
      <td>
        <strong>{_escape(signal.company_name)}</strong><br>
        <span class="muted">{_escape(signal.company_domain or '-')}</span>
      </td>
      <td><a href="{_escape(signal.source_url)}" target="_blank" rel="noreferrer">{title}</a></td>
      <td>{_escape(signal.signal_source)}</td>
      <td>
        <span class="pill {signal.lead_score}">{signal.lead_score}</span><br>
        <span class="muted">Score: {signal.company_total_score} | Rows: {signal.company_signal_count}</span>
      </td>
      <td>{software}</td>
      <td>{location_industry}</td>
      <td>{signal.confidence:.2f}<br><span class="muted">Raw: {signal.raw_score}</span></td>
      <td>{reason}</td>
      <td>{''.join(indicators)}</td>
      <td>{detected}</td>
    </tr>
    """


def _render_error_page(message: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Dashboard Error</title></head>
<body style="font-family: Georgia, serif; background:#f8f3ea; color:#1d2a33; padding:32px;">
  <h1>Dashboard query failed</h1>
  <p>{_escape(message)}</p>
</body>
</html>"""


def _empty_state(message: str) -> str:
    return f'<div class="empty">{_escape(message)}</div>'


def _empty_state_row(colspan: int, message: str) -> str:
    return f'<tr><td colspan="{colspan}"><div class="empty">{_escape(message)}</div></td></tr>'


def _option(value: str, label: str, current: str) -> str:
    selected = ' selected' if value == current else ''
    return f'<option value="{_escape(value)}"{selected}>{_escape(label)}</option>'


def _query_string(values: dict[str, str]) -> str:
    payload = {key: value for key, value in values.items() if value}
    return urlencode(payload)


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


if __name__ == "__main__":
    raise SystemExit(main())
