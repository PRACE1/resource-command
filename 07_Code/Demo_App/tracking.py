"""
Resource Command — Demo Tracking Module
========================================

Per-recipient demo access tracking. Bolt-on for demo_server.py.

How it works
------------
1. You generate a per-recipient URL when you share the demo:
       https://<host>/?k=ian-zeiti-2026-06-16
   That `k=` parameter is the recipient's unique key.

2. The frontend fires `POST /track/visit?k=...` on page load and
   `POST /track/action?k=...&type=...` whenever something meaningful
   happens (proof generated, validator panel opened, passport viewed,
   tab closed).

3. You read the activity from `GET /track/admin?token=<your_admin_key>`
   — returns an HTML dashboard showing per-recipient timelines.

Integration (one line in demo_server.py):

    from tracking import tracking_router, RecipientMiddleware
    app.include_router(tracking_router)
    app.add_middleware(RecipientMiddleware)

That's it.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import (
    Column, DateTime, Integer, String, Text, create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker
from starlette.middleware.base import BaseHTTPMiddleware

# ─── Recipient registry ───────────────────────────────────────────────────────
#
# Each entry maps a per-recipient `k=` key to a friendly name + context.
# Add a new key here whenever you share the demo with someone new.

RECIPIENTS: dict[str, dict[str, str]] = {
    # ZEITI / Ian Mwiinga
    "ian-zeiti-2026-06-16": {
        "name":         "Ian Mwiinga",
        "organisation": "ZEITI",
        "context":      "16 Jun 2026 methodology call",
        "shared_at":    "2026-06-08",
    },
    # Trail of Bits / Lindsay Rakowski
    "lindsay-tob-2026-06-09": {
        "name":         "Lindsay Rakowski",
        "organisation": "Trail of Bits",
        "context":      "9 Jun 2026 scoping call",
        "shared_at":    "2026-06-08",
    },
    # Barry Whitehat
    "barry-whitehat-2026": {
        "name":         "Barry Whitehat",
        "organisation": "Semaphore / Independent",
        "context":      "Independent ZK review",
        "shared_at":    "TBD",
    },
    # David Wamulume — Ministry of Energy
    "wamulume-ministry-2026": {
        "name":         "David Wamulume",
        "organisation": "Ministry of Energy, Zambia",
        "context":      "Pre-ministry introduction",
        "shared_at":    "TBD",
    },
    # KoBold Metals
    "kobold-2026": {
        "name":         "KoBold Metals",
        "organisation": "KoBold Metals",
        "context":      "Engineering session",
        "shared_at":    "TBD",
    },
    # Catch-all for unmarked traffic (mostly Kennedy testing)
    "_internal": {
        "name":         "Internal / unmarked",
        "organisation": "Kgosi Sovereign Holdings",
        "context":      "Internal / testing",
        "shared_at":    "n/a",
    },
}

# ─── Admin password ───────────────────────────────────────────────────────────
# Change this. Used to gate the /track/admin dashboard.
ADMIN_TOKEN = "kgosi-2026-changeme"

# ─── Database ─────────────────────────────────────────────────────────────────
TRACKING_DB = Path(__file__).parent / "tracking.db"
engine = create_engine(
    f"sqlite:///{TRACKING_DB}",
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DemoVisit(Base):
    __tablename__ = "demo_visits"
    id              = Column(Integer, primary_key=True, index=True)
    recipient_key   = Column(String, index=True)
    timestamp       = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    ip_address      = Column(String)
    user_agent      = Column(String)
    referer         = Column(String, nullable=True)
    page            = Column(String, nullable=True)
    notes           = Column(Text, nullable=True)


class DemoAction(Base):
    __tablename__ = "demo_actions"
    id              = Column(Integer, primary_key=True, index=True)
    recipient_key   = Column(String, index=True)
    timestamp       = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    action_type     = Column(String, index=True)   # e.g. "proof_generated", "consensus_started"
    payload         = Column(Text, nullable=True)  # any JSON-encoded extra detail
    ip_address      = Column(String)


class ApiHit(Base):
    """Every backend API hit, lightweight — for forensic timeline reconstruction."""
    __tablename__ = "api_hits"
    id              = Column(Integer, primary_key=True, index=True)
    recipient_key   = Column(String, index=True)
    timestamp       = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    method          = Column(String)
    path            = Column(String, index=True)
    status_code     = Column(Integer)
    duration_ms     = Column(Integer)
    ip_address      = Column(String)


Base.metadata.create_all(bind=engine)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def _resolve_recipient(key: str | None) -> str:
    """Validate and resolve a recipient key. Falls back to _internal."""
    if not key:
        return "_internal"
    return key if key in RECIPIENTS else "_internal"


def _client_ip(request: Request) -> str:
    # Respect common reverse-proxy headers if set by Cloudflare, nginx, etc.
    for hdr in ("cf-connecting-ip", "x-real-ip", "x-forwarded-for"):
        v = request.headers.get(hdr)
        if v:
            return v.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ─── Middleware: log every API hit ────────────────────────────────────────────
class RecipientMiddleware(BaseHTTPMiddleware):
    """Logs every request's path + status, attributed to a recipient if known."""

    async def dispatch(self, request: Request, call_next):
        started = datetime.now(timezone.utc)
        # Recipient key may be in query string or in a cookie
        rk = request.query_params.get("k") or request.cookies.get("rc_recipient")
        rk = _resolve_recipient(rk)

        response = await call_next(request)

        # Skip our own admin and tracking endpoints to avoid recursion noise
        path = request.url.path
        if path.startswith(("/track/admin", "/track/visit", "/track/action", "/api/health")):
            return response

        try:
            ended = datetime.now(timezone.utc)
            with SessionLocal() as db:
                db.add(ApiHit(
                    recipient_key = rk,
                    method        = request.method,
                    path          = path,
                    status_code   = response.status_code,
                    duration_ms   = int((ended - started).total_seconds() * 1000),
                    ip_address    = _client_ip(request),
                ))
                db.commit()
        except Exception:
            # Tracking must never break the demo
            pass

        return response


