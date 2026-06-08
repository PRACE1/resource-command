"""
Specter-Vision FastAPI Bridge
Connects the React terminal to the ComfyUI/Wan2.1 render engine.
"""

import asyncio
import os
import uuid
import shutil
from pathlib import Path
from typing import Annotated, Literal

import aiofiles
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from comfy_client import ComfyClient, load_workflow, patch_workflow, patch_workflow_elite

# ── Config ────────────────────────────────────────────────────────────
COMFYUI_URL  = os.getenv("COMFYUI_URL",  "http://localhost:8188")
OUTPUT_DIR   = Path(os.getenv("OUTPUT_DIR",  "./outputs"))
UPLOAD_DIR   = Path(os.getenv("UPLOAD_DIR",  "./uploads"))
WORKFLOW_DIR = Path(os.getenv("WORKFLOW_DIR", "./workflows"))

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ── In-memory stores (swap for Redis in prod) ─────────────────────────
jobs:    dict[str, dict] = {}
exports: dict[str, dict] = {}

# ── Institutional Export — FFmpeg format profiles ──────────────────────
EXPORT_PROFILES: dict[str, dict] = {
    "prores422": {
        "label":      "ProRes 422 HQ",
        "ext":        ".mov",
        "media_type": "video/quicktime",
        "ffmpeg_args": [
            "-c:v", "prores_ks",
            "-profile:v", "3",          # 3 = ProRes 422 HQ; 2 = standard
            "-vendor", "ap10",
            "-pix_fmt", "yuv422p10le",  # 10-bit 4:2:2
            "-color_primaries", "bt709",
            "-color_trc", "bt709",
            "-colorspace", "bt709",
            "-c:a", "copy",
        ],
    },
    "h264_presentation": {
        "label":      "H.264 Boardroom",
        "ext":        "_boardroom.mp4",
        "media_type": "video/mp4",
        "ffmpeg_args": [
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "slow",
            "-profile:v", "high",
            "-level:v", "4.2",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",  # progressive download for presentations
            "-c:a", "copy",
        ],
    },
    "h264_web": {
        "label":      "H.264 Web / Mobile",
        "ext":        "_web.mp4",
        "media_type": "video/mp4",
        "ffmpeg_args": [
            "-c:v", "libx264",
            "-crf", "26",
            "-preset", "medium",
            "-vf", "scale='min(1280,iw)':-2",   # cap at 720p, keep aspect
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-maxrate", "4M",
            "-bufsize", "8M",
            "-c:a", "copy",
        ],
    },
}

