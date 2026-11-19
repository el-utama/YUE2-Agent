# YUE2-Agent — Multi-Agent Song Generation System for YuE2 Studio

## Overview
YUE2-Agent is a 7-agent orchestration system that drives **YuE2 Studio** (v4.1.0+) via its MCP server to generate full songs with vocals, editable scores, and album-ready exports. Each agent is a specialized sub-agent in `.kilo/agent/` that follows YuE2's strict writing conventions.

## Quick Start
1. Install **YuE2 Studio** from https://github.com/timoncool/YuE2-Studio/releases (Windows 10/11, GPU ≥6 GB VRAM).
2. Launch Studio with `--headless` (runs in background, serves MCP at `http://127.0.0.1:8791/mcp`).
3. Connect MCP client (Claude Code, Cursor, etc.):
   ```bash
   claude mcp add --transport http yue2-studio http://127.0.0.1:8791/mcp
   ```
4. Start the **manager** agent with a song idea. It delegates to sub-agents automatically.

## Agents
| Agent | File | Role |
|-------|------|------|
| **manager** | `.kilo/agent/manager.md` | Orchestrates pipeline; entry point for all song requests |
| **lyricist** | `.kilo/agent/lyricist.md` | Writes structured lyrics (sections, density, Anti-AI checklist) |
| **music-stylist** | `.kilo/agent/music-stylist.md` | Writes YuE2 style sentence (language, genre, vocal, instruments, mood, production, BPM) |
| **reviewer** | `.kilo/agent/reviewer.md` | Validates style+lyrics against YuE2 rules; gatekeeper |
| **critiquer** | `.kilo/agent/critiquer.md` | Improves aesthetics/singability/emotional impact |
| **releaser** | `.kilo/agent/releaser.md` | Imports audio+lyrics into album folder with manifest |
| **tiktok-composer** | `.kilo/agent/tiktok-composer.md` | Short-form 30–60s songs optimized for TikTok/Reels/Shorts |

## Workflow
```
User Idea
    ↓
manager (entry point)
    ↓
├── music-stylist  → style sentence
├── lyricist       → tagged lyrics
    ↓ (parallel when possible)
reviewer → PASS/FAIL (gate)
    ↓ (if PASS)
critiquer (optional, quality uplift)
    ↓
manager → assembles final package
    ↓
YuE2 Studio MCP: song_create → studio_wait → song in library
    ↓
releaser → album folder + manifest + m3u playlist
```

## Requirements
- YuE2 Studio v4.1.0+ (Ruach Studio fine-tune, songs one-by-one, export)
- Windows 10/11 x64, NVIDIA GPU ≥6 GB VRAM (AMD/Intel Vulkan experimental)
- Model set downloaded (Q6_K ~4.3 GB for 7+ GB VRAM)
- MCP client connected to Studio (`yue2-studio` server)

## Resources
- YuE2 Studio: https://github.com/timoncool/YuE2-Studio
- MCP Skill: `studio://skill` (served by Studio)
- Lyric Guide: `lyric-guide.md` (10 genres, Anti-AI checklist, patterns)
