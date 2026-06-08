# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""
Specter-Vision Model Downloader
Downloads all required models for Wan 2.1 I2V + ControlNet + RIFE pipeline.
Run once from the specter-vision/ directory.
"""

import os
import sys
import urllib.request
from pathlib import Path

BASE = Path(__file__).parent / "volumes" / "models"

# ── Try huggingface_hub ────────────────────────────────────────────────────────
try:
    from huggingface_hub import hf_hub_download
    HF_AVAILABLE = True
    print("✓ huggingface_hub available")
except ImportError:
    HF_AVAILABLE = False
    print("Installing huggingface_hub...")
    os.system(f"{sys.executable} -m pip install huggingface_hub -q")
    from huggingface_hub import hf_hub_download
    HF_AVAILABLE = True


def dl(repo_id: str, filename: str, subdir: str, repo_type: str = "model"):
    dest_dir = BASE / subdir
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / Path(filename).name
    if dest_file.exists() and dest_file.stat().st_size > 1_000_000:
        print(f"  ✓ Already have: {dest_file.name}  ({dest_file.stat().st_size // 1_000_000} MB)")
        return
    print(f"  ↓ Downloading {filename}  [{repo_id}]")
    hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=str(dest_dir),
        repo_type=repo_type,
    )
    print(f"  ✓ Done: {dest_file.name}")


def dl_url(url: str, subdir: str, filename: str):
    dest_dir = BASE / subdir
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / filename
    if dest_file.exists() and dest_file.stat().st_size > 1_000_000:
        print(f"  ✓ Already have: {filename}")
        return
    print(f"  ↓ Downloading {filename} from {url}")
    urllib.request.urlretrieve(url, dest_file, reporthook=lambda b, bs, total:
        print(f"\r  {b * bs / max(total, 1) * 100:.0f}%", end="", flush=True) if b % 50 == 0 else None)
    print(f"\n  ✓ Done: {filename}")


print("\n═══════════════════════════════════════════")
print("   SPECTER-VISION MODEL DOWNLOADER v1.0")
print("═══════════════════════════════════════════\n")

# ── 1. Main Wan 2.1 diffusion model (BF16, ~14 GB) ────────────────────────────
print("[1/7] Wan 2.1 I2V 14B main model  (~14 GB — this is the big one)")
dl("Kijai/WanVideo_comfy", "wan2.1_i2v_480p_14B_bf16.safetensors", "diffusion_models")

# ── 2. VAE (~400 MB) ──────────────────────────────────────────────────────────
print("[2/7] Wan 2.1 VAE  (~400 MB)")
dl("Kijai/WanVideo_comfy", "wan_2.1_vae.safetensors", "vae")

# ── 3. CLIP Vision encoder (~600 MB) ──────────────────────────────────────────
print("[3/7] CLIP Vision H  (~600 MB)")
dl("Kijai/WanVideo_comfy", "clip_vision_h.safetensors", "clip_vision")

# ── 4. UMT5 text encoder FP8  (~5 GB) ────────────────────────────────────────
print("[4/7] UMT5 XXL text encoder FP8  (~5 GB)")
dl("Kijai/WanVideo_comfy", "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "text_encoders")

# ── 5. DepthAnything V2 ControlNet  (~1.3 GB) ─────────────────────────────────
print("[5/7] DepthAnything V2 ControlNet  (~1.3 GB)")
try:
    dl("TheDenk/wan2.1-i2v-controlnet-depth-v1", "diffusion_pytorch_model.safetensors", "controlnet")
    # Rename to expected filename
    src = BASE / "controlnet" / "diffusion_pytorch_model.safetensors"
    dst = BASE / "controlnet" / "depth_anything_v2_controlnet.safetensors"
    if src.exists() and not dst.exists():
        src.rename(dst)
        print(f"  ✓ Renamed to depth_anything_v2_controlnet.safetensors")
except Exception as e:
    print(f"  ⚠ Depth ControlNet not found at TheDenk — trying alternate: {e}")
    try:
        dl("Kijai/WanVideo_comfy", "depth_anything_v2_controlnet.safetensors", "controlnet")
    except Exception as e2:
        print(f"  ⚠ Not available yet on HF — skipping, geometry lock depth will fallback: {e2}")

# ── 6. Canny ControlNet for Wan  (~1.3 GB) ────────────────────────────────────
print("[6/7] Canny ControlNet for Wan  (~1.3 GB)")
try:
    dl("TheDenk/wan2.1-i2v-controlnet-canny-v1", "diffusion_pytorch_model.safetensors", "controlnet")
    src = BASE / "controlnet" / "diffusion_pytorch_model.safetensors"
    dst = BASE / "controlnet" / "controlnet_canny_wan.safetensors"
    if src.exists() and not dst.exists():
        src.rename(dst)
        print(f"  ✓ Renamed to controlnet_canny_wan.safetensors")
except Exception as e:
    print(f"  ⚠ Canny ControlNet not found — trying alternate: {e}")
    try:
        dl("Kijai/WanVideo_comfy", "controlnet_canny_wan.safetensors", "controlnet")
    except Exception as e2:
        print(f"  ⚠ Not available yet — geometry lock canny will fallback: {e2}")

# ── 7. RIFE 4.7 frame interpolation (~50 MB) ──────────────────────────────────
print("[7/7] RIFE 4.7 frame interpolation model  (~50 MB)")
try:
    dl("Kijai/rife-ncnn-vulkan_wrapper", "rife47.pth", "rife")
except Exception as e:
    print(f"  ⚠ Trying alternate RIFE source: {e}")
    try:
        dl_url(
            "https://github.com/hzwer/ECCV2022-RIFE/releases/download/v4.7/rife47.pth",
            "rife", "rife47.pth"
        )
    except Exception as e2:
        print(f"  ⚠ RIFE download failed — temporal master will use passthrough: {e2}")

print("\n═══════════════════════════════════════════")
print("   DOWNLOAD COMPLETE")
print("═══════════════════════════════════════════")
print("\nNext: docker compose up -d")
print("Then: open http://localhost:5173")