# ── App ───────────────────────────────────────────────────────────────
app = FastAPI(title="Specter-Vision API", version="1.0.0", docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

comfy = ComfyClient(COMFYUI_URL)

# ── Models ────────────────────────────────────────────────────────────
class JobStatus(BaseModel):
    job_id:   str
    status:   str          # queued | running | complete | failed
    progress: float = 0.0
    message:  str   = ""
    video_url: str | None = None
    error:    str | None = None


# ── Health / Status ───────────────────────────────────────────────────
@app.get("/api/comfyui/status")
async def comfyui_status():
    try:
        stats = await comfy.system_stats()
        queue = await comfy.queue_info()

        vram_used  = stats.get("system", {}).get("vram_used",  0)
        vram_total = stats.get("system", {}).get("vram_total", 1)
        q_running  = len(queue.get("queue_running", []))
        q_pending  = len(queue.get("queue_pending", []))

        return {
            "status": "online",
            "vram": {
                "used_gb":  round(vram_used  / 1e9, 1),
                "total_gb": round(vram_total / 1e9, 1),
                "pct":      round(vram_used  / max(vram_total, 1) * 100),
            },
            "queue": q_running + q_pending,
        }
    except Exception as exc:
        return JSONResponse({"status": "offline", "error": str(exc)}, status_code=503)


# ── Generation ────────────────────────────────────────────────────────
@app.post("/api/generate")
async def generate(
    background_tasks: BackgroundTasks,
    # ── Core params ──────────────────────────────────────────────────
    prompt:           Annotated[str, Form()],
    negative_prompt:  Annotated[str, Form()] = "blurry, distorted, low quality",
    motion_bucket_id: Annotated[int, Form()] = 110,
    num_frames:       Annotated[int, Form()] = 81,
    fps:              Annotated[int, Form()] = 24,
    guidance_scale:   Annotated[float, Form()] = 6.0,
    steps:            Annotated[int, Form()] = 25,
    model_mode:       Annotated[str, Form()] = "i2v",
    # ── Elite: Geometry Lock ─────────────────────────────────────────
    geometry_lock:              Annotated[bool,  Form()] = False,
    geometry_lock_depth_strength: Annotated[float, Form()] = 0.80,
    geometry_lock_canny_strength: Annotated[float, Form()] = 0.60,
    # ── Elite: Temporal Master ───────────────────────────────────────
    temporal_master:  Annotated[bool, Form()] = True,
    output_crf:       Annotated[int,  Form()] = 18,
    # ── Image ────────────────────────────────────────────────────────
    image:            UploadFile | None = File(None),
):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "queued", "progress": 0.0, "message": "Queued", "video_url": None, "error": None}

    # Persist uploaded image
    image_path: Path | None = None
    if image and image.filename:
        suffix     = Path(image.filename).suffix or ".png"
        image_path = UPLOAD_DIR / f"{job_id}{suffix}"
        async with aiofiles.open(image_path, "wb") as f:
            content = await image.read()
            await f.write(content)

    params = dict(
        prompt=prompt,
        negative_prompt=negative_prompt,
        motion_bucket_id=motion_bucket_id,
        num_frames=num_frames,
        fps=fps,
        guidance_scale=guidance_scale,
        steps=steps,
        model_mode=model_mode,
        image_path=image_path,
        geometry_lock=geometry_lock,
        geometry_lock_depth_strength=geometry_lock_depth_strength,
        geometry_lock_canny_strength=geometry_lock_canny_strength,
        temporal_master=temporal_master,
        output_crf=output_crf,
    )

    background_tasks.add_task(_run_generation, job_id, params)
    return {"job_id": job_id}


