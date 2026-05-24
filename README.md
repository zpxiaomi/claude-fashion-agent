# Claude Fashion Agent

A prompt-chaining AI pipeline that turns a static fashion product image into a short video using Claude Vision and fal.ai.

## How it works

```
Fashion image URL
      │
      ▼
[Step 1-2] Claude Vision (claude-sonnet-4-6)
           Analyzes the image and generates a cinematic
           100-150 word video prompt via the Anthropic API
      │
      ▼
[Step 3]   Claude Agent SDK + kling-video-generator skill
           Calls the fal.ai Kling v2.6 Pro image-to-video API
           and writes the result to video_result.json
      │
      ▼
[Step 4]   Downloads the .mp4 locally and opens it
           in your default video player
```

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (package manager)
- [Claude Code CLI](https://claude.ai/code) — installed and authenticated
- Anthropic API key
- [fal.ai](https://fal.ai) API key

## Setup

1. Clone the repo and install dependencies:

```bash
git clone https://github.com/zpxiaomi/claude-fashion-agent.git
cd claude-fashion-agent
uv sync
```

2. Create a `.env` file (use `.env.example` as a template):

```bash
cp .env.example .env
```

3. Fill in your API keys in `.env`:

```
ANTHROPIC_API_KEY=your-anthropic-key
FAL_KEY=your-fal-key
```

4. Authenticate Claude Code CLI:

```bash
claude auth login
```

## Usage

```bash
uv run python agent.py
```

The output video is saved as `output_video.mp4` in the project root and opened automatically.

To use a different image, edit the `image_url` at the bottom of `agent.py`.

## Configuration

Two constants at the top of `generate_video_with_skill()` control the video model and duration:

```python
VIDEO_SKILL    = "kling-video-generator"  # or "seedance-video-generator"
VIDEO_DURATION = "5"                      # Kling: "5" or "10" | Seedance: "auto" or 4-15
```

## Video models

| Skill | Model | Duration | Resolution |
|---|---|---|---|
| `kling-video-generator` | fal-ai/kling-video/v2.6/pro | 5s or 10s | Fixed |
| `seedance-video-generator` | bytedance/seedance-2.0 | auto or 4–15s | 480p / 720p / 1080p |

## Project structure

```
claude-fashion-agent/
├── agent.py                          # Main pipeline
├── prompts/
│   └── fashion_video_creator.md     # System prompt for Claude Vision
├── .claude/
│   └── skills/
│       ├── kling-video-generator/   # Skill: Kling v2.6 Pro API
│       └── seedance-video-generator/ # Skill: Seedance 2.0 API
├── pyproject.toml
└── .env                             # API keys (not committed)
```