# ─── Routes ───────────────────────────────────────────────────────────────────
tracking_router = APIRouter(prefix="/track", tags=["tracking"])


@tracking_router.post("/visit")
async def track_visit(request: Request):
    """
    Record that a recipient opened the demo. The frontend calls this on page load.
    Falls back to the cookie if `k=` isn't in the query string.
    """
    rk = _resolve_recipient(request.query_params.get("k"))
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass

    with SessionLocal() as db:
        visit = DemoVisit(
            recipient_key = rk,
            ip_address    = _client_ip(request),
            user_agent    = request.headers.get("user-agent", "")[:512],
            referer       = request.headers.get("referer", "")[:512],
            page          = body.get("page", "")[:512],
            notes         = (json.dumps(body)[:2048]) if body else None,
        )
        db.add(visit)
        db.commit()
        visit_id = visit.id

    resp = JSONResponse({
        "ok":        True,
        "visit_id":  visit_id,
        "recipient": rk,
        "name":      RECIPIENTS.get(rk, {}).get("name", "Unknown"),
    })
    # Set the cookie so subsequent hits attribute correctly even without ?k= in the URL
    resp.set_cookie(
        key      = "rc_recipient",
        value    = rk,
        max_age  = 60 * 60 * 24 * 30,   # 30 days
        httponly = False,                # readable by JS so frontend can verify
        samesite = "lax",
    )
    return resp


@tracking_router.post("/action")
async def track_action(request: Request):
    """
    Record an action taken inside the demo. The frontend calls this when
    something meaningful happens — proof generated, consensus reached, etc.

    Body: {"type": "proof_generated", "payload": {...}}
    """
    rk = _resolve_recipient(
        request.query_params.get("k") or request.cookies.get("rc_recipient")
    )
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    action_type = (body.get("type") or "unknown")[:128]
    payload     = body.get("payload")
    payload_str = json.dumps(payload)[:4096] if payload is not None else None

    with SessionLocal() as db:
        db.add(DemoAction(
            recipient_key = rk,
            action_type   = action_type,
            payload       = payload_str,
            ip_address    = _client_ip(request),
        ))
        db.commit()

    return {"ok": True, "recipient": rk, "type": action_type}


