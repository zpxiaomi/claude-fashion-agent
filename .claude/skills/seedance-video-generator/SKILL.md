---
name: seedance-video-generator
description: Generate videos from images using the fal.ai Seedance 2.0 (ByteDance) API. Use when the user wants to animate an image, create video from a photo, generate video with audio, or call the seedance or bytedance image-to-video fal.ai model.
---

# Seedance 2.0 Video Generator

Generates videos from a starting image using `bytedance/seedance-2.0/image-to-video`.

## Quick Start

```python
import fal_client

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            print(f"  [fal.ai] {log['message']}")

result = fal_client.subscribe(
    "bytedance/seedance-2.0/image-to-video",
    arguments={
        "prompt": "A model walks confidently down a runway",
        "image_url": "https://example.com/image.jpg",
    },
    with_logs=True,
    on_queue_update=on_queue_update,
)

video_url = result["video"]["url"]
seed_used = result["seed"]
```

## Input Parameters

| Parameter | Type | Default | Required | Notes |
|---|---|---|---|---|
| `prompt` | string | — | Yes | Describe motion and action |
| `image_url` | string | — | Yes | JPEG/PNG/WebP, max 30 MB; URL or base64 |
| `end_image_url` | string | — | No | Final frame for transition effects |
| `resolution` | `"480p"` `"720p"` `"1080p"` | `"720p"` | No | Output resolution |
| `duration` | `"auto"` or `4`–`15` | `"auto"` | No | Length in seconds |
| `aspect_ratio` | `"auto"` `"16:9"` `"9:16"` `"1:1"` `"4:3"` `"3:4"` `"21:9"` | `"auto"` | No | Output aspect ratio |
| `generate_audio` | boolean | `true` | No | Synchronized audio generation |
| `seed` | integer | — | No | Fix for reproducible results |
| `end_user_id` | string | — | No | Unique end-user identifier |

## Output

```python
result["video"]["url"]           # Download URL (mp4)
result["video"]["file_size"]     # Size in bytes
result["video"]["content_type"]  # "video/mp4"
result["seed"]                   # Seed actually used
```

## Uploading Local Files

```python
image_url = fal_client.upload_file("path/to/image.jpg")
```

## Async / Webhook Pattern (for long runs)

```python
handler = fal_client.submit(
    "bytedance/seedance-2.0/image-to-video",
    arguments={...},
    webhook_url="https://your-server.com/webhook",
)
request_id = handler.request_id

# Poll status
status = fal_client.status("bytedance/seedance-2.0/image-to-video", request_id, with_logs=True)

# Fetch result when done
result = fal_client.result("bytedance/seedance-2.0/image-to-video", request_id)
```

## vs Kling v2.6 Pro

| Feature | Seedance 2.0 | Kling v2.6 Pro |
|---|---|---|
| Model ID | `bytedance/seedance-2.0/image-to-video` | `fal-ai/kling-video/v2.6/pro/image-to-video` |
| Image param | `image_url` | `start_image_url` |
| Resolution control | Yes (`480p`/`720p`/`1080p`) | No |
| Aspect ratio control | Yes | No |
| Duration | `auto` or 4–15 s | `"5"` or `"10"` |
| Seed output | Yes | No |
| Audio | Yes | Yes |

## Authentication

Set `FAL_KEY` in environment (never expose client-side):
```
FAL_KEY=your-key-here
```
