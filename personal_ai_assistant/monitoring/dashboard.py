from collections import defaultdict

import plotly.graph_objects as go
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from personal_ai_assistant.monitoring.request_monitor import read_records
from personal_ai_assistant.utils.config import settings

dashboard_router = APIRouter()

_CSS = """
body { font-family: Arial, sans-serif; background: #f4f6f8; margin: 0; padding: 16px; }
h1 { margin: 0 0 12px 0; }
.summary { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
.stat { background: #fff; border-radius: 8px; padding: 12px 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.stat .value { font-size: 26px; font-weight: bold; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 12px; }
.card { background: #fff; border-radius: 8px; padding: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
"""


def _style(fig, title: str, log_y: bool = False):
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=360,
        margin=dict(l=40, r=20, t=50, b=40),
    )
    if log_y:
        fig.update_yaxes(type="log")
    return fig


def _build_figures(records):
    counts = defaultdict(int)
    latencies = defaultdict(list)
    times = defaultdict(list)
    statuses = defaultdict(int)

    for r in records:
        counts[r["path"]] += 1
        latencies[r["path"]].append(r["latency_ms"])
        times[r["path"]].append(r["timestamp"])
        statuses[str(r["status_code"])] += 1

    paths = list(counts.keys())

    fig_count = _style(
        go.Figure(go.Bar(x=paths, y=[counts[p] for p in paths])),
        "Requests per endpoint",
    )

    averages = [sum(latencies[p]) / len(latencies[p]) for p in paths]
    fig_avg = _style(
        go.Figure(go.Bar(x=paths, y=averages)),
        "Average latency per endpoint (ms, log scale)",
        log_y=True,
    )

    fig_time = go.Figure()
    for p in paths:
        fig_time.add_trace(go.Scatter(x=times[p], y=latencies[p], mode="lines+markers", name=p))
    _style(fig_time, "Latency over time (ms, log scale)", log_y=True)

    fig_status = _style(
        go.Figure(go.Pie(labels=list(statuses.keys()), values=list(statuses.values()))),
        "HTTP status codes",
    )

    return [fig_count, fig_avg, fig_time, fig_status]


@dashboard_router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    records = read_records(settings.dashboard_max_points)

    total = len(records)
    errors = sum(1 for r in records if r["status_code"] >= 400)
    avg_latency = sum(r["latency_ms"] for r in records) / total if total else 0.0

    if total == 0:
        charts_html = "<p>No requests recorded yet. Call a few endpoints, then refresh this page.</p>"
    else:
        figures = _build_figures(records)
        charts_html = "".join(
            f'<div class="card">{fig.to_html(full_html=False, include_plotlyjs=(i == 0))}</div>'
            for i, fig in enumerate(figures)
        )

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="{settings.dashboard_refresh_seconds}">
    <title>{settings.app_name} - Dashboard</title>
    <style>{_CSS}</style>
</head>
<body>
    <h1>{settings.app_name} - Dashboard</h1>
    <div class="summary">
        <div class="stat"><div>Total requests</div><div class="value">{total}</div></div>
        <div class="stat"><div>Errors (4xx/5xx)</div><div class="value">{errors}</div></div>
        <div class="stat"><div>Avg latency (ms)</div><div class="value">{avg_latency:.1f}</div></div>
    </div>
    <div class="grid">{charts_html}</div>
</body>
</html>"""
    return HTMLResponse(html)