@tracking_router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(token: str | None = None):
    """
    Read-only HTML dashboard of all recipient activity.

    Visit:  http://localhost:8000/track/admin?token=<ADMIN_TOKEN>
    """
    if token != ADMIN_TOKEN:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = "Provide ?token=<admin_token>",
        )

    with SessionLocal() as db:
        visits  = db.query(DemoVisit).order_by(DemoVisit.timestamp.desc()).limit(500).all()
        actions = db.query(DemoAction).order_by(DemoAction.timestamp.desc()).limit(500).all()
        hits    = db.query(ApiHit).order_by(ApiHit.timestamp.desc()).limit(500).all()

    # Build per-recipient summary
    summary: dict[str, dict[str, Any]] = {}
    for v in visits:
        s = summary.setdefault(v.recipient_key, {"visits": 0, "actions": 0, "hits": 0, "last_seen": None})
        s["visits"]  += 1
        s["last_seen"] = max(s["last_seen"] or v.timestamp, v.timestamp)
    for a in actions:
        s = summary.setdefault(a.recipient_key, {"visits": 0, "actions": 0, "hits": 0, "last_seen": None})
        s["actions"] += 1
        s["last_seen"] = max(s["last_seen"] or a.timestamp, a.timestamp)
    for h in hits:
        s = summary.setdefault(h.recipient_key, {"visits": 0, "actions": 0, "hits": 0, "last_seen": None})
        s["hits"]    += 1
        s["last_seen"] = max(s["last_seen"] or h.timestamp, h.timestamp)

    def _row(label: str, value: Any) -> str:
        return f'<tr><td style="padding:4px 12px;color:#666">{label}</td><td style="padding:4px 12px">{value}</td></tr>'

    summary_html = ""
    for rk, s in sorted(summary.items(), key=lambda kv: (kv[1]["last_seen"] or datetime.min), reverse=True):
        info = RECIPIENTS.get(rk, {})
        last = s["last_seen"].strftime("%Y-%m-%d %H:%M UTC") if s["last_seen"] else "—"
        summary_html += f"""
        <div style="border:1px solid #d9c898;border-radius:6px;padding:14px;margin:12px 0;background:#f5f1e8">
          <h3 style="margin:0 0 6px 0;color:#0D1B2A">{info.get('name', rk)}
            <span style="font-size:12px;font-weight:normal;color:#999">{rk}</span>
          </h3>
          <div style="color:#555;font-size:13px;margin-bottom:8px">{info.get('organisation', '')} · {info.get('context', '')}</div>
          <table style="font-size:13px">
            <tr><td style="padding:2px 12px 2px 0;color:#666">Visits</td><td><b>{s['visits']}</b></td>
                <td style="padding:2px 12px 2px 24px;color:#666">Actions</td><td><b>{s['actions']}</b></td>
                <td style="padding:2px 12px 2px 24px;color:#666">API hits</td><td><b>{s['hits']}</b></td>
                <td style="padding:2px 12px 2px 24px;color:#666">Last seen</td><td><b>{last}</b></td></tr>
          </table>
        </div>"""

    # Recent activity timeline (mixed visits + actions, newest first)
    timeline_rows = []
    for v in visits[:40]:
        timeline_rows.append((v.timestamp, "VISIT", v.recipient_key, f"{v.ip_address} · {v.user_agent[:80]}"))
    for a in actions[:40]:
        timeline_rows.append((a.timestamp, a.action_type.upper(), a.recipient_key, (a.payload or "")[:120]))
    timeline_rows.sort(key=lambda r: r[0], reverse=True)

    timeline_html = ""
    for ts, kind, rk, detail in timeline_rows[:60]:
        name = RECIPIENTS.get(rk, {}).get("name", rk)
        timeline_html += f"""
        <tr>
          <td style="padding:4px 10px;font-family:monospace;font-size:12px;color:#999">{ts.strftime('%Y-%m-%d %H:%M:%S')}</td>
          <td style="padding:4px 10px;color:#C9952A;font-weight:bold">{kind}</td>
          <td style="padding:4px 10px;font-weight:bold;color:#0D1B2A">{name}</td>
          <td style="padding:4px 10px;color:#555;font-size:12px">{detail}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html><head><title>RC Demo Tracking</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", Roboto, sans-serif; background: #fff; color: #0D1B2A; max-width: 1200px; margin: 24px auto; padding: 24px; }}
  h1 {{ color: #0D1B2A; border-bottom: 2px solid #C9952A; padding-bottom: 8px; }}
  h2 {{ color: #0D1B2A; margin-top: 32px; }}
  .recipient-list {{ }}
  table {{ width: 100%; border-collapse: collapse; }}
  thead td {{ background: #0D1B2A; color: #fff; padding: 8px 10px; font-size: 13px; }}
  tbody tr:nth-child(odd) {{ background: #f9f7f0; }}
</style></head><body>
<h1>Resource Command — Demo Tracking</h1>
<p style="color:#666">Per-recipient visit + action log. Last 500 of each type.</p>

<h2>Recipients</h2>
<div class="recipient-list">{summary_html or "<p style='color:#999'>No activity yet.</p>"}</div>

<h2>Recent timeline</h2>
<table>
  <thead>
    <tr><td style="width:170px">Time (UTC)</td><td style="width:140px">Type</td><td style="width:220px">Recipient</td><td>Detail</td></tr>
  </thead>
  <tbody>{timeline_html or "<tr><td colspan='4' style='padding:14px;color:#999'>No activity yet.</td></tr>"}</tbody>
</table>

<p style="color:#999;margin-top:32px;font-size:12px">
  Add a new recipient: edit <code>RECIPIENTS</code> in <code>tracking.py</code> and restart the server.<br>
  Per-recipient URL pattern: <code>/?k=&lt;recipient_key&gt;</code>
</p>
</body></html>"""


@tracking_router.get("/snippet")
async def js_snippet():
    """
    Returns the JS snippet to drop into the frontend. Auto-pings /track/visit
    on page load and exposes window.rcTrack(actionType, payload) to fire actions.
    """
    return JSONResponse({"snippet": _FRONTEND_SNIPPET.strip()})


_FRONTEND_SNIPPET = """
<!-- Resource Command tracking — drop into <head> of index.html -->
<script>
(function () {
  var params = new URLSearchParams(window.location.search);
  var k = params.get('k');
  var base = ''; // same origin

  // Ping visit on load
  fetch(base + '/track/visit' + (k ? '?k=' + encodeURIComponent(k) : ''), {
    method: 'POST',
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ page: window.location.pathname }),
  }).catch(function () {});

  // Expose action-tracking function
  window.rcTrack = function (actionType, payload) {
    fetch(base + '/track/action', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: actionType, payload: payload || null }),
    }).catch(function () {});
  };

  // Track tab close
  window.addEventListener('beforeunload', function () {
    try {
      navigator.sendBeacon(
        base + '/track/action',
        new Blob([JSON.stringify({ type: 'tab_closed', payload: {} })],
                 { type: 'application/json' })
      );
    } catch (e) {}
  });
})();
</script>
"""
