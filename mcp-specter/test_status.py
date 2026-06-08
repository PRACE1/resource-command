import asyncio
import httpx
import os

SPECTER_URL = "http://localhost:8000"

async def check_status():
    async with httpx.AsyncClient(base_url=SPECTER_URL, timeout=5.0) as client:
        try:
            r = await client.get("/api/comfyui/status")
            data = r.json()
            if data.get("status") == "online":
                print("✅ Specter-Vision ONLINE")
            else:
                print(f"❌ Specter-Vision OFFLINE: {data.get('error', 'unknown')}")
        except Exception as e:
            print(f"❌ Cannot reach Specter-Vision: {e}")

if __name__ == "__main__":
    asyncio.run(check_status())
