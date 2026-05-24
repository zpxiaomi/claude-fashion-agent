import asyncio
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

import httpx
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    TextBlock,
    query,
)
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent
load_dotenv(PROJECT_ROOT / ".env", override=True)

PROMPT_FILE = PROJECT_ROOT / "prompts" / "fashion_video_creator.md"
SYSTEM_PROMPT = PROMPT_FILE.read_text()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")


async def generate_video_prompt(image_url: str) -> str:
    """Step 1 & 2: Analyze image with Claude Vision and return a video prompt."""
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("Missing ANTHROPIC_API_KEY in environment.")

    payload = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 500,
        "system": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "url", "url": image_url}},
                    {
                        "type": "text",
                        "text": (
                            "Use the system instructions to analyze this image and return "
                            "only the final 100-150 word video generation prompt text."
                        ),
                    },
                ],
            }
        ],
    }

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    def _call() -> str:
        with httpx.Client(timeout=90) as client:
            resp = client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        text_blocks = [
            block.get("text", "").strip()
            for block in data.get("content", [])
            if block.get("type") == "text"
        ]
        prompt = "\n".join(filter(None, text_blocks))
        if not prompt:
            raise RuntimeError(f"Anthropic response had no text content: {data}")
        return prompt

    return await asyncio.to_thread(_call)


# Switch between configs by uncommenting one line:
VIDEO_SKILL, VIDEO_DURATION = "kling-video-generator", "5"         # Kling: "5" or "10"
# VIDEO_SKILL, VIDEO_DURATION = "seedance-video-generator", "auto"  # Seedance: "auto" or 4-15


async def generate_video_with_skill(video_prompt: str, image_url: str) -> str:
    """Step 3: Use the configured video skill via Claude Agent SDK to create the video."""
    result_file = PROJECT_ROOT / "video_result.json"
    result_file.unlink(missing_ok=True)

    agent_prompt = (
        f"Use the {VIDEO_SKILL} skill to generate a fashion video.\n\n"
        f"Parameters:\n"
        f"- start_image_url: {image_url}\n"
        f"- prompt: {video_prompt}\n"
        f"- duration: {VIDEO_DURATION}\n\n"
        "Run the fal.ai API call using Python and fal_client. "
        f"After the video is generated, write the result to '{result_file}' as JSON with this structure:\n"
        '{"video_url": "<url>", "file_size": <bytes>}\n'
        "Use the video URL from result['video']['url']."
    )

    options = ClaudeAgentOptions(
        cwd=str(PROJECT_ROOT),
        setting_sources=["project"],
        allowed_tools=["Bash"],
    )

    async for message in query(prompt=agent_prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"  [agent] {block.text}")

    if not result_file.exists():
        raise RuntimeError("Agent did not write video_result.json — video generation may have failed.")

    data = json.loads(result_file.read_text())
    result_file.unlink(missing_ok=True)
    return data.get("video_url", "")


def download_video(video_url: str, output_path: Path) -> None:
    """Download the video from the given URL to a local file."""
    with httpx.Client(timeout=120) as client:
        with client.stream("GET", video_url) as resp:
            resp.raise_for_status()
            with output_path.open("wb") as f:
                for chunk in resp.iter_bytes(chunk_size=8192):
                    f.write(chunk)


async def create_fashion_video(image_url: str) -> dict:
    """Main workflow: Claude Vision → kling-video-generator skill → video."""
    print(f"Processing image: {image_url}")

    print("\n[Step 1-2] Generating video prompt via Claude Vision...")
    video_prompt = await generate_video_prompt(image_url)
    if not video_prompt.strip():
        raise RuntimeError("Generated video prompt is empty.")
    print(f"Generated prompt:\n{video_prompt}\n")

    print("[Step 3] Generating video via kling-video-generator skill...")
    video_url = await generate_video_with_skill(video_prompt, image_url)
    if not video_url:
        raise RuntimeError("No video URL returned from agent.")

    print("\n[Step 4] Downloading video...")
    output_dir = PROJECT_ROOT / "output"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"output_video_{VIDEO_SKILL}_{timestamp}.mp4"
    await asyncio.to_thread(download_video, video_url, output_path)
    print(f"Saved to: {output_path}")

    print("Opening video...")
    subprocess.Popen(["xdg-open", str(output_path)])

    return {"video_prompt": video_prompt, "video_url": video_url, "local_file": str(output_path)}


if __name__ == "__main__":
    image_url = "https://example.com/your-fashion-product-image.jpg"  # replace with your image URL
    result = asyncio.run(create_fashion_video(image_url))
    print(f"\nResult: {result}")
