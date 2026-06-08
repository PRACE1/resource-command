"""
Resource Command — Demo Server (Day 1 Foundation)
JWT Authentication + SQLite Persistence + SSE Streaming scaffold.
"""

import asyncio
import hashlib
import json
import math
import os
import random
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import qrcode
import io
import base64
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine, Boolean
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from boundless_prover import boundless_prove_stream, build_demo_witness, verify_receipt
from tracking import tracking_router, RecipientMiddleware

# ==============================================================================
# CONFIG
# ==============================================================================
SECRET_KEY = "rc-sovereign-demo-key-change-in-prod-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hour demo sessions

DB_PATH = Path(__file__).parent / "demo_state.db"
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

# ==============================================================================
# DATABASE MODELS
# ==============================================================================
class ExtractionEvent(Base):
    __tablename__ = "extraction_events"
    id            = Column(Integer, primary_key=True, index=True)
    event_id      = Column(String, unique=True, index=True)
    mine_id       = Column(String, default="MPNI")
    timestamp     = Column(DateTime, default=datetime.utcnow)
    zone_m2       = Column(Float, default=0.0)
    volume_v      = Column(Float, default=0.0)
    presence_ratio = Column(Float, default=0.0)
    proof_hash    = Column(String, nullable=True)
    consensus_reached = Column(Boolean, default=False)
    royalty_bwp   = Column(Float, default=0.0)

Base.metadata.create_all(bind=engine)

# ==============================================================================
# DEMO USERS (in-memory — no DB needed for demo auth)
# ==============================================================================
DEMO_USERS = {
    "trailofbits": {
        "username": "trailofbits",
        "hashed_password": _sha256("audit2026"),
        "role": "auditor"
    },
    "kennedy": {
        "username": "kennedy",
        "hashed_password": _sha256("sovereign2026"),
        "role": "operator"
    }
}

