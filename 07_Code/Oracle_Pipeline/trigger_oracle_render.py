import os
import httpx
import asyncio

REPLICATE_API_TOKEN = "r8_RSewqxs03L4w7aKwIda8bzU8s4rHmP82khxmG"
MODEL = "wavespeedai/wan-2.1-t2v-480p"

PROMPT = (
    "Cinematic 2.39:1 anamorphic shot of the ORACLE Sovereign Extraction Vehicle. "
    "Heavy industrial lattice design with depth-graded vertex glow, moving through "
    "a vast copper mining facility at golden hour. Volumetric haze, Kodak 5219 film grain, "
    "photorealistic, 8k detail, extreme mechanical precision."
)

async def trigger_render():
    headers = {
        "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "input": {
            "prompt": PROMPT,
            "num_frames": 81,
            "sample_steps": 25,
            "sample_guide_scale": 6.0,
            "fps": 16
        }
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        print(f"Sending request to Replicate for the ORACLE Hero Shot...")
        r = await client.post(
            f"https://api.replicate.com/v1/models/{MODEL}/predictions",
            headers=headers,
            json=payload
        )
        if r.status_code != 201:
            print(f"Error: {r.status_code} - {r.text}")
            return
            
        prediction = r.json()
        pred_id = prediction["id"]
        print(f"Prediction queued! ID: {pred_id}")
        print(f"View progress at: https://replicate.com/p/{pred_id}")
        
        # Poll for completion
        while True:
            await asyncio.sleep(20)
            r = await client.get(
                f"https://api.replicate.com/v1/predictions/{pred_id}",
                headers=headers
            )
            pred = r.json()
            status = pred["status"]
            print(f"Status: {status}...")
            
            if status == "succeeded":
                output = pred["output"]
                video_url = output if isinstance(output, str) else output[0]
                print(f"RENDER COMPLETE!")
                print(f"Video URL: {video_url}")
                break
            elif status == "failed":
                print(f"Render failed: {pred.get('error')}")
                break

if __name__ == "__main__":
    asyncio.run(trigger_render())