async def _run_generation(job_id: str, params: dict):
    try:
        jobs[job_id].update(status="running", progress=5.0, message="Uploading image to render engine…")

        # Upload image to ComfyUI if provided
        comfy_image_name: str | None = None
        if params.get("image_path"):
            async with aiofiles.open(params["image_path"], "rb") as f:
                image_bytes = await f.read()
            comfy_image_name = await comfy.upload_image(
                image_bytes, filename=f"{job_id}.png"
            )

        jobs[job_id].update(progress=10.0, message="Building workflow graph…")

        # Select workflow — always use elite for I2V; fall back to base for T2V
        is_elite = params["model_mode"] == "i2v"
        wf_name  = "wan_i2v_elite.json" if is_elite else "wan_t2v.json"
        wf_path  = WORKFLOW_DIR / wf_name

        # Graceful fallback: if elite workflow not present, use base
        if not wf_path.exists() and is_elite:
            wf_path = WORKFLOW_DIR / "wan_i2v.json"
            is_elite = False

        if not wf_path.exists():
            raise FileNotFoundError(f"Workflow not found: {wf_path}")

        workflow = load_workflow(wf_path)

        if is_elite:
            workflow = patch_workflow_elite(
                workflow,
                prompt=params["prompt"],
                negative_prompt=params["negative_prompt"],
                image_filename=comfy_image_name,
                motion_bucket_id=params["motion_bucket_id"],
                num_frames=params["num_frames"],
                fps=params["fps"],
                guidance_scale=params["guidance_scale"],
                steps=params["steps"],
                geometry_lock=params["geometry_lock"],
                geometry_lock_depth_strength=params["geometry_lock_depth_strength"],
                geometry_lock_canny_strength=params["geometry_lock_canny_strength"],
                temporal_master=params["temporal_master"],
                output_crf=params["output_crf"],
            )
        else:
            workflow = patch_workflow(
                workflow,
                prompt=params["prompt"],
                negative_prompt=params["negative_prompt"],
                image_filename=comfy_image_name,
                motion_bucket_id=params["motion_bucket_id"],
                num_frames=params["num_frames"],
                fps=params["fps"],
                guidance_scale=params["guidance_scale"],
                steps=params["steps"],
            )

        jobs[job_id].update(progress=15.0, message="Submitting to ComfyUI queue…")
        prompt_id = await comfy.queue_prompt(workflow)

        # Poll for completion
        jobs[job_id].update(progress=20.0, message="Rendering sequence…")
        history = await _poll_with_progress(job_id, prompt_id)

        # Retrieve output video
        outputs = comfy.extract_outputs(history)
        if not outputs:
            raise RuntimeError("ComfyUI returned no outputs.")

        video_out = next((o for o in outputs if o["type"] == "video"), outputs[0])
        video_bytes = await comfy.download_output(
            video_out["filename"], subfolder=video_out.get("subfolder", "")
        )

        out_path = OUTPUT_DIR / f"{job_id}.mp4"
        async with aiofiles.open(out_path, "wb") as f:
            await f.write(video_bytes)

        jobs[job_id].update(
            status="complete",
            progress=100.0,
            message="Sequence rendered.",
            video_url=f"/api/output/{job_id}.mp4",
        )

    except Exception as exc:
        jobs[job_id].update(status="failed", error=str(exc), message=f"Error: {exc}")


async def _poll_with_progress(job_id: str, prompt_id: str, timeout: float = 600.0):
    elapsed   = 0.0
    interval  = 2.0
    steps_est = jobs[job_id].get("steps", 25) or 25

    while elapsed < timeout:
        await asyncio.sleep(interval)
        elapsed += interval

        entry = await comfy.get_history(prompt_id)
        if entry:
            if entry.get("status", {}).get("completed"):
                jobs[job_id].update(progress=95.0, message="Post-processing…")
                return entry
            # Rough progress from ComfyUI node execution messages
            msgs = entry.get("status", {}).get("messages", [])
            executed = sum(1 for m in msgs if m[0] == "execution_cached" or m[0] == "executed")
            pct = 20.0 + min(executed / max(steps_est, 1), 1.0) * 72.0
            jobs[job_id].update(progress=round(pct, 1), message=f"Diffusing… step ~{executed}/{steps_est}")

    raise TimeoutError(f"Render timed out after {timeout}s")


# ── Job status ────────────────────────────────────────────────────────
@app.get("/api/job/{job_id}", response_model=JobStatus)
async def job_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, detail="Job not found")
    return JobStatus(job_id=job_id, **job)


# ── Output serving ────────────────────────────────────────────────────
@app.get("/api/output/{filename}")
async def serve_output(filename: str):
    path = OUTPUT_DIR / filename
    if not path.exists():
        raise HTTPException(404, detail="Output not found")
    return FileResponse(path, media_type="video/mp4")


# ── Job listing ───────────────────────────────────────────────────────
@app.get("/api/jobs")
async def list_jobs():
    return [
        {"job_id": jid, **{k: v for k, v in jdata.items()}}
        for jid, jdata in reversed(list(jobs.items()))
    ]


# ═══════════════════════════════════════════════════════════════════════
#  INSTITUTIONAL EXPORT
# ═══════════════════════════════════════════════════════════════════════

