---
name: kling-video-generator
description: Generate videos from images using the fal.ai Kling Video v2.6 Pro API. Use when the user wants to create a video from an image, animate a photo, generate fashion video, or call the kling-video fal.ai model.
---

# Kling Video Generator

Generates videos from a starting image using `fal-ai/kling-video/v2.6/pro/image-to-video`.

## Quick Start

```python
import fal_client

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            print(f"  [fal.ai] {log['message']}")

result = fal_client.subscribe(
    "fal-ai/kling-video/v2.6/pro/image-to-video",
    arguments={
        "prompt": "A model walks confidently down a runway",
        "start_image_url": "https://example.com/image.jpg",
    },
    with_logs=True,
    on_queue_update=on_queue_update,
)

video_url = result["video"]["url"]
```

## Input Parameters

| Parameter | Type | Default | Required | Notes |
|---|---|---|---|---|
| `prompt` | string | — | Yes | Describe the motion and scene |
| `start_image_url` | string | — | Yes | Publicly accessible URL or base64 data URI |
| `end_image_url` | string | — | No | Pin the final frame |
| `duration` | `"5"` or `"10"` | `"5"` | No | Video length in seconds |
| `negative_prompt` | string | `"blur, distort, and low quality"` | No | What to avoid |
| `generate_audio` | boolean | `true` | No | AI audio synthesis |
| `voice_ids` | list[string] | — | No | Reference as `<<<voice_1>>>` in prompt |

## Output

```python
result["video"]["url"]          # Download URL (mp4)
result["video"]["file_size"]    # Size in bytes
result["video"]["content_type"] # "video/mp4"
```

## Uploading Local Files

```python
image_url = fal_client.upload_file("path/to/image.jpg")
```

## Async / Webhook Pattern (for long runs)

```python
handler = fal_client.submit(
    "fal-ai/kling-video/v2.6/pro/image-to-video",
    arguments={...},
    webhook_url="https://your-server.com/webhook",
)
request_id = handler.request_id
# Later:
result = fal_client.result("fal-ai/kling-video/v2.6/pro/image-to-video", request_id)
```

## Authentication

Set `FAL_KEY` in environment (never expose client-side):
```
FAL_KEY=your-key-here
```