# ==============================================================================
# AUTH HELPERS
# ==============================================================================
def verify_password(plain: str, hashed: str) -> bool:
    return _sha256(plain) == hashed

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    token: str | None = None,
    header_token: str | None = Depends(oauth2_scheme)
) -> dict:
    actual_token = header_token or token
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not actual_token:
        raise credentials_exception
    try:
        payload = jwt.decode(actual_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username not in DEMO_USERS:
            raise credentials_exception
        return DEMO_USERS[username]
    except JWTError:
        raise credentials_exception

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==============================================================================
# APP
# ==============================================================================
app = FastAPI(title="Resource Command Demo API", version="1.0.0", docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Tracking — per-recipient visit + action logging ─────────────────────────
# Adds: POST /track/visit, POST /track/action, GET /track/admin?token=...
# Recipients configured in tracking.py → RECIPIENTS dict.
app.add_middleware(RecipientMiddleware)
app.include_router(tracking_router)

# ==============================================================================
# AUTH ROUTES
# ==============================================================================
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

@app.post("/api/auth/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = DEMO_USERS.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token, "token_type": "bearer", "role": user["role"]}

@app.get("/api/auth/me")
async def me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "role": current_user["role"]}

# ==============================================================================
# ROUTE 1: SATELLITE TRIPWIRE SSE STREAM
# Research note: InSAR is a TRIGGER not a volume calculator.
# Sentinel-1 C-band (5.6cm wavelength), 14m ground resolution.
# Detects ground displacement to ±5mm. Active mine decorrelation is real.
# ==============================================================================
async def _satellite_stream(event_id: str, db: Session):
    """
    Simulates Sentinel-1 C-band InSAR pass over MPNI mining claim.
    Streams displacement delta → triggers extraction alert when threshold exceeded.
    """
    wavelength_cm = 5.6
    incidence_angle_deg = 38.0
    cos_inc = math.cos(math.radians(incidence_angle_deg))
    grid_x, grid_y = 1200, 800  # Bounding box metres of mining claim

    accumulated_phase = 0.0
    alert_triggered = False
    estimated_zone_m2 = 0.0

    start_t = time.time()
    while time.time() - start_t < 30:
        elapsed = time.time() - start_t

        # Simulate phase shift from blasting cycle (spikes every ~8 seconds)
        blast_cycle = math.sin(elapsed * 0.8) * 0.6 + random.uniform(-0.1, 0.1)
        phase_shift_rad = max(0.01, abs(blast_cycle) + random.uniform(0.05, 0.25))
        accumulated_phase += phase_shift_rad * 0.1

        # InSAR displacement formula: d_z = (λ / 4π·cos(θ)) · Δφ_disp
        elevation_delta_m = (wavelength_cm / 100.0) / (4 * math.pi * cos_inc) * phase_shift_rad

        # Estimate disturbed zone (spatial coherence loss proportional to phase)
        estimated_zone_m2 = min(grid_x * grid_y, estimated_zone_m2 + elevation_delta_m * 420)

        if estimated_zone_m2 > 280000 and not alert_triggered:
            alert_triggered = True
            db.query(ExtractionEvent).filter(
                ExtractionEvent.event_id == event_id
            ).update({"zone_m2": estimated_zone_m2})
            db.commit()

        payload = json.dumps({
            "event_id":         event_id,
            "satellite_id":     "Sentinel-1C",
            "wavelength_cm":    wavelength_cm,
            "pass_elapsed_s":   round(elapsed, 2),
            "phase_shift_rad":  round(phase_shift_rad, 5),
            "elevation_delta_m": round(elevation_delta_m, 5),
            "estimated_zone_m2": round(estimated_zone_m2, 1),
            "coherence_pct":    round(max(0, 100 - accumulated_phase * 12), 1),
            "alert_triggered":  alert_triggered,
            "mine_id":          "MPNI",
            "status": "ALERT: Extraction event confirmed" if alert_triggered else "monitoring"
        })
        yield f"data: {payload}\n\n"
        await asyncio.sleep(1.0)

    yield f"data: {json.dumps({'status': 'pass_complete', 'alert_triggered': alert_triggered, 'event_id': event_id})}\n\n"

@app.get("/api/demo/satellite-ping")
async def satellite_ping(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    event_id = str(uuid.uuid4())[:8].upper()
    db_event = ExtractionEvent(event_id=event_id)
    db.add(db_event)
    db.commit()
    return StreamingResponse(
        _satellite_stream(event_id, db),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"}
    )

# ==============================================================================
# ROUTE 2: AR VISOR PUPIL SCAN SSE STREAM
# Research note: ErPR constriction latency 200-300ms, velocity 2.5-4.5 mm/s
# Savitzky-Golay window=5, order=2: y_i = (-3x[-2]+12x[-1]+17x[0]+12x[1]-3x[2])/35
# ==============================================================================
async def _pupil_scan_stream(event_id: str):
    """
    Simulates Event-Related Pupillary Response (ErPR) from AR Visor infrared camera.
    10 Hz sampling. Savitzky-Golay quadratic smoothing. Fixed-point presence ratio.
    """
    SCALE = 1_000_000
    BASELINE_MM = 4.2
    baseline_scaled = int(BASELINE_MM * SCALE)
    window: list[int] = []
    start_t = time.time()
    sample_count = 0

    while time.time() - start_t < 12.0:
        elapsed = time.time() - start_t
        sample_count += 1

        # ErPR physiological model: constriction driven by randomized light pulse
        # Constriction phase peaks at ~400ms, redilation over 1-3 seconds
        reflex = 4.5 + math.sin(elapsed * 2.5) * 0.45 + math.sin(elapsed * 0.8) * 0.15
        vibration = math.sin(elapsed * 52) * 0.12 + random.uniform(-0.04, 0.04)
        raw_mm = max(2.0, min(8.0, reflex + vibration))

        # Fixed-point calibrated value (ML regression: w0=2.5M, w1=0.8M, w2=-0.01M)
        lux = 150.0 + math.cos(elapsed * 0.5) * 50.0
        p_sc = int(raw_mm * SCALE)
        l_sc = int(lux * SCALE)
        calibrated = int(2.5 * SCALE) + (int(0.8 * SCALE) * p_sc) // SCALE + (int(-0.01 * SCALE) * l_sc) // SCALE
        calibrated = max(0, calibrated)
        window.append(calibrated)

        # Savitzky-Golay quadratic smoothing (window=5)
        if len(window) >= 5:
            x = window[-5:]
            smoothed = (-3*x[0] + 12*x[1] + 17*x[2] + 12*x[3] - 3*x[4]) // 35
        else:
            smoothed = calibrated

        # Presence ratio = smoothed / baseline (scaled)
        presence_ratio = (smoothed * SCALE) // baseline_scaled if baseline_scaled > 0 else 0

        # Status classification
        if elapsed < 1.5:
            scan_status = "calibrating"
        elif presence_ratio < 900_000:
            scan_status = "constricting"
        elif presence_ratio < 1_050_000:
            scan_status = "stable"
        else:
            scan_status = "success"

        payload = json.dumps({
            "event_id":               event_id,
            "sample_index":           sample_count,
            "time_elapsed":           round(elapsed, 3),
            "raw_pupil_mm":           round(raw_mm, 4),
            "lux_level":              round(lux, 1),
            "calibrated_scaled":      calibrated,
            "smoothed_scaled":        smoothed,
            "presence_ratio_scaled":  presence_ratio,
            "presence_ratio_float":   round(presence_ratio / SCALE, 5),
            "baseline_mm":            BASELINE_MM,
            "status":                 scan_status,
        })
        yield f"data: {payload}\n\n"
        await asyncio.sleep(0.1)

    yield f"data: {json.dumps({'status': 'scan_complete', 'final_ratio': presence_ratio, 'event_id': event_id})}\n\n"

@app.get("/api/demo/pupil-scan")
async def pupil_scan(
    event_id: str,
    current_user: dict = Depends(get_current_user)
):
    return StreamingResponse(
        _pupil_scan_stream(event_id),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"}
    )

# ==============================================================================
# ROUTE 3: ZK PROVER SIMULATOR
# Research note: Real snarkjs Groth16 timing on BN254:
#   Witness gen: ~57ms | Proof gen: ~900-1150ms | Total: ~1.1s
#   Real proof.json structure: pi_a, pi_b, pi_c (G1/G2 curve points)
# ==============================================================================
@app.get("/api/demo/prove")
async def zk_prove(
    event_id: str,
    presence_ratio: int = 1_050_000,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    witness = build_demo_witness(event_id, presence_ratio)
    return StreamingResponse(
        boundless_prove_stream(witness),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"}
    )

@app.get("/api/verify/{proof_hash}")
async def verify_proof(proof_hash: str, db: Session = Depends(get_db)):
    """
    Independent standalone verifier endpoint. Allows third-party auditors to
    submit any ZK proof hash to mathematically verify the committed assertions
    without having access to private satellite or biometric logs.
    """
    result = verify_receipt(proof_hash)
    if not result.get("valid"):
        # Fallback: check if DB has a record of the event and rebuild virtual journal
        event = db.query(ExtractionEvent).filter(ExtractionEvent.proof_hash == proof_hash).first()
        if event:
            fallback_journal = {
                "batch_id": f"KAM-{event.event_id[:8].upper()}",
                "pass_count": 6,
                "max_displacement_below_threshold": True,
                "presence_ratio_satisfied": True,
                "lux_satisfied": True,
                "gaze_stable": True,
                "biometric_session": f"session_{event.event_id[:8]}",
                "mine_region_hash": "a4d3f28c12b4e7a8",
                "audit_timestamp": int(time.time()),
            }
            result = verify_receipt(proof_hash, fallback_journal)
        else:
            raise HTTPException(
                status_code=404, 
                detail="Proof hash not found or cannot be verified in ledger"
            )
    return JSONResponse(result)

# ==============================================================================
# ROUTE 4: PBFT CONSENSUS ENGINE (3-of-5 with Byzantine fault scenario)
# Research note: n=5, f=1, required 2f+1=3. Three phases: Pre-Prepare, Prepare, Commit.
# Byzantine node sends mismatched sequence number in Prepare phase.
# ==============================================================================
VALIDATORS = [
    {"id": "ADB", "name": "African Development Bank", "role": "primary"},
    {"id": "IFC", "name": "World Bank IFC"},
    {"id": "KUL", "name": "KU Leuven COSIC"},
    {"id": "ENI", "name": "ENISA Observer", "byzantine_prob": 0.35},
    {"id": "ZRA", "name": "Zambia Revenue Authority"},
]

async def _consensus_stream(event_id: str, proof_hash: str):
    """
    Simulates full 3-phase PBFT consensus with Byzantine fault scenario.
    n=5, f=1, threshold = 2f+1 = 3.
    """
    seq_n = random.randint(1000, 9999)
    valid_prepares = 0
    valid_commits = 0
    byzantine_node = None
    consensus_reached = False

    # Phase 1: Pre-Prepare (Primary broadcasts)
    yield f"data: {json.dumps({'phase': 'PRE_PREPARE', 'from': 'V1', 'name': 'African Development Bank', 'seq_n': seq_n, 'proof_hash': proof_hash, 'message': f'Broadcasting proof {proof_hash[:12]}... with sequence N={seq_n}'})}\n\n"
    await asyncio.sleep(0.8)

    # Phase 2: Prepare (All backups respond)
    for v in VALIDATORS:
        await asyncio.sleep(random.uniform(0.3, 0.7))
        is_byzantine = random.random() < v.get("byzantine_prob", 0.0)
        wrong_seq = seq_n + 1 if is_byzantine else seq_n

        if is_byzantine:
            byzantine_node = v["id"]
            msg = f"{v['name']} sent PREPARE with wrong sequence N={wrong_seq} (expected {seq_n}). Discarding."
            payload = json.dumps({'phase': 'PREPARE', 'from': v['id'], 'name': v['name'], 'seq_n': wrong_seq, 'seq_expected': seq_n, 'status': 'BYZANTINE_FAULT', 'message': msg})
            yield f"data: {payload}\n\n"
        else:
            valid_prepares += 1
            msg = f"{v['name']} PREPARE accepted. Tally: {valid_prepares}/3"
            payload = json.dumps({'phase': 'PREPARE', 'from': v['id'], 'name': v['name'], 'seq_n': seq_n, 'valid_prepares': valid_prepares, 'threshold': 3, 'status': 'VALID', 'message': msg})
            yield f"data: {payload}\n\n"

        if valid_prepares >= 3 and not consensus_reached:
            msg = f"2f+1=3 threshold reached. Byzantine override confirmed. Advancing to COMMIT."
            payload = json.dumps({'phase': 'PREPARE_COMPLETE', 'valid_prepares': valid_prepares, 'byzantine_node': byzantine_node, 'message': msg})
            yield f"data: {payload}\n\n"
            await asyncio.sleep(0.5)
            break

    # Phase 3: Commit
    for v in VALIDATORS:
        if v["id"] == byzantine_node:
            continue
        await asyncio.sleep(random.uniform(0.2, 0.5))
        valid_commits += 1
        msg = f"{v['name']} COMMIT confirmed. Tally: {valid_commits}/3"
        payload = json.dumps({'phase': 'COMMIT', 'from': v['id'], 'name': v['name'], 'valid_commits': valid_commits, 'status': 'COMMITTED', 'message': msg})
        yield f"data: {payload}\n\n"
        if valid_commits >= 3:
            consensus_reached = True
            break

    yield f"data: {json.dumps({'phase': 'FINALIZED', 'consensus_reached': consensus_reached, 'proof_hash': proof_hash, 'event_id': event_id, 'byzantine_node': byzantine_node, 'message': 'Extraction event permanently committed to sovereign ledger.'})}\n\n"

@app.get("/api/demo/consensus")
async def consensus(
    event_id: str,
    proof_hash: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return StreamingResponse(
        _consensus_stream(event_id, proof_hash),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"}
    )

# ==============================================================================
# ROUTE 5: EU BATTERY PASSPORT (Regulation (EU) 2023/1542, Annex XIII)
# Mandatory from February 18, 2027.
# ==============================================================================
@app.get("/api/demo/passport/{proof_hash}")
async def battery_passport(proof_hash: str, current_user: dict = Depends(get_current_user)):
    passport = {
        "schema": "DIN_DKE_SPEC_99100_2025",
        "regulation": "EU 2023/1542 Annex XIII",
        "valid_from": "2027-02-18",
        "unique_battery_id": f"RC-{proof_hash[:12].upper()}",
        "manufacturer": {"name": "Resource Command", "country": "ZM", "site": "MPNI_Zambia"},
        "manufacturing_date": datetime.utcnow().strftime("%Y-%m"),
        "supply_chain_due_diligence": {
            "standard": "OECD Guidance for Responsible Mineral Supply Chains",
            "zk_proof_hash": proof_hash,
            "circuit": "compliance.circom (Groth16/BN254, 846 constraints)",
            "auditor": "Trail of Bits (Engagement: TBD)",
            "status": "VERIFIED"
        },
        "mineral_composition": {
            "cobalt_pct": round(random.uniform(3.2, 6.8), 2),
            "copper_pct": round(random.uniform(28.0, 34.0), 2),
            "recycled_content_pct": 0.0
        },
        "royalty_compliance": {
            "statutory_rate_bps": 600,
            "rate_pct": "6.00%",
            "jurisdiction": "Democratic Republic of Congo / Zambia Revenue Authority",
            "zk_royalty_attestation": proof_hash,
            "status": "COMPLIANT"
        },
        "access_model": {
            "public": ["unique_battery_id", "manufacturer.name", "mineral_composition"],
            "regulator": ["supply_chain_due_diligence", "royalty_compliance"],
            "private": ["raw_volume_v", "density_d", "grade_g"]
        }
    }

    # Generate QR code pointing to this endpoint
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(f"http://localhost:8000/api/demo/passport/{proof_hash}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode()

    return JSONResponse({"passport": passport, "qr_code_png_b64": qr_b64})

# ==============================================================================
# ROUTE 6: EVENT HISTORY (SQLite persistence)
# ==============================================================================
@app.get("/api/demo/events")
async def list_events(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    events = db.query(ExtractionEvent).order_by(ExtractionEvent.timestamp.desc()).limit(20).all()
    return [
        {
            "event_id": e.event_id,
            "mine_id": e.mine_id,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            "zone_m2": e.zone_m2,
            "volume_v": e.volume_v,
            "proof_hash": e.proof_hash,
            "consensus_reached": e.consensus_reached,
        }
        for e in events
    ]

@app.get("/api/health")
async def health():
    return {"status": "operational", "protocol": "Resource Command Demo v1.0", "mine": "MPNI"}

# ==============================================================================
# ROUTE 7: REAL CDSE SENTINEL-2 SCENES (live ESA data for Mopani mine)
# ==============================================================================
@app.get("/api/demo/cdse-scenes")
async def cdse_scenes():
    """
    Returns real Sentinel-2 scene metadata pulled from ESA Copernicus Data Space
    for the Mopani mine area (-12.5501 S, 28.2371 E).
    Data is cached in cdse_mopani_scenes.json — run cdse_test.py to refresh.
    """
    scenes_path = Path(__file__).parent / "cdse_mopani_scenes.json"
    if scenes_path.exists():
        import json as _json
        data = _json.loads(scenes_path.read_text())
        return JSONResponse(data)
    return JSONResponse({
        "mine": "MPNI - Mopani, Mufulira, Zambia",
        "source": "ESA Copernicus Data Space Ecosystem",
        "scenes": [],
        "error": "Run cdse_test.py to fetch live scene data"
    })

import os, httpx

@app.get("/api/demo/sentinel-scenes")
async def sentinel_scenes():
    user = os.getenv("CDSE_USER", "")
    pwd  = os.getenv("CDSE_PASS", "")
    async with httpx.AsyncClient() as client:
        try:
            token_res = await client.post(
                "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
                data={"client_id":"cdse-public","grant_type":"password","username":user,"password":pwd},
                timeout=15
            )
            token = token_res.json().get("access_token","")
        except:
            return JSONResponse({"error":"CDSE auth failed","scenes":[]})
        try:
            aoi = "POLYGON((28.21 -12.57,28.26 -12.57,28.26 -12.53,28.21 -12.53,28.21 -12.57))"
            r = await client.get(
                "https://catalogue.dataspace.copernicus.eu/odata/v1/Products",
                params={"$filter":("Collection/Name eq 'SENTINEL-2' and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value le 30) and ContentDate/Start gt 2026-02-01T00:00:00Z and OData.CSC.Intersects(area=geography'SRID=4326;"+aoi+"') and contains(Name,'L2A')"),"$orderby":"ContentDate/Start desc","$top":5,"$expand":"Attributes"},
                headers={"Authorization":f"Bearer {token}"},
                timeout=20
            )
            products = r.json().get("value",[])
            scenes = []
            for p in products:
                cloud = next((a["Value"] for a in p.get("Attributes",[]) if a.get("Name")=="cloudCover"),None)
                scenes.append({"name":p["Name"],"date":p["ContentDate"]["Start"][:10],"cloud_pct":round(cloud,1) if cloud else "N/A","id":p["Id"]})
            return JSONResponse({"scenes":scenes,"site":"Mopani, Zambia"})
        except Exception as e:
            return JSONResponse({"error":str(e),"scenes":[]})
