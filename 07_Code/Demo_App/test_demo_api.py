"""
Resource Command — Full API Cross-Check Test Suite
Verifies every endpoint is alive, authenticated, and returning correct data.
"""

import json
import urllib.request
import urllib.parse
import urllib.error

BASE = "http://localhost:8002"
TOKEN = None
PROOF_HASH = None
EVENT_ID = None
PASS_COUNT = 0
FAIL_COUNT = 0

def ok(label, detail=""):
    global PASS_COUNT
    PASS_COUNT += 1
    print(f"  ✅ PASS  {label}" + (f" — {detail}" if detail else ""))

def fail(label, detail=""):
    global FAIL_COUNT
    FAIL_COUNT += 1
    print(f"  ❌ FAIL  {label}" + (f" — {detail}" if detail else ""))

def get(path, token=None, expect_keys=None):
    req = urllib.request.Request(f"{BASE}{path}")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        res = urllib.request.urlopen(req, timeout=8)
        data = json.loads(res.read().decode())
        if expect_keys:
            missing = [k for k in expect_keys if k not in data]
            if missing:
                fail(path, f"Missing keys: {missing}")
                return None
        return data
    except urllib.error.HTTPError as e:
        fail(path, f"HTTP {e.code}: {e.read().decode()[:120]}")
        return None
    except Exception as e:
        fail(path, str(e)[:120])
        return None

def post_form(path, fields):
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=data)
    try:
        res = urllib.request.urlopen(req, timeout=8)
        return json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        fail(path, f"HTTP {e.code}: {e.read().decode()[:120]}")
        return None
    except Exception as e:
        fail(path, str(e)[:120])
        return None

def get_sse_first_event(path, token=None):
    """Reads the first SSE data line and returns parsed JSON."""
    req = urllib.request.Request(f"{BASE}{path}")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        res = urllib.request.urlopen(req, timeout=10)
        for raw_line in res:
            line = raw_line.decode("utf-8").strip()
            if line.startswith("data:"):
                return json.loads(line[5:].strip())
        return None
    except Exception as e:
        fail(path, str(e)[:120])
        return None

# ==============================================================================
print("\n" + "="*60)
print(" RESOURCE COMMAND — ENDPOINT CROSS-CHECK")
print("="*60)

# 1. Health check (no auth needed)
print("\n[1] Health Check")
data = get("/api/health")
if data and data.get("status") == "operational":
    ok("/api/health", f"protocol={data.get('protocol')}")
else:
    fail("/api/health", str(data))

# 2. Auth — wrong password (expect 401)
print("\n[2] Auth — Reject Wrong Password")
try:
    post_form("/api/auth/token", {"username": "kennedy", "password": "wrongpassword"})
    fail("/api/auth/token wrong-pass", "Should have returned 401")
except:
    data = None  # already handled in post_form
    ok("/api/auth/token wrong-pass", "Correctly rejects invalid credentials")

# 3. Auth — correct login
print("\n[3] Auth — Valid Login (kennedy / sovereign2026)")
res = post_form("/api/auth/token", {"username": "kennedy", "password": "sovereign2026"})
if res and "access_token" in res:
    TOKEN = res["access_token"]
    ok("/api/auth/token", f"role={res.get('role')} | token length={len(TOKEN)}")
else:
    fail("/api/auth/token", "No token returned")

# 4. Auth — /me endpoint
print("\n[4] Auth — /me with valid token")
if TOKEN:
    data = get("/api/auth/me", token=TOKEN, expect_keys=["username", "role"])
    if data:
        ok("/api/auth/me", f"username={data['username']} role={data['role']}")
    else:
        fail("/api/auth/me")

# 5. Satellite Ping SSE (first event)
print("\n[5] Satellite Ping — SSE first event")
if TOKEN:
    event = get_sse_first_event("/api/demo/satellite-ping", token=TOKEN)
    if event and "event_id" in event and "phase_shift_rad" in event:
        EVENT_ID = event["event_id"]
        ok("/api/demo/satellite-ping", f"event_id={EVENT_ID} | zone={event.get('estimated_zone_m2')}m2 | coherence={event.get('coherence_pct')}%")
    else:
        fail("/api/demo/satellite-ping", str(event)[:120])

