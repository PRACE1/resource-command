# OPERATIONS MANUAL
## Specter-Vision Private Video Terminal
### Kgosi Capital — Revision 1.0

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  SPECTER-VISION TERMINAL  (React, port 5173)                │
│  ┌──────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Brand   │  │  Cinematic       │  │  Generation      │  │
│  │  Vault   │  │  Canvas          │  │  Engine          │  │
│  │  (CAD    │  │  (Preview/Video) │  │  Director's Menu │  │
│  │  Assets) │  │  Export Panel    │  │  Motion Slider   │  │
│  └──────────┘  └──────────────────┘  └──────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ REST / JSON
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  FASTAPI BRIDGE  (Python, port 8000)                        │
│  • Prompt composition (base + Director's Menu suffixes)     │
│  • Workflow patching  (geometry lock + temporal params)     │
│  • Export engine      (FFmpeg: ProRes 422 / H.264)          │
└────────────────────────┬────────────────────────────────────┘
                         │ ComfyUI API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  COMFYUI  (port 8188)                                       │
│  Wan 2.1 I2V 14B  ←  ControlNet (depth + canny)            │
│  RIFE VFI 2×     ←  Tiled VAE decode                       │
└─────────────────────────────────────────────────────────────┘
```

**Data flow for a single generation:**
1. Upload CAD render → Brand Vault → select as Input Frame
2. Write or inject a prompt template → PromptTerminal
3. Enable Director's Menu presets (prompt suffixes + pipeline flags)
4. Click GENERATE — FastAPI patches the ComfyUI workflow graph and queues it
5. Canvas shows render progress; on completion the video plays automatically
6. Institutional Export Panel appears — select ProRes or H.264 and download

---

## 2. First-Run Checklist

```
□ sudo ./setup.sh              # one-click server setup
□ Place model files            # see checklist printed by setup.sh
□ docker compose up -d
□ Open http://localhost:5173
□ Upload one ORACLE 250V8 CAD render into the Brand Vault
□ Select ANAMORPHIC + TEMPORAL MASTER in Director's Menu
□ Write a test prompt and click GENERATE SEQUENCE
□ Verify the video plays. Export as H.264 Boardroom.
```

---

## 3. Geometry Lock — CAD Asset Guide

### What it does
Geometry Lock extracts two structural guides from your CAD render and enforces them as ControlNet conditioning throughout the diffusion process:

| Guide | Purpose | Default Strength |
|---|---|---|
| **Depth map** (DepthAnything V2) | Preserves spatial z-ordering — prevents panels and surfaces from swapping depth | 0.80 |
| **Canny edge map** | Preserves sharp line boundaries — prevents body lines from softening or melting | 0.60 |

Both guides taper off after ~65% of the denoising steps. This means structure is enforced hard during the coarse-composition phase and released during the fine-texture phase — so the ORACLE 250V8 reads as precisely manufactured, not painterly.

### When to enable
| Scenario | Recommendation |
|---|---|
| Hero product shot — the chassis must be perfect | **Enable. Depth 0.80 / Canny 0.60** |
| Slow cinematic reveal, no extreme angles | **Enable at reduced strength: 0.65 / 0.45** |
| Facility establishing shot (plant not vehicle) | Disable — no CAD geometry to protect |
| Pure atmospheric / fog shot | Disable — ControlNet fights atmospheric diffusion |

### CAD render requirements for best results
- **Resolution:** 1280×720 minimum. The depth estimator degrades below 512px.
- **Background:** Neutral grey or black. Complex backgrounds confuse the depth estimator and leak into the conditioning.
- **Lighting:** Even studio lighting or three-point. Harsh shadows create false depth discontinuities.
- **Format:** PNG (lossless). JPEG compression artifacts become depth noise.
- **Angle:** 30–60° above horizontal. Pure top-down or dead-straight profiles give the depth estimator less to work with.

### Tuning the lock strength
The `geometry_lock_strength` sliders map to:
- **0.40–0.55** — "Soft lock" — geometry is suggested, not enforced. Some organic drift allowed. Use for dramatic motion shots where a fully rigid chassis would look uncanny.
- **0.65–0.75** — "Standard" — correct for most institutional videos. Sharp geometry, natural surface texture.
- **0.80–0.90** — "Hard lock" — maximum fidelity. Body lines are pixel-perfect. Use for close-up detail shots, QA presentations, or engineering reviews.
- **> 0.90** — Not recommended. The model over-contours surfaces and loses photorealistic texture.

---

## 4. Directed Motion — Mine-Site Scenario Matrix

The **Directed Motion** slider controls `motion_bucket_id` in the Wan 2.1 I2V model. This is not a camera movement instruction — it sets the model's *expectation* of how much inter-frame change is appropriate given the input frame.

```
  0 ──────────────────────────────────────── 255
  SUBTLE     FLUID      DYNAMIC     CINEMATIC
   0–20%    20–50%      50–78%       78–100%
```

### Scenario Matrix

| Scenario | Slider % | Notes |
|---|---|---|
| **Component close-up** — bolts, tolerances, engine internals | 5–15% | Micro-vibration only. The ORACLE 250V8 reads as machined. Pair with MACRO SPEC template. |
| **Conveyor / processing line** — machinery in operation | 20–35% | Slight operational vibration + ambient environmental movement. Avoid higher — it fights the static machinery. |
| **Ground-level facility walk-through** | 35–50% | Forward dolly effect. Conveys scale without distortion. Enable Geometry Lock. |
| **Crusher / plant reveal** — mid-distance establishing | 55–70% | Pan or crane up. Good for operational credibility content. Pair with VOLUMETRIC preset. |
| **ORACLE 250V8 product hero** — front/rear quarter | 65–80% | The vehicle reads as alive and powerful without warping. Sweet spot for investor decks. |
| **Aerial facility overview** — full pit/site scale | 80–90% | Drone pull-back energy. Pair with AERIAL PULL template + VOLUMETRIC. Disable Geometry Lock. |
| **Full cinematic — ORACLE in motion** | 90–100% | Maximum drama. Use only with ANAMORPHIC + KODAK 5219. High VRAM usage. Geometry Lock at 0.50 or off. |

### Rule of thumb
> If the subject is **stationary machinery**, keep below 55%.  
> If the subject is the **ORACLE 250V8 vehicle**, 65–80% is the investment-grade sweet spot.  
> Values above 85% look cinematic on smooth surfaces and hallucinated on complex ones — enable Geometry Lock.

---

## 5. Director's Menu — Preset Combinations

### Institutional Industrial
The following combination is the default for investor-grade content:

| Preset | Status | Reason |
|---|---|---|
| ANAMORPHIC | ✓ ON | 2.39:1 immediately signals professional production |
| KODAK 5219 | ✓ ON | Film grain eliminates the "AI render" look |
| VOLUMETRIC | Situational | Enable for facility shots; disable for clean studio shots |
| GEOMETRY LOCK | ✓ ON (0.75) | Mandatory for ORACLE 250V8 hero shots |
| TEMPORAL MASTER | ✓ ON | Always on — eliminates flicker by default |

### Combinations to avoid
| Combination | Why |
|---|---|
| ANAMORPHIC + very tight Macro at >80% motion | The oval bokeh fights extreme close-up depth — bokeh competes with the subject |
| KODAK 5219 + H.264 Web export | Film grain is high-frequency texture — heavily compressed by H.264 at CRF 26. Use H.264 Boardroom (CRF 18) instead |
| VOLUMETRIC + Geometry Lock >0.85 | Fog/haze is soft and diffuse; the ControlNet is hard and structural. They fight. Use Geometry Lock at 0.55 max when volumetric is active |

---

## 6. Institutional Export — Format Selection Guide

| Format | Codec | Container | Bit Depth | Use Case |
|---|---|---|---|---|
| **ProRes 422 HQ** | Apple ProRes | .MOV | 10-bit 4:2:2 | Master archive + NLE editing (DaVinci Resolve, Premiere Pro, Avid). Non-destructive colour grading. |
| **H.264 Boardroom** | H.264 High | .MP4 | 8-bit 4:2:0 | PowerPoint, Keynote, LinkedIn, boardroom HDMI. CRF 18 = near-lossless. ~12 MB/min |
| **H.264 Web / Mobile** | H.264 | .MP4 | 8-bit 4:2:0 | WhatsApp (< 64 MB cap), Instagram, Telegram. 720p cap, 4 Mbps ceiling. ~4 MB/min |

**Recommended workflow:**
1. Always keep the **ProRes 422 HQ** master for every completed render
2. Derive H.264 Boardroom from the master — never re-encode from H.264
3. Derive H.264 Web last — it is the most lossy step

---

## 7. Troubleshooting

### "ComfyUI: OFFLINE" in the status bar
```bash
docker compose logs comfyui --tail=50   # check for Python errors
docker compose restart comfyui
```
The most common cause is a missing model file. ComfyUI fails silently on missing checkpoints.

### Generation fails immediately after submission
The elite workflow silently falls back to `wan_i2v.json` if `wan_i2v_elite.json` is missing. Check:
```
volumes/custom_nodes/ComfyUI-WanVideoWrapper/   ← must exist
volumes/models/diffusion_models/wan2.1-i2v-...  ← must exist
```

### Geometry is melting despite Geometry Lock enabled
- Verify `comfyui_controlnet_aux` is installed and loaded (`docker compose logs comfyui | grep controlnet_aux`)
- Verify ControlNet model files are in `volumes/models/controlnet/`
- Reduce Motion slider below 60% — very high motion values override geometry conditioning

### Video flickers despite Temporal Master enabled
- Verify `ComfyUI-Frame-Interpolation` is installed
- Verify `rife47.pth` is in `volumes/models/rife/`
- RIFE with multiplier=1 is a pass-through — check the backend log confirms `"temporal_master": true` is being sent in the request

### ProRes 422 export fails
```bash
docker exec specter-backend ffmpeg -version   # confirms FFmpeg is installed
docker compose logs backend --tail=20         # shows FFmpeg stderr
```
Ensure the source `.mp4` exists in `volumes/output/` before attempting export.

### VRAM out-of-memory during generation
- Reduce `FRAMES` parameter to 41 (= ~3.5 seconds at 12fps, RIFE interpolates to 24fps)
- Set `load_device: "offload_device"` in `wan_i2v_elite.json` node "1" (default)
- Disable Geometry Lock temporarily (removes ControlNet VRAM overhead)
- A100 40GB: should handle 14B at full 81 frames fp8
- A100 80GB: handles 14B at bf16 comfortably

---

*Specter-Vision Operations Manual — Kgosi Capital Internal Use*  
*Revision 1.0 — Generated by Project Specter-Vision build pipeline*
