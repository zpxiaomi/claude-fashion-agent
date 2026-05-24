import asyncio
import os
import re
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


async def generate_video_with_skill(video_prompt: str, image_url: str) -> str:
    """Step 3: Use kling-video-generator skill via Claude Agent SDK to create the video."""
    agent_prompt = (
        "Use the kling-video-generator skill to generate a fashion video.\n\n"
        f"Parameters:\n"
        f"- start_image_url: {image_url}\n"
        f"- prompt: {video_prompt}\n\n"
        "Run the fal.ai API call using Python and fal_client. "
        "After the video is generated, print the video URL on the last line "
        "prefixed exactly with 'VIDEO_URL: '."
    )

    options = ClaudeAgentOptions(
        cwd=str(PROJECT_ROOT),
        setting_sources=["project"],
        skills=["kling-video-generator"],
        allowed_tools=["Bash"],
    )

    full_response = ""
    async for message in query(prompt=agent_prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"  [agent] {block.text}")
                    full_response += block.text

    match = re.search(r"VIDEO_URL:\s*(https?://\S+)", full_response)
    if not match:
        match = re.search(r"https?://\S+(?:\.mp4|fal\.media)\S*", full_response)

    return match.group(1) if match else ""


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
    print(f"\nVideo URL: {video_url}")

    return {"video_prompt": video_prompt, "video_url": video_url}


if __name__ == "__main__":
    image_url = "https://pic.hse24-dach.net/media/de/products/483851002/0_182e12ae-7a7b-5888-9bde-377abf750000_pics2080.jpg"
    result = asyncio.run(create_fashion_video(image_url))
    print(f"\nResult: {result}")
