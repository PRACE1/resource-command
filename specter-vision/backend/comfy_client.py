"""
Async ComfyUI client — wraps the ComfyUI HTTP + WebSocket API.
"""

import asyncio
import json
import uuid
import base64
from pathlib import Path
from io import BytesIO
from typing import Any

import aiohttp
from PIL import Image


class ComfyClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.ws_url   = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    # ── Cluster health ───────────────────────────────────────────────
    async def system_stats(self) -> dict:
        s = await self._get_session()
        async with s.get(f"{self.base_url}/system_stats", timeout=aiohttp.ClientTimeout(total=5)) as r:
            return await r.json()

    async def queue_info(self) -> dict:
        s = await self._get_session()
        async with s.get(f"{self.base_url}/queue", timeout=aiohttp.ClientTimeout(total=5)) as r:
            return await r.json()

    # ── Image upload ─────────────────────────────────────────────────
    async def upload_image(self, image_bytes: bytes, filename: str = "input.png") -> str:
        """Upload image to ComfyUI /upload/image, return server filename."""
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        form = aiohttp.FormData()
        form.add_field("image", buf, filename=filename, content_type="image/png")
        form.add_field("overwrite", "true")
        form.add_field("type", "input")

        s = await self._get_session()
        async with s.post(f"{self.base_url}/upload/image", data=form) as r:
            data = await r.json()
            return data["name"]

    # ── Prompt submission ────────────────────────────────────────────
    async def queue_prompt(self, workflow: dict, client_id: str | None = None) -> str:
        """Submit workflow to /prompt queue, return prompt_id."""
        if client_id is None:
            client_id = str(uuid.uuid4())
        payload = {"prompt": workflow, "client_id": client_id}

        s = await self._get_session()
        async with s.post(
            f"{self.base_url}/prompt",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as r:
            if r.status != 200:
                body = await r.text()
                raise RuntimeError(f"ComfyUI /prompt returned {r.status}: {body}")
            data = await r.json()
            return data["prompt_id"]

    # ── History polling ──────────────────────────────────────────────
    async def get_history(self, prompt_id: str) -> dict | None:
        """Returns history entry for prompt_id, or None if still queued."""
        s = await self._get_session()
        async with s.get(f"{self.base_url}/history/{prompt_id}") as r:
            data = await r.json()
            return data.get(prompt_id)

    async def wait_for_completion(
        self,
        prompt_id: str,
        poll_interval: float = 1.5,
        timeout: float = 600.0,
    ) -> dict:
        """Poll until the job is done; returns the history entry."""
        elapsed = 0.0
        while elapsed < timeout:
            entry = await self.get_history(prompt_id)
            if entry and entry.get("status", {}).get("completed"):
                return entry
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        raise TimeoutError(f"Job {prompt_id} did not complete in {timeout}s")

    # ── Output retrieval ─────────────────────────────────────────────
    async def download_output(self, filename: str, subfolder: str = "", file_type: str = "output") -> bytes:
        """Download a generated file from ComfyUI /view endpoint."""
        params = {"filename": filename, "subfolder": subfolder, "type": file_type}
        s = await self._get_session()
        async with s.get(f"{self.base_url}/view", params=params) as r:
            if r.status != 200:
                raise RuntimeError(f"ComfyUI /view returned {r.status} for {filename}")
            return await r.read()

    def extract_outputs(self, history_entry: dict) -> list[dict]:
        """Parse history entry and return list of {node_id, filename, type}."""
        outputs = []
        for node_id, node_data in history_entry.get("outputs", {}).items():
            for media_type in ("videos", "images", "gifs"):
                for item in node_data.get(media_type, []):
                    outputs.append({
                        "node_id":  node_id,
                        "filename": item.get("filename", ""),
                        "subfolder": item.get("subfolder", ""),
                        "type":     media_type.rstrip("s"),
                    })
        return outputs


# ── Workflow template helpers ────────────────────────────────────────
def load_workflow(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def patch_workflow(
    workflow: dict,
    *,
    prompt: str,
    negative_prompt: str,
    image_filename: str | None,
    motion_bucket_id: int,
    num_frames: int,
    fps: int,
    guidance_scale: float,
    steps: int,
) -> dict:
    """Inject base generation parameters (compatible with wan_i2v.json)."""
    wf = json.loads(json.dumps(workflow))   # deep copy

    _set_node_input(wf, "positive_prompt",  "text",             prompt)
    _set_node_input(wf, "negative_prompt",  "text",             negative_prompt)
    _set_node_input(wf, "sampler",          "steps",            steps)
    _set_node_input(wf, "sampler",          "cfg",              guidance_scale)
    _set_node_input(wf, "sampler",          "num_frames",       num_frames)
    _set_node_input(wf, "motion_params",    "motion_bucket_id", motion_bucket_id)
    _set_node_input(wf, "video_combine",    "frame_rate",       fps)

    if image_filename:
        _set_node_input(wf, "load_image", "image", image_filename)

    return wf


def patch_workflow_elite(
    workflow: dict,
    *,
    prompt: str,
    negative_prompt: str,
    image_filename: str | None,
    motion_bucket_id: int,
    num_frames: int,
    fps: int,
    guidance_scale: float,
    steps: int,
    # ── Geometry Lock ──────────────────────────────────
    geometry_lock: bool = False,
    geometry_lock_depth_strength: float = 0.80,
    geometry_lock_canny_strength: float = 0.60,
    # ── Temporal Master ────────────────────────────────
    temporal_master: bool = True,
    rife_multiplier: int = 2,
    output_crf: int = 18,
) -> dict:
    """
    Inject all elite parameters into wan_i2v_elite.json.

    Geometry Lock:
      Sets ControlNet depth/canny strength to 0.0 when disabled — the
      ControlNetApplyAdvanced node becomes a pass-through at strength=0,
      keeping the graph valid without removing nodes.

    Temporal Master:
      rife_multiplier=1 disables RIFE interpolation (returns original frames).
      rife_multiplier=2 doubles frame count for smoother 24fps output.
      output_crf controls H264 quality (18 = near-lossless, 23 = default).
    """
    wf = patch_workflow(
        workflow,
        prompt=prompt,
        negative_prompt=negative_prompt,
        image_filename=image_filename,
        motion_bucket_id=motion_bucket_id,
        num_frames=num_frames,
        fps=fps,
        guidance_scale=guidance_scale,
        steps=steps,
    )

    # Geometry Lock — zero-out ControlNet strength to disable without graph surgery
    depth_strength = geometry_lock_depth_strength if geometry_lock else 0.0
    canny_strength = geometry_lock_canny_strength if geometry_lock else 0.0
    _set_node_input(wf, "depth_controlnet_apply", "strength", depth_strength)
    _set_node_input(wf, "canny_controlnet_apply", "strength", canny_strength)

    # Geometry Lock — tighten end_percent when lock is very strong (>0.8)
    # keeps structure grounded in the first 50% of denoising steps
    if geometry_lock and geometry_lock_depth_strength > 0.8:
        _set_node_input(wf, "depth_controlnet_apply", "end_percent", 0.60)
        _set_node_input(wf, "canny_controlnet_apply", "end_percent", 0.45)

    # Temporal Master
    actual_multiplier = rife_multiplier if temporal_master else 1
    _set_node_input(wf, "frame_interpolation", "multiplier", actual_multiplier)
    _set_node_input(wf, "video_combine",        "crf",        output_crf)

    return wf


def _set_node_input(workflow: dict, node_title: str, key: str, value: Any):
    """Find a node by _meta.title and update one input field in-place."""
    for node in workflow.values():
        if isinstance(node, dict):
            if node.get("_meta", {}).get("title") == node_title:
                node["inputs"][key] = value
                return
    # silently ignore missing nodes — allows partial workflows during dev