@app.post("/api/export/{job_id}")
async def start_export(
    job_id: str,
    background_tasks: BackgroundTasks,
    format: Annotated[str, Query()] = "prores422",
):
    """
    Transcode a completed render to a delivery format using FFmpeg.
    Supported formats: prores422 | h264_presentation | h264_web
    """
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, detail="Job not found")
    if job["status"] != "complete":
        raise HTTPException(400, detail=f"Job status is '{job['status']}' — must be 'complete'")

    source_path = OUTPUT_DIR / f"{job_id}.mp4"
    if not source_path.exists():
        raise HTTPException(404, detail="Source render not found on disk")

    if format not in EXPORT_PROFILES:
        raise HTTPException(400, detail=f"Unknown format '{format}'. Valid: {list(EXPORT_PROFILES)}")

    export_id = str(uuid.uuid4())
    exports[export_id] = {
        "status":       "processing",
        "progress":     0.0,
        "format":       format,
        "label":        EXPORT_PROFILES[format]["label"],
        "job_id":       job_id,
        "download_url": None,
        "output_path":  None,
        "error":        None,
    }

    background_tasks.add_task(_run_export, export_id, source_path, format)
    return {"export_id": export_id}


async def _run_export(export_id: str, source_path: Path, format: str):
    profile  = EXPORT_PROFILES[format]
    ext      = profile["ext"]
    out_path = OUTPUT_DIR / f"{source_path.stem}_export_{format}{ext}"

    cmd = [
        "ffmpeg",
        "-y",                   # overwrite without prompt
        "-i", str(source_path),
        *profile["ffmpeg_args"],
        str(out_path),
    ]

    try:
        exports[export_id].update(progress=5.0)

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Stream stderr to extract progress while waiting
        # FFmpeg writes duration/time to stderr; we parse it for a rough pct
        duration_s: float | None = None
        if proc.stderr:
            async for raw_line in proc.stderr:
                line = raw_line.decode("utf-8", errors="replace")
                if duration_s is None and "Duration:" in line:
                    try:
                        t = line.split("Duration:")[1].split(",")[0].strip()
                        h, m, s = t.split(":")
                        duration_s = int(h) * 3600 + int(m) * 60 + float(s)
                    except Exception:
                        pass
                if duration_s and "time=" in line:
                    try:
                        t = line.split("time=")[1].split(" ")[0].strip()
                        h, m, s = t.split(":")
                        elapsed = int(h) * 3600 + int(m) * 60 + float(s)
                        pct = min(95.0, (elapsed / duration_s) * 100.0)
                        exports[export_id].update(progress=round(pct, 1))
                    except Exception:
                        pass

        await proc.wait()

        if proc.returncode != 0:
            stderr_out = await proc.stderr.read() if proc.stderr else b""
            raise RuntimeError(f"FFmpeg exited {proc.returncode}: {stderr_out.decode()[-400:]}")

        if not out_path.exists():
            raise RuntimeError("FFmpeg completed but output file not found")

        exports[export_id].update(
            status="ready",
            progress=100.0,
            output_path=str(out_path),
            download_url=f"/api/export/download/{export_id}",
        )

    except Exception as exc:
        exports[export_id].update(status="error", error=str(exc))


@app.get("/api/export/status/{export_id}")
async def export_status(export_id: str):
    exp = exports.get(export_id)
    if not exp:
        raise HTTPException(404, detail="Export not found")
    return exp


@app.get("/api/export/download/{export_id}")
async def export_download(export_id: str):
    exp = exports.get(export_id)
    if not exp:
        raise HTTPException(404, detail="Export not found")
    if exp["status"] != "ready":
        raise HTTPException(409, detail=f"Export status is '{exp['status']}' — not ready yet")

    path = Path(exp["output_path"])
    if not path.exists():
        raise HTTPException(404, detail="Export file missing from disk")

    profile  = EXPORT_PROFILES[exp["format"]]
    filename = path.name

    return FileResponse(
        path,
        media_type=profile["media_type"],
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/export/formats")
async def list_export_formats():
    return {k: {"label": v["label"], "ext": v["ext"]} for k, v in EXPORT_PROFILES.items()}
