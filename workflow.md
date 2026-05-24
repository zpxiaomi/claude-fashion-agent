# Fashion Product Video Generation Workflow

This workflow generates fashion product showcase videos from static product images using AI.

---

## Overview

**Input:** Product image URL
**Output:** Fashion video with model showcasing the product
**Tools:** `claude-agent-sdk` (see `agent.py`)

---

## Step 1: Generate Video Prompt

Analyze the input product image and create a detailed video generation prompt.

### Prompt Requirements

Describe the following elements:

| Element | Details to Include |
|---------|-------------------|
| **Product** | Type, style, color, material, key features |
| **Model** | Pose, expression, body language, movement |
| **Movement** | Walking pattern, turns, gestures that highlight the product |
| **Setting** | Background, lighting, atmosphere |
| **Camera** | Angles, zooms, tracking shots |

### Example Output

```
A model wearing a flowing crimson evening gown walks down a minimalist
white runway. She pauses mid-walk for a graceful twirl, letting the fabric
catch the light. Close-up shots highlight the dress's intricate beadwork.
Soft studio lighting, elegant and confident atmosphere.
```

---

## Step 2: Generate Video

Use the generated prompt with the input image to create the fashion video.

### Implementation

```python
# See agent.py
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="<generated_prompt>",
    image_url="<product_image_url>",
    options=ClaudeAgentOptions(allowed_tools=["Bash", "Glob"]),
):
    if hasattr(message, "result"):
        print(message.result)
```

### Output

The generated video file path or URL.

---

## File Structure

```
.
├── agent.py              # Main execution script
├── prompts/
│   └── fashion_video_creator.md  # Prompt templates
├── pyproject.toml        # Dependencies (claude-agent-sdk)
└── workflow.md           # This file
```

---

## Quick Start

1. Ensure dependencies are installed: `uv sync` or `pip install -e .`
2. Run the agent: `python agent.py`
3. Replace the image URL in `agent.py` with your product image