# 6. Pupil Scan SSE (first event)
print("\n[6] AR Visor Pupil Scan — SSE first event")
eid = EVENT_ID or "TEST01"
if TOKEN:
    event = get_sse_first_event(f"/api/demo/pupil-scan?event_id={eid}", token=TOKEN)
    if event and "raw_pupil_mm" in event and "presence_ratio_float" in event:
        ok("/api/demo/pupil-scan", f"raw={event['raw_pupil_mm']}mm | ratio={event['presence_ratio_float']} | status={event['status']}")
    else:
        fail("/api/demo/pupil-scan", str(event)[:120])

# 7. ZK Prover SSE (first event — should be a log line)
print("\n[7] ZK Prover — SSE first log event")
eid = EVENT_ID or "TEST01"
if TOKEN:
    event = get_sse_first_event(f"/api/demo/prove?event_id={eid}&presence_ratio=1050000", token=TOKEN)
    if event and event.get("type") == "log":
        ok("/api/demo/prove", f"type=log | message={event['message'][:60]}")
    else:
        fail("/api/demo/prove", str(event)[:120])

# 8. Consensus SSE (first event — should be PRE_PREPARE)
print("\n[8] PBFT Consensus — SSE first event (PRE_PREPARE phase)")
fake_hash = "0x" + "a" * 62
if TOKEN:
    event = get_sse_first_event(f"/api/demo/consensus?event_id={eid}&proof_hash={fake_hash}", token=TOKEN)
    if event and event.get("phase") == "PRE_PREPARE":
        ok("/api/demo/consensus", f"phase={event['phase']} | seq_n={event.get('seq_n')} | from={event.get('from')}")
    else:
        fail("/api/demo/consensus", str(event)[:120])

# 9. EU Battery Passport
print("\n[9] EU Battery Passport — Annex XIII schema")
if TOKEN:
    data = get(f"/api/demo/passport/{fake_hash}", token=TOKEN, expect_keys=["passport", "qr_code_png_b64"])
    if data:
        p = data["passport"]
        has_qr = len(data.get("qr_code_png_b64", "")) > 100
        has_schema = p.get("schema") == "DIN_DKE_SPEC_99100_2025"
        has_royalty = "royalty_compliance" in p
        if has_qr and has_schema and has_royalty:
            ok("/api/demo/passport", f"schema={p['schema']} | royalty_status={p['royalty_compliance']['status']} | QR=✓")
        else:
            fail("/api/demo/passport", f"qr={has_qr} schema={has_schema} royalty={has_royalty}")

# 10. Event History (SQLite persistence)
print("\n[10] Event History — SQLite persistence")
if TOKEN:
    data = get("/api/demo/events", token=TOKEN)
    if isinstance(data, list):
        ok("/api/demo/events", f"{len(data)} event(s) persisted in SQLite")
    else:
        fail("/api/demo/events", str(data)[:80])

# 11. Unauthorized access test
print("\n[11] Security — Reject request without token")
try:
    urllib.request.urlopen(f"{BASE}/api/demo/events", timeout=5)
    fail("/api/demo/events no-auth", "Should have returned 401")
except urllib.error.HTTPError as e:
    if e.code == 401:
        ok("/api/demo/events no-auth", "Correctly returns 401 for unauthenticated request")
    else:
        fail("/api/demo/events no-auth", f"Got HTTP {e.code} instead of 401")
except Exception as e:
    fail("/api/demo/events no-auth", str(e)[:80])

# ==============================================================================
print("\n" + "="*60)
print(f" RESULTS: {PASS_COUNT} PASSED  |  {FAIL_COUNT} FAILED")
print("="*60)
if FAIL_COUNT == 0:
    print(" ALL ENDPOINTS OPERATIONAL — DEMO SERVER IS PRODUCTION READY")
else:
    print(f" {FAIL_COUNT} ENDPOINT(S) NEED ATTENTION")
print("="*60 + "\n")
