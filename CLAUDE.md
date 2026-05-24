# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync                    # Install dependencies
uv run python agent.py     # Run the pipeline
```

There are no tests or linting configured.

## Architecture

A two-stage prompt-chaining pipeline in `agent.py`:

**Stage 1 — Claude Vision** (`generate_video_prompt`): Calls the Anthropic Messages API directly (via `httpx`) with the image URL and the system prompt in `prompts/fashion_video_creator.md`. Returns a 100–150 word cinematic prompt string.

**Stage 2 — Agent SDK subagent** (`generate_video_with_skill`): Spawns a Claude Agent SDK subagent that is told to invoke one of the two local skills (`kling-video-generator` or `seedance-video-generator`). The subagent calls the fal.ai API via `fal_client` and writes the video URL to `video_result.json`. The parent process reads that file, deletes it, then downloads the mp4.

## Video models and duration constraints

The two skills differ in their APIs — always keep `VIDEO_SKILL` and `VIDEO_DURATION` in sync:

| `VIDEO_SKILL` | fal.ai model | `duration` values | Image param |
|---|---|---|---|
| `kling-video-generator` | `fal-ai/kling-video/v2.6/pro/image-to-video` | `"5"` or `"10"` (string) | `start_image_url` |
| `seedance-video-generator` | `bytedance/seedance-2.0/image-to-video` | `"auto"` or integer `4`–`15` | `image_url` |

Seedance also supports `resolution` (`480p`/`720p`/`1080p`) and `aspect_ratio` that Kling does not.

## Local skills

Skills live in `.claude/skills/` and are invoked by name in the agent prompt. Each skill's `SKILL.md` contains the full API reference and a copy-pasteable quick-start snippet the subagent uses to write its Bash code.

## Environment

Required in `.env`:
- `ANTHROPIC_API_KEY` — used by Stage 1 directly via the Anthropic REST API
- `FAL_KEY` — picked up automatically by `fal_client` in the subagent
- `ANTHROPIC_MODEL` — optional, defaults to `claude-sonnet-4-6